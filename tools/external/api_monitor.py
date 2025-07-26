# tools/external/api_monitor.py
# API 호출 모니터링 및 관리 시스템

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from enum import Enum

# 로깅 설정
logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """API 상태 열거형"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    RATE_LIMITED = "rate_limited"

@dataclass
class APICallRecord:
    """API 호출 기록"""
    timestamp: datetime
    endpoint: str
    success: bool
    response_time: float
    error_message: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None

@dataclass
class APIMetrics:
    """API 메트릭"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    rate_limit_hits: int = 0
    last_call_time: Optional[datetime] = None
    status: APIStatus = APIStatus.HEALTHY

class APIMonitor:
    """API 모니터링 시스템"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.call_records: deque = deque(maxlen=max_records)
        self.metrics = APIMetrics()
        self.status_history: deque = deque(maxlen=100)
        self.rate_limit_window = timedelta(minutes=1)
        self.max_calls_per_minute = 60  # OpenAI 기본 제한
        self.lock = threading.Lock()
        
        # 알림 설정
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% 이상 오류율
            "response_time": 5.0,  # 5초 이상 응답 시간
            "rate_limit_ratio": 0.8  # 80% 이상 rate limit 사용
        }
        
        self.alerts_enabled = True
        self.alert_callbacks = []
    
    def record_api_call(
        self,
        endpoint: str,
        success: bool,
        response_time: float,
        error_message: Optional[str] = None,
        token_usage: Optional[Dict[str, int]] = None,
        model: Optional[str] = None
    ):
        """API 호출 기록"""
        with self.lock:
            # 호출 기록 추가
            record = APICallRecord(
                timestamp=datetime.now(),
                endpoint=endpoint,
                success=success,
                response_time=response_time,
                error_message=error_message,
                token_usage=token_usage,
                model=model
            )
            self.call_records.append(record)
            
            # 메트릭 업데이트
            self._update_metrics(record)
            
            # 상태 평가
            self._evaluate_status()
            
            # 알림 확인
            if self.alerts_enabled:
                self._check_alerts()
    
    def _update_metrics(self, record: APICallRecord):
        """메트릭 업데이트"""
        self.metrics.total_calls += 1
        self.metrics.last_call_time = record.timestamp
        
        if record.success:
            self.metrics.successful_calls += 1
        else:
            self.metrics.failed_calls += 1
            if record.error_message and "rate_limit" in record.error_message.lower():
                self.metrics.rate_limit_hits += 1
        
        # 평균 응답 시간 계산
        total_time = (self.metrics.average_response_time * (self.metrics.total_calls - 1) + 
                     record.response_time)
        self.metrics.average_response_time = total_time / self.metrics.total_calls
        
        # 토큰 사용량 업데이트
        if record.token_usage:
            total_tokens = record.token_usage.get("total_tokens", 0)
            self.metrics.total_tokens_used += total_tokens
    
    def _evaluate_status(self):
        """API 상태 평가"""
        if not self.call_records:
            return
        
        # 최근 10분간의 기록만 고려
        recent_time = datetime.now() - timedelta(minutes=10)
        recent_records = [r for r in self.call_records if r.timestamp > recent_time]
        
        if not recent_records:
            return
        
        # 오류율 계산
        error_rate = sum(1 for r in recent_records if not r.success) / len(recent_records)
        
        # 평균 응답 시간 계산
        avg_response_time = sum(r.response_time for r in recent_records) / len(recent_records)
        
        # Rate limit 비율 계산
        rate_limit_rate = sum(1 for r in recent_records 
                             if r.error_message and "rate_limit" in r.error_message.lower()) / len(recent_records)
        
        # 상태 결정
        if rate_limit_rate > 0.5:
            new_status = APIStatus.RATE_LIMITED
        elif error_rate > 0.3 or avg_response_time > 10.0:
            new_status = APIStatus.DOWN
        elif error_rate > 0.1 or avg_response_time > 5.0:
            new_status = APIStatus.DEGRADED
        else:
            new_status = APIStatus.HEALTHY
        
        # 상태 변경 시 기록
        if new_status != self.metrics.status:
            self.status_history.append({
                "timestamp": datetime.now(),
                "old_status": self.metrics.status.value,
                "new_status": new_status.value,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time
            })
            self.metrics.status = new_status
            logger.info(f"API 상태 변경: {new_status.value}")
    
    def _check_alerts(self):
        """알림 조건 확인"""
        if not self.call_records:
            return
        
        # 최근 5분간의 기록 확인
        recent_time = datetime.now() - timedelta(minutes=5)
        recent_records = [r for r in self.call_records if r.timestamp > recent_time]
        
        if len(recent_records) < 5:  # 최소 5개 호출 필요
            return
        
        # 오류율 알림
        error_rate = sum(1 for r in recent_records if not r.success) / len(recent_records)
        if error_rate > self.alert_thresholds["error_rate"]:
            self._trigger_alert("high_error_rate", {
                "error_rate": error_rate,
                "threshold": self.alert_thresholds["error_rate"],
                "recent_calls": len(recent_records)
            })
        
        # 응답 시간 알림
        avg_response_time = sum(r.response_time for r in recent_records) / len(recent_records)
        if avg_response_time > self.alert_thresholds["response_time"]:
            self._trigger_alert("slow_response", {
                "avg_response_time": avg_response_time,
                "threshold": self.alert_thresholds["response_time"],
                "recent_calls": len(recent_records)
            })
        
        # Rate limit 알림
        rate_limit_calls = sum(1 for r in recent_records 
                              if r.error_message and "rate_limit" in r.error_message.lower())
        rate_limit_ratio = rate_limit_calls / len(recent_records)
        if rate_limit_ratio > self.alert_thresholds["rate_limit_ratio"]:
            self._trigger_alert("rate_limit_warning", {
                "rate_limit_ratio": rate_limit_ratio,
                "threshold": self.alert_thresholds["rate_limit_ratio"],
                "recent_calls": len(recent_records)
            })
    
    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """알림 발생"""
        alert = {
            "type": alert_type,
            "timestamp": datetime.now(),
            "data": data,
            "message": self._generate_alert_message(alert_type, data)
        }
        
        logger.warning(f"API 알림: {alert['message']}")
        
        # 등록된 콜백 실행
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {str(e)}")
    
    def _generate_alert_message(self, alert_type: str, data: Dict[str, Any]) -> str:
        """알림 메시지 생성"""
        if alert_type == "high_error_rate":
            return f"높은 오류율 감지: {data['error_rate']:.1%} (임계값: {data['threshold']:.1%})"
        elif alert_type == "slow_response":
            return f"느린 응답 시간 감지: {data['avg_response_time']:.2f}초 (임계값: {data['threshold']:.2f}초)"
        elif alert_type == "rate_limit_warning":
            return f"Rate limit 경고: {data['rate_limit_ratio']:.1%} (임계값: {data['threshold']:.1%})"
        else:
            return f"알 수 없는 알림: {alert_type}"
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 조회"""
        with self.lock:
            return {
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "success_rate": (self.metrics.successful_calls / self.metrics.total_calls 
                               if self.metrics.total_calls > 0 else 0.0),
                "average_response_time": self.metrics.average_response_time,
                "total_tokens_used": self.metrics.total_tokens_used,
                "rate_limit_hits": self.metrics.rate_limit_hits,
                "current_status": self.metrics.status.value,
                "last_call_time": self.metrics.last_call_time.isoformat() if self.metrics.last_call_time else None
            }
    
    def get_recent_calls(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """최근 호출 기록 조회"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_records = [r for r in self.call_records if r.timestamp > cutoff_time]
        
        return [
            {
                "timestamp": record.timestamp.isoformat(),
                "endpoint": record.endpoint,
                "success": record.success,
                "response_time": record.response_time,
                "error_message": record.error_message,
                "token_usage": record.token_usage,
                "model": record.model
            }
            for record in recent_records
        ]
    
    def get_status_history(self) -> List[Dict[str, Any]]:
        """상태 변경 이력 조회"""
        return list(self.status_history)
    
    def add_alert_callback(self, callback):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback):
        """알림 콜백 제거"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def reset_metrics(self):
        """메트릭 초기화"""
        with self.lock:
            self.call_records.clear()
            self.metrics = APIMetrics()
            self.status_history.clear()
            logger.info("API 메트릭이 초기화되었습니다.")

class RateLimiter:
    """Rate Limiting 관리"""
    
    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls_per_minute = max_calls_per_minute
        self.call_times: deque = deque()
        self.lock = threading.Lock()
    
    def can_make_call(self) -> bool:
        """호출 가능 여부 확인"""
        with self.lock:
            now = datetime.now()
            cutoff_time = now - timedelta(minutes=1)
            
            # 1분 이전 호출 기록 제거
            while self.call_times and self.call_times[0] < cutoff_time:
                self.call_times.popleft()
            
            return len(self.call_times) < self.max_calls_per_minute
    
    def record_call(self):
        """호출 기록"""
        with self.lock:
            self.call_times.append(datetime.now())
    
    def get_wait_time(self) -> float:
        """대기 시간 계산 (초)"""
        with self.lock:
            if len(self.call_times) < self.max_calls_per_minute:
                return 0.0
            
            oldest_call = self.call_times[0]
            wait_until = oldest_call + timedelta(minutes=1)
            wait_time = (wait_until - datetime.now()).total_seconds()
            
            return max(0.0, wait_time)

# 전역 모니터 및 Rate Limiter 인스턴스
api_monitor = APIMonitor()
rate_limiter = RateLimiter()

def log_api_call(
    endpoint: str,
    success: bool,
    response_time: float,
    error_message: Optional[str] = None,
    token_usage: Optional[Dict[str, int]] = None,
    model: Optional[str] = None
):
    """API 호출 로깅 헬퍼 함수"""
    api_monitor.record_api_call(
        endpoint=endpoint,
        success=success,
        response_time=response_time,
        error_message=error_message,
        token_usage=token_usage,
        model=model
    )

def check_rate_limit() -> bool:
    """Rate limit 확인 헬퍼 함수"""
    return rate_limiter.can_make_call()

def wait_for_rate_limit():
    """Rate limit 대기 헬퍼 함수"""
    wait_time = rate_limiter.get_wait_time()
    if wait_time > 0:
        logger.info(f"Rate limit 대기: {wait_time:.2f}초")
        time.sleep(wait_time)

def record_rate_limit_call():
    """Rate limit 호출 기록 헬퍼 함수"""
    rate_limiter.record_call()