# services/auth_service.py
# 인증 서비스

from models.user import User
from utils.jwt_utils import JWTManager
from utils.password_utils import PasswordManager, validate_password
from utils.validation_utils import ValidationUtils
from utils.response_utils import create_response
from services.database_service import DatabaseService
from utils.error_handler import (
    AuthenticationError, ValidationError, DatabaseError, 
    handle_errors, ErrorCategory, ErrorSeverity
)
from utils.logging_config import LoggingConfig
import logging
from typing import Dict, Any, Optional, Tuple

logger = LoggingConfig.get_contextual_logger('auth_service')

class AuthService:
    """인증 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    @staticmethod
    @handle_errors(ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM)
    def register_user(username: str, email: str, password: str, user_type: str) -> Dict[str, Any]:
        """
        사용자 회원가입
        
        Args:
            username: 사용자명
            email: 이메일
            password: 비밀번호
            user_type: 사용자 유형 (beginner, business)
            
        Returns:
            회원가입 결과 딕셔너리
        """
        try:
            # 입력 데이터 검증
            validation_result = AuthService._validate_registration_data(
                username, email, password, user_type
            )
            if not validation_result['success']:
                raise ValidationError(
                    validation_result['message'],
                    details={'error_code': validation_result.get('error_code')}
                )
            
            # 중복 사용자 확인
            duplicate_check = AuthService._check_duplicate_user(username, email)
            if not duplicate_check['success']:
                raise ValidationError(
                    duplicate_check['message'],
                    details={'error_code': duplicate_check.get('error_code')}
                )
            
            # 사용자 생성
            user = User(
                username=username,
                email=email,
                password=password,  # User 모델에서 자동으로 해시화
                user_type=user_type,
                user_level='low'  # 기본값
            )
            
            # 데이터베이스에 저장
            if not user.save():
                logger.error(f"사용자 저장 실패 - username: {username}")
                raise DatabaseError(
                    "회원가입 처리 중 데이터베이스 오류가 발생했습니다.",
                    severity=ErrorSeverity.HIGH,
                    details={'username': username}
                )
            
            # JWT 토큰 생성
            token = JWTManager.generate_token(
                user.user_id,
                user.user_type,
                user.user_level
            )
            
            logger.info(f"사용자 회원가입 완료 - ID: {user.user_id}, username: {username}")
            
            return create_response(
                success=True,
                message="회원가입이 완료되었습니다.",
                data={
                    'user': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type,
                        'user_level': user.user_level,
                        'created_at': user.created_at.isoformat()
                    },
                    'token': token
                }
            )
            
        except Exception as e:
            logger.error(f"회원가입 처리 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="회원가입 처리 중 오류가 발생했습니다.",
                error_code="REGISTRATION_ERROR"
            )
    
    @staticmethod
    def login_user(username_or_email: str, password: str) -> Dict[str, Any]:
        """
        사용자 로그인
        
        Args:
            username_or_email: 사용자명 또는 이메일
            password: 비밀번호
            
        Returns:
            로그인 결과 딕셔너리
        """
        try:
            # 입력 데이터 검증
            if not username_or_email or not password:
                return create_response(
                    success=False,
                    message="사용자명/이메일과 비밀번호를 입력해주세요.",
                    error_code="MISSING_CREDENTIALS"
                )
            
            # 사용자 인증
            user = User.authenticate(username_or_email, password)
            if not user:
                logger.warning(f"로그인 실패 - username_or_email: {username_or_email}")
                return create_response(
                    success=False,
                    message="사용자명/이메일 또는 비밀번호가 올바르지 않습니다.",
                    error_code="INVALID_CREDENTIALS"
                )
            
            # 계정 활성화 상태 확인
            if not user.is_active:
                logger.warning(f"비활성화된 계정 로그인 시도 - user_id: {user.user_id}")
                return create_response(
                    success=False,
                    message="비활성화된 계정입니다. 관리자에게 문의하세요.",
                    error_code="ACCOUNT_DISABLED"
                )
            
            # JWT 토큰 생성
            token = JWTManager.generate_token(
                user.user_id,
                user.user_type,
                user.user_level
            )
            
            logger.info(f"사용자 로그인 성공 - user_id: {user.user_id}")
            
            return create_response(
                success=True,
                message="로그인이 완료되었습니다.",
                data={
                    'user': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type,
                        'user_level': user.user_level,
                        'last_login': user.updated_at.isoformat()
                    },
                    'token': token
                }
            )
            
        except Exception as e:
            logger.error(f"로그인 처리 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="로그인 처리 중 오류가 발생했습니다.",
                error_code="LOGIN_ERROR"
            )
    
    @staticmethod
    def refresh_token(current_token: str) -> Dict[str, Any]:
        """
        JWT 토큰 갱신
        
        Args:
            current_token: 현재 JWT 토큰
            
        Returns:
            토큰 갱신 결과 딕셔너리
        """
        try:
            # 토큰 검증 및 갱신
            new_token = JWTManager.refresh_token(current_token)
            if not new_token:
                return create_response(
                    success=False,
                    message="토큰 갱신에 실패했습니다. 다시 로그인해주세요.",
                    error_code="TOKEN_REFRESH_FAILED"
                )
            
            # 토큰에서 사용자 정보 추출
            payload = JWTManager.verify_token(new_token)
            if not payload:
                return create_response(
                    success=False,
                    message="갱신된 토큰이 유효하지 않습니다.",
                    error_code="INVALID_REFRESHED_TOKEN"
                )
            
            logger.info(f"토큰 갱신 완료 - user_id: {payload['user_id']}")
            
            return create_response(
                success=True,
                message="토큰이 갱신되었습니다.",
                data={
                    'token': new_token,
                    'user_id': payload['user_id'],
                    'expires_at': payload['exp']
                }
            )
            
        except Exception as e:
            logger.error(f"토큰 갱신 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="토큰 갱신 중 오류가 발생했습니다.",
                error_code="TOKEN_REFRESH_ERROR"
            )
    
    @staticmethod
    def get_user_profile(user_id: int) -> Dict[str, Any]:
        """
        사용자 프로필 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 프로필 정보
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            # 학습 진도 정보 포함
            progress_summary = user.get_overall_progress()
            recent_activity = user.get_recent_activity(limit=5)
            
            return create_response(
                success=True,
                message="사용자 프로필을 조회했습니다.",
                data={
                    'user': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'user_type': user.user_type,
                        'user_level': user.user_level,
                        'created_at': user.created_at.isoformat(),
                        'is_active': user.is_active
                    },
                    'progress_summary': progress_summary,
                    'recent_activity': [
                        {
                            'loop_id': loop.loop_id,
                            'chapter_id': loop.chapter_id,
                            'started_at': loop.started_at.isoformat(),
                            'status': loop.loop_status
                        } for loop in recent_activity
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"사용자 프로필 조회 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="사용자 프로필 조회 중 오류가 발생했습니다.",
                error_code="PROFILE_FETCH_ERROR"
            )
    
    @staticmethod
    def _validate_registration_data(username: str, email: str, password: str, user_type: str) -> Dict[str, Any]:
        """회원가입 데이터 검증"""
        # 사용자명 검증
        if not ValidationUtils.validate_username(username):
            return create_response(
                success=False,
                message="사용자명은 3-50자의 영문, 숫자, 언더스코어만 사용 가능합니다.",
                error_code="INVALID_USERNAME"
            )
        
        # 이메일 검증
        if not ValidationUtils.validate_email(email):
            return create_response(
                success=False,
                message="올바른 이메일 형식을 입력해주세요.",
                error_code="INVALID_EMAIL"
            )
        
        # 비밀번호 강도 검증
        is_valid, message = validate_password(password)
        if not is_valid:
            return create_response(
                success=False,
                message=message,
                error_code="WEAK_PASSWORD"
            )
        
        # 사용자 유형 검증
        if user_type not in ['beginner', 'business']:
            return create_response(
                success=False,
                message="올바른 사용자 유형을 선택해주세요.",
                error_code="INVALID_USER_TYPE"
            )
        
        return create_response(success=True, message="검증 완료")
    
    @staticmethod
    def _check_duplicate_user(username: str, email: str) -> Dict[str, Any]:
        """중복 사용자 확인"""
        # 사용자명 중복 확인
        if User.get_by_username(username):
            return create_response(
                success=False,
                message="이미 사용 중인 사용자명입니다.",
                error_code="USERNAME_EXISTS"
            )
        
        # 이메일 중복 확인
        if User.get_by_email(email):
            return create_response(
                success=False,
                message="이미 사용 중인 이메일입니다.",
                error_code="EMAIL_EXISTS"
            )
        
        return create_response(success=True, message="중복 확인 완료")