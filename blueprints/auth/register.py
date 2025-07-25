# blueprints/auth/register.py
# 회원가입 API 엔드포인트

from flask import request, jsonify
from . import auth_bp
from models.user import User
from utils.password_utils import validate_password
from utils.validation_utils import validate_email, validate_username
from utils.response_utils import success_response, error_response
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
        "user_type": "beginner|business",
        "user_level": "low|medium|high" (선택사항, 기본값: low)
    }
    
    Response:
    {
        "success": true,
        "message": "회원가입이 완료되었습니다.",
        "data": {
            "user_id": 1,
            "username": "사용자명",
            "email": "이메일",
            "user_type": "beginner",
            "user_level": "low"
        }
    }
    """
    try:
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        # 필수 필드 확인
        required_fields = ['username', 'email', 'password', 'user_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}", 
                400
            )
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        user_type = data['user_type']
        user_level = data.get('user_level', 'low')
        
        # 입력값 검증
        # 사용자명 검증
        is_valid_username, username_error = validate_username(username)
        if not is_valid_username:
            return error_response(username_error, 400)
        
        # 이메일 검증
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            return error_response(email_error, 400)
        
        # 비밀번호 강도 검증
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return error_response(password_error, 400)
        
        # 사용자 유형 검증
        if user_type not in ['beginner', 'business']:
            return error_response("사용자 유형은 'beginner' 또는 'business'여야 합니다.", 400)
        
        # 사용자 레벨 검증
        if user_level not in ['low', 'medium', 'high']:
            return error_response("사용자 레벨은 'low', 'medium', 'high' 중 하나여야 합니다.", 400)
        
        # 중복 확인
        existing_user = User.get_by_username(username)
        if existing_user:
            return error_response("이미 사용 중인 사용자명입니다.", 409)
        
        existing_email = User.get_by_email(email)
        if existing_email:
            return error_response("이미 사용 중인 이메일입니다.", 409)
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            user_level=user_level
        )
        
        # 데이터베이스에 저장
        new_user.save()
        
        logger.info(f"새 사용자 회원가입 완료 - ID: {new_user.user_id}, 사용자명: {username}")
        
        # 응답 데이터 구성
        user_data = {
            'user_id': new_user.user_id,
            'username': new_user.username,
            'email': new_user.email,
            'user_type': new_user.user_type,
            'user_level': new_user.user_level,
            'created_at': new_user.created_at.isoformat()
        }
        
        return success_response(
            "회원가입이 완료되었습니다.",
            user_data,
            201
        )
        
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류 발생: {str(e)}")
        return error_response("회원가입 처리 중 오류가 발생했습니다.", 500)


@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    """
    사용자명 중복 확인 API
    
    Request Body:
    {
        "username": "확인할사용자명"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "available": true,
            "message": "사용 가능한 사용자명입니다."
        }
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('username'):
            return error_response("사용자명을 입력해주세요.", 400)
        
        username = data['username'].strip()
        
        # 사용자명 형식 검증
        is_valid, error_message = validate_username(username)
        if not is_valid:
            return success_response("사용자명 확인 완료", {
                'available': False,
                'message': error_message
            })
        
        # 중복 확인
        existing_user = User.get_by_username(username)
        if existing_user:
            return success_response("사용자명 확인 완료", {
                'available': False,
                'message': '이미 사용 중인 사용자명입니다.'
            })
        
        return success_response("사용자명 확인 완료", {
            'available': True,
            'message': '사용 가능한 사용자명입니다.'
        })
        
    except Exception as e:
        logger.error(f"사용자명 중복 확인 중 오류 발생: {str(e)}")
        return error_response("사용자명 확인 중 오류가 발생했습니다.", 500)


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    이메일 중복 확인 API
    
    Request Body:
    {
        "email": "확인할@이메일.com"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "available": true,
            "message": "사용 가능한 이메일입니다."
        }
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return error_response("이메일을 입력해주세요.", 400)
        
        email = data['email'].strip().lower()
        
        # 이메일 형식 검증
        is_valid, error_message = validate_email(email)
        if not is_valid:
            return success_response("이메일 확인 완료", {
                'available': False,
                'message': error_message
            })
        
        # 중복 확인
        existing_user = User.get_by_email(email)
        if existing_user:
            return success_response("이메일 확인 완료", {
                'available': False,
                'message': '이미 사용 중인 이메일입니다.'
            })
        
        return success_response("이메일 확인 완료", {
            'available': True,
            'message': '사용 가능한 이메일입니다.'
        })
        
    except Exception as e:
        logger.error(f"이메일 중복 확인 중 오류 발생: {str(e)}")
        return error_response("이메일 확인 중 오류가 발생했습니다.", 500)