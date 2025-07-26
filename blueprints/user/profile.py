# blueprints/user/profile.py
# 사용자 프로필 관리 API 엔드포인트

from flask import request, jsonify, g, Blueprint
from services.auth_service import AuthService
from utils.response_utils import create_response
from utils.jwt_utils import token_required
from utils.validation_utils import ValidationUtils
from utils.password_utils import validate_password
import logging

logger = logging.getLogger(__name__)

# 프로필 관련 블루프린트 생성
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@token_required
def get_profile():
    """
    사용자 프로필 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "사용자 프로필을 조회했습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "user_type": "business",
                "user_level": "high",
                "created_at": "2024-01-01T00:00:00",
                "is_active": true
            },
            "progress_summary": {
                "total_chapters": 5,
                "completed_chapters": 3,
                "in_progress_chapters": 1,
                "average_understanding": 85.5,
                "total_study_time": 180
            },
            "recent_activity": [...]
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
        logger.error(f"프로필 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@profile_bp.route('/', methods=['PUT'])
@token_required
def update_profile():
    """
    사용자 프로필 수정 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "username": "new_username",
        "email": "new_email@example.com",
        "user_type": "business"
    }
    
    Response:
    {
        "success": true,
        "message": "프로필이 수정되었습니다.",
        "data": {
            "user": {
                "user_id": 1,
                "username": "new_username",
                "email": "new_email@example.com",
                "user_type": "business",
                "user_level": "high",
                "updated_at": "2024-01-01T01:00:00"
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
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
        
        from models.user import User
        
        # 사용자 조회
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 수정 가능한 필드들
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        user_type = data.get('user_type', '').strip()
        
        # 변경사항 확인 및 검증
        changes_made = False
        
        # 사용자명 변경
        if username and username != user.username:
            if not ValidationUtils.validate_username(username):
                return jsonify(create_response(
                    success=False,
                    message="사용자명은 3-50자의 영문, 숫자, 언더스코어만 사용 가능합니다.",
                    error_code="INVALID_USERNAME"
                )), 400
            
            # 중복 확인
            existing_user = User.get_by_username(username)
            if existing_user and existing_user.user_id != user_id:
                return jsonify(create_response(
                    success=False,
                    message="이미 사용 중인 사용자명입니다.",
                    error_code="USERNAME_EXISTS"
                )), 409
            
            user.username = username
            changes_made = True
        
        # 이메일 변경
        if email and email != user.email:
            if not ValidationUtils.validate_email(email):
                return jsonify(create_response(
                    success=False,
                    message="올바른 이메일 형식을 입력해주세요.",
                    error_code="INVALID_EMAIL"
                )), 400
            
            # 중복 확인
            existing_user = User.get_by_email(email)
            if existing_user and existing_user.user_id != user_id:
                return jsonify(create_response(
                    success=False,
                    message="이미 사용 중인 이메일입니다.",
                    error_code="EMAIL_EXISTS"
                )), 409
            
            user.email = email
            changes_made = True
        
        # 사용자 타입 변경
        if user_type and user_type != user.user_type:
            if user_type not in ['beginner', 'business']:
                return jsonify(create_response(
                    success=False,
                    message="올바른 사용자 유형을 선택해주세요.",
                    error_code="INVALID_USER_TYPE"
                )), 400
            
            user.user_type = user_type
            changes_made = True
        
        # 변경사항이 없는 경우
        if not changes_made:
            return jsonify(create_response(
                success=True,
                message="변경할 내용이 없습니다.",
                data={
                    'user': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type,
                        'user_level': user.user_level,
                        'updated_at': user.updated_at.isoformat()
                    }
                }
            )), 200
        
        # 변경사항 저장
        if not user.save():
            return jsonify(create_response(
                success=False,
                message="프로필 수정 중 오류가 발생했습니다.",
                error_code="UPDATE_FAILED"
            )), 500
        
        logger.info(f"프로필 수정 완료 - user_id: {user_id}")
        
        return jsonify(create_response(
            success=True,
            message="프로필이 수정되었습니다.",
            data={
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                    'user_level': user.user_level,
                    'updated_at': user.updated_at.isoformat()
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"프로필 수정 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@profile_bp.route('/password', methods=['PUT'])
@token_required
def change_password():
    """
    비밀번호 변경 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "current_password": "현재_비밀번호",
        "new_password": "새_비밀번호",
        "confirm_password": "새_비밀번호_확인"
    }
    
    Response:
    {
        "success": true,
        "message": "비밀번호가 변경되었습니다.",
        "data": {
            "changed_at": "2024-01-01T01:00:00"
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
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
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify(create_response(
                success=False,
                message="현재 비밀번호, 새 비밀번호, 비밀번호 확인을 모두 입력해주세요.",
                error_code="MISSING_FIELDS"
            )), 400
        
        # 새 비밀번호 확인
        if new_password != confirm_password:
            return jsonify(create_response(
                success=False,
                message="새 비밀번호와 비밀번호 확인이 일치하지 않습니다.",
                error_code="PASSWORD_MISMATCH"
            )), 400
        
        from models.user import User
        
        # 사용자 조회
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            return jsonify(create_response(
                success=False,
                message="현재 비밀번호가 올바르지 않습니다.",
                error_code="INVALID_CURRENT_PASSWORD"
            )), 400
        
        # 새 비밀번호 강도 검증
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify(create_response(
                success=False,
                message=message,
                error_code="WEAK_PASSWORD"
            )), 400
        
        # 현재 비밀번호와 동일한지 확인
        if user.check_password(new_password):
            return jsonify(create_response(
                success=False,
                message="새 비밀번호는 현재 비밀번호와 달라야 합니다.",
                error_code="SAME_PASSWORD"
            )), 400
        
        # 비밀번호 변경
        user.set_password(new_password)
        
        if not user.save():
            return jsonify(create_response(
                success=False,
                message="비밀번호 변경 중 오류가 발생했습니다.",
                error_code="PASSWORD_CHANGE_FAILED"
            )), 500
        
        logger.info(f"비밀번호 변경 완료 - user_id: {user_id}")
        
        return jsonify(create_response(
            success=True,
            message="비밀번호가 변경되었습니다.",
            data={
                'changed_at': user.updated_at.isoformat()
            }
        )), 200
        
    except Exception as e:
        logger.error(f"비밀번호 변경 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@profile_bp.route('/deactivate', methods=['POST'])
@token_required
def deactivate_account():
    """
    계정 비활성화 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "password": "비밀번호_확인",
        "reason": "비활성화_사유"
    }
    
    Response:
    {
        "success": true,
        "message": "계정이 비활성화되었습니다.",
        "data": {
            "deactivated_at": "2024-01-01T01:00:00"
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
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
        password = data.get('password', '')
        reason = data.get('reason', '').strip()
        
        if not password:
            return jsonify(create_response(
                success=False,
                message="비밀번호 확인이 필요합니다.",
                error_code="MISSING_PASSWORD"
            )), 400
        
        from models.user import User
        
        # 사용자 조회
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 비밀번호 확인
        if not user.check_password(password):
            return jsonify(create_response(
                success=False,
                message="비밀번호가 올바르지 않습니다.",
                error_code="INVALID_PASSWORD"
            )), 400
        
        # 이미 비활성화된 계정인지 확인
        if not user.is_active:
            return jsonify(create_response(
                success=False,
                message="이미 비활성화된 계정입니다.",
                error_code="ALREADY_DEACTIVATED"
            )), 400
        
        # 계정 비활성화
        user.is_active = False
        
        if not user.save():
            return jsonify(create_response(
                success=False,
                message="계정 비활성화 중 오류가 발생했습니다.",
                error_code="DEACTIVATION_FAILED"
            )), 500
        
        logger.info(f"계정 비활성화 완료 - user_id: {user_id}, reason: {reason}")
        
        return jsonify(create_response(
            success=True,
            message="계정이 비활성화되었습니다.",
            data={
                'deactivated_at': user.updated_at.isoformat(),
                'reason': reason
            }
        )), 200
        
    except Exception as e:
        logger.error(f"계정 비활성화 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@profile_bp.route('/preferences', methods=['GET'])
@token_required
def get_preferences():
    """
    사용자 학습 선호도 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "학습 선호도를 조회했습니다.",
        "data": {
            "user_type": "business",
            "user_level": "high",
            "preferred_difficulty": "medium",
            "learning_goals": ["업무 자동화", "창작 활동"],
            "notification_settings": {
                "email_notifications": true,
                "study_reminders": false
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.user import User
        
        # 사용자 조회
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 기본 선호도 정보 (향후 확장 가능)
        preferences = {
            'user_type': user.user_type,
            'user_level': user.user_level,
            'preferred_difficulty': user.user_level,  # 기본값으로 사용자 레벨 사용
            'learning_goals': [],  # 향후 별도 테이블로 관리 가능
            'notification_settings': {
                'email_notifications': True,
                'study_reminders': False
            }
        }
        
        return jsonify(create_response(
            success=True,
            message="학습 선호도를 조회했습니다.",
            data=preferences
        )), 200
        
    except Exception as e:
        logger.error(f"학습 선호도 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500