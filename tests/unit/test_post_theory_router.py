# tests/unit/test_post_theory_router.py
# PostTheoryRouter 단위 테스트

import pytest
from routers.post_theory_router import PostTheoryRouter
from workflow.state_management import TutorState, StateManager


class TestPostTheoryRouter:
    """PostTheoryRouter 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.router = PostTheoryRouter()
        self.base_state = StateManager.create_initial_state(
            user_id="test_user",
            user_type="beginner",
            user_level="low"
        )
    
    def test_analyze_user_intent_question_patterns(self):
        """질문 패턴 인식 테스트"""
        question_messages = [
            "이게 뭐예요?",
            "어떻게 작동하나요?",
            "왜 그런 건가요?",
            "궁금한 게 있어요",
            "이해가 안 돼요",
            "설명해 주세요",
            "예시를 보여주세요",
            "차이점이 뭔가요?"
        ]
        
        for message in question_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "question", f"'{message}'는 질문으로 인식되어야 합니다"
    
    def test_analyze_user_intent_quiz_patterns(self):
        """문제 요청 패턴 인식 테스트"""
        quiz_messages = [
            "문제 주세요",
            "퀴즈를 풀어보고 싶어요",
            "테스트해 보겠습니다",
            "연습해 보고 싶어요",
            "실습을 해보죠",
            "확인해 보겠습니다",
            "다음으로 넘어가죠",
            "계속 진행해 주세요",
            "이해했습니다"
        ]
        
        for message in quiz_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "quiz", f"'{message}'는 퀴즈 요청으로 인식되어야 합니다"
    
    def test_analyze_user_intent_proceed_patterns(self):
        """진행 요청 패턴 인식 테스트 (퀴즈로 가중치)"""
        proceed_messages = [
            "좋아요",
            "네, 알겠습니다",
            "예",
            "계속해 주세요",
            "다음 단계로 가죠",
            "문제 주세요"
        ]
        
        for message in proceed_messages:
            intent = self.router._analyze_user_intent(message)
            assert intent == "quiz", f"'{message}'는 퀴즈 진행으로 인식되어야 합니다"
    
    def test_route_to_qna(self):
        """QnAResolver로 라우팅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "이게 뭐예요?"
        
        result_state = self.router._route_to_qna(state)
        
        assert result_state['current_stage'] == 'qna'
        assert result_state['qa_source_router'] == 'post_theory'
        assert result_state['ui_mode'] == 'chat'
        assert len(result_state['current_loop_conversations']) > 0
        assert "답변을 준비하고 있습니다" in result_state['system_message']
    
    def test_route_to_quiz(self):
        """QuizGenerator로 라우팅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "문제 주세요"
        
        result_state = self.router._route_to_quiz(state)
        
        assert result_state['current_stage'] == 'quiz'
        assert result_state['ui_mode'] == 'quiz'
        assert len(result_state['current_loop_conversations']) > 0
        assert "문제를 준비하고 있습니다" in result_state['system_message']
    
    def test_request_clarification(self):
        """명확화 요청 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "음..."
        
        result_state = self.router._request_clarification(state)
        
        assert result_state['ui_mode'] == 'chat'
        assert "무엇을 도와드릴까요?" in result_state['system_message']
        assert result_state['ui_elements']['type'] == 'clarification'
        assert len(result_state['ui_elements']['options']) == 3
    
    def test_execute_with_question(self):
        """질문 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "AI가 뭔가요?"
        
        result_state = self.router.execute(state)
        
        assert result_state['current_stage'] == 'qna'
        assert result_state['qa_source_router'] == 'post_theory'
        assert result_state['ui_mode'] == 'chat'
    
    def test_execute_with_quiz_request(self):
        """문제 요청 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "문제를 풀어보고 싶어요"
        
        result_state = self.router.execute(state)
        
        assert result_state['current_stage'] == 'quiz'
        assert result_state['ui_mode'] == 'quiz'
    
    def test_execute_with_empty_message(self):
        """빈 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = ""
        
        result_state = self.router.execute(state)
        
        # 빈 메시지는 기본적으로 퀴즈로 라우팅
        assert result_state['current_stage'] == 'quiz'
        assert result_state['ui_mode'] == 'quiz'
    
    def test_execute_with_unclear_message(self):
        """애매한 메시지로 execute 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "음... 그냥..."
        
        result_state = self.router.execute(state)
        
        # 애매한 메시지는 명확화 요청
        assert result_state['ui_mode'] == 'chat'
        assert "무엇을 도와드릴까요?" in result_state['system_message']
    
    def test_get_routing_decision(self):
        """라우팅 결정 정보 반환 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "AI가 뭔가요?"
        
        # execute 실행 후 라우팅 정보 확인
        self.router.execute(state)
        decision = self.router.get_routing_decision(state)
        
        assert decision['router'] == 'PostTheoryRouter'
        assert decision['user_message'] == "AI가 뭔가요?"
        assert decision['detected_intent'] == 'question'
        assert decision['next_stage'] == 'qna'
    
    def test_conversation_logging(self):
        """대화 기록 로깅 테스트"""
        state = self.base_state.copy()
        state['user_message'] = "문제 주세요"
        
        initial_conv_count = len(state['current_loop_conversations'])
        result_state = self.router.execute(state)
        
        # 대화가 기록되었는지 확인
        assert len(result_state['current_loop_conversations']) == initial_conv_count + 1
        
        # 기록된 대화 내용 확인
        last_conversation = result_state['current_loop_conversations'][-1]
        assert last_conversation['agent_name'] == 'PostTheoryRouter'
        assert last_conversation['user_message'] == "문제 주세요"
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
        state['user_message'] = "AI가 뭔가요?"
        result_state = self.router.execute(state)
        
        assert result_state['ui_elements']['type'] == 'loading'
        assert '답변 준비 중' in result_state['ui_elements']['message']


if __name__ == "__main__":
    pytest.main([__file__])