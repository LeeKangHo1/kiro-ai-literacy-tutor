# tests/unit/test_workflow.py
# 워크플로우 기본 구조 테스트

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from workflow.state_management import TutorState, StateManager
from workflow.node_definitions import NodeDefinitions, NodeRegistry
from workflow.edge_conditions import EdgeConditions, EdgeRegistry

# LangGraph 의존성을 조건부로 임포트
try:
    from workflow.graph_builder import TutorGraphBuilder, GraphExecutor
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    TutorGraphBuilder = None
    GraphExecutor = None


class TestStateManager:
    """StateManager 테스트 클래스"""
    
    def test_create_initial_state(self):
        """초기 상태 생성 테스트"""
        user_id = "test_user_123"
        state = StateManager.create_initial_state(user_id)
        
        assert state['user_id'] == user_id
        assert state['current_chapter'] == 1
        assert state['current_stage'] == 'theory'
        assert state['user_level'] == 'low'
        assert state['user_type'] == 'beginner'
        assert isinstance(state['current_loop_conversations'], list)
        assert len(state['current_loop_conversations']) == 0
        assert isinstance(state['recent_loops_summary'], list)
        assert len(state['recent_loops_summary']) == 0
    
    def test_validate_state_valid(self):
        """유효한 상태 검증 테스트"""
        state = StateManager.create_initial_state("test_user")
        assert StateManager.validate_state(state) == True
    
    def test_validate_state_invalid_level(self):
        """잘못된 레벨 상태 검증 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['user_level'] = 'invalid_level'
        assert StateManager.validate_state(state) == False
    
    def test_validate_state_invalid_type(self):
        """잘못된 타입 상태 검증 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['user_type'] = 'invalid_type'
        assert StateManager.validate_state(state) == False
    
    def test_add_conversation(self):
        """대화 추가 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        state = StateManager.add_conversation(
            state,
            agent_name="TestAgent",
            user_message="테스트 메시지",
            system_response="테스트 응답"
        )
        
        assert len(state['current_loop_conversations']) == 1
        conversation = state['current_loop_conversations'][0]
        assert conversation['agent_name'] == "TestAgent"
        assert conversation['user_message'] == "테스트 메시지"
        assert conversation['system_response'] == "테스트 응답"
        assert conversation['sequence_order'] == 1
    
    def test_start_new_loop(self):
        """새 루프 시작 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 기존 대화 추가
        state = StateManager.add_conversation(
            state, "TestAgent", "메시지", "응답"
        )
        
        old_loop_id = state['current_loop_id']
        
        # 새 루프 시작
        state = StateManager.start_new_loop(state)
        
        assert state['current_loop_id'] != old_loop_id
        assert len(state['current_loop_conversations']) == 0
        assert len(state['recent_loops_summary']) == 1
    
    def test_get_context_for_agent(self):
        """에이전트용 컨텍스트 생성 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_chapter'] = 2
        state['user_level'] = 'medium'
        
        context = StateManager.get_context_for_agent(state, "TestAgent")
        
        assert "사용자 레벨: medium" in context
        assert "현재 챕터: 2" in context


class TestNodeDefinitions:
    """NodeDefinitions 테스트 클래스"""
    
    def test_start_node(self):
        """시작 노드 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        result_state = NodeDefinitions.start_node(state)
        
        assert result_state['system_message'] == "학습을 시작합니다."
        assert result_state['current_stage'] == "theory"
    
    def test_end_node(self):
        """종료 노드 테스트"""
        state = StateManager.create_initial_state("test_user")
        
        # 대화 추가
        state = StateManager.add_conversation(
            state, "TestAgent", "메시지", "응답"
        )
        
        result_state = NodeDefinitions.end_node(state)
        
        assert result_state['system_message'] == "학습 루프가 완료되었습니다."
        assert result_state['current_stage'] == "completed"
        assert len(result_state['recent_loops_summary']) == 1


class TestNodeRegistry:
    """NodeRegistry 테스트 클래스"""
    
    def test_get_node_existing(self):
        """존재하는 노드 가져오기 테스트"""
        node_func = NodeRegistry.get_node('start')
        assert node_func is not None
        assert callable(node_func)
    
    def test_get_node_non_existing(self):
        """존재하지 않는 노드 가져오기 테스트"""
        node_func = NodeRegistry.get_node('non_existing_node')
        assert node_func is None
    
    def test_validate_node_name_valid(self):
        """유효한 노드 이름 검증 테스트"""
        assert NodeRegistry.validate_node_name('start') == True
        assert NodeRegistry.validate_node_name('learning_supervisor') == True
    
    def test_validate_node_name_invalid(self):
        """잘못된 노드 이름 검증 테스트"""
        assert NodeRegistry.validate_node_name('invalid_node') == False
    
    def test_get_all_nodes(self):
        """모든 노드 가져오기 테스트"""
        nodes = NodeRegistry.get_all_nodes()
        
        assert isinstance(nodes, dict)
        assert 'start' in nodes
        assert 'end' in nodes
        assert 'learning_supervisor' in nodes
        assert len(nodes) > 0


class TestEdgeConditions:
    """EdgeConditions 테스트 클래스"""
    
    def test_supervisor_routing_condition_theory(self):
        """슈퍼바이저 라우팅 - 이론 단계 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'theory'
        
        result = EdgeConditions.supervisor_routing_condition(state)
        assert result == "theory_educator"
    
    def test_supervisor_routing_condition_completed(self):
        """슈퍼바이저 라우팅 - 완료 단계 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'completed'
        
        result = EdgeConditions.supervisor_routing_condition(state)
        assert result == "end"
    
    def test_supervisor_routing_condition_question(self):
        """슈퍼바이저 라우팅 - 질문 단계 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'question'
        
        result = EdgeConditions.supervisor_routing_condition(state)
        assert result == "qna_resolver"
    
    def test_should_continue_condition_true(self):
        """계속 진행 조건 - True 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'theory'
        
        result = EdgeConditions.should_continue_condition(state)
        assert result == True
    
    def test_should_continue_condition_false_error(self):
        """계속 진행 조건 - 오류 상태 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['ui_mode'] = 'error'
        
        result = EdgeConditions.should_continue_condition(state)
        assert result == False
    
    def test_should_continue_condition_false_completed(self):
        """계속 진행 조건 - 완료 상태 테스트"""
        state = StateManager.create_initial_state("test_user")
        state['current_stage'] = 'completed'
        
        result = EdgeConditions.should_continue_condition(state)
        assert result == False


class TestEdgeRegistry:
    """EdgeRegistry 테스트 클래스"""
    
    def test_get_condition_existing(self):
        """존재하는 조건 가져오기 테스트"""
        condition_func = EdgeRegistry.get_condition('supervisor_routing')
        assert condition_func is not None
        assert callable(condition_func)
    
    def test_get_condition_non_existing(self):
        """존재하지 않는 조건 가져오기 테스트"""
        condition_func = EdgeRegistry.get_condition('non_existing_condition')
        assert condition_func is None
    
    def test_validate_condition_name_valid(self):
        """유효한 조건 이름 검증 테스트"""
        assert EdgeRegistry.validate_condition_name('supervisor_routing') == True
        assert EdgeRegistry.validate_condition_name('should_continue') == True
    
    def test_validate_condition_name_invalid(self):
        """잘못된 조건 이름 검증 테스트"""
        assert EdgeRegistry.validate_condition_name('invalid_condition') == False


class TestTutorGraphBuilder:
    """TutorGraphBuilder 테스트 클래스"""
    
    def test_build_graph(self):
        """그래프 빌드 테스트"""
        builder = TutorGraphBuilder()
        graph = builder.build_graph()
        
        assert graph is not None
        assert builder.graph is not None
    
    @patch('workflow.graph_builder.StateGraph')
    def test_add_nodes(self, mock_state_graph):
        """노드 추가 테스트"""
        mock_workflow = Mock()
        mock_state_graph.return_value = mock_workflow
        
        builder = TutorGraphBuilder()
        builder._add_nodes(mock_workflow)
        
        # 모든 노드가 추가되었는지 확인
        expected_calls = len(NodeRegistry.get_all_nodes())
        assert mock_workflow.add_node.call_count == expected_calls
    
    def test_compile_graph(self):
        """그래프 컴파일 테스트"""
        builder = TutorGraphBuilder()
        
        # 실제 컴파일은 LangGraph 의존성 때문에 스킵하고 구조만 테스트
        try:
            compiled_graph = builder.compile_graph()
            assert compiled_graph is not None
        except ImportError:
            # LangGraph가 설치되지 않은 경우 패스
            pytest.skip("LangGraph not installed")


class TestGraphExecutor:
    """GraphExecutor 테스트 클래스"""
    
    def test_initialize(self):
        """그래프 실행기 초기화 테스트"""
        executor = GraphExecutor()
        
        try:
            executor.initialize()
            assert executor.compiled_graph is not None
        except ImportError:
            # LangGraph가 설치되지 않은 경우 패스
            pytest.skip("LangGraph not installed")
    
    def test_execute_step_error_handling(self):
        """실행 단계 오류 처리 테스트"""
        executor = GraphExecutor()
        state = StateManager.create_initial_state("test_user")
        
        # 컴파일된 그래프가 없는 상태에서 실행
        result_state = executor.execute_step(state)
        
        # 오류 상태로 변경되어야 함
        assert 'ui_mode' in result_state
        assert 'system_message' in result_state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])