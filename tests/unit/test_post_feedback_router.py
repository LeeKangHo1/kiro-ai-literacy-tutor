# tests/unit/test_post_feedback_router.py
# PostFeedbackRouter 단위 테스트

import pytest
from routers.post_feedback_router import PostFeedbackRouter
from workflow.state_management import TutorState, StateManager


class TestPostFeedbackRouter:
    """PostFeedbackRouter 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.router = PostFeedbackRouter()
        self.base_state = StateManager.create_initial_state(
            user_id="test_user",
            user_type="beginner",
            user_level="low"
        )
        # 피드백 후 상황을 시뮬레이션
        self.base_state['current_stage'] = 'feedback'
    
    def test_analyze_user_intent_question_patterns(self):
        """추가 질문 패턴 인식 테스트"""
        question_messages = [
            "이게 왜 틀렸나요?",
            "어떻게 해야 맞나요?",
            "궁금한 게 있어요",
            "이해가 안 돼요",
            "설명해 주세요",
            "예시를 더 보여주세요",
            "차이점이 뭔가요?",
            "틀렸다고 하는데 왜 그런가요?",
            "잘못된 부분이 어디인가요?"
        ]
        
        for message in question_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "question", f"'{message}'는 질문으로 인식되어야 합니다"
    
    def test_analyze_user_intent_proceed_patterns(self):
        """진행 요청 패턴 인식 테스트"""
        proceed_messages = [
            "다음으로 넘어가죠",
            "계속 진행해 주세요",
            "좋아요",
            "네, 알겠습니다",
            "이해했습니다",
            "감사합니다",
            "됐어요",
            "충분해요",
            "새로운 문제 주세요",
            "다른 문제도 풀어보고 싶어요"
        ]
        
        for message in proceed_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "proceed", f"'{message}'는 진행 요청으로 인식되어야 합니다"
    
    def test_analyze_user_intent_retry_patterns(self):
        """재시도 패턴 인식 테스트"""
        retry_messages = [
            "다시 해보고 싶어요",
            "재시도하겠습니다",
            "한번 더 해보죠",
            "또 해보겠습니다",
            "못 했어요",
            "실패했네요",
            "힌트 주세요",
            "도움이 필요해요"
        ]
        
        for message in retry_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "retry", f"'{message}'는 재시도 요청으로 인식되어야 합니다"
    
    def test_route_to_qna(self):
        """QnAResolver로 라우팅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "이게 왜 틀렸나요?"
        
        result_state = self.router._route_to_qna(state)
        
        assert result_state['current_stage'] == 'qna'
        assert result_state['qa_source_router'] == 'post_feedback'
        assert result_state['ui_mode'] == 'chat'
        assert len(result_state['current_loop_conversations']) > 0
        assert "답변을 준비하고 있습니다" in result_state['system_message']
    
    def test_route_to_supervisor(self):
        """LearningSupervisor로 라우팅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "다음으로 넘어가죠"
        
        result_state = self.router._route_to_supervisor(state)
        
        assert result_state['current_stage'] == 'supervision'
        assert result_state['ui_mode'] == 'chat'
        assert len(result_state['current_loop_conversations']) > 0
        assert "다음 단계를 준비하고 있습니다" in result_state['system_message']
    
    def test_handle_retry_request_from_quiz(self):
        """퀴즈 단계에서 재시도 요청 처리 테스트"""
        state = self.base_state.copy()
        state['current_stage'] = 'quiz'
        state['user_message'] = "다시 해보고 싶어요"
        
        result_state = self.router._handle_retry_request(state)
        
        assert result_state['current_stage'] == 'quiz'
        assert result_state['ui_mode'] == 'quiz'
        assert "다시 문제를 준비해 드리겠습니다" in result_state['system_message']
        assert result_state['ui_elements']['type'] == 'loading'
    
    def test_handle_retry_request_from_other_stage(self):
        """기타 단계에서 재시도 요청 처리 테스트"""
        state = self.base_state.copy()
        state['current_stage'] = 'feedback'
        state['user_message'] = "도움이 필요해요"
        
        result_state = self.router._handle_retry_request(state)
        
        assert result_state['current_stage'] == 'qna'
        assert result_state['qa_source_router'] == 'post_feedback'
        assert result_state['ui_mode'] == 'chat'
        assert "구체적으로 질문해 주세요" in result_state['system_message']
    
    def test_request_clarification(self):
        """명확화 요청 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "음..."
        
        result_state = self.router._request_clarification(state)
        
        assert result_state['ui_mode'] == 'chat'
        assert "어떻게 도와드릴까요?" in result_state['system_message']
        assert result_state['ui_elements']['type'] == 'clarification'
        assert len(result_state['ui_elements']['options']) == 3
    
    def test_execute_with_question(self):
        """질문 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "왜 이게 틀렸나요?"
        
        result_state = self.router.execute(state)
        
        assert result_state['current_stage'] == 'qna'
        assert result_state['qa_source_router'] == 'post_feedback'
        assert result_state['ui_mode'] == 'chat'
    
    def test_execute_with_proceed_request(self):
        """진행 요청 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "이해했습니다. 다음으로 가죠"
        
        result_state = self.router.execute(state)
        
        assert result_state['current_stage'] == 'supervision'
        assert result_state['ui_mode'] == 'chat'
    
    def test_execute_with_retry_request(self):
        """재시도 요청 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['current_stage'] = 'quiz'
        state['user_message'] = "다시 해보고 싶어요"
        
        result_state = self.router.execute(state)
        
        assert result_state['current_stage'] == 'quiz'
        assert result_state['ui_mode'] == 'quiz'
    
    def test_execute_with_empty_message(self):
        """빈 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = ""
        
        result_state = self.router.execute(state)
        
        # 빈 메시지는 기본적으로 진행으로 라우팅
        assert result_state['current_stage'] == 'supervision'
        assert result_state['ui_mode'] == 'chat'
    
    def test_execute_with_unclear_message(self):
        """애매한 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "음... 그냥..."
        
        result_state = self.router.execute(state)
        
        # 애매한 메시지는 명확화 요청
        assert result_state['ui_mode'] == 'chat'
        assert "어떻게 도와드릴까요?" in result_state['system_message']
    
    def test_get_routing_decision(self):
        """라우팅 결정 정보 반환 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "왜 틀렸나요?"
        
        # execute 실행 후 라우팅 정보 확인
        self.router.execute(state)
        decision = self.router.get_routing_decision(state)
        
        assert decision['router'] == 'PostFeedbackRouter'
        assert decision['user_message'] == "왜 틀렸나요?"
        assert decision['detected_intent'] == 'question'
        assert decision['next_stage'] == 'qna'
    
    def test_get_next_stage_for_intent(self):
        """의도별 다음 단계 매핑 테스트"""
        assert self.router._get_next_stage_for_intent('question') == 'qna'
        assert self.router._get_next_stage_for_intent('proceed') == 'supervision'
        assert self.router._get_next_stage_for_intent('retry') == 'quiz'
        assert self.router._get_next_stage_for_intent('unclear') == 'clarification'
        assert self.router._get_next_stage_for_intent('unknown') == 'unknown'
    
    def test_conversation_logging(self):
        """대화 기록 로깅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "다음으로 가죠"
        
        initial_conv_count = len(state['current_loop_conversations'])
        result_state = self.router.execute(state)
        
        # 대화가 기록되었는지 확인
        assert len(result_state['current_loop_conversations']) == initial_conv_count + 1
        
        # 기록된 대화 내용 확인
        last_conversation = result_state['current_loop_conversations'][-1]
        assert last_conversation['agent_name'] == 'PostFeedbackRouter'
        assert last_conversation['user_message'] == "다음으로 가죠"
        assert 'system_response' in last_conversation
    
    def test_ui_elements_generation(self):
        """UI 요소 생성 테스트"""
        state = self.base_state.copy()
        
        # 명확화 요청 시 UI 요소 확인
        state['user_message'] = "음..."
        result_state = self.router.execute(state)
        
        assert result_state['ui_elements'] is not None
        assert result_state['ui_elements']['type'] == 'clarification'
        assert 'options' in result_state['ui_elements']
        
        # 로딩 UI 요소 확인 (QnA 라우팅)
        state['user_message'] = "왜 틀렸나요?"
        result_state = self.router.execute(state)
        
        assert result_state['ui_elements']['type'] == 'loading'
        assert '답변 준비 중' in result_state['ui_elements']['message']
    
    def test_qa_source_router_tracking(self):
        """QA 소스 라우터 추적 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "이해가 안 돼요"
        
        result_state = self.router.execute(state)
        
        # QnA로 라우팅될 때 소스 라우터가 올바르게 설정되는지 확인
        assert result_state['qa_source_router'] == 'post_feedback'
        assert result_state['current_stage'] == 'qna'


if __name__ == "__main__":
    pytest.main([__file__])