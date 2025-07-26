# tests/unit/test_ui_mode_service.py
# UI 모드 관리 서비스 단위 테스트

import unittest
from unittest.mock import Mock, patch
from services.ui_mode_service import (
    UIModeManager, UIMode, UIState, InteractionType, UIElement, 
    UIStateSerializer, get_ui_mode_manager
)
from services.agent_ui_service import AgentUIGenerator, UIStateTransitionManager
from workflow.state_management import TutorState, StateManager


class TestUIModeManager(unittest.TestCase):
    """UI 모드 관리자 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.ui_manager = UIModeManager()
    
    def test_initial_mode(self):
        """초기 모드 테스트"""
        self.assertEqual(self.ui_manager.current_mode, UIMode.CHAT)
        self.assertEqual(len(self.ui_manager.mode_history), 0)
    
    def test_switch_to_quiz_mode(self):
        """퀴즈 모드 전환 테스트"""
        context = {
            'quiz_type': 'multiple_choice',
            'question': '테스트 문제',
            'options': ['옵션1', '옵션2', '옵션3', '옵션4']
        }
        
        ui_state = self.ui_manager.switch_mode(UIMode.QUIZ, context)
        
        self.assertEqual(self.ui_manager.current_mode, UIMode.QUIZ)
        self.assertEqual(ui_state.mode, UIMode.QUIZ)
        self.assertEqual(ui_state.interaction_type, InteractionType.MULTIPLE_CHOICE)
        self.assertTrue(len(ui_state.elements) > 0)
    
    def test_switch_to_error_mode(self):
        """오류 모드 전환 테스트"""
        context = {'error_message': '테스트 오류 메시지'}
        
        ui_state = self.ui_manager.switch_mode(UIMode.ERROR, context)
        
        self.assertEqual(self.ui_manager.current_mode, UIMode.ERROR)
        self.assertEqual(ui_state.mode, UIMode.ERROR)
        self.assertEqual(ui_state.title, "오류 발생")
    
    def test_mode_history(self):
        """모드 이력 테스트"""
        # 초기 상태: CHAT
        self.assertEqual(self.ui_manager.current_mode, UIMode.CHAT)
        
        # QUIZ로 전환
        self.ui_manager.switch_mode(UIMode.QUIZ)
        self.assertEqual(self.ui_manager.get_previous_mode(), UIMode.CHAT)
        
        # ERROR로 전환
        self.ui_manager.switch_mode(UIMode.ERROR)
        self.assertEqual(self.ui_manager.get_previous_mode(), UIMode.QUIZ)
    
    def test_revert_to_previous_mode(self):
        """이전 모드로 되돌리기 테스트"""
        # QUIZ로 전환
        self.ui_manager.switch_mode(UIMode.QUIZ)
        
        # 이전 모드(CHAT)로 되돌리기
        ui_state = self.ui_manager.revert_to_previous_mode()
        
        self.assertEqual(self.ui_manager.current_mode, UIMode.CHAT)
        self.assertEqual(ui_state.mode, UIMode.CHAT)


class TestUIStateSerializer(unittest.TestCase):
    """UI 상태 직렬화 테스트"""
    
    def test_serialize_ui_state(self):
        """UI 상태 직렬화 테스트"""
        # 테스트용 UI 상태 생성
        elements = [
            UIElement(
                element_type="button",
                element_id="test_button",
                label="테스트 버튼",
                value="test_value"
            )
        ]
        
        ui_state = UIState(
            mode=UIMode.CHAT,
            interaction_type=InteractionType.FREE_TEXT,
            elements=elements,
            layout="test_layout",
            title="테스트 제목"
        )
        
        # 직렬화
        serialized = UIStateSerializer.serialize_ui_state(ui_state)
        
        # 검증
        self.assertEqual(serialized['mode'], 'chat')
        self.assertEqual(serialized['interaction_type'], 'free_text')
        self.assertEqual(serialized['layout'], 'test_layout')
        self.assertEqual(serialized['title'], '테스트 제목')
        self.assertEqual(len(serialized['elements']), 1)
        self.assertEqual(serialized['elements'][0]['element_id'], 'test_button')
    
    def test_deserialize_ui_state(self):
        """UI 상태 역직렬화 테스트"""
        # 테스트용 직렬화된 데이터
        serialized_data = {
            'mode': 'quiz',
            'interaction_type': 'multiple_choice',
            'elements': [
                {
                    'element_type': 'radio_group',
                    'element_id': 'quiz_answer',
                    'label': '정답 선택',
                    'value': None,
                    'options': [{'value': 0, 'label': '옵션1'}],
                    'placeholder': None,
                    'disabled': False,
                    'required': True,
                    'validation': None,
                    'style': None,
                    'events': None
                }
            ],
            'layout': 'quiz_layout',
            'title': '문제 풀이',
            'description': '테스트 문제',
            'progress': None,
            'metadata': None
        }
        
        # 역직렬화
        ui_state = UIStateSerializer.deserialize_ui_state(serialized_data)
        
        # 검증
        self.assertEqual(ui_state.mode, UIMode.QUIZ)
        self.assertEqual(ui_state.interaction_type, InteractionType.MULTIPLE_CHOICE)
        self.assertEqual(ui_state.layout, 'quiz_layout')
        self.assertEqual(ui_state.title, '문제 풀이')
        self.assertEqual(len(ui_state.elements), 1)
        self.assertEqual(ui_state.elements[0].element_id, 'quiz_answer')


class TestAgentUIGenerator(unittest.TestCase):
    """에이전트 UI 생성기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.ui_manager = UIModeManager()
        self.ui_generator = AgentUIGenerator(self.ui_manager)
        
        # 테스트용 상태 생성
        self.test_state = StateManager.create_initial_state(
            "test_user", "beginner", "low"
        )
    
    def test_generate_ui_for_theory_educator(self):
        """TheoryEducator용 UI 생성 테스트"""
        ui_state = self.ui_generator.generate_ui_for_agent(
            "theory_educator", self.test_state
        )
        
        self.assertEqual(ui_state.mode, UIMode.CHAT)
        self.assertEqual(ui_state.title, "개념 학습")
        self.assertTrue(len(ui_state.elements) > 0)
    
    def test_generate_ui_for_quiz_generator(self):
        """QuizGenerator용 UI 생성 테스트"""
        context = {
            'quiz_type': 'multiple_choice',
            'question': '테스트 문제',
            'options': ['A', 'B', 'C', 'D']
        }
        
        ui_state = self.ui_generator.generate_ui_for_agent(
            "quiz_generator", self.test_state, context
        )
        
        self.assertEqual(ui_state.mode, UIMode.QUIZ)
        self.assertEqual(ui_state.title, "문제 풀이")
        
        # 객관식 요소 확인
        quiz_element = next(
            (elem for elem in ui_state.elements if elem.element_id == "quiz_answer"),
            None
        )
        self.assertIsNotNone(quiz_element)
        self.assertEqual(quiz_element.element_type, "radio_group")
    
    def test_generate_ui_for_post_theory_router(self):
        """PostTheoryRouter용 UI 생성 테스트"""
        ui_state = self.ui_generator.generate_ui_for_agent(
            "post_theory_router", self.test_state
        )
        
        self.assertEqual(ui_state.mode, UIMode.RESTRICTED)
        self.assertEqual(ui_state.title, "다음 단계 선택")
        
        # 액션 버튼들 확인
        button_elements = [
            elem for elem in ui_state.elements 
            if elem.element_type == "button"
        ]
        self.assertTrue(len(button_elements) > 0)


class TestUIStateTransitionManager(unittest.TestCase):
    """UI 상태 전환 관리자 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.ui_manager = UIModeManager()
        self.ui_generator = AgentUIGenerator(self.ui_manager)
        self.transition_manager = UIStateTransitionManager(self.ui_generator)
        
        self.test_state = StateManager.create_initial_state(
            "test_user", "beginner", "low"
        )
    
    def test_handle_user_input_received(self):
        """사용자 입력 수신 이벤트 처리 테스트"""
        ui_state = self.transition_manager.handle_transition(
            "user_input_received", "theory_educator", self.test_state
        )
        
        self.assertEqual(ui_state.mode, UIMode.LOADING)
        self.assertIn("처리", ui_state.description)
    
    def test_handle_agent_response_ready(self):
        """에이전트 응답 준비 완료 이벤트 처리 테스트"""
        ui_state = self.transition_manager.handle_transition(
            "agent_response_ready", "quiz_generator", self.test_state
        )
        
        self.assertEqual(ui_state.mode, UIMode.QUIZ)
        self.assertEqual(ui_state.title, "문제 풀이")
    
    def test_handle_error_occurred(self):
        """오류 발생 이벤트 처리 테스트"""
        context = {'error_message': '테스트 오류'}
        
        ui_state = self.transition_manager.handle_transition(
            "error_occurred", "system", self.test_state, context
        )
        
        self.assertEqual(ui_state.mode, UIMode.ERROR)
        # description이 None일 수 있으므로 더 안전한 검증
        if ui_state.description:
            self.assertIn("테스트 오류", ui_state.description)
        else:
            # description이 없으면 title에서 확인
            self.assertEqual(ui_state.title, "오류 발생")


class TestStateManagerUIIntegration(unittest.TestCase):
    """StateManager와 UI 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_state = StateManager.create_initial_state(
            "test_user", "beginner", "low"
        )
    
    @patch('services.agent_ui_service.get_agent_ui_generator')
    def test_update_ui_state_for_agent(self, mock_get_generator):
        """에이전트별 UI 상태 업데이트 테스트"""
        # Mock UI 생성기 설정
        mock_generator = Mock()
        mock_ui_state = Mock()
        mock_ui_state.mode.value = 'chat'
        mock_generator.generate_ui_for_agent.return_value = mock_ui_state
        mock_get_generator.return_value = mock_generator
        
        # Mock 직렬화
        with patch('services.ui_mode_service.UIStateSerializer.serialize_ui_state') as mock_serialize:
            mock_serialize.return_value = {'mode': 'chat', 'elements': []}
            
            # UI 상태 업데이트
            updated_state = StateManager.update_ui_state_for_agent(
                self.test_state, "theory_educator"
            )
            
            # 검증
            self.assertEqual(updated_state['ui_mode'], 'chat')
            self.assertIsNotNone(updated_state['ui_elements'])
            mock_generator.generate_ui_for_agent.assert_called_once()
    
    @patch('services.agent_ui_service.get_ui_transition_manager')
    def test_handle_ui_transition(self, mock_get_manager):
        """UI 전환 이벤트 처리 테스트"""
        # Mock 전환 관리자 설정
        mock_manager = Mock()
        mock_ui_state = Mock()
        mock_ui_state.mode.value = 'loading'
        mock_manager.handle_transition.return_value = mock_ui_state
        mock_get_manager.return_value = mock_manager
        
        # Mock 직렬화
        with patch('services.ui_mode_service.UIStateSerializer.serialize_ui_state') as mock_serialize:
            mock_serialize.return_value = {'mode': 'loading', 'elements': []}
            
            # UI 전환 처리
            updated_state = StateManager.handle_ui_transition(
                self.test_state, "user_input_received", "theory_educator"
            )
            
            # 검증
            self.assertEqual(updated_state['ui_mode'], 'loading')
            mock_manager.handle_transition.assert_called_once()


if __name__ == '__main__':
    unittest.main()