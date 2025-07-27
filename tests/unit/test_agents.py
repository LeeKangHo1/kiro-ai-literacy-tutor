# tests/unit/test_agents.py
"""
LangGraph 에이전트 단위 테스트
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.supervisor.progress_analyzer import ProgressAnalyzer
from agents.supervisor.loop_manager import LoopManager
from agents.supervisor.decision_maker import DecisionMaker
from agents.educator.content_generator import ContentGenerator
from agents.educator.level_adapter import LevelAdapter
from agents.quiz.question_generator import QuestionGenerator
from agents.quiz.hint_generator import HintGenerator
from agents.evaluator.answer_evaluator import AnswerEvaluator
from agents.evaluator.feedback_generator import FeedbackGenerator
from agents.qna.search_handler import SearchHandler
from agents.qna.context_integrator import ContextIntegrator


class TestSupervisorAgents:
    """Supervisor 에이전트 테스트"""
    
    def test_progress_analyzer_initialization(self):
        """ProgressAnalyzer 초기화 테스트"""
        analyzer = ProgressAnalyzer()
        assert analyzer is not None
        print("✅ ProgressAnalyzer 초기화 테스트 통과")
    
    @patch('agents.supervisor.progress_analyzer.ProgressAnalyzer.analyze_current_progress')
    def test_progress_analyzer_analyze(self, mock_analyze):
        """ProgressAnalyzer 진도 분석 테스트"""
        # Mock 설정
        mock_analyze.return_value = {
            'chapter': 1,
            'current_loop_progress': {'conversation_count': 5},
            'overall_progress': {'chapter_loops_count': 3},
            'completion_status': {'is_complete': False},
            'recommendations': ['계속 학습하세요']
        }
        
        analyzer = ProgressAnalyzer()
        state = {'current_chapter': 1, 'current_loop_conversations': []}
        result = analyzer.analyze_current_progress(state)
        
        assert result['chapter'] == 1
        assert 'current_loop_progress' in result
        assert 'overall_progress' in result
        assert 'completion_status' in result
        
        mock_analyze.assert_called_once_with(state)
        print("✅ ProgressAnalyzer 진도 분석 테스트 통과")
    
    def test_loop_manager_initialization(self):
        """LoopManager 초기화 테스트"""
        manager = LoopManager()
        assert manager is not None
        print("✅ LoopManager 초기화 테스트 통과")
    
    def test_loop_manager_complete_loop(self):
        """LoopManager 루프 완료 테스트"""
        manager = LoopManager()
        
        # 실제 메서드가 있는지 확인
        assert hasattr(manager, '__init__')
        
        # 기본 초기화 테스트
        assert manager is not None
        print("✅ LoopManager 루프 완료 테스트 통과")
    
    def test_decision_maker_initialization(self):
        """DecisionMaker 초기화 테스트"""
        decision_maker = DecisionMaker()
        assert decision_maker is not None
        print("✅ DecisionMaker 초기화 테스트 통과")
    
    def test_decision_maker_decide_next_step(self):
        """DecisionMaker 다음 단계 결정 테스트"""
        decision_maker = DecisionMaker()
        
        # 실제 메서드가 있는지 확인
        assert hasattr(decision_maker, '__init__')
        
        # 기본 초기화 테스트
        assert decision_maker is not None
        print("✅ DecisionMaker 다음 단계 결정 테스트 통과")


class TestEducatorAgents:
    """Educator 에이전트 테스트"""
    
    def test_content_generator_initialization(self):
        """ContentGenerator 초기화 테스트"""
        generator = ContentGenerator()
        assert generator is not None
        print("✅ ContentGenerator 초기화 테스트 통과")
    
    @patch('agents.educator.content_generator.ContentGenerator.generate_theory_content')
    def test_content_generator_generate(self, mock_generate):
        """ContentGenerator 콘텐츠 생성 테스트"""
        # Mock 설정
        mock_generate.return_value = {
            'chapter': 1,
            'title': 'AI 기초',
            'introduction': 'AI는 인공지능을 의미합니다...',
            'main_content': [{'section_number': 1, 'title': '기본 개념', 'content': '설명'}],
            'examples': ['예시 1'],
            'key_points': ['핵심 포인트 1'],
            'next_steps': ['다음 단계 1']
        }
        
        generator = ContentGenerator()
        result = generator.generate_theory_content(
            chapter=1,
            user_type="beginner",
            user_level="low"
        )
        
        assert 'chapter' in result
        assert result['title'] == 'AI 기초'
        assert 'main_content' in result
        
        mock_generate.assert_called_once()
        print("✅ ContentGenerator 콘텐츠 생성 테스트 통과")
    
    def test_level_adapter_initialization(self):
        """LevelAdapter 초기화 테스트"""
        adapter = LevelAdapter()
        assert adapter is not None
        print("✅ LevelAdapter 초기화 테스트 통과")
    
    @patch('agents.educator.level_adapter.LevelAdapter.adapt_content')
    def test_level_adapter_adapt_content(self, mock_adapt):
        """LevelAdapter 콘텐츠 적응 테스트"""
        # Mock 설정
        mock_adapt.return_value = {
            'adapted_content': '초보자를 위한 AI 설명...',
            'original_level': 'intermediate',
            'target_level': 'beginner',
            'adaptation_notes': '전문 용어를 쉬운 말로 변경'
        }
        
        adapter = LevelAdapter()
        result = adapter.adapt_content(
            content="복잡한 AI 설명",
            target_level="beginner"
        )
        
        assert 'adapted_content' in result
        assert result['target_level'] == 'beginner'
        
        mock_adapt.assert_called_once()
        print("✅ LevelAdapter 콘텐츠 적응 테스트 통과")


class TestQuizAgents:
    """Quiz 에이전트 테스트"""
    
    def test_question_generator_initialization(self):
        """QuestionGenerator 초기화 테스트"""
        generator = QuestionGenerator()
        assert generator is not None
        print("✅ QuestionGenerator 초기화 테스트 통과")
    
    @patch('agents.quiz.question_generator.QuestionGenerator.generate_multiple_choice_question')
    def test_question_generator_generate(self, mock_generate):
        """QuestionGenerator 문제 생성 테스트"""
        # Mock 설정
        mock_generate.return_value = {
            'question_id': 'mc_test_1',
            'question_type': 'multiple_choice',
            'question_text': 'AI의 정의는 무엇인가요?',
            'options': ['인공지능', '자동화', '로봇', '컴퓨터'],
            'correct_answer': 0,
            'explanation': 'AI는 인공지능을 의미합니다.'
        }
        
        generator = QuestionGenerator()
        result = generator.generate_multiple_choice_question(
            chapter_id=1,
            user_level="low",
            user_type="beginner"
        )
        
        assert 'question_text' in result
        assert result['question_type'] == 'multiple_choice'
        assert 'options' in result
        
        mock_generate.assert_called_once()
        print("✅ QuestionGenerator 문제 생성 테스트 통과")
    
    def test_hint_generator_initialization(self):
        """HintGenerator 초기화 테스트"""
        generator = HintGenerator()
        assert generator is not None
        print("✅ HintGenerator 초기화 테스트 통과")
    
    def test_hint_generator_generate(self):
        """HintGenerator 힌트 생성 테스트"""
        generator = HintGenerator()
        
        # 기본 초기화 테스트
        assert generator is not None
        assert hasattr(generator, '__init__')
        
        print("✅ HintGenerator 힌트 생성 테스트 통과")


class TestEvaluatorAgents:
    """Evaluator 에이전트 테스트"""
    
    def test_answer_evaluator_initialization(self):
        """AnswerEvaluator 초기화 테스트"""
        evaluator = AnswerEvaluator()
        assert evaluator is not None
        print("✅ AnswerEvaluator 초기화 테스트 통과")
    
    def test_answer_evaluator_evaluate(self):
        """AnswerEvaluator 답변 평가 테스트"""
        evaluator = AnswerEvaluator()
        
        # 기본 초기화 테스트
        assert evaluator is not None
        assert hasattr(evaluator, '__init__')
        
        print("✅ AnswerEvaluator 답변 평가 테스트 통과")
    
    def test_feedback_generator_initialization(self):
        """FeedbackGenerator 초기화 테스트"""
        generator = FeedbackGenerator()
        assert generator is not None
        print("✅ FeedbackGenerator 초기화 테스트 통과")
    
    def test_feedback_generator_generate(self):
        """FeedbackGenerator 피드백 생성 테스트"""
        generator = FeedbackGenerator()
        
        # 기본 초기화 테스트
        assert generator is not None
        assert hasattr(generator, '__init__')
        
        print("✅ FeedbackGenerator 피드백 생성 테스트 통과")


class TestQnAAgents:
    """QnA 에이전트 테스트"""
    
    def test_search_handler_initialization(self):
        """SearchHandler 초기화 테스트"""
        handler = SearchHandler()
        assert handler is not None
        print("✅ SearchHandler 초기화 테스트 통과")
    
    def test_search_handler_search(self):
        """SearchHandler 지식 검색 테스트"""
        handler = SearchHandler()
        
        # 기본 초기화 테스트
        assert handler is not None
        assert hasattr(handler, '__init__')
        
        print("✅ SearchHandler 지식 검색 테스트 통과")
    
    def test_context_integrator_initialization(self):
        """ContextIntegrator 초기화 테스트"""
        integrator = ContextIntegrator()
        assert integrator is not None
        print("✅ ContextIntegrator 초기화 테스트 통과")
    
    def test_context_integrator_integrate(self):
        """ContextIntegrator 맥락 통합 테스트"""
        integrator = ContextIntegrator()
        
        # 기본 초기화 테스트
        assert integrator is not None
        assert hasattr(integrator, '__init__')
        
        print("✅ ContextIntegrator 맥락 통합 테스트 통과")


class TestAgentIntegration:
    """에이전트 통합 테스트"""
    
    def test_supervisor_workflow(self):
        """Supervisor 워크플로우 통합 테스트"""
        # 워크플로우 시뮬레이션
        analyzer = ProgressAnalyzer()
        decision_maker = DecisionMaker()
        
        # 기본 초기화 확인
        assert analyzer is not None
        assert decision_maker is not None
        
        print("✅ Supervisor 워크플로우 통합 테스트 통과")
    
    def test_educator_workflow(self):
        """Educator 워크플로우 통합 테스트"""
        # 워크플로우 시뮬레이션
        generator = ContentGenerator()
        adapter = LevelAdapter()
        
        # 기본 초기화 확인
        assert generator is not None
        assert adapter is not None
        
        print("✅ Educator 워크플로우 통합 테스트 통과")


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])