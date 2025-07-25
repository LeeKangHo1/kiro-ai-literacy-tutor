# models/quiz_attempt.py
# 퀴즈 시도 기록 모델

from . import db, BaseModel
from datetime import datetime
import json

class QuizAttempt(db.Model, BaseModel):
    """퀴즈 시도 기록 모델"""
    __tablename__ = 'QUIZ_ATTEMPTS'
    
    attempt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('CHAPTERS.chapter_id', ondelete='CASCADE'), nullable=False)
    loop_id = db.Column(db.String(100), db.ForeignKey('LEARNING_LOOPS.loop_id', ondelete='SET NULL'), nullable=True, index=True)
    quiz_type = db.Column(
        db.Enum('multiple_choice', 'prompt_practice', 'diagnostic', name='quiz_type_enum'),
        nullable=False, index=True
    )
    question_content = db.Column(db.JSON, nullable=False)  # 문제 내용 (JSON 형태)
    user_answer = db.Column(db.Text)  # 사용자 답변
    correct_answer = db.Column(db.Text)  # 정답
    is_correct = db.Column(db.Boolean, default=False, index=True)  # 정답 여부
    score = db.Column(db.Numeric(5, 2), default=0.00, index=True)  # 점수 (0.00 ~ 100.00)
    hint_used = db.Column(db.Boolean, default=False)  # 힌트 사용 여부
    hint_content = db.Column(db.Text)  # 사용된 힌트 내용
    feedback = db.Column(db.Text)  # 피드백 내용
    time_taken_seconds = db.Column(db.Integer, default=0)  # 소요 시간 (초)
    difficulty_level = db.Column(
        db.Enum('low', 'medium', 'high', name='difficulty_level_enum'),
        nullable=False, index=True
    )
    attempt_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metadata = db.Column(db.JSON)  # 추가 메타데이터
    
    # 인덱스 설정
    __table_args__ = (
        db.Index('idx_user_chapter', 'user_id', 'chapter_id'),
    )
    
    def __init__(self, user_id, chapter_id, quiz_type, question_content, 
                 difficulty_level, loop_id=None, user_answer=None, correct_answer=None,
                 hint_used=False, hint_content=None, metadata=None):
        self.user_id = user_id
        self.chapter_id = chapter_id
        self.loop_id = loop_id
        self.quiz_type = quiz_type
        self.question_content = question_content
        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.difficulty_level = difficulty_level
        self.hint_used = hint_used
        self.hint_content = hint_content
        self.metadata = metadata or {}
    
    def evaluate_answer(self, user_answer, feedback=None):
        """답변 평가 및 점수 계산"""
        self.user_answer = user_answer
        self.feedback = feedback
        
        if self.quiz_type == 'multiple_choice':
            self.is_correct = (user_answer.strip().lower() == self.correct_answer.strip().lower())
            self.score = 100.0 if self.is_correct else 0.0
        
        elif self.quiz_type == 'prompt_practice':
            # 프롬프트 실습의 경우 더 복잡한 평가 로직 필요
            # 여기서는 기본적인 평가만 구현
            self.is_correct = True  # 프롬프트 실습은 일반적으로 정답/오답이 명확하지 않음
            self.score = self.calculate_prompt_score(user_answer)
        
        elif self.quiz_type == 'diagnostic':
            # 진단 퀴즈의 경우 정답 여부보다는 수준 파악이 목적
            self.is_correct = (user_answer.strip().lower() == self.correct_answer.strip().lower())
            self.score = 100.0 if self.is_correct else 0.0
        
        # 힌트 사용 시 점수 감점
        if self.hint_used:
            self.score = max(0.0, self.score * 0.8)  # 20% 감점
        
        self.save()
        
        # 사용자 학습 진도에 퀴즈 결과 반영
        self.update_user_progress()
    
    def calculate_prompt_score(self, user_answer):
        """프롬프트 답변 점수 계산 (기본 구현)"""
        if not user_answer or len(user_answer.strip()) < 10:
            return 20.0
        
        # 기본적인 점수 계산 로직
        # 실제로는 LLM을 사용하여 더 정교한 평가 가능
        score = 60.0  # 기본 점수
        
        # 길이 기반 점수 (적절한 길이)
        if 50 <= len(user_answer) <= 500:
            score += 20.0
        
        # 키워드 포함 여부 (예시)
        keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '프롬프트']
        keyword_count = sum(1 for keyword in keywords if keyword in user_answer)
        score += min(20.0, keyword_count * 5.0)
        
        return min(100.0, score)
    
    def use_hint(self, hint_content):
        """힌트 사용"""
        self.hint_used = True
        self.hint_content = hint_content
        self.save()
    
    def update_user_progress(self):
        """사용자 학습 진도에 퀴즈 결과 반영"""
        from .user import UserLearningProgress
        
        progress = UserLearningProgress.get_or_create(self.user_id, self.chapter_id)
        progress.add_quiz_attempt(self.score)
    
    def get_question_content(self):
        """문제 내용 반환"""
        return self.question_content or {}
    
    def get_metadata(self):
        """메타데이터 반환"""
        return self.metadata or {}
    
    def update_metadata(self, key, value):
        """메타데이터 업데이트"""
        if not self.metadata:
            self.metadata = {}
        self.metadata[key] = value
        self.save()
    
    def get_performance_summary(self):
        """성과 요약"""
        return {
            'attempt_id': self.attempt_id,
            'quiz_type': self.quiz_type,
            'is_correct': self.is_correct,
            'score': float(self.score),
            'hint_used': self.hint_used,
            'time_taken_seconds': self.time_taken_seconds,
            'difficulty_level': self.difficulty_level,
            'attempt_timestamp': self.attempt_timestamp.isoformat()
        }
    
    def get_time_taken_formatted(self):
        """소요 시간을 포맷된 문자열로 반환"""
        minutes = self.time_taken_seconds // 60
        seconds = self.time_taken_seconds % 60
        
        if minutes > 0:
            return f"{minutes}분 {seconds}초"
        else:
            return f"{seconds}초"
    
    @classmethod
    def get_user_attempts(cls, user_id, chapter_id=None, quiz_type=None, limit=None):
        """사용자 퀴즈 시도 기록 조회"""
        query = cls.query.filter_by(user_id=user_id)
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        if quiz_type:
            query = query.filter_by(quiz_type=quiz_type)
        
        query = query.order_by(db.desc(cls.attempt_timestamp))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_chapter_attempts(cls, chapter_id, quiz_type=None):
        """챕터별 퀴즈 시도 기록 조회"""
        query = cls.query.filter_by(chapter_id=chapter_id)
        
        if quiz_type:
            query = query.filter_by(quiz_type=quiz_type)
        
        return query.order_by(db.desc(cls.attempt_timestamp)).all()
    
    @classmethod
    def get_user_quiz_stats(cls, user_id, chapter_id=None):
        """사용자 퀴즈 통계"""
        query = cls.query.filter_by(user_id=user_id)
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        attempts = query.all()
        
        if not attempts:
            return {
                'total_attempts': 0,
                'correct_attempts': 0,
                'success_rate': 0,
                'average_score': 0,
                'total_time_seconds': 0,
                'hint_usage_rate': 0
            }
        
        correct_attempts = len([a for a in attempts if a.is_correct])
        total_score = sum([a.score for a in attempts])
        total_time = sum([a.time_taken_seconds for a in attempts])
        hint_used_count = len([a for a in attempts if a.hint_used])
        
        return {
            'total_attempts': len(attempts),
            'correct_attempts': correct_attempts,
            'success_rate': round((correct_attempts / len(attempts)) * 100, 2),
            'average_score': round(total_score / len(attempts), 2),
            'total_time_seconds': total_time,
            'hint_usage_rate': round((hint_used_count / len(attempts)) * 100, 2)
        }
    
    @classmethod
    def get_difficulty_performance(cls, user_id, difficulty_level):
        """난이도별 성과"""
        attempts = cls.query.filter_by(
            user_id=user_id,
            difficulty_level=difficulty_level
        ).all()
        
        if not attempts:
            return None
        
        correct_count = len([a for a in attempts if a.is_correct])
        avg_score = sum([a.score for a in attempts]) / len(attempts)
        
        return {
            'difficulty_level': difficulty_level,
            'total_attempts': len(attempts),
            'success_rate': round((correct_count / len(attempts)) * 100, 2),
            'average_score': round(avg_score, 2)
        }
    
    @classmethod
    def get_recent_attempts(cls, user_id, limit=10):
        """최근 퀴즈 시도 기록"""
        return cls.query.filter_by(user_id=user_id).order_by(
            db.desc(cls.attempt_timestamp)
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<QuizAttempt {self.attempt_id} User:{self.user_id} Chapter:{self.chapter_id} Type:{self.quiz_type} Score:{self.score}>'