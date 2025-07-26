# tests/unit/test_progress_service.py
# 진도 추적 서비스 단위 테스트

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.progress_service import ProgressService
from models.user import UserLearningProgress
from models.learning_loop import LearningLoop
from models.quiz_attempt import QuizAttempt

class TestProgressService(unittest.TestCase):
    """진도 추적 서비스 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.progress_service = ProgressService()
        self.user_id = 1
        self.chapter_id = 1
    
    @patch('services.progress_service.UserLearningProgress')
    @patch('services.progress_service.LearningLoop')
    def test_calculate_chapter_progress(self, mock_learning_loop, mock_progress):
        """챕터 진도 계산 테스트"""
        # Mock 데이터 설정
        mock_progress_instance = Mock()
        mock_progress_instance.progress_percentage = 75.0
        mock_progress_instance.understanding_score = 85.0
        mock_progress_instance.study_time_minutes = 120
        mock_progress_instance.last_studied = datetime.now()
        mock_progress_instance.is_completed = False
        mock_progress_instance.completed_at = None
        
        mock_progress.get_or_create.return_value = mock_progress_instance
        
        # Mock 루프 데이터
        mock_loop = Mock()
        mock_loop.interaction_count = 10
        mock_loop.duration_minutes = 25
        mock_loop.get_conversations.return_value = []
        mock_loop.get_performance_metrics.return_value = {
            'duration_minutes': 25,
            'interaction_count': 10,
            'quiz_success_rate': 80.0
        }
        
        mock_learning_loop.get_user_loops.return_value = [mock_loop]
        
        # 테스트 실행
        result = self.progress_service.calculate_chapter_progress(self.user_id, self.chapter_id)
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], self.user_id)
        self.assertEqual(result['chapter_id'], self.chapter_id)
        self.assertEqual(result['progress_percentage'], 75.0)
        self.assertEqual(result['understanding_score'], 85.0)
        self.assertEqual(result['loops_completed'], 1)
    
    @patch('services.progress_service.UserLearningProgress')
    def test_update_chapter_progress(self, mock_progress):
        """챕터 진도 업데이트 테스트"""
        # Mock 데이터 설정
        mock_progress_instance = Mock()
        mock_progress_instance.progress_percentage = 50.0
        mock_progress_instance.understanding_score = 70.0
        mock_progress_instance.study_time_minutes = 60
        mock_progress_instance.is_completed = False
        mock_progress_instance.save = Mock()
        
        mock_progress.get_or_create.return_value = mock_progress_instance
        
        # 테스트 실행
        result = self.progress_service.update_chapter_progress(
            user_id=self.user_id,
            chapter_id=self.chapter_id,
            progress_increment=25.0,
            understanding_score=80.0,
            study_time_minutes=30
        )
        
        # 검증
        self.assertEqual(mock_progress_instance.progress_percentage, 75.0)
        self.assertEqual(mock_progress_instance.understanding_score, 73.0)  # 가중 평균
        self.assertEqual(mock_progress_instance.study_time_minutes, 90)
        mock_progress_instance.save.assert_called_once()
    
    @patch('services.progress_service.QuizAttempt')
    @patch('services.progress_service.LearningLoop')
    def test_calculate_understanding_score(self, mock_learning_loop, mock_quiz_attempt):
        """이해도 점수 계산 테스트"""
        # Mock 퀴즈 시도 데이터
        mock_attempts = []
        for i in range(3):
            attempt = Mock()
            attempt.score = 80 + i * 5  # 80, 85, 90
            attempt.is_correct = True
            attempt.hint_used = i == 0  # 첫 번째만 힌트 사용
            attempt.attempted_at = datetime.now() - timedelta(days=i)
            mock_attempts.append(attempt)
        
        mock_query = Mock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_attempts
        
        mock_quiz_attempt.query = mock_query
        
        # 테스트 실행
        score = self.progress_service.calculate_understanding_score(self.user_id, self.chapter_id)
        
        # 검증
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    @patch('services.progress_service.LearningLoop')
    def test_get_learning_statistics(self, mock_learning_loop):
        """학습 통계 조회 테스트"""
        # Mock 루프 데이터
        mock_loops = []
        for i in range(5):
            loop = Mock()
            loop.loop_status = 'completed'
            loop.duration_minutes = 20 + i * 5
            loop.interaction_count = 8 + i
            loop.started_at = datetime.now() - timedelta(days=i)
            loop.chapter_id = self.chapter_id
            mock_loops.append(loop)
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_loops
        
        mock_learning_loop.query = mock_query
        
        # 테스트 실행
        stats = self.progress_service.get_learning_statistics(
            user_id=self.user_id,
            chapter_id=self.chapter_id,
            days=30
        )
        
        # 검증
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_loops'], 5)
        self.assertEqual(stats['completed_loops'], 5)
        self.assertEqual(stats['completion_rate'], 100.0)
        self.assertIn('daily_activity', stats)
        self.assertIn('learning_efficiency', stats)
    
    def test_calculate_learning_efficiency(self):
        """학습 효율성 계산 테스트"""
        # Mock 루프 데이터
        mock_loops = []
        for i in range(3):
            loop = Mock()
            loop.loop_status = 'completed'
            loop.duration_minutes = 20  # 적절한 범위
            loop.interaction_count = 10  # 적절한 범위
            mock_loops.append(loop)
        
        # 테스트 실행
        efficiency = self.progress_service._calculate_learning_efficiency(mock_loops)
        
        # 검증
        self.assertIsInstance(efficiency, float)
        self.assertGreaterEqual(efficiency, 0)
        self.assertLessEqual(efficiency, 100)
    
    def test_calculate_learning_consistency(self):
        """학습 일관성 계산 테스트"""
        # Mock 루프 데이터 (일관된 간격)
        mock_loops = []
        base_time = datetime.now()
        for i in range(5):
            loop = Mock()
            loop.started_at = base_time - timedelta(hours=i * 24)  # 매일 같은 시간
            mock_loops.append(loop)
        
        # 테스트 실행
        consistency = self.progress_service._calculate_learning_consistency(mock_loops)
        
        # 검증
        self.assertIsInstance(consistency, float)
        self.assertGreaterEqual(consistency, 0)
        self.assertLessEqual(consistency, 100)
    
    @patch('services.progress_service.UserLearningProgress')
    @patch('services.progress_service.LearningLoop')
    def test_generate_progress_recommendations(self, mock_learning_loop, mock_progress):
        """진도 기반 추천사항 생성 테스트"""
        # Mock 진도 데이터
        mock_progress_instance = Mock()
        mock_progress_instance.progress_percentage = 45.0  # 중간 진도
        mock_progress_instance.understanding_score = 65.0  # 낮은 이해도
        
        mock_progress.get_or_create.return_value = mock_progress_instance
        mock_learning_loop.get_user_loops.return_value = []
        
        # 테스트 실행
        recommendations = self.progress_service._generate_progress_recommendations(
            self.user_id, self.chapter_id
        )
        
        # 검증
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 3)  # 최대 3개
        
        # 낮은 이해도에 대한 추천이 포함되어야 함
        recommendation_text = ' '.join(recommendations)
        self.assertIn('복습', recommendation_text)
    
    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        # 빈 루프 리스트로 테스트
        efficiency = self.progress_service._calculate_learning_efficiency([])
        consistency = self.progress_service._calculate_learning_consistency([])
        avg_duration = self.progress_service._calculate_average_loop_duration([])
        
        # 검증
        self.assertEqual(efficiency, 0.0)
        self.assertEqual(consistency, 100.0)  # 빈 데이터는 일관성 높음으로 간주
        self.assertEqual(avg_duration, 0.0)

if __name__ == '__main__':
    unittest.main()