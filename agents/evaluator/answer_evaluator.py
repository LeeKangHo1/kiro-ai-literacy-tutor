# agents/evaluator/answer_evaluator.py
# 답변 평가 모듈

from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """평가 결과 데이터 클래스"""
    is_correct: bool
    score: float
    understanding_level: str  # low, medium, high
    strengths: List[str]
    weaknesses: List[str]
    detailed_analysis: Dict[str, Any]


class AnswerEvaluator:
    """답변 평가 클래스 - 객관식 및 프롬프트 답변 채점 및 이해도 측정"""
    
    def __init__(self):
        self.evaluation_criteria = self._load_evaluation_criteria()
        self.understanding_thresholds = {
            "low": 0.4,
            "medium": 0.7,
            "high": 0.9
        }
    
    def evaluate_multiple_choice_answer(
        self,
        question_data: Dict[str, Any],
        user_answer: int,
        hint_used: bool = False,
        response_time: Optional[int] = None
    ) -> EvaluationResult:
        """
        객관식 답변 평가
        
        Args:
            question_data: 문제 데이터
            user_answer: 사용자 답변 (선택지 인덱스)
            hint_used: 힌트 사용 여부
            response_time: 응답 시간 (초)
            
        Returns:
            EvaluationResult: 평가 결과
        """
        try:
            correct_answer = question_data.get("correct_answer", 0)
            options = question_data.get("options", [])
            difficulty = question_data.get("difficulty", "medium")
            
            # 기본 정답 여부 확인
            is_correct = user_answer == correct_answer
            
            # 기본 점수 계산
            base_score = 100.0 if is_correct else 0.0
            
            # 점수 조정 요소들
            score_adjustments = self._calculate_score_adjustments(
                is_correct, hint_used, response_time, difficulty
            )
            
            final_score = max(0.0, min(100.0, base_score + score_adjustments))
            
            # 이해도 수준 결정
            understanding_level = self._determine_understanding_level(
                is_correct, hint_used, response_time, difficulty, final_score
            )
            
            # 강점과 약점 분석
            strengths, weaknesses = self._analyze_mc_performance(
                is_correct, hint_used, response_time, difficulty, user_answer, correct_answer
            )
            
            # 상세 분석
            detailed_analysis = {
                "question_type": "multiple_choice",
                "difficulty": difficulty,
                "correct_answer_index": correct_answer,
                "user_answer_index": user_answer,
                "selected_option": options[user_answer] if user_answer < len(options) else "Invalid",
                "correct_option": options[correct_answer] if correct_answer < len(options) else "Unknown",
                "hint_penalty": -10 if hint_used else 0,
                "time_bonus": self._calculate_time_bonus(response_time, difficulty),
                "base_score": base_score,
                "final_score": final_score
            }
            
            return EvaluationResult(
                is_correct=is_correct,
                score=final_score,
                understanding_level=understanding_level,
                strengths=strengths,
                weaknesses=weaknesses,
                detailed_analysis=detailed_analysis
            )
            
        except Exception as e:
            print(f"객관식 답변 평가 오류: {e}")
            return self._create_error_evaluation_result()
    
    def evaluate_prompt_answer(
        self,
        question_data: Dict[str, Any],
        user_answer: str,
        hint_used: bool = False,
        response_time: Optional[int] = None,
        chatgpt_test_result: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        프롬프트 답변 평가
        
        Args:
            question_data: 문제 데이터
            user_answer: 사용자가 작성한 프롬프트
            hint_used: 힌트 사용 여부
            response_time: 응답 시간 (초)
            chatgpt_test_result: ChatGPT API 테스트 결과
            
        Returns:
            EvaluationResult: 평가 결과
        """
        try:
            requirements = question_data.get("requirements", [])
            evaluation_criteria = question_data.get("evaluation_criteria", [])
            difficulty = question_data.get("difficulty", "medium")
            
            # 요구사항 충족도 평가
            requirements_score = self._evaluate_requirements_fulfillment(user_answer, requirements)
            
            # 프롬프트 품질 평가
            quality_score = self._evaluate_prompt_quality(user_answer, evaluation_criteria)
            
            # ChatGPT 테스트 결과 평가 (있는 경우)
            effectiveness_score = self._evaluate_prompt_effectiveness(chatgpt_test_result)
            
            # 종합 점수 계산
            base_score = (requirements_score * 0.4 + quality_score * 0.4 + effectiveness_score * 0.2)
            
            # 점수 조정
            score_adjustments = self._calculate_prompt_score_adjustments(
                hint_used, response_time, difficulty, len(user_answer)
            )
            
            final_score = max(0.0, min(100.0, base_score + score_adjustments))
            
            # 정답 여부 (70점 이상을 정답으로 간주)
            is_correct = final_score >= 70.0
            
            # 이해도 수준 결정
            understanding_level = self._determine_prompt_understanding_level(
                final_score, requirements_score, quality_score, effectiveness_score
            )
            
            # 강점과 약점 분석
            strengths, weaknesses = self._analyze_prompt_performance(
                user_answer, requirements, requirements_score, quality_score, effectiveness_score
            )
            
            # 상세 분석
            detailed_analysis = {
                "question_type": "prompt_practice",
                "difficulty": difficulty,
                "user_prompt": user_answer,
                "prompt_length": len(user_answer),
                "word_count": len(user_answer.split()),
                "requirements_score": requirements_score,
                "quality_score": quality_score,
                "effectiveness_score": effectiveness_score,
                "base_score": base_score,
                "final_score": final_score,
                "requirements_analysis": self._analyze_requirements_detail(user_answer, requirements),
                "chatgpt_test_result": chatgpt_test_result
            }
            
            return EvaluationResult(
                is_correct=is_correct,
                score=final_score,
                understanding_level=understanding_level,
                strengths=strengths,
                weaknesses=weaknesses,
                detailed_analysis=detailed_analysis
            )
            
        except Exception as e:
            print(f"프롬프트 답변 평가 오류: {e}")
            return self._create_error_evaluation_result()
    
    def _calculate_score_adjustments(
        self, 
        is_correct: bool, 
        hint_used: bool, 
        response_time: Optional[int], 
        difficulty: str
    ) -> float:
        """점수 조정 계산"""
        adjustments = 0.0
        
        # 힌트 사용 페널티
        if hint_used:
            penalty_map = {"easy": -5, "medium": -10, "hard": -15}
            adjustments += penalty_map.get(difficulty, -10)
        
        # 응답 시간 보너스/페널티
        if response_time and is_correct:
            time_adjustment = self._calculate_time_bonus(response_time, difficulty)
            adjustments += time_adjustment
        
        return adjustments
    
    def _calculate_time_bonus(self, response_time: Optional[int], difficulty: str) -> float:
        """응답 시간 기반 보너스 계산"""
        if not response_time:
            return 0.0
        
        # 난이도별 적정 시간 (초)
        optimal_times = {"easy": 30, "medium": 60, "hard": 120}
        optimal_time = optimal_times.get(difficulty, 60)
        
        if response_time <= optimal_time:
            # 빠른 응답 보너스
            return min(10.0, (optimal_time - response_time) / optimal_time * 10)
        elif response_time <= optimal_time * 2:
            # 적정 시간 내
            return 0.0
        else:
            # 느린 응답 페널티
            return max(-5.0, -((response_time - optimal_time * 2) / optimal_time))
    
    def _determine_understanding_level(
        self, 
        is_correct: bool, 
        hint_used: bool, 
        response_time: Optional[int], 
        difficulty: str,
        final_score: float
    ) -> str:
        """이해도 수준 결정"""
        
        # 기본 점수 기반 판단
        if final_score >= 90:
            base_level = "high"
        elif final_score >= 70:
            base_level = "medium"
        else:
            base_level = "low"
        
        # 추가 요소 고려
        if not is_correct:
            return "low"
        
        if hint_used and base_level == "high":
            base_level = "medium"
        
        if response_time and difficulty == "easy" and response_time > 120:
            if base_level == "high":
                base_level = "medium"
        
        return base_level
    
    def _analyze_mc_performance(
        self, 
        is_correct: bool, 
        hint_used: bool, 
        response_time: Optional[int], 
        difficulty: str,
        user_answer: int,
        correct_answer: int
    ) -> Tuple[List[str], List[str]]:
        """객관식 성과 분석"""
        
        strengths = []
        weaknesses = []
        
        if is_correct:
            strengths.append("정답을 정확히 선택했습니다")
            if not hint_used:
                strengths.append("힌트 없이 스스로 해결했습니다")
            if response_time and response_time <= 60:
                strengths.append("빠른 시간 내에 답을 찾았습니다")
        else:
            weaknesses.append("정답을 선택하지 못했습니다")
            
        if hint_used:
            weaknesses.append("힌트가 필요했습니다")
            
        if response_time and response_time > 180:
            weaknesses.append("문제 해결에 시간이 오래 걸렸습니다")
            
        # 난이도별 추가 분석
        if difficulty == "hard" and is_correct:
            strengths.append("어려운 문제를 잘 해결했습니다")
        elif difficulty == "easy" and not is_correct:
            weaknesses.append("기본 개념 이해가 부족합니다")
            
        return strengths, weaknesses
    
    def _evaluate_requirements_fulfillment(self, user_answer: str, requirements: List[str]) -> float:
        """요구사항 충족도 평가"""
        if not requirements:
            return 80.0  # 기본 점수
        
        fulfilled_count = 0
        total_requirements = len(requirements)
        
        for requirement in requirements:
            if self._check_requirement_fulfillment(user_answer, requirement):
                fulfilled_count += 1
        
        return (fulfilled_count / total_requirements) * 100 if total_requirements > 0 else 80.0
    
    def _check_requirement_fulfillment(self, user_answer: str, requirement: str) -> bool:
        """개별 요구사항 충족 여부 확인"""
        user_answer_lower = user_answer.lower()
        requirement_lower = requirement.lower()
        
        # 키워드 기반 간단한 체크
        if "역할" in requirement_lower or "role" in requirement_lower:
            return "당신은" in user_answer or "you are" in user_answer_lower or "역할" in user_answer
        
        if "톤" in requirement_lower or "tone" in requirement_lower:
            tone_keywords = ["친근", "정중", "전문적", "친절", "공감", "따뜻"]
            return any(keyword in user_answer for keyword in tone_keywords)
        
        if "구체적" in requirement_lower or "specific" in requirement_lower:
            return len(user_answer.split()) > 20  # 단어 수 기준
        
        if "예시" in requirement_lower or "example" in requirement_lower:
            return "예를 들어" in user_answer or "예시" in user_answer or "for example" in user_answer_lower
        
        if "단계" in requirement_lower or "step" in requirement_lower:
            step_indicators = ["1.", "2.", "첫째", "둘째", "먼저", "다음", "step"]
            return any(indicator in user_answer_lower for indicator in step_indicators)
        
        # 기본적으로 충족으로 가정 (더 정교한 분석 필요)
        return True
    
    def _evaluate_prompt_quality(self, user_answer: str, evaluation_criteria: List[str]) -> float:
        """프롬프트 품질 평가"""
        quality_score = 0.0
        criteria_count = len(evaluation_criteria) if evaluation_criteria else 3
        
        # 기본 품질 지표들
        quality_indicators = {
            "clarity": self._check_clarity(user_answer),
            "completeness": self._check_completeness(user_answer),
            "structure": self._check_structure(user_answer)
        }
        
        # 평가 기준별 점수 계산
        for criterion in evaluation_criteria:
            if "명확" in criterion or "clarity" in criterion.lower():
                quality_score += quality_indicators["clarity"]
            elif "완성도" in criterion or "completeness" in criterion.lower():
                quality_score += quality_indicators["completeness"]
            elif "구조" in criterion or "structure" in criterion.lower():
                quality_score += quality_indicators["structure"]
            else:
                quality_score += 70.0  # 기본 점수
        
        # 기준이 없으면 기본 지표들의 평균 사용
        if not evaluation_criteria:
            quality_score = sum(quality_indicators.values()) / len(quality_indicators)
        else:
            quality_score = quality_score / criteria_count
        
        return min(100.0, quality_score)
    
    def _check_clarity(self, user_answer: str) -> float:
        """명확성 체크"""
        score = 50.0  # 기본 점수
        
        # 길이 적절성
        word_count = len(user_answer.split())
        if 20 <= word_count <= 200:
            score += 20
        
        # 문장 구조
        sentences = user_answer.split('.')
        if len(sentences) >= 2:
            score += 15
        
        # 구체적 지시어 사용
        specific_words = ["구체적으로", "정확히", "명확히", "자세히"]
        if any(word in user_answer for word in specific_words):
            score += 15
        
        return min(100.0, score)
    
    def _check_completeness(self, user_answer: str) -> float:
        """완성도 체크"""
        score = 50.0  # 기본 점수
        
        # 역할 정의 포함
        if "당신은" in user_answer or "역할" in user_answer:
            score += 20
        
        # 맥락 정보 포함
        context_words = ["상황", "배경", "맥락", "환경"]
        if any(word in user_answer for word in context_words):
            score += 15
        
        # 출력 형식 지정
        format_words = ["형식", "형태", "방식", "구조"]
        if any(word in user_answer for word in format_words):
            score += 15
        
        return min(100.0, score)
    
    def _check_structure(self, user_answer: str) -> float:
        """구조성 체크"""
        score = 50.0  # 기본 점수
        
        # 단락 구분
        paragraphs = user_answer.split('\n')
        if len(paragraphs) >= 2:
            score += 20
        
        # 순서 지시어
        order_words = ["먼저", "다음", "마지막", "1.", "2.", "3."]
        if any(word in user_answer for word in order_words):
            score += 15
        
        # 논리적 연결어
        connectors = ["따라서", "그러므로", "또한", "그리고", "하지만"]
        if any(word in user_answer for word in connectors):
            score += 15
        
        return min(100.0, score)
    
    def _evaluate_prompt_effectiveness(self, chatgpt_test_result: Optional[Dict[str, Any]]) -> float:
        """프롬프트 효과성 평가 (ChatGPT 테스트 결과 기반)"""
        if not chatgpt_test_result:
            return 70.0  # 기본 점수
        
        if not chatgpt_test_result.get("success", False):
            return 30.0  # 실패 시 낮은 점수
        
        response = chatgpt_test_result.get("response", "")
        
        # 응답 품질 기반 점수
        if len(response) < 50:
            return 40.0  # 너무 짧은 응답
        elif len(response) > 2000:
            return 60.0  # 너무 긴 응답
        else:
            return 85.0  # 적절한 응답
    
    def _calculate_prompt_score_adjustments(
        self, 
        hint_used: bool, 
        response_time: Optional[int], 
        difficulty: str,
        prompt_length: int
    ) -> float:
        """프롬프트 점수 조정"""
        adjustments = 0.0
        
        # 힌트 사용 페널티
        if hint_used:
            penalty_map = {"easy": -5, "medium": -8, "hard": -12}
            adjustments += penalty_map.get(difficulty, -8)
        
        # 길이 적절성 보너스/페널티
        if 50 <= prompt_length <= 500:
            adjustments += 5
        elif prompt_length < 20:
            adjustments -= 10
        elif prompt_length > 1000:
            adjustments -= 5
        
        # 응답 시간 조정
        if response_time:
            time_adjustment = self._calculate_time_bonus(response_time, difficulty)
            adjustments += time_adjustment * 0.5  # 프롬프트는 시간 가중치 낮춤
        
        return adjustments
    
    def _determine_prompt_understanding_level(
        self, 
        final_score: float, 
        requirements_score: float, 
        quality_score: float, 
        effectiveness_score: float
    ) -> str:
        """프롬프트 이해도 수준 결정"""
        
        # 종합 점수 기반
        if final_score >= 85:
            return "high"
        elif final_score >= 65:
            return "medium"
        else:
            return "low"
    
    def _analyze_prompt_performance(
        self, 
        user_answer: str, 
        requirements: List[str], 
        requirements_score: float, 
        quality_score: float, 
        effectiveness_score: float
    ) -> Tuple[List[str], List[str]]:
        """프롬프트 성과 분석"""
        
        strengths = []
        weaknesses = []
        
        # 요구사항 충족도 분석
        if requirements_score >= 80:
            strengths.append("요구사항을 잘 충족했습니다")
        elif requirements_score < 50:
            weaknesses.append("요구사항 충족도가 부족합니다")
        
        # 품질 분석
        if quality_score >= 80:
            strengths.append("프롬프트 품질이 우수합니다")
        elif quality_score < 60:
            weaknesses.append("프롬프트 구조와 명확성을 개선해야 합니다")
        
        # 효과성 분석
        if effectiveness_score >= 80:
            strengths.append("실제 AI와의 상호작용에서 효과적입니다")
        elif effectiveness_score < 60:
            weaknesses.append("AI 응답 품질을 높이는 방향으로 개선이 필요합니다")
        
        # 길이 분석
        word_count = len(user_answer.split())
        if 30 <= word_count <= 150:
            strengths.append("적절한 길이의 프롬프트입니다")
        elif word_count < 20:
            weaknesses.append("프롬프트가 너무 짧습니다")
        elif word_count > 200:
            weaknesses.append("프롬프트가 너무 길어 복잡할 수 있습니다")
        
        return strengths, weaknesses
    
    def _analyze_requirements_detail(self, user_answer: str, requirements: List[str]) -> Dict[str, bool]:
        """요구사항 상세 분석"""
        analysis = {}
        for requirement in requirements:
            analysis[requirement] = self._check_requirement_fulfillment(user_answer, requirement)
        return analysis
    
    def _create_error_evaluation_result(self) -> EvaluationResult:
        """오류 시 기본 평가 결과 생성"""
        return EvaluationResult(
            is_correct=False,
            score=0.0,
            understanding_level="low",
            strengths=[],
            weaknesses=["평가 중 오류가 발생했습니다"],
            detailed_analysis={"error": "evaluation_failed"}
        )
    
    def _load_evaluation_criteria(self) -> Dict[str, Any]:
        """평가 기준 로드"""
        return {
            "multiple_choice": {
                "correct_weight": 0.8,
                "time_weight": 0.1,
                "hint_penalty": 0.1
            },
            "prompt_practice": {
                "requirements_weight": 0.4,
                "quality_weight": 0.4,
                "effectiveness_weight": 0.2
            }
        }