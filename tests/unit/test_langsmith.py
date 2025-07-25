# tests/unit/test_langsmith.py
# LangSmith 설정 테스트

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from utils.langsmith_config import (
    LangSmithConfig, 
    initialize_langsmith,
    get_langsmith_callbacks,
    trace_agent_execution,
    end_agent_trace,
    log_user_feedback
)


class TestLangSmithConfig:
    """LangSmithConfig 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.config = LangSmithConfig()
    
    @patch.dict(os.environ, {
        'LANGCHAIN_TRACING_V2': 'true',
        'LANGCHAIN_API_KEY': 'test-api-key',
        'LANGCHAIN_PROJECT': 'test-project'
    })
    @patch('utils.langsmith_config.Client')
    @patch('utils.langsmith_config.LangChainTracer')
    def test_initialize_success(self, mock_tracer, mock_client):
        """성공적인 초기화 테스트"""
        # Mock 설정
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_tracer_instance = Mock()
        mock_tracer.return_value = mock_tracer_instance
        
        # 초기화 실행
        result = self.config.initialize()
        
        # 검증
        assert result == True
        assert self.config.client == mock_client_instance
        assert self.config.tracer == mock_tracer_instance
        assert self.config.project_name == 'test-project'
    
    @patch.dict(os.environ, {
        'LANGCHAIN_TRACING_V2': 'false'
    })
    def test_initialize_disabled(self):
        """비활성화된 상태 초기화 테스트"""
        result = self.config.initialize()
        
        assert result == False
        assert self.config.client is None
        assert self.config.tracer is None
    
    @patch.dict(os.environ, {
        'LANGCHAIN_TRACING_V2': 'true'
    })
    def test_initialize_no_api_key(self):
        """API 키 없는 상태 초기화 테스트"""
        # LANGCHAIN_API_KEY 환경 변수 제거
        if 'LANGCHAIN_API_KEY' in os.environ:
            del os.environ['LANGCHAIN_API_KEY']
        
        result = self.config.initialize()
        
        assert result == False
        assert self.config.client is None
    
    def test_get_callbacks_with_tracer(self):
        """트레이서가 있는 경우 콜백 반환 테스트"""
        mock_tracer = Mock()
        self.config.tracer = mock_tracer
        
        callbacks = self.config.get_callbacks()
        
        assert callbacks == [mock_tracer]
    
    def test_get_callbacks_without_tracer(self):
        """트레이서가 없는 경우 콜백 반환 테스트"""
        callbacks = self.config.get_callbacks()
        
        assert callbacks == []
    
    def test_create_run_success(self):
        """실행 추적 생성 성공 테스트"""
        # Mock 클라이언트 설정
        mock_client = Mock()
        mock_run = Mock()
        mock_run.id = 'test-run-id'
        mock_client.create_run.return_value = mock_run
        
        self.config.client = mock_client
        self.config.project_name = 'test-project'
        
        # 실행 추적 생성
        run_id = self.config.create_run(
            name='test_run',
            run_type='agent',
            inputs={'test': 'input'},
            tags=['test']
        )
        
        # 검증
        assert run_id == 'test-run-id'
        mock_client.create_run.assert_called_once_with(
            name='test_run',
            run_type='agent',
            inputs={'test': 'input'},
            project_name='test-project',
            tags=['test']
        )
    
    def test_create_run_no_client(self):
        """클라이언트 없는 상태에서 실행 추적 생성 테스트"""
        run_id = self.config.create_run('test_run')
        
        assert run_id is None
    
    def test_end_run_success(self):
        """실행 추적 종료 성공 테스트"""
        mock_client = Mock()
        self.config.client = mock_client
        
        self.config.end_run(
            run_id='test-run-id',
            outputs={'result': 'success'},
            error=None
        )
        
        mock_client.update_run.assert_called_once_with(
            run_id='test-run-id',
            outputs={'result': 'success'},
            error=None
        )
    
    def test_log_feedback_success(self):
        """피드백 로깅 성공 테스트"""
        mock_client = Mock()
        self.config.client = mock_client
        
        self.config.log_feedback(
            run_id='test-run-id',
            key='user_rating',
            score=0.8,
            comment='Good response'
        )
        
        mock_client.create_feedback.assert_called_once_with(
            run_id='test-run-id',
            key='user_rating',
            score=0.8,
            comment='Good response'
        )
    
    def test_is_enabled_true(self):
        """활성화 상태 확인 테스트"""
        self.config.client = Mock()
        self.config.tracer = Mock()
        
        assert self.config.is_enabled() == True
    
    def test_is_enabled_false(self):
        """비활성화 상태 확인 테스트"""
        assert self.config.is_enabled() == False


class TestLangSmithFunctions:
    """LangSmith 유틸리티 함수 테스트 클래스"""
    
    @patch('utils.langsmith_config.langsmith_config')
    def test_initialize_langsmith(self, mock_config):
        """LangSmith 초기화 함수 테스트"""
        mock_config.initialize.return_value = True
        
        result = initialize_langsmith()
        
        assert result == True
        mock_config.initialize.assert_called_once()
    
    @patch('utils.langsmith_config.langsmith_config')
    def test_get_langsmith_callbacks(self, mock_config):
        """LangSmith 콜백 반환 함수 테스트"""
        mock_callbacks = [Mock()]
        mock_config.get_callbacks.return_value = mock_callbacks
        
        callbacks = get_langsmith_callbacks()
        
        assert callbacks == mock_callbacks
        mock_config.get_callbacks.assert_called_once()
    
    @patch('utils.langsmith_config.langsmith_config')
    def test_trace_agent_execution(self, mock_config):
        """에이전트 실행 추적 함수 테스트"""
        mock_config.create_run.return_value = 'test-run-id'
        
        run_id = trace_agent_execution(
            agent_name='TestAgent',
            inputs={'test': 'input'},
            tags=['test']
        )
        
        assert run_id == 'test-run-id'
        mock_config.create_run.assert_called_once_with(
            name='TestAgent_execution',
            run_type='agent',
            inputs={'test': 'input'},
            tags=['test', 'TestAgent', 'agent_execution']
        )
    
    @patch('utils.langsmith_config.langsmith_config')
    def test_end_agent_trace(self, mock_config):
        """에이전트 실행 추적 종료 함수 테스트"""
        end_agent_trace(
            run_id='test-run-id',
            outputs={'result': 'success'},
            error=None
        )
        
        mock_config.end_run.assert_called_once_with(
            'test-run-id',
            {'result': 'success'},
            None
        )
    
    @patch('utils.langsmith_config.langsmith_config')
    def test_log_user_feedback(self, mock_config):
        """사용자 피드백 로깅 함수 테스트"""
        log_user_feedback(
            run_id='test-run-id',
            rating=4,
            comment='Good response'
        )
        
        mock_config.log_feedback.assert_called_once_with(
            run_id='test-run-id',
            key='user_rating',
            score=0.8,  # 4/5 = 0.8
            comment='Good response'
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])