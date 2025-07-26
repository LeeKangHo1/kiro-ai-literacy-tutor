# tools/external/error_handler.py
# 외부 서비스 오류 처리 시스템

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import threading
from collections import defaultdict, deque

# 로깅 설정
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """서비스 유형 열거형"""
    CHATGPT_API = "chatgpt_api"
    CHROMADB = "chromadb"
    WEB_SEARCH = "web_search"
    EXTERNAL_API = "external_api"

class ErrorSeverity(Enum):
    """오류 심각도 열거형"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ServiceError:
    """서비스 오류 정보"""
    service_type: ServiceType
    error_code: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime
    context: Dict[str, Any]
    retry_count: int = 0
    resolved: bool = False

class FallbackStrategy(ABC):
    """대체 전략 추상 클래스"""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """대체 전략 실행"""
        pass
    
    @abstractmethod
    def is_applicable(self, error: ServiceError) -> bool:
        """전략 적용 가능 여부 확인"""
        pass

class ChatGPTFallbackStrategy(FallbackStrategy):
    """ChatGPT API 대체 전략"""
    
    def __init__(self):
        self.fallback_responses = {
            "theory_explanation": "죄송합니다. 현재 AI 서비스에 일시적인 문제가 있어 상세한 설명을 제공할 수 없습니다. 기본적인 개념 설명을 제공하겠습니다.",
            "quiz_generation": "현재 문제 생성 서비스에 문제가 있습니다. 미리 준비된 문제를 제공하겠습니다.",
            "feedback_generation": "피드백 생성 서비스에 문제가 있습니다. 기본적인 평가 결과를 제공하겠습니다.",
            "qna_response": "질문 답변 서비스에 일시적인 문제가 있습니다. 기본 지식베이스에서 답변을 찾아보겠습니다.",
            "prompt_practice": "프롬프트 실습 서비스에 문제가 있습니다. 기본적인 프롬프트 가이드를 제공하겠습니다."
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ChatGPT API 대체 응답 생성"""
        request_type = context.get("request_type", "general")
        fallback_message = self.fallback_responses.get(
            request_type, 
            "죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요."
        )
        
        return {
            "success": False,
            "content": fallback_message,
            "is_fallback": True,
            "fallback_type": "chatgpt_unavailable",
            "original_error": context.get("error_message", ""),
            "suggested_action": "잠시 후 다시 시도하거나 다른 방법으로 학습을 계속해보세요."
        }
    
    def is_applicable(self, error: ServiceError) -> bool:
        """ChatGPT API 오류에 적용 가능"""
        return error.service_type == ServiceType.CHATGPT_API

class ChromaDBFallbackStrategy(FallbackStrategy):
    """ChromaDB 대체 전략"""
    
    def __init__(self):
        self.basic_knowledge = {
            "AI": "인공지능(AI)은 인간의 지능을 모방하여 학습, 추론, 인식 등의 작업을 수행하는 컴퓨터 시스템입니다.",
            "머신러닝": "머신러닝은 데이터를 통해 컴퓨터가 자동으로 학습하고 성능을 향상시키는 AI의 한 분야입니다.",
            "딥러닝": "딥러닝은 인공신경망을 여러 층으로 쌓아 복잡한 패턴을 학습하는 머신러닝의 한 방법입니다.",
            "프롬프트": "프롬프트는 AI 모델에게 원하는 작업이나 응답을 요청하기 위한 입력 텍스트입니다.",
            "ChatGPT": "ChatGPT는 OpenAI에서 개발한 대화형 AI 모델로, 자연어 처리를 통해 다양한 질문에 답변할 수 있습니다."
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """ChromaDB 대체 검색 수행"""
        query = context.get("query", "").lower()
        
        # 기본 지식베이스에서 키워드 매칭
        matched_content = []
        for keyword, content in self.basic_knowledge.items():
            if keyword.lower() in query or any(word in keyword.lower() for word in query.split()):
                matched_content.append({
                    "content": content,
                    "source": "기본 지식베이스",
                    "relevance_score": 0.7
                })
        
        if not matched_content:
            matched_content.append({
                "content": "죄송합니다. 현재 지식베이스 서비스에 문제가 있어 정확한 답변을 찾을 수 없습니다. 기본적인 AI 관련 정보는 공식 문서나 신뢰할 수 있는 웹사이트를 참조해주세요.",
                "source": "기본 응답",
                "relevance_score": 0.3
            })
        
        return {
            "success": True,
            "results": matched_content,
            "is_fallback": True,
            "fallback_type": "chromadb_unavailable",
            "total_results": len(matched_content),
            "message": "지식베이스 서비스에 문제가 있어 기본 지식으로 답변을 제공합니다."
        }
    
    def is_applicable(self, error: ServiceError) -> bool:
        """ChromaDB 오류에 적용 가능"""
        return error.service_type == ServiceType.CHROMADB

class WebSearchFallbackStrategy(FallbackStrategy):
    """웹 검색 대체 전략"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """웹 검색 대체 응답 생성"""
        query = context.get("query", "")
        
        return {
            "success": False,
            "results": [],
            "is_fallback": True,
            "fallback_type": "web_search_unavailable",
            "message": f"웹 검색 서비스에 문제가 있습니다. '{query}'에 대한 정보는 직접 검색 엔진을 이용해주세요.",
            "suggested_sources": [
                "https://www.google.com",
                "https://www.wikipedia.org",
                "공식 AI 관련 문서 사이트"
            ]
        }
    
    def is_applicable(self, error: ServiceError) -> bool:
        """웹 검색 오류에 적용 가능"""
        return error.service_type == ServiceType.WEB_SEARCH

class ServiceErrorHandler:
    """서비스 오류 처리 관리자"""
    
    def __init__(self):
        self.error_history: deque = deque(maxlen=1000)
        self.fallback_strategies: List[FallbackStrategy] = [
            ChatGPTFallbackStrategy(),
            ChromaDBFallbackStrategy(),
            WebSearchFallbackStrategy()
        ]
        self.service_status = defaultdict(lambda: "healthy")
        self.retry_policies = {
            ServiceType.CHATGPT_API: {"max_retries": 3, "backoff_factor": 2.0},
            ServiceType.CHROMADB: {"max_retries": 2, "backoff_factor": 1.5},
            ServiceType.WEB_SEARCH: {"max_retries": 2, "backoff_factor": 1.0}
        }
        self.circuit_breakers = {}
        self.alert_callbacks = []
        self.lock = threading.Lock()
    
    def handle_error(
        self,
        service_type: ServiceType,
        error_code: str,
        error_message: str,
        context: Dict[str, Any],
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> Dict[str, Any]:
        """서비스 오류 처리"""
        
        # 오류 기록 생성
        error = ServiceError(
            service_type=service_type,
            error_code=error_code,
            error_message=error_message,
            severity=severity,
            timestamp=datetime.now(),
            context=context
        )
        
        with self.lock:
            self.error_history.append(error)
            self._update_service_status(service_type, error)
        
        # 로깅
        logger.error(f"서비스 오류 발생 - {service_type.value}: {error_message}")
        
        # 알림 발송
        self._send_alert(error)
        
        # Circuit Breaker 확인
        if self._is_circuit_open(service_type):
            return self._handle_circuit_breaker(service_type, context)
        
        # 재시도 정책 적용
        if self._should_retry(error):
            return self._attempt_retry(error)
        
        # 대체 전략 실행
        return self._execute_fallback(error)
    
    def _update_service_status(self, service_type: ServiceType, error: ServiceError):
        """서비스 상태 업데이트"""
        recent_errors = [e for e in self.error_history 
                        if e.service_type == service_type and 
                        e.timestamp > datetime.now() - timedelta(minutes=5)]
        
        if len(recent_errors) >= 5:
            self.service_status[service_type] = "critical"
        elif len(recent_errors) >= 3:
            self.service_status[service_type] = "degraded"
        elif error.severity == ErrorSeverity.CRITICAL:
            self.service_status[service_type] = "critical"
        else:
            self.service_status[service_type] = "error"
    
    def _send_alert(self, error: ServiceError):
        """알림 발송"""
        alert_data = {
            "service": error.service_type.value,
            "error_code": error.error_code,
            "message": error.error_message,
            "severity": error.severity.value,
            "timestamp": error.timestamp.isoformat(),
            "context": error.context
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {str(e)}")
    
    def _is_circuit_open(self, service_type: ServiceType) -> bool:
        """Circuit Breaker 상태 확인"""
        circuit = self.circuit_breakers.get(service_type)
        if not circuit:
            return False
        
        # 5분 내 5회 이상 오류 시 Circuit Open
        recent_errors = [e for e in self.error_history 
                        if e.service_type == service_type and 
                        e.timestamp > datetime.now() - timedelta(minutes=5)]
        
        return len(recent_errors) >= 5
    
    def _handle_circuit_breaker(self, service_type: ServiceType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Circuit Breaker 처리"""
        logger.warning(f"Circuit Breaker 활성화: {service_type.value}")
        
        return {
            "success": False,
            "is_circuit_breaker": True,
            "service": service_type.value,
            "message": f"{service_type.value} 서비스가 일시적으로 차단되었습니다. 잠시 후 다시 시도해주세요.",
            "retry_after": 300  # 5분 후 재시도
        }
    
    def _should_retry(self, error: ServiceError) -> bool:
        """재시도 여부 결정"""
        policy = self.retry_policies.get(error.service_type)
        if not policy:
            return False
        
        return error.retry_count < policy["max_retries"]
    
    def _attempt_retry(self, error: ServiceError) -> Dict[str, Any]:
        """재시도 시도"""
        policy = self.retry_policies[error.service_type]
        wait_time = policy["backoff_factor"] ** error.retry_count
        
        logger.info(f"재시도 대기: {wait_time}초 - {error.service_type.value}")
        time.sleep(wait_time)
        
        error.retry_count += 1
        
        return {
            "success": False,
            "should_retry": True,
            "retry_count": error.retry_count,
            "wait_time": wait_time,
            "message": f"재시도 중... ({error.retry_count}/{policy['max_retries']})"
        }
    
    def _execute_fallback(self, error: ServiceError) -> Dict[str, Any]:
        """대체 전략 실행"""
        for strategy in self.fallback_strategies:
            if strategy.is_applicable(error):
                try:
                    result = strategy.execute(error.context)
                    logger.info(f"대체 전략 실행 완료: {error.service_type.value}")
                    return result
                except Exception as e:
                    logger.error(f"대체 전략 실행 오류: {str(e)}")
        
        # 기본 대체 응답
        return {
            "success": False,
            "is_fallback": True,
            "fallback_type": "default",
            "message": f"{error.service_type.value} 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요.",
            "error_code": error.error_code,
            "timestamp": error.timestamp.isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        with self.lock:
            status_summary = {}
            for service_type in ServiceType:
                recent_errors = [e for e in self.error_history 
                               if e.service_type == service_type and 
                               e.timestamp > datetime.now() - timedelta(hours=1)]
                
                status_summary[service_type.value] = {
                    "status": self.service_status.get(service_type, "healthy"),
                    "recent_errors": len(recent_errors),
                    "last_error": recent_errors[-1].timestamp.isoformat() if recent_errors else None
                }
            
            return {
                "services": status_summary,
                "total_errors_24h": len([e for e in self.error_history 
                                       if e.timestamp > datetime.now() - timedelta(hours=24)]),
                "circuit_breakers_active": len([s for s in ServiceType if self._is_circuit_open(s)])
            }
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """오류 통계 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]
        
        stats = {
            "total_errors": len(recent_errors),
            "by_service": defaultdict(int),
            "by_severity": defaultdict(int),
            "by_hour": defaultdict(int)
        }
        
        for error in recent_errors:
            stats["by_service"][error.service_type.value] += 1
            stats["by_severity"][error.severity.value] += 1
            hour_key = error.timestamp.strftime("%Y-%m-%d %H:00")
            stats["by_hour"][hour_key] += 1
        
        return {
            "period_hours": hours,
            "statistics": dict(stats),
            "most_problematic_service": max(stats["by_service"].items(), 
                                          key=lambda x: x[1])[0] if stats["by_service"] else None
        }
    
    def add_alert_callback(self, callback: Callable):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def reset_circuit_breaker(self, service_type: ServiceType):
        """Circuit Breaker 리셋"""
        if service_type in self.circuit_breakers:
            del self.circuit_breakers[service_type]
        self.service_status[service_type] = "healthy"
        logger.info(f"Circuit Breaker 리셋: {service_type.value}")

# 전역 오류 처리기 인스턴스
error_handler = ServiceErrorHandler()

def handle_service_error(
    service_type: ServiceType,
    error_code: str,
    error_message: str,
    context: Dict[str, Any],
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
) -> Dict[str, Any]:
    """서비스 오류 처리 헬퍼 함수"""
    return error_handler.handle_error(
        service_type=service_type,
        error_code=error_code,
        error_message=error_message,
        context=context,
        severity=severity
    )

def get_all_service_status() -> Dict[str, Any]:
    """모든 서비스 상태 조회 헬퍼 함수"""
    return error_handler.get_service_status()

def get_error_stats(hours: int = 24) -> Dict[str, Any]:
    """오류 통계 조회 헬퍼 함수"""
    return error_handler.get_error_statistics(hours)