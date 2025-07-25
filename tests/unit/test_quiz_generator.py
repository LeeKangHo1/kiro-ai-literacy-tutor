# tests/unit/test_quiz_generator.py
# QuizGenerator 에이전트 테스트

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.quiz.question_generator import QuestionGenerator
from agents.quiz.hint_generator import HintGenerator
from agents.quiz.difficulty_manager import DifficultyManager
from agents.quiz import QuizGenerator, create_quiz_generator
from tools.content.quiz_tool import quiz_generation_tool, validate_quiz_answer
from tools.content.hint_tool import hint_generation_tool


class TestQuestionGenerator:
    """QuestionGenerator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.generator = QuestionGenerator()
    
    def test_generate_multiple_choice_question_basic(self):
        """기본 객관식 문제 생성 테스트"""
        result = self.generator.generate_multiple_choice_question(
            chapter_id=1,
            user_level="medium",
            user_type="beginner"
        )
        
        assert result is not None
        assert "question_id" in result
        assert "question_type" in result
        assert result["question_type"] == "multiple_choice"
        assert "question_text" in result
        assert "options" in result
        assert "correct_answer" in result
        assert isinstance(result["options"], list)
        assert len(result["options"]) > 0
        assert isinstance(result["correct_answer"], int)
        assert 0 <= result["correct_answer"] < len(result["options"])
    
    def test_generate_multiple_choice_question_different_levels(self):
        """다양한 사용자 레벨에 대한 객관식 문제 생성 테스트"""
        levels = ["low", "medium", "high"]
        
        for level in levels:
            result = self.generator.generate_multiple_choice_question(
                chapter_id=1,
                user_level=level,
                user_type="beginner"
            )
            
            assert result["user_level"] == level
            assert "question_text" in result
            assert len(result["options"]) >= 2
    
    def test_generate_prompt_question_basic(self):
        """기본 프롬프트 문제 생성 테스트"""
        result = self.generator.generate_prompt_question(
            chapter_id=3,
            user_level="medium",
            user_type="business"
        )
        
        assert result is not None
        assert "question_id" in result
        assert "question_type" in result
        assert result["question_type"] == "prompt_practice"
        assert "scenario" in result
        assert "task_description" in result
        assert "requirements" in result
        assert isinstance(result["requirements"], list)
    
    def test_generate_prompt_question_different_types(self):
        """다양한 사용자 유형에 대한 프롬프트 문제 생성 테스트"""
        user_types = ["beginner", "business"]
        
        for user_type in user_types:
            result = self.generator.generate_prompt_question(
                chapter_id=3,
                user_level="medium",
                user_type=user_type
            )
            
            assert result["user_type"] == user_type
            assert "scenario" in result
            assert "task_description" in result


class TestHintGenerator:
    """HintGenerator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.generator = HintGenerator()
    
    def test_generate_multiple_choice_hint(self):
        """객관식 문제 힌트 생성 테스트"""
        question_data = {
            "question_id": "test_mc_1",
            "question_type": "multiple_choice",
            "chapter_id": 1,
            "question_text": "AI가 무엇의 줄임말인가요?",
            "options": ["Artificial Intelligence", "Advanced Internet", "Automatic Information", "Applied Integration"],
            "correct_answer": 0,
            "explanation": "AI는 Artificial Intelligence의 줄임말입니다."
        }
        
        # 레벨 1 힌트
        hint_result = self.generator.generate_hint(question_data, hint_level=1, user_level="medium")
        
        assert hint_result is not None
        assert "hint_id" in hint_result
        assert "hint_level" in hint_result
        assert hint_result["hint_level"] == 1
        assert "hint_text" in hint_result
        assert "hint_type" in hint_result
        assert hint_result["hint_type"] == "multiple_choice"
    
    def test_generate_prompt_hint(self):
        """프롬프트 문제 힌트 생성 테스트"""
        question_data = {
            "question_id": "test_prompt_1",
            "question_type": "prompt_practice",
            "chapter_id": 3,
            "scenario": "온라인 쇼핑몰 고객 서비스",
            "task_description": "고객의 불만사항을 해결하는 프롬프트를 작성하세요.",
            "requirements": ["친근한 톤 사용", "구체적인 해결책 제시"]
        }
        
        hint_result = self.generator.generate_hint(question_data, hint_level=2, user_level="medium")
        
        assert hint_result is not None
        assert hint_result["hint_level"] == 2
        assert hint_result["hint_type"] == "prompt_practice"
        assert len(hint_result["hint_text"]) > 0
    
    def test_hint_level_progression(self):
        """힌트 레벨 진행 테스트"""
        question_data = {
            "question_id": "test_progression",
            "question_type": "multiple_choice",
            "chapter_id": 1,
            "question_text": "테스트 문제",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0
        }
        
        # 각 레벨별 힌트 생성
        for level in [1, 2, 3]:
            hint_result = self.generator.generate_hint(question_data, hint_level=level)
            assert hint_result["hint_level"] == level
            assert len(hint_result["hint_text"]) > 0


class TestDifficultyManager:
    """DifficultyManager 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.manager = DifficultyManager()
    
    def test_calculate_current_difficulty_no_performance(self):
        """성과 데이터가 없을 때 난이도 계산 테스트"""
        difficulty = self.manager.calculate_current_difficulty("user1", 1, [])
        assert difficulty == "medium"  # 기본 난이도
    
    def test_calculate_current_difficulty_with_performance(self):
        """성과 데이터가 있을 때 난이도 계산 테스트"""
        # 높은 성과 데이터
        high_performance = [
            {"is_correct": True, "hint_used": False, "response_time": 30},
            {"is_correct": True, "hint_used": False, "response_time": 25},
            {"is_correct": True, "hint_used": False, "response_time": 35}
        ]
        
        difficulty = self.manager.calculate_current_difficulty("user1", 1, high_performance)
        assert difficulty in ["medium", "hard"]  # 성과에 따라 medium 이상
        
        # 낮은 성과 데이터
        low_performance = [
            {"is_correct": False, "hint_used": True, "response_time": 120},
            {"is_correct": False, "hint_used": True, "response_time": 150},
            {"is_correct": True, "hint_used": True, "response_time": 100}
        ]
        
        difficulty = self.manager.calculate_current_difficulty("user1", 1, low_performance)
        assert difficulty in ["easy", "medium"]  # 성과에 따라 medium 이하
    
    def test_adjust_difficulty_based_on_answer(self):
        """답변 결과에 따른 난이도 조정 테스트"""
        # 정답이고 힌트 미사용 시 난이도 상승
        new_difficulty = self.manager.adjust_difficulty_based_on_answer(
            current_difficulty="medium",
            is_correct=True,
            hint_used=False,
            response_time_seconds=25
        )
        assert new_difficulty in ["medium", "hard"]
        
        # 오답이거나 힌트 사용 시 난이도 하락
        new_difficulty = self.manager.adjust_difficulty_based_on_answer(
            current_difficulty="medium",
            is_correct=False,
            hint_used=True
        )
        assert new_difficulty in ["easy", "medium"]
    
    def test_get_difficulty_parameters(self):
        """난이도별 파라미터 반환 테스트"""
        params = self.manager.get_difficulty_parameters("easy", "multiple_choice")
        assert "concept_complexity" in params
        assert params["concept_complexity"] == "basic"
        
        params = self.manager.get_difficulty_parameters("hard", "prompt_practice")
        assert "task_complexity" in params
        assert params["task_complexity"] == "complex"
    
    def test_should_provide_hint(self):
        """힌트 제공 여부 결정 테스트"""
        # easy 난이도에서 2번 시도 후 힌트 제공
        should_provide = self.manager.should_provide_hint("easy", 2)
        assert should_provide == True
        
        # hard 난이도에서 1번 시도 후 힌트 제공
        should_provide = self.manager.should_provide_hint("hard", 1)
        assert should_provide == True
        
        # medium 난이도에서 첫 시도는 힌트 제공 (attempts threshold가 1이므로)
        should_provide = self.manager.should_provide_hint("medium", 1, 30)
        assert should_provide == True


class TestQuizGenerator:
    """QuizGenerator 에이전트 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.agent = QuizGenerator()
    
    def test_agent_creation(self):
        """에이전트 생성 테스트"""
        assert self.agent.agent_name == "QuizGenerator"
        assert hasattr(self.agent, 'question_generator')
        assert hasattr(self.agent, 'hint_generator')
        assert hasattr(self.agent, 'difficulty_manager')
    
    def test_execute_multiple_choice_request(self):
        """객관식 문제 요청 실행 테스트"""
        state = {
            "user_message": "객관식 문제를 내주세요",
            "current_chapter": 1,
            "user_level": "medium",
            "user_type": "beginner",
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        result_state = self.agent.execute(state)
        
        assert "system_message" in result_state
        assert "ui_elements" in result_state
        assert result_state["ui_mode"] == "quiz"
        assert result_state["current_stage"] == "quiz_solving"
        assert len(result_state["current_loop_conversations"]) > 0
    
    def test_execute_prompt_request(self):
        """프롬프트 문제 요청 실행 테스트"""
        state = {
            "user_message": "프롬프트 작성 문제를 내주세요",
            "current_chapter": 3,
            "user_level": "medium",
            "user_type": "business",
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        result_state = self.agent.execute(state)
        
        assert "system_message" in result_state
        assert "ui_elements" in result_state
        assert result_state["ui_mode"] == "quiz"
        assert "프롬프트" in result_state["system_message"]
    
    def test_handle_hint_request(self):
        """힌트 요청 처리 테스트"""
        # 먼저 퀴즈를 생성한 상태 설정
        state = {
            "user_id": "test_user",
            "user_level": "medium",
            "quiz_attempt_count": 1,
            "current_loop_conversations": [
                {
                    "agent": "QuizGenerator",
                    "quiz_data": {
                        "question_id": "test_q1",
                        "question_type": "multiple_choice",
                        "question_text": "테스트 문제",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0
                    }
                }
            ]
        }
        
        result_state = self.agent.handle_hint_request(state)
        
        assert "system_message" in result_state
        assert "💡" in result_state["system_message"]
        assert result_state.get("hint_used") == True
        assert "last_hint_level" in result_state


class TestQuizTools:
    """퀴즈 도구 테스트"""
    
    def test_quiz_generation_tool_multiple_choice(self):
        """객관식 퀴즈 생성 도구 테스트"""
        result = quiz_generation_tool(
            chapter_id=1,
            user_level="medium",
            user_type="beginner",
            quiz_type="multiple_choice"
        )
        
        assert result["success"] == True
        assert "quiz_data" in result
        assert "ui_elements" in result
        assert result["quiz_data"]["question_type"] == "multiple_choice"
    
    def test_quiz_generation_tool_prompt_practice(self):
        """프롬프트 실습 퀴즈 생성 도구 테스트"""
        result = quiz_generation_tool(
            chapter_id=3,
            user_level="medium",
            user_type="business",
            quiz_type="prompt_practice"
        )
        
        assert result["success"] == True
        assert result["quiz_data"]["question_type"] == "prompt_practice"
        assert "scenario" in result["quiz_data"]
        assert "requirements" in result["quiz_data"]
    
    def test_validate_quiz_answer_multiple_choice(self):
        """객관식 답변 검증 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1,
            "explanation": "정답은 B입니다."
        }
        
        # 정답 검증
        result = validate_quiz_answer(question_data, 1, hint_used=False, response_time=45)
        assert result["is_valid"] == True
        assert result["is_correct"] == True
        assert result["score"] > 0
        
        # 오답 검증
        result = validate_quiz_answer(question_data, 0, hint_used=True, response_time=120)
        assert result["is_valid"] == True
        assert result["is_correct"] == False
        assert result["score"] == 0
    
    def test_validate_quiz_answer_prompt_practice(self):
        """프롬프트 답변 검증 테스트"""
        question_data = {
            "question_type": "prompt_practice",
            "requirements": ["친근한 톤 사용", "구체적인 해결책 제시"]
        }
        
        # 유효한 프롬프트
        valid_prompt = "당신은 친근한 고객서비스 담당자입니다. 고객의 문제를 구체적으로 해결해주세요."
        result = validate_quiz_answer(question_data, valid_prompt, hint_used=False)
        
        assert result["is_valid"] == True
        assert "requirements_met" in result
        assert result["needs_evaluation"] == True
        
        # 너무 짧은 프롬프트
        short_prompt = "안녕하세요"
        result = validate_quiz_answer(question_data, short_prompt)
        
        assert result["is_valid"] == False
        assert "너무 짧습니다" in result["error"]


class TestHintTools:
    """힌트 도구 테스트"""
    
    def test_hint_generation_tool(self):
        """힌트 생성 도구 테스트"""
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "question_text": "테스트 문제",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1
        }
        
        result = hint_generation_tool(
            question_data=question_data,
            hint_level=1,
            user_level="medium",
            attempt_count=2
        )
        
        assert result["success"] == True
        assert "hint_data" in result
        assert "ui_elements" in result
        assert result["hint_data"]["hint_level"] == 1
    
    def test_hint_generation_tool_early_attempt(self):
        """초기 시도에서 힌트 요청 테스트"""
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice",
            "difficulty": "medium"
        }
        
        result = hint_generation_tool(
            question_data=question_data,
            hint_level=1,
            attempt_count=1,
            time_spent=20
        )
        
        # medium 난이도에서 첫 시도도 힌트 제공 (attempts threshold가 1이므로)
        assert result["success"] == True
        assert "hint_data" in result
        # 성공한 경우이므로 should_retry는 없음
        assert "hint_data" in result


def test_create_quiz_generator():
    """QuizGenerator 생성 함수 테스트"""
    agent = create_quiz_generator()
    assert isinstance(agent, QuizGenerator)
    assert agent.agent_name == "QuizGenerator"


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 코드
    pytest.main([__file__, "-v"])