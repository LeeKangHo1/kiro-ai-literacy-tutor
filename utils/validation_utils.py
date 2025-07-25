# utils/validation_utils.py
# 검증 유틸리티

import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def validate_email(email: str) -> Tuple[bool, str]:
    """
    이메일 주소 유효성 검증
    
    Args:
        email: 검증할 이메일 주소
        
    Returns:
        (유효성 여부, 오류 메시지)
    """
    try:
        if not email:
            return False, "이메일을 입력해주세요."
        
        # 기본 길이 확인
        if len(email) > 254:
            return False, "이메일 주소가 너무 깁니다."
        
        # 이메일 정규식 패턴
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "올바른 이메일 형식이 아닙니다."
        
        # @ 기호 개수 확인
        if email.count('@') != 1:
            return False, "올바른 이메일 형식이 아닙니다."
        
        # 로컬 부분과 도메인 부분 분리
        local_part, domain_part = email.split('@')
        
        # 로컬 부분 검증
        if len(local_part) == 0 or len(local_part) > 64:
            return False, "이메일의 사용자명 부분이 올바르지 않습니다."
        
        # 도메인 부분 검증
        if len(domain_part) == 0 or len(domain_part) > 253:
            return False, "이메일의 도메인 부분이 올바르지 않습니다."
        
        # 연속된 점 확인
        if '..' in email:
            return False, "이메일에 연속된 점이 포함될 수 없습니다."
        
        # 시작과 끝에 점 확인
        if local_part.startswith('.') or local_part.endswith('.'):
            return False, "이메일의 사용자명 부분은 점으로 시작하거나 끝날 수 없습니다."
        
        return True, "유효한 이메일 주소입니다."
        
    except Exception as e:
        logger.error(f"이메일 검증 중 오류 발생: {str(e)}")
        return False, "이메일 검증 중 오류가 발생했습니다."


def validate_username(username: str) -> Tuple[bool, str]:
    """
    사용자명 유효성 검증
    
    Args:
        username: 검증할 사용자명
        
    Returns:
        (유효성 여부, 오류 메시지)
    """
    try:
        if not username:
            return False, "사용자명을 입력해주세요."
        
        # 길이 확인
        if len(username) < 3:
            return False, "사용자명은 최소 3자 이상이어야 합니다."
        
        if len(username) > 50:
            return False, "사용자명은 최대 50자까지 가능합니다."
        
        # 허용되는 문자 확인 (영문자, 숫자, 언더스코어, 하이픈)
        username_pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(username_pattern, username):
            return False, "사용자명은 영문자, 숫자, 언더스코어(_), 하이픈(-)만 사용할 수 있습니다."
        
        # 시작과 끝 문자 확인 (영문자 또는 숫자로 시작/끝)
        if not (username[0].isalnum() and username[-1].isalnum()):
            return False, "사용자명은 영문자 또는 숫자로 시작하고 끝나야 합니다."
        
        # 연속된 특수문자 확인
        if re.search(r'[_-]{2,}', username):
            return False, "언더스코어나 하이픈이 연속으로 2개 이상 올 수 없습니다."
        
        # 예약어 확인
        reserved_words = [
            'admin', 'administrator', 'root', 'system', 'user', 'guest',
            'api', 'www', 'mail', 'email', 'support', 'help', 'info',
            'test', 'demo', 'sample', 'null', 'undefined', 'anonymous'
        ]
        
        if username.lower() in reserved_words:
            return False, "사용할 수 없는 사용자명입니다."
        
        return True, "유효한 사용자명입니다."
        
    except Exception as e:
        logger.error(f"사용자명 검증 중 오류 발생: {str(e)}")
        return False, "사용자명 검증 중 오류가 발생했습니다."


def validate_user_type(user_type: str) -> Tuple[bool, str]:
    """
    사용자 유형 유효성 검증
    
    Args:
        user_type: 검증할 사용자 유형
        
    Returns:
        (유효성 여부, 오류 메시지)
    """
    try:
        if not user_type:
            return False, "사용자 유형을 선택해주세요."
        
        valid_types = ['beginner', 'business']
        if user_type not in valid_types:
            return False, f"사용자 유형은 {', '.join(valid_types)} 중 하나여야 합니다."
        
        return True, "유효한 사용자 유형입니다."
        
    except Exception as e:
        logger.error(f"사용자 유형 검증 중 오류 발생: {str(e)}")
        return False, "사용자 유형 검증 중 오류가 발생했습니다."


def validate_user_level(user_level: str) -> Tuple[bool, str]:
    """
    사용자 레벨 유효성 검증
    
    Args:
        user_level: 검증할 사용자 레벨
        
    Returns:
        (유효성 여부, 오류 메시지)
    """
    try:
        if not user_level:
            return False, "사용자 레벨을 선택해주세요."
        
        valid_levels = ['low', 'medium', 'high']
        if user_level not in valid_levels:
            return False, f"사용자 레벨은 {', '.join(valid_levels)} 중 하나여야 합니다."
        
        return True, "유효한 사용자 레벨입니다."
        
    except Exception as e:
        logger.error(f"사용자 레벨 검증 중 오류 발생: {str(e)}")
        return False, "사용자 레벨 검증 중 오류가 발생했습니다."


def validate_request_data(data: dict, required_fields: list) -> Tuple[bool, str]:
    """
    요청 데이터의 필수 필드 검증
    
    Args:
        data: 검증할 데이터 딕셔너리
        required_fields: 필수 필드 리스트
        
    Returns:
        (유효성 여부, 오류 메시지)
    """
    try:
        if not data:
            return False, "요청 데이터가 없습니다."
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            return False, f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
        
        if empty_fields:
            return False, f"다음 필드는 비어있을 수 없습니다: {', '.join(empty_fields)}"
        
        return True, "유효한 요청 데이터입니다."
        
    except Exception as e:
        logger.error(f"요청 데이터 검증 중 오류 발생: {str(e)}")
        return False, "요청 데이터 검증 중 오류가 발생했습니다."


def sanitize_input(input_string: str, max_length: int = None) -> str:
    """
    입력 문자열 정제
    
    Args:
        input_string: 정제할 문자열
        max_length: 최대 길이 (선택사항)
        
    Returns:
        정제된 문자열
    """
    try:
        if not input_string:
            return ""
        
        # 앞뒤 공백 제거
        sanitized = input_string.strip()
        
        # HTML 태그 제거 (기본적인 XSS 방지)
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # 특수 문자 이스케이프 (SQL 인젝션 기본 방지)
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # 최대 길이 제한
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
        
    except Exception as e:
        logger.error(f"입력 정제 중 오류 발생: {str(e)}")
        return ""


def validate_pagination_params(page: str, per_page: str, max_per_page: int = 100) -> Tuple[bool, str, int, int]:
    """
    페이지네이션 파라미터 검증
    
    Args:
        page: 페이지 번호 (문자열)
        per_page: 페이지당 항목 수 (문자열)
        max_per_page: 최대 페이지당 항목 수
        
    Returns:
        (유효성 여부, 오류 메시지, 페이지 번호, 페이지당 항목 수)
    """
    try:
        # 기본값 설정
        page_num = 1
        per_page_num = 20
        
        # 페이지 번호 검증
        if page:
            try:
                page_num = int(page)
                if page_num < 1:
                    return False, "페이지 번호는 1 이상이어야 합니다.", 0, 0
            except ValueError:
                return False, "페이지 번호는 숫자여야 합니다.", 0, 0
        
        # 페이지당 항목 수 검증
        if per_page:
            try:
                per_page_num = int(per_page)
                if per_page_num < 1:
                    return False, "페이지당 항목 수는 1 이상이어야 합니다.", 0, 0
                if per_page_num > max_per_page:
                    return False, f"페이지당 항목 수는 최대 {max_per_page}개까지 가능합니다.", 0, 0
            except ValueError:
                return False, "페이지당 항목 수는 숫자여야 합니다.", 0, 0
        
        return True, "유효한 페이지네이션 파라미터입니다.", page_num, per_page_num
        
    except Exception as e:
        logger.error(f"페이지네이션 파라미터 검증 중 오류 발생: {str(e)}")
        return False, "페이지네이션 파라미터 검증 중 오류가 발생했습니다.", 0, 0