# tools/external/prompt_practice_tool.py
# 프롬프트 실습 전용 도구

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field
from .chatgpt_tool import api_manager, PromptQualityAnalyzer

# 로깅 설정
logger = logging.getLogger(__name__)

class PromptPracticeResult(BaseModel):
    """프롬프트 실습 결과 모델"""
    success: bool = Field(description="실습 성공 여부")
    user_prompt: str = Field(description="사용자가 작성한 프롬프트")
    chatgpt_response: str = Field(description="ChatGPT 응답")
    quality_analysis: Dict[str, Any] = Field(description="프롬프트 품질 분석")
    performance_metrics: Dict[str, Any] = Field(description="성능 지표")
    feedback: str = Field(description="개선 피드백")
    suggestions: List[str] = Field(description="개선 제안사항")
    error_message: Optional[str] = Field(description="오류 메시지")

class PromptPracticeManager:
    """프롬프트 실습 관리자"""
    
    def __init__(self):
        self.quality_analyzer = PromptQualityAnalyzer()
        self.practice_scenarios = {
            "basic": {
                "name": "기본 질문 작성",
                "description": "간단한 정보 요청 프롬프트 작성",
                "example": "AI의 정의에 대해 초보자가 이해하기 쉽게 설명해주세요.",
                "evaluation_criteria": ["명확성", "구체성", "적절한 길이"]
            },
            "creative": {
                "name": "창의적 콘텐츠 생성",
                "description": "창의적인 콘텐츠 생성을 위한 프롬프트 작성",
                "example": "AI 학습에 대한 재미있는 비유를 사용해서 블로그 글을 작성해주세요.",
                "evaluation_criteria": ["창의성 유도", "구체적 지시", "톤앤매너 지정"]
            },
            "analytical": {
                "name": "분석적 사고 유도",
                "description": "분석과 추론을 요구하는 프롬프트 작성",
                "example": "머신러닝과 딥러닝의 차이점을 표로 정리하고 각각의 장단점을 분석해주세요.",
                "evaluation_criteria": ["분석 요구사항", "출력 형식 지정", "비교 기준 제시"]
            },
            "roleplay": {
                "name": "역할 기반 대화",
                "description": "특정 역할을 부여한 대화형 프롬프트 작성",
                "example": "당신은 AI 전문가입니다. 비전공자에게 ChatGPT 활용법을 설명해주세요.",
                "evaluation_criteria": ["역할 정의", "대상 명시", "상황 설정"]
            }
        }
    
    def evaluate_prompt_effectiveness(
        self,
        prompt: str,
        response: str,
        scenario_type: str = "basic"
    ) -> Dict[str, Any]:
        """프롬프트 효과성 평가"""
        
        # 기본 품질 분석
        quality_analysis = self.quality_analyzer.analyze_prompt_quality(prompt)
        
        # 시나리오별 평가
        scenario = self.practice_scenarios.get(scenario_type, self.practice_scenarios["basic"])
        scenario_score = self._evaluate_scenario_specific(prompt, response, scenario)
        
        # 응답 품질 평가
        response_quality = self._evaluate_response_quality(response)
        
        # 종합 점수 계산
        overall_score = (
            quality_analysis["overall_score"] * 0.4 +
            scenario_score * 0.3 +
            response_quality * 0.3
        )
        
        return {
            "prompt_quality": quality_analysis,
            "scenario_score": scenario_score,
            "response_quality": response_quality,
            "overall_score": overall_score,
            "scenario_type": scenario_type,
            "scenario_name": scenario["name"]
        }
    
    def _evaluate_scenario_specific(
        self,
        prompt: str,
        response: str,
        scenario: Dict[str, Any]
    ) -> float:
        """시나리오별 특화 평가"""
        
        criteria = scenario.get("evaluation_criteria", [])
        score = 0.0
        
        for criterion in criteria:
            if criterion == "명확성":
                score += 0.3 if self._check_clarity(prompt) else 0.0
            elif criterion == "구체성":
                score += 0.3 if self._check_specificity(prompt) else 0.0
            elif criterion == "적절한 길이":
                score += 0.2 if 50 <= len(prompt) <= 300 else 0.0
            elif criterion == "창의성 유도":
                score += 0.3 if self._check_creativity_prompt(prompt) else 0.0
            elif criterion == "구체적 지시":
                score += 0.3 if self._check_specific_instructions(prompt) else 0.0
            elif criterion == "톤앤매너 지정":
                score += 0.2 if self._check_tone_specification(prompt) else 0.0
            elif criterion == "분석 요구사항":
                score += 0.4 if self._check_analysis_request(prompt) else 0.0
            elif criterion == "출력 형식 지정":
                score += 0.3 if self._check_format_specification(prompt) else 0.0
            elif criterion == "비교 기준 제시":
                score += 0.2 if self._check_comparison_criteria(prompt) else 0.0
            elif criterion == "역할 정의":
                score += 0.4 if self._check_role_definition(prompt) else 0.0
            elif criterion == "대상 명시":
                score += 0.3 if self._check_target_specification(prompt) else 0.0
            elif criterion == "상황 설정":
                score += 0.2 if self._check_context_setting(prompt) else 0.0
        
        return min(1.0, score)
    
    def _check_clarity(self, prompt: str) -> bool:
        """명확성 검사"""
        clarity_indicators = ["무엇", "어떻게", "왜", "설명", "알려주세요", "해주세요"]
        return any(indicator in prompt for indicator in clarity_indicators)
    
    def _check_specificity(self, prompt: str) -> bool:
        """구체성 검사"""
        specificity_indicators = ["구체적으로", "자세히", "예를 들어", "단계별로", "방법"]
        return any(indicator in prompt for indicator in specificity_indicators)
    
    def _check_creativity_prompt(self, prompt: str) -> bool:
        """창의성 유도 검사"""
        creativity_indicators = ["창의적", "재미있게", "독창적", "새로운", "참신한"]
        return any(indicator in prompt for indicator in creativity_indicators)
    
    def _check_specific_instructions(self, prompt: str) -> bool:
        """구체적 지시 검사"""
        instruction_indicators = ["작성해", "만들어", "생성해", "제작해", "개발해"]
        return any(indicator in prompt for indicator in instruction_indicators)
    
    def _check_tone_specification(self, prompt: str) -> bool:
        """톤앤매너 지정 검사"""
        tone_indicators = ["친근하게", "전문적으로", "쉽게", "재미있게", "정중하게"]
        return any(indicator in prompt for indicator in tone_indicators)
    
    def _check_analysis_request(self, prompt: str) -> bool:
        """분석 요구사항 검사"""
        analysis_indicators = ["분석", "비교", "평가", "검토", "조사"]
        return any(indicator in prompt for indicator in analysis_indicators)
    
    def _check_format_specification(self, prompt: str) -> bool:
        """출력 형식 지정 검사"""
        format_indicators = ["표로", "목록으로", "단계별로", "번호를 매겨", "형식으로"]
        return any(indicator in prompt for indicator in format_indicators)
    
    def _check_comparison_criteria(self, prompt: str) -> bool:
        """비교 기준 제시 검사"""
        comparison_indicators = ["차이점", "공통점", "장단점", "비교", "대비"]
        return any(indicator in prompt for indicator in comparison_indicators)
    
    def _check_role_definition(self, prompt: str) -> bool:
        """역할 정의 검사"""
        role_indicators = ["당신은", "역할", "전문가", "선생님", "컨설턴트"]
        return any(indicator in prompt for indicator in role_indicators)
    
    def _check_target_specification(self, prompt: str) -> bool:
        """대상 명시 검사"""
        target_indicators = ["초보자", "전문가", "학생", "직장인", "일반인"]
        return any(indicator in prompt for indicator in target_indicators)
    
    def _check_context_setting(self, prompt: str) -> bool:
        """상황 설정 검사"""
        context_indicators = ["상황", "환경", "조건", "배경", "맥락"]
        return any(indicator in prompt for indicator in context_indicators)
    
    def _evaluate_response_quality(self, response: str) -> float:
        """응답 품질 평가"""
        if not response or len(response.strip()) < 10:
            return 0.0
        
        score = 0.0
        
        # 길이 적절성 (100-2000자)
        length = len(response)
        if 100 <= length <= 2000:
            score += 0.3
        elif length < 100:
            score += length / 100 * 0.3
        else:
            score += max(0.1, 0.3 - (length - 2000) / 5000)
        
        # 구조화 정도
        if any(marker in response for marker in ["\n\n", "1.", "2.", "-", "•"]):
            score += 0.3
        
        # 정보성 (키워드 다양성)
        words = response.split()
        unique_words = set(words)
        if len(words) > 0:
            diversity = len(unique_words) / len(words)
            score += min(0.4, diversity * 0.8)
        
        return min(1.0, score)
    
    def generate_feedback(self, evaluation: Dict[str, Any]) -> str:
        """피드백 생성"""
        overall_score = evaluation["overall_score"]
        prompt_quality = evaluation["prompt_quality"]
        
        if overall_score >= 0.8:
            feedback = "훌륭한 프롬프트입니다! 명확하고 구체적이며 효과적인 응답을 이끌어냈습니다."
        elif overall_score >= 0.6:
            feedback = "좋은 프롬프트입니다. 몇 가지 개선사항을 적용하면 더욱 효과적일 것입니다."
        elif overall_score >= 0.4:
            feedback = "기본적인 프롬프트입니다. 명확성과 구체성을 높이면 더 나은 결과를 얻을 수 있습니다."
        else:
            feedback = "프롬프트 개선이 필요합니다. 더 명확하고 구체적인 지시사항을 포함해보세요."
        
        # 구체적인 개선 제안 추가
        if prompt_quality["suggestions"]:
            feedback += "\n\n개선 제안사항:\n"
            for i, suggestion in enumerate(prompt_quality["suggestions"], 1):
                feedback += f"{i}. {suggestion}\n"
        
        return feedback

# 전역 실습 관리자 인스턴스
practice_manager = PromptPracticeManager()

@tool
def prompt_practice_tool(
    user_prompt: str,
    scenario_type: str = "basic",
    system_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    프롬프트 실습을 위한 ChatGPT API 호출 및 평가 도구
    
    Args:
        user_prompt: 사용자가 작성한 프롬프트
        scenario_type: 실습 시나리오 유형 (basic, creative, analytical, roleplay)
        system_message: 시스템 메시지 (선택사항)
    
    Returns:
        실습 결과 및 평가 딕셔너리
    """
    try:
        # ChatGPT API 호출
        api_response = api_manager.call_chatgpt_api(
            prompt=user_prompt,
            system_message=system_message,
            temperature=0.7
        )
        
        if not api_response.success:
            return {
                "success": False,
                "user_prompt": user_prompt,
                "chatgpt_response": "",
                "error_message": api_response.error_message,
                "quality_analysis": {},
                "performance_metrics": {},
                "feedback": "API 호출에 실패했습니다.",
                "suggestions": []
            }
        
        # 프롬프트 효과성 평가
        evaluation = practice_manager.evaluate_prompt_effectiveness(
            prompt=user_prompt,
            response=api_response.content,
            scenario_type=scenario_type
        )
        
        # 피드백 생성
        feedback = practice_manager.generate_feedback(evaluation)
        
        # 성능 지표 구성
        performance_metrics = {
            "response_time": api_response.response_time,
            "token_usage": api_response.usage,
            "model_used": api_response.model,
            "overall_score": evaluation["overall_score"],
            "scenario_score": evaluation["scenario_score"]
        }
        
        result = {
            "success": True,
            "user_prompt": user_prompt,
            "chatgpt_response": api_response.content,
            "quality_analysis": evaluation["prompt_quality"],
            "performance_metrics": performance_metrics,
            "feedback": feedback,
            "suggestions": evaluation["prompt_quality"]["suggestions"],
            "scenario_type": scenario_type,
            "scenario_name": evaluation["scenario_name"]
        }
        
        # 로깅
        logger.info(f"프롬프트 실습 완료 - 점수: {evaluation['overall_score']:.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"prompt_practice_tool 실행 중 오류: {str(e)}")
        return {
            "success": False,
            "user_prompt": user_prompt,
            "chatgpt_response": "",
            "error_message": f"도구 실행 중 오류가 발생했습니다: {str(e)}",
            "quality_analysis": {},
            "performance_metrics": {},
            "feedback": "실습 중 오류가 발생했습니다.",
            "suggestions": []
        }

@tool
def get_practice_scenarios() -> Dict[str, Any]:
    """
    사용 가능한 프롬프트 실습 시나리오 목록을 반환합니다.
    
    Returns:
        시나리오 정보 딕셔너리
    """
    return {
        "scenarios": practice_manager.practice_scenarios,
        "default_scenario": "basic",
        "description": "프롬프트 작성 실습을 위한 다양한 시나리오를 제공합니다."
    }