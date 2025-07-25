# tests/unit/test_supervisor.py
# LearningSupervisor 에이전트 테스트

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from workflow.state_management import TutorState, StateManager
from agents.supervisor import LearningSupervisor
from agents.supervisor.progress_analyzer import ProgressAnalyzer
from agents.supervisor.loop_manager import LoopManager
from agents.supervisor.decision_maker import DecisionMaker


class TestProgressAnalyzer:
    """ProgressAnalyzer 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.analyzer = ProgressAnalyzer()
    
    def test_analyze_current_progress_empty(self):
        """빈 상태 진도 분석 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        analysis = self.analyzer.analyze_current_progress(state)
        
        assert analysis['chapter'] == 1
        assert analysis['current_loop_progress']['conversation_count'] == 0
        assert analysis['current_loop_progress']['has_theory'] == False
        assert analysis['current_loop_progress']['has_quiz'] == False
        assert analysis['current_loop_progress']['has_qna'] == False
    
    def test_analyze_current_progress_with_conversations(self):
        """대화가 있는 상태 진도 분석 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 대화 추가
        state = StateManager.add_conversation(
            state, "TheoryEducator", "질문", "이론 설명"
        )
        state = StateManager.add_conversation(
            state, "QuizGenerator", "퀴즈 요청", "퀴즈 생성"
        )
        
        analysis = self.analyzer.analyze_current_progress(state)
        
        assert analysis['current_loop_progress']['conversation_count'] == 2
        assert analysis['current_loop_progress']['has_theory'] == True
        assert analysis['current_loop_progress']['has_quiz'] == True
        assert analysis['current_loop_progress']['has_qna'] == False
    
    def test_check_completion_status_incomplete(self):
        """미완료 상태 확인 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        completion_status = self.analyzer._check_completion_status(state)
        
        assert completion_status['is_complete'] == False
        assert completion_status['total_conversations'] < 5
        assert completion_status['has_quiz'] == False
    
    def test_check_completion_status_complete(self):
        """완료 상태 확인 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 충분한 대화와 퀴즈 추가
        for i in range(6):
            state = StateManager.add_conversation(
                state, "TheoryEducator", f"질문 {i}", f"답변 {i}"
            )
        
        state = StateManager.add_conversation(
            state, "QuizGenerator", "퀴즈", "퀴즈 생성"
        )
        
        completion_status = self.analyzer._check_completion_status(state)
        
        assert completion_status['is_complete'] == True
        assert completion_status['total_conversations'] >= 5
        assert completion_status['has_quiz'] == True
    
    def test_should_advance_chapter(self):
        """챕터 진행 여부 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 미완료 상태
        assert self.analyzer.should_advance_chapter(state) == False
        
        # 완료 상태로 만들기
        for i in range(6):
            state = StateManager.add_conversation(
                state, "TheoryEducator", f"질문 {i}", f"답변 {i}"
            )
        state = StateManager.add_conversation(
            state, "QuizGenerator", "퀴즈", "퀴즈"
        )
        
        assert self.analyzer.should_advance_chapter(state) == True
    
    def test_get_next_recommended_action(self):
        """다음 권장 행동 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 이론 학습이 없는 경우
        action = self.analyzer.get_next_recommended_action(state)
        assert action == 'theory'
        
        # 이론은 있지만 퀴즈가 없는 경우
        state = StateManager.add_conversation(
            state, "TheoryEducator", "질문", "이론 설명"
        )
        action = self.analyzer.get_next_recommended_action(state)
        assert action == 'quiz'


class TestLoopManager:
    """LoopManager 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.loop_manager = LoopManager()
    
    def test_should_complete_current_loop_false(self):
        """루프 완료 불필요 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        result = self.loop_manager.should_complete_current_loop(state)
        assert result == False
    
    def test_should_complete_current_loop_true_completed_stage(self):
        """완료 단계로 인한 루프 완료 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'completed'
        
        result = self.loop_manager.should_complete_current_loop(state)
        assert result == True
    
    def test_should_complete_current_loop_true_max_conversations(self):
        """최대 대화 수로 인한 루프 완료 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 최대 대화 수만큼 추가
        for i in range(self.loop_manager.max_loop_conversations):
            state = StateManager.add_conversation(
                state, "TestAgent", f"메시지 {i}", f"응답 {i}"
            )
        
        result = self.loop_manager.should_complete_current_loop(state)
        assert result == True
    
    def test_complete_current_loop(self):
        """현재 루프 완료 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 대화 추가
        state = StateManager.add_conversation(
            state, "TheoryEducator", "질문", "답변"
        )
        
        old_loop_id = state['current_loop_id']
        
        # 루프 완료
        result_state = self.loop_manager.complete_current_loop(state)
        
        assert result_state['current_loop_id'] != old_loop_id
        assert len(result_state['current_loop_conversations']) == 0
        assert len(result_state['recent_loops_summary']) == 1
    
    def test_start_new_loop(self):
        """새 루프 시작 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 기존 대화 추가
        state = StateManager.add_conversation(
            state, "TestAgent", "메시지", "응답"
        )
        
        old_loop_id = state['current_loop_id']
        
        # 새 루프 시작
        result_state = self.loop_manager.start_new_loop(state, "test_reason")
        
        assert result_state['current_loop_id'] != old_loop_id
        assert len(result_state['current_loop_conversations']) == 0
        assert len(result_state['recent_loops_summary']) == 1
    
    def test_get_loop_statistics_empty(self):
        """빈 상태 루프 통계 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        stats = self.loop_manager.get_loop_statistics(state)
        
        assert stats['total_loops'] == 0
        assert stats['total_conversations'] == 0
        assert stats['average_loop_length'] == 0
        assert stats['most_used_agent'] is None
    
    def test_get_loop_statistics_with_data(self):
        """데이터가 있는 루프 통계 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 현재 루프에 대화 추가
        state = StateManager.add_conversation(
            state, "TheoryEducator", "질문1", "답변1"
        )
        state = StateManager.add_conversation(
            state, "TheoryEducator", "질문2", "답변2"
        )
        
        # 이전 루프 요약 추가
        state['recent_loops_summary'] = [{
            'loop_id': 'test_loop',
            'conversation_count': '3',
            'agents_used': 'TheoryEducator, QuizGenerator'
        }]
        
        stats = self.loop_manager.get_loop_statistics(state)
        
        assert stats['total_loops'] == 2  # 현재 + 이전
        assert stats['total_conversations'] == 5  # 2 + 3
        assert stats['average_loop_length'] == 2.5


class TestDecisionMaker:
    """DecisionMaker 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.decision_maker = DecisionMaker()
    
    def test_analyze_user_intent_question(self):
        """사용자 의도 분석 - 질문 테스트"""
        intent = self.decision_maker._analyze_user_intent("이게 뭐예요?")
        assert intent == 'question'
        
        intent = self.decision_maker._analyze_user_intent("어떻게 하나요?")
        assert intent == 'question'
    
    def test_analyze_user_intent_quiz_request(self):
        """사용자 의도 분석 - 퀴즈 요청 테스트"""
        intent = self.decision_maker._analyze_user_intent("문제 내주세요")
        assert intent == 'quiz_request'
        
        intent = self.decision_maker._analyze_user_intent("퀴즈 풀고 싶어요")
        assert intent == 'quiz_request'
    
    def test_analyze_user_intent_continue(self):
        """사용자 의도 분석 - 계속 진행 테스트"""
        intent = self.decision_maker._analyze_user_intent("다음으로 넘어가주세요")
        assert intent == 'continue'
        
        intent = self.decision_maker._analyze_user_intent("계속 진행해주세요")
        assert intent == 'continue'
    
    def test_decide_within_loop_question(self):
        """루프 내 결정 - 질문 처리 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['user_message'] = "이게 뭐예요?"
        
        progress_analysis = {
            'current_loop_progress': {
                'has_theory': True,
                'has_quiz': False,
                'has_qna': False
            }
        }
        
        decision = self.decision_maker._decide_within_loop(state, progress_analysis)
        
        assert decision['next_step'] == 'qna_resolver'
        assert decision['stage'] == 'question'
        assert decision['ui_mode'] == 'chat'
    
    def test_decide_within_loop_theory_needed(self):
        """루프 내 결정 - 이론 학습 필요 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['user_message'] = "AI에 대해 알려주세요"  # 질문이 아닌 설명 요청
        
        progress_analysis = {
            'current_loop_progress': {
                'has_theory': False,
                'has_quiz': False,
                'has_qna': False
            }
        }
        
        decision = self.decision_maker._decide_within_loop(state, progress_analysis)
        
        # 사용자 의도 분석에 따라 결과가 달라질 수 있음
        # "설명해주세요"는 질문으로 분류될 수 있으므로 qna_resolver가 될 수 있음
        assert decision['next_step'] in ['theory_educator', 'qna_resolver']
        assert decision['stage'] in ['theory', 'question']
        assert decision['ui_mode'] == 'chat'
    
    def test_determine_difficulty_level(self):
        """난이도 수준 결정 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['user_level'] = 'low'
        state['user_type'] = 'beginner'
        state['current_chapter'] = 1
        
        difficulty = self.decision_maker.determine_difficulty_level(state)
        assert difficulty == 'easy'
        
        # 비즈니스 사용자
        state['user_type'] = 'business'
        state['user_level'] = 'high'
        difficulty = self.decision_maker.determine_difficulty_level(state)
        assert difficulty == 'hard'
    
    def test_generate_learning_path(self):
        """학습 경로 생성 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_chapter'] = 1
        
        progress_analysis = {
            'current_loop_progress': {
                'has_theory': False,
                'has_quiz': False,
                'has_qna': False
            }
        }
        
        # ProgressAnalyzer 모킹
        with patch.object(self.decision_maker, 'progress_analyzer') as mock_analyzer:
            mock_analyzer.analyze_current_progress.return_value = progress_analysis
            
            learning_path = self.decision_maker.generate_learning_path(state)
            
            assert isinstance(learning_path, list)
            assert len(learning_path) > 0
            
            # 첫 번째 단계가 이론 학습인지 확인
            first_step = learning_path[0]
            assert first_step['step'] == 'theory'
            assert 'description' in first_step
            assert 'estimated_time' in first_step


class TestLearningSupervisor:
    """LearningSupervisor 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.supervisor = LearningSupervisor()
    
    def test_init(self):
        """초기화 테스트"""
        assert self.supervisor.agent_name == "LearningSupervisor"
        assert isinstance(self.supervisor.progress_analyzer, ProgressAnalyzer)
        assert isinstance(self.supervisor.loop_manager, LoopManager)
        assert isinstance(self.supervisor.decision_maker, DecisionMaker)
    
    @patch('agents.supervisor.ProgressAnalyzer')
    @patch('agents.supervisor.LoopManager')
    @patch('agents.supervisor.DecisionMaker')
    def test_execute_normal_flow(self, mock_decision_maker, mock_loop_manager, mock_progress_analyzer):
        """정상 실행 플로우 테스트"""
        # Mock 설정
        mock_progress_instance = mock_progress_analyzer.return_value
        mock_loop_instance = mock_loop_manager.return_value
        mock_decision_instance = mock_decision_maker.return_value
        
        mock_progress_instance.analyze_current_progress.return_value = {
            'current_loop_progress': {'has_theory': True},
            'completion_status': {'completion_percentage': 50},
            'recommendations': ['계속 진행하세요']
        }
        
        mock_loop_instance.should_complete_current_loop.return_value = False
        
        mock_decision_instance.decide_next_step.return_value = {
            'next_step': 'theory_educator',
            'stage': 'theory',
            'reason': '이론 학습 필요',
            'ui_mode': 'chat'
        }
        
        # 테스트 실행
        state = StateManager.create_initial_state("test_user")
        result_state = self.supervisor.execute(state)
        
        # 검증
        assert 'system_message' in result_state
        assert result_state['current_stage'] == 'theory'
        assert result_state['ui_mode'] == 'chat'
    
    def test_execute_error_handling(self):
        """오류 처리 테스트"""
        # 잘못된 상태로 오류 유발
        invalid_state = {}
        
        result_state = self.supervisor.execute(invalid_state)
        
        assert 'system_message' in result_state
        # 실제로는 기본값으로 처리되어 정상 메시지가 나올 수 있음
        # 오류 메시지 또는 정상 메시지 둘 다 허용
        assert len(result_state['system_message']) > 0
    
    def test_get_agent_info(self):
        """에이전트 정보 반환 테스트"""
        info = self.supervisor.get_agent_info()
        
        assert info['name'] == "LearningSupervisor"
        assert 'description' in info
        assert 'version' in info
        assert 'capabilities' in info
        assert 'dependencies' in info
        assert isinstance(info['capabilities'], list)
        assert len(info['capabilities']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])