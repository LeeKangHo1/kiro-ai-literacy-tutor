# blueprints/auth/login.py
# 로그인 API 엔드포인트

from flask import request, jsonify, g
from . import auth_bp
from services.auth_service import AuthService
from utils.response_utils import create_response
from utils.jwt_utils import token_required
import logging

logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    사용자 로그인 API
    
    Request Body:
    {
        "username_or_email": "사용자명 또는 이메일",
        "password": "비밀번호"
    }
    
    Response:
    {
        "success": true,
        "message": "로그인이 완료되었습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "user_type": "beginner",
                "user_level": "low",
                "last_login": "2024-01-01T00:00:00"
            },
            "token": "jwt_token_here"
        }
    }
    """
    try:
        # Content-Type 확인
        if not request.is_json:
            return jsonify(create_response(
                success=False,
                message="Content-Type은 application/json이어야 합니다.",
                error_code="INVALID_CONTENT_TYPE"
            )), 400
        
        # 요청 데이터 추출
        data = request.get_json()
        if not data:
            return jsonify(create_response(
                success=False,
                message="요청 데이터가 없습니다.",
                error_code="NO_DATA"
            )), 400
        
        # 필수 필드 확인
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify(create_response(
                success=False,
                message="사용자명/이메일과 비밀번호를 입력해주세요.",
                error_code="MISSING_CREDENTIALS"
            )), 400
        
        # 로그인 처리
        result = AuthService.login_user(username_or_email, password)
        
        # 응답 상태 코드 결정
        status_code = 200 if result['success'] else 401
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code == 'INVALID_CREDENTIALS':
                status_code = 401  # Unauthorized
            elif error_code == 'ACCOUNT_DISABLED':
                status_code = 403  # Forbidden
            elif error_code == 'MISSING_CREDENTIALS':
                status_code = 400  # Bad Request
            else:
                status_code = 500  # Internal Server Error
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"로그인 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    사용자 로그아웃 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "로그아웃이 완료되었습니다."
    }
    
    Note: JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없습니다.
    클라이언트에서 토큰을 삭제하는 것으로 로그아웃을 처리합니다.
    향후 토큰 블랙리스트 기능을 추가할 수 있습니다.
    """
    try:
        user_id = g.current_user['user_id']
        logger.info(f"사용자 로그아웃 - user_id: {user_id}")
        
        return jsonify(create_response(
            success=True,
            message="로그아웃이 완료되었습니다.",
            data={
                'logged_out_at': __import__('datetime').datetime.utcnow().isoformat()
            }
        )), 200
        
    except Exception as e:
        logger.error(f"로그아웃 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """
    JWT 토큰 검증 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "유효한 토큰입니다.",
        "data": {
            "user": {
                "user_id": 1,
                "user_type": "beginner",
                "user_level": "low"
            },
            "token_info": {
                "issued_at": "2024-01-01T00:00:00",
                "expires_at": "2024-01-01T01:00:00"
            }
        }
    }
    """
    try:
        # 토큰에서 추출된 사용자 정보 (token_required 데코레이터에서 설정)
        current_user = g.current_user
        
        # 토큰 정보 추가
        from utils.jwt_utils import JWTManager
        token = JWTManager.extract_token_from_header()
        payload = JWTManager.verify_token(token) if token else None
        
        token_info = {}
        if payload:
            token_info = {
                'issued_at': __import__('datetime').datetime.fromtimestamp(payload['iat']).isoformat(),
                'expires_at': __import__('datetime').datetime.fromtimestamp(payload['exp']).isoformat()
            }
        
        return jsonify(create_response(
            success=True,
            message="유효한 토큰입니다.",
            data={
                'user': current_user,
                'token_info': token_info
            }
        )), 200
        
    except Exception as e:
        logger.error(f"토큰 검증 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    현재 로그인한 사용자 정보 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "사용자 정보를 조회했습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "user_type": "beginner",
                "user_level": "low",
                "created_at": "2024-01-01T00:00:00",
                "is_active": true
            },
            "progress_summary": {
                "total_chapters": 5,
                "completed_chapters": 2,
                "in_progress_chapters": 1,
                "average_understanding": 85.5,
                "total_study_time": 120
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # AuthService를 통해 사용자 프로필 조회
        result = AuthService.get_user_profile(user_id)
        
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"현재 사용자 정보 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500