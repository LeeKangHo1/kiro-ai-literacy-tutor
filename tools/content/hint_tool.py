# tools/content/hint_tool.py
# 힌트 생성 도구

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from agents.quiz.hint_generator import HintGenerator
from agents.quiz.difficulty_manager import DifficultyManager


def hint_generation_tool(
    question_data: Dict[str, Any],
    hint_level: int = 1,
    user_level: str = "medium",
    attempt_count: int = 1,
    time_spent: Optional[int] = None
) -> Dict[str, Any]:
    """
    힌트 생성 도구
    
    Args:
        question_data: 문제 데이터
        hint_level: 힌트 단계 (1: 가벼운, 2: 중간, 3: 강한)
        user_level: 사용자 수준
        attempt_count: 시도 횟수
        time_spent: 소요 시간 (초)
        
    Returns:
        Dict: 생성된 힌트 데이터
    """
    try:
        # 도구 초기화
        hint_generator = HintGenerator()
        difficulty_manager = DifficultyManager()
        
        # 힌트 제공 여부 확인
        difficulty = question_data.get("difficulty", "medium")
        should_provide = difficulty_manager.should_provide_hint(
            difficulty, attempt_count, time_spent
        )
        
        if not should_provide and attempt_count == 1:
            return {
                "success": False,
                "message": "아직 조금 더 생각해보세요. 힌트는 나중에 제공해드릴게요.",
                "hint_data": None,
                "should_retry": True
            }
        
        # 힌트 생성
        hint_data = hint_generator.generate_hint(question_data, hint_level, user_level)
        
        # UI 요소 생성
        ui_elements = _generate_hint_ui_elements(hint_data, question_data)
        
        # 힌트 사용 기록
        hint_usage_record = {
            "question_id": question_data.get("question_id"),
            "hint_level": hint_level,
            "attempt_count": attempt_count,
            "time_spent": time_spent,
            "provided_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "hint_data": hint_data,
            "ui_elements": ui_elements,
            "usage_record": hint_usage_record,
            "next_hint_available": hint_level < 3  # 최대 3단계까지
        }
        
    except Exception as e:
        print(f"힌트 생성 도구 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "hint_data": None
        }


def _generate_hint_ui_elements(hint_data: Dict[str, Any], question_data: Dict[str, Any]) -> Dict[str, Any]:
    """힌트 UI 요소 생성"""
    
    hint_level = hint_data.get("hint_level", 1)
    hint_type = hint_data.get("hint_type", "default")
    
    base_ui = {
        "type": "hint_display",
        "hint_level": hint_level,
        "hint_text": hint_data.get("hint_text", ""),
        "show_close_button": True,
        "auto_close_timer": None  # 자동 닫기 없음
    }
    
    # 힌트 레벨별 스타일링
    if hint_level == 1:
        ui_style = {
            "background_color": "#e3f2fd",  # 연한 파란색
            "border_color": "#2196f3",
            "icon": "💡",
            "title": "힌트"
        }
    elif hint_level == 2:
        ui_style = {
            "background_color": "#fff3e0",  # 연한 주황색
            "border_color": "#ff9800",
            "icon": "🔍",
            "title": "더 자세한 힌트"
        }
    else:  # level 3
        ui_style = {
            "background_color": "#f3e5f5",  # 연한 보라색
            "border_color": "#9c27b0",
            "icon": "🎯",
            "title": "강한 힌트"
        }
    
    # 문제 유형별 추가 요소
    if hint_type == "multiple_choice":
        additional_elements = {
            "show_options_highlight": hint_level >= 2,  # 2단계부터 선택지 하이라이트
            "highlight_correct_area": hint_level >= 3   # 3단계에서 정답 영역 표시
        }
    elif hint_type == "prompt_practice":
        additional_elements = {
            "show_structure_guide": hint_level >= 1,
            "show_example_snippet": hint_level >= 2,
            "show_template": hint_level >= 3
        }
    else:
        additional_elements = {}
    
    return {
        **base_ui,
        **ui_style,
        **additional_elements
    }


def record_hint_usage(
    user_id: str,
    question_id: str,
    hint_level: int,
    hint_effectiveness: Optional[str] = None
) -> Dict[str, Any]:
    """
    힌트 사용 기록 저장
    
    Args:
        user_id: 사용자 ID
        question_id: 문제 ID
        hint_level: 사용된 힌트 레벨
        hint_effectiveness: 힌트 효과성 ("helpful", "not_helpful", "confusing")
        
    Returns:
        Dict: 기록 결과
    """
    try:
        usage_record = {
            "user_id": user_id,
            "question_id": question_id,
            "hint_level": hint_level,
            "used_at": datetime.now().isoformat(),
            "effectiveness": hint_effectiveness
        }
        
        # 실제로는 데이터베이스에 저장
        # 여기서는 로그만 출력
        print(f"힌트 사용 기록: {json.dumps(usage_record, ensure_ascii=False)}")
        
        return {
            "success": True,
            "record_id": f"hint_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "message": "힌트 사용이 기록되었습니다."
        }
        
    except Exception as e:
        print(f"힌트 사용 기록 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_hint_statistics(user_id: str, chapter_id: Optional[int] = None) -> Dict[str, Any]:
    """
    사용자의 힌트 사용 통계 조회
    
    Args:
        user_id: 사용자 ID
        chapter_id: 챕터 ID (선택사항)
        
    Returns:
        Dict: 힌트 사용 통계
    """
    try:
        # 실제로는 데이터베이스에서 조회
        # 여기서는 샘플 데이터 반환
        sample_stats = {
            "user_id": user_id,
            "chapter_id": chapter_id,
            "total_hints_used": 15,
            "hint_level_distribution": {
                "level_1": 8,
                "level_2": 5,
                "level_3": 2
            },
            "effectiveness_feedback": {
                "helpful": 12,
                "not_helpful": 2,
                "confusing": 1
            },
            "average_hints_per_question": 1.2,
            "improvement_trend": "decreasing",  # 힌트 사용이 감소하는 추세
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "statistics": sample_stats
        }
        
    except Exception as e:
        print(f"힌트 통계 조회 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def suggest_next_hint_level(
    current_level: int,
    user_response: Optional[str] = None,
    time_since_hint: Optional[int] = None
) -> Dict[str, Any]:
    """
    다음 힌트 레벨 제안
    
    Args:
        current_level: 현재 힌트 레벨
        user_response: 사용자 응답 (힌트 후)
        time_since_hint: 힌트 제공 후 경과 시간 (초)
        
    Returns:
        Dict: 다음 힌트 레벨 제안
    """
    try:
        # 최대 레벨 체크
        if current_level >= 3:
            return {
                "success": False,
                "message": "더 이상 제공할 힌트가 없습니다. 답을 확인해보세요.",
                "suggested_level": None,
                "should_reveal_answer": True
            }
        
        # 시간 기반 제안
        if time_since_hint and time_since_hint > 120:  # 2분 경과
            suggested_level = current_level + 1
            message = "조금 더 구체적인 힌트를 드릴까요?"
        else:
            suggested_level = current_level + 1
            message = "다음 단계 힌트가 필요하시면 요청해주세요."
        
        return {
            "success": True,
            "suggested_level": suggested_level,
            "message": message,
            "should_reveal_answer": False
        }
        
    except Exception as e:
        print(f"다음 힌트 레벨 제안 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def validate_hint_request(
    question_data: Dict[str, Any],
    requested_level: int,
    user_progress: Dict[str, Any]
) -> Dict[str, Any]:
    """
    힌트 요청 유효성 검증
    
    Args:
        question_data: 문제 데이터
        requested_level: 요청된 힌트 레벨
        user_progress: 사용자 진행 상황
        
    Returns:
        Dict: 검증 결과
    """
    try:
        # 레벨 범위 검증
        if requested_level < 1 or requested_level > 3:
            return {
                "is_valid": False,
                "error": "힌트 레벨은 1-3 사이여야 합니다."
            }
        
        # 순차적 힌트 요청 검증
        last_hint_level = user_progress.get("last_hint_level", 0)
        if requested_level > last_hint_level + 1:
            return {
                "is_valid": False,
                "error": f"힌트는 순서대로 요청해주세요. 다음 가능한 레벨: {last_hint_level + 1}"
            }
        
        # 문제 유형별 힌트 가용성 검증
        question_type = question_data.get("question_type", "multiple_choice")
        if question_type not in ["multiple_choice", "prompt_practice"]:
            return {
                "is_valid": False,
                "error": "이 문제 유형에는 힌트를 제공할 수 없습니다."
            }
        
        return {
            "is_valid": True,
            "message": "힌트 요청이 유효합니다."
        }
        
    except Exception as e:
        print(f"힌트 요청 검증 오류: {e}")
        return {
            "is_valid": False,
            "error": str(e)
        }