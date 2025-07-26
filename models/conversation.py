# models/conversation.py
# 대화 기록 모델

from . import db, BaseModel
from datetime import datetime
import json

class Conversation(db.Model, BaseModel):
    """대화 기록 모델"""
    __tablename__ = 'CONVERSATIONS'
    
    conversation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loop_id = db.Column(db.String(100), db.ForeignKey('LEARNING_LOOPS.loop_id', ondelete='CASCADE'), nullable=False, index=True)
    agent_name = db.Column(db.String(100), nullable=False, index=True)
    message_type = db.Column(
        db.Enum('user', 'system', 'tool', 'router', name='message_type_enum'),
        nullable=False, index=True
    )
    user_message = db.Column(db.Text)  # 사용자 메시지
    system_response = db.Column(db.Text)  # 시스템 응답
    ui_elements = db.Column(db.JSON)  # UI 요소 정보
    ui_mode = db.Column(
        db.Enum('chat', 'quiz', 'restricted', 'error', name='ui_mode_enum'),
        default='chat'
    )
    processing_time_ms = db.Column(db.Integer, default=0)  # 처리 시간 (밀리초)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sequence_order = db.Column(db.Integer, nullable=False, index=True)
    conv_metadata = db.Column(db.JSON)  # 추가 메타데이터
    
    # 복합 유니크 제약조건
    __table_args__ = (
        db.UniqueConstraint('loop_id', 'sequence_order', name='uk_loop_sequence'),
    )
    
    def __init__(self, loop_id, agent_name, message_type, sequence_order,
                 user_message=None, system_response=None, ui_elements=None, 
                 ui_mode='chat', processing_time_ms=0, conv_metadata=None):
        self.loop_id = loop_id
        self.agent_name = agent_name
        self.message_type = message_type
        self.sequence_order = sequence_order
        self.user_message = user_message
        self.system_response = system_response
        self.ui_elements = ui_elements or {}
        self.ui_mode = ui_mode
        self.processing_time_ms = processing_time_ms
        self.conv_metadata = conv_metadata or {}
    
    def get_ui_elements(self):
        """UI 요소 반환"""
        return self.ui_elements or {}
    
    def update_ui_elements(self, elements):
        """UI 요소 업데이트"""
        if self.ui_elements:
            self.ui_elements.update(elements)
        else:
            self.ui_elements = elements
        self.save()
    
    def add_ui_element(self, key, value):
        """UI 요소 추가"""
        if not self.ui_elements:
            self.ui_elements = {}
        self.ui_elements[key] = value
        self.save()
    
    def get_metadata(self):
        """메타데이터 반환"""
        return self.conv_metadata or {}
    
    def update_metadata(self, key, value):
        """메타데이터 업데이트"""
        if not self.conv_metadata:
            self.conv_metadata = {}
        self.conv_metadata[key] = value
        self.save()
    
    def get_message_content(self):
        """메시지 내용 반환 (타입에 따라)"""
        if self.message_type == 'user':
            return self.user_message
        elif self.message_type in ['system', 'tool', 'router']:
            return self.system_response
        return None
    
    def get_display_info(self):
        """화면 표시용 정보 반환"""
        return {
            'conversation_id': self.conversation_id,
            'agent_name': self.agent_name,
            'message_type': self.message_type,
            'content': self.get_message_content(),
            'ui_elements': self.get_ui_elements(),
            'ui_mode': self.ui_mode,
            'timestamp': self.timestamp.isoformat(),
            'sequence_order': self.sequence_order
        }
    
    def is_user_message(self):
        """사용자 메시지인지 확인"""
        return self.message_type == 'user'
    
    def is_system_message(self):
        """시스템 메시지인지 확인"""
        return self.message_type in ['system', 'tool', 'router']
    
    def get_processing_time_seconds(self):
        """처리 시간을 초 단위로 반환"""
        return self.processing_time_ms / 1000.0
    
    @classmethod
    def get_loop_conversations(cls, loop_id, limit=None):
        """루프의 대화 목록 조회"""
        query = cls.query.filter_by(loop_id=loop_id).order_by(cls.sequence_order)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_recent_conversations(cls, loop_id, limit=10):
        """최근 대화 조회"""
        return cls.query.filter_by(loop_id=loop_id).order_by(
            db.desc(cls.sequence_order)
        ).limit(limit).all()
    
    @classmethod
    def get_conversations_by_agent(cls, loop_id, agent_name):
        """특정 에이전트의 대화 조회"""
        return cls.query.filter_by(
            loop_id=loop_id,
            agent_name=agent_name
        ).order_by(cls.sequence_order).all()
    
    @classmethod
    def get_conversations_by_type(cls, loop_id, message_type):
        """메시지 타입별 대화 조회"""
        return cls.query.filter_by(
            loop_id=loop_id,
            message_type=message_type
        ).order_by(cls.sequence_order).all()
    
    @classmethod
    def get_user_interactions(cls, loop_id):
        """사용자 상호작용만 조회"""
        return cls.get_conversations_by_type(loop_id, 'user')
    
    @classmethod
    def get_system_responses(cls, loop_id):
        """시스템 응답만 조회"""
        return cls.query.filter(
            cls.loop_id == loop_id,
            cls.message_type.in_(['system', 'tool', 'router'])
        ).order_by(cls.sequence_order).all()
    
    @classmethod
    def get_conversation_stats(cls, loop_id):
        """대화 통계"""
        conversations = cls.get_loop_conversations(loop_id)
        
        if not conversations:
            return {
                'total_messages': 0,
                'user_messages': 0,
                'system_messages': 0,
                'average_processing_time_ms': 0,
                'total_duration_minutes': 0
            }
        
        user_messages = len([c for c in conversations if c.message_type == 'user'])
        system_messages = len([c for c in conversations if c.message_type != 'user'])
        avg_processing_time = sum([c.processing_time_ms for c in conversations]) / len(conversations)
        
        # 전체 대화 지속 시간 계산
        first_msg = conversations[0]
        last_msg = conversations[-1]
        duration = (last_msg.timestamp - first_msg.timestamp).total_seconds() / 60
        
        return {
            'total_messages': len(conversations),
            'user_messages': user_messages,
            'system_messages': system_messages,
            'average_processing_time_ms': round(avg_processing_time, 2),
            'total_duration_minutes': round(duration, 2)
        }
    
    @classmethod
    def search_conversations(cls, loop_id, search_term):
        """대화 내용 검색"""
        return cls.query.filter(
            cls.loop_id == loop_id,
            db.or_(
                cls.user_message.contains(search_term),
                cls.system_response.contains(search_term)
            )
        ).order_by(cls.sequence_order).all()
    
    def get_context_window(self, window_size=3):
        """주변 대화 맥락 조회"""
        start_seq = max(1, self.sequence_order - window_size)
        end_seq = self.sequence_order + window_size
        
        return Conversation.query.filter(
            Conversation.loop_id == self.loop_id,
            Conversation.sequence_order.between(start_seq, end_seq)
        ).order_by(Conversation.sequence_order).all()
    
    def __repr__(self):
        return f'<Conversation {self.conversation_id} Loop:{self.loop_id} Agent:{self.agent_name} Type:{self.message_type}>'