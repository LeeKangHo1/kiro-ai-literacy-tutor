# workflow/graph_builder.py
# StateGraph 구성 및 노드 연결 모듈

from langgraph.graph import StateGraph, END
from .state_management import TutorState
from .node_definitions import NodeRegistry
from .edge_conditions import EdgeRegistry


class TutorGraphBuilder:
    """튜터 시스템의 LangGraph 워크플로우를 구성하는 클래스"""
    
    def __init__(self):
        self.graph = None
        self.compiled_graph = None
    
    def build_graph(self) -> StateGraph:
        """전체 워크플로우 그래프 구성"""
        
        # StateGraph 초기화
        workflow = StateGraph(TutorState)
        
        # 노드 추가
        self._add_nodes(workflow)
        
        # 엣지 추가
        self._add_edges(workflow)
        
        # 시작점 설정
        workflow.set_entry_point("start")
        
        self.graph = workflow
        return workflow
    
    def _add_nodes(self, workflow: StateGraph):
        """모든 노드를 워크플로우에 추가"""
        
        # NodeRegistry에서 모든 노드 가져와서 추가
        nodes = NodeRegistry.get_all_nodes()
        
        for node_name, node_function in nodes.items():
            workflow.add_node(node_name, node_function)
    
    def _add_edges(self, workflow: StateGraph):
        """모든 엣지를 워크플로우에 추가"""
        
        # 1. 시작 노드 → LearningSupervisor
        workflow.add_edge("start", "learning_supervisor")
        
        # 2. LearningSupervisor → 조건부 라우팅
        workflow.add_conditional_edges(
            "learning_supervisor",
            EdgeRegistry.get_condition('supervisor_routing'),
            {
                "theory_educator": "theory_educator",
                "end": END,
                "qna_resolver": "qna_resolver"
            }
        )
        
        # 3. TheoryEducator → PostTheoryRouter
        workflow.add_edge("theory_educator", "post_theory_router")
        
        # 4. PostTheoryRouter → 조건부 라우팅 (QnA 또는 Quiz)
        workflow.add_conditional_edges(
            "post_theory_router",
            EdgeRegistry.get_condition('post_theory_routing'),
            {
                "qna_resolver": "qna_resolver",
                "quiz_generator": "quiz_generator"
            }
        )
        
        # 5. QuizGenerator → EvaluationFeedback
        workflow.add_edge("quiz_generator", "evaluation_feedback")
        
        # 6. EvaluationFeedback → PostFeedbackRouter
        workflow.add_edge("evaluation_feedback", "post_feedback_router")
        
        # 7. PostFeedbackRouter → 조건부 라우팅 (QnA 또는 Supervisor)
        workflow.add_conditional_edges(
            "post_feedback_router",
            EdgeRegistry.get_condition('post_feedback_routing'),
            {
                "qna_resolver": "qna_resolver",
                "learning_supervisor": "learning_supervisor"
            }
        )
        
        # 8. QnAResolver → 조건부 라우팅 (출처에 따라 다른 라우터로)
        workflow.add_conditional_edges(
            "qna_resolver",
            EdgeRegistry.get_condition('qna_routing'),
            {
                "post_theory_router": "post_theory_router",
                "post_feedback_router": "post_feedback_router",
                "learning_supervisor": "learning_supervisor"
            }
        )
        
        # 9. 종료 노드 → END
        workflow.add_edge("end", END)
    
    def compile_graph(self):
        """그래프 컴파일"""
        if self.graph is None:
            self.build_graph()
        
        self.compiled_graph = self.graph.compile()
        return self.compiled_graph
    
    def get_compiled_graph(self):
        """컴파일된 그래프 반환"""
        if self.compiled_graph is None:
            self.compile_graph()
        
        return self.compiled_graph


class GraphExecutor:
    """그래프 실행을 담당하는 클래스"""
    
    def __init__(self, graph_builder: TutorGraphBuilder = None):
        self.graph_builder = graph_builder or TutorGraphBuilder()
        self.compiled_graph = None
    
    def initialize(self):
        """그래프 초기화"""
        self.compiled_graph = self.graph_builder.get_compiled_graph()
    
    def execute_step(self, state: TutorState) -> TutorState:
        """단일 스텝 실행"""
        if self.compiled_graph is None:
            self.initialize()
        
        try:
            # 그래프 실행
            result = self.compiled_graph.invoke(state)
            return result
        
        except Exception as e:
            # 실행 오류 처리
            state['system_message'] = f"워크플로우 실행 중 오류가 발생했습니다: {str(e)}"
            state['ui_mode'] = 'error'
            return state
    
    def execute_stream(self, state: TutorState):
        """스트리밍 실행 (단계별 결과 반환)"""
        if self.compiled_graph is None:
            self.initialize()
        
        try:
            for step_result in self.compiled_graph.stream(state):
                yield step_result
        
        except Exception as e:
            # 실행 오류 처리
            error_state = state.copy()
            error_state['system_message'] = f"워크플로우 스트리밍 중 오류가 발생했습니다: {str(e)}"
            error_state['ui_mode'] = 'error'
            yield error_state


class GraphValidator:
    """그래프 유효성 검증을 담당하는 클래스"""
    
    @staticmethod
    def validate_graph_structure(graph_builder: TutorGraphBuilder) -> bool:
        """그래프 구조 유효성 검증"""
        try:
            # 그래프 빌드 시도
            graph = graph_builder.build_graph()
            
            # 컴파일 시도
            compiled = graph.compile()
            
            return True
        
        except Exception as e:
            print(f"그래프 검증 실패: {str(e)}")
            return False
    
    @staticmethod
    def validate_node_connections(graph_builder: TutorGraphBuilder) -> bool:
        """노드 연결 유효성 검증"""
        # 필수 노드들이 모두 존재하는지 확인
        required_nodes = [
            'start', 'learning_supervisor', 'theory_educator',
            'post_theory_router', 'quiz_generator', 'evaluation_feedback',
            'post_feedback_router', 'qna_resolver', 'end'
        ]
        
        available_nodes = NodeRegistry.get_all_nodes().keys()
        
        for node in required_nodes:
            if node not in available_nodes:
                print(f"필수 노드 누락: {node}")
                return False
        
        return True
    
    @staticmethod
    def validate_edge_conditions(graph_builder: TutorGraphBuilder) -> bool:
        """엣지 조건 유효성 검증"""
        # 필수 조건들이 모두 존재하는지 확인
        required_conditions = [
            'supervisor_routing', 'post_theory_routing',
            'post_feedback_routing', 'qna_routing'
        ]
        
        available_conditions = EdgeRegistry.get_all_conditions().keys()
        
        for condition in required_conditions:
            if condition not in available_conditions:
                print(f"필수 조건 누락: {condition}")
                return False
        
        return True


# 전역 그래프 인스턴스 (싱글톤 패턴)
_global_graph_builder = None
_global_executor = None


def get_graph_builder() -> TutorGraphBuilder:
    """전역 그래프 빌더 인스턴스 반환"""
    global _global_graph_builder
    if _global_graph_builder is None:
        _global_graph_builder = TutorGraphBuilder()
    return _global_graph_builder


def get_graph_executor() -> GraphExecutor:
    """전역 그래프 실행기 인스턴스 반환"""
    global _global_executor
    if _global_executor is None:
        _global_executor = GraphExecutor(get_graph_builder())
    return _global_executor


def reset_global_instances():
    """전역 인스턴스 초기화 (테스트용)"""
    global _global_graph_builder, _global_executor
    _global_graph_builder = None
    _global_executor = None


class TutorWorkflow:
    """튜터 워크플로우 실행을 위한 래퍼 클래스"""
    
    def __init__(self):
        self.executor = get_graph_executor()
    
    def execute(self, state: TutorState) -> TutorState:
        """워크플로우 실행"""
        return self.executor.execute_step(state)
    
    def stream(self, state: TutorState):
        """워크플로우 스트리밍 실행"""
        return self.executor.execute_stream(state)


def create_workflow_graph():
    """워크플로우 그래프 생성 (테스트용)"""
    builder = get_graph_builder()
    return builder.get_compiled_graph()