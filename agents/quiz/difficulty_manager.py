# agents/quiz/difficulty_manager.py
# 난이도 관리 모듈

from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta


class DifficultyManager:
    """난이도 관리 클래스 - 사용자 성과에 따른 동적 난이도 조절"""
    
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.performance_weights = {
            "correct_rate": 0.4,      # 정답률
            "hint_usage": 0.3,        # 힌트 사용 빈도
            "response_time": 0.2,     # 응답 시간
            "consecutive_correct": 0.1 # 연속 정답
        }
    
    def calculate_current_difficulty(
        self, 
        user_id: str, 
        chapter_id: int,
        recent_performance: List[Dict[str, Any]]
    ) -> str:
        """
        사용자의 최근 성과를 바탕으로 현재 적절한 난이도 계산
        
        Args:
            user_id: 사용자 ID
            chapter_id: 챕터 ID
            recent_performance: 최근 퀴즈 성과 데이터
            
        Returns:
            str: 계산된 난이도 (easy/medium/hard)
        """
        try:
            if not recent_performance:
                return "medium"  # 기본 난이도
            
            # 성과 지표 계산
            performance_score = self._calculate_performance_score(recent_performance)
            
            # 난이도 결정
            if performance_score >= 0.8:
                return "hard"
            elif performance_score >= 0.5:
                return "medium"
            else:
                return "easy"
                
        except Exception as e:
            print(f"난이도 계산 오류: {e}")
            return "medium"
    
    def adjust_difficulty_based_on_answer(
        self,
        current_difficulty: str,
        is_correct: bool,
        hint_used: bool,
        response_time_seconds: Optional[int] = None
    ) -> str:
        """
        답변 결과에 따른 즉시 난이도 조정
        
        Args:
            current_difficulty: 현재 난이도
            is_correct: 정답 여부
            hint_used: 힌트 사용 여부
            response_time_seconds: 응답 시간 (초)
            
        Returns:
            str: 조정된 난이도
        """
        try:
            difficulty_index = self.difficulty_levels.index(current_difficulty)
            
            # 정답이고 힌트를 사용하지 않은 경우
            if is_correct and not hint_used:
                if response_time_seconds and response_time_seconds < 30:  # 빠른 응답
                    difficulty_index = min(difficulty_index + 1, len(self.difficulty_levels) - 1)
            
            # 오답이거나 힌트를 많이 사용한 경우
            elif not is_correct or hint_used:
                difficulty_index = max(difficulty_index - 1, 0)
            
            return self.difficulty_levels[difficulty_index]
            
        except Exception as e:
            print(f"난이도 조정 오류: {e}")
            return current_difficulty
    
    def get_difficulty_parameters(self, difficulty: str, question_type: str) -> Dict[str, Any]:
        """
        난이도별 문제 생성 파라미터 반환
        
        Args:
            difficulty: 난이도 레벨
            question_type: 문제 유형
            
        Returns:
            Dict: 난이도별 파라미터
        """
        parameters = {
            "easy": {
                "multiple_choice": {
                    "concept_complexity": "basic",
                    "distractor_similarity": "low",  # 오답 선택지 유사도
                    "context_length": "short",
                    "vocabulary_level": "simple"
                },
                "prompt_practice": {
                    "task_complexity": "simple",
                    "requirements_count": 2,
                    "context_detail": "minimal",
                    "evaluation_strictness": "lenient"
                }
            },
            "medium": {
                "multiple_choice": {
                    "concept_complexity": "intermediate",
                    "distractor_similarity": "medium",
                    "context_length": "medium",
                    "vocabulary_level": "standard"
                },
                "prompt_practice": {
                    "task_complexity": "moderate",
                    "requirements_count": 3,
                    "context_detail": "standard",
                    "evaluation_strictness": "standard"
                }
            },
            "hard": {
                "multiple_choice": {
                    "concept_complexity": "advanced",
                    "distractor_similarity": "high",
                    "context_length": "long",
                    "vocabulary_level": "advanced"
                },
                "prompt_practice": {
                    "task_complexity": "complex",
                    "requirements_count": 4,
                    "context_detail": "comprehensive",
                    "evaluation_strictness": "strict"
                }
            }
        }
        
        return parameters.get(difficulty, parameters["medium"]).get(question_type, {})
    
    def _calculate_performance_score(self, recent_performance: List[Dict[str, Any]]) -> float:
        """최근 성과 데이터를 바탕으로 성과 점수 계산"""
        if not recent_performance:
            return 0.5  # 중간 점수
        
        # 최근 10개 문제로 제한
        recent_data = recent_performance[-10:]
        
        # 정답률 계산
        correct_count = sum(1 for p in recent_data if p.get("is_correct", False))
        correct_rate = correct_count / len(recent_data)
        
        # 힌트 사용률 계산 (낮을수록 좋음)
        hint_usage_count = sum(1 for p in recent_data if p.get("hint_used", False))
        hint_usage_rate = hint_usage_count / len(recent_data)
        
        # 평균 응답 시간 계산 (적절한 시간대 선호)
        response_times = [p.get("response_time", 60) for p in recent_data if p.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 60
        
        # 응답 시간 점수 (30-120초가 적절)
        if 30 <= avg_response_time <= 120:
            time_score = 1.0
        elif avg_response_time < 30:
            time_score = 0.7  # 너무 빠름
        else:
            time_score = max(0.3, 1.0 - (avg_response_time - 120) / 300)  # 너무 느림
        
        # 연속 정답 계산
        consecutive_correct = self._calculate_consecutive_correct(recent_data)
        consecutive_score = min(consecutive_correct / 3, 1.0)  # 최대 3연속까지 고려
        
        # 가중 평균 계산
        performance_score = (
            correct_rate * self.performance_weights["correct_rate"] +
            (1 - hint_usage_rate) * self.performance_weights["hint_usage"] +
            time_score * self.performance_weights["response_time"] +
            consecutive_score * self.performance_weights["consecutive_correct"]
        )
        
        return max(0.0, min(1.0, performance_score))  # 0-1 범위로 제한
    
    def _calculate_consecutive_correct(self, performance_data: List[Dict[str, Any]]) -> int:
        """연속 정답 개수 계산"""
        consecutive = 0
        for performance in reversed(performance_data):
            if performance.get("is_correct", False):
                consecutive += 1
            else:
                break
        return consecutive
    
    def get_difficulty_feedback(self, difficulty: str, performance_score: float) -> str:
        """난이도 조정에 대한 피드백 메시지 생성"""
        feedback_messages = {
            "easy": {
                "high": "기본기가 탄탄하네요! 조금 더 도전적인 문제로 넘어가보겠습니다.",
                "medium": "꾸준히 잘 하고 계세요. 이 수준에서 조금 더 연습해보겠습니다.",
                "low": "천천히 차근차근 해보세요. 기본 개념부터 다시 정리해보겠습니다."
            },
            "medium": {
                "high": "실력이 많이 늘었네요! 더 어려운 문제에 도전해보겠습니다.",
                "medium": "적절한 수준에서 잘 학습하고 계세요.",
                "low": "조금 어려우셨나요? 좀 더 쉬운 문제로 기초를 다져보겠습니다."
            },
            "hard": {
                "high": "훌륭합니다! 고급 수준의 문제도 잘 해결하고 계세요.",
                "medium": "어려운 문제에 잘 도전하고 계세요. 계속 이 수준에서 연습해보겠습니다.",
                "low": "고급 문제가 조금 어려우셨나요? 중간 수준으로 조정해보겠습니다."
            }
        }
        
        # 성과 점수에 따른 레벨 결정
        if performance_score >= 0.8:
            level = "high"
        elif performance_score >= 0.5:
            level = "medium"
        else:
            level = "low"
        
        return feedback_messages.get(difficulty, feedback_messages["medium"]).get(level, 
            "계속 열심히 학습해보세요!")
    
    def should_provide_hint(
        self, 
        difficulty: str, 
        attempt_count: int,
        time_spent: Optional[int] = None
    ) -> bool:
        """
        힌트 제공 여부 결정
        
        Args:
            difficulty: 현재 난이도
            attempt_count: 시도 횟수
            time_spent: 소요 시간 (초)
            
        Returns:
            bool: 힌트 제공 여부
        """
        hint_thresholds = {
            "easy": {"attempts": 2, "time": 120},
            "medium": {"attempts": 1, "time": 90},
            "hard": {"attempts": 1, "time": 60}
        }
        
        threshold = hint_thresholds.get(difficulty, hint_thresholds["medium"])
        
        # 시도 횟수 기준
        if attempt_count >= threshold["attempts"]:
            return True
        
        # 시간 기준 (제공된 경우)
        if time_spent and time_spent >= threshold["time"]:
            return True
        
        return False