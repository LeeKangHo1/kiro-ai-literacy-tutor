# utils/auth_middleware.py
# 인증 미들웨어

from flask import request, jsonify, g, current_app
from functools import wraps
from utils.jwt_utils import JWTManager
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """인증 미들웨어 클래스"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 애플리케이션에 미들웨어 초기화"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """요청 전 처리"""
        try:
            # 인증이 필요하지 않은 엔드포인트 목록
            public_endpoints = [
                '/api/auth/register',
                '/api/auth/login',
                '/api/auth/refresh',
                '/health',
                '/api/docs',
                '/'
            ]
            
            # 현재 요청 경로 확인
            current_path = request.path
            
            # 정적 파일이나 공개 엔드포인트는 인증 건너뛰기
            if (current_path.startswith('/static/') or 
                current_path in public_endpoints or
                request.method == 'OPTIONS'):
                return
            
            # JWT 토큰 추출 및 검증
            token = JWTManager.extract_token_from_header()
            if token:
                payload = JWTManager.verify_token(token)
                if payload:
                    g.current_user = {
                        'user_id': payload['user_id'],
                        'user_type': payload['user_type'],
                        'user_level': payload['user_level']
                    }
                    g.is_authenticated = True
                else:
                    g.current_user = None
                    g.is_authenticated = False
            else:
                g.current_user = None
                g.is_authenticated = False
            
        except Exception as e:
            logger.error(f"인증 미들웨어 오류: {str(e)}")
            g.current_user = None
            g.is_authenticated = False
    
    def after_request(self, response):
        """요청 후 처리"""
        try:
            # CORS 헤더 추가
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 
                               'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 
                               'GET,PUT,POST,DELETE,OPTIONS')
            
            # 보안 헤더 추가
            response.headers.add('X-Content-Type-Options', 'nosniff')
            response.headers.add('X-Frame-Options', 'DENY')
            response.headers.add('X-XSS-Protection', '1; mode=block')
            
            return response
            
        except Exception as e:
            logger.error(f"응답 후처리 미들웨어 오류: {str(e)}")
            return response


def require_auth_level(required_level: str):
    """
    특정 사용자 레벨이 필요한 엔드포인트를 위한 데코레이터
    
    Args:
        required_level: 필요한 사용자 레벨 ('low', 'medium', 'high')
    
    사용법:
        @require_auth_level('high')
        def advanced_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 인증 확인
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'success': False,
                        'message': '인증이 필요합니다.',
                        'error_code': 'AUTH_REQUIRED'
                    }), 401
                
                # 레벨 확인
                user_level = g.current_user.get('user_level')
                level_hierarchy = {'low': 1, 'medium': 2, 'high': 3}
                
                required_level_value = level_hierarchy.get(required_level, 0)
                user_level_value = level_hierarchy.get(user_level, 0)
                
                if user_level_value < required_level_value:
                    return jsonify({
                        'success': False,
                        'message': f'이 기능을 사용하려면 {required_level} 레벨 이상이 필요합니다.',
                        'error_code': 'INSUFFICIENT_LEVEL'
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"레벨 인증 데코레이터 오류: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '권한 확인 중 오류가 발생했습니다.',
                    'error_code': 'AUTH_ERROR'
                }), 500
        
        return decorated
    return decorator


def require_user_type(required_type: str):
    """
    특정 사용자 유형이 필요한 엔드포인트를 위한 데코레이터
    
    Args:
        required_type: 필요한 사용자 유형 ('beginner', 'business')
    
    사용법:
        @require_user_type('business')
        def business_only_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 인증 확인
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'success': False,
                        'message': '인증이 필요합니다.',
                        'error_code': 'AUTH_REQUIRED'
                    }), 401
                
                # 사용자 유형 확인
                user_type = g.current_user.get('user_type')
                if user_type != required_type:
                    return jsonify({
                        'success': False,
                        'message': f'이 기능은 {required_type} 사용자만 이용할 수 있습니다.',
                        'error_code': 'INVALID_USER_TYPE'
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"사용자 유형 인증 데코레이터 오류: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '권한 확인 중 오류가 발생했습니다.',
                    'error_code': 'AUTH_ERROR'
                }), 500
        
        return decorated
    return decorator


def get_current_user():
    """
    현재 인증된 사용자 정보 반환
    
    Returns:
        현재 사용자 정보 딕셔너리 또는 None
    """
    return getattr(g, 'current_user', None)


def is_authenticated():
    """
    현재 사용자가 인증되었는지 확인
    
    Returns:
        인증 여부 (bool)
    """
    return getattr(g, 'is_authenticated', False)


def require_auth(f):
    """
    인증이 필요한 엔드포인트를 위한 데코레이터
    
    사용법:
        @require_auth
        def protected_endpoint():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 인증 확인
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'success': False,
                    'message': '인증이 필요합니다.',
                    'error_code': 'AUTH_REQUIRED'
                }), 401
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"인증 데코레이터 오류: {str(e)}")
            return jsonify({
                'success': False,
                'message': '인증 확인 중 오류가 발생했습니다.',
                'error_code': 'AUTH_ERROR'
            }), 500
    
    return decorated


def token_required(f):
    """
    토큰 인증이 필요한 엔드포인트를 위한 데코레이터 (require_auth의 별칭)
    
    사용법:
        @token_required
        def protected_endpoint():
            pass
    """
    return require_auth(f)