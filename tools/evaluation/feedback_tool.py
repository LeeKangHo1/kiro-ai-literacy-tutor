# tools/evaluation/feedback_tool.py
# 피드백 도구

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from agents.evaluator.feedback_generator import FeedbackGenerator
from agents.evaluator.answer_evaluator import EvaluationResult


def feedback_generation_tool(
    evaluation_result: Dict[str, Any],
    question_data: Dict[str, Any],
    user_profile: Dict[str, Any],
    learning_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    피드백 생성 도구
    
    Args:
        evaluation_result: 평가 결과 딕셔너리
        question_data: 문제 데이터
        user_profile: 사용자 프로필
        learning_context: 학습 맥락
        
    Returns:
        Dict: 생성된 피드백 데이터
    """
    try:
        feedback_generator = FeedbackGenerator()
        
        # 평가 결과를 EvaluationResult 객체로 변환
        eval_result_obj = _dict_to_evaluation_result(evaluation_result)
        
        # 종합 피드백 생성
        feedback_data = feedback_generator.generate_comprehensive_feedback(
            eval_result_obj, question_data, user_profile, learning_context
        )
        
        # 추가 메타데이터
        feedback_data["tool_version"] = "1.0"
        feedback_data["feedback_type"] = "comprehensive"
        
        return {
            "success": True,
            "feedback_data": feedback_data
        }
        
    except Exception as e:
        print(f"피드백 생성 도구 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "feedback_data": None
        }


def _dict_to_evaluation_result(eval_dict: Dict[str, Any]) -> EvaluationResult:
    """딕셔너리를 EvaluationResult 객체로 변환"""
    return EvaluationResult(
        is_correct=eval_dict.get("is_correct", False),
        score=eval_dict.get("score", 0.0),
        understanding_level=eval_dict.get("understanding_level", "low"),
        strengths=eval_dict.get("strengths", []),
        weaknesses=eval_dict.get("weaknesses", []),
        detailed_analysis=eval_dict.get("detailed_analysis", {})
    )


def generate_quick_feedback(
    is_correct: bool,
    score: float,
    question_type: str = "multiple_choice",
    user_type: str = "beginner"
) -> Dict[str, Any]:
    """
    빠른 피드백 생성 (간단한 버전)
    
    Args:
        is_correct: 정답 여부
        score: 점수
        question_type: 문제 유형
        user_type: 사용자 유형
        
    Returns:
        Dict: 간단한 피드백 데이터
    """
    try:
        # 기본 메시지 생성
        if is_correct:
            if score >= 90:
                main_message = "🎉 완벽합니다!"
                encouragement = "훌륭한 실력이네요!"
            elif score >= 80:
                main_message = "✅ 정답입니다!"
                encouragement = "잘 하셨어요!"
            else:
                main_message = "✅ 정답입니다."
                encouragement = "조금 더 빠르게 답할 수 있도록 연습해보세요."
        else:
            main_message = "❌ 아쉽게도 정답이 아닙니다."
            encouragement = "괜찮아요! 다시 한 번 시도해보세요."
        
        # 사용자 유형별 맞춤 메시지
        if user_type == "business":
            if is_correct:
                encouragement += " 실무에 바로 적용할 수 있을 것 같아요!"
            else:
                encouragement += " 실무 경험을 바탕으로 다시 생각해보세요."
        
        return {
            "success": True,
            "feedback_data": {
                "feedback_id": f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "main_feedback": main_message,
                "encouragement": encouragement,
                "score": score,
                "is_correct": is_correct,
                "feedback_type": "quick",
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"빠른 피드백 생성 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def generate_adaptive_feedback(
    evaluation_result: Dict[str, Any],
    user_performance_history: List[Dict[str, Any]],
    difficulty_level: str = "medium"
) -> Dict[str, Any]:
    """
    적응형 피드백 생성 (사용자 성과 이력 기반)
    
    Args:
        evaluation_result: 현재 평가 결과
        user_performance_history: 사용자 성과 이력
        difficulty_level: 난이도 수준
        
    Returns:
        Dict: 적응형 피드백 데이터
    """
    try:
        is_correct = evaluation_result.get("is_correct", False)
        score = evaluation_result.get("score", 0.0)
        understanding_level = evaluation_result.get("understanding_level", "low")
        
        # 성과 이력 분석
        performance_analysis = _analyze_performance_history(user_performance_history)
        
        # 적응형 메시지 생성
        adaptive_message = _generate_adaptive_message(
            is_correct, score, understanding_level, performance_analysis, difficulty_level
        )
        
        # 개인화된 다음 단계 제안
        next_steps = _generate_adaptive_next_steps(
            performance_analysis, is_correct, understanding_level
        )
        
        return {
            "success": True,
            "feedback_data": {
                "feedback_id": f"adaptive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "main_feedback": adaptive_message["main"],
                "encouragement": adaptive_message["encouragement"],
                "improvement_tips": adaptive_message["tips"],
                "next_steps": next_steps,
                "performance_analysis": performance_analysis,
                "feedback_type": "adaptive",
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"적응형 피드백 생성 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _analyze_performance_history(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """성과 이력 분석"""
    if not history:
        return {
            "trend": "no_data",
            "average_score": 0.0,
            "accuracy_rate": 0.0,
            "improvement_rate": 0.0
        }
    
    # 최근 10개 결과 분석
    recent_history = history[-10:]
    
    # 평균 점수
    average_score = sum(h.get("score", 0) for h in recent_history) / len(recent_history)
    
    # 정확도
    correct_count = sum(1 for h in recent_history if h.get("is_correct", False))
    accuracy_rate = correct_count / len(recent_history)
    
    # 개선 추세 (전반부 vs 후반부)
    if len(recent_history) >= 4:
        mid_point = len(recent_history) // 2
        first_half_avg = sum(h.get("score", 0) for h in recent_history[:mid_point]) / mid_point
        second_half_avg = sum(h.get("score", 0) for h in recent_history[mid_point:]) / (len(recent_history) - mid_point)
        improvement_rate = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
        
        if improvement_rate > 0.1:
            trend = "improving"
        elif improvement_rate < -0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        improvement_rate = 0.0
        trend = "insufficient_data"
    
    return {
        "trend": trend,
        "average_score": average_score,
        "accuracy_rate": accuracy_rate,
        "improvement_rate": improvement_rate,
        "total_attempts": len(history),
        "recent_attempts": len(recent_history)
    }


def _generate_adaptive_message(
    is_correct: bool,
    score: float,
    understanding_level: str,
    performance_analysis: Dict[str, Any],
    difficulty_level: str
) -> Dict[str, str]:
    """적응형 메시지 생성"""
    
    trend = performance_analysis.get("trend", "stable")
    average_score = performance_analysis.get("average_score", 0.0)
    accuracy_rate = performance_analysis.get("accuracy_rate", 0.0)
    
    # 메인 피드백
    if is_correct:
        if score >= 90:
            main = "🌟 완벽한 답변입니다!"
        elif score >= 80:
            main = "✅ 정답입니다! 잘 하셨어요."
        else:
            main = "✅ 정답입니다."
    else:
        main = "❌ 아쉽게도 정답이 아닙니다."
    
    # 추세 기반 격려 메시지
    if trend == "improving":
        encouragement = "최근 실력이 많이 향상되고 있어요! 🚀"
    elif trend == "declining":
        encouragement = "최근 조금 어려워하고 계시네요. 천천히 해보세요. 💪"
    elif trend == "stable":
        if accuracy_rate >= 0.8:
            encouragement = "꾸준히 좋은 성과를 유지하고 계시네요! 👍"
        else:
            encouragement = "꾸준히 노력하고 계시네요. 조금 더 화이팅! ⭐"
    else:
        encouragement = "새로운 도전을 시작하셨네요! 화이팅! 🎯"
    
    # 개선 팁
    tips = []
    if not is_correct:
        if difficulty_level == "hard" and average_score < 60:
            tips.append("어려운 문제입니다. 기본 개념부터 다시 확인해보세요.")
        elif accuracy_rate < 0.5:
            tips.append("기초를 더 탄탄히 다져보세요.")
        else:
            tips.append("이런 유형의 문제를 더 연습해보세요.")
    
    if understanding_level == "low" and trend != "improving":
        tips.append("개념 설명을 다시 읽어보시는 것을 추천합니다.")
    
    return {
        "main": main,
        "encouragement": encouragement,
        "tips": tips
    }


def _generate_adaptive_next_steps(
    performance_analysis: Dict[str, Any],
    is_correct: bool,
    understanding_level: str
) -> Dict[str, Any]:
    """적응형 다음 단계 제안"""
    
    trend = performance_analysis.get("trend", "stable")
    accuracy_rate = performance_analysis.get("accuracy_rate", 0.0)
    average_score = performance_analysis.get("average_score", 0.0)
    
    if is_correct and understanding_level == "high" and trend == "improving":
        # 다음 단계로 진행
        return {
            "action": "advance",
            "message": "다음 단계로 진행할 준비가 되었습니다!",
            "suggestions": [
                "더 어려운 문제에 도전하기",
                "다음 챕터로 넘어가기",
                "실제 프로젝트에 적용해보기"
            ]
        }
    elif accuracy_rate >= 0.7 and average_score >= 70:
        # 현재 수준에서 더 연습
        return {
            "action": "practice",
            "message": "이 수준에서 조금 더 연습해보세요.",
            "suggestions": [
                "비슷한 난이도 문제 더 풀어보기",
                "다양한 유형의 문제 시도하기",
                "속도 향상 연습하기"
            ]
        }
    else:
        # 복습 및 기초 강화
        return {
            "action": "review",
            "message": "기본 개념을 다시 복습해보세요.",
            "suggestions": [
                "개념 설명 다시 읽어보기",
                "쉬운 문제부터 다시 시작하기",
                "질문하기를 통해 이해 확인하기"
            ]
        }


def save_feedback_effectiveness(
    feedback_id: str,
    user_id: str,
    effectiveness_rating: int,
    user_comments: Optional[str] = None
) -> Dict[str, Any]:
    """
    피드백 효과성 저장
    
    Args:
        feedback_id: 피드백 ID
        user_id: 사용자 ID
        effectiveness_rating: 효과성 평점 (1-5)
        user_comments: 사용자 코멘트
        
    Returns:
        Dict: 저장 결과
    """
    try:
        if not 1 <= effectiveness_rating <= 5:
            return {
                "success": False,
                "error": "효과성 평점은 1-5 사이여야 합니다."
            }
        
        effectiveness_data = {
            "feedback_id": feedback_id,
            "user_id": user_id,
            "effectiveness_rating": effectiveness_rating,
            "user_comments": user_comments,
            "recorded_at": datetime.now().isoformat()
        }
        
        # 실제로는 데이터베이스에 저장
        print(f"피드백 효과성 저장: {json.dumps(effectiveness_data, ensure_ascii=False)}")
        
        return {
            "success": True,
            "message": "피드백 효과성이 기록되었습니다.",
            "record_id": f"effectiveness_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
    except Exception as e:
        print(f"피드백 효과성 저장 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_feedback_analytics(
    user_id: Optional[str] = None,
    chapter_id: Optional[int] = None,
    date_range: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    피드백 분석 데이터 조회
    
    Args:
        user_id: 사용자 ID (선택사항)
        chapter_id: 챕터 ID (선택사항)
        date_range: 날짜 범위 (선택사항)
        
    Returns:
        Dict: 피드백 분석 데이터
    """
    try:
        # 실제로는 데이터베이스에서 조회
        # 여기서는 샘플 데이터 반환
        analytics_data = {
            "total_feedbacks": 150,
            "average_effectiveness": 4.2,
            "feedback_types": {
                "comprehensive": 80,
                "quick": 50,
                "adaptive": 20
            },
            "user_satisfaction": {
                "very_satisfied": 60,
                "satisfied": 70,
                "neutral": 15,
                "dissatisfied": 4,
                "very_dissatisfied": 1
            },
            "common_improvements": [
                "더 구체적인 개선 방법 제시",
                "개인화된 학습 경로 추천",
                "실시간 힌트 품질 향상"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "analytics": analytics_data
        }
        
    except Exception as e:
        print(f"피드백 분석 조회 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }