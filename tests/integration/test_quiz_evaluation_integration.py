# tests/integration/test_quiz_evaluation_integration.py
# QuizGenerator와 EvaluationFeedbackAgent 통합 테스트

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.quiz import QuizGenerator
from agents.evaluator import EvaluationFeedbackAgent
from tools.content.quiz_tool import quiz_generation_tool
from tools.evaluation.answer_eval_tool import answer_evaluation_tool
from tools.evaluation.feedback_tool import feedback_generation_tool


class TestQuizEvaluationIntegration:
    """QuizGenerator와 EvaluationFeedbackAgent 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.quiz_agent = QuizGenerator()
        self.eval_agent = EvaluationFeedbackAgent()
    
    def test_complete_multiple_choice_flow(self):
        """완전한 객관식 문제 플로우 테스트"""
        # 1. 퀴즈 생성
        initial_state = {
            "user_message": "객관식 문제를 내주세요",
            "current_chapter": 1,
            "user_level": "medium",
            "user_type": "beginner",
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        quiz_state = self.quiz_agent.execute(initial_state)
        
        # 퀴즈 생성 확인
        assert quiz_state["ui_mode"] == "quiz"
        assert quiz_state["current_stage"] == "quiz_solving"
        assert len(quiz_state["current_loop_conversations"]) > 0
        
        # 생성된 퀴즈 데이터 추출
        quiz_data = None
        for conv in quiz_state["current_loop_conversations"]:
            if conv.get("agent") == "QuizGenerator" and "quiz_data" in conv:
                quiz_data = conv["quiz_data"]
                break
        
        assert quiz_data is not None
        assert quiz_data["question_type"] == "multiple_choice"
        
        # 2. 사용자 답변 시뮬레이션
        correct_answer = quiz_data["correct_answer"]
        quiz_state["user_answer"] = correct_answer  # 정답 선택
        quiz_state["hint_used"] = False
        quiz_state["response_time"] = 45
        
        # 3. 평가 및 피드백 생성
        eval_state = self.eval_agent.execute(quiz_state)
        
        # 평가 결과 확인
        assert eval_state["ui_mode"] == "feedback"
        assert eval_state["current_stage"] == "feedback_review"
        assert "last_evaluation" in eval_state
        assert "last_feedback" in eval_state
        
        # 정답이므로 긍정적 피드백 확인
        evaluation = eval_state["last_evaluation"]
        assert evaluation["is_correct"] == True
        assert evaluation["score"] > 0
        
        feedback_message = eval_state["system_message"]
        assert "✅" in feedback_message or "🎉" in feedback_message
    
    def test_complete_prompt_practice_flow(self):
        """완전한 프롬프트 실습 플로우 테스트"""
        # 1. 프롬프트 퀴즈 생성
        initial_state = {
            "user_message": "프롬프트 작성 문제를 내주세요",
            "current_chapter": 3,
            "user_level": "medium",
            "user_type": "business",
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        quiz_state = self.quiz_agent.execute(initial_state)
        
        # 퀴즈 생성 확인
        assert quiz_state["ui_mode"] == "quiz"
        assert "프롬프트" in quiz_state["system_message"]
        
        # 생성된 퀴즈 데이터 추출
        quiz_data = None
        for conv in quiz_state["current_loop_conversations"]:
            if conv.get("agent") == "QuizGenerator" and "quiz_data" in conv:
                quiz_data = conv["quiz_data"]
                break
        
        assert quiz_data is not None
        assert quiz_data["question_type"] == "prompt_practice"
        assert "scenario" in quiz_data
        assert "requirements" in quiz_data
        
        # 2. 사용자 프롬프트 답변 시뮬레이션
        user_prompt = """
당신은 친근하고 전문적인 고객서비스 담당자입니다.
고객의 문의사항에 대해 다음과 같이 응답해주세요:

1. 먼저 고객의 상황을 공감하며 인사
2. 문제 상황을 구체적으로 파악
3. 단계별 해결 방안 제시
4. 추가 도움이 필요한지 확인

응답은 친근하면서도 전문적인 톤으로 작성해주세요.
        """.strip()
        
        quiz_state["user_answer"] = user_prompt
        quiz_state["hint_used"] = False
        quiz_state["response_time"] = 180
        
        # ChatGPT 테스트 시뮬레이션
        chatgpt_result = self.eval_agent._simulate_chatgpt_test(user_prompt)
        quiz_state["chatgpt_test_result"] = chatgpt_result
        
        # 3. 평가 및 피드백 생성
        eval_state = self.eval_agent.execute(quiz_state)
        
        # 평가 결과 확인
        assert eval_state["ui_mode"] == "feedback"
        assert "last_evaluation" in eval_state
        assert "last_feedback" in eval_state
        
        evaluation = eval_state["last_evaluation"]
        assert evaluation["question_type"] == "prompt_practice"
        assert "requirements_analysis" in evaluation["detailed_analysis"]
        
        feedback_message = eval_state["system_message"]
        assert "프롬프트" in feedback_message or "점수" in feedback_message
    
    def test_hint_request_and_evaluation_flow(self):
        """힌트 요청 후 평가 플로우 테스트"""
        # 1. 퀴즈 생성
        initial_state = {
            "user_message": "객관식 문제를 내주세요",
            "current_chapter": 1,
            "user_level": "medium",
            "user_type": "beginner",
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        quiz_state = self.quiz_agent.execute(initial_state)
        
        # 2. 힌트 요청
        quiz_state["quiz_attempt_count"] = 2  # 2번째 시도로 설정
        hint_state = self.quiz_agent.handle_hint_request(quiz_state)
        
        # 힌트 제공 확인
        assert hint_state.get("hint_used") == True
        assert "💡" in hint_state["system_message"]
        assert "last_hint_level" in hint_state
        
        # 3. 힌트 사용 후 답변
        quiz_data = None
        for conv in hint_state["current_loop_conversations"]:
            if conv.get("agent") == "QuizGenerator" and "quiz_data" in conv:
                quiz_data = conv["quiz_data"]
                break
        
        hint_state["user_answer"] = quiz_data["correct_answer"]  # 정답 선택
        hint_state["response_time"] = 90
        
        # 4. 평가 (힌트 사용 고려)
        eval_state = self.eval_agent.execute(hint_state)
        
        # 힌트 사용으로 인한 점수 감점 확인
        evaluation = eval_state["last_evaluation"]
        assert evaluation["is_correct"] == True
        assert evaluation["detailed_analysis"]["hint_penalty"] < 0
        
        # 피드백에 힌트 사용 언급 확인 (힌트 사용 시 약점에 포함됨)
        evaluation = eval_state["last_evaluation"]
        feedback = eval_state["last_feedback"]
        assert evaluation["detailed_analysis"]["hint_penalty"] < 0 or any("힌트" in weakness for weakness in evaluation.get("weaknesses", []))
    
    def test_difficulty_adjustment_flow(self):
        """난이도 조정 플로우 테스트"""
        # 사용자 성과 이력 시뮬레이션 (높은 성과)
        high_performance = [
            {"is_correct": True, "hint_used": False, "response_time": 30, "difficulty": "medium"},
            {"is_correct": True, "hint_used": False, "response_time": 25, "difficulty": "medium"},
            {"is_correct": True, "hint_used": False, "response_time": 35, "difficulty": "medium"}
        ]
        
        # 퀴즈 생성 (성과 데이터 포함)
        result = quiz_generation_tool(
            chapter_id=1,
            user_level="medium",
            user_type="beginner",
            quiz_type="multiple_choice",
            user_performance=high_performance,
            user_id="test_user"
        )
        
        assert result["success"] == True
        quiz_data = result["quiz_data"]
        
        # 높은 성과로 인해 난이도가 상승했는지 확인
        difficulty = result.get("difficulty", "medium")
        assert difficulty in ["medium", "hard"]
        
        # 난이도별 파라미터가 적용되었는지 확인
        assert "difficulty_params" in quiz_data
    
    def test_learning_progress_tracking(self):
        """학습 진도 추적 테스트"""
        # 여러 번의 평가 결과 시뮬레이션
        evaluation_results = []
        
        for i in range(5):
            question_data = {
                "question_type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "correct_answer": 1,
                "difficulty": "medium"
            }
            
            # 점진적으로 향상되는 성과 시뮬레이션
            user_answer = 1 if i >= 2 else 0  # 처음 2개는 오답, 나머지는 정답
            hint_used = i < 3  # 처음 3개는 힌트 사용
            
            eval_result = answer_evaluation_tool(
                question_data=question_data,
                user_answer=user_answer,
                hint_used=hint_used,
                response_time=60 - i * 10  # 점점 빨라짐
            )
            
            if eval_result["success"]:
                evaluation_results.append(eval_result["evaluation_result"])
        
        # 학습 진도 계산
        from tools.evaluation.answer_eval_tool import calculate_learning_progress
        
        progress_result = calculate_learning_progress(
            user_id="test_user",
            chapter_id=1,
            evaluation_results=evaluation_results
        )
        
        assert progress_result["success"] == True
        progress_data = progress_result["progress_data"]
        
        # 향상 추세 확인
        assert progress_data["accuracy_trend"] == "improving"
        assert progress_data["total_attempts"] == 5
        assert progress_data["average_score"] > 0
    
    def test_error_handling_integration(self):
        """오류 처리 통합 테스트"""
        # 1. 잘못된 퀴즈 데이터로 평가 시도
        invalid_state = {
            "user_id": "test_user",
            "user_answer": 1,
            "current_loop_conversations": [
                {
                    "agent": "QuizGenerator",
                    "quiz_data": {
                        "question_type": "invalid_type",  # 잘못된 타입
                        "options": ["A", "B"],
                        "correct_answer": 0
                    }
                }
            ]
        }
        
        eval_state = self.eval_agent.execute(invalid_state)
        
        # 오류 처리 확인
        assert "오류가 발생했습니다" in eval_state["system_message"]
        assert eval_state["ui_mode"] == "chat"
        
        # 2. 퀴즈 데이터가 없는 상태에서 평가 시도
        empty_state = {
            "user_id": "test_user",
            "current_loop_conversations": []
        }
        
        eval_state = self.eval_agent.execute(empty_state)
        
        assert "평가할 문제나 답변을 찾을 수 없습니다" in eval_state["system_message"]
    
    def test_ui_mode_transitions(self):
        """UI 모드 전환 테스트"""
        # 초기 상태 (chat 모드)
        state = {
            "user_message": "문제를 내주세요",
            "current_chapter": 1,
            "user_level": "medium",
            "user_type": "beginner",
            "user_id": "test_user",
            "ui_mode": "chat",
            "current_loop_conversations": []
        }
        
        # 1. chat -> quiz 모드 전환
        quiz_state = self.quiz_agent.execute(state)
        assert quiz_state["ui_mode"] == "quiz"
        assert quiz_state["current_stage"] == "quiz_solving"
        
        # 2. 답변 추가
        quiz_data = quiz_state["current_loop_conversations"][0]["quiz_data"]
        quiz_state["user_answer"] = quiz_data["correct_answer"]
        
        # 3. quiz -> feedback 모드 전환
        eval_state = self.eval_agent.execute(quiz_state)
        assert eval_state["ui_mode"] == "feedback"
        assert eval_state["current_stage"] == "feedback_review"
        
        # UI 요소 확인
        assert "ui_elements" in eval_state
        ui_elements = eval_state["ui_elements"]
        assert ui_elements.get("type") == "feedback_display"
        assert "score_display" in ui_elements
        assert "show_next_button" in ui_elements


class TestToolsIntegration:
    """도구들 간의 통합 테스트"""
    
    def test_quiz_to_evaluation_tool_chain(self):
        """퀴즈 생성 -> 답변 평가 도구 체인 테스트"""
        # 1. 퀴즈 생성
        quiz_result = quiz_generation_tool(
            chapter_id=1,
            user_level="medium",
            user_type="beginner",
            quiz_type="multiple_choice"
        )
        
        assert quiz_result["success"] == True
        quiz_data = quiz_result["quiz_data"]
        
        # 2. 답변 평가
        eval_result = answer_evaluation_tool(
            question_data=quiz_data,
            user_answer=quiz_data["correct_answer"],
            hint_used=False,
            response_time=45
        )
        
        assert eval_result["success"] == True
        evaluation = eval_result["evaluation_result"]
        
        # 3. 피드백 생성
        feedback_result = feedback_generation_tool(
            evaluation_result=evaluation,
            question_data=quiz_data,
            user_profile={"user_level": "medium", "user_type": "beginner"},
            learning_context={"current_chapter": 1, "recent_performance": []}
        )
        
        assert feedback_result["success"] == True
        feedback_data = feedback_result["feedback_data"]
        
        # 전체 체인 결과 확인
        assert evaluation["is_correct"] == True
        assert "main_feedback" in feedback_data
        assert "encouragement" in feedback_data
        assert "improvement_tips" in feedback_data
    
    def test_hint_to_evaluation_integration(self):
        """힌트 -> 평가 통합 테스트"""
        from tools.content.hint_tool import hint_generation_tool
        
        # 1. 문제 데이터 준비
        question_data = {
            "question_id": "test_q1",
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "question_text": "AI가 무엇의 줄임말인가요?",
            "options": ["Artificial Intelligence", "Advanced Internet", "Automatic Information", "Applied Integration"],
            "correct_answer": 0
        }
        
        # 2. 힌트 생성
        hint_result = hint_generation_tool(
            question_data=question_data,
            hint_level=1,
            user_level="medium",
            attempt_count=2
        )
        
        assert hint_result["success"] == True
        
        # 3. 힌트 사용 후 답변 평가
        eval_result = answer_evaluation_tool(
            question_data=question_data,
            user_answer=0,  # 정답
            hint_used=True,  # 힌트 사용
            response_time=90
        )
        
        assert eval_result["success"] == True
        evaluation = eval_result["evaluation_result"]
        
        # 힌트 사용이 평가에 반영되었는지 확인
        assert evaluation["is_correct"] == True
        assert evaluation["detailed_analysis"]["hint_penalty"] < 0
        assert evaluation["score"] < 100  # 힌트 페널티로 인한 감점


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 코드
    pytest.main([__file__, "-v"])