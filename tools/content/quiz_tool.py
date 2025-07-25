# tools/content/quiz_tool.py
# 퀴즈 생성 도구

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from agents.quiz.question_generator import QuestionGenerator
from agents.quiz.difficulty_manager import DifficultyManager


def quiz_generation_tool(
    chapter_id: int,
    user_level: str,
    user_type: str,
    quiz_type: str = "multiple_choice",
    difficulty: Optional[str] = None,
    user_performance: Optional[List[Dict[str, Any]]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    퀴즈 생성 도구
    
    Args:
        chapter_id: 챕터 ID
        user_level: 사용자 수준 (low/medium/high)
        user_type: 사용자 유형 (beginner/business)
        quiz_type: 퀴즈 유형 (multiple_choice/prompt_practice)
        difficulty: 지정된 난이도 (없으면 자동 계산)
        user_performance: 사용자 성과 데이터
        user_id: 사용자 ID
        
    Returns:
        Dict: 생성된 퀴즈 데이터
    """
    try:
        # 도구 초기화
        question_generator = QuestionGenerator()
        difficulty_manager = DifficultyManager()
        
        # 난이도 결정
        if not difficulty and user_performance and user_id:
            difficulty = difficulty_manager.calculate_current_difficulty(
                user_id, chapter_id, user_performance
            )
        elif not difficulty:
            difficulty = "medium"  # 기본 난이도
        
        # 난이도별 파라미터 가져오기
        difficulty_params = difficulty_manager.get_difficulty_parameters(difficulty, quiz_type)
        
        # 문제 생성
        if quiz_type == "multiple_choice":
            question_data = question_generator.generate_multiple_choice_question(
                chapter_id, user_level, user_type, difficulty
            )
        elif quiz_type == "prompt_practice":
            question_data = question_generator.generate_prompt_question(
                chapter_id, user_level, user_type, difficulty
            )
        else:
            return {
                "success": False,
                "error": f"지원하지 않는 퀴즈 유형: {quiz_type}",
                "quiz_data": None
            }
        
        # 난이도 파라미터 추가
        question_data["difficulty_params"] = difficulty_params
        
        # UI 요소 생성
        ui_elements = _generate_quiz_ui_elements(question_data, quiz_type)
        
        return {
            "success": True,
            "quiz_data": question_data,
            "ui_elements": ui_elements,
            "difficulty": difficulty,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"퀴즈 생성 도구 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "quiz_data": None
        }


def _generate_quiz_ui_elements(question_data: Dict[str, Any], quiz_type: str) -> Dict[str, Any]:
    """퀴즈 UI 요소 생성"""
    
    base_ui = {
        "mode": "quiz",
        "question_id": question_data.get("question_id"),
        "chapter_id": question_data.get("chapter_id"),
        "difficulty": question_data.get("difficulty"),
        "show_hint_button": True,
        "show_submit_button": True
    }
    
    if quiz_type == "multiple_choice":
        return {
            **base_ui,
            "type": "multiple_choice",
            "question_text": question_data.get("question_text"),
            "options": question_data.get("options", []),
            "allow_multiple_selection": False,
            "show_explanation": False,  # 답변 후에 표시
            "timer_enabled": True,
            "timer_duration": 300  # 5분
        }
    
    elif quiz_type == "prompt_practice":
        return {
            **base_ui,
            "type": "prompt_practice",
            "scenario": question_data.get("scenario"),
            "task_description": question_data.get("task_description"),
            "requirements": question_data.get("requirements", []),
            "text_area_placeholder": "여기에 프롬프트를 작성해주세요...",
            "min_length": 50,
            "max_length": 1000,
            "show_character_count": True,
            "show_requirements_checklist": True,
            "enable_chatgpt_test": True  # ChatGPT API 테스트 기능
        }
    
    return base_ui


def validate_quiz_answer(
    question_data: Dict[str, Any],
    user_answer: Any,
    hint_used: bool = False,
    response_time: Optional[int] = None
) -> Dict[str, Any]:
    """
    퀴즈 답변 검증
    
    Args:
        question_data: 문제 데이터
        user_answer: 사용자 답변
        hint_used: 힌트 사용 여부
        response_time: 응답 시간 (초)
        
    Returns:
        Dict: 검증 결과
    """
    try:
        question_type = question_data.get("question_type", "multiple_choice")
        
        if question_type == "multiple_choice":
            return _validate_multiple_choice_answer(question_data, user_answer, hint_used, response_time)
        elif question_type == "prompt_practice":
            return _validate_prompt_answer(question_data, user_answer, hint_used, response_time)
        else:
            return {
                "is_valid": False,
                "error": f"지원하지 않는 문제 유형: {question_type}"
            }
            
    except Exception as e:
        print(f"답변 검증 오류: {e}")
        return {
            "is_valid": False,
            "error": str(e)
        }


def _validate_multiple_choice_answer(
    question_data: Dict[str, Any],
    user_answer: int,
    hint_used: bool,
    response_time: Optional[int]
) -> Dict[str, Any]:
    """객관식 답변 검증"""
    correct_answer = question_data.get("correct_answer", 0)
    options = question_data.get("options", [])
    
    # 답변 유효성 검사
    if not isinstance(user_answer, int) or user_answer < 0 or user_answer >= len(options):
        return {
            "is_valid": False,
            "error": "유효하지 않은 답변입니다."
        }
    
    is_correct = user_answer == correct_answer
    
    return {
        "is_valid": True,
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "user_answer": user_answer,
        "explanation": question_data.get("explanation", ""),
        "hint_used": hint_used,
        "response_time": response_time,
        "score": _calculate_score(is_correct, hint_used, response_time)
    }


def _validate_prompt_answer(
    question_data: Dict[str, Any],
    user_answer: str,
    hint_used: bool,
    response_time: Optional[int]
) -> Dict[str, Any]:
    """프롬프트 답변 검증"""
    if not isinstance(user_answer, str):
        return {
            "is_valid": False,
            "error": "답변은 텍스트 형태여야 합니다."
        }
    
    # 기본 길이 검증
    if len(user_answer.strip()) < 20:
        return {
            "is_valid": False,
            "error": "답변이 너무 짧습니다. 최소 20자 이상 작성해주세요."
        }
    
    # 요구사항 기본 체크
    requirements = question_data.get("requirements", [])
    requirements_met = _check_prompt_requirements(user_answer, requirements)
    
    return {
        "is_valid": True,
        "user_answer": user_answer,
        "requirements_met": requirements_met,
        "hint_used": hint_used,
        "response_time": response_time,
        "needs_evaluation": True,  # EvaluationFeedbackAgent에서 상세 평가 필요
        "preliminary_score": _calculate_prompt_preliminary_score(requirements_met, hint_used)
    }


def _check_prompt_requirements(user_answer: str, requirements: List[str]) -> Dict[str, bool]:
    """프롬프트 요구사항 기본 체크"""
    requirements_met = {}
    
    for req in requirements:
        # 간단한 키워드 기반 체크 (실제로는 더 정교한 분석 필요)
        if "역할" in req or "role" in req.lower():
            requirements_met[req] = "당신은" in user_answer or "you are" in user_answer.lower()
        elif "톤" in req or "tone" in req.lower():
            requirements_met[req] = any(word in user_answer for word in ["친근", "정중", "전문적", "친절"])
        elif "구체적" in req or "specific" in req.lower():
            requirements_met[req] = len(user_answer.split()) > 30  # 단어 수 기준
        else:
            requirements_met[req] = True  # 기본적으로 충족으로 가정
    
    return requirements_met


def _calculate_score(is_correct: bool, hint_used: bool, response_time: Optional[int]) -> float:
    """객관식 점수 계산"""
    if not is_correct:
        return 0.0
    
    base_score = 100.0
    
    # 힌트 사용 페널티
    if hint_used:
        base_score *= 0.7
    
    # 응답 시간 보너스/페널티
    if response_time:
        if response_time <= 30:  # 30초 이내
            base_score *= 1.1
        elif response_time > 180:  # 3분 초과
            base_score *= 0.9
    
    return min(100.0, base_score)


def _calculate_prompt_preliminary_score(requirements_met: Dict[str, bool], hint_used: bool) -> float:
    """프롬프트 예비 점수 계산"""
    if not requirements_met:
        return 50.0
    
    met_count = sum(requirements_met.values())
    total_count = len(requirements_met)
    
    base_score = (met_count / total_count) * 100 if total_count > 0 else 50.0
    
    # 힌트 사용 페널티
    if hint_used:
        base_score *= 0.8
    
    return base_score