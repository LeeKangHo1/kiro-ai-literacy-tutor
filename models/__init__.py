# models/__init__.py
# SQLAlchemy 모델 패키지

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# SQLAlchemy 인스턴스 생성
db = SQLAlchemy()

class BaseModel:
    """모든 모델의 기본 클래스"""
    
    def save(self):
        """모델 인스턴스를 데이터베이스에 저장"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        """모델 인스턴스를 데이터베이스에서 삭제"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, **kwargs):
        """모델 인스턴스 업데이트"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            if hasattr(self, 'updated_at'):
                self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        """모델 인스턴스를 딕셔너리로 변환"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, (dict, list)):
                result[column.name] = value
            else:
                result[column.name] = value
        return result
    
    @classmethod
    def get_by_id(cls, id):
        """ID로 모델 인스턴스 조회"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """모든 모델 인스턴스 조회"""
        return cls.query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """새 모델 인스턴스 생성 및 저장"""
        instance = cls(**kwargs)
        instance.save()
        return instance

# 모델 클래스들을 import
from .user import User
from .chapter import Chapter
from .learning_loop import LearningLoop
from .conversation import Conversation
from .quiz_attempt import QuizAttempt

# UserLearningProgress 모델은 user.py에서 정의됨
from .user import UserLearningProgress

__all__ = [
    'db', 
    'BaseModel',
    'User', 
    'Chapter', 
    'UserLearningProgress',
    'LearningLoop', 
    'Conversation', 
    'QuizAttempt'
]