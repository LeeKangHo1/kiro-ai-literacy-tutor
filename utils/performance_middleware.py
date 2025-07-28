# utils/performance_middleware.py
"""
성능 모니터링 미들웨어
"""

import time
import logging
from functools import wraps
from flask import request, g, jsonify
from services.performance_service import performance_monitor, monitor_api_performance

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """성능 모니터링 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 미들웨어 등록"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """요청 시작 시 실행"""
        g.start_time = time.time()
        g.request_id = f"{int(time.time() * 1000)}_{id(request)}"
        
        # 요청 정보 로깅
        logger.info(f"[{g.request_id}] {request.method} {request.path} 시작")
    
    def after_request(self, response):
        """응답 전송 전 실행"""
        if hasattr(g, 'start_time'):
            execution_time = time.time() - g.start_time
            
            # 성능 메트릭 기록
            endpoint = f"{request.method} {request.endpoint or request.path}"
            performance_monitor.record_api_time(endpoint, execution_time, response.status_code)
            
            # 응답 헤더에 실행 시간 추가
            response.headers['X-Response-Time'] = f"{execution_time:.3f}s"
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            
            # 느린 요청 로깅
            if execution_time > 2.0:
                logger.warning(
                    f"[{g.request_id}] 느린 요청: {endpoint} - "
                    f"{execution_time:.3f}초 (상태: {response.status_code})"
                )
            else:
                logger.info(
                    f"[{g.request_id}] {endpoint} 완료 - "
                    f"{execution_time:.3f}초 (상태: {response.status_code})"
                )
        
        return response
    
    def teardown_request(self, exception):
        """요청 종료 시 실행"""
        if exception:
            logger.error(f"[{getattr(g, 'request_id', 'unknown')}] 요청 처리 중 예외 발생: {exception}")


def performance_monitoring(endpoint_name: str = None):
    """성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 엔드포인트 이름 결정
            name = endpoint_name or f"{request.method} {func.__name__}"
            
            start_time = time.time()
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                
                # 응답에서 상태 코드 추출
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                return result
                
            except Exception as e:
                status_code = 500
                logger.error(f"엔드포인트 {name} 실행 오류: {e}")
                raise
            
            finally:
                execution_time = time.time() - start_time
                performance_monitor.record_api_time(name, execution_time, status_code)
        
        return wrapper
    return decorator


def database_monitoring(query_name: str):
    """데이터베이스 쿼리 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_query_time(query_name, execution_time)
                
                # 느린 쿼리 로깅
                if execution_time > 1.0:
                    logger.warning(f"느린 쿼리: {query_name} - {execution_time:.3f}초")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_query_time(f"{query_name}_error", execution_time)
                logger.error(f"쿼리 {query_name} 실행 오류: {e}")
                raise
        
        return wrapper
    return decorator


class RequestLimiter:
    """요청 제한 클래스"""
    
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.requests = {}  # IP별 요청 기록
    
    def is_allowed(self, client_ip: str) -> bool:
        """요청 허용 여부 확인"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # 해당 IP의 요청 기록 정리 (1분 이전 기록 삭제)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > minute_ago
            ]
        else:
            self.requests[client_ip] = []
        
        # 현재 요청 수 확인
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # 현재 요청 기록
        self.requests[client_ip].append(current_time)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """남은 요청 수 반환"""
        current_requests = len(self.requests.get(client_ip, []))
        return max(0, self.max_requests - current_requests)


# 전역 요청 제한기 인스턴스
request_limiter = RequestLimiter()


def rate_limit(max_requests: int = 60):
    """요청 제한 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            if not request_limiter.is_allowed(client_ip):
                logger.warning(f"요청 제한 초과: {client_ip}")
                return jsonify({
                    'error': '요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요.',
                    'retry_after': 60
                }), 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class HealthChecker:
    """시스템 상태 확인 클래스"""
    
    @staticmethod
    def check_database_health():
        """데이터베이스 상태 확인"""
        try:
            from models import db
            db.session.execute("SELECT 1")
            return {'status': 'healthy', 'message': '데이터베이스 연결 정상'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'데이터베이스 연결 실패: {e}'}
    
    @staticmethod
    def check_external_services():
        """외부 서비스 상태 확인"""
        services_status = {}
        
        # ChromaDB 상태 확인
        try:
            from services.chromadb_service import chromadb_service
            # 간단한 연결 테스트
            services_status['chromadb'] = {'status': 'healthy', 'message': 'ChromaDB 연결 정상'}
        except Exception as e:
            services_status['chromadb'] = {'status': 'unhealthy', 'message': f'ChromaDB 연결 실패: {e}'}
        
        # OpenAI API 상태 확인 (실제 호출 없이 설정만 확인)
        try:
            import os
            if os.environ.get('OPENAI_API_KEY'):
                services_status['openai'] = {'status': 'healthy', 'message': 'OpenAI API 키 설정됨'}
            else:
                services_status['openai'] = {'status': 'unhealthy', 'message': 'OpenAI API 키 미설정'}
        except Exception as e:
            services_status['openai'] = {'status': 'unhealthy', 'message': f'OpenAI 설정 확인 실패: {e}'}
        
        return services_status
    
    @staticmethod
    def get_system_health():
        """전체 시스템 상태 확인"""
        health_status = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # 데이터베이스 상태
        db_health = HealthChecker.check_database_health()
        health_status['components']['database'] = db_health
        
        # 외부 서비스 상태
        external_services = HealthChecker.check_external_services()
        health_status['components'].update(external_services)
        
        # 전체 상태 결정
        unhealthy_components = [
            name for name, status in health_status['components'].items()
            if status['status'] == 'unhealthy'
        ]
        
        if unhealthy_components:
            health_status['overall_status'] = 'degraded' if len(unhealthy_components) == 1 else 'unhealthy'
            health_status['unhealthy_components'] = unhealthy_components
        
        return health_status


# 전역 상태 확인기 인스턴스
health_checker = HealthChecker()