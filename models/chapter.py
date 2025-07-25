# models/chapter.py
# 챕터 모델

from . import db, BaseModel
from datetime import datetime
import json

class Chapter(db.Model, BaseModel):
    """챕터 모델"""
    __tablename__ = 'CHAPTERS'
    
    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_number = db.Column(db.Integer, nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.Enum('low', 'medium', 'high', name='difficulty_level_enum'), nullable=False, index=True)
    estimated_duration = db.Column(db.Integer, default=30)  # 예상 소요 시간 (분)
    prerequisites = db.Column(db.JSON)  # 선수 챕터 정보
    learning_objectives = db.Column(db.JSON)  # 학습 목표
    content_metadata = db.Column(db.JSON)  # 콘텐츠 메타데이터
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user_progress = db.relationship('UserLearningProgress', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    learning_loops = db.relationship('LearningLoop', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, chapter_number, title, description=None, difficulty_level='low', 
                 estimated_duration=30, prerequisites=None, learning_objectives=None, content_metadata=None):
        self.chapter_number = chapter_number
        self.title = title
        self.description = description
        self.difficulty_level = difficulty_level
        self.estimated_duration = estimated_duration
        self.prerequisites = prerequisites or []
        self.learning_objectives = learning_objectives or {}
        self.content_metadata = content_metadata or {}
    
    def get_prerequisites(self):
        """선수 챕터 목록 반환"""
        if not self.prerequisites:
            return []
        return self.prerequisites
    
    def get_learning_objectives(self):
        """학습 목표 반환"""
        if not self.learning_objectives:
            return {}
        return self.learning_objectives
    
    def get_content_metadata(self):
        """콘텐츠 메타데이터 반환"""
        if not self.content_metadata:
            return {}
        return self.content_metadata
    
    def check_prerequisites_met(self, user_id):
        """사용자가 선수 조건을 만족하는지 확인"""
        if not self.prerequisites:
            return True
        
        from .user import UserLearningProgress
        
        for prereq_chapter_id in self.prerequisites:
            progress = UserLearningProgress.query.filter_by(
                user_id=user_id, 
                chapter_id=prereq_chapter_id
            ).first()
            
            if not progress or progress.completion_status != 'completed':
                return False
        
        return True
    
    def get_user_progress(self, user_id):
        """특정 사용자의 이 챕터 진도 조회"""
        from .user import UserLearningProgress
        return UserLearningProgress.query.filter_by(
            user_id=user_id, 
            chapter_id=self.chapter_id
        ).first()
    
    def get_completion_stats(self):
        """챕터 완료 통계"""
        from .user import UserLearningProgress
        
        total_users = UserLearningProgress.query.filter_by(chapter_id=self.chapter_id).count()
        completed_users = UserLearningProgress.query.filter_by(
            chapter_id=self.chapter_id, 
            completion_status='completed'
        ).count()
        
        completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0
        
        # 평균 이해도 점수
        avg_understanding = db.session.query(
            db.func.avg(UserLearningProgress.understanding_score)
        ).filter_by(chapter_id=self.chapter_id).scalar() or 0
        
        # 평균 학습 시간
        avg_study_time = db.session.query(
            db.func.avg(UserLearningProgress.total_study_time)
        ).filter_by(chapter_id=self.chapter_id).scalar() or 0
        
        return {
            'total_users': total_users,
            'completed_users': completed_users,
            'completion_rate': round(completion_rate, 2),
            'average_understanding_score': round(float(avg_understanding), 2),
            'average_study_time_minutes': round(float(avg_study_time), 2)
        }
    
    def get_quiz_stats(self):
        """챕터 퀴즈 통계"""
        quiz_attempts = self.quiz_attempts.all()
        
        if not quiz_attempts:
            return {
                'total_attempts': 0,
                'average_score': 0,
                'success_rate': 0,
                'average_time_taken': 0
            }
        
        total_attempts = len(quiz_attempts)
        correct_attempts = len([q for q in quiz_attempts if q.is_correct])
        average_score = sum([q.score for q in quiz_attempts]) / total_attempts
        success_rate = (correct_attempts / total_attempts * 100)
        average_time = sum([q.time_taken_seconds for q in quiz_attempts]) / total_attempts
        
        return {
            'total_attempts': total_attempts,
            'average_score': round(average_score, 2),
            'success_rate': round(success_rate, 2),
            'average_time_taken_seconds': round(average_time, 2)
        }
    
    @classmethod
    def get_by_number(cls, chapter_number):
        """챕터 번호로 조회"""
        return cls.query.filter_by(chapter_number=chapter_number, is_active=True).first()
    
    @classmethod
    def get_active_chapters(cls):
        """활성화된 챕터 목록 조회"""
        return cls.query.filter_by(is_active=True).order_by(cls.chapter_number).all()
    
    @classmethod
    def get_chapters_by_difficulty(cls, difficulty_level):
        """난이도별 챕터 조회"""
        return cls.query.filter_by(
            difficulty_level=difficulty_level, 
            is_active=True
        ).order_by(cls.chapter_number).all()
    
    @classmethod
    def get_available_chapters_for_user(cls, user_id):
        """사용자가 학습 가능한 챕터 목록"""
        chapters = cls.get_active_chapters()
        available_chapters = []
        
        for chapter in chapters:
            if chapter.check_prerequisites_met(user_id):
                available_chapters.append(chapter)
        
        return available_chapters
    
    def update_content_metadata(self, metadata):
        """콘텐츠 메타데이터 업데이트"""
        if self.content_metadata:
            self.content_metadata.update(metadata)
        else:
            self.content_metadata = metadata
        self.save()
    
    def add_learning_objective(self, objective):
        """학습 목표 추가"""
        if not self.learning_objectives:
            self.learning_objectives = {'objectives': []}
        
        if 'objectives' not in self.learning_objectives:
            self.learning_objectives['objectives'] = []
        
        if objective not in self.learning_objectives['objectives']:
            self.learning_objectives['objectives'].append(objective)
            self.save()
    
    def __repr__(self):
        return f'<Chapter {self.chapter_number}: {self.title}>'