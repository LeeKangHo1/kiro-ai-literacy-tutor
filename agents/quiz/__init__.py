# agents/quiz/__init__.py
# QuizGenerator 에이전트 패키지

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from .question_generator import QuestionGenerator
from .hint_generator import HintGenerator
from .difficulty_manager import DifficultyManager
from tools.content.quiz_tool import quiz_generation_tool, validate_quiz_answer
from tools.content.hint_tool import hint_generation_tool


class QuizGenerator:
    """
    QuizGenerator 에이전트 - 문제 출제 전문가
    사용자 수준과 성과에 맞는 객관식 및 프롬프트 문제를 생성하고 관리
    """
    
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.hint_generator = HintGenerator()
        self.difficulty_manager = DifficultyManager()
        self.agent_name = "QuizGenerator"
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        QuizGenerator 에이전트 실행
        
        Args:
            state: TutorState 딕셔너리
            
        Returns:
            Dict: 업데이트된 state
        """
        try:
            user_message = state.get("user_message", "").lower()
            current_chapter = state.get("current_chapter", 1)
            user_level = state.get("user_level", "medium")
            user_type = state.get("user_type", "beginner")
            user_id = state.get("user_id", "")
            
            # 사용자 요청 분석
            if "객관식" in user_message or "선택" in user_message or "multiple" in user_message:
                quiz_type = "multiple_choice"
            elif "프롬프트" in user_message or "작성" in user_message or "prompt" in user_message:
                quiz_type = "prompt_practice"
            else:
                # 기본적으로 객관식 문제 생성
                quiz_type = "multiple_choice"
            
            # 사용자 성과 데이터 가져오기 (실제로는 DB에서 조회)
            user_performance = self._get_user_performance(user_id, current_chapter)
            
            # 퀴즈 생성
            quiz_result = quiz_generation_tool(
                chapter_id=current_chapter,
                user_level=user_level,
                user_type=user_type,
                quiz_type=quiz_type,
                user_performance=user_performance,
                user_id=user_id
            )
            
            if not quiz_result.get("success", False):
                state["system_message"] = "죄송합니다. 문제 생성 중 오류가 발생했습니다. 다시 시도해주세요."
                state["ui_mode"] = "chat"
                return state
            
            # 문제 데이터와 UI 요소 설정
            quiz_data = quiz_result["quiz_data"]
            ui_elements = quiz_result["ui_elements"]
            
            # 시스템 메시지 생성
            system_message = self._generate_quiz_message(quiz_data, quiz_type)
            
            # State 업데이트
            state["system_message"] = system_message
            state["ui_elements"] = ui_elements
            state["ui_mode"] = "quiz"
            state["current_stage"] = "quiz_solving"
            
            # 현재 루프 대화에 추가
            conversation_entry = {
                "agent": self.agent_name,
                "message_type": "system",
                "content": system_message,
                "quiz_data": quiz_data,
                "ui_elements": ui_elements,
                "timestamp": datetime.now().isoformat()
            }
            
            if "current_loop_conversations" not in state:
                state["current_loop_conversations"] = []
            state["current_loop_conversations"].append(conversation_entry)
            
            return state
            
        except Exception as e:
            print(f"QuizGenerator 실행 오류: {e}")
            state["system_message"] = "문제 생성 중 오류가 발생했습니다. 다시 시도해주세요."
            state["ui_mode"] = "chat"
            return state
    
    def handle_hint_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        힌트 요청 처리
        
        Args:
            state: TutorState 딕셔너리
            
        Returns:
            Dict: 업데이트된 state
        """
        try:
            # 현재 문제 데이터 찾기
            current_quiz = self._get_current_quiz_from_state(state)
            if not current_quiz:
                state["system_message"] = "현재 풀고 있는 문제를 찾을 수 없습니다."
                return state
            
            # 힌트 레벨 결정
            hint_level = self._determine_hint_level(state)
            user_level = state.get("user_level", "medium")
            
            # 힌트 생성
            hint_result = hint_generation_tool(
                question_data=current_quiz,
                hint_level=hint_level,
                user_level=user_level,
                attempt_count=state.get("quiz_attempt_count", 1)
            )
            
            if not hint_result.get("success", False):
                state["system_message"] = hint_result.get("message", "힌트를 생성할 수 없습니다.")
                return state
            
            # 힌트 UI 요소 추가
            hint_ui = hint_result["ui_elements"]
            current_ui = state.get("ui_elements", {})
            current_ui["hint_display"] = hint_ui
            state["ui_elements"] = current_ui
            
            # 힌트 메시지
            hint_data = hint_result["hint_data"]
            state["system_message"] = f"💡 {hint_data['hint_text']}"
            
            # 힌트 사용 기록
            state["hint_used"] = True
            state["last_hint_level"] = hint_level
            
            return state
            
        except Exception as e:
            print(f"힌트 요청 처리 오류: {e}")
            state["system_message"] = "힌트 생성 중 오류가 발생했습니다."
            return state
    
    def _generate_quiz_message(self, quiz_data: Dict[str, Any], quiz_type: str) -> str:
        """퀴즈 메시지 생성"""
        
        difficulty_text = {
            "easy": "쉬운",
            "medium": "보통",
            "hard": "어려운"
        }.get(quiz_data.get("difficulty", "medium"), "보통")
        
        if quiz_type == "multiple_choice":
            return f"""
📝 **{difficulty_text} 난이도 객관식 문제**

{quiz_data.get('question_text', '')}

아래 선택지 중에서 정답을 선택해주세요. 어려우시면 💡 힌트 버튼을 눌러보세요!
            """.strip()
        
        elif quiz_type == "prompt_practice":
            scenario = quiz_data.get("scenario", "")
            task_description = quiz_data.get("task_description", "")
            requirements = quiz_data.get("requirements", [])
            
            req_text = "\n".join([f"• {req}" for req in requirements])
            
            return f"""
✍️ **{difficulty_text} 난이도 프롬프트 작성 실습**

**상황:** {scenario}

**과제:** {task_description}

**요구사항:**
{req_text}

위 조건을 만족하는 프롬프트를 작성해주세요. 완성되면 실제 ChatGPT API로 테스트해볼 수 있습니다!
            """.strip()
        
        return "문제가 준비되었습니다. 풀어보세요!"
    
    def _get_user_performance(self, user_id: str, chapter_id: int) -> List[Dict[str, Any]]:
        """사용자 성과 데이터 조회 (실제로는 DB에서)"""
        # 샘플 데이터 반환
        return [
            {
                "question_id": "sample_1",
                "is_correct": True,
                "hint_used": False,
                "response_time": 45,
                "difficulty": "medium"
            },
            {
                "question_id": "sample_2",
                "is_correct": False,
                "hint_used": True,
                "response_time": 120,
                "difficulty": "medium"
            }
        ]
    
    def _get_current_quiz_from_state(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """현재 상태에서 퀴즈 데이터 추출"""
        conversations = state.get("current_loop_conversations", [])
        
        # 가장 최근의 QuizGenerator 메시지에서 퀴즈 데이터 찾기
        for conv in reversed(conversations):
            if conv.get("agent") == self.agent_name and "quiz_data" in conv:
                return conv["quiz_data"]
        
        return None
    
    def _determine_hint_level(self, state: Dict[str, Any]) -> int:
        """현재 상황에 맞는 힌트 레벨 결정"""
        last_hint_level = state.get("last_hint_level", 0)
        return min(last_hint_level + 1, 3)  # 최대 3레벨까지


# 에이전트 인스턴스 생성 함수
def create_quiz_generator() -> QuizGenerator:
    """QuizGenerator 에이전트 인스턴스 생성"""
    return QuizGenerator()