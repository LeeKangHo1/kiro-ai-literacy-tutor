# services/database_service.py
"""
데이터베이스 서비스
"""

from models import db
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
import logging
from utils.performance_middleware import database_monitoring

logger = logging.getLogger(__name__)


class DatabaseService:
    """데이터베이스 관련 서비스 클래스"""
    
    @staticmethod
    @database_monitoring("create_record")
    def create_record(model_class, **kwargs) -> Optional[Any]:
        """레코드 생성"""
        try:
            record = model_class(**kwargs)
            db.session.add(record)
            db.session.commit()
            return record
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"레코드 생성 실패: {e}")
            return None
    
    @staticmethod
    @database_monitoring("get_record_by_id")
    def get_record_by_id(model_class, record_id: int) -> Optional[Any]:
        """ID로 레코드 조회"""
        try:
            return model_class.query.get(record_id)
        except SQLAlchemyError as e:
            logger.error(f"레코드 조회 실패: {e}")
            return None
    
    @staticmethod
    @database_monitoring("get_records_by_filter")
    def get_records_by_filter(model_class, **filters) -> List[Any]:
        """필터로 레코드 조회"""
        try:
            return model_class.query.filter_by(**filters).all()
        except SQLAlchemyError as e:
            logger.error(f"레코드 필터 조회 실패: {e}")
            return []
    
    @staticmethod
    def update_record(record, **kwargs) -> bool:
        """레코드 업데이트"""
        try:
            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"레코드 업데이트 실패: {e}")
            return False
    
    @staticmethod
    def delete_record(record) -> bool:
        """레코드 삭제"""
        try:
            db.session.delete(record)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"레코드 삭제 실패: {e}")
            return False
    
    @staticmethod
    def execute_query(query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """직접 쿼리 실행"""
        try:
            result = db.session.execute(query, params or {})
            db.session.commit()
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"쿼리 실행 실패: {e}")
            return None
    
    @staticmethod
    def get_connection_status() -> Dict[str, Any]:
        """데이터베이스 연결 상태 확인"""
        try:
            db.session.execute("SELECT 1")
            return {
                'status': 'connected',
                'message': '데이터베이스 연결 정상'
            }
        except SQLAlchemyError as e:
            return {
                'status': 'disconnected',
                'message': f'데이터베이스 연결 실패: {e}'
            }


# 편의를 위한 함수들
def database_service():
    """DatabaseService 인스턴스 반환"""
    return DatabaseService()