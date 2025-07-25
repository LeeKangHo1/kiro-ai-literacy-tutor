# tools/evaluation/answer_eval_tool.py
# 답변 평가 도구

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from agents.evaluator.answer_evaluator import AnswerEvaluator, EvaluationResult


def answer_evaluation_tool(
    question_data: Dict[str, Any],
    user_answer: Any,
    hint_used: bool = False,
    response_time: Optional[int] = None,
    chatgpt_test_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    답변 평가 도구
    
    Args:
        question_data: 문제 데이터
        user_answer: 사용자 답변
        hint_used: 힌트 사용 여부
        response_time: 응답 시간 (초)
        chatgpt_test_result: ChatGPT API 테스트 결과 (프롬프트 문제용)
        
    Returns:
        Dict: 평가 결과
    """
    try:
        evaluator = AnswerEvaluator()
        question_type = question_data.get("question_type", "multiple_choice")
        
        # 문제 유형별 평가 실행
        if question_type == "multiple_choice":
            if not isinstance(user_answer, int):
                return {
                    "success": False,
                    "error": "객관식 답변은 정수형이어야 합니다.",
                    "evaluation_result": None
                }
            
            evaluation_result = evaluator.evaluate_multiple_choice_answer(
                question_data, user_answer, hint_used, response_time
            )
            
        elif question_type == "prompt_practice":
            if not isinstance(user_answer, str):
                return {
                    "success": False,
                    "error": "프롬프트 답변은 문자열이어야 합니다.",
                    "evaluation_result": None
                }
            
            evaluation_result = evaluator.evaluate_prompt_answer(
                question_data, user_answer, hint_used, response_time, chatgpt_test_result
            )
            
        else:
            return {
                "success": False,
                "error": f"지원하지 않는 문제 유형: {question_type}",
                "evaluation_result": None
            }
        
        # 평가 결과 후처리
        processed_result = _process_evaluation_result(evaluation_result, question_data)
        
        return {
            "success": True,
            "evaluation_result": processed_result,
            "evaluated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"답변 평가 도구 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "evaluation_result": None
        }


def _process_evaluation_result(
    evaluation_result: EvaluationResult, 
    question_data: Dict[str, Any]
) -> Dict[str, Any]:
    """평가 결과 후처리"""
    
    return {
        "is_correct": evaluation_result.is_correct,
        "score": evaluation_result.score,
        "understanding_level": evaluation_result.understanding_level,
        "strengths": evaluation_result.strengths,
        "weaknesses": evaluation_result.weaknesses,
        "detailed_analysis": evaluation_result.detailed_analysis,
        "question_id": question_data.get("question_id"),
        "question_type": question_data.get("question_type"),
        "difficulty": question_data.get("difficulty")
    }


def batch_evaluate_answers(
    questions_and_answers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    여러 답변 일괄 평가
    
    Args:
        questions_and_answers: 문제와 답변 쌍의 리스트
        
    Returns:
        Dict: 일괄 평가 결과
    """
    try:
        evaluator = AnswerEvaluator()
        results = []
        total_score = 0.0
        correct_count = 0
        
        for item in questions_and_answers:
            question_data = item.get("question_data", {})
            user_answer = item.get("user_answer")
            hint_used = item.get("hint_used", False)
            response_time = item.get("response_time")
            
            # 개별 평가 실행
            eval_result = answer_evaluation_tool(
                question_data, user_answer, hint_used, response_time
            )
            
            if eval_result.get("success", False):
                evaluation = eval_result["evaluation_result"]
                results.append(evaluation)
                total_score += evaluation["score"]
                if evaluation["is_correct"]:
                    correct_count += 1
        
        # 통계 계산
        total_questions = len(results)
        average_score = total_score / total_questions if total_questions > 0 else 0
        accuracy_rate = correct_count / total_questions if total_questions > 0 else 0
        
        # 전체 이해도 수준 결정
        overall_understanding = _determine_overall_understanding(results)
        
        return {
            "success": True,
            "batch_results": results,
            "statistics": {
                "total_questions": total_questions,
                "correct_count": correct_count,
                "accuracy_rate": accuracy_rate,
                "average_score": average_score,
                "overall_understanding": overall_understanding
            },
            "evaluated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"일괄 평가 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _determine_overall_understanding(results: List[Dict[str, Any]]) -> str:
    """전체 이해도 수준 결정"""
    if not results:
        return "unknown"
    
    understanding_levels = [r.get("understanding_level", "low") for r in results]
    level_counts = {
        "high": understanding_levels.count("high"),
        "medium": understanding_levels.count("medium"),
        "low": understanding_levels.count("low")
    }
    
    total = len(understanding_levels)
    
    if level_counts["high"] / total >= 0.6:
        return "high"
    elif level_counts["medium"] / total >= 0.5:
        return "medium"
    else:
        return "low"


def calculate_learning_progress(
    user_id: str,
    chapter_id: int,
    evaluation_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    학습 진도 계산
    
    Args:
        user_id: 사용자 ID
        chapter_id: 챕터 ID
        evaluation_results: 평가 결과 리스트
        
    Returns:
        Dict: 학습 진도 정보
    """
    try:
        if not evaluation_results:
            return {
                "success": False,
                "error": "평가 결과가 없습니다."
            }
        
        # 최근 성과 분석
        recent_results = evaluation_results[-10:]  # 최근 10개
        
        # 정확도 추세 계산
        accuracy_trend = _calculate_accuracy_trend(recent_results)
        
        # 이해도 발전 추세
        understanding_trend = _calculate_understanding_trend(recent_results)
        
        # 평균 점수
        average_score = sum(r.get("score", 0) for r in recent_results) / len(recent_results)
        
        # 강점/약점 분석
        strengths_analysis = _analyze_strengths_weaknesses(recent_results, "strengths")
        weaknesses_analysis = _analyze_strengths_weaknesses(recent_results, "weaknesses")
        
        # 진도율 계산 (임시 - 실제로는 챕터별 목표 대비)
        completion_rate = min(100.0, len(evaluation_results) * 10)  # 10문제당 100%
        
        return {
            "success": True,
            "progress_data": {
                "user_id": user_id,
                "chapter_id": chapter_id,
                "completion_rate": completion_rate,
                "average_score": average_score,
                "accuracy_trend": accuracy_trend,
                "understanding_trend": understanding_trend,
                "strengths_summary": strengths_analysis,
                "weaknesses_summary": weaknesses_analysis,
                "total_attempts": len(evaluation_results),
                "recent_performance": recent_results[-5:],  # 최근 5개
                "calculated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"학습 진도 계산 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _calculate_accuracy_trend(results: List[Dict[str, Any]]) -> str:
    """정확도 추세 계산"""
    if len(results) < 3:
        return "insufficient_data"
    
    # 전반부와 후반부 비교
    mid_point = len(results) // 2
    first_half = results[:mid_point]
    second_half = results[mid_point:]
    
    first_accuracy = sum(1 for r in first_half if r.get("is_correct", False)) / len(first_half)
    second_accuracy = sum(1 for r in second_half if r.get("is_correct", False)) / len(second_half)
    
    if second_accuracy > first_accuracy + 0.1:
        return "improving"
    elif second_accuracy < first_accuracy - 0.1:
        return "declining"
    else:
        return "stable"


def _calculate_understanding_trend(results: List[Dict[str, Any]]) -> str:
    """이해도 추세 계산"""
    if len(results) < 3:
        return "insufficient_data"
    
    understanding_scores = {
        "high": 3,
        "medium": 2,
        "low": 1
    }
    
    # 전반부와 후반부 비교
    mid_point = len(results) // 2
    first_half = results[:mid_point]
    second_half = results[mid_point:]
    
    first_avg = sum(understanding_scores.get(r.get("understanding_level", "low"), 1) for r in first_half) / len(first_half)
    second_avg = sum(understanding_scores.get(r.get("understanding_level", "low"), 1) for r in second_half) / len(second_half)
    
    if second_avg > first_avg + 0.3:
        return "improving"
    elif second_avg < first_avg - 0.3:
        return "declining"
    else:
        return "stable"


def _analyze_strengths_weaknesses(results: List[Dict[str, Any]], category: str) -> List[str]:
    """강점/약점 분석"""
    all_items = []
    for result in results:
        items = result.get(category, [])
        all_items.extend(items)
    
    # 빈도 계산
    item_counts = {}
    for item in all_items:
        item_counts[item] = item_counts.get(item, 0) + 1
    
    # 상위 5개 반환
    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items[:5]]


def generate_performance_report(
    user_id: str,
    chapter_id: int,
    evaluation_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    성과 보고서 생성
    
    Args:
        user_id: 사용자 ID
        chapter_id: 챕터 ID
        evaluation_results: 평가 결과 리스트
        
    Returns:
        Dict: 성과 보고서
    """
    try:
        progress_result = calculate_learning_progress(user_id, chapter_id, evaluation_results)
        
        if not progress_result.get("success", False):
            return progress_result
        
        progress_data = progress_result["progress_data"]
        
        # 보고서 생성
        report = {
            "report_id": f"report_{user_id}_{chapter_id}_{datetime.now().strftime('%Y%m%d')}",
            "user_id": user_id,
            "chapter_id": chapter_id,
            "summary": {
                "completion_rate": progress_data["completion_rate"],
                "average_score": progress_data["average_score"],
                "total_attempts": progress_data["total_attempts"],
                "overall_trend": progress_data["accuracy_trend"]
            },
            "detailed_analysis": progress_data,
            "recommendations": _generate_recommendations(progress_data),
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "report": report
        }
        
    except Exception as e:
        print(f"성과 보고서 생성 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _generate_recommendations(progress_data: Dict[str, Any]) -> List[str]:
    """추천사항 생성"""
    recommendations = []
    
    average_score = progress_data.get("average_score", 0)
    accuracy_trend = progress_data.get("accuracy_trend", "stable")
    understanding_trend = progress_data.get("understanding_trend", "stable")
    
    # 점수 기반 추천
    if average_score >= 90:
        recommendations.append("훌륭한 성과입니다! 다음 챕터로 진행하세요.")
    elif average_score >= 70:
        recommendations.append("좋은 성과입니다. 조금 더 연습 후 다음 단계로 진행하세요.")
    else:
        recommendations.append("기본 개념을 더 연습하시기 바랍니다.")
    
    # 추세 기반 추천
    if accuracy_trend == "improving":
        recommendations.append("실력이 향상되고 있습니다. 현재 학습 방법을 유지하세요.")
    elif accuracy_trend == "declining":
        recommendations.append("최근 성과가 하락했습니다. 기초 개념을 다시 복습해보세요.")
    
    if understanding_trend == "improving":
        recommendations.append("이해도가 깊어지고 있습니다. 심화 문제에 도전해보세요.")
    
    return recommendations