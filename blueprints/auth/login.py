# blueprints/auth/login.py
# 로그인 API 엔드포인트

from flask import request, jsonify, g
from . import auth_bp
from models.user import User
from utils.jwt_utils import JWTManager, token_required
from utils.response_utils import success_response, error_response
from datetime import datetime, timedelta
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
            "access_token": "JWT토큰",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "user_id": 1,
                "username": "사용자명",
                "email": "이메일",
                "user_type": "beginner",
                "user_level": "low"
            }
        }
    }
    """
    try:
        # 요청 데이터 검증
        data = request.get_json()
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return error_response("사용자명(또는 이메일)과 비밀번호를 입력해주세요.", 400)
        
        # 사용자 인증
        user = User.authenticate(username_or_email, password)
        if not user:
            logger.warning(f"로그인 실패 - 사용자명/이메일: {username_or_email}")
            return error_response("사용자명(또는 이메일) 또는 비밀번호가 올바르지 않습니다.", 401)
        
        # 계정 활성화 상태 확인
        if not user.is_active:
            logger.warning(f"비활성화된 계정 로그인 시도 - 사용자 ID: {user.user_id}")
            return error_response("비활성화된 계정입니다. 관리자에게 문의하세요.", 403)
        
        # JWT 토큰 생성
        try:
            access_token = JWTManager.generate_token(
                user.user_id,
                user.user_type,
                user.user_level
            )
        except Exception as e:
            logger.error(f"JWT 토큰 생성 실패 - 사용자 ID: {user.user_id}, 오류: {str(e)}")
            return error_response("로그인 처리 중 오류가 발생했습니다.", 500)
        
        # 마지막 로그인 시간 업데이트 (필요시)
        user.updated_at = datetime.utcnow()
        user.save()
        
        logger.info(f"로그인 성공 - 사용자 ID: {user.user_id}, 사용자명: {user.username}")
        
        # 응답 데이터 구성
        response_data = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # 1시간 (초 단위)
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'user_level': user.user_level,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }
        
        return success_response("로그인이 완료되었습니다.", response_data)
        
    except Exception as e:
        logger.error(f"로그인 처리 중 오류 발생: {str(e)}")
        return error_response("로그인 처리 중 오류가 발생했습니다.", 500)


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    사용자 로그아웃 API
    
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Response:
    {
        "success": true,
        "message": "로그아웃이 완료되었습니다."
    }
    """
    try:
        # 현재 사용자 정보 가져오기
        current_user = g.current_user
        
        logger.info(f"로그아웃 - 사용자 ID: {current_user['user_id']}")
        
        # JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없음
        # 클라이언트에서 토큰을 삭제하도록 안내
        # 향후 토큰 블랙리스트 기능을 구현할 수 있음
        
        return success_response("로그아웃이 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"로그아웃 처리 중 오류 발생: {str(e)}")
        return error_response("로그아웃 처리 중 오류가 발생했습니다.", 500)


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    현재 로그인한 사용자 정보 조회 API
    
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Response:
    {
        "success": true,
        "data": {
            "user_id": 1,
            "username": "사용자명",
            "email": "이메일",
            "user_type": "beginner",
            "user_level": "low",
            "learning_progress": {
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
        # 현재 사용자 정보 가져오기
        current_user_info = g.current_user
        user_id = current_user_info['user_id']
        
        # 데이터베이스에서 사용자 상세 정보 조회
        user = User.query.get(user_id)
        if not user:
            return error_response("사용자를 찾을 수 없습니다.", 404)
        
        # 학습 진도 정보 가져오기
        learning_progress = user.get_overall_progress()
        
        # 응답 데이터 구성
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'user_level': user.user_level,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'learning_progress': learning_progress
        }
        
        return success_response("사용자 정보 조회 완료", user_data)
        
    except Exception as e:
        logger.error(f"사용자 정보 조회 중 오류 발생: {str(e)}")
        return error_response("사용자 정보 조회 중 오류가 발생했습니다.", 500)


@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    """
    사용자 프로필 수정 API
    
    Headers:
        Authorization: Bearer <JWT토큰>
    
    Request Body:
    {
        "email": "새이메일@example.com",
        "user_level": "medium"
    }
    
    Response:
    {
        "success": true,
        "message": "프로필이 업데이트되었습니다.",
        "data": {
            "user_id": 1,
            "username": "사용자명",
            "email": "새이메일@example.com",
            "user_type": "beginner",
            "user_level": "medium"
        }
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
            return error_response("수정할 데이터가 없습니다.", 400)
        
        updated_fields = []
        
        # 이메일 수정
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                # 이메일 형식 검증
                from utils.validation_utils import validate_email
                is_valid, error_message = validate_email(new_email)
                if not is_valid:
                    return error_response(error_message, 400)
                
                # 중복 확인
                existing_user = User.get_by_email(new_email)
                if existing_user and existing_user.user_id != user.user_id:
                    return error_response("이미 사용 중인 이메일입니다.", 409)
                
                user.email = new_email
                updated_fields.append('이메일')
        
        # 사용자 레벨 수정
        if 'user_level' in data:
            new_level = data['user_level']
            if new_level not in ['low', 'medium', 'high']:
                return error_response("사용자 레벨은 'low', 'medium', 'high' 중 하나여야 합니다.", 400)
            
            if new_level != user.user_level:
                user.user_level = new_level
                updated_fields.append('사용자 레벨')
        
        # 변경사항이 없는 경우
        if not updated_fields:
            return success_response("변경사항이 없습니다.", {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'user_level': user.user_level
            })
        
        # 변경사항 저장
        user.updated_at = datetime.utcnow()
        user.save()
        
        logger.info(f"프로필 업데이트 - 사용자 ID: {user.user_id}, 수정 필드: {', '.join(updated_fields)}")
        
        # 응답 데이터 구성
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'user_level': user.user_level,
            'updated_at': user.updated_at.isoformat()
        }
        
        return success_response(
            f"프로필이 업데이트되었습니다. (수정된 항목: {', '.join(updated_fields)})",
            user_data
        )
        
    except Exception as e:
        logger.error(f"프로필 업데이트 중 오류 발생: {str(e)}")
        return error_response("프로필 업데이트 중 오류가 발생했습니다.", 500)