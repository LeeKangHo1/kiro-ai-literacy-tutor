# tools/external/alert_system.py
# 알림 시스템

import logging
import json
from typing import Dict, Any, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from .error_handler import error_handler
from .api_monitor import api_monitor

# 로깅 설정
logger = logging.getLogger(__name__)

class AlertChannel(Enum):
    """알림 채널 유형"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"

@dataclass
class AlertRule:
    """알림 규칙"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    message_template: str
    channels: List[AlertChannel]
    cooldown_minutes: int = 5
    enabled: bool = True

class AlertSystem:
    """알림 시스템"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
        # 기본 알림 규칙 설정
        self._setup_default_rules()
        
        # 오류 처리기와 API 모니터에 콜백 등록
        error_handler.add_alert_callback(self._handle_error_alert)
        api_monitor.add_alert_callback(self._handle_api_alert)
    
    def _setup_default_rules(self):
        """기본 알림 규칙 설정"""
        
        # ChatGPT API 오류율 높음
        self.add_rule(AlertRule(
            name="chatgpt_high_error_rate",
            condition=lambda data: (
                data.get("service") == "chatgpt_api" and
                data.get("data", {}).get("error_rate", 0) > 0.2
            ),
            message_template="ChatGPT API 오류율이 높습니다: {error_rate:.1%}",
            channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
            cooldown_minutes=10
        ))
        
        # ChromaDB 연결 실패
        self.add_rule(AlertRule(
            name="chromadb_connection_failed",
            condition=lambda data: (
                data.get("service") == "chromadb" and
                "connection" in data.get("error_code", "").lower()
            ),
            message_template="ChromaDB 연결에 실패했습니다: {message}",
            channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
            cooldown_minutes=5
        ))
        
        # API 응답 시간 느림
        self.add_rule(AlertRule(
            name="slow_api_response",
            condition=lambda data: (
                data.get("type") == "slow_response" and
                data.get("data", {}).get("avg_response_time", 0) > 10.0
            ),
            message_template="API 응답 시간이 느립니다: {avg_response_time:.2f}초",
            channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
            cooldown_minutes=15
        ))
        
        # Rate limit 경고
        self.add_rule(AlertRule(
            name="rate_limit_warning",
            condition=lambda data: (
                data.get("type") == "rate_limit_warning"
            ),
            message_template="Rate limit 경고: {rate_limit_ratio:.1%}",
            channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
            cooldown_minutes=5
        ))
    
    def add_rule(self, rule: AlertRule):
        """알림 규칙 추가"""
        self.rules.append(rule)
        logger.info(f"알림 규칙 추가됨: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """알림 규칙 제거"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        logger.info(f"알림 규칙 제거됨: {rule_name}")
    
    def _handle_error_alert(self, alert_data: Dict[str, Any]):
        """오류 처리기에서 온 알림 처리"""
        self._process_alert(alert_data)
    
    def _handle_api_alert(self, alert_data: Dict[str, Any]):
        """API 모니터에서 온 알림 처리"""
        self._process_alert(alert_data)
    
    def _process_alert(self, alert_data: Dict[str, Any]):
        """알림 처리"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(alert_data):
                    # Cooldown 확인
                    if self._is_in_cooldown(rule.name):
                        continue
                    
                    # 알림 발송
                    self._send_alert(rule, alert_data)
                    
                    # Cooldown 시간 기록
                    self.last_alert_times[rule.name] = datetime.now()
                    
            except Exception as e:
                logger.error(f"알림 규칙 처리 중 오류 ({rule.name}): {str(e)}")
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Cooldown 시간 확인"""
        last_time = self.last_alert_times.get(rule_name)
        if not last_time:
            return False
        
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False
        
        cooldown_delta = datetime.now() - last_time
        return cooldown_delta.total_seconds() < (rule.cooldown_minutes * 60)
    
    def _send_alert(self, rule: AlertRule, alert_data: Dict[str, Any]):
        """알림 발송"""
        try:
            # 메시지 생성
            message = rule.message_template.format(**alert_data.get("data", {}), **alert_data)
            
            alert_info = {
                "rule_name": rule.name,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "channels": [channel.value for channel in rule.channels],
                "alert_data": alert_data
            }
            
            # 채널별 알림 발송
            for channel in rule.channels:
                self._send_to_channel(channel, alert_info)
            
            # 알림 이력 저장
            self.alert_history.append(alert_info)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)
            
            logger.info(f"알림 발송됨: {rule.name} - {message}")
            
        except Exception as e:
            logger.error(f"알림 발송 중 오류: {str(e)}")
    
    def _send_to_channel(self, channel: AlertChannel, alert_info: Dict[str, Any]):
        """특정 채널로 알림 발송"""
        try:
            if channel == AlertChannel.LOG:
                logger.warning(f"[ALERT] {alert_info['message']}")
            
            elif channel == AlertChannel.CONSOLE:
                print(f"🚨 ALERT: {alert_info['message']} ({alert_info['timestamp']})")
            
            elif channel == AlertChannel.EMAIL:
                # 이메일 발송 로직 (구현 필요)
                logger.info(f"이메일 알림 발송 (구현 필요): {alert_info['message']}")
            
            elif channel == AlertChannel.WEBHOOK:
                # 웹훅 발송 로직 (구현 필요)
                logger.info(f"웹훅 알림 발송 (구현 필요): {alert_info['message']}")
            
        except Exception as e:
            logger.error(f"채널 {channel.value}로 알림 발송 실패: {str(e)}")
    
    def get_alert_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """알림 이력 조회"""
        return self.alert_history[-limit:]
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """활성 알림 규칙 조회"""
        return [
            {
                "name": rule.name,
                "enabled": rule.enabled,
                "channels": [channel.value for channel in rule.channels],
                "cooldown_minutes": rule.cooldown_minutes,
                "last_triggered": self.last_alert_times.get(rule.name, "").isoformat() if self.last_alert_times.get(rule.name) else None
            }
            for rule in self.rules
        ]
    
    def enable_rule(self, rule_name: str):
        """알림 규칙 활성화"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"알림 규칙 활성화됨: {rule_name}")
                return True
        return False
    
    def disable_rule(self, rule_name: str):
        """알림 규칙 비활성화"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"알림 규칙 비활성화됨: {rule_name}")
                return True
        return False
    
    def test_alert(self, rule_name: str):
        """알림 테스트"""
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False
        
        test_data = {
            "type": "test",
            "message": "테스트 알림입니다",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": True}
        }
        
        self._send_alert(rule, test_data)
        return True

# 전역 알림 시스템 인스턴스
alert_system = AlertSystem()

def get_alert_system() -> AlertSystem:
    """알림 시스템 인스턴스 반환"""
    return alert_system