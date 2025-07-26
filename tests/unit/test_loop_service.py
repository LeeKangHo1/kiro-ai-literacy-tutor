# tests/unit/test_loop_service.py
# 루프 관리 서비스 단위 테스트

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.loop_service import LoopService
from workflow.state_management import TutorState, StateManager

class TestLoopService(unittest.TestCase):
    """루프 관리 서비스 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.loop_service = LoopService()
        self.user_id = 1
        self.chapter_id = 1
        
        # 테스트용 State 생성
        self.test_state = StateManager.create_initial_state(
            user_id=str(self.user_id),
            user_type="beginner",
            user_level="low"
        )
        self.test_state['current_chapter'] = self.chapter_id
    
    @patch('services.loop_service.LearningLoop')
    def test_start_new_loop(self, mock_learning_loop):
        """새 루프 시작 테스트"""
        # Mock 루프 인스턴스
        mock_loop = Mock()
        mock_loop.loop_id = "test_loop_123"
        mock_loop.started_at = datetime.now()
        mock_loop.start_loop = Mock()
        
        mock_learning_loop.return_value = mock_loop
        mock_learning_loop.get_active_loop.return_value = None  # 기존 활성 루프 없음
        
        # 테스트 실행
        new_loop, updated_state = self.loop_service.start_new_loop(
            user_id=self.user_id,
            chapter_id=self.chapter_id,
            loop_type='mixed',
            state=self.test_state
        )
        
        # 검증
        self.assertEqual(new_loop, mock_loop)
        self.assertEqual(updated_state['current_loop_id'], "test_loop_123")
        self.assertEqual(updated_state['current_chapter'], self.chapter_id)
        mock_loop.start_loop.assert_called_once()
    
    @patch('services.loop_service.LearningLoop')
    def test_complete_loop(self, mock_learning_loop):
        """루프 완료 테스트"""
        # Mock 루프 인스턴스
        mock_loop = Mock()
        mock_loop.loop_id = "test_loop_123"
        mock_loop.loop_status = 'active'
        mock_loop.complete_loop = Mock()
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_loop
        mock_learning_loop.query = mock_query
        
        # 테스트 실행
        completed_loop = self.loop_service.complete_loop(
            loop_id="test_loop_123",
            summary="테스트 요약",
            auto_summary=False
        )
        
        # 검증
        self.assertEqual(completed_loop, mock_loop)
        mock_loop.complete_loop.assert_called_once_with("테스트 요약")
    
    @patch('services.loop_service.LearningLoop')
    def test_add_conversation_to_loop(self, mock_learning_loop):
        """루프에 대화 추가 테스트"""
        # Mock 루프와 대화
        mock_conversation = Mock()
        mock_conversation.processing_time_ms = 0
        mock_conversation.save = Mock()
        
        mock_loop = Mock()
        mock_loop.add_conversation.return_value = mock_conversation
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_loop
        mock_learning_loop.query = mock_query
        
        # 테스트 실행
        conversation = self.loop_service.add_conversation_to_loop(
            loop_id="test_loop_123",
            agent_name="TheoryEducator",
            message_type="system",
            system_response="테스트 응답",
            processing_time_ms=1500
        )
        
        # 검증
        self.assertEqual(conversation, mock_conversation)
        self.assertEqual(conversation.processing_time_ms, 1500)
        mock_loop.add_conversation.assert_called_once()
        conversation.save.assert_called_once()
    
    def test_update_state_with_conversation(self):
        """State 대화 업데이트 테스트"""
        # 초기 대화 수 확인
        initial_count = len(self.test_state['current_loop_conversations'])
        
        # Mock 루프 ID 설정
        self.test_state['current_loop_id'] = "test_loop_123"
        
        with patch.object(self.loop_service, 'add_conversation_to_loop') as mock_add:
            # 테스트 실행
            updated_state = self.loop_service.update_state_with_conversation(
                state=self.test_state,
                agent_name="TheoryEducator",
                user_message="테스트 질문",
                system_response="테스트 응답"
            )
            
            # 검증
            self.assertEqual(len(updated_state['current_loop_conversations']), initial_count + 1)
            mock_add.assert_called_once()
    
    @patch('services.loop_service.LearningLoop')
    def test_generate_loop_summary(self, mock_learning_loop):
        """루프 요약 생성 테스트"""
        # Mock 대화 데이터
        mock_conversations = []
        for i in range(3):
            conv = Mock()
            conv.agent_name = f"Agent{i}"
            conv.message_type = 'user' if i % 2 == 0 else 'system'
            conv.user_message = f"사용자 메시지 {i}" if i % 2 == 0 else None
            conv.system_response = f"시스템 응답 {i}" if i % 2 == 1 else None
            mock_conversations.append(conv)
        
        # Mock 루프
        mock_loop = Mock()
        mock_loop.loop_id = "test_loop_123"
        mock_loop.chapter_id = self.chapter_id
        mock_loop.started_at = datetime.now() - timedelta(minutes=30)
        mock_loop.completed_at = datetime.now()
        mock_loop.get_conversations.return_value = mock_conversations
        mock_loop.get_performance_metrics.return_value = {
            'duration_minutes': 30,
            'quiz_attempts_count': 2,
            'quiz_success_rate': 80.0
        }
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_loop
        mock_learning_loop.query = mock_query
        
        # 테스트 실행
        summary = self.loop_service.generate_loop_summary("test_loop_123")
        
        # 검증
        self.assertIsInstance(summary, str)
        self.assertIn("test_loop", summary)
        self.assertIn("챕터", summary)
        self.assertIn("대화 수", summary)
    
    def test_optimize_state_size(self):
        """State 크기 최적화 테스트"""
        # 많은 대화로 State 채우기
        conversations = []
        for i in range(60):  # 50개 초과
            conv = {
                'agent_name': f'Agent{i % 3}',
                'user_message': f'메시지 {i}',
                'system_response': f'응답 {i}',
                'ui_elements': None,
                'timestamp': datetime.now().isoformat(),
                'sequence_order': i + 1
            }
            conversations.append(conv)
        
        self.test_state['current_loop_conversations'] = conversations
        
        # 테스트 실행
        optimized_state = self.loop_service.optimize_state_size(self.test_state)
        
        # 검증
        self.assertLessEqual(len(optimized_state['current_loop_conversations']), 31)  # 요약 + 30개
        
        # 첫 번째 대화가 요약인지 확인
        first_conv = optimized_state['current_loop_conversations'][0]
        self.assertEqual(first_conv['agent_name'], 'system')
        self.assertIn('[이전 대화 요약]', first_conv['system_response'])
    
    def test_compress_conversations(self):
        """대화 압축 테스트"""
        # 테스트 대화 데이터
        conversations = [
            {
                'user_message': '첫 번째 질문입니다',
                'system_response': None,
                'agent_name': 'user'
            },
            {
                'user_message': None,
                'system_response': '첫 번째 답변입니다',
                'agent_name': 'TheoryEducator'
            },
            {
                'user_message': '두 번째 질문입니다',
                'system_response': None,
                'agent_name': 'user'
            }
        ]
        
        # 테스트 실행
        compressed = self.loop_service._compress_conversations(conversations)
        
        # 검증
        self.assertIsInstance(compressed, str)
        self.assertIn('질문', compressed)
        self.assertIn('응답', compressed)
    
    @patch('services.loop_service.LearningLoop')
    def test_get_loop_statistics(self, mock_learning_loop):
        """루프 통계 조회 테스트"""
        # Mock 루프 데이터
        mock_loops = []
        for i in range(5):
            loop = Mock()
            loop.loop_status = 'completed' if i < 4 else 'abandoned'
            loop.duration_minutes = 20 + i * 5
            loop.interaction_count = 8 + i
            loop.started_at = datetime.now() - timedelta(days=i)
            mock_loops.append(loop)
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_loops
        mock_learning_loop.query = mock_query
        
        # 테스트 실행
        stats = self.loop_service.get_loop_statistics(
            user_id=self.user_id,
            chapter_id=self.chapter_id,
            days=30
        )
        
        # 검증
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_loops'], 5)
        self.assertEqual(stats['completed_loops'], 4)
        self.assertEqual(stats['abandoned_loops'], 1)
        self.assertEqual(stats['completion_rate'], 80.0)
        self.assertIn('daily_activity', stats)
    
    def test_get_loop_context_for_state(self):
        """State용 루프 컨텍스트 조회 테스트"""
        with patch('services.loop_service.LearningLoop') as mock_learning_loop:
            # Mock 최근 요약
            mock_learning_loop.get_recent_loops_summary.return_value = [
                {
                    'loop_id': 'loop1',
                    'summary': '첫 번째 루프 요약',
                    'completed_at': datetime.now().isoformat()
                }
            ]
            
            # Mock 현재 루프
            mock_current_loop = Mock()
            mock_current_loop.get_conversations.return_value = []
            
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_current_loop
            mock_learning_loop.query = mock_query
            
            # 테스트 실행
            context = self.loop_service.get_loop_context_for_state(
                user_id=self.user_id,
                chapter_id=self.chapter_id,
                current_loop_id="current_loop_123"
            )
            
            # 검증
            self.assertIn('recent_loops_summary', context)
            self.assertIn('current_loop_conversations', context)
            self.assertEqual(len(context['recent_loops_summary']), 1)
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        # 존재하지 않는 루프 완료 시도
        with patch('services.loop_service.LearningLoop') as mock_learning_loop:
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = None  # 루프 없음
            mock_learning_loop.query = mock_query
            
            # 예외 발생 확인
            with self.assertRaises(ValueError):
                self.loop_service.complete_loop("nonexistent_loop")

if __name__ == '__main__':
    unittest.main()