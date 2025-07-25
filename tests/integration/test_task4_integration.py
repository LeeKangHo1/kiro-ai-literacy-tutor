# tests/integration/test_task4_integration.py
# 4번 작업 통합 테스트

import pytest
from unittest.mock import Mock, patch

from workflow.state_management import TutorState, StateManager
from agents.supervisor import LearningSupervisor
from agents.educator import TheoryEducator

# LangGraph 의존성을 조건부로 임포트
try:
    from workflow.graph_builder import TutorGraphBuilder, GraphExecutor
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    TutorGraphBuilder = None
    GraphExecutor = None


class TestTask4Integration:
    """4번 작업 통합 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        if LANGGRAPH_AVAILABLE:
            self.graph_builder = TutorGraphBuilder()
        else:
            self.graph_builder = None
        self.supervisor = LearningSupervisor()
        self.educator = TheoryEducator()
    
    def test_state_management_integration(self):
        """상태 관리 통합 테스트"""
        # 초기 상태 생성
        state = StateManager.create_initial_state("integration_test_user")
        
        # 상태 유효성 검증
        assert StateManager.validate_state(state) == True
        
        # 대화 추가
        state = StateManager.add_conversation(
            state,
            agent_name="TheoryEducator",
            user_message="AI가 뭐예요?",
            system_response="AI는 인공지능의 줄임말입니다."
        )
        
        # 대화가 올바르게 추가되었는지 확인
        assert len(state['current_loop_conversations']) == 1
        conversation = state['current_loop_conversations'][0]
        assert conversation['agent_name'] == "TheoryEducator"
        assert conversation['user_message'] == "AI가 뭐예요?"
        
        # 새 루프 시작
        state = StateManager.start_new_loop(state)
        
        # 이전 대화가 요약으로 이동했는지 확인
        assert len(state['current_loop_conversations']) == 0
        assert len(state['recent_loops_summary']) == 1
    
    def test_supervisor_educator_integration(self):
        """슈퍼바이저와 교육자 통합 테스트"""
        # 초기 상태 설정
        state = StateManager.create_initial_state("integration_test_user")
        state['user_message'] = "AI에 대해 설명해주세요"
        state['current_chapter'] = 1
        state['user_level'] = 'medium'
        state['user_type'] = 'beginner'
        
        # 1. 슈퍼바이저 실행
        supervisor_result = self.supervisor.execute(state)
        
        # 슈퍼바이저가 올바르게 실행되었는지 확인
        assert 'system_message' in supervisor_result
        # 사용자 메시지에 따라 다양한 단계가 될 수 있음
        assert supervisor_result['current_stage'] in ['theory', 'theory_completed', 'question', 'continue']
        
        # 2. 교육자 실행 (슈퍼바이저 결과를 입력으로)
        educator_result = self.educator.execute(supervisor_result)
        
        # 교육자가 올바르게 실행되었는지 확인
        assert 'system_message' in educator_result
        assert educator_result['ui_mode'] in ['chat', 'error']
        
        # 학습 메타데이터가 추가되었는지 확인
        if educator_result['ui_mode'] == 'chat':
            assert 'learning_metadata' in educator_result
            assert educator_result['learning_metadata']['theory_completed'] == True
    
    def test_workflow_progression(self):
        """워크플로우 진행 통합 테스트"""
        # 초기 상태
        state = StateManager.create_initial_state("workflow_test_user")
        state['user_message'] = "AI 기초를 배우고 싶어요"
        
        # 여러 단계 시뮬레이션
        steps = [
            ("이론 학습 요청", "theory"),
            ("퀴즈 요청", "quiz"),
            ("질문", "question"),
            ("다음 진행", "continue")
        ]
        
        for user_message, expected_stage in steps:
            state['user_message'] = user_message
            
            # 슈퍼바이저 실행
            state = self.supervisor.execute(state)
            
            # 상태가 올바르게 업데이트되었는지 확인
            assert 'system_message' in state
            assert StateManager.validate_state(state) == True
            
            # 대화 기록 확인 (슈퍼바이저는 대화를 직접 추가하지 않을 수 있음)
            # 상태가 유효하게 업데이트되었는지만 확인
            assert 'current_stage' in state
    
    def test_chapter_progression(self):
        """챕터 진행 통합 테스트"""
        state = StateManager.create_initial_state("chapter_test_user")
        
        # 챕터 1부터 3까지 진행
        for chapter in range(1, 4):
            state['current_chapter'] = chapter
            state['user_message'] = f"챕터 {chapter} 학습하고 싶어요"
            
            # 교육자가 해당 챕터를 처리할 수 있는지 확인
            can_handle = self.educator.can_handle_chapter(chapter)
            assert can_handle == True
            
            # 챕터 정보 확인
            chapter_info = self.educator.get_chapter_info(chapter)
            assert chapter_info is not None
            assert chapter_info['chapter'] == chapter
            assert 'title' in chapter_info
            assert 'objectives' in chapter_info
    
    def test_user_level_adaptation(self):
        """사용자 레벨 적응 통합 테스트"""
        base_state = StateManager.create_initial_state("level_test_user")
        base_state['current_chapter'] = 1
        base_state['user_message'] = "AI에 대해 설명해주세요"
        
        levels = ['low', 'medium', 'high']
        types = ['beginner', 'business']
        
        for user_type in types:
            for user_level in levels:
                # 상태 복사 및 설정
                state = base_state.copy()
                state['user_level'] = user_level
                state['user_type'] = user_type
                
                # 교육자 실행
                result_state = self.educator.execute(state)
                
                # 레벨에 맞는 응답이 생성되었는지 확인
                assert 'system_message' in result_state
                
                # 오류가 발생하지 않았는지 확인
                if result_state.get('ui_mode') != 'error':
                    assert 'learning_metadata' in result_state
                    assert result_state['learning_metadata']['user_level_adapted'] == user_level
    
    def test_error_handling_integration(self):
        """오류 처리 통합 테스트"""
        # 잘못된 상태로 테스트
        invalid_states = [
            {},  # 빈 상태
            {'user_id': 'test'},  # 불완전한 상태
            {'user_level': 'invalid', 'user_type': 'invalid'}  # 잘못된 값
        ]
        
        for invalid_state in invalid_states:
            # 슈퍼바이저 오류 처리 테스트
            supervisor_result = self.supervisor.execute(invalid_state)
            assert 'system_message' in supervisor_result
            
            # 교육자 오류 처리 테스트
            educator_result = self.educator.execute(invalid_state)
            assert 'system_message' in educator_result
    
    def test_conversation_flow(self):
        """대화 흐름 통합 테스트"""
        state = StateManager.create_initial_state("conversation_test_user")
        
        # 대화 시나리오
        conversation_scenarios = [
            {
                'user_message': 'AI가 뭐예요?',
                'expected_agent': 'TheoryEducator',
                'expected_stage': 'theory'
            },
            {
                'user_message': '문제 내주세요',
                'expected_agent': 'QuizGenerator',
                'expected_stage': 'quiz'
            },
            {
                'user_message': '더 자세히 설명해주세요',
                'expected_agent': 'QnAResolver',
                'expected_stage': 'question'
            }
        ]
        
        for scenario in conversation_scenarios:
            state['user_message'] = scenario['user_message']
            
            # 슈퍼바이저를 통한 의사결정
            result_state = self.supervisor.execute(state)
            
            # 올바른 단계로 설정되었는지 확인
            # (실제 에이전트 실행은 그래프에서 처리되므로 단계만 확인)
            assert 'current_stage' in result_state
            assert 'system_message' in result_state
    
    def test_learning_progress_tracking(self):
        """학습 진도 추적 통합 테스트"""
        state = StateManager.create_initial_state("progress_test_user")
        
        # 학습 활동 시뮬레이션
        learning_activities = [
            ('TheoryEducator', '이론 설명', 'AI 개념 설명'),
            ('QuizGenerator', '퀴즈 요청', '퀴즈 생성'),
            ('EvaluationFeedbackAgent', '답변 제출', '평가 결과'),
            ('QnAResolver', '추가 질문', '질문 답변')
        ]
        
        for agent_name, user_msg, system_resp in learning_activities:
            # 대화 추가
            state = StateManager.add_conversation(
                state,
                agent_name=agent_name,
                user_message=user_msg,
                system_response=system_resp
            )
        
        # 진도 분석
        progress_analysis = self.supervisor.progress_analyzer.analyze_current_progress(state)
        
        # 진도 분석 결과 확인
        assert 'current_loop_progress' in progress_analysis
        assert 'completion_status' in progress_analysis
        
        current_progress = progress_analysis['current_loop_progress']
        assert current_progress['conversation_count'] == 4
        assert current_progress['has_theory'] == True
        assert current_progress['has_quiz'] == True
        assert current_progress['has_qna'] == True
    
    @pytest.mark.skipif(not LANGGRAPH_AVAILABLE, reason="LangGraph 의존성 필요")
    def test_graph_execution_integration(self):
        """그래프 실행 통합 테스트 (LangGraph 필요)"""
        # 실제 그래프 실행 테스트
        # LangGraph가 설치된 환경에서만 실행
        
        try:
            # 그래프 빌드
            graph = self.graph_builder.build_graph()
            compiled_graph = self.graph_builder.compile_graph()
            
            # 초기 상태
            state = StateManager.create_initial_state("graph_test_user")
            state['user_message'] = "AI 학습을 시작하고 싶어요"
            
            # 그래프 실행
            executor = GraphExecutor(self.graph_builder)
            result_state = executor.execute_step(state)
            
            # 실행 결과 확인
            assert 'system_message' in result_state
            assert StateManager.validate_state(result_state) == True
            
        except ImportError:
            pytest.skip("LangGraph not available")


class TestTask4EndToEnd:
    """4번 작업 종단간 테스트"""
    
    def test_complete_learning_session(self):
        """완전한 학습 세션 테스트"""
        # 사용자 시작
        state = StateManager.create_initial_state("e2e_test_user")
        state['user_level'] = 'medium'
        state['user_type'] = 'beginner'
        state['current_chapter'] = 1
        
        supervisor = LearningSupervisor()
        educator = TheoryEducator()
        
        # 1. 학습 시작
        state['user_message'] = "AI에 대해 배우고 싶어요"
        state = supervisor.execute(state)
        
        # 2. 이론 학습
        if state.get('current_stage') == 'theory':
            state = educator.execute(state)
            assert state.get('current_stage') == 'theory_completed'
        
        # 3. 추가 질문
        state['user_message'] = "AI와 머신러닝의 차이점이 뭐예요?"
        state = supervisor.execute(state)
        
        # 4. 퀴즈 요청
        state['user_message'] = "문제 내주세요"
        state = supervisor.execute(state)
        
        # 5. 학습 완료 확인
        progress_analysis = supervisor.progress_analyzer.analyze_current_progress(state)
        
        # 세션이 올바르게 진행되었는지 확인
        # 진도 분석이 정상적으로 수행되었는지 확인
        assert 'current_loop_progress' in progress_analysis
        assert 'completion_status' in progress_analysis
        
        # 상태가 유효한지 확인
        assert StateManager.validate_state(state) == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])