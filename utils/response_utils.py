# utils/response_utils.py
# 응답 처리 유틸리티

from flask import jsonify
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_response(success: bool, message: str, data: Any = None, error_code: str = None) -> Dict:
    """
    표준 응답 형식 생성
    
    Args:
        success: 성공 여부
        message: 응답 메시지
        data: 응답 데이터 (선택사항)
        error_code: 오류 코드 (선택사항)
        
    Returns:
        표준 응답 딕셔너리
    """
    try:
        response_data = {
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response_data['data'] = data
        
        if error_code:
            response_data['error_code'] = error_code
        
        return response_data
        
    except Exception as e:
        logger.error(f"응답 생성 중 오류 발생: {str(e)}")
        return {
            'success': False,
            'message': '응답 생성 중 오류가 발생했습니다.',
            'error_code': 'RESPONSE_GENERATION_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }

def success_response(message: str, data: Any = None, status_code: int = 200) -> tuple:
    """
    성공 응답 생성
    
    Args:
        message: 성공 메시지
        data: 응답 데이터 (선택사항)
        status_code: HTTP 상태 코드 (기본값: 200)
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    try:
        response_data = {
            'success': True,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response_data['data'] = data
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"성공 응답 생성 중 오류 발생: {str(e)}")
        return jsonify({
            'success': False,
            'message': '응답 생성 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


def error_response(message: str, status_code: int = 400, error_code: str = None, details: Dict = None) -> tuple:
    """
    오류 응답 생성
    
    Args:
        message: 오류 메시지
        status_code: HTTP 상태 코드 (기본값: 400)
        error_code: 오류 코드 (선택사항)
        details: 추가 오류 세부사항 (선택사항)
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    try:
        response_data = {
            'success': False,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if error_code:
            response_data['error_code'] = error_code
        
        if details:
            response_data['details'] = details
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"오류 응답 생성 중 오류 발생: {str(e)}")
        return jsonify({
            'success': False,
            'message': '응답 생성 중 오류가 발생했습니다.',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


def paginated_response(message: str, data: list, page: int, per_page: int, total: int, status_code: int = 200) -> tuple:
    """
    페이지네이션된 응답 생성
    
    Args:
        message: 응답 메시지
        data: 페이지네이션된 데이터 리스트
        page: 현재 페이지 번호
        per_page: 페이지당 항목 수
        total: 전체 항목 수
        status_code: HTTP 상태 코드 (기본값: 200)
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    try:
        # 페이지네이션 메타데이터 계산
        total_pages = (total + per_page - 1) // per_page  # 올림 계산
        has_prev = page > 1
        has_next = page < total_pages
        
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': page - 1 if has_prev else None,
                'next_page': page + 1 if has_next else None
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"페이지네이션 응답 생성 중 오류 발생: {str(e)}")
        return error_response("페이지네이션 응답 생성 중 오류가 발생했습니다.", 500)


def validation_error_response(errors: Dict[str, str], status_code: int = 400) -> tuple:
    """
    검증 오류 응답 생성
    
    Args:
        errors: 필드별 오류 메시지 딕셔너리
        status_code: HTTP 상태 코드 (기본값: 400)
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    try:
        response_data = {
            'success': False,
            'message': '입력 데이터 검증에 실패했습니다.',
            'error_code': 'VALIDATION_ERROR',
            'errors': errors,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"검증 오류 응답 생성 중 오류 발생: {str(e)}")
        return error_response("검증 오류 응답 생성 중 오류가 발생했습니다.", 500)


def unauthorized_response(message: str = "인증이 필요합니다.") -> tuple:
    """
    인증 오류 응답 생성 (401)
    
    Args:
        message: 인증 오류 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 401, 'UNAUTHORIZED')


def forbidden_response(message: str = "접근 권한이 없습니다.") -> tuple:
    """
    권한 오류 응답 생성 (403)
    
    Args:
        message: 권한 오류 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 403, 'FORBIDDEN')


def not_found_response(message: str = "요청한 리소스를 찾을 수 없습니다.") -> tuple:
    """
    리소스 없음 응답 생성 (404)
    
    Args:
        message: 리소스 없음 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 404, 'NOT_FOUND')


def conflict_response(message: str = "리소스 충돌이 발생했습니다.") -> tuple:
    """
    리소스 충돌 응답 생성 (409)
    
    Args:
        message: 충돌 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 409, 'CONFLICT')


def internal_server_error_response(message: str = "서버 내부 오류가 발생했습니다.") -> tuple:
    """
    서버 내부 오류 응답 생성 (500)
    
    Args:
        message: 서버 오류 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 500, 'INTERNAL_SERVER_ERROR')


def rate_limit_response(message: str = "요청 한도를 초과했습니다.") -> tuple:
    """
    요청 한도 초과 응답 생성 (429)
    
    Args:
        message: 요청 한도 초과 메시지
        
    Returns:
        Flask JSON 응답과 상태 코드 튜플
    """
    return error_response(message, 429, 'RATE_LIMIT_EXCEEDED')


def format_model_data(model_instance, fields: list = None, exclude_fields: list = None) -> Dict:
    """
    SQLAlchemy 모델 인스턴스를 딕셔너리로 변환
    
    Args:
        model_instance: SQLAlchemy 모델 인스턴스
        fields: 포함할 필드 리스트 (선택사항)
        exclude_fields: 제외할 필드 리스트 (선택사항)
        
    Returns:
        모델 데이터 딕셔너리
    """
    try:
        if not model_instance:
            return {}
        
        # 모델의 모든 컬럼 가져오기
        data = {}
        for column in model_instance.__table__.columns:
            column_name = column.name
            
            # 필드 필터링
            if fields and column_name not in fields:
                continue
            if exclude_fields and column_name in exclude_fields:
                continue
            
            value = getattr(model_instance, column_name)
            
            # datetime 객체를 ISO 형식 문자열로 변환
            if isinstance(value, datetime):
                value = value.isoformat()
            
            data[column_name] = value
        
        return data
        
    except Exception as e:
        logger.error(f"모델 데이터 변환 중 오류 발생: {str(e)}")
        return {}


def format_model_list(model_list: list, fields: list = None, exclude_fields: list = None) -> list:
    """
    SQLAlchemy 모델 인스턴스 리스트를 딕셔너리 리스트로 변환
    
    Args:
        model_list: SQLAlchemy 모델 인스턴스 리스트
        fields: 포함할 필드 리스트 (선택사항)
        exclude_fields: 제외할 필드 리스트 (선택사항)
        
    Returns:
        모델 데이터 딕셔너리 리스트
    """
    try:
        if not model_list:
            return []
        
        return [format_model_data(model, fields, exclude_fields) for model in model_list]
        
    except Exception as e:
        logger.error(f"모델 리스트 변환 중 오류 발생: {str(e)}")
        return []