# workflow/node_definitions.py
# 각 에이전트 노드 정의 모듈

from typing import Dict, Any
from .state_management import TutorState, StateManager


class NodeDefinitions:
    """LangGraph 워크플로우의 각 노드를 정의하는 클래스"""
    
    @staticmethod
    def learning_supervisor_node(state: TutorState) -> TutorState:
        """LearningSupervisor 에이전트 노드"""
        try:
            # 에이전트 임포트 (순환 임포트 방지를 위해 함수 내부에서 임포트)
            from agents.supervisor import LearningSupervisor
            
            supervisor = LearningSupervisor()
            result_state = supervisor.execute(state)
            
            # 대화 기록 추가
            StateManager.add_conversation(
                result_state,
                agent_name="LearningSupervisor",
                user_message=state.get('user_message', ''),
                system_response=result_state.get('system_message', ''),
                ui_elements=result_state.get('ui_elements')
            )
            
            return result_state
            
        except Exception as e:
            # 오류 처리
            error_message = f"LearningSupervisor 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def theory_educator_node(state: TutorState) -> TutorState:
        """TheoryEducator 에이전트 노드"""
        try:
            from agents.educator import TheoryEducator
            
            educator = TheoryEducator()
            result_state = educator.execute(state)
            
            # 대화 기록 추가
            StateManager.add_conversation(
                result_state,
                agent_name="TheoryEducator",
                user_message=state.get('user_message', ''),
                system_response=result_state.get('system_message', ''),
                ui_elements=result_state.get('ui_elements')
            )
            
            return result_state
            
        except Exception as e:
            error_message = f"TheoryEducator 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def post_theory_router_node(state: TutorState) -> TutorState:
        """PostTheoryRouter 노드"""
        try:
            from routers.post_theory_router import PostTheoryRouter
            
            router = PostTheoryRouter()
            result_state = router.execute(state)
            
            # 라우터는 대화 기록에 추가하지 않음 (내부 처리)
            return result_state
            
        except Exception as e:
            error_message = f"PostTheoryRouter 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def quiz_generator_node(state: TutorState) -> TutorState:
        """QuizGenerator 에이전트 노드"""
        try:
            from agents.quiz import QuizGenerator
            
            quiz_gen = QuizGenerator()
            result_state = quiz_gen.execute(state)
            
            # 대화 기록 추가
            StateManager.add_conversation(
                result_state,
                agent_name="QuizGenerator",
                user_message=state.get('user_message', ''),
                system_response=result_state.get('system_message', ''),
                ui_elements=result_state.get('ui_elements')
            )
            
            return result_state
            
        except Exception as e:
            error_message = f"QuizGenerator 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def evaluation_feedback_node(state: TutorState) -> TutorState:
        """EvaluationFeedbackAgent 에이전트 노드"""
        try:
            from agents.evaluator import EvaluationFeedbackAgent
            
            evaluator = EvaluationFeedbackAgent()
            result_state = evaluator.execute(state)
            
            # 대화 기록 추가
            StateManager.add_conversation(
                result_state,
                agent_name="EvaluationFeedbackAgent",
                user_message=state.get('user_message', ''),
                system_response=result_state.get('system_message', ''),
                ui_elements=result_state.get('ui_elements')
            )
            
            return result_state
            
        except Exception as e:
            error_message = f"EvaluationFeedbackAgent 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def post_feedback_router_node(state: TutorState) -> TutorState:
        """PostFeedbackRouter 노드"""
        try:
            from routers.post_feedback_router import PostFeedbackRouter
            
            router = PostFeedbackRouter()
            result_state = router.execute(state)
            
            # 라우터는 대화 기록에 추가하지 않음 (내부 처리)
            return result_state
            
        except Exception as e:
            error_message = f"PostFeedbackRouter 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def qna_resolver_node(state: TutorState) -> TutorState:
        """QnAResolver 에이전트 노드"""
        try:
            from agents.qna import QnAResolver
            
            qna_resolver = QnAResolver()
            result_state = qna_resolver.execute(state)
            
            # 대화 기록 추가
            StateManager.add_conversation(
                result_state,
                agent_name="QnAResolver",
                user_message=state.get('user_message', ''),
                system_response=result_state.get('system_message', ''),
                ui_elements=result_state.get('ui_elements')
            )
            
            return result_state
            
        except Exception as e:
            error_message = f"QnAResolver 실행 중 오류가 발생했습니다: {str(e)}"
            state['system_message'] = error_message
            state['ui_mode'] = 'error'
            return state
    
    @staticmethod
    def start_node(state: TutorState) -> TutorState:
        """워크플로우 시작 노드"""
        # 새로운 루프 시작
        state = StateManager.start_new_loop(state)
        
        # 시작 메시지 설정
        state['system_message'] = "학습을 시작합니다."
        state['current_stage'] = "theory"
        
        return state
    
    @staticmethod
    def end_node(state: TutorState) -> TutorState:
        """워크플로우 종료 노드"""
        # 현재 루프 완료 처리
        if state['current_loop_conversations']:
            loop_summary = StateManager._create_loop_summary(state)
            state['recent_loops_summary'].append(loop_summary)
            
            # 최대 5개 루프 요약만 유지
            if len(state['recent_loops_summary']) > 5:
                state['recent_loops_summary'] = state['recent_loops_summary'][-5:]
        
        # 종료 메시지 설정
        state['system_message'] = "학습 루프가 완료되었습니다."
        state['current_stage'] = "completed"
        
        return state


class NodeRegistry:
    """노드 등록 및 관리를 위한 레지스트리 클래스"""
    
    # 사용 가능한 모든 노드 정의
    NODES = {
        'start': NodeDefinitions.start_node,
        'learning_supervisor': NodeDefinitions.learning_supervisor_node,
        'theory_educator': NodeDefinitions.theory_educator_node,
        'post_theory_router': NodeDefinitions.post_theory_router_node,
        'quiz_generator': NodeDefinitions.quiz_generator_node,
        'evaluation_feedback': NodeDefinitions.evaluation_feedback_node,
        'post_feedback_router': NodeDefinitions.post_feedback_router_node,
        'qna_resolver': NodeDefinitions.qna_resolver_node,
        'end': NodeDefinitions.end_node
    }
    
    @classmethod
    def get_node(cls, node_name: str):
        """노드 이름으로 노드 함수 반환"""
        return cls.NODES.get(node_name)
    
    @classmethod
    def get_all_nodes(cls) -> Dict[str, Any]:
        """모든 노드 반환"""
        return cls.NODES.copy()
    
    @classmethod
    def validate_node_name(cls, node_name: str) -> bool:
        """노드 이름 유효성 검증"""
        return node_name in cls.NODES