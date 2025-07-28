# utils/logging_config.py
"""
구조화된 로깅 시스템 설정
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, has_request_context
import traceback


class StructuredFormatter(logging.Formatter):
    """구조화된 JSON 로그 포매터"""
    
    def __init__(self, include_extra_fields=True):
        super().__init__()
        self.include_extra_fields = include_extra_fields
    
    def format(self, record):
        """로그 레코드를 JSON 형태로 포맷"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread
        }
        
        # 요청 컨텍스트 정보 추가
        if has_request_context():
            try:
                log_entry.update({
                    'request_id': getattr(g, 'request_id', None),
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'user_id': getattr(g, 'current_user_id', None)
                })
            except Exception:
                # 요청 컨텍스트 정보 추가 실패 시 무시
                pass
        
        # 예외 정보 추가
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # 추가 필드 포함
        if self.include_extra_fields and hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # 성능 관련 정보
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        
        if hasattr(record, 'query_info'):
            log_entry['query_info'] = record.query_info
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ContextualLogger:
    """컨텍스트 정보를 포함한 로거 래퍼"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.extra_context = {}
    
    def set_context(self, **kwargs):
        """로깅 컨텍스트 설정"""
        self.extra_context.update(kwargs)
    
    def clear_context(self):
        """로깅 컨텍스트 초기화"""
        self.extra_context.clear()
    
    def _log_with_context(self, level, message, extra_fields=None, **kwargs):
        """컨텍스트와 함께 로그 기록"""
        combined_extra = self.extra_context.copy()
        if extra_fields:
            combined_extra.update(extra_fields)
        
        # LogRecord에 추가 필드 전달
        extra = {'extra_fields': combined_extra}
        extra.update(kwargs)
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message, **kwargs):
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message, **kwargs):
        """예외 정보와 함께 에러 로그 기록"""
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)


class LoggingConfig:
    """로깅 설정 관리 클래스"""
    
    @staticmethod
    def setup_logging(app=None, log_level='INFO', log_file='app.log', max_file_size=10*1024*1024, backup_count=5):
        """로깅 시스템 초기화"""
        
        # 로그 레벨 설정
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # 개발 환경에서는 간단한 포맷, 프로덕션에서는 JSON 포맷
        if app and app.config.get('DEBUG'):
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            console_formatter = StructuredFormatter()
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 파일 핸들러 설정 (회전 로그)
        if log_file:
            # 로그 디렉토리 생성
            log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(StructuredFormatter())
            root_logger.addHandler(file_handler)
        
        # 에러 전용 파일 핸들러
        error_log_file = log_file.replace('.log', '_error.log') if log_file else 'logs/error.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)
        
        # 특정 라이브러리 로그 레벨 조정
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        # Flask 앱에 로깅 설정 적용
        if app:
            app.logger.handlers = root_logger.handlers
            app.logger.setLevel(numeric_level)
        
        logging.info("로깅 시스템 초기화 완료")
    
    @staticmethod
    def get_contextual_logger(name: str) -> ContextualLogger:
        """컨텍스트 로거 생성"""
        return ContextualLogger(name)


class LogAnalyzer:
    """로그 분석 도구"""
    
    @staticmethod
    def analyze_log_file(log_file_path: str, hours: int = 24) -> Dict[str, Any]:
        """로그 파일 분석"""
        try:
            analysis = {
                'total_entries': 0,
                'level_counts': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
                'error_patterns': {},
                'slow_operations': [],
                'top_modules': {},
                'request_stats': {'total_requests': 0, 'avg_response_time': 0},
                'analysis_period_hours': hours
            }
            
            cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
            total_response_time = 0
            response_time_count = 0
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # 시간 필터링
                        log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00')).timestamp()
                        if log_time < cutoff_time:
                            continue
                        
                        analysis['total_entries'] += 1
                        
                        # 레벨별 카운트
                        level = log_entry.get('level', 'UNKNOWN')
                        if level in analysis['level_counts']:
                            analysis['level_counts'][level] += 1
                        
                        # 모듈별 통계
                        module = log_entry.get('module', 'unknown')
                        analysis['top_modules'][module] = analysis['top_modules'].get(module, 0) + 1
                        
                        # 에러 패턴 분석
                        if level in ['ERROR', 'CRITICAL']:
                            message = log_entry.get('message', '')
                            # 간단한 패턴 매칭 (실제로는 더 정교한 분석 가능)
                            error_type = message.split(':')[0] if ':' in message else message[:50]
                            analysis['error_patterns'][error_type] = analysis['error_patterns'].get(error_type, 0) + 1
                        
                        # 느린 작업 감지
                        if 'execution_time' in log_entry and log_entry['execution_time'] > 2.0:
                            analysis['slow_operations'].append({
                                'timestamp': log_entry['timestamp'],
                                'module': module,
                                'function': log_entry.get('function', ''),
                                'execution_time': log_entry['execution_time'],
                                'message': log_entry.get('message', '')[:100]
                            })
                        
                        # 요청 통계
                        if 'method' in log_entry:
                            analysis['request_stats']['total_requests'] += 1
                            if 'execution_time' in log_entry:
                                total_response_time += log_entry['execution_time']
                                response_time_count += 1
                    
                    except (json.JSONDecodeError, KeyError):
                        # JSON 파싱 실패 시 무시
                        continue
            
            # 평균 응답 시간 계산
            if response_time_count > 0:
                analysis['request_stats']['avg_response_time'] = total_response_time / response_time_count
            
            # 상위 모듈 정렬
            analysis['top_modules'] = dict(sorted(
                analysis['top_modules'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10])
            
            # 느린 작업 정렬
            analysis['slow_operations'] = sorted(
                analysis['slow_operations'], 
                key=lambda x: x['execution_time'], 
                reverse=True
            )[:20]
            
            return analysis
            
        except Exception as e:
            logging.error(f"로그 분석 실패: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_recent_errors(log_file_path: str, hours: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 에러 로그 조회"""
        try:
            errors = []
            cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # 시간 및 레벨 필터링
                        log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00')).timestamp()
                        if log_time < cutoff_time or log_entry.get('level') not in ['ERROR', 'CRITICAL']:
                            continue
                        
                        errors.append({
                            'timestamp': log_entry['timestamp'],
                            'level': log_entry['level'],
                            'message': log_entry['message'],
                            'module': log_entry.get('module', ''),
                            'function': log_entry.get('function', ''),
                            'exception': log_entry.get('exception', {}),
                            'request_id': log_entry.get('request_id', ''),
                            'user_id': log_entry.get('user_id', '')
                        })
                        
                        if len(errors) >= limit:
                            break
                    
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return sorted(errors, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logging.error(f"최근 에러 조회 실패: {e}")
            return []


# 전역 로거 인스턴스들
app_logger = LoggingConfig.get_contextual_logger('app')
db_logger = LoggingConfig.get_contextual_logger('database')
api_logger = LoggingConfig.get_contextual_logger('api')
agent_logger = LoggingConfig.get_contextual_logger('agent')
performance_logger = LoggingConfig.get_contextual_logger('performance')


def log_function_call(logger_name: str = 'app'):
    """함수 호출 로깅 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = LoggingConfig.get_contextual_logger(logger_name)
            
            start_time = datetime.utcnow()
            logger.info(f"{func.__name__} 함수 호출 시작", extra_fields={
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(f"{func.__name__} 함수 호출 완료", extra_fields={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'success': True
                })
                
                return result
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.exception(f"{func.__name__} 함수 호출 실패: {e}", extra_fields={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'success': False,
                    'error_type': type(e).__name__
                })
                
                raise
        
        return wrapper
    return decorator