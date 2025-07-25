# tests/unit/test_evaluation_feedback.py
# EvaluationFeedbackAgent 에이전트 테스트

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.evaluator.answer_evaluator import AnswerEvaluator, EvaluationResult
from agents.evaluator.feedback_generator import FeedbackGenerator
from agents.evaluator import EvaluationFeedbackAgent, create_evaluation_feedback_agent
from tools.evaluation.answer_eval_tool import (
    answer_evaluation_tool, 
    batch_evaluate_answers,
    calculate_learning_progress
)
from tools.evaluation.feedback_tool import (
    feedback_generation_tool,
    generate_quick_feedback,
    generate_adaptive_feedback
)


class TestAnswerEvaluator:
    """AnswerEvaluator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.evaluator = AnswerEvaluator()
    
    def test_evaluate_multiple_choice_correct_answer(self):
        """객관식 정답 평가 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1,
            "difficulty": "medium",
            "explanation": "정답은 B입니다."
        }
        
        result = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 1, hint_used=False, response_time=45
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.is_correct == True
        assert result.score > 0
        assert result.understanding_level in ["low", "medium", "high"]
        assert len(result.strengths) > 0
        assert "question_type" in result.detailed_analysis
    
    def test_evaluate_multiple_choice_wrong_answer(self):
        """객관식 오답 평가 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1,
            "difficulty": "medium",
            "explanation": "정답은 B입니다."
        }
        
        result = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 0, hint_used=True, response_time=120
        )
        
        assert result.is_correct == False
        assert result.score == 0
        assert result.understanding_level == "low"
        assert len(result.weaknesses) > 0
    
    def test_evaluate_multiple_choice_with_hint_penalty(self):
        """힌트 사용 시 점수 페널티 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1,
            "difficulty": "medium"
        }
        
        # 힌트 미사용
        result_no_hint = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 1, hint_used=False
        )
        
        # 힌트 사용
        result_with_hint = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 1, hint_used=True
        )
        
        assert result_no_hint.score > result_with_hint.score
        assert result_with_hint.detailed_analysis["hint_penalty"] < 0
    
    def test_evaluate_prompt_answer_good_quality(self):
        """고품질 프롬프트 평가 테스트"""
        question_data = {
            "question_type": "prompt_practice",
            "requirements": ["역할 정의", "친근한 톤", "구체적인 지시"],
            "evaluation_criteria": ["명확성", "완성도", "구조성"],
            "difficulty": "medium"
        }
        
        good_prompt = """
당신은 친근하고 전문적인 고객서비스 담당자입니다.
고객의 문의사항에 대해 다음과 같이 응답해주세요:

1. 먼저 고객의 상황을 공감하며 인사
2. 문제 상황을 구체적으로 파악
3. 단계별 해결 방안 제시
4. 추가 도움이 필요한지 확인

응답은 친근하면서도 전문적인 톤으로 작성해주세요.
        """.strip()
        
        result = self.evaluator.evaluate_prompt_answer(
            question_data, good_prompt, hint_used=False, response_time=180
        )
        
        assert result.is_correct == True  # 70점 이상
        assert result.score >= 70
        assert result.understanding_level in ["medium", "high"]
        assert len(result.strengths) > 0
    
    def test_evaluate_prompt_answer_poor_quality(self):
        """저품질 프롬프트 평가 테스트"""
        question_data = {
            "question_type": "prompt_practice",
            "requirements": ["역할 정의", "친근한 톤", "구체적인 지시"],
            "evaluation_criteria": ["명확성", "완성도", "구조성"],
            "difficulty": "medium"
        }
        
        poor_prompt = "고객에게 답변해주세요."
        
        result = self.evaluator.evaluate_prompt_answer(
            question_data, poor_prompt, hint_used=True, response_time=300
        )
        
        assert result.is_correct == False  # 70점 미만
        assert result.score < 70
        assert result.understanding_level == "low"
        assert len(result.weaknesses) > 0
    
    def test_understanding_level_determination(self):
        """이해도 수준 결정 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0,
            "difficulty": "easy"
        }
        
        # 높은 이해도 (정답, 힌트 미사용, 빠른 응답)
        result = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 0, hint_used=False, response_time=20
        )
        assert result.understanding_level in ["medium", "high"]
        
        # 낮은 이해도 (오답)
        result = self.evaluator.evaluate_multiple_choice_answer(
            question_data, 1, hint_used=True, response_time=150
        )
        assert result.understanding_level == "low"


class TestFeedbackGenerator:
    """FeedbackGenerator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.generator = FeedbackGenerator()
    
    def test_generate_comprehensive_feedback_correct_answer(self):
        """정답에 대한 종합 피드백 생성 테스트"""
        evaluation_result = EvaluationResult(
            is_correct=True,
            score=85.0,
            understanding_level="high",
            strengths=["정답을 정확히 선택했습니다", "힌트 없이 해결했습니다"],
            weaknesses=[],
            detailed_analysis={"question_type": "multiple_choice", "difficulty": "medium"}
        )
        
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice",
            "difficulty": "medium"
        }
        
        user_profile = {
            "user_level": "medium",
            "user_type": "beginner"
        }
        
        learning_context = {
            "current_chapter": 1,
            "recent_performance": []
        }
        
        feedback = self.generator.generate_comprehensive_feedback(
            evaluation_result, question_data, user_profile, learning_context
        )
        
        assert "feedback_id" in feedback
        assert "main_feedback" in feedback
        assert "encouragement" in feedback
        assert "improvement_tips" in feedback
        assert "next_steps" in feedback
        assert "ui_elements" in feedback
        assert "🎉" in feedback["main_feedback"] or "✅" in feedback["main_feedback"]
    
    def test_generate_comprehensive_feedback_wrong_answer(self):
        """오답에 대한 종합 피드백 생성 테스트"""
        evaluation_result = EvaluationResult(
            is_correct=False,
            score=0.0,
            understanding_level="low",
            strengths=[],
            weaknesses=["정답을 선택하지 못했습니다", "힌트가 필요했습니다"],
            detailed_analysis={"question_type": "multiple_choice", "difficulty": "medium"}
        )
        
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "user_answer": 0,
            "correct_answer": 1,
            "options": ["A", "B", "C", "D"],
            "explanation": "정답은 B입니다."
        }
        
        user_profile = {
            "user_level": "medium",
            "user_type": "beginner"
        }
        
        learning_context = {
            "current_chapter": 1,
            "recent_performance": []
        }
        
        feedback = self.generator.generate_comprehensive_feedback(
            evaluation_result, question_data, user_profile, learning_context
        )
        
        assert "❌" in feedback["main_feedback"]
        assert len(feedback["improvement_tips"]) > 0
        assert feedback["next_steps"]["action"] == "review"
    
    def test_generate_prompt_feedback(self):
        """프롬프트 문제 피드백 생성 테스트"""
        evaluation_result = EvaluationResult(
            is_correct=True,
            score=75.0,
            understanding_level="medium",
            strengths=["요구사항을 잘 충족했습니다"],
            weaknesses=["프롬프트 구조 개선 필요"],
            detailed_analysis={
                "question_type": "prompt_practice",
                "requirements_score": 80,
                "quality_score": 70,
                "effectiveness_score": 75
            }
        )
        
        question_data = {
            "question_id": "test_prompt_1",
            "question_type": "prompt_practice"
        }
        
        user_profile = {"user_level": "medium", "user_type": "business"}
        learning_context = {"current_chapter": 3, "recent_performance": []}
        
        feedback = self.generator.generate_comprehensive_feedback(
            evaluation_result, question_data, user_profile, learning_context
        )
        
        assert "👍" in feedback["main_feedback"] or "📝" in feedback["main_feedback"]
        assert "요구사항 충족도" in feedback["main_feedback"]
        assert "프롬프트 품질" in feedback["main_feedback"]
    
    def test_personalized_message_generation(self):
        """개인화된 메시지 생성 테스트"""
        evaluation_result = EvaluationResult(
            is_correct=True,
            score=90.0,
            understanding_level="high",
            strengths=["완벽한 답변"],
            weaknesses=[],
            detailed_analysis={}
        )
        
        # 초보자 프로필
        beginner_profile = {"user_type": "beginner", "user_level": "medium"}
        # 비즈니스 프로필
        business_profile = {"user_type": "business", "user_level": "high"}
        
        question_data = {"question_type": "multiple_choice"}
        learning_context = {"recent_performance": []}
        
        beginner_feedback = self.generator.generate_comprehensive_feedback(
            evaluation_result, question_data, beginner_profile, learning_context
        )
        
        business_feedback = self.generator.generate_comprehensive_feedback(
            evaluation_result, question_data, business_profile, learning_context
        )
        
        # 사용자 유형에 따라 다른 메시지가 생성되는지 확인
        assert beginner_feedback["personalized_message"] != business_feedback["personalized_message"]


class TestEvaluationFeedbackAgent:
    """EvaluationFeedbackAgent 에이전트 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.agent = EvaluationFeedbackAgent()
    
    def test_agent_creation(self):
        """에이전트 생성 테스트"""
        assert self.agent.agent_name == "EvaluationFeedbackAgent"
        assert hasattr(self.agent, 'answer_evaluator')
        assert hasattr(self.agent, 'feedback_generator')
    
    def test_execute_with_multiple_choice_answer(self):
        """객관식 답변 처리 실행 테스트"""
        state = {
            "user_id": "test_user",
            "user_level": "medium",
            "user_type": "beginner",
            "current_chapter": 1,
            "user_answer": 1,
            "hint_used": False,
            "response_time": 45,
            "current_loop_conversations": [
                {
                    "agent": "QuizGenerator",
                    "quiz_data": {
                        "question_id": "test_q1",
                        "question_type": "multiple_choice",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 1,
                        "explanation": "정답은 B입니다."
                    }
                }
            ]
        }
        
        result_state = self.agent.execute(state)
        
        assert "system_message" in result_state
        assert "ui_elements" in result_state
        assert result_state["ui_mode"] == "feedback"
        assert result_state["current_stage"] == "feedback_review"
        assert "last_evaluation" in result_state
        assert "last_feedback" in result_state
        assert len(result_state["current_loop_conversations"]) > 1
    
    def test_execute_with_prompt_answer(self):
        """프롬프트 답변 처리 실행 테스트"""
        state = {
            "user_id": "test_user",
            "user_level": "medium",
            "user_type": "business",
            "current_chapter": 3,
            "user_answer": "당신은 친근한 고객서비스 담당자입니다. 고객의 문제를 해결해주세요.",
            "hint_used": False,
            "current_loop_conversations": [
                {
                    "agent": "QuizGenerator",
                    "quiz_data": {
                        "question_id": "test_prompt_1",
                        "question_type": "prompt_practice",
                        "scenario": "고객 서비스",
                        "requirements": ["친근한 톤", "구체적 해결책"]
                    }
                }
            ]
        }
        
        result_state = self.agent.execute(state)
        
        assert result_state["ui_mode"] == "feedback"
        assert "last_evaluation" in result_state
        assert "프롬프트" in result_state["system_message"] or "점수" in result_state["system_message"]
    
    def test_handle_chatgpt_test(self):
        """ChatGPT 테스트 처리 테스트"""
        state = {
            "user_id": "test_user"
        }
        
        test_prompt = "당신은 전문적인 AI 어시스턴트입니다. 사용자의 질문에 친절하게 답변해주세요."
        
        result_state = self.agent.handle_chatgpt_test(state, test_prompt)
        
        assert "chatgpt_test_result" in result_state
        assert "system_message" in result_state
        assert "ChatGPT 테스트 결과" in result_state["system_message"]
    
    def test_execute_without_quiz_data(self):
        """퀴즈 데이터가 없을 때 실행 테스트"""
        state = {
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        result_state = self.agent.execute(state)
        
        assert "평가할 문제나 답변을 찾을 수 없습니다" in result_state["system_message"]
        assert result_state["ui_mode"] == "chat"


class TestEvaluationTools:
    """평가 도구 테스트"""
    
    def test_answer_evaluation_tool_multiple_choice(self):
        """객관식 답변 평가 도구 테스트"""
        question_data = {
            "question_type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 1,
            "difficulty": "medium"
        }
        
        result = answer_evaluation_tool(
            question_data=question_data,
            user_answer=1,
            hint_used=False,
            response_time=45
        )
        
        assert result["success"] == True
        assert "evaluation_result" in result
        assert result["evaluation_result"]["is_correct"] == True
        assert result["evaluation_result"]["score"] > 0
    
    def test_answer_evaluation_tool_prompt_practice(self):
        """프롬프트 실습 답변 평가 도구 테스트"""
        question_data = {
            "question_type": "prompt_practice",
            "requirements": ["역할 정의", "친근한 톤"]
        }
        
        prompt_answer = "당신은 친근한 고객서비스 담당자입니다. 고객을 도와주세요."
        
        result = answer_evaluation_tool(
            question_data=question_data,
            user_answer=prompt_answer,
            hint_used=False
        )
        
        assert result["success"] == True
        assert result["evaluation_result"]["question_type"] == "prompt_practice"
        assert "requirements_analysis" in result["evaluation_result"]["detailed_analysis"]
    
    def test_batch_evaluate_answers(self):
        """일괄 답변 평가 테스트"""
        questions_and_answers = [
            {
                "question_data": {
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0
                },
                "user_answer": 0,
                "hint_used": False
            },
            {
                "question_data": {
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 1
                },
                "user_answer": 2,
                "hint_used": True
            }
        ]
        
        result = batch_evaluate_answers(questions_and_answers)
        
        assert result["success"] == True
        assert "batch_results" in result
        assert "statistics" in result
        assert len(result["batch_results"]) == 2
        assert result["statistics"]["total_questions"] == 2
        assert result["statistics"]["correct_count"] == 1
        assert result["statistics"]["accuracy_rate"] == 0.5
    
    def test_calculate_learning_progress(self):
        """학습 진도 계산 테스트"""
        evaluation_results = [
            {"is_correct": True, "score": 85, "understanding_level": "high"},
            {"is_correct": False, "score": 45, "understanding_level": "low"},
            {"is_correct": True, "score": 92, "understanding_level": "high"},
            {"is_correct": True, "score": 78, "understanding_level": "medium"}
        ]
        
        result = calculate_learning_progress("test_user", 1, evaluation_results)
        
        assert result["success"] == True
        assert "progress_data" in result
        progress = result["progress_data"]
        assert "completion_rate" in progress
        assert "average_score" in progress
        assert "accuracy_trend" in progress
        assert "understanding_trend" in progress


class TestFeedbackTools:
    """피드백 도구 테스트"""
    
    def test_feedback_generation_tool(self):
        """피드백 생성 도구 테스트"""
        evaluation_result = {
            "is_correct": True,
            "score": 85.0,
            "understanding_level": "high",
            "strengths": ["정답을 정확히 선택했습니다"],
            "weaknesses": [],
            "detailed_analysis": {"question_type": "multiple_choice"}
        }
        
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice"
        }
        
        user_profile = {
            "user_level": "medium",
            "user_type": "beginner"
        }
        
        learning_context = {
            "current_chapter": 1,
            "recent_performance": []
        }
        
        result = feedback_generation_tool(
            evaluation_result, question_data, user_profile, learning_context
        )
        
        assert result["success"] == True
        assert "feedback_data" in result
        assert "main_feedback" in result["feedback_data"]
        assert "encouragement" in result["feedback_data"]
    
    def test_generate_quick_feedback(self):
        """빠른 피드백 생성 테스트"""
        result = generate_quick_feedback(
            is_correct=True,
            score=90.0,
            question_type="multiple_choice",
            user_type="beginner"
        )
        
        assert result["success"] == True
        assert "feedback_data" in result
        assert result["feedback_data"]["is_correct"] == True
        assert "🎉" in result["feedback_data"]["main_feedback"]
    
    def test_generate_adaptive_feedback(self):
        """적응형 피드백 생성 테스트"""
        evaluation_result = {
            "is_correct": True,
            "score": 85.0,
            "understanding_level": "high"
        }
        
        user_performance_history = [
            {"is_correct": True, "score": 80},
            {"is_correct": False, "score": 45},
            {"is_correct": True, "score": 90},
            {"is_correct": True, "score": 85}
        ]
        
        result = generate_adaptive_feedback(
            evaluation_result, user_performance_history, "medium"
        )
        
        assert result["success"] == True
        assert "feedback_data" in result
        assert "performance_analysis" in result["feedback_data"]
        assert "next_steps" in result["feedback_data"]


def test_create_evaluation_feedback_agent():
    """EvaluationFeedbackAgent 생성 함수 테스트"""
    agent = create_evaluation_feedback_agent()
    assert isinstance(agent, EvaluationFeedbackAgent)
    assert agent.agent_name == "EvaluationFeedbackAgent"


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 코드
    pytest.main([__file__, "-v"])