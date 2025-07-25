# models/user.py
# 사용자 모델 및 학습 진도 모델

from . import db, BaseModel
from datetime import datetime
from sqlalchemy import func
from utils.password_utils import hash_password, verify_password

class User(db.Model, BaseModel):
    """사용자 모델"""
    __tablename__ = 'USERS'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('beginner', 'business', name='user_type_enum'), nullable=False, index=True)
    user_level = db.Column(db.Enum('low', 'medium', 'high', name='user_level_enum'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 관계 설정
    learning_progress = db.relationship('UserLearningProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    learning_loops = db.relationship('LearningLoop', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, user_type, user_level='low'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.user_type = user_type
        self.user_level = user_level
    
    def set_password(self, password):
        """비밀번호 해시화하여 저장"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """비밀번호 검증"""
        return verify_password(password, self.password_hash)
    
    def get_learning_progress(self, chapter_id=None):
        """학습 진도 조회"""
        if chapter_id:
            return self.learning_progress.filter_by(chapter_id=chapter_id).first()
        return self.learning_progress.all()
    
    def get_overall_progress(self):
        """전체 학습 진도 통계"""
        progress_data = self.learning_progress.all()
        if not progress_data:
            return {
                'total_chapters': 0,
                'completed_chapters': 0,
                'in_progress_chapters': 0,
                'average_understanding': 0.0,
                'total_study_time': 0
            }
        
        completed = len([p for p in progress_data if p.completion_status == 'completed'])
        in_progress = len([p for p in progress_data if p.completion_status == 'in_progress'])
        avg_understanding = sum([p.understanding_score for p in progress_data]) / len(progress_data)
        total_time = sum([p.total_study_time for p in progress_data])
        
        return {
            'total_chapters': len(progress_data),
            'completed_chapters': completed,
            'in_progress_chapters': in_progress,
            'average_understanding': round(avg_understanding, 2),
            'total_study_time': total_time
        }
    
    def get_recent_activity(self, limit=10):
        """최근 활동 조회"""
        return self.learning_loops.order_by(
            db.desc('started_at')
        ).limit(limit).all()
    
    @classmethod
    def get_by_username(cls, username):
        """사용자명으로 사용자 조회"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """이메일로 사용자 조회"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def authenticate(cls, username_or_email, password):
        """사용자 인증"""
        user = cls.get_by_username(username_or_email) or cls.get_by_email(username_or_email)
        if user and user.check_password(password) and user.is_active:
            return user
        return None
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserLearningProgress(db.Model, BaseModel):
    """사용자 학습 진도 모델"""
    __tablename__ = 'USER_LEARNING_PROGRESS'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('CHAPTERS.chapter_id', ondelete='CASCADE'), nullable=False)
    progress_percentage = db.Column(db.Numeric(5, 2), default=0.00, index=True)
    understanding_score = db.Column(db.Numeric(5, 2), default=0.00, index=True)
    completion_status = db.Column(
        db.Enum('not_started', 'in_progress', 'completed', 'skipped', name='completion_status_enum'),
        default='not_started', index=True
    )
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total_study_time = db.Column(db.Integer, default=0)  # 분 단위
    quiz_attempts_count = db.Column(db.Integer, default=0)
    average_quiz_score = db.Column(db.Numeric(5, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 복합 유니크 제약조건
    __table_args__ = (
        db.UniqueConstraint('user_id', 'chapter_id', name='uk_user_chapter'),
    )
    
    def start_learning(self):
        """학습 시작"""
        if self.completion_status == 'not_started':
            self.completion_status = 'in_progress'
            self.started_at = datetime.utcnow()
            self.last_accessed_at = datetime.utcnow()
            self.save()
    
    def complete_learning(self):
        """학습 완료"""
        self.completion_status = 'completed'
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.00
        self.last_accessed_at = datetime.utcnow()
        self.save()
    
    def update_progress(self, progress_percentage=None, understanding_score=None, study_time_minutes=0):
        """진도 업데이트"""
        if progress_percentage is not None:
            self.progress_percentage = min(100.00, max(0.00, progress_percentage))
        
        if understanding_score is not None:
            self.understanding_score = min(100.00, max(0.00, understanding_score))
        
        if study_time_minutes > 0:
            self.total_study_time += study_time_minutes
        
        self.last_accessed_at = datetime.utcnow()
        
        # 진도가 100%면 자동으로 완료 처리
        if self.progress_percentage >= 100.00 and self.completion_status != 'completed':
            self.complete_learning()
        else:
            self.save()
    
    def add_quiz_attempt(self, score):
        """퀴즈 시도 결과 추가"""
        self.quiz_attempts_count += 1
        
        # 평균 점수 계산
        if self.quiz_attempts_count == 1:
            self.average_quiz_score = score
        else:
            current_total = self.average_quiz_score * (self.quiz_attempts_count - 1)
            self.average_quiz_score = (current_total + score) / self.quiz_attempts_count
        
        self.last_accessed_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def get_or_create(cls, user_id, chapter_id):
        """사용자-챕터 진도 조회 또는 생성"""
        progress = cls.query.filter_by(user_id=user_id, chapter_id=chapter_id).first()
        if not progress:
            progress = cls(user_id=user_id, chapter_id=chapter_id)
            progress.save()
        return progress
    
    @classmethod
    def get_user_progress_summary(cls, user_id):
        """사용자의 전체 진도 요약"""
        return cls.query.filter_by(user_id=user_id).all()
    
    def __repr__(self):
        return f'<UserLearningProgress User:{self.user_id} Chapter:{self.chapter_id} Status:{self.completion_status}>'