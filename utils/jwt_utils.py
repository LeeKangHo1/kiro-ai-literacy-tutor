# utils/jwt_utils.py
# JWT 토큰 유틸리티

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, g
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """JWT 토큰 관리 클래스"""
    
    @staticmethod
    def generate_token(user_id: int, user_type: str, user_level: str) -> str:
        """
        JWT 토큰 생성
        
        Args:
            user_id: 사용자 ID
            user_type: 사용자 유형 (beginner, business)
            user_level: 사용자 레벨 (low, medium, high)
            
        Returns:
            JWT 토큰 문자열
        """
        try:
            payload = {
                'user_id': user_id,
                'user_type': user_type,
                'user_level': user_level,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
            }
            
            token = jwt.encode(
                payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            logger.info(f"JWT 토큰 생성 완료 - 사용자 ID: {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"JWT 토큰 생성 실패: {str(e)}")
            raise Exception("토큰 생성에 실패했습니다.")
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        JWT 토큰 검증
        
        Args:
            token: JWT 토큰 문자열
            
        Returns:
            토큰 페이로드 또는 None (검증 실패 시)
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # 토큰 만료 확인
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("만료된 JWT 토큰 접근 시도")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("만료된 JWT 토큰")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"유효하지 않은 JWT 토큰: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT 토큰 검증 오류: {str(e)}")
            return None
    
    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        """
        JWT 토큰 갱신
        
        Args:
            token: 기존 JWT 토큰
            
        Returns:
            새로운 JWT 토큰 또는 None (갱신 실패 시)
        """
        try:
            payload = JWTManager.verify_token(token)
            if not payload:
                return None
            
            # 새로운 토큰 생성
            new_token = JWTManager.generate_token(
                payload['user_id'],
                payload['user_type'],
                payload['user_level']
            )
            
            logger.info(f"JWT 토큰 갱신 완료 - 사용자 ID: {payload['user_id']}")
            return new_token
            
        except Exception as e:
            logger.error(f"JWT 토큰 갱신 실패: {str(e)}")
            return None
    
    @staticmethod
    def extract_token_from_header() -> Optional[str]:
        """
        HTTP 헤더에서 JWT 토큰 추출
        
        Returns:
            JWT 토큰 문자열 또는 None
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # "Bearer <token>" 형식에서 토큰 추출
            token_parts = auth_header.split(' ')
            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                return None
            
            return token_parts[1]
            
        except Exception as e:
            logger.error(f"토큰 헤더 파싱 오류: {str(e)}")
            return None


def token_required(f):
    """
    JWT 토큰 인증이 필요한 엔드포인트를 위한 데코레이터
    
    사용법:
        @token_required
        def protected_endpoint():
            # g.current_user로 현재 사용자 정보 접근 가능
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 헤더에서 토큰 추출
            token = JWTManager.extract_token_from_header()
            if not token:
                return jsonify({
                    'success': False,
                    'message': '인증 토큰이 필요합니다.',
                    'error_code': 'TOKEN_MISSING'
                }), 401
            
            # 토큰 검증
            payload = JWTManager.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'message': '유효하지 않거나 만료된 토큰입니다.',
                    'error_code': 'TOKEN_INVALID'
                }), 401
            
            # 현재 사용자 정보를 g 객체에 저장
            g.current_user = {
                'user_id': payload['user_id'],
                'user_type': payload['user_type'],
                'user_level': payload['user_level']
            }
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"토큰 인증 데코레이터 오류: {str(e)}")
            return jsonify({
                'success': False,
                'message': '인증 처리 중 오류가 발생했습니다.',
                'error_code': 'AUTH_ERROR'
            }), 500
    
    return decorated


def optional_token(f):
    """
    선택적 JWT 토큰 인증 데코레이터
    토큰이 있으면 검증하고, 없어도 요청을 처리함
    
    사용법:
        @optional_token
        def public_endpoint():
            # g.current_user가 있으면 인증된 사용자, 없으면 익명 사용자
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 헤더에서 토큰 추출
            token = JWTManager.extract_token_from_header()
            
            if token:
                # 토큰이 있으면 검증
                payload = JWTManager.verify_token(token)
                if payload:
                    g.current_user = {
                        'user_id': payload['user_id'],
                        'user_type': payload['user_type'],
                        'user_level': payload['user_level']
                    }
                else:
                    # 토큰이 유효하지 않으면 익명 사용자로 처리
                    g.current_user = None
            else:
                # 토큰이 없으면 익명 사용자로 처리
                g.current_user = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"선택적 토큰 인증 데코레이터 오류: {str(e)}")
            # 오류가 발생해도 요청을 계속 처리
            g.current_user = None
            return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    관리자 권한이 필요한 엔드포인트를 위한 데코레이터
    (향후 확장을 위해 준비)
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        # 현재는 모든 인증된 사용자를 허용
        # 향후 관리자 권한 체크 로직 추가 가능
        return f(*args, **kwargs)
    
    return decorated