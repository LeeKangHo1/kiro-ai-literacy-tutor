# agents/evaluator/feedback_generator.py
# 피드백 생성 모듈

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from .answer_evaluator import EvaluationResult


class FeedbackGenerator:
    """피드백 생성 클래스 - 개인화된 학습 피드백 생성"""
    
    def __init__(self):
        self.feedback_templates = self._load_feedback_templates()
        self.encouragement_messages = self._load_encouragement_messages()
        self.improvement_suggestions = self._load_improvement_suggestions()
    
    def generate_comprehensive_feedback(
        self,
        evaluation_result: EvaluationResult,
        question_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        learning_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        종합적인 개인화 피드백 생성
        
        Args:
            evaluation_result: 평가 결과
            question_data: 문제 데이터
            user_profile: 사용자 프로필 (레벨, 유형 등)
            learning_context: 학습 맥락 (진도, 최근 성과 등)
            
        Returns:
            Dict: 생성된 피드백 데이터
        """
        try:
            question_type = question_data.get("question_type", "multiple_choice")
            
            # 기본 피드백 구성 요소 생성
            main_feedback = self._generate_main_feedback(evaluation_result, question_data)
            encouragement = self._generate_encouragement(evaluation_result, user_profile)
            improvement_tips = self._generate_improvement_tips(evaluation_result, question_data, user_profile)
            next_steps = self._generate_next_steps(evaluation_result, learning_context)
            
            # 개인화 요소 추가
            personalized_message = self._generate_personalized_message(
                evaluation_result, user_profile, learning_context
            )
            
            # UI 요소 생성
            ui_elements = self._generate_feedback_ui_elements(
                evaluation_result, question_type, question_data
            )
            
            feedback_data = {
                "feedback_id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question_id": question_data.get("question_id"),
                "evaluation_result": evaluation_result.__dict__,
                "main_feedback": main_feedback,
                "encouragement": encouragement,
                "improvement_tips": improvement_tips,
                "next_steps": next_steps,
                "personalized_message": personalized_message,
                "ui_elements": ui_elements,
                "generated_at": datetime.now().isoformat()
            }
            
            return feedback_data
            
        except Exception as e:
            print(f"종합 피드백 생성 오류: {e}")
            return self._generate_error_feedback()
    
    def _generate_main_feedback(
        self, 
        evaluation_result: EvaluationResult, 
        question_data: Dict[str, Any]
    ) -> str:
        """메인 피드백 메시지 생성"""
        
        question_type = question_data.get("question_type", "multiple_choice")
        is_correct = evaluation_result.is_correct
        score = evaluation_result.score
        understanding_level = evaluation_result.understanding_level
        
        if question_type == "multiple_choice":
            return self._generate_mc_main_feedback(is_correct, score, understanding_level, question_data)
        elif question_type == "prompt_practice":
            return self._generate_prompt_main_feedback(evaluation_result, question_data)
        else:
            return "답변을 검토했습니다."
    
    def _generate_mc_main_feedback(
        self, 
        is_correct: bool, 
        score: float, 
        understanding_level: str,
        question_data: Dict[str, Any]
    ) -> str:
        """객관식 메인 피드백 생성"""
        
        if is_correct:
            if score >= 90:
                feedback = "🎉 정답입니다! 완벽하게 이해하고 계시네요."
            elif score >= 80:
                feedback = "✅ 정답입니다! 잘 하셨어요."
            else:
                feedback = "✅ 정답입니다. 조금 더 빠르게 답할 수 있도록 연습해보세요."
        else:
            user_answer_idx = question_data.get("user_answer", -1)
            correct_answer_idx = question_data.get("correct_answer", 0)
            options = question_data.get("options", [])
            
            if user_answer_idx < len(options) and correct_answer_idx < len(options):
                feedback = f"""
❌ 아쉽게도 정답이 아닙니다.

**선택하신 답:** {user_answer_idx + 1}번 - {options[user_answer_idx]}
**정답:** {correct_answer_idx + 1}번 - {options[correct_answer_idx]}

**설명:** {question_data.get('explanation', '정답에 대한 설명이 없습니다.')}
                """.strip()
            else:
                feedback = "❌ 정답이 아닙니다. 다시 한 번 생각해보세요."
        
        return feedback
    
    def _generate_prompt_main_feedback(
        self, 
        evaluation_result: EvaluationResult, 
        question_data: Dict[str, Any]
    ) -> str:
        """프롬프트 메인 피드백 생성"""
        
        score = evaluation_result.score
        detailed_analysis = evaluation_result.detailed_analysis
        
        if score >= 85:
            main_message = "🌟 훌륭한 프롬프트입니다! 매우 잘 작성하셨네요."
        elif score >= 70:
            main_message = "👍 좋은 프롬프트입니다! 기본 요구사항을 잘 충족했습니다."
        elif score >= 50:
            main_message = "📝 괜찮은 시도입니다. 몇 가지 개선점이 있어요."
        else:
            main_message = "💪 좋은 시도였습니다! 함께 더 나은 프롬프트를 만들어보세요."
        
        # 점수 세부 분석 추가
        requirements_score = detailed_analysis.get("requirements_score", 0)
        quality_score = detailed_analysis.get("quality_score", 0)
        effectiveness_score = detailed_analysis.get("effectiveness_score", 0)
        
        analysis_text = f"""
**평가 결과:**
• 요구사항 충족도: {requirements_score:.0f}점
• 프롬프트 품질: {quality_score:.0f}점
• 실행 효과성: {effectiveness_score:.0f}점
• **종합 점수: {score:.0f}점**
        """.strip()
        
        return f"{main_message}\n\n{analysis_text}"
    
    def _generate_encouragement(
        self, 
        evaluation_result: EvaluationResult, 
        user_profile: Dict[str, Any]
    ) -> str:
        """격려 메시지 생성"""
        
        is_correct = evaluation_result.is_correct
        understanding_level = evaluation_result.understanding_level
        user_level = user_profile.get("user_level", "medium")
        user_type = user_profile.get("user_type", "beginner")
        
        # 성과에 따른 격려 메시지 선택
        if is_correct and understanding_level == "high":
            encouragement_type = "excellent"
        elif is_correct:
            encouragement_type = "good"
        elif understanding_level == "medium":
            encouragement_type = "improving"
        else:
            encouragement_type = "supportive"
        
        # 사용자 유형별 맞춤 메시지
        messages = self.encouragement_messages.get(user_type, {}).get(encouragement_type, [])
        if not messages:
            messages = self.encouragement_messages.get("beginner", {}).get(encouragement_type, ["계속 노력하세요!"])
        
        return random.choice(messages)
    
    def _generate_improvement_tips(
        self, 
        evaluation_result: EvaluationResult, 
        question_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """개선 팁 생성"""
        
        tips = []
        weaknesses = evaluation_result.weaknesses
        question_type = question_data.get("question_type", "multiple_choice")
        understanding_level = evaluation_result.understanding_level
        
        # 약점 기반 개선 팁
        for weakness in weaknesses:
            if "정답을 선택하지 못했습니다" in weakness:
                tips.append("문제를 천천히 읽고 핵심 키워드를 찾아보세요.")
                tips.append("각 선택지를 문제와 연결해서 생각해보세요.")
            elif "힌트가 필요했습니다" in weakness:
                tips.append("기본 개념을 더 확실히 익혀보세요.")
                tips.append("비슷한 유형의 문제를 더 연습해보세요.")
            elif "시간이 오래 걸렸습니다" in weakness:
                tips.append("핵심 개념을 빠르게 파악하는 연습을 해보세요.")
                tips.append("문제 유형별 해결 패턴을 익혀보세요.")
        
        # 문제 유형별 추가 팁
        if question_type == "prompt_practice":
            detailed_analysis = evaluation_result.detailed_analysis
            requirements_score = detailed_analysis.get("requirements_score", 0)
            quality_score = detailed_analysis.get("quality_score", 0)
            
            if requirements_score < 70:
                tips.append("요구사항을 하나씩 체크하며 프롬프트를 작성해보세요.")
                tips.append("역할, 맥락, 출력 형식을 명확히 지정해보세요.")
            
            if quality_score < 70:
                tips.append("더 구체적이고 명확한 지시사항을 포함해보세요.")
                tips.append("프롬프트의 구조를 논리적으로 정리해보세요.")
        
        # 이해도 수준별 추가 팁
        if understanding_level == "low":
            tips.append("기본 개념부터 차근차근 다시 학습해보세요.")
            tips.append("쉬운 문제부터 단계적으로 연습해보세요.")
        elif understanding_level == "medium":
            tips.append("조금 더 도전적인 문제에 도전해보세요.")
            tips.append("실제 상황에 적용해보는 연습을 해보세요.")
        
        # 중복 제거 및 최대 5개로 제한
        unique_tips = list(dict.fromkeys(tips))  # 중복 제거
        return unique_tips[:5]
    
    def _generate_next_steps(
        self, 
        evaluation_result: EvaluationResult, 
        learning_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """다음 단계 제안 생성"""
        
        is_correct = evaluation_result.is_correct
        understanding_level = evaluation_result.understanding_level
        current_chapter = learning_context.get("current_chapter", 1)
        
        if is_correct and understanding_level == "high":
            # 다음 단계로 진행
            next_action = "continue"
            message = "다음 개념으로 넘어가거나 더 어려운 문제에 도전해보세요!"
            suggestions = [
                "다음 챕터 학습하기",
                "심화 문제 풀어보기",
                "실제 프로젝트에 적용해보기"
            ]
        elif is_correct:
            # 현재 수준에서 더 연습
            next_action = "practice_more"
            message = "이 수준에서 조금 더 연습한 후 다음 단계로 넘어가세요."
            suggestions = [
                "비슷한 난이도 문제 더 풀어보기",
                "개념 복습하기",
                "다른 유형 문제 시도해보기"
            ]
        else:
            # 복습 및 재학습
            next_action = "review"
            message = "기본 개념을 다시 복습하고 비슷한 문제를 더 연습해보세요."
            suggestions = [
                "개념 설명 다시 읽어보기",
                "쉬운 문제부터 다시 시작하기",
                "질문하기를 통해 이해 확인하기"
            ]
        
        return {
            "action": next_action,
            "message": message,
            "suggestions": suggestions
        }
    
    def _generate_personalized_message(
        self, 
        evaluation_result: EvaluationResult, 
        user_profile: Dict[str, Any],
        learning_context: Dict[str, Any]
    ) -> str:
        """개인화된 메시지 생성"""
        
        user_type = user_profile.get("user_type", "beginner")
        user_level = user_profile.get("user_level", "medium")
        recent_performance = learning_context.get("recent_performance", [])
        
        # 최근 성과 분석
        if recent_performance:
            recent_correct_rate = sum(1 for p in recent_performance if p.get("is_correct", False)) / len(recent_performance)
            
            if recent_correct_rate >= 0.8:
                trend_message = "최근 성과가 매우 좋습니다! 꾸준히 실력이 늘고 있어요."
            elif recent_correct_rate >= 0.6:
                trend_message = "꾸준히 발전하고 있습니다. 이 조자로 계속 해보세요!"
            else:
                trend_message = "조금 더 기초를 다지는 시간이 필요할 것 같아요. 천천히 해보세요."
        else:
            trend_message = "새로운 학습을 시작하셨네요! 차근차근 해보세요."
        
        # 사용자 유형별 맞춤 메시지
        if user_type == "beginner":
            type_message = "AI 학습 초보자로서 기초를 탄탄히 다지고 계시네요."
        else:  # business
            type_message = "실무 활용을 목표로 하시는 만큼 실제 적용 가능한 스킬을 익히고 계시네요."
        
        return f"{type_message} {trend_message}"
    
    def _generate_feedback_ui_elements(
        self, 
        evaluation_result: EvaluationResult, 
        question_type: str,
        question_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """피드백 UI 요소 생성"""
        
        is_correct = evaluation_result.is_correct
        score = evaluation_result.score
        
        # 기본 UI 요소
        ui_elements = {
            "type": "feedback_display",
            "score_display": {
                "show": True,
                "score": score,
                "max_score": 100,
                "color": self._get_score_color(score)
            },
            "result_icon": "✅" if is_correct else "❌",
            "show_explanation": True,
            "show_next_button": True,
            "show_retry_button": not is_correct,
            "show_hint_button": False  # 피드백 단계에서는 힌트 비활성화
        }
        
        # 문제 유형별 추가 요소
        if question_type == "multiple_choice":
            ui_elements.update({
                "highlight_correct_answer": True,
                "show_option_analysis": True,
                "correct_answer_index": question_data.get("correct_answer", 0)
            })
        elif question_type == "prompt_practice":
            detailed_analysis = evaluation_result.detailed_analysis
            ui_elements.update({
                "show_requirements_checklist": True,
                "requirements_analysis": detailed_analysis.get("requirements_analysis", {}),
                "show_chatgpt_result": detailed_analysis.get("chatgpt_test_result") is not None,
                "chatgpt_result": detailed_analysis.get("chatgpt_test_result"),
                "show_improvement_suggestions": True
            })
        
        return ui_elements
    
    def _get_score_color(self, score: float) -> str:
        """점수에 따른 색상 반환"""
        if score >= 90:
            return "#4caf50"  # 초록색
        elif score >= 70:
            return "#2196f3"  # 파란색
        elif score >= 50:
            return "#ff9800"  # 주황색
        else:
            return "#f44336"  # 빨간색
    
    def _generate_error_feedback(self) -> Dict[str, Any]:
        """오류 시 기본 피드백 생성"""
        return {
            "feedback_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "main_feedback": "피드백 생성 중 오류가 발생했습니다.",
            "encouragement": "다시 시도해보세요.",
            "improvement_tips": ["시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요."],
            "next_steps": {
                "action": "retry",
                "message": "다시 시도해주세요.",
                "suggestions": ["페이지 새로고침", "다시 답변 제출"]
            },
            "ui_elements": {
                "type": "error_display",
                "show_retry_button": True
            }
        }
    
    def _load_feedback_templates(self) -> Dict[str, Any]:
        """피드백 템플릿 로드"""
        return {
            "multiple_choice": {
                "correct": {
                    "high": "완벽합니다! 개념을 정확히 이해하고 계시네요.",
                    "medium": "정답입니다! 잘 하셨어요.",
                    "low": "정답이지만 조금 더 확실히 알아두세요."
                },
                "incorrect": {
                    "high": "아쉽네요. 다시 한 번 생각해보세요.",
                    "medium": "정답이 아닙니다. 개념을 다시 확인해보세요.",
                    "low": "괜찮습니다. 기초부터 다시 학습해보세요."
                }
            },
            "prompt_practice": {
                "excellent": "훌륭한 프롬프트입니다! 실무에서도 바로 사용할 수 있을 것 같아요.",
                "good": "좋은 프롬프트입니다. 몇 가지만 보완하면 더 완벽해질 것 같아요.",
                "needs_improvement": "기본기는 갖추셨네요. 조금 더 구체적으로 작성해보세요.",
                "poor": "좋은 시도였습니다! 단계별로 차근차근 개선해보세요."
            }
        }
    
    def _load_encouragement_messages(self) -> Dict[str, Any]:
        """격려 메시지 로드"""
        return {
            "beginner": {
                "excellent": [
                    "정말 빠르게 실력이 늘고 있어요! 🌟",
                    "초보자라고 하기엔 너무 잘하시는데요? 👏",
                    "이 조자로 계속하면 금세 전문가가 될 것 같아요! 🚀"
                ],
                "good": [
                    "차근차근 잘 배우고 계시네요! 👍",
                    "기초를 탄탄히 다지고 계시는 모습이 보기 좋아요! 📚",
                    "꾸준히 하시면 분명 실력이 늘 거예요! 💪"
                ],
                "improving": [
                    "실수를 통해 배우는 것도 중요해요! 🌱",
                    "포기하지 마세요. 조금씩 나아지고 있어요! ⭐",
                    "모든 전문가도 처음엔 초보였답니다! 🎯"
                ],
                "supportive": [
                    "괜찮아요! 천천히 해보세요. 🤗",
                    "어려워도 포기하지 마세요. 함께 해보아요! 💝",
                    "실패는 성공의 어머니라고 하잖아요! 🌈"
                ]
            },
            "business": {
                "excellent": [
                    "실무에 바로 적용할 수 있는 수준이네요! 💼",
                    "비즈니스 감각이 뛰어나시네요! 📈",
                    "동료들에게도 공유해보세요! 🤝"
                ],
                "good": [
                    "실무 활용도가 높은 답변이에요! 👔",
                    "비즈니스 현장에서 유용할 것 같아요! 💡",
                    "실용적인 접근이 인상적이에요! ⚡"
                ],
                "improving": [
                    "실무 경험이 도움이 될 거예요! 🎯",
                    "비즈니스 관점에서 다시 생각해보세요! 🔍",
                    "실제 업무에 적용하며 연습해보세요! 🛠️"
                ],
                "supportive": [
                    "새로운 기술 학습은 항상 도전이죠! 🚀",
                    "업무 효율성을 위한 투자라고 생각하세요! 📊",
                    "실무진의 학습 의지가 대단해요! 👨‍💼"
                ]
            }
        }
    
    def _load_improvement_suggestions(self) -> Dict[str, List[str]]:
        """개선 제안 로드"""
        return {
            "multiple_choice": [
                "문제를 천천히 읽고 핵심 키워드를 찾아보세요.",
                "각 선택지를 문제와 연결해서 생각해보세요.",
                "소거법을 활용해 명백히 틀린 답부터 제거해보세요.",
                "개념 정의를 정확히 기억하고 적용해보세요.",
                "비슷한 유형의 문제를 더 많이 연습해보세요."
            ],
            "prompt_practice": [
                "역할, 맥락, 출력 형식을 명확히 지정해보세요.",
                "구체적이고 측정 가능한 요구사항을 포함해보세요.",
                "단계별로 논리적인 구조를 만들어보세요.",
                "예시나 샘플을 포함해 더 명확하게 만들어보세요.",
                "실제 ChatGPT에서 테스트하며 개선해보세요."
            ]
        }