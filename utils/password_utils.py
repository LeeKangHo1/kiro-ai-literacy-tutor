# utils/password_utils.py
# 비밀번호 암호화 유틸리티

import bcrypt
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class PasswordManager:
    """비밀번호 관리 클래스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 bcrypt로 해시화
        
        Args:
            password: 평문 비밀번호
            
        Returns:
            해시화된 비밀번호 문자열
        """
        try:
            # 비밀번호를 바이트로 인코딩
            password_bytes = password.encode('utf-8')
            
            # bcrypt로 해시 생성 (salt 자동 생성)
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            
            # 문자열로 디코딩하여 반환
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"비밀번호 해시화 실패: {str(e)}")
            raise Exception("비밀번호 암호화에 실패했습니다.")
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            password: 평문 비밀번호
            hashed_password: 해시화된 비밀번호
            
        Returns:
            비밀번호 일치 여부 (bool)
        """
        try:
            # 문자열을 바이트로 인코딩
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # bcrypt로 비밀번호 검증
            return bcrypt.checkpw(password_bytes, hashed_bytes)
            
        except Exception as e:
            logger.error(f"비밀번호 검증 실패: {str(e)}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        비밀번호 강도 검증
        
        Args:
            password: 검증할 비밀번호
            
        Returns:
            (유효성 여부, 오류 메시지)
        """
        try:
            # 최소 길이 확인
            if len(password) < 8:
                return False, "비밀번호는 최소 8자 이상이어야 합니다."
            
            # 최대 길이 확인
            if len(password) > 128:
                return False, "비밀번호는 최대 128자까지 가능합니다."
            
            # 영문자 포함 확인
            if not re.search(r'[a-zA-Z]', password):
                return False, "비밀번호에는 영문자가 포함되어야 합니다."
            
            # 숫자 포함 확인
            if not re.search(r'\d', password):
                return False, "비밀번호에는 숫자가 포함되어야 합니다."
            
            # 특수문자 포함 확인 (선택사항이지만 권장)
            special_chars = r'[!@#$%^&*(),.?":{}|<>]'
            has_special = re.search(special_chars, password)
            
            # 연속된 문자 확인
            if re.search(r'(.)\1{2,}', password):
                return False, "동일한 문자가 3번 이상 연속될 수 없습니다."
            
            # 일반적인 패턴 확인
            common_patterns = [
                r'123456',
                r'password',
                r'qwerty',
                r'abc123'
            ]
            
            for pattern in common_patterns:
                if re.search(pattern, password.lower()):
                    return False, "일반적인 패턴의 비밀번호는 사용할 수 없습니다."
            
            # 모든 검증 통과
            if has_special:
                return True, "강력한 비밀번호입니다."
            else:
                return True, "보통 강도의 비밀번호입니다. 특수문자를 포함하면 더 안전합니다."
            
        except Exception as e:
            logger.error(f"비밀번호 강도 검증 오류: {str(e)}")
            return False, "비밀번호 검증 중 오류가 발생했습니다."
    
    @staticmethod
    def generate_temporary_password(length: int = 12) -> str:
        """
        임시 비밀번호 생성 (비밀번호 재설정 등에 사용)
        
        Args:
            length: 생성할 비밀번호 길이
            
        Returns:
            임시 비밀번호 문자열
        """
        import secrets
        import string
        
        try:
            # 사용할 문자 집합
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            
            # 각 문자 유형에서 최소 1개씩 선택
            password = [
                secrets.choice(string.ascii_lowercase),
                secrets.choice(string.ascii_uppercase),
                secrets.choice(string.digits),
                secrets.choice("!@#$%^&*")
            ]
            
            # 나머지 길이만큼 랜덤 문자 추가
            for _ in range(length - 4):
                password.append(secrets.choice(alphabet))
            
            # 리스트를 섞어서 문자열로 변환
            secrets.SystemRandom().shuffle(password)
            return ''.join(password)
            
        except Exception as e:
            logger.error(f"임시 비밀번호 생성 실패: {str(e)}")
            raise Exception("임시 비밀번호 생성에 실패했습니다.")


def hash_password(password: str) -> str:
    """비밀번호 해시화 (편의 함수)"""
    return PasswordManager.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호 검증 (편의 함수)"""
    return PasswordManager.verify_password(password, hashed_password)


def validate_password(password: str) -> Tuple[bool, str]:
    """비밀번호 강도 검증 (편의 함수)"""
    return PasswordManager.validate_password_strength(password)