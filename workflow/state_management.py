# workflow/state_management.py
# TutorState 관리 및 검증 모듈

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import uuid
import json


class TutorState(TypedDict):
    """튜터 시스템의 전체 상태를 관리하는 TypedDict 클래스"""
    
    # 기본 정보
    user_id: str                    # 사용자 고유 ID
    user_message: str               # 현재 사용자 메시지
    current_chapter: int            # 현재 학습 중인 챕터
    current_stage: str              # 현재 학습 단계
    user_level: str                 # 사용자 수준 (low/medium/high)
    user_type: str                  # 사용자 유형 (beginner/business)
    
    # 라우팅 관리
    qa_source_router: str           # 질문 출처 라우터 식별
    ui_mode: str                    # UI 모드 (chat/quiz/restricted)
    
    # 현재 루프 대화 (임시)
    current_loop_conversations: List[Dict[str, Any]]
    
    # 최근 루프 요약 (최대 5개)
    recent_loops_summary: List[Dict[str, str]]
    
    # 현재 루프 메타정보
    current_loop_id: str            # 현재 루프 고유 ID
    loop_start_time: str            # 루프 시작 시간 (ISO format)
    
    # 시스템 응답
    system_message: str             # 시스템 메시지
    ui_elements: Optional[Dict[str, Any]]  # UI 요소 정보


class StateManager:
    """TutorState 관리 및 검증을 담당하는 클래스"""
    
    @staticmethod
    def create_initial_state(user_id: str, user_type: str = "beginner", 
                           user_level: str = "low") -> TutorState:
        """초기 상태 생성"""
        return TutorState(
            user_id=user_id,
            user_message="",
            current_chapter=1,
            current_stage="theory",
            user_level=user_level,
            user_type=user_type,
            qa_source_router="",
            ui_mode="chat",
            current_loop_conversations=[],
            recent_loops_summary=[],
            current_loop_id=str(uuid.uuid4()),
            loop_start_time=datetime.now().isoformat(),
            system_message="",
            ui_elements=None
        )
    
    @staticmethod
    def validate_state(state: TutorState) -> bool:
        """상태 유효성 검증"""
        required_fields = [
            'user_id', 'user_message', 'current_chapter', 'current_stage',
            'user_level', 'user_type', 'qa_source_router', 'ui_mode',
            'current_loop_conversations', 'recent_loops_summary',
            'current_loop_id', 'loop_start_time', 'system_message'
        ]
        
        for field in required_fields:
            if field not in state:
                return False
        
        # 타입별 추가 검증
        if state['user_level'] not in ['low', 'medium', 'high']:
            return False
        
        if state['user_type'] not in ['beginner', 'business']:
            return False
        
        if state['ui_mode'] not in ['chat', 'quiz', 'restricted', 'error']:
            return False
        
        return True
    
    @staticmethod
    def start_new_loop(state: TutorState) -> TutorState:
        """새로운 학습 루프 시작"""
        # 현재 루프가 있다면 요약으로 저장
        if state['current_loop_conversations']:
            loop_summary = StateManager._create_loop_summary(state)
            state['recent_loops_summary'].append(loop_summary)
            
            # 최대 5개 루프 요약만 유지
            if len(state['recent_loops_summary']) > 5:
                state['recent_loops_summary'] = state['recent_loops_summary'][-5:]
        
        # 새 루프 초기화
        state['current_loop_id'] = str(uuid.uuid4())
        state['loop_start_time'] = datetime.now().isoformat()
        state['current_loop_conversations'] = []
        
        return state
    
    @staticmethod
    def complete_current_loop(state: TutorState, summary: str = None) -> TutorState:
        """현재 루프 완료 처리"""
        if state['current_loop_conversations']:
            # 자동 요약 생성 또는 제공된 요약 사용
            if not summary:
                summary_dict = StateManager._create_loop_summary(state)
                summary = f"루프 {summary_dict['loop_id'][:8]}: {summary_dict['main_topics']}"
            
            # 완료된 루프를 요약에 추가
            completed_summary = StateManager._create_loop_summary(state)
            completed_summary['summary'] = summary
            completed_summary['status'] = 'completed'
            
            state['recent_loops_summary'].append(completed_summary)
            
            # 최대 5개 루프 요약만 유지
            if len(state['recent_loops_summary']) > 5:
                state['recent_loops_summary'] = state['recent_loops_summary'][-5:]
            
            # 현재 루프 초기화
            state['current_loop_conversations'] = []
        
        return state
    
    @staticmethod
    def add_conversation(state: TutorState, agent_name: str, 
                        user_message: str = "", system_response: str = "",
                        ui_elements: Optional[Dict[str, Any]] = None) -> TutorState:
        """대화 내용을 현재 루프에 추가"""
        conversation = {
            'agent_name': agent_name,
            'user_message': user_message,
            'system_response': system_response,
            'ui_elements': ui_elements,
            'timestamp': datetime.now().isoformat(),
            'sequence_order': len(state['current_loop_conversations']) + 1
        }
        
        state['current_loop_conversations'].append(conversation)
        return state
    
    @staticmethod
    def _create_loop_summary(state: TutorState) -> Dict[str, str]:
        """현재 루프의 요약 생성"""
        conversations = state['current_loop_conversations']
        
        # 기본 요약 정보
        summary = {
            'loop_id': state['current_loop_id'],
            'chapter': str(state['current_chapter']),
            'start_time': state['loop_start_time'],
            'end_time': datetime.now().isoformat(),
            'conversation_count': str(len(conversations))
        }
        
        # 주요 활동 요약
        agents_used = set()
        user_questions = []
        
        for conv in conversations:
            agents_used.add(conv['agent_name'])
            if conv['user_message']:
                user_questions.append(conv['user_message'][:100])  # 처음 100자만
        
        summary['agents_used'] = ', '.join(agents_used)
        summary['main_topics'] = ' | '.join(user_questions[:3])  # 최대 3개 질문
        
        return summary
    
    @staticmethod
    def get_context_for_agent(state: TutorState, agent_name: str) -> str:
        """특정 에이전트를 위한 컨텍스트 생성"""
        context_parts = []
        
        # 사용자 기본 정보
        context_parts.append(f"사용자 유형: {state['user_type']}")
        context_parts.append(f"사용자 레벨: {state['user_level']}")
        context_parts.append(f"현재 챕터: {state['current_chapter']}")
        context_parts.append(f"현재 단계: {state['current_stage']}")
        
        # 최근 루프 요약
        if state['recent_loops_summary']:
            context_parts.append("\n=== 최근 학습 요약 ===")
            for summary in state['recent_loops_summary'][-3:]:  # 최근 3개만
                context_parts.append(
                    f"루프 {summary['loop_id'][:8]}: {summary['main_topics']}"
                )
        
        # 현재 루프 대화
        if state['current_loop_conversations']:
            context_parts.append("\n=== 현재 루프 대화 ===")
            for conv in state['current_loop_conversations'][-5:]:  # 최근 5개만
                if conv['user_message']:
                    context_parts.append(f"사용자: {conv['user_message']}")
                if conv['system_response']:
                    context_parts.append(f"{conv['agent_name']}: {conv['system_response'][:200]}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def update_ui_mode(state: TutorState, mode: str) -> TutorState:
        """UI 모드 업데이트"""
        if mode in ['chat', 'quiz', 'restricted', 'error']:
            state['ui_mode'] = mode
        return state
    
    @staticmethod
    def set_system_response(state: TutorState, message: str, 
                          ui_elements: Optional[Dict[str, Any]] = None) -> TutorState:
        """시스템 응답 설정"""
        state['system_message'] = message
        state['ui_elements'] = ui_elements
        return state
    
    @staticmethod
    def update_ui_state_for_agent(state: TutorState, agent_name: str, 
                                context: Optional[Dict] = None) -> TutorState:
        """에이전트별 UI 상태 업데이트"""
        try:
            from services.agent_ui_service import get_agent_ui_generator
            from services.ui_mode_service import UIStateSerializer
            
            ui_generator = get_agent_ui_generator()
            ui_state = ui_generator.generate_ui_for_agent(agent_name, state, context)
            
            # UI 상태를 직렬화하여 state에 저장
            serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
            state['ui_elements'] = serialized_ui
            state['ui_mode'] = ui_state.mode.value
            
        except Exception as e:
            # UI 생성 실패 시 기본 UI 설정
            state['ui_mode'] = 'error'
            state['ui_elements'] = {
                "mode": "error",
                "elements": [],
                "title": "UI 오류",
                "description": f"UI 생성 중 오류가 발생했습니다: {str(e)}"
            }
        
        return state
    
    @staticmethod
    def handle_ui_transition(state: TutorState, event: str, agent_name: str,
                           context: Optional[Dict] = None) -> TutorState:
        """UI 전환 이벤트 처리"""
        try:
            from services.agent_ui_service import get_ui_transition_manager
            from services.ui_mode_service import UIStateSerializer
            
            transition_manager = get_ui_transition_manager()
            ui_state = transition_manager.handle_transition(event, agent_name, state, context)
            
            # UI 상태를 직렬화하여 state에 저장
            serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
            state['ui_elements'] = serialized_ui
            state['ui_mode'] = ui_state.mode.value
            
        except Exception as e:
            # 전환 실패 시 오류 상태로 설정
            state['ui_mode'] = 'error'
            state['ui_elements'] = {
                "mode": "error",
                "elements": [],
                "title": "전환 오류",
                "description": f"UI 전환 중 오류가 발생했습니다: {str(e)}"
            }
        
        return state