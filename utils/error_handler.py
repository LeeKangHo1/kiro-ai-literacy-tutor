# utils/error_handler.py
"""
통합 오류 처리 시스템
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from flask import Flask, request, jsonify, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from utils.logging_config import LoggingConfig
from utils.response_utils import error_response


class ErrorSeverity:
    """오류 심각도 레벨"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class ErrorCategory:
    """오류 카테고리"""
    DATABASE = 'database'
    AUTHENTICATION = 'authentication'
    VALIDATION = 'validation'
    EXTERNAL_SERVICE = 'external_service'
    BUSINESS_LOGIC = 'business_logic'
    SYSTEM = 'system'
    NETWORK = 'network'
    UNKNOWN = 'unknown'


class CustomError(Exception):
    """커스텀 예외 기본 클래스"""
    
    def __init__(self, message: str, error_code: str = None, category: str = ErrorCategory.UNKNOWN, 
                 severity: str = ErrorSeverity.MEDIUM, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class DatabaseError(CustomError):
    """데이터베이스 관련 오류"""
    
    def __init__(self, message: str, query: str = None, **kwargs):
        super().__init__(message, category=ErrorCategory.DATABASE, **kwargs)
        if query:
            self.details['query'] = query


class AuthenticationError(CustomError):
    """인증 관련 오류"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.AUTHENTICATION, **kwargs)


class ValidationError(CustomError):
    """검증 관련 오류"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, severity=ErrorSeverity.LOW, **kwargs)
        if field:
            self.details['field'] = field


class ExternalServiceError(CustomError):
    """외부 서비스 관련 오류"""
    
    def __init__(self, message: str, service_name: str = None, **kwargs):
        super().__init__(message, category=ErrorCategory.EXTERNAL_SERVICE, **kwargs)
        if service_name:
            self.details['service_name'] = service_name


class BusinessLogicError(CustomError):
    """비즈니스 로직 관련 오류"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.BUSINESS_LOGIC, **kwargs)


class ErrorTracker:
    """오류 추적 및 통계 관리"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.logger = LoggingConfig.get_contextual_logger('error_tracker')
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """오류 추적 기록"""
        error_info = {
            'timestamp': datetime.utcnow(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        
        # 커스텀 에러인 경우 추가 정보 포함
        if isinstance(error, CustomError):
            error_info.update({
                'error_code': error.error_code,
                'category': error.category,
                'severity': error.severity,
                'details': error.details
            })
        
        # 오류 카운트 업데이트
        error_key = f"{error_info['error_type']}:{error_info['message'][:100]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # 오류 히스토리 추가 (최대 1000개 유지)
        self.error_history.append(error_info)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # 로그 기록
        self.logger.error(f"오류 추적: {error_info['error_type']}", extra_fields=error_info)
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """오류 통계 조회"""
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        
        recent_errors = [
            error for error in self.error_history
            if error['timestamp'].timestamp() > cutoff_time
        ]
        
        # 카테고리별 통계
        category_counts = {}
        severity_counts = {}
        type_counts = {}
        
        for error in recent_errors:
            # 카테고리별
            category = error.get('category', ErrorCategory.UNKNOWN)
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # 심각도별
            severity = error.get('severity', ErrorSeverity.MEDIUM)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # 타입별
            error_type = error['error_type']
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
        
        return {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'category_breakdown': category_counts,
            'severity_breakdown': severity_counts,
            'type_breakdown': dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'most_frequent_errors': dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def get_recent_errors(self, limit: int = 50, severity: str = None) -> List[Dict[str, Any]]:
        """최근 오류 목록 조회"""
        errors = self.error_history[-limit:] if not severity else [
            error for error in self.error_history[-limit*2:]
            if error.get('severity') == severity
        ]
        
        return sorted(errors, key=lambda x: x['timestamp'], reverse=True)[:limit]


class ErrorNotifier:
    """오류 알림 시스템"""
    
    def __init__(self):
        self.logger = LoggingConfig.get_contextual_logger('error_notifier')
        self.notification_handlers = []
    
    def add_notification_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """알림 핸들러 추가"""
        self.notification_handlers.append(handler)
    
    def notify_error(self, error: Exception, context: Dict[str, Any] = None):
        """오류 알림 전송"""
        # 심각한 오류만 알림
        if isinstance(error, CustomError) and error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            error_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'error_type': type(error).__name__,
                'message': str(error),
                'severity': error.severity,
                'category': error.category,
                'context': context or {}
            }
            
            for handler in self.notification_handlers:
                try:
                    handler(error_info)
                except Exception as e:
                    self.logger.error(f"알림 핸들러 실행 실패: {e}")
    
    def email_notification_handler(self, smtp_server: str, smtp_port: int, 
                                 username: str, password: str, recipients: List[str]):
        """이메일 알림 핸들러 생성"""
        def handler(error_info: Dict[str, Any]):
            try:
                msg = MIMEMultipart()
                msg['From'] = username
                msg['To'] = ', '.join(recipients)
                msg['Subject'] = f"[AI Literacy Navigator] {error_info['severity'].upper()} 오류 발생"
                
                body = f"""
오류가 발생했습니다.

시간: {error_info['timestamp']}
오류 유형: {error_info['error_type']}
심각도: {error_info['severity']}
카테고리: {error_info['category']}
메시지: {error_info['message']}

컨텍스트:
{error_info['context']}
                """
                
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                
                self.logger.info(f"오류 알림 이메일 전송 완료: {error_info['error_type']}")
                
            except Exception as e:
                self.logger.error(f"이메일 알림 전송 실패: {e}")
        
        return handler


class ErrorRecoveryManager:
    """오류 복구 관리자"""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.logger = LoggingConfig.get_contextual_logger('error_recovery')
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """복구 전략 등록"""
        self.recovery_strategies[error_type] = strategy
    
    def attempt_recovery(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """오류 복구 시도"""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            try:
                self.logger.info(f"오류 복구 시도: {error_type.__name__}")
                success = self.recovery_strategies[error_type](error, context)
                
                if success:
                    self.logger.info(f"오류 복구 성공: {error_type.__name__}")
                else:
                    self.logger.warning(f"오류 복구 실패: {error_type.__name__}")
                
                return success
                
            except Exception as recovery_error:
                self.logger.error(f"복구 전략 실행 중 오류: {recovery_error}")
                return False
        
        return False


class GlobalErrorHandler:
    """전역 오류 처리기"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.error_tracker = ErrorTracker()
        self.error_notifier = ErrorNotifier()
        self.recovery_manager = ErrorRecoveryManager()
        self.logger = LoggingConfig.get_contextual_logger('global_error_handler')
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask 앱에 오류 처리기 등록"""
        self.app = app
        
        # 일반 예외 처리기
        @app.errorhandler(Exception)
        def handle_general_exception(error):
            return self._handle_error(error)
        
        # HTTP 예외 처리기
        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            return self._handle_http_error(error)
        
        # 데이터베이스 예외 처리기
        @app.errorhandler(SQLAlchemyError)
        def handle_database_exception(error):
            return self._handle_database_error(error)
        
        # 커스텀 예외 처리기들
        @app.errorhandler(CustomError)
        def handle_custom_error(error):
            return self._handle_custom_error(error)
        
        # 복구 전략 등록
        self._register_default_recovery_strategies()
        
        # 알림 핸들러 설정
        self._setup_notification_handlers()
    
    def _handle_error(self, error: Exception):
        """일반 예외 처리"""
        context = self._get_request_context()
        
        # 오류 추적
        self.error_tracker.track_error(error, context)
        
        # 복구 시도
        if self.recovery_manager.attempt_recovery(error, context):
            self.logger.info(f"오류 복구 성공: {type(error).__name__}")
            return error_response("일시적인 문제가 해결되었습니다.", 200)
        
        # 알림 전송
        self.error_notifier.notify_error(error, context)
        
        # 로그 기록
        self.logger.exception(f"처리되지 않은 예외: {error}", extra_fields={
            'error_type': type(error).__name__,
            'context': context
        })
        
        return error_response("서버 내부 오류가 발생했습니다.", 500)
    
    def _handle_http_error(self, error: HTTPException):
        """HTTP 예외 처리"""
        context = self._get_request_context()
        
        self.logger.warning(f"HTTP 오류: {error.code} - {error.description}", extra_fields={
            'status_code': error.code,
            'context': context
        })
        
        return error_response(error.description, error.code)
    
    def _handle_database_error(self, error: SQLAlchemyError):
        """데이터베이스 예외 처리"""
        context = self._get_request_context()
        
        # 데이터베이스 오류로 변환
        db_error = DatabaseError(
            "데이터베이스 오류가 발생했습니다.",
            severity=ErrorSeverity.HIGH,
            details={'original_error': str(error)}
        )
        
        self.error_tracker.track_error(db_error, context)
        self.error_notifier.notify_error(db_error, context)
        
        self.logger.exception(f"데이터베이스 오류: {error}", extra_fields={
            'context': context
        })
        
        return error_response("데이터베이스 처리 중 오류가 발생했습니다.", 500)
    
    def _handle_custom_error(self, error: CustomError):
        """커스텀 예외 처리"""
        context = self._get_request_context()
        
        self.error_tracker.track_error(error, context)
        
        # 심각도에 따른 처리
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.error_notifier.notify_error(error, context)
            self.logger.error(f"심각한 오류: {error.message}", extra_fields={
                'error_code': error.error_code,
                'category': error.category,
                'severity': error.severity,
                'details': error.details,
                'context': context
            })
        else:
            self.logger.warning(f"경고: {error.message}", extra_fields={
                'error_code': error.error_code,
                'category': error.category,
                'context': context
            })
        
        # HTTP 상태 코드 결정
        status_code = self._get_http_status_for_error(error)
        
        return error_response(error.message, status_code, {
            'error_code': error.error_code,
            'category': error.category,
            'details': error.details
        })
    
    def _get_request_context(self) -> Dict[str, Any]:
        """요청 컨텍스트 정보 수집"""
        context = {}
        
        try:
            if request:
                context.update({
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'request_id': getattr(g, 'request_id', None),
                    'user_id': getattr(g, 'current_user_id', None)
                })
        except RuntimeError:
            # 요청 컨텍스트 외부에서 호출된 경우
            pass
        
        return context
    
    def _get_http_status_for_error(self, error: CustomError) -> int:
        """커스텀 오류에 대한 HTTP 상태 코드 결정"""
        if error.category == ErrorCategory.AUTHENTICATION:
            return 401
        elif error.category == ErrorCategory.VALIDATION:
            return 400
        elif error.category == ErrorCategory.EXTERNAL_SERVICE:
            return 503
        elif error.severity == ErrorSeverity.CRITICAL:
            return 500
        else:
            return 400
    
    def _register_default_recovery_strategies(self):
        """기본 복구 전략 등록"""
        
        def database_recovery(error, context):
            """데이터베이스 연결 복구 시도"""
            try:
                from models import db
                db.session.rollback()
                db.session.close()
                # 간단한 연결 테스트
                db.session.execute("SELECT 1")
                return True
            except:
                return False
        
        def external_service_recovery(error, context):
            """외부 서비스 오류 복구 (재시도)"""
            # 실제로는 더 정교한 재시도 로직 구현
            return False
        
        self.recovery_manager.register_recovery_strategy(SQLAlchemyError, database_recovery)
        self.recovery_manager.register_recovery_strategy(ExternalServiceError, external_service_recovery)
    
    def _setup_notification_handlers(self):
        """알림 핸들러 설정"""
        # 환경 변수에서 이메일 설정 읽기
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        admin_emails = os.environ.get('ADMIN_EMAILS', '').split(',')
        
        if smtp_server and smtp_username and smtp_password and admin_emails[0]:
            email_handler = self.error_notifier.email_notification_handler(
                smtp_server, smtp_port, smtp_username, smtp_password, admin_emails
            )
            self.error_notifier.add_notification_handler(email_handler)


# 전역 오류 처리기 인스턴스
global_error_handler = GlobalErrorHandler()


def handle_errors(error_category: str = ErrorCategory.UNKNOWN, 
                 severity: str = ErrorSeverity.MEDIUM):
    """오류 처리 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomError:
                # 커스텀 오류는 그대로 전파
                raise
            except Exception as e:
                # 일반 예외를 커스텀 오류로 변환
                custom_error = CustomError(
                    message=f"{func.__name__} 실행 중 오류 발생: {str(e)}",
                    error_code=f"{func.__name__}_error",
                    category=error_category,
                    severity=severity,
                    details={
                        'function': func.__name__,
                        'module': func.__module__,
                        'original_error': str(e)
                    }
                )
                raise custom_error from e
        
        return wrapper
    return decorator