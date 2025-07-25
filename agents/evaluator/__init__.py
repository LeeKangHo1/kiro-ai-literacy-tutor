# agents/evaluator/__init__.py
# EvaluationFeedbackAgent 에이전트 패키지

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from .answer_evaluator import AnswerEvaluator, EvaluationResult
from .feedback_generator import FeedbackGenerator
from tools.evaluation.answer_eval_tool import answer_evaluation_tool
from tools.evaluation.feedback_tool import feedback_generation_tool


class EvaluationFeedbackAgent:
    """
    EvaluationFeedbackAgent - 평가 및 피드백 전문가
    사용자 답변을 평가하고 개인화된 피드백을 제공하는 에이전트
    """
    
    def __init__(self):
        self.answer_evaluator = AnswerEvaluator()
        self.feedback_generator = FeedbackGenerator()
        self.agent_name = "EvaluationFeedbackAgent"
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        EvaluationFeedbackAgent 실행
        
        Args:
            state: TutorState 딕셔너리
            
        Returns:
            Dict: 업데이트된 state
        """
        try:
            # 현재 문제와 사용자 답변 추출
            current_quiz = self._extract_current_quiz(state)
            user_answer = self._extract_user_answer(state)
            
            if not current_quiz or user_answer is None:
                state["system_message"] = "평가할 문제나 답변을 찾을 수 없습니다."
                state["ui_mode"] = "chat"
                return state
            
            # 힌트 사용 여부 및 응답 시간 확인
            hint_used = state.get("hint_used", False)
            response_time = self._calculate_response_time(state)
            
            # ChatGPT 테스트 결과 (프롬프트 문제인 경우)
            chatgpt_test_result = state.get("chatgpt_test_result")
            
            # 답변 평가 실행
            evaluation_result = answer_evaluation_tool(
                question_data=current_quiz,
                user_answer=user_answer,
                hint_used=hint_used,
                response_time=response_time,
                chatgpt_test_result=chatgpt_test_result
            )
            
            if not evaluation_result.get("success", False):
                state["system_message"] = f"답변 평가 중 오류가 발생했습니다: {evaluation_result.get('error', '')}"
                state["ui_mode"] = "chat"
                return state
            
            # 사용자 프로필 및 학습 맥락 준비
            user_profile = self._prepare_user_profile(state)
            learning_context = self._prepare_learning_context(state)
            
            # 피드백 생성
            feedback_result = feedback_generation_tool(
                evaluation_result=evaluation_result["evaluation_result"],
                question_data=current_quiz,
                user_profile=user_profile,
                learning_context=learning_context
            )
            
            if not feedback_result.get("success", False):
                state["system_message"] = "피드백 생성 중 오류가 발생했습니다."
                state["ui_mode"] = "chat"
                return state
            
            # 피드백 데이터 처리
            feedback_data = feedback_result["feedback_data"]
            
            # 시스템 메시지 생성
            system_message = self._generate_feedback_message(feedback_data)
            
            # UI 요소 설정
            ui_elements = feedback_data.get("ui_elements", {})
            
            # State 업데이트
            state["system_message"] = system_message
            state["ui_elements"] = ui_elements
            state["ui_mode"] = "feedback"
            state["current_stage"] = "feedback_review"
            
            # 평가 결과를 state에 저장
            eval_result = evaluation_result["evaluation_result"]
            state["last_evaluation"] = eval_result
            state["last_feedback"] = feedback_data
            
            # 현재 루프 대화에 추가
            conversation_entry = {
                "agent": self.agent_name,
                "message_type": "system",
                "content": system_message,
                "evaluation_result": eval_result,
                "feedback_data": feedback_data,
                "ui_elements": ui_elements,
                "timestamp": datetime.now().isoformat()
            }
            
            if "current_loop_conversations" not in state:
                state["current_loop_conversations"] = []
            state["current_loop_conversations"].append(conversation_entry)
            
            # 학습 진도 업데이트 (정답인 경우)
            if eval_result.get("is_correct", False):
                self._update_learning_progress(state, eval_result)
            
            return state
            
        except Exception as e:
            print(f"EvaluationFeedbackAgent 실행 오류: {e}")
            state["system_message"] = "평가 및 피드백 처리 중 오류가 발생했습니다."
            state["ui_mode"] = "chat"
            return state
    
    def handle_chatgpt_test(self, state: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """
        ChatGPT API 테스트 처리 (프롬프트 실습용)
        
        Args:
            state: TutorState 딕셔너리
            user_prompt: 사용자가 작성한 프롬프트
            
        Returns:
            Dict: 업데이트된 state
        """
        try:
            # 실제로는 ChatGPT API 호출
            # 여기서는 시뮬레이션
            test_result = self._simulate_chatgpt_test(user_prompt)
            
            # 테스트 결과를 state에 저장
            state["chatgpt_test_result"] = test_result
            
            # 테스트 결과 메시지
            if test_result.get("success", False):
                message = f"""
🤖 **ChatGPT 테스트 결과**

**입력한 프롬프트:**
{user_prompt}

**ChatGPT 응답:**
{test_result.get('response', '')}

**응답 품질:** {test_result.get('quality_assessment', '보통')}

이제 답변을 제출하시면 프롬프트 품질을 종합적으로 평가해드리겠습니다!
                """.strip()
            else:
                message = f"""
❌ **ChatGPT 테스트 실패**

오류: {test_result.get('error', '알 수 없는 오류')}

프롬프트를 수정한 후 다시 테스트해보세요.
                """.strip()
            
            state["system_message"] = message
            
            return state
            
        except Exception as e:
            print(f"ChatGPT 테스트 처리 오류: {e}")
            state["system_message"] = "ChatGPT 테스트 중 오류가 발생했습니다."
            return state
    
    def _extract_current_quiz(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """현재 퀴즈 데이터 추출"""
        conversations = state.get("current_loop_conversations", [])
        
        # 가장 최근의 QuizGenerator 메시지에서 퀴즈 데이터 찾기
        for conv in reversed(conversations):
            if conv.get("agent") == "QuizGenerator" and "quiz_data" in conv:
                return conv["quiz_data"]
        
        return None
    
    def _extract_user_answer(self, state: Dict[str, Any]) -> Any:
        """사용자 답변 추출"""
        # 실제로는 사용자 입력에서 추출
        # 여기서는 state에서 직접 가져옴
        return state.get("user_answer")
    
    def _calculate_response_time(self, state: Dict[str, Any]) -> Optional[int]:
        """응답 시간 계산"""
        # 실제로는 문제 제시 시간과 답변 제출 시간의 차이 계산
        # 여기서는 시뮬레이션
        return state.get("response_time", 60)  # 기본 60초
    
    def _prepare_user_profile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 프로필 준비"""
        return {
            "user_id": state.get("user_id", ""),
            "user_level": state.get("user_level", "medium"),
            "user_type": state.get("user_type", "beginner"),
            "current_chapter": state.get("current_chapter", 1)
        }
    
    def _prepare_learning_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """학습 맥락 준비"""
        # 실제로는 DB에서 최근 성과 데이터 조회
        recent_performance = self._get_recent_performance(state.get("user_id", ""))
        
        return {
            "current_chapter": state.get("current_chapter", 1),
            "recent_performance": recent_performance,
            "loop_count": len(state.get("recent_loops_summary", [])),
            "current_stage": state.get("current_stage", "quiz_solving")
        }
    
    def _get_recent_performance(self, user_id: str) -> List[Dict[str, Any]]:
        """최근 성과 데이터 조회 (시뮬레이션)"""
        # 실제로는 DB에서 조회
        return [
            {"is_correct": True, "score": 85, "hint_used": False},
            {"is_correct": False, "score": 45, "hint_used": True},
            {"is_correct": True, "score": 92, "hint_used": False}
        ]
    
    def _generate_feedback_message(self, feedback_data: Dict[str, Any]) -> str:
        """피드백 메시지 생성"""
        main_feedback = feedback_data.get("main_feedback", "")
        encouragement = feedback_data.get("encouragement", "")
        improvement_tips = feedback_data.get("improvement_tips", [])
        next_steps = feedback_data.get("next_steps", {})
        
        message = f"{main_feedback}\n\n"
        
        if encouragement:
            message += f"💬 {encouragement}\n\n"
        
        if improvement_tips:
            message += "📝 **개선 팁:**\n"
            for tip in improvement_tips:
                message += f"• {tip}\n"
            message += "\n"
        
        next_message = next_steps.get("message", "")
        if next_message:
            message += f"🎯 **다음 단계:** {next_message}"
        
        return message.strip()
    
    def _update_learning_progress(self, state: Dict[str, Any], eval_result: Dict[str, Any]):
        """학습 진도 업데이트"""
        # 실제로는 DB 업데이트
        # 여기서는 로그만 출력
        progress_data = {
            "user_id": state.get("user_id"),
            "chapter_id": state.get("current_chapter"),
            "score": eval_result.get("score"),
            "understanding_level": eval_result.get("understanding_level"),
            "updated_at": datetime.now().isoformat()
        }
        
        print(f"학습 진도 업데이트: {json.dumps(progress_data, ensure_ascii=False)}")
    
    def _simulate_chatgpt_test(self, user_prompt: str) -> Dict[str, Any]:
        """ChatGPT API 테스트 시뮬레이션"""
        # 실제로는 OpenAI API 호출
        # 여기서는 시뮬레이션
        
        if len(user_prompt.strip()) < 10:
            return {
                "success": False,
                "error": "프롬프트가 너무 짧습니다."
            }
        
        # 간단한 응답 시뮬레이션
        simulated_response = f"안녕하세요! 다음과 같이 도움을 드릴 수 있습니다:\n\n[프롬프트 '{user_prompt[:30]}...'에 대한 시뮬레이션 응답입니다]"
        
        # 품질 평가 시뮬레이션
        if "구체적" in user_prompt and "역할" in user_prompt:
            quality = "우수"
        elif "당신은" in user_prompt or "please" in user_prompt.lower():
            quality = "좋음"
        else:
            quality = "보통"
        
        return {
            "success": True,
            "response": simulated_response,
            "quality_assessment": quality,
            "response_length": len(simulated_response),
            "tested_at": datetime.now().isoformat()
        }


# 에이전트 인스턴스 생성 함수
def create_evaluation_feedback_agent() -> EvaluationFeedbackAgent:
    """EvaluationFeedbackAgent 인스턴스 생성"""
    return EvaluationFeedbackAgent()