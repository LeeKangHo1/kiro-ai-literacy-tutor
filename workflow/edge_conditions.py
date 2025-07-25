# workflow/edge_conditions.py
# 조건부 라우팅 엣지 정의 모듈

from typing import Literal
from .state_management import TutorState


class EdgeConditions:
    """LangGraph 워크플로우의 조건부 엣지를 정의하는 클래스"""
    
    @staticmethod
    def supervisor_routing_condition(state: TutorState) -> Literal[
        "theory_educator", "end", "qna_resolver"
    ]:
        """LearningSupervisor에서의 라우팅 조건"""
        
        # 오류 상태인 경우 종료
        if state.get('ui_mode') == 'error':
            return "end"
        
        # 현재 단계에 따른 라우팅
        current_stage = state.get('current_stage', '')
        
        if current_stage == 'theory':
            return "theory_educator"
        elif current_stage == 'completed':
            return "end"
        elif current_stage == 'question':
            return "qna_resolver"
        else:
            # 기본적으로 이론 설명으로
            return "theory_educator"
    
    @staticmethod
    def post_theory_routing_condition(state: TutorState) -> Literal[
        "qna_resolver", "quiz_generator"
    ]:
        """PostTheoryRouter에서의 라우팅 조건"""
        
        # 라우터가 설정한 다음 단계 확인
        next_stage = state.get('current_stage', '')
        
        if next_stage == 'question':
            return "qna_resolver"
        elif next_stage == 'quiz':
            return "quiz_generator"
        else:
            # 기본적으로 퀴즈로 (사용자가 명확한 의도를 표현하지 않은 경우)
            return "quiz_generator"
    
    @staticmethod
    def post_feedback_routing_condition(state: TutorState) -> Literal[
        "qna_resolver", "learning_supervisor"
    ]:
        """PostFeedbackRouter에서의 라우팅 조건"""
        
        # 라우터가 설정한 다음 단계 확인
        next_stage = state.get('current_stage', '')
        
        if next_stage == 'question':
            return "qna_resolver"
        elif next_stage == 'continue' or next_stage == 'completed':
            return "learning_supervisor"
        else:
            # 기본적으로 supervisor로 (루프 완료 처리)
            return "learning_supervisor"
    
    @staticmethod
    def qna_routing_condition(state: TutorState) -> Literal[
        "post_theory_router", "post_feedback_router", "learning_supervisor"
    ]:
        """QnAResolver에서의 라우팅 조건"""
        
        # 질문의 출처에 따라 다른 라우터로 복귀
        qa_source = state.get('qa_source_router', '')
        
        if qa_source == 'post_theory':
            return "post_theory_router"
        elif qa_source == 'post_feedback':
            return "post_feedback_router"
        else:
            # 직접 호출된 경우 supervisor로
            return "learning_supervisor"
    
    @staticmethod
    def should_continue_condition(state: TutorState) -> bool:
        """워크플로우 계속 진행 여부 판단"""
        
        # 오류 상태인 경우 중단
        if state.get('ui_mode') == 'error':
            return False
        
        # 완료 상태인 경우 중단
        if state.get('current_stage') == 'completed':
            return False
        
        # 최대 대화 수 제한 (무한 루프 방지)
        max_conversations = 50
        current_conversations = len(state.get('current_loop_conversations', []))
        
        if current_conversations >= max_conversations:
            return False
        
        return True
    
    @staticmethod
    def is_user_input_required(state: TutorState) -> bool:
        """사용자 입력이 필요한지 판단"""
        
        # 퀴즈 모드인 경우 사용자 입력 필요
        if state.get('ui_mode') == 'quiz':
            return True
        
        # 특정 UI 요소가 있는 경우 사용자 입력 필요
        ui_elements = state.get('ui_elements')
        if ui_elements and ui_elements.get('requires_input', False):
            return True
        
        # 질문 답변 후에는 사용자 입력 필요
        if state.get('current_stage') == 'question_answered':
            return True
        
        return False


class EdgeRegistry:
    """엣지 조건 등록 및 관리를 위한 레지스트리 클래스"""
    
    # 사용 가능한 모든 엣지 조건 정의
    CONDITIONS = {
        'supervisor_routing': EdgeConditions.supervisor_routing_condition,
        'post_theory_routing': EdgeConditions.post_theory_routing_condition,
        'post_feedback_routing': EdgeConditions.post_feedback_routing_condition,
        'qna_routing': EdgeConditions.qna_routing_condition,
        'should_continue': EdgeConditions.should_continue_condition,
        'is_user_input_required': EdgeConditions.is_user_input_required
    }
    
    @classmethod
    def get_condition(cls, condition_name: str):
        """조건 이름으로 조건 함수 반환"""
        return cls.CONDITIONS.get(condition_name)
    
    @classmethod
    def get_all_conditions(cls):
        """모든 조건 반환"""
        return cls.CONDITIONS.copy()
    
    @classmethod
    def validate_condition_name(cls, condition_name: str) -> bool:
        """조건 이름 유효성 검증"""
        return condition_name in cls.CONDITIONS


class RoutingHelper:
    """라우팅 관련 유틸리티 함수들"""
    
    @staticmethod
    def set_next_stage(state: TutorState, stage: str) -> TutorState:
        """다음 단계 설정"""
        state['current_stage'] = stage
        return state
    
    @staticmethod
    def set_qa_source(state: TutorState, source: str) -> TutorState:
        """질문 출처 설정"""
        state['qa_source_router'] = source
        return state
    
    @staticmethod
    def analyze_user_intent(user_message: str) -> str:
        """사용자 의도 분석 (간단한 키워드 기반)"""
        message_lower = user_message.lower()
        
        # 질문 패턴
        question_keywords = ['?', '뭐', '무엇', '어떻게', '왜', '언제', '어디서', '질문', '궁금']
        if any(keyword in message_lower for keyword in question_keywords):
            return 'question'
        
        # 문제 요청 패턴
        quiz_keywords = ['문제', '퀴즈', '테스트', '연습', '실습', '풀어', '출제']
        if any(keyword in message_lower for keyword in quiz_keywords):
            return 'quiz'
        
        # 진행 요청 패턴
        continue_keywords = ['다음', '계속', '진행', '넘어가', '완료', '끝']
        if any(keyword in message_lower for keyword in continue_keywords):
            return 'continue'
        
        # 기본값은 질문으로 처리
        return 'question'
    
    @staticmethod
    def should_end_loop(state: TutorState) -> bool:
        """현재 루프를 종료해야 하는지 판단"""
        
        # 명시적 완료 요청
        if state.get('current_stage') == 'completed':
            return True
        
        # 대화 수가 너무 많은 경우
        conversations = state.get('current_loop_conversations', [])
        if len(conversations) > 20:  # 한 루프당 최대 20개 대화
            return True
        
        # 오류 상태인 경우
        if state.get('ui_mode') == 'error':
            return True
        
        return False