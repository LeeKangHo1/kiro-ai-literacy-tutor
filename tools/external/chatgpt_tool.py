# tools/external/chatgpt_tool.py
# ChatGPT API 연동 도구

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
from langchain.tools import tool
from pydantic import BaseModel, Field
from .api_monitor import log_api_call, check_rate_limit, wait_for_rate_limit, record_rate_limit_call
from .error_handler import handle_service_error, ServiceType, ErrorSeverity

# 로깅 설정
logger = logging.getLogger(__name__)

class ChatGPTResponse(BaseModel):
    """ChatGPT API 응답 모델"""
    success: bool = Field(description="API 호출 성공 여부")
    content: str = Field(description="생성된 응답 내용")
    usage: Optional[Dict[str, int]] = Field(default=None, description="토큰 사용량 정보")
    model: str = Field(description="사용된 모델명")
    response_time: float = Field(description="응답 시간(초)")
    error_message: Optional[str] = Field(default=None, description="오류 메시지")
    quality_score: Optional[float] = Field(default=None, description="응답 품질 점수")

class PromptQualityAnalyzer:
    """프롬프트 품질 분석기"""
    
    @staticmethod
    def analyze_prompt_quality(prompt: str) -> Dict[str, Any]:
        """프롬프트 품질 분석"""
        analysis = {
            "length_score": 0.0,
            "clarity_score": 0.0,
            "specificity_score": 0.0,
            "structure_score": 0.0,
            "overall_score": 0.0,
            "suggestions": []
        }
        
        # 길이 점수 (50-500자가 적정)
        length = len(prompt)
        if 50 <= length <= 500:
            analysis["length_score"] = 1.0
        elif length < 50:
            analysis["length_score"] = length / 50
            analysis["suggestions"].append("프롬프트가 너무 짧습니다. 더 구체적인 설명을 추가해보세요.")
        else:
            analysis["length_score"] = max(0.5, 1.0 - (length - 500) / 1000)
            analysis["suggestions"].append("프롬프트가 너무 깁니다. 핵심 내용으로 간소화해보세요.")
        
        # 명확성 점수 (질문 형태, 명확한 지시어 포함)
        clarity_keywords = ["무엇", "어떻게", "왜", "언제", "어디서", "설명", "분석", "요약", "작성"]
        clarity_count = sum(1 for keyword in clarity_keywords if keyword in prompt)
        analysis["clarity_score"] = min(1.0, clarity_count / 3)
        
        if analysis["clarity_score"] < 0.5:
            analysis["suggestions"].append("더 명확한 질문이나 지시어를 사용해보세요.")
        
        # 구체성 점수 (구체적인 예시, 조건, 형식 지정)
        specificity_keywords = ["예시", "예를 들어", "형식", "조건", "요구사항", "단계별", "구체적으로"]
        specificity_count = sum(1 for keyword in specificity_keywords if keyword in prompt)
        analysis["specificity_score"] = min(1.0, specificity_count / 2)
        
        if analysis["specificity_score"] < 0.5:
            analysis["suggestions"].append("구체적인 예시나 조건을 추가해보세요.")
        
        # 구조 점수 (문단 구분, 번호 매기기 등)
        has_structure = any(marker in prompt for marker in ["\n", "1.", "2.", "-", "•"])
        analysis["structure_score"] = 1.0 if has_structure else 0.3
        
        if analysis["structure_score"] < 0.5:
            analysis["suggestions"].append("프롬프트를 구조화하여 읽기 쉽게 만들어보세요.")
        
        # 전체 점수 계산
        analysis["overall_score"] = (
            analysis["length_score"] * 0.2 +
            analysis["clarity_score"] * 0.3 +
            analysis["specificity_score"] * 0.3 +
            analysis["structure_score"] * 0.2
        )
        
        return analysis

class ChatGPTAPIManager:
    """ChatGPT API 관리자"""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_retries = 3
        self.retry_delay = 1.0
        self.quality_analyzer = PromptQualityAnalyzer()
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAI 클라이언트 초기화"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. 오프라인 모드로 동작합니다.")
                self.client = None
                return
            
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI 클라이언트가 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
            self.client = None
    
    def _handle_api_error(self, error: Exception, attempt: int) -> Optional[str]:
        """API 오류 처리"""
        error_message = str(error)
        error_code = "unknown_error"
        severity = ErrorSeverity.MEDIUM
        
        if "rate_limit" in error_message.lower():
            error_code = "rate_limit_exceeded"
            severity = ErrorSeverity.HIGH
            if attempt < self.max_retries:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Rate limit 도달. {wait_time}초 후 재시도... (시도 {attempt + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return None
            else:
                final_error = "API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요."
        
        elif "invalid_api_key" in error_message.lower():
            error_code = "invalid_api_key"
            severity = ErrorSeverity.CRITICAL
            final_error = "API 키가 유효하지 않습니다. 설정을 확인해주세요."
        
        elif "insufficient_quota" in error_message.lower():
            error_code = "insufficient_quota"
            severity = ErrorSeverity.CRITICAL
            final_error = "API 사용량이 초과되었습니다. 요금제를 확인해주세요."
        
        elif "model_not_found" in error_message.lower():
            error_code = "model_not_found"
            severity = ErrorSeverity.HIGH
            final_error = f"요청한 모델({self.model})을 찾을 수 없습니다."
        
        else:
            error_code = "api_call_failed"
            severity = ErrorSeverity.MEDIUM
            final_error = f"API 호출 중 오류가 발생했습니다: {error_message}"
        
        # 오류 처리 시스템에 기록
        handle_service_error(
            service_type=ServiceType.CHATGPT_API,
            error_code=error_code,
            error_message=error_message,
            context={
                "attempt": attempt,
                "max_retries": self.max_retries,
                "model": self.model
            },
            severity=severity
        )
        
        return final_error
    
    def call_chatgpt_api(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        analyze_quality: bool = True
    ) -> ChatGPTResponse:
        """ChatGPT API 호출"""
        start_time = time.time()
        
        # Rate limit 확인 및 대기
        if not check_rate_limit():
            wait_for_rate_limit()
        
        # 프롬프트 품질 분석
        quality_analysis = None
        if analyze_quality:
            quality_analysis = self.quality_analyzer.analyze_prompt_quality(prompt)
        
        # 메시지 구성
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # 클라이언트가 초기화되지 않은 경우 (오프라인 모드)
        if not self.client:
            response_time = time.time() - start_time
            error_message = "OpenAI API 클라이언트가 초기화되지 않았습니다. API 키를 확인해주세요."
            
            # 실패한 API 호출 로깅
            log_api_call(
                endpoint="chat/completions",
                success=False,
                response_time=response_time,
                error_message=error_message,
                model=self.model
            )
            
            return ChatGPTResponse(
                success=False,
                content="",
                model=self.model,
                response_time=response_time,
                error_message=error_message
            )
        
        # API 호출 시도
        for attempt in range(self.max_retries):
            try:
                # Rate limit 호출 기록
                record_rate_limit_call()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response_time = time.time() - start_time
                
                # 성공적인 API 호출 로깅
                log_api_call(
                    endpoint="chat/completions",
                    success=True,
                    response_time=response_time,
                    token_usage=response.usage.model_dump() if response.usage else None,
                    model=response.model
                )
                
                return ChatGPTResponse(
                    success=True,
                    content=response.choices[0].message.content,
                    usage=response.usage.model_dump() if response.usage else None,
                    model=response.model,
                    response_time=response_time,
                    quality_score=quality_analysis["overall_score"] if quality_analysis else None
                )
                
            except Exception as e:
                error_message = self._handle_api_error(e, attempt)
                if error_message:
                    response_time = time.time() - start_time
                    
                    # 실패한 API 호출 로깅
                    log_api_call(
                        endpoint="chat/completions",
                        success=False,
                        response_time=response_time,
                        error_message=error_message,
                        model=self.model
                    )
                    
                    return ChatGPTResponse(
                        success=False,
                        content="",
                        model=self.model,
                        response_time=response_time,
                        error_message=error_message
                    )
        
        # 모든 재시도 실패
        response_time = time.time() - start_time
        error_message = "최대 재시도 횟수를 초과했습니다."
        
        # 실패한 API 호출 로깅
        log_api_call(
            endpoint="chat/completions",
            success=False,
            response_time=response_time,
            error_message=error_message,
            model=self.model
        )
        
        return ChatGPTResponse(
            success=False,
            content="",
            model=self.model,
            response_time=response_time,
            error_message=error_message
        )

# 전역 API 매니저 인스턴스
api_manager = ChatGPTAPIManager()

@tool
def chatgpt_api_tool(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    ChatGPT API를 호출하여 응답을 생성합니다.
    
    Args:
        prompt: 사용자 프롬프트
        system_message: 시스템 메시지 (선택사항)
        temperature: 창의성 수준 (0.0-1.0)
        max_tokens: 최대 토큰 수 (선택사항)
    
    Returns:
        API 응답 결과 딕셔너리
    """
    try:
        response = api_manager.call_chatgpt_api(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        result = {
            "success": response.success,
            "content": response.content,
            "model": response.model,
            "response_time": response.response_time
        }
        
        if response.usage:
            result["usage"] = response.usage
        
        if response.quality_score:
            result["quality_score"] = response.quality_score
        
        if response.error_message:
            result["error_message"] = response.error_message
        
        # 로깅
        if response.success:
            logger.info(f"ChatGPT API 호출 성공 - 응답 시간: {response.response_time:.2f}초")
        else:
            logger.error(f"ChatGPT API 호출 실패: {response.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"chatgpt_api_tool 실행 중 오류: {str(e)}")
        return {
            "success": False,
            "content": "",
            "error_message": f"도구 실행 중 오류가 발생했습니다: {str(e)}",
            "model": api_manager.model,
            "response_time": 0.0
        }
@tool

def get_api_status() -> Dict[str, Any]:
    """
    ChatGPT API 상태 및 메트릭을 조회합니다.
    
    Returns:
        API 상태 정보 딕셔너리
    """
    try:
        from .api_monitor import api_monitor
        
        metrics = api_monitor.get_current_metrics()
        recent_calls = api_monitor.get_recent_calls(minutes=30)
        status_history = api_monitor.get_status_history()
        
        return {
            "current_metrics": metrics,
            "recent_calls_count": len(recent_calls),
            "status_changes_today": len([s for s in status_history 
                                        if s["timestamp"].date() == datetime.now().date()]),
            "api_health": metrics["current_status"],
            "success_rate": f"{metrics['success_rate']:.1%}",
            "avg_response_time": f"{metrics['average_response_time']:.2f}초"
        }
        
    except Exception as e:
        logger.error(f"get_api_status 실행 중 오류: {str(e)}")
        return {
            "error": f"상태 조회 중 오류가 발생했습니다: {str(e)}",
            "current_metrics": {},
            "recent_calls_count": 0,
            "status_changes_today": 0,
            "api_health": "unknown",
            "success_rate": "N/A",
            "avg_response_time": "N/A"
        }

@tool
def reset_api_metrics() -> Dict[str, Any]:
    """
    API 메트릭을 초기화합니다.
    
    Returns:
        초기화 결과 딕셔너리
    """
    try:
        from .api_monitor import api_monitor
        
        old_metrics = api_monitor.get_current_metrics()
        api_monitor.reset_metrics()
        
        return {
            "success": True,
            "message": "API 메트릭이 성공적으로 초기화되었습니다.",
            "previous_total_calls": old_metrics["total_calls"],
            "previous_success_rate": f"{old_metrics['success_rate']:.1%}"
        }
        
    except Exception as e:
        logger.error(f"reset_api_metrics 실행 중 오류: {str(e)}")
        return {
            "success": False,
            "message": f"메트릭 초기화 중 오류가 발생했습니다: {str(e)}"
        }