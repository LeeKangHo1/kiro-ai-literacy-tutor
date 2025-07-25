# utils/langsmith_config.py
# LangSmith 설정 및 초기화

import os
from typing import Optional, Dict, Any
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager


class LangSmithConfig:
    """LangSmith 설정 및 관리 클래스"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.tracer: Optional[LangChainTracer] = None
        self.callback_manager: Optional[CallbackManager] = None
        self.project_name = None
        
    def initialize(self) -> bool:
        """LangSmith 초기화"""
        try:
            # 환경 변수 확인
            api_key = os.getenv('LANGCHAIN_API_KEY')
            tracing_enabled = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
            self.project_name = os.getenv('LANGCHAIN_PROJECT', 'ai-literacy-navigator')
            
            if not api_key or not tracing_enabled:
                print("LangSmith 설정이 비활성화되어 있습니다.")
                return False
            
            # LangSmith 클라이언트 초기화
            self.client = Client(
                api_url=os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com'),
                api_key=api_key
            )
            
            # 트레이서 초기화
            self.tracer = LangChainTracer(
                project_name=self.project_name,
                client=self.client
            )
            
            # 콜백 매니저 초기화
            self.callback_manager = CallbackManager([self.tracer])
            
            print(f"LangSmith가 성공적으로 초기화되었습니다. 프로젝트: {self.project_name}")
            return True
            
        except Exception as e:
            print(f"LangSmith 초기화 실패: {str(e)}")
            return False
    
    def get_callbacks(self) -> list:
        """콜백 리스트 반환"""
        if self.tracer:
            return [self.tracer]
        return []
    
    def get_callback_manager(self) -> Optional[CallbackManager]:
        """콜백 매니저 반환"""
        return self.callback_manager
    
    def create_run(self, name: str, run_type: str = "chain", 
                   inputs: Optional[Dict[str, Any]] = None,
                   tags: Optional[list] = None) -> Optional[str]:
        """새로운 실행 추적 생성"""
        if not self.client:
            return None
        
        try:
            run = self.client.create_run(
                name=name,
                run_type=run_type,
                inputs=inputs or {},
                project_name=self.project_name,
                tags=tags or []
            )
            return str(run.id)
        except Exception as e:
            print(f"실행 추적 생성 실패: {str(e)}")
            return None
    
    def end_run(self, run_id: str, outputs: Optional[Dict[str, Any]] = None,
                error: Optional[str] = None):
        """실행 추적 종료"""
        if not self.client or not run_id:
            return
        
        try:
            self.client.update_run(
                run_id=run_id,
                outputs=outputs or {},
                error=error
            )
        except Exception as e:
            print(f"실행 추적 종료 실패: {str(e)}")
    
    def log_feedback(self, run_id: str, key: str, score: float, 
                     comment: Optional[str] = None):
        """피드백 로깅"""
        if not self.client or not run_id:
            return
        
        try:
            self.client.create_feedback(
                run_id=run_id,
                key=key,
                score=score,
                comment=comment
            )
        except Exception as e:
            print(f"피드백 로깅 실패: {str(e)}")
    
    def is_enabled(self) -> bool:
        """LangSmith 활성화 여부 확인"""
        return self.client is not None and self.tracer is not None


# 전역 LangSmith 설정 인스턴스
langsmith_config = LangSmithConfig()


def initialize_langsmith() -> bool:
    """LangSmith 초기화 함수"""
    return langsmith_config.initialize()


def get_langsmith_callbacks() -> list:
    """LangSmith 콜백 반환"""
    return langsmith_config.get_callbacks()


def get_langsmith_callback_manager() -> Optional[CallbackManager]:
    """LangSmith 콜백 매니저 반환"""
    return langsmith_config.get_callback_manager()


def trace_agent_execution(agent_name: str, inputs: Dict[str, Any], 
                         tags: Optional[list] = None) -> Optional[str]:
    """에이전트 실행 추적"""
    return langsmith_config.create_run(
        name=f"{agent_name}_execution",
        run_type="agent",
        inputs=inputs,
        tags=(tags or []) + [agent_name, "agent_execution"]
    )


def end_agent_trace(run_id: str, outputs: Dict[str, Any], 
                   error: Optional[str] = None):
    """에이전트 실행 추적 종료"""
    langsmith_config.end_run(run_id, outputs, error)


def log_user_feedback(run_id: str, rating: int, comment: Optional[str] = None):
    """사용자 피드백 로깅"""
    langsmith_config.log_feedback(
        run_id=run_id,
        key="user_rating",
        score=rating / 5.0,  # 1-5 점수를 0-1로 정규화
        comment=comment
    )