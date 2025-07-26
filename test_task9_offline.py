# test_task9_offline.py
# 작업 9: 학습 루프 관리 시스템 오프라인 테스트

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath('.'))

# 데이터베이스 의존성 없이 테스트하기 위한 Mock 설정
sys.modules['models'] = Mock()
sys.modules['models.learning_loop'] = Mock()
sys.modules['models.conversation'] = Mock()
sys.modules['models.user'] = Mock()
sys.modules['models.quiz_attempt'] = Mock()
sys.modules['models.chapter'] = Mock()
sys.modules['services.database_service'] = Mock()

from workflow.state_management import TutorState, StateManager

class TestTask9Offline(unittest.TestCase):
    """작업 9 오프라인 테스트: 데이터베이스 없이 핵심 로직 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.user_id = 1
        self.chapter_id = 1
        
        # 테스트용 State 생성
        self.test_state = StateManager.create_initial_state(
            user_id=str(self.user_id),
            user_type="beginner",
            user_level="low"
        )
        self.test_state['current_chapter'] = self.chapter_id
    
    def test_state_creation_and_validation(self):
        """State 생성 및 검증 테스트"""
        print("\n=== State 생성 및 검증 테스트 ===")
        
        # 1. 초기 상태 생성
        state = StateManager.create_initial_state("test_user", "business", "high")
        
        # 2. 기본 필드 확인
        self.assertEqual(state['user_id'], "test_user")
        self.assertEqual(state['user_type'], "business")
        self.assertEqual(state['user_level'], "high")
        self.assertEqual(state['current_chapter'], 1)
        self.assertEqual(state['ui_mode'], "chat")
        self.assertEqual(len(state['current_loop_conversations']), 0)
        self.assertEqual(len(state['recent_loops_summary']), 0)
        
        # 3. State 유효성 검증
        self.assertTrue(StateManager.validate_state(state))
        
        # 4. 잘못된 State 검증
        invalid_state = state.copy()
        invalid_state['user_level'] = 'invalid_level'
        self.assertFalse(StateManager.validate_state(invalid_state))
        
        print("✓ State 생성 및 검증 정상 작동")
    
    def test_conversation_management(self):
        """대화 관리 테스트"""
        print("\n=== 대화 관리 테스트 ===")
        
        # 1. 대화 추가
        self.test_state = StateManager.add_conversation(
            self.test_state,
            agent_name="TheoryEducator",
            user_message="AI란 무엇인가요?",
            system_response="AI는 인공지능을 의미합니다."
        )
        
        # 2. 대화 추가 확인
        self.assertEqual(len(self.test_state['current_loop_conversations']), 1)
        
        conv = self.test_state['current_loop_conversations'][0]
        self.assertEqual(conv['agent_name'], "TheoryEducator")
        self.assertEqual(conv['user_message'], "AI란 무엇인가요?")
        self.assertEqual(conv['system_response'], "AI는 인공지능을 의미합니다.")
        self.assertEqual(conv['sequence_order'], 1)
        
        # 3. 여러 대화 추가
        agents_and_messages = [
            ("QuizGenerator", "", "다음 문제를 풀어보세요..."),
            ("QnAResolver", "머신러닝이 뭔가요?", "머신러닝은 AI의 한 분야입니다."),
            ("EvaluationFeedbackAgent", "", "잘 이해하셨네요!")
        ]
        
        for agent, user_msg, system_msg in agents_and_messages:
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=agent,
                user_message=user_msg,
                system_response=system_msg
            )
        
        # 4. 전체 대화 수 확인
        self.assertEqual(len(self.test_state['current_loop_conversations']), 4)
        
        # 5. 시퀀스 순서 확인
        for i, conv in enumerate(self.test_state['current_loop_conversations']):
            self.assertEqual(conv['sequence_order'], i + 1)
        
        print("✓ 대화 관리 정상 작동")
    
    def test_loop_summary_creation(self):
        """루프 요약 생성 테스트"""
        print("\n=== 루프 요약 생성 테스트 ===")
        
        # 1. 다양한 대화 추가
        conversations = [
            ("TheoryEducator", "AI의 정의를 알려주세요", "AI는 인공지능입니다"),
            ("TheoryEducator", "머신러닝에 대해 설명해주세요", "머신러닝은 데이터로부터 학습하는 기술입니다"),
            ("QuizGenerator", "", "AI에 관한 문제를 출제하겠습니다"),
            ("QnAResolver", "딥러닝과 머신러닝의 차이는?", "딥러닝은 머신러닝의 하위 분야입니다"),
            ("EvaluationFeedbackAgent", "", "이해도가 향상되었습니다")
        ]
        
        for agent, user_msg, system_msg in conversations:
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=agent,
                user_message=user_msg,
                system_response=system_msg
            )
        
        # 2. 루프 요약 생성
        summary = StateManager._create_loop_summary(self.test_state)
        
        # 3. 요약 내용 검증
        self.assertIn('loop_id', summary)
        self.assertIn('chapter', summary)
        self.assertIn('start_time', summary)
        self.assertIn('end_time', summary)
        self.assertIn('conversation_count', summary)
        self.assertIn('agents_used', summary)
        self.assertIn('main_topics', summary)
        
        # 4. 구체적 내용 확인
        self.assertEqual(summary['chapter'], str(self.chapter_id))
        self.assertEqual(summary['conversation_count'], '5')
        self.assertIn('TheoryEducator', summary['agents_used'])
        self.assertIn('QuizGenerator', summary['agents_used'])
        self.assertIn('AI의 정의', summary['main_topics'])
        
        print("✓ 루프 요약 생성 정상 작동")
    
    def test_loop_completion(self):
        """루프 완료 처리 테스트"""
        print("\n=== 루프 완료 처리 테스트 ===")
        
        # 1. 대화 추가
        for i in range(3):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{i}",
                user_message=f"질문 {i}",
                system_response=f"답변 {i}"
            )
        
        # 2. 완료 전 상태 확인
        self.assertEqual(len(self.test_state['current_loop_conversations']), 3)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 0)
        
        # 3. 루프 완료 처리
        self.test_state = StateManager.complete_current_loop(
            self.test_state,
            summary="첫 번째 루프 완료"
        )
        
        # 4. 완료 후 상태 확인
        self.assertEqual(len(self.test_state['current_loop_conversations']), 0)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 1)
        
        # 5. 요약 내용 확인
        summary = self.test_state['recent_loops_summary'][0]
        self.assertEqual(summary['summary'], "첫 번째 루프 완료")
        self.assertEqual(summary['status'], 'completed')
        
        print("✓ 루프 완료 처리 정상 작동")
    
    def test_multiple_loop_management(self):
        """다중 루프 관리 테스트"""
        print("\n=== 다중 루프 관리 테스트 ===")
        
        # 1. 첫 번째 루프
        for i in range(3):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name="TheoryEducator",
                user_message=f"이론 질문 {i}",
                system_response=f"이론 답변 {i}"
            )
        
        self.test_state = StateManager.complete_current_loop(
            self.test_state,
            summary="이론 학습 완료"
        )
        
        # 2. 두 번째 루프
        for i in range(2):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name="QuizGenerator",
                user_message="",
                system_response=f"퀴즈 문제 {i}"
            )
        
        self.test_state = StateManager.complete_current_loop(
            self.test_state,
            summary="퀴즈 풀이 완료"
        )
        
        # 3. 세 번째 루프
        for i in range(4):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name="QnAResolver",
                user_message=f"Q&A 질문 {i}",
                system_response=f"Q&A 답변 {i}"
            )
        
        self.test_state = StateManager.complete_current_loop(
            self.test_state,
            summary="Q&A 세션 완료"
        )
        
        # 4. 결과 검증
        self.assertEqual(len(self.test_state['current_loop_conversations']), 0)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 3)
        
        # 5. 각 루프 요약 확인
        summaries = self.test_state['recent_loops_summary']
        self.assertEqual(summaries[0]['summary'], "이론 학습 완료")
        self.assertEqual(summaries[1]['summary'], "퀴즈 풀이 완료")
        self.assertEqual(summaries[2]['summary'], "Q&A 세션 완료")
        
        print("✓ 다중 루프 관리 정상 작동")
    
    def test_loop_summary_limit(self):
        """루프 요약 개수 제한 테스트"""
        print("\n=== 루프 요약 개수 제한 테스트 ===")
        
        # 1. 6개의 루프 생성 (제한은 5개)
        for loop_num in range(6):
            # 각 루프에 대화 추가
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{loop_num}",
                user_message=f"루프 {loop_num} 질문",
                system_response=f"루프 {loop_num} 답변"
            )
            
            # 루프 완료
            self.test_state = StateManager.complete_current_loop(
                self.test_state,
                summary=f"루프 {loop_num} 완료"
            )
        
        # 2. 최대 5개만 유지되는지 확인
        self.assertEqual(len(self.test_state['recent_loops_summary']), 5)
        
        # 3. 가장 오래된 루프(0번)가 제거되고 최근 5개만 남아있는지 확인
        summaries = self.test_state['recent_loops_summary']
        summary_texts = [s['summary'] for s in summaries]
        
        self.assertNotIn("루프 0 완료", summary_texts)
        self.assertIn("루프 1 완료", summary_texts)
        self.assertIn("루프 5 완료", summary_texts)
        
        print("✓ 루프 요약 개수 제한 정상 작동")
    
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
            system_response="자연어 처리는 컴퓨터가 인간의 언어를 이해하고 처리하는 기술입니다"
        )
        
        self.test_state = StateManager.add_conversation(
            self.test_state,
            agent_name="QnAResolver",
            user_message="NLP의 주요 기술은 무엇인가요?",
            system_response="토큰화, 형태소 분석, 구문 분석 등이 있습니다"
        )
        
        # 3. 컨텍스트 생성
        context = StateManager.get_context_for_agent(self.test_state, "QnAResolver")
        
        # 4. 컨텍스트 내용 검증
        self.assertIn("사용자 유형: beginner", context)
        self.assertIn("사용자 레벨: low", context)
        self.assertIn("현재 챕터: 1", context)
        self.assertIn("최근 학습 요약", context)
        self.assertIn("AI 기본 개념", context)
        self.assertIn("현재 루프 대화", context)
        self.assertIn("자연어 처리", context)
        self.assertIn("NLP의 주요 기술", context)
        
        print("✓ 컨텍스트 생성 정상 작동")
    
    def test_ui_mode_management(self):
        """UI 모드 관리 테스트"""
        print("\n=== UI 모드 관리 테스트 ===")
        
        # 1. 초기 UI 모드 확인
        self.assertEqual(self.test_state['ui_mode'], 'chat')
        
        # 2. UI 모드 변경
        self.test_state = StateManager.update_ui_mode(self.test_state, 'quiz')
        self.assertEqual(self.test_state['ui_mode'], 'quiz')
        
        # 3. 잘못된 UI 모드 설정 시도
        self.test_state = StateManager.update_ui_mode(self.test_state, 'invalid_mode')
        self.assertEqual(self.test_state['ui_mode'], 'quiz')  # 변경되지 않음
        
        # 4. 유효한 UI 모드들 테스트
        valid_modes = ['chat', 'quiz', 'restricted', 'error']
        for mode in valid_modes:
            self.test_state = StateManager.update_ui_mode(self.test_state, mode)
            self.assertEqual(self.test_state['ui_mode'], mode)
        
        print("✓ UI 모드 관리 정상 작동")
    
    def test_system_response_management(self):
        """시스템 응답 관리 테스트"""
        print("\n=== 시스템 응답 관리 테스트 ===")
        
        # 1. 시스템 응답 설정
        test_message = "안녕하세요! AI 학습을 시작하겠습니다."
        test_ui_elements = {
            'buttons': ['시작하기', '도움말'],
            'progress': 25
        }
        
        self.test_state = StateManager.set_system_response(
            self.test_state,
            message=test_message,
            ui_elements=test_ui_elements
        )
        
        # 2. 설정 확인
        self.assertEqual(self.test_state['system_message'], test_message)
        self.assertEqual(self.test_state['ui_elements'], test_ui_elements)
        
        # 3. UI 요소 없이 메시지만 설정
        simple_message = "계속 진행하겠습니다."
        self.test_state = StateManager.set_system_response(
            self.test_state,
            message=simple_message
        )
        
        self.assertEqual(self.test_state['system_message'], simple_message)
        self.assertIsNone(self.test_state['ui_elements'])
        
        print("✓ 시스템 응답 관리 정상 작동")
    
    def test_new_loop_initialization(self):
        """새 루프 초기화 테스트"""
        print("\n=== 새 루프 초기화 테스트 ===")
        
        # 1. 현재 루프에 대화 추가
        for i in range(3):
            self.test_state = StateManager.add_conversation(
                self.test_state,
                agent_name=f"Agent{i}",
                user_message=f"질문 {i}",
                system_response=f"답변 {i}"
            )
        
        original_loop_id = self.test_state['current_loop_id']
        
        # 2. 새 루프 시작
        self.test_state = StateManager.start_new_loop(self.test_state)
        
        # 3. 새 루프 확인
        self.assertNotEqual(self.test_state['current_loop_id'], original_loop_id)
        self.assertEqual(len(self.test_state['current_loop_conversations']), 0)
        self.assertEqual(len(self.test_state['recent_loops_summary']), 1)
        
        # 4. 이전 루프가 요약에 저장되었는지 확인
        summary = self.test_state['recent_loops_summary'][0]
        self.assertEqual(summary['loop_id'], original_loop_id)
        self.assertEqual(summary['conversation_count'], '3')
        
        print("✓ 새 루프 초기화 정상 작동")

def run_task9_offline_tests():
    """작업 9 오프라인 테스트 실행"""
    print("=" * 60)
    print("작업 9: 학습 루프 관리 시스템 오프라인 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask9Offline)
    
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
    success = run_task9_offline_tests()
    sys.exit(0 if success else 1)