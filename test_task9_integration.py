# test_task9_integration.py
# 작업 9: 학습 루프 관리 시스템 통합 테스트

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath('.'))

from workflow.state_management import TutorState, StateManager
from services.loop_service import LoopService
from services.progress_service import ProgressService
from agents.supervisor.loop_manager import LoopManager

class TestTask9Integration(unittest.TestCase):
    """작업 9 통합 테스트: 학습 루프 관리 시스템"""
    
    def setUp(self):
        """테스트 설정"""
        self.user_id = 1
        self.chapter_id = 1
        
        # 서비스 인스턴스 생성
        self.loop_service = LoopService()
        self.progress_service = ProgressService()
        self.loop_manager = LoopManager()
        
        # 테스트용 State 생성
        self.test_state = StateManager.create_initial_state(
            user_id=str(self.user_id),
            user_type="beginner",
            user_level="low"
        )
        self.test_state['current_chapter'] = self.chapter_id
    
    def test_state_management_integration(self):
        """State 관리 통합 테스트"""
        print("\n=== State 관리 통합 테스트 ===")
        
        # 1. 초기 상태 검증
        self.assertTrue(StateManager.validate_state(self.test_state))
        self.assertEqual(len(self.test_state['current_loop_conversations']), 0)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 0)
        
        # 2. 대화 추가
        self.test_state = StateManager.add_conversation(
            self.test_state,
            agent_name="TheoryEducator",
            user_message="AI란 무엇인가요?",
            system_response="AI는 인공지능을 의미합니다..."
        )
        
        self.assertEqual(len(self.test_state['current_loop_conversations']), 1)
        conv = self.test_state['current_loop_conversations'][0]
        self.assertEqual(conv['agent_name'], "TheoryEducator")
        self.assertEqual(conv['user_message'], "AI란 무엇인가요?")
        
        # 3. 더 많은 대화 추가
        for i in range(3):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{i}",
                user_message=f"질문 {i}",
                system_response=f"답변 {i}"
            )
        
        self.assertEqual(len(self.test_state['current_loop_conversations']), 4)
        
        # 4. 루프 완료 처리
        self.test_state = StateManager.complete_current_loop(
            self.test_state,
            summary="첫 번째 루프 완료"
        )
        
        self.assertEqual(len(self.test_state['current_loop_conversations']), 0)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 1)
        
        summary = self.test_state['recent_loops_summary'][0]
        self.assertEqual(summary['summary'], "첫 번째 루프 완료")
        self.assertEqual(summary['status'], 'completed')
        
        print("✓ State 관리 기본 기능 정상 작동")
    
    def test_loop_manager_integration(self):
        """루프 매니저 통합 테스트"""
        print("\n=== 루프 매니저 통합 테스트 ===")
        
        # 1. 루프 완료 조건 테스트
        should_complete, reason = self.loop_manager.should_complete_loop(self.test_state)
        self.assertFalse(should_complete)  # 빈 루프는 완료하지 않음
        
        # 2. 많은 대화로 루프 채우기
        for i in range(55):  # 최대 대화 수 초과
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{i % 3}",
                user_message=f"질문 {i}",
                system_response=f"답변 {i}"
            )
        
        should_complete, reason = self.loop_manager.should_complete_loop(self.test_state)
        self.assertTrue(should_complete)
        self.assertIn("대화 수 한계", reason)
        
        # 3. 루프 상태 정보 조회
        status_info = self.loop_manager.get_loop_status_info(self.test_state)
        self.assertIsInstance(status_info, dict)
        self.assertEqual(status_info['conversation_count'], 55)
        self.assertTrue(status_info['should_complete'])
        
        print("✓ 루프 매니저 완료 조건 판단 정상 작동")
    
    def test_loop_summary_generation(self):
        """루프 요약 생성 테스트"""
        print("\n=== 루프 요약 생성 테스트 ===")
        
        # 1. 다양한 에이전트와 대화 추가
        agents_and_messages = [
            ("TheoryEducator", "AI의 기본 개념을 설명해주세요", "AI는 인공지능입니다..."),
            ("QuizGenerator", "", "다음 문제를 풀어보세요: AI의 정의는?"),
            ("QnAResolver", "머신러닝과 딥러닝의 차이는?", "머신러닝은 더 넓은 개념이고..."),
            ("EvaluationFeedbackAgent", "", "훌륭합니다! 이해도가 높아졌네요.")
        ]
        
        for agent, user_msg, system_msg in agents_and_messages:
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=agent,
                user_message=user_msg,
                system_response=system_msg
            )
        
        # 2. 포괄적인 요약 생성
        summary = self.loop_manager.generate_comprehensive_summary(self.test_state)
        
        self.assertIsInstance(summary, str)
        self.assertIn("루프", summary)
        self.assertIn("챕터", summary)
        self.assertIn("주요 활동", summary)
        self.assertIn("TheoryEducator", summary)
        self.assertIn("QuizGenerator", summary)
        
        # 3. 요약에 주요 질문이 포함되는지 확인
        self.assertIn("AI의 기본 개념", summary)
        self.assertIn("머신러닝과 딥러닝", summary)
        
        print("✓ 루프 요약 생성 정상 작동")
    
    def test_state_optimization(self):
        """State 최적화 테스트"""
        print("\n=== State 최적화 테스트 ===")
        
        # 1. 많은 대화로 State 채우기 (60개)
        for i in range(60):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{i % 5}",
                user_message=f"사용자 메시지 {i}",
                system_response=f"시스템 응답 {i}"
            )
        
        initial_count = len(self.test_state['current_loop_conversations'])
        self.assertEqual(initial_count, 60)
        
        # 2. State 최적화 실행
        optimized_state = self.loop_service.optimize_state_size(self.test_state)
        
        # 3. 최적화 결과 검증
        optimized_count = len(optimized_state['current_loop_conversations'])
        self.assertLessEqual(optimized_count, 31)  # 요약 + 최근 30개
        
        # 4. 첫 번째 대화가 요약인지 확인
        first_conv = optimized_state['current_loop_conversations'][0]
        self.assertEqual(first_conv['agent_name'], 'system')
        self.assertIn('[이전 대화 요약]', first_conv['system_response'])
        
        print(f"✓ State 최적화 완료: {initial_count}개 → {optimized_count}개")
    
    @patch('services.progress_service.UserLearningProgress')
    @patch('services.progress_service.LearningLoop')
    def test_progress_tracking_integration(self, mock_learning_loop, mock_progress):
        """진도 추적 통합 테스트"""
        print("\n=== 진도 추적 통합 테스트 ===")
        
        # 1. Mock 데이터 설정
        mock_progress_instance = Mock()
        mock_progress_instance.progress_percentage = 60.0
        mock_progress_instance.understanding_score = 75.0
        mock_progress_instance.study_time_minutes = 90
        mock_progress_instance.is_completed = False
        mock_progress_instance.last_studied = datetime.now()
        mock_progress_instance.save = Mock()
        
        mock_progress.get_or_create.return_value = mock_progress_instance
        
        # Mock 루프 데이터
        mock_loops = []
        for i in range(3):
            loop = Mock()
            loop.interaction_count = 8 + i
            loop.duration_minutes = 20 + i * 5
            loop.loop_status = 'completed'
            loop.get_conversations.return_value = []
            loop.get_performance_metrics.return_value = {
                'duration_minutes': 20 + i * 5,
                'interaction_count': 8 + i,
                'quiz_success_rate': 80.0 + i * 5
            }
            mock_loops.append(loop)
        
        mock_learning_loop.get_user_loops.return_value = mock_loops
        
        # 2. 챕터 진도 계산
        progress_data = self.progress_service.calculate_chapter_progress(
            self.user_id, self.chapter_id
        )
        
        # 3. 결과 검증
        self.assertIsInstance(progress_data, dict)
        self.assertEqual(progress_data['user_id'], self.user_id)
        self.assertEqual(progress_data['chapter_id'], self.chapter_id)
        self.assertEqual(progress_data['progress_percentage'], 60.0)
        self.assertEqual(progress_data['loops_completed'], 3)
        
        # 4. 진도 업데이트 테스트
        updated_progress = self.progress_service.update_chapter_progress(
            user_id=self.user_id,
            chapter_id=self.chapter_id,
            progress_increment=20.0,
            understanding_score=85.0,
            study_time_minutes=30
        )
        
        # 5. 업데이트 검증
        self.assertEqual(mock_progress_instance.progress_percentage, 80.0)
        mock_progress_instance.save.assert_called()
        
        print("✓ 진도 추적 및 업데이트 정상 작동")
    
    def test_loop_completion_workflow(self):
        """루프 완료 워크플로우 테스트"""
        print("\n=== 루프 완료 워크플로우 테스트 ===")
        
        # 1. 학습 시나리오 시뮬레이션
        learning_scenario = [
            ("TheoryEducator", "AI란 무엇인가요?", "AI는 인공지능의 줄임말로..."),
            ("TheoryEducator", "머신러닝에 대해 알려주세요", "머신러닝은 AI의 한 분야로..."),
            ("QuizGenerator", "문제를 내주세요", "다음 중 AI의 정의로 올바른 것은?"),
            ("QnAResolver", "딥러닝과 머신러닝의 차이는?", "딥러닝은 머신러닝의 하위 분야로..."),
            ("EvaluationFeedbackAgent", "", "이해도가 많이 향상되었습니다!")
        ]
        
        # 2. 대화 진행
        for agent, user_msg, system_msg in learning_scenario:
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=agent,
                user_message=user_msg,
                system_response=system_msg
            )
        
        # 3. 완료 조건 확인
        completion_signals = self.loop_manager._check_completion_signals(
            self.test_state['current_loop_conversations']
        )
        
        # 주요 에이전트들이 모두 참여했으므로 완료 신호가 있어야 함
        agents_in_conversation = {conv['agent_name'] for conv in self.test_state['current_loop_conversations']}
        required_agents = {'TheoryEducator', 'QuizGenerator', 'EvaluationFeedbackAgent'}
        
        if required_agents.issubset(agents_in_conversation):
            self.assertTrue(completion_signals['should_complete'])
        
        # 4. 루프 완료 처리
        completed_state = self.loop_manager.complete_current_loop(
            self.test_state,
            reason="학습 목표 달성"
        )
        
        # 5. 완료 결과 검증
        self.assertEqual(len(completed_state['current_loop_conversations']), 0)
        self.assertGreater(len(completed_state['recent_loops_summary']), 0)
        
        print("✓ 루프 완료 워크플로우 정상 작동")
    
    def test_context_generation(self):
        """컨텍스트 생성 테스트"""
        print("\n=== 컨텍스트 생성 테스트 ===")
        
        # 1. 이전 루프 요약 추가
        self.test_state['recent_loops_summary'] = [
            {
                'loop_id': 'loop_001',
                'main_topics': 'AI 기본 개념 | 머신러닝 소개',
                'agents_used': 'TheoryEducator, QuizGenerator'
            },
            {
                'loop_id': 'loop_002', 
                'main_topics': '딥러닝 기초 | 신경망 구조',
                'agents_used': 'TheoryEducator, QnAResolver'
            }
        ]
        
        # 2. 현재 루프에 대화 추가
        self.test_state = StateManager.add_conversation(
            self.test_state,
            agent_name="TheoryEducator",
            user_message="자연어 처리에 대해 알려주세요",
            system_response="자연어 처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 기술입니다..."
        )
        
        # 3. 에이전트용 컨텍스트 생성
        context = StateManager.get_context_for_agent(self.test_state, "QnAResolver")
        
        # 4. 컨텍스트 검증
        self.assertIn("사용자 유형: beginner", context)
        self.assertIn("현재 챕터: 1", context)
        self.assertIn("최근 학습 요약", context)
        self.assertIn("AI 기본 개념", context)
        self.assertIn("현재 루프 대화", context)
        self.assertIn("자연어 처리", context)
        
        print("✓ 컨텍스트 생성 정상 작동")
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        print("\n=== 오류 처리 테스트 ===")
        
        # 1. 잘못된 State 검증
        invalid_state = self.test_state.copy()
        del invalid_state['user_id']  # 필수 필드 제거
        
        self.assertFalse(StateManager.validate_state(invalid_state))
        
        # 2. 빈 대화 리스트 처리
        empty_state = StateManager.create_initial_state("test_user")
        summary = self.loop_manager.generate_comprehensive_summary(empty_state)
        
        self.assertIn("대화 내용이 없는", summary)
        
        # 3. State 최적화 시 빈 대화 처리
        optimized_empty = self.loop_service.optimize_state_size(empty_state)
        self.assertEqual(len(optimized_empty['current_loop_conversations']), 0)
        
        print("✓ 오류 처리 정상 작동")
    
    def test_performance_metrics(self):
        """성능 지표 테스트"""
        print("\n=== 성능 지표 테스트 ===")
        
        # 1. 대화 추가 (시간 간격 시뮬레이션)
        start_time = datetime.now()
        
        for i in range(10):
            # 시간 간격을 두고 대화 추가
            conv_time = start_time + timedelta(minutes=i * 2)
            conversation = {
                'agent_name': f'Agent{i % 3}',
                'user_message': f'질문 {i}',
                'system_response': f'답변 {i}',
                'ui_elements': None,
                'timestamp': conv_time.isoformat(),
                'sequence_order': i + 1
            }
            self.test_state['current_loop_conversations'].append(conversation)
        
        # 2. 루프 상태 정보 조회
        status_info = self.loop_manager.get_loop_status_info(self.test_state)
        
        # 3. 성능 지표 검증
        self.assertEqual(status_info['conversation_count'], 10)
        self.assertGreater(status_info['duration_minutes'], 0)
        self.assertEqual(len(status_info['agents_used']), 3)
        
        print(f"✓ 성능 지표 계산 완료: {status_info['conversation_count']}개 대화, {status_info['duration_minutes']:.1f}분")

def run_task9_tests():
    """작업 9 테스트 실행"""
    print("=" * 60)
    print("작업 9: 학습 루프 관리 시스템 통합 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask9Integration)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n전체 성공률: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_task9_tests()
    sys.exit(0 if success else 1)