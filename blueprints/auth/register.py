# blueprints/auth/register.py
# 회원가입 API 엔드포인트

from flask import request, jsonify
from . import auth_bp
from services.auth_service import AuthService
from utils.response_utils import create_response
import logging

logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    사용자 회원가입 API
    
    Request Body:
    {
        "username": "사용자명",
        "email": "이메일",
        "password": "비밀번호",
        "user_type": "beginner|business"
    }
    
    Response:
    {
        "success": true,
        "message": "회원가입이 완료되었습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "user_type": "beginner",
                "user_level": "low",
                "created_at": "2024-01-01T00:00:00"
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
        required_fields = ['username', 'email', 'password', 'user_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify(create_response(
                success=False,
                message=f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}",
                error_code="MISSING_FIELDS"
            )), 400
        
        # 회원가입 처리
        result = AuthService.register_user(
            username=data['username'].strip(),
            email=data['email'].strip().lower(),
            password=data['password'],
            user_type=data['user_type']
        )
        
        # 응답 상태 코드 결정
        status_code = 201 if result['success'] else 400
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code in ['USERNAME_EXISTS', 'EMAIL_EXISTS']:
                status_code = 409  # Conflict
            elif error_code in ['INVALID_USERNAME', 'INVALID_EMAIL', 'WEAK_PASSWORD', 'INVALID_USER_TYPE']:
                status_code = 400  # Bad Request
            else:
                status_code = 500  # Internal Server Error
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"회원가입 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    """
    사용자명 중복 확인 API
    
    Request Body:
    {
        "username": "확인할_사용자명"
    }
    
    Response:
    {
        "success": true,
        "message": "사용 가능한 사용자명입니다.",
        "data": {
            "available": true
        }
    }
    """
    try:
        if not request.is_json:
            return jsonify(create_response(
                success=False,
                message="Content-Type은 application/json이어야 합니다.",
                error_code="INVALID_CONTENT_TYPE"
            )), 400
        
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify(create_response(
                success=False,
                message="사용자명을 입력해주세요.",
                error_code="MISSING_USERNAME"
            )), 400
        
        # 사용자명 형식 검증
        from utils.validation_utils import ValidationUtils
        if not ValidationUtils.validate_username(username):
            return jsonify(create_response(
                success=False,
                message="사용자명은 3-50자의 영문, 숫자, 언더스코어만 사용 가능합니다.",
                error_code="INVALID_USERNAME_FORMAT"
            )), 400
        
        # 중복 확인
        from models.user import User
        existing_user = User.get_by_username(username)
        available = existing_user is None
        
        return jsonify(create_response(
            success=True,
            message="사용 가능한 사용자명입니다." if available else "이미 사용 중인 사용자명입니다.",
            data={
                'available': available,
                'username': username
            }
        )), 200
        
    except Exception as e:
        logger.error(f"사용자명 중복 확인 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    이메일 중복 확인 API
    
    Request Body:
    {
        "email": "확인할_이메일@example.com"
    }
    
    Response:
    {
        "success": true,
        "message": "사용 가능한 이메일입니다.",
        "data": {
            "available": true
        }
    }
    """
    try:
        if not request.is_json:
            return jsonify(create_response(
                success=False,
                message="Content-Type은 application/json이어야 합니다.",
                error_code="INVALID_CONTENT_TYPE"
            )), 400
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify(create_response(
                success=False,
                message="이메일을 입력해주세요.",
                error_code="MISSING_EMAIL"
            )), 400
        
        # 이메일 형식 검증
        from utils.validation_utils import ValidationUtils
        if not ValidationUtils.validate_email(email):
            return jsonify(create_response(
                success=False,
                message="올바른 이메일 형식을 입력해주세요.",
                error_code="INVALID_EMAIL_FORMAT"
            )), 400
        
        # 중복 확인
        from models.user import User
        existing_user = User.get_by_email(email)
        available = existing_user is None
        
        return jsonify(create_response(
            success=True,
            message="사용 가능한 이메일입니다." if available else "이미 사용 중인 이메일입니다.",
            data={
                'available': available,
                'email': email
            }
        )), 200
        
    except Exception as e:
        logger.error(f"이메일 중복 확인 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500