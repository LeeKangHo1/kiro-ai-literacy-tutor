# tests/integration/test_ui_integration.py
# UI 모드 관리 시스템 통합 테스트

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import json
from datetime import datetime

from services.ui_mode_service import (
    UIModeManager, UIMode, UIState, InteractionType, UIElement,
    UIStateSerializer, get_ui_mode_manager
)
from services.agent_ui_service import (
    AgentUIGenerator, UIStateTransitionManager,
    get_agent_ui_generator, get_ui_transition_manager
)
from services.websocket_service import WebSocketManager, WebSocketMessage
from workflow.state_management import TutorState, StateManager
from agents.educator.content_generator import ContentGenerator
from agents.quiz.question_generator import QuestionGenerator


class TestUIWorkflowIntegration(unittest.TestCase):
    """UI 모드 관리와 워크플로우 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.ui_manager = UIModeManager()
        self.ui_generator = AgentUIGenerator(self.ui_manager)
        self.transition_manager = UIStateTransitionManager(self.ui_generator)
        
        # 테스트용 상태 생성
        self.test_state = StateManager.create_initial_state(
            "test_user_123", "beginner", "low"
        )
        self.test_state['user_message'] = "AI에 대해 설명해주세요"
        self.test_state['current_chapter'] = 1
    
    def test_theory_educator_ui_workflow(self):
        """TheoryEducator UI 워크플로우 테스트"""
        content_generator = ContentGenerator()
        
        # 1. 사용자 입력 수신 -> 로딩 상태
        loading_ui = self.transition_manager.handle_transition(
            "user_input_received", "theory_educator", self.test_state
        )
        self.assertEqual(loading_ui.mode, UIMode.LOADING)
        
        # 2. 이론 콘텐츠 생성
        content = content_generator.generate_theory_content(
            1, "beginner", "low", "AI에 대해 설명해주세요"
        )
        self.assertIsNotNone(content)
        self.assertEqual(content['chapter'], 1)
        
        # 3. 에이전트 응답 준비 완료 -> 채팅 모드
        context = {
            'title': content['title'],
            'description': '개념 설명이 완료되었습니다.',
            'show_progress': True,
            'content_type': 'theory'
        }
        
        response_ui = self.transition_manager.handle_transition(
            "agent_response_ready", "theory_educator", self.test_state, context
        )
        self.assertEqual(response_ui.mode, UIMode.CHAT)
        # context에서 제공된 title이 사용됨
        self.assertEqual(response_ui.title, "AI는 무엇인가?")
    
    def test_quiz_generator_ui_workflow(self):
        """QuizGenerator UI 워크플로우 테스트"""
        quiz_generator = QuestionGenerator()
        
        # 1. 사용자 퀴즈 요청 -> 로딩 상태
        loading_ui = self.transition_manager.handle_transition(
            "user_input_received", "quiz_generator", self.test_state
        )
        self.assertEqual(loading_ui.mode, UIMode.LOADING)
        
        # 2. 객관식 문제 생성
        quiz_data = quiz_generator.generate_multiple_choice_question(
            1, "low", "beginner"
        )
        self.assertIsNotNone(quiz_data)
        self.assertEqual(quiz_data['question_type'], 'multiple_choice')
        
        # 3. 퀴즈 UI 생성
        context = {
            'quiz_type': 'multiple_choice',
            'question': quiz_data['question_text'],
            'options': quiz_data['options'],
            'hint_available': True,
            'quiz_info': quiz_data
        }
        
        quiz_ui = self.transition_manager.handle_transition(
            "agent_response_ready", "quiz_generator", self.test_state, context
        )
        self.assertEqual(quiz_ui.mode, UIMode.QUIZ)
        self.assertEqual(quiz_ui.interaction_type, InteractionType.MULTIPLE_CHOICE)
        
        # 4. 퀴즈 제출 -> 로딩 상태
        submit_ui = self.transition_manager.handle_transition(
            "quiz_submitted", "quiz_generator", self.test_state
        )
        self.assertEqual(submit_ui.mode, UIMode.LOADING)
    
    def test_router_ui_workflow(self):
        """Router UI 워크플로우 테스트"""
        # PostTheoryRouter UI 생성
        router_ui = self.ui_generator.generate_ui_for_agent(
            "post_theory_router", self.test_state
        )
        
        self.assertEqual(router_ui.mode, UIMode.RESTRICTED)
        self.assertEqual(router_ui.interaction_type, InteractionType.BUTTON_CLICK)
        
        # 버튼 요소들 확인
        button_elements = [
            elem for elem in router_ui.elements 
            if elem.element_type == "button"
        ]
        self.assertTrue(len(button_elements) >= 2)  # 최소 2개 버튼 (질문하기, 문제풀기)
    
    def test_error_handling_workflow(self):
        """오류 처리 워크플로우 테스트"""
        error_context = {
            'error_message': '테스트 오류가 발생했습니다.'
        }
        
        error_ui = self.transition_manager.handle_transition(
            "error_occurred", "system", self.test_state, error_context
        )
        
        self.assertEqual(error_ui.mode, UIMode.ERROR)
        self.assertEqual(error_ui.title, "오류 발생")
        
        # 재시도 버튼 확인
        retry_button = next(
            (elem for elem in error_ui.elements if elem.element_id == "retry_action"),
            None
        )
        self.assertIsNotNone(retry_button)
        self.assertEqual(retry_button.label, "다시 시도")


class TestUIStateSerialization(unittest.TestCase):
    """UI 상태 직렬화 통합 테스트"""
    
    def test_full_serialization_cycle(self):
        """완전한 직렬화/역직렬화 사이클 테스트"""
        # 복잡한 UI 상태 생성
        elements = [
            UIElement(
                element_type="textarea",
                element_id="user_input",
                label="메시지 입력",
                placeholder="질문을 입력하세요...",
                required=True,
                validation={"max_length": 1000}
            ),
            UIElement(
                element_type="button",
                element_id="submit_btn",
                label="전송",
                style={"variant": "primary"},
                events=["click"]
            ),
            UIElement(
                element_type="progress",
                element_id="progress_bar",
                label="진행률",
                value=75
            )
        ]
        
        original_ui_state = UIState(
            mode=UIMode.CHAT,
            interaction_type=InteractionType.FREE_TEXT,
            elements=elements,
            layout="chat_layout",
            title="AI 학습 튜터",
            description="자유롭게 질문해보세요",
            progress={"current": 3, "total": 4},
            metadata={"session_id": "test_session"}
        )
        
        # 직렬화
        serialized = UIStateSerializer.serialize_ui_state(original_ui_state)
        
        # 직렬화된 데이터 검증
        self.assertEqual(serialized['mode'], 'chat')
        self.assertEqual(serialized['interaction_type'], 'free_text')
        self.assertEqual(len(serialized['elements']), 3)
        self.assertEqual(serialized['title'], 'AI 학습 튜터')
        
        # 역직렬화
        deserialized_ui_state = UIStateSerializer.deserialize_ui_state(serialized)
        
        # 역직렬화된 데이터 검증
        self.assertEqual(deserialized_ui_state.mode, UIMode.CHAT)
        self.assertEqual(deserialized_ui_state.interaction_type, InteractionType.FREE_TEXT)
        self.assertEqual(len(deserialized_ui_state.elements), 3)
        self.assertEqual(deserialized_ui_state.title, 'AI 학습 튜터')
        self.assertEqual(deserialized_ui_state.elements[0].element_id, 'user_input')
        self.assertEqual(deserialized_ui_state.elements[1].label, '전송')
        self.assertEqual(deserialized_ui_state.elements[2].value, 75)


class TestWebSocketIntegration(unittest.TestCase):
    """WebSocket 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.websocket_manager = WebSocketManager()
    
    def test_websocket_message_creation(self):
        """WebSocket 메시지 생성 테스트"""
        message_data = {
            'ui_state': {'mode': 'chat', 'elements': []},
            'agent_name': 'theory_educator',
            'update_type': 'full_update'
        }
        
        message = WebSocketMessage(
            message_id="test_msg_123",
            message_type="ui_update",
            user_id="test_user",
            data=message_data,
            timestamp=datetime.now().isoformat()
        )
        
        # JSON 직렬화/역직렬화 테스트
        json_str = message.to_json()
        self.assertIsInstance(json_str, str)
        
        parsed_message = WebSocketMessage.from_json(json_str)
        self.assertEqual(parsed_message.message_type, "ui_update")
        self.assertEqual(parsed_message.user_id, "test_user")
        self.assertEqual(parsed_message.data['agent_name'], 'theory_educator')
    
    def test_message_handler_registration(self):
        """메시지 핸들러 등록 테스트"""
        # 기본 핸들러들이 등록되어 있는지 확인
        expected_handlers = ['ping', 'subscribe', 'unsubscribe', 'ui_request', 'state_sync']
        
        for handler_type in expected_handlers:
            self.assertIn(handler_type, self.websocket_manager.message_handlers)
            self.assertIsNotNone(self.websocket_manager.message_handlers[handler_type])


class TestStateManagerUIIntegration(unittest.TestCase):
    """StateManager와 UI 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_state = StateManager.create_initial_state(
            "integration_test_user", "business", "medium"
        )
    
    @patch('services.agent_ui_service.get_agent_ui_generator')
    @patch('services.ui_mode_service.UIStateSerializer.serialize_ui_state')
    def test_state_ui_update_integration(self, mock_serialize, mock_get_generator):
        """상태와 UI 업데이트 통합 테스트"""
        # Mock 설정
        mock_ui_state = Mock()
        mock_ui_state.mode.value = 'quiz'
        mock_generator = Mock()
        mock_generator.generate_ui_for_agent.return_value = mock_ui_state
        mock_get_generator.return_value = mock_generator
        
        mock_serialize.return_value = {
            'mode': 'quiz',
            'elements': [{'element_id': 'test_element'}],
            'title': '문제 풀이'
        }
        
        # UI 상태 업데이트
        updated_state = StateManager.update_ui_state_for_agent(
            self.test_state, "quiz_generator", {'quiz_type': 'multiple_choice'}
        )
        
        # 검증
        self.assertEqual(updated_state['ui_mode'], 'quiz')
        self.assertIsNotNone(updated_state['ui_elements'])
        self.assertEqual(updated_state['ui_elements']['title'], '문제 풀이')
        
        # Mock 호출 검증
        mock_generator.generate_ui_for_agent.assert_called_once_with(
            "quiz_generator", self.test_state, {'quiz_type': 'multiple_choice'}
        )
        mock_serialize.assert_called_once()
    
    @patch('services.agent_ui_service.get_ui_transition_manager')
    @patch('services.ui_mode_service.UIStateSerializer.serialize_ui_state')
    def test_ui_transition_integration(self, mock_serialize, mock_get_manager):
        """UI 전환 통합 테스트"""
        # Mock 설정
        mock_ui_state = Mock()
        mock_ui_state.mode.value = 'loading'
        mock_manager = Mock()
        mock_manager.handle_transition.return_value = mock_ui_state
        mock_get_manager.return_value = mock_manager
        
        mock_serialize.return_value = {
            'mode': 'loading',
            'elements': [],
            'title': '처리 중'
        }
        
        # UI 전환 처리
        updated_state = StateManager.handle_ui_transition(
            self.test_state, "user_input_received", "theory_educator",
            {'loading_message': '콘텐츠 생성 중...'}
        )
        
        # 검증
        self.assertEqual(updated_state['ui_mode'], 'loading')
        self.assertEqual(updated_state['ui_elements']['title'], '처리 중')
        
        # Mock 호출 검증
        mock_manager.handle_transition.assert_called_once_with(
            "user_input_received", "theory_educator", self.test_state,
            {'loading_message': '콘텐츠 생성 중...'}
        )


class TestEndToEndUIFlow(unittest.TestCase):
    """End-to-End UI 플로우 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.initial_state = StateManager.create_initial_state(
            "e2e_test_user", "beginner", "low"
        )
        self.ui_generator = get_agent_ui_generator()
        self.transition_manager = get_ui_transition_manager()
    
    def test_complete_learning_flow(self):
        """완전한 학습 플로우 테스트"""
        current_state = self.initial_state.copy()
        current_state['user_message'] = "AI가 무엇인지 설명해주세요"
        
        # 1. 사용자 입력 -> 로딩 상태
        current_state = StateManager.handle_ui_transition(
            current_state, "user_input_received", "theory_educator"
        )
        self.assertEqual(current_state['ui_mode'], 'loading')
        
        # 2. 이론 설명 완료 -> 채팅 모드
        current_state = StateManager.update_ui_state_for_agent(
            current_state, "theory_educator",
            {'title': 'AI는 무엇인가?', 'show_progress': True}
        )
        self.assertEqual(current_state['ui_mode'], 'chat')
        
        # 3. 사용자가 문제 요청 -> 퀴즈 모드
        current_state['user_message'] = "문제 주세요"
        current_state = StateManager.handle_ui_transition(
            current_state, "user_input_received", "quiz_generator"
        )
        self.assertEqual(current_state['ui_mode'], 'loading')
        
        # 4. 퀴즈 생성 완료 -> 퀴즈 UI
        current_state = StateManager.update_ui_state_for_agent(
            current_state, "quiz_generator",
            {
                'quiz_type': 'multiple_choice',
                'question': 'AI의 정의는?',
                'options': ['옵션1', '옵션2', '옵션3', '옵션4']
            }
        )
        self.assertEqual(current_state['ui_mode'], 'quiz')
        
        # 5. 퀴즈 제출 -> 로딩 상태
        current_state = StateManager.handle_ui_transition(
            current_state, "quiz_submitted", "evaluation_feedback"
        )
        self.assertEqual(current_state['ui_mode'], 'loading')
        
        # 6. 피드백 완료 -> 제한된 UI (다음 행동 선택)
        current_state = StateManager.update_ui_state_for_agent(
            current_state, "post_feedback_router",
            {
                'is_correct': True,
                'score': 100,
                'available_actions': ['continue', 'ask_question']
            }
        )
        self.assertEqual(current_state['ui_mode'], 'restricted')
        
        # 각 단계에서 UI 요소가 적절히 생성되었는지 확인
        self.assertIsNotNone(current_state.get('ui_elements'))
        
        print("✅ End-to-End UI 플로우 테스트 완료")
        print(f"최종 UI 모드: {current_state['ui_mode']}")
        print(f"현재 단계: {current_state['current_stage']}")


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)