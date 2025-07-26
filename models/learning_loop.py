# models/learning_loop.py
# 학습 루프 모델

from . import db, BaseModel
from datetime import datetime
import uuid
import json

class LearningLoop(db.Model, BaseModel):
    """학습 루프 모델"""
    __tablename__ = 'LEARNING_LOOPS'
    
    loop_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('USERS.user_id', ondelete='CASCADE'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('CHAPTERS.chapter_id', ondelete='CASCADE'), nullable=False)
    loop_sequence = db.Column(db.Integer, nullable=False, index=True)
    loop_status = db.Column(
        db.Enum('active', 'completed', 'abandoned', name='loop_status_enum'),
        default='active', index=True
    )
    loop_summary = db.Column(db.Text)  # 루프 요약 (압축된 대화 내용)
    loop_type = db.Column(
        db.Enum('theory', 'quiz', 'qna', 'mixed', name='loop_type_enum'),
        default='mixed'
    )
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, index=True)
    duration_minutes = db.Column(db.Integer, default=0)  # 루프 소요 시간 (분)
    interaction_count = db.Column(db.Integer, default=0)  # 상호작용 횟수
    loop_metadata = db.Column(db.JSON)  # 추가 메타데이터
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    conversations = db.relationship('Conversation', backref='learning_loop', lazy='dynamic', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='learning_loop', lazy='dynamic')
    
    # 복합 유니크 제약조건
    __table_args__ = (
        db.UniqueConstraint('user_id', 'chapter_id', 'loop_sequence', name='uk_user_chapter_sequence'),
        db.Index('idx_user_chapter', 'user_id', 'chapter_id'),
    )
    
    def __init__(self, user_id, chapter_id, loop_type='mixed', loop_metadata=None):
        self.loop_id = self.generate_loop_id()
        self.user_id = user_id
        self.chapter_id = chapter_id
        self.loop_type = loop_type
        self.loop_sequence = self.get_next_sequence_number()
        self.loop_metadata = loop_metadata or {}
    
    @staticmethod
    def generate_loop_id():
        """고유한 루프 ID 생성"""
        return f"loop_{uuid.uuid4().hex[:16]}_{int(datetime.utcnow().timestamp())}"
    
    def get_next_sequence_number(self):
        """다음 시퀀스 번호 계산"""
        last_loop = LearningLoop.query.filter_by(
            user_id=self.user_id,
            chapter_id=self.chapter_id
        ).order_by(db.desc(LearningLoop.loop_sequence)).first()
        
        return (last_loop.loop_sequence + 1) if last_loop else 1
    
    def start_loop(self):
        """루프 시작"""
        self.loop_status = 'active'
        self.started_at = datetime.utcnow()
        self.save()
    
    def complete_loop(self, summary=None):
        """루프 완료"""
        self.loop_status = 'completed'
        self.completed_at = datetime.utcnow()
        
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
        
        if summary:
            self.loop_summary = summary
        
        # 상호작용 횟수 업데이트
        self.interaction_count = self.conversations.count()
        
        self.save()
        
        # 사용자 학습 진도 업데이트
        self.update_user_progress()
    
    def abandon_loop(self, reason=None):
        """루프 중단"""
        self.loop_status = 'abandoned'
        self.completed_at = datetime.utcnow()
        
        if reason:
            if not self.loop_metadata:
                self.loop_metadata = {}
            self.loop_metadata['abandon_reason'] = reason
        
        self.save()
    
    def add_conversation(self, agent_name, message_type, user_message=None, 
                        system_response=None, ui_elements=None, ui_mode='chat'):
        """대화 추가"""
        from .conversation import Conversation
        
        sequence_order = self.conversations.count() + 1
        
        conversation = Conversation(
            loop_id=self.loop_id,
            agent_name=agent_name,
            message_type=message_type,
            user_message=user_message,
            system_response=system_response,
            ui_elements=ui_elements,
            ui_mode=ui_mode,
            sequence_order=sequence_order
        )
        conversation.save()
        return conversation
    
    def get_conversations(self, limit=None):
        """대화 목록 조회"""
        query = self.conversations.order_by('sequence_order')
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_conversation_summary(self):
        """대화 요약 생성"""
        conversations = self.get_conversations()
        
        if not conversations:
            return "대화 내용이 없습니다."
        
        # 간단한 요약 생성 (실제로는 LLM을 사용할 수 있음)
        summary_parts = []
        for conv in conversations:
            if conv.message_type == 'user' and conv.user_message:
                summary_parts.append(f"사용자: {conv.user_message[:100]}...")
            elif conv.message_type == 'system' and conv.system_response:
                summary_parts.append(f"{conv.agent_name}: {conv.system_response[:100]}...")
        
        return "\n".join(summary_parts[:10])  # 최대 10개 항목
    
    def update_user_progress(self):
        """사용자 학습 진도 업데이트"""
        from .user import UserLearningProgress
        
        progress = UserLearningProgress.get_or_create(self.user_id, self.chapter_id)
        
        # 루프 완료에 따른 진도 증가 (예: 루프당 20% 증가)
        progress_increment = 20.0
        new_progress = min(100.0, progress.progress_percentage + progress_increment)
        
        # 퀴즈 결과를 바탕으로 이해도 점수 계산
        quiz_attempts = self.quiz_attempts.all()
        if quiz_attempts:
            avg_quiz_score = sum([q.score for q in quiz_attempts]) / len(quiz_attempts)
            understanding_score = avg_quiz_score
        else:
            understanding_score = progress.understanding_score
        
        progress.update_progress(
            progress_percentage=new_progress,
            understanding_score=understanding_score,
            study_time_minutes=self.duration_minutes
        )
    
    def get_performance_metrics(self):
        """루프 성과 지표"""
        conversations = self.get_conversations()
        quiz_attempts = self.quiz_attempts.all()
        
        metrics = {
            'loop_id': self.loop_id,
            'duration_minutes': self.duration_minutes,
            'interaction_count': len(conversations),
            'quiz_attempts_count': len(quiz_attempts),
            'quiz_success_rate': 0,
            'average_quiz_score': 0,
            'completion_status': self.loop_status
        }
        
        if quiz_attempts:
            correct_attempts = len([q for q in quiz_attempts if q.is_correct])
            metrics['quiz_success_rate'] = (correct_attempts / len(quiz_attempts)) * 100
            metrics['average_quiz_score'] = sum([q.score for q in quiz_attempts]) / len(quiz_attempts)
        
        return metrics
    
    @classmethod
    def get_user_loops(cls, user_id, chapter_id=None, status=None, limit=None):
        """사용자 루프 조회"""
        query = cls.query.filter_by(user_id=user_id)
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        if status:
            query = query.filter_by(loop_status=status)
        
        query = query.order_by(db.desc(cls.started_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_recent_loops_summary(cls, user_id, chapter_id, limit=5):
        """최근 루프 요약 조회 (State 관리용)"""
        loops = cls.query.filter_by(
            user_id=user_id,
            chapter_id=chapter_id,
            loop_status='completed'
        ).order_by(db.desc(cls.completed_at)).limit(limit).all()
        
        summaries = []
        for loop in loops:
            summaries.append({
                'loop_id': loop.loop_id,
                'summary': loop.loop_summary or loop.get_conversation_summary(),
                'completed_at': loop.completed_at.isoformat() if loop.completed_at else None,
                'loop_type': loop.loop_type,
                'performance': loop.get_performance_metrics()
            })
        
        return summaries
    
    @classmethod
    def get_active_loop(cls, user_id, chapter_id):
        """활성 루프 조회"""
        return cls.query.filter_by(
            user_id=user_id,
            chapter_id=chapter_id,
            loop_status='active'
        ).first()
    
    def update_metadata(self, key, value):
        """메타데이터 업데이트"""
        if not self.loop_metadata:
            self.loop_metadata = {}
        self.loop_metadata[key] = value
        self.save()
    
    def __repr__(self):
        return f'<LearningLoop {self.loop_id} User:{self.user_id} Chapter:{self.chapter_id} Status:{self.loop_status}>'