# blueprints/auth/token.py
# JWT 토큰 관리 API 엔드포인트

from flask import request, jsonify, g
from . import auth_bp
from services.auth_service import AuthService
from utils.response_utils import create_response
from utils.jwt_utils import JWTManager, token_required
import logging

logger = logging.getLogger(__name__)

@auth_bp.route('/token/refresh', methods=['POST'])
def refresh_token():
    """
    JWT 토큰 갱신 API
    
    Request Body:
    {
        "token": "현재_jwt_token"
    }
    
    또는 Authorization 헤더 사용:
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "토큰이 갱신되었습니다.",
        "data": {
            "token": "새로운_jwt_token",
            "user_id": 1,
            "expires_at": 1640995200
        }
    }
    """
    try:
        # 토큰 추출 (Body 또는 Header에서)
        token = None
        
        # 1. Authorization 헤더에서 토큰 추출 시도
        token = JWTManager.extract_token_from_header()
        
        # 2. 헤더에 없으면 요청 Body에서 추출 시도
        if not token and request.is_json:
            data = request.get_json()
            if data:
                token = data.get('token')
        
        if not token:
            return jsonify(create_response(
                success=False,
                message="갱신할 토큰이 제공되지 않았습니다.",
                error_code="TOKEN_MISSING"
            )), 400
        
        # 토큰 갱신 처리
        result = AuthService.refresh_token(token)
        
        # 응답 상태 코드 결정
        status_code = 200 if result['success'] else 401
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code in ['TOKEN_REFRESH_FAILED', 'INVALID_REFRESHED_TOKEN']:
                status_code = 401  # Unauthorized
            else:
                status_code = 500  # Internal Server Error
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"토큰 갱신 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/token/validate', methods=['POST'])
def validate_token():
    """
    JWT 토큰 유효성 검증 API
    
    Request Body:
    {
        "token": "검증할_jwt_token"
    }
    
    또는 Authorization 헤더 사용:
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "유효한 토큰입니다.",
        "data": {
            "valid": true,
            "user_id": 1,
            "user_type": "beginner",
            "user_level": "low",
            "issued_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T01:00:00",
            "remaining_time": 3600
        }
    }
    """
    try:
        # 토큰 추출 (Body 또는 Header에서)
        token = None
        
        # 1. Authorization 헤더에서 토큰 추출 시도
        token = JWTManager.extract_token_from_header()
        
        # 2. 헤더에 없으면 요청 Body에서 추출 시도
        if not token and request.is_json:
            data = request.get_json()
            if data:
                token = data.get('token')
        
        if not token:
            return jsonify(create_response(
                success=False,
                message="검증할 토큰이 제공되지 않았습니다.",
                error_code="TOKEN_MISSING",
                data={'valid': False}
            )), 400
        
        # 토큰 검증
        payload = JWTManager.verify_token(token)
        
        if not payload:
            return jsonify(create_response(
                success=False,
                message="유효하지 않거나 만료된 토큰입니다.",
                error_code="INVALID_TOKEN",
                data={'valid': False}
            )), 401
        
        # 토큰 정보 구성
        import datetime
        issued_at = datetime.datetime.fromtimestamp(payload['iat'])
        expires_at = datetime.datetime.fromtimestamp(payload['exp'])
        remaining_time = int((expires_at - datetime.datetime.utcnow()).total_seconds())
        
        return jsonify(create_response(
            success=True,
            message="유효한 토큰입니다.",
            data={
                'valid': True,
                'user_id': payload['user_id'],
                'user_type': payload['user_type'],
                'user_level': payload['user_level'],
                'issued_at': issued_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'remaining_time': max(0, remaining_time)  # 음수 방지
            }
        )), 200
        
    except Exception as e:
        logger.error(f"토큰 검증 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR",
            data={'valid': False}
        )), 500


@auth_bp.route('/token/info', methods=['GET'])
@token_required
def get_token_info():
    """
    현재 토큰 정보 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "토큰 정보를 조회했습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "user_type": "beginner",
                "user_level": "low"
            },
            "token_info": {
                "issued_at": "2024-01-01T00:00:00",
                "expires_at": "2024-01-01T01:00:00",
                "remaining_time": 3600,
                "is_expired": false
            }
        }
    }
    """
    try:
        # 현재 사용자 정보 (token_required 데코레이터에서 설정)
        current_user = g.current_user
        
        # 토큰 정보 추출
        token = JWTManager.extract_token_from_header()
        payload = JWTManager.verify_token(token) if token else None
        
        if not payload:
            return jsonify(create_response(
                success=False,
                message="토큰 정보를 가져올 수 없습니다.",
                error_code="TOKEN_INFO_ERROR"
            )), 500
        
        # 토큰 정보 구성
        import datetime
        issued_at = datetime.datetime.fromtimestamp(payload['iat'])
        expires_at = datetime.datetime.fromtimestamp(payload['exp'])
        now = datetime.datetime.utcnow()
        remaining_time = int((expires_at - now).total_seconds())
        is_expired = now > expires_at
        
        return jsonify(create_response(
            success=True,
            message="토큰 정보를 조회했습니다.",
            data={
                'user': current_user,
                'token_info': {
                    'issued_at': issued_at.isoformat(),
                    'expires_at': expires_at.isoformat(),
                    'remaining_time': max(0, remaining_time),
                    'is_expired': is_expired
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"토큰 정보 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/token/revoke', methods=['POST'])
@token_required
def revoke_token():
    """
    토큰 무효화 API (향후 확장용)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "토큰이 무효화되었습니다."
    }
    
    Note: 현재는 JWT의 stateless 특성상 실제 무효화는 구현되지 않았습니다.
    향후 Redis 등을 사용한 토큰 블랙리스트 기능을 추가할 수 있습니다.
    """
    try:
        user_id = g.current_user['user_id']
        
        # TODO: 향후 토큰 블랙리스트 기능 구현
        # - Redis에 토큰 저장
        # - 토큰 검증 시 블랙리스트 확인
        
        logger.info(f"토큰 무효화 요청 - user_id: {user_id}")
        
        return jsonify(create_response(
            success=True,
            message="토큰 무효화 요청이 처리되었습니다. 클라이언트에서 토큰을 삭제해주세요.",
            data={
                'revoked_at': __import__('datetime').datetime.utcnow().isoformat(),
                'note': "JWT의 특성상 서버에서 즉시 무효화되지 않습니다. 클라이언트에서 토큰을 삭제하여 로그아웃 처리하세요."
            }
        )), 200
        
    except Exception as e:
        logger.error(f"토큰 무효화 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500