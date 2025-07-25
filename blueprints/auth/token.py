# blueprints/auth/token.py
# 토큰 관리 API 엔드포인트

from flask import request, jsonify, g
from . import auth_bp
from models.user import User
from utils.jwt_utils import JWTManager, token_required
from utils.response_utils import success_response, error_response
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    JWT 토큰 갱신 API
    
    Request Body:
    {
        "refresh_token": "기존JWT토큰"
    }
    
    또는 Authorization 헤더 사용:
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Response:
    {
        "success": true,
        "message": "토큰이 갱신되었습니다.",
        "data": {
            "access_token": "새JWT토큰",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    """
    try:
        # 토큰 추출 (헤더 또는 바디에서)
        token = None
        
        # Authorization 헤더에서 토큰 추출 시도
        token = JWTManager.extract_token_from_header()
        
        # 헤더에 없으면 요청 바디에서 추출 시도
        if not token:
            data = request.get_json()
            if data and data.get('refresh_token'):
                token = data['refresh_token']
        
        if not token:
            return error_response("갱신할 토큰이 제공되지 않았습니다.", 400)
        
        # 토큰 갱신
        new_token = JWTManager.refresh_token(token)
        if not new_token:
            return error_response("유효하지 않거나 만료된 토큰입니다.", 401)
        
        logger.info("JWT 토큰 갱신 완료")
        
        # 응답 데이터 구성
        response_data = {
            'access_token': new_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1시간 (초 단위)
        }
        
        return success_response("토큰이 갱신되었습니다.", response_data)
        
    except Exception as e:
        logger.error(f"토큰 갱신 중 오류 발생: {str(e)}")
        return error_response("토큰 갱신 중 오류가 발생했습니다.", 500)


@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    JWT 토큰 검증 API
    
    Request Body:
    {
        "token": "검증할JWT토큰"
    }
    
    또는 Authorization 헤더 사용:
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Response:
    {
        "success": true,
        "message": "유효한 토큰입니다.",
        "data": {
            "valid": true,
            "user_id": 1,
            "user_type": "beginner",
            "user_level": "low",
            "expires_at": "2024-01-01T12:00:00Z"
        }
    }
    """
    try:
        # 토큰 추출 (헤더 또는 바디에서)
        token = None
        
        # Authorization 헤더에서 토큰 추출 시도
        token = JWTManager.extract_token_from_header()
        
        # 헤더에 없으면 요청 바디에서 추출 시도
        if not token:
            data = request.get_json()
            if data and data.get('token'):
                token = data['token']
        
        if not token:
            return error_response("검증할 토큰이 제공되지 않았습니다.", 400)
        
        # 토큰 검증
        payload = JWTManager.verify_token(token)
        if not payload:
            return success_response("토큰 검증 완료", {
                'valid': False,
                'message': '유효하지 않거나 만료된 토큰입니다.'
            })
        
        # 사용자 존재 여부 확인
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return success_response("토큰 검증 완료", {
                'valid': False,
                'message': '사용자가 존재하지 않거나 비활성화되었습니다.'
            })
        
        logger.info(f"토큰 검증 성공 - 사용자 ID: {payload['user_id']}")
        
        # 응답 데이터 구성
        response_data = {
            'valid': True,
            'user_id': payload['user_id'],
            'user_type': payload['user_type'],
            'user_level': payload['user_level'],
            'issued_at': datetime.fromtimestamp(payload['iat']).isoformat(),
            'expires_at': datetime.fromtimestamp(payload['exp']).isoformat()
        }
        
        return success_response("유효한 토큰입니다.", response_data)
        
    except Exception as e:
        logger.error(f"토큰 검증 중 오류 발생: {str(e)}")
        return error_response("토큰 검증 중 오류가 발생했습니다.", 500)


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    비밀번호 변경 API
    
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Request Body:
    {
        "current_password": "현재비밀번호",
        "new_password": "새비밀번호"
    }
    
    Response:
    {
        "success": true,
        "message": "비밀번호가 변경되었습니다."
    }
    """
    try:
        # 현재 사용자 정보 가져오기
        current_user_info = g.current_user
        user_id = current_user_info['user_id']
        
        # 데이터베이스에서 사용자 조회
        user = User.query.get(user_id)
        if not user:
            return error_response("사용자를 찾을 수 없습니다.", 404)
        
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return error_response("현재 비밀번호와 새 비밀번호를 모두 입력해주세요.", 400)
        
        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            logger.warning(f"비밀번호 변경 실패 - 잘못된 현재 비밀번호, 사용자 ID: {user_id}")
            return error_response("현재 비밀번호가 올바르지 않습니다.", 401)
        
        # 새 비밀번호 강도 검증
        from utils.password_utils import validate_password
        is_valid, error_message = validate_password(new_password)
        if not is_valid:
            return error_response(error_message, 400)
        
        # 현재 비밀번호와 동일한지 확인
        if user.check_password(new_password):
            return error_response("새 비밀번호는 현재 비밀번호와 달라야 합니다.", 400)
        
        # 비밀번호 변경
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        user.save()
        
        logger.info(f"비밀번호 변경 완료 - 사용자 ID: {user_id}")
        
        return success_response("비밀번호가 변경되었습니다.")
        
    except Exception as e:
        logger.error(f"비밀번호 변경 중 오류 발생: {str(e)}")
        return error_response("비밀번호 변경 중 오류가 발생했습니다.", 500)


@auth_bp.route('/deactivate', methods=['POST'])
@token_required
def deactivate_account():
    """
    계정 비활성화 API
    
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Request Body:
    {
        "password": "비밀번호확인",
        "reason": "비활성화사유" (선택사항)
    }
    
    Response:
    {
        "success": true,
        "message": "계정이 비활성화되었습니다."
    }
    """
    try:
        # 현재 사용자 정보 가져오기
        current_user_info = g.current_user
        user_id = current_user_info['user_id']
        
        # 데이터베이스에서 사용자 조회
        user = User.query.get(user_id)
        if not user:
            return error_response("사용자를 찾을 수 없습니다.", 404)
        
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        password = data.get('password', '')
        reason = data.get('reason', '')
        
        if not password:
            return error_response("비밀번호를 입력해주세요.", 400)
        
        # 비밀번호 확인
        if not user.check_password(password):
            logger.warning(f"계정 비활성화 실패 - 잘못된 비밀번호, 사용자 ID: {user_id}")
            return error_response("비밀번호가 올바르지 않습니다.", 401)
        
        # 계정 비활성화
        user.is_active = False
        user.updated_at = datetime.utcnow()
        user.save()
        
        logger.info(f"계정 비활성화 완료 - 사용자 ID: {user_id}, 사유: {reason}")
        
        return success_response("계정이 비활성화되었습니다.")
        
    except Exception as e:
        logger.error(f"계정 비활성화 중 오류 발생: {str(e)}")
        return error_response("계정 비활성화 중 오류가 발생했습니다.", 500)