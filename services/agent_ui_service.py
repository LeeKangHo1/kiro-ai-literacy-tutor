# services/agent_ui_service.py
# 에이전트별 UI 요소 생성 및 관리 서비스

from typing import Dict, Any, Optional, List
from .ui_mode_service import UIModeManager, UIMode, UIState, InteractionType, UIElement
from workflow.state_management import TutorState


class AgentUIGenerator:
    """에이전트별 UI 요소 생성기"""
    
    def __init__(self, ui_manager: UIModeManager):
        self.ui_manager = ui_manager
        self.agent_ui_configs = self._initialize_agent_ui_configs()
    
    def _initialize_agent_ui_configs(self) -> Dict[str, Dict]:
        """에이전트별 UI 설정 초기화"""
        return {
            "learning_supervisor": {
                "default_mode": UIMode.RESTRICTED,
                "available_actions": ["next", "review"],
                "title": "학습 진행 관리",
                "layout": "supervisor_layout"
            },
            
            "theory_educator": {
                "default_mode": UIMode.CHAT,
                "show_progress": True,
                "title": "개념 학습",
                "layout": "theory_layout"
            },
            
            "post_theory_router": {
                "default_mode": UIMode.RESTRICTED,
                "available_actions": ["question", "quiz"],
                "title": "다음 단계 선택",
                "layout": "router_layout"
            },
            
            "quiz_generator": {
                "default_mode": UIMode.QUIZ,
                "hint_available": True,
                "title": "문제 풀이",
                "layout": "quiz_layout"
            },
            
            "evaluation_feedback": {
                "default_mode": UIMode.RESTRICTED,
                "available_actions": ["continue", "retry"],
                "title": "평가 결과",
                "layout": "feedback_layout"
            },
            
            "post_feedback_router": {
                "default_mode": UIMode.RESTRICTED,
                "available_actions": ["question", "next"],
                "title": "다음 행동 선택",
                "layout": "router_layout"
            },
            
            "qna_resolver": {
                "default_mode": UIMode.CHAT,
                "show_context": True,
                "title": "질문 답변",
                "layout": "qna_layout"
            }
        }
    
    def generate_ui_for_agent(self, agent_name: str, state: TutorState, 
                            context: Optional[Dict] = None) -> UIState:
        """특정 에이전트를 위한 UI 생성"""
        context = context or {}
        agent_config = self.agent_ui_configs.get(agent_name, {})
        
        # 에이전트별 특화 컨텍스트 생성
        agent_context = self._create_agent_context(agent_name, state, context)
        
        # 기본 설정과 컨텍스트 병합
        merged_context = {**agent_config, **agent_context}
        
        # UI 모드 결정
        ui_mode = self._determine_ui_mode(agent_name, state, merged_context)
        
        # UI 상태 생성
        ui_state = self.ui_manager.switch_mode(ui_mode, merged_context)
        
        # 에이전트별 추가 커스터마이징
        ui_state = self._customize_ui_for_agent(agent_name, ui_state, state, merged_context)
        
        return ui_state
    
    def _create_agent_context(self, agent_name: str, state: TutorState, 
                            base_context: Dict) -> Dict:
        """에이전트별 특화 컨텍스트 생성"""
        context = base_context.copy()
        
        if agent_name == "learning_supervisor":
            context.update(self._create_supervisor_context(state))
        elif agent_name == "theory_educator":
            context.update(self._create_theory_context(state))
        elif agent_name == "quiz_generator":
            context.update(self._create_quiz_context(state))
        elif agent_name == "evaluation_feedback":
            context.update(self._create_feedback_context(state))
        elif agent_name == "qna_resolver":
            context.update(self._create_qna_context(state))
        elif agent_name in ["post_theory_router", "post_feedback_router"]:
            context.update(self._create_router_context(agent_name, state))
        
        return context
    
    def _create_supervisor_context(self, state: TutorState) -> Dict:
        """LearningSupervisor용 컨텍스트 생성"""
        return {
            "description": f"챕터 {state['current_chapter']} 학습을 진행하고 있습니다.",
            "progress_value": self._calculate_chapter_progress(state),
            "show_progress": True,
            "available_actions": ["continue", "review_progress"]
        }
    
    def _create_theory_context(self, state: TutorState) -> Dict:
        """TheoryEducator용 컨텍스트 생성"""
        return {
            "description": f"{state['user_type']} 사용자를 위한 개념 설명입니다.",
            "show_progress": True,
            "progress_value": self._calculate_chapter_progress(state),
            "user_level_info": {
                "type": state['user_type'],
                "level": state['user_level']
            }
        }
    
    def _create_quiz_context(self, state: TutorState) -> Dict:
        """QuizGenerator용 컨텍스트 생성"""
        # 현재 대화에서 퀴즈 정보 추출
        quiz_info = self._extract_quiz_info_from_conversations(state)
        
        return {
            "quiz_type": quiz_info.get("type", "multiple_choice"),
            "question": quiz_info.get("question", "문제를 생성하고 있습니다..."),
            "options": quiz_info.get("options", []),
            "hint_available": True,
            "difficulty": state['user_level']
        }
    
    def _create_feedback_context(self, state: TutorState) -> Dict:
        """EvaluationFeedback용 컨텍스트 생성"""
        # 최근 답변 정보 추출
        feedback_info = self._extract_feedback_info_from_conversations(state)
        
        return {
            "description": feedback_info.get("feedback", "답변을 평가하고 있습니다..."),
            "score": feedback_info.get("score"),
            "is_correct": feedback_info.get("is_correct"),
            "available_actions": ["continue", "retry"] if not feedback_info.get("is_correct") else ["continue"]
        }
    
    def _create_qna_context(self, state: TutorState) -> Dict:
        """QnAResolver용 컨텍스트 생성"""
        return {
            "description": "궁금한 점을 자유롭게 질문해보세요.",
            "show_context": True,
            "context_info": {
                "chapter": state['current_chapter'],
                "stage": state['current_stage'],
                "recent_topics": self._get_recent_topics(state)
            }
        }
    
    def _create_router_context(self, router_name: str, state: TutorState) -> Dict:
        """Router용 컨텍스트 생성"""
        if router_name == "post_theory_router":
            return {
                "description": "개념 설명이 완료되었습니다. 다음 단계를 선택해주세요.",
                "available_actions": ["ask_question", "take_quiz"]
            }
        elif router_name == "post_feedback_router":
            return {
                "description": "피드백을 확인했습니다. 다음 행동을 선택해주세요.",
                "available_actions": ["ask_question", "continue_learning"]
            }
        
        return {}
    
    def _determine_ui_mode(self, agent_name: str, state: TutorState, context: Dict) -> UIMode:
        """에이전트와 상황에 따른 UI 모드 결정"""
        # 오류 상태 확인
        if state.get('system_message', '').startswith('오류') or 'error' in context:
            return UIMode.ERROR
        
        # 에이전트별 기본 모드
        agent_config = self.agent_ui_configs.get(agent_name, {})
        default_mode = agent_config.get("default_mode", UIMode.CHAT)
        
        # 특수 상황 처리
        if context.get("loading", False):
            return UIMode.LOADING
        
        # 퀴즈 타입별 모드 조정
        if agent_name == "quiz_generator":
            quiz_type = context.get("quiz_type", "multiple_choice")
            if quiz_type in ["multiple_choice", "prompt_practice"]:
                return UIMode.QUIZ
        
        return default_mode
    
    def _customize_ui_for_agent(self, agent_name: str, ui_state: UIState, 
                              state: TutorState, context: Dict) -> UIState:
        """에이전트별 UI 추가 커스터마이징"""
        
        if agent_name == "quiz_generator":
            ui_state = self._customize_quiz_ui(ui_state, context)
        elif agent_name == "evaluation_feedback":
            ui_state = self._customize_feedback_ui(ui_state, context)
        elif agent_name in ["post_theory_router", "post_feedback_router"]:
            ui_state = self._customize_router_ui(ui_state, agent_name, context)
        elif agent_name == "qna_resolver":
            ui_state = self._customize_qna_ui(ui_state, context)
        
        return ui_state
    
    def _customize_quiz_ui(self, ui_state: UIState, context: Dict) -> UIState:
        """퀴즈 UI 커스터마이징"""
        quiz_type = context.get("quiz_type", "multiple_choice")
        
        if quiz_type == "multiple_choice" and context.get("options"):
            # 객관식 옵션 업데이트
            for element in ui_state.elements:
                if element.element_id == "quiz_answer":
                    element.options = [
                        {"value": i, "label": option} 
                        for i, option in enumerate(context["options"])
                    ]
        
        elif quiz_type == "prompt_practice":
            # 프롬프트 실습 UI 추가 설정
            for element in ui_state.elements:
                if element.element_id == "prompt_input":
                    element.placeholder = "ChatGPT에게 보낼 프롬프트를 작성해주세요..."
                    element.validation = {"min_length": 10, "max_length": 500}
        
        return ui_state
    
    def _customize_feedback_ui(self, ui_state: UIState, context: Dict) -> UIState:
        """피드백 UI 커스터마이징"""
        is_correct = context.get("is_correct", False)
        score = context.get("score")
        
        # 점수 표시 요소 추가
        if score is not None:
            score_element = UIElement(
                element_type="score_display",
                element_id="answer_score",
                label=f"점수: {score}점",
                value=score,
                style={"color": "green" if is_correct else "orange"}
            )
            ui_state.elements.insert(0, score_element)
        
        # 정답 여부에 따른 버튼 조정
        if not is_correct:
            # 재시도 버튼 추가
            retry_button = UIElement(
                element_type="button",
                element_id="retry_quiz",
                label="다시 풀기",
                style={"variant": "secondary"},
                events=["click"]
            )
            ui_state.elements.append(retry_button)
        
        return ui_state
    
    def _customize_router_ui(self, ui_state: UIState, router_name: str, context: Dict) -> UIState:
        """라우터 UI 커스터마이징"""
        available_actions = context.get("available_actions", [])
        
        # 기존 요소 제거하고 새로운 액션 버튼들 추가
        ui_state.elements = []
        
        for action in available_actions:
            if action == "ask_question":
                button = UIElement(
                    element_type="button",
                    element_id="choose_question",
                    label="질문하기",
                    style={"variant": "outline"},
                    events=["click"]
                )
            elif action == "take_quiz":
                button = UIElement(
                    element_type="button",
                    element_id="choose_quiz",
                    label="문제 풀기",
                    style={"variant": "primary"},
                    events=["click"]
                )
            elif action == "continue_learning":
                button = UIElement(
                    element_type="button",
                    element_id="continue_learning",
                    label="학습 계속하기",
                    style={"variant": "primary"},
                    events=["click"]
                )
            else:
                button = UIElement(
                    element_type="button",
                    element_id=f"action_{action}",
                    label=action.replace("_", " ").title(),
                    style={"variant": "secondary"},
                    events=["click"]
                )
            
            ui_state.elements.append(button)
        
        return ui_state
    
    def _customize_qna_ui(self, ui_state: UIState, context: Dict) -> UIState:
        """QnA UI 커스터마이징"""
        if context.get("show_context"):
            # 컨텍스트 정보 표시 요소 추가
            context_info = context.get("context_info", {})
            context_element = UIElement(
                element_type="info_panel",
                element_id="learning_context",
                label="현재 학습 상황",
                value=context_info,
                style={"variant": "info"}
            )
            ui_state.elements.insert(0, context_element)
        
        return ui_state
    
    # 헬퍼 메서드들
    def _calculate_chapter_progress(self, state: TutorState) -> int:
        """챕터 진행률 계산"""
        # 현재 루프 수와 대화 수를 기반으로 진행률 추정
        loop_count = len(state['recent_loops_summary'])
        conversation_count = len(state['current_loop_conversations'])
        
        # 간단한 진행률 계산 (실제로는 더 정교한 로직 필요)
        progress = min(100, (loop_count * 20) + (conversation_count * 5))
        return progress
    
    def _extract_quiz_info_from_conversations(self, state: TutorState) -> Dict:
        """대화에서 퀴즈 정보 추출"""
        conversations = state['current_loop_conversations']
        
        for conv in reversed(conversations):  # 최신 대화부터 검색
            if conv['agent_name'] == 'quiz_generator' and conv.get('ui_elements'):
                ui_elements = conv['ui_elements']
                if isinstance(ui_elements, dict):
                    return ui_elements.get('quiz_info', {})
        
        return {}
    
    def _extract_feedback_info_from_conversations(self, state: TutorState) -> Dict:
        """대화에서 피드백 정보 추출"""
        conversations = state['current_loop_conversations']
        
        for conv in reversed(conversations):  # 최신 대화부터 검색
            if conv['agent_name'] == 'evaluation_feedback' and conv.get('ui_elements'):
                ui_elements = conv['ui_elements']
                if isinstance(ui_elements, dict):
                    return ui_elements.get('feedback_info', {})
        
        return {}
    
    def _get_recent_topics(self, state: TutorState) -> List[str]:
        """최근 대화 주제 추출"""
        topics = []
        conversations = state['current_loop_conversations']
        
        for conv in conversations[-5:]:  # 최근 5개 대화
            if conv.get('user_message'):
                # 간단한 주제 추출 (실제로는 NLP 기법 사용 가능)
                message = conv['user_message'][:50]
                if message not in topics:
                    topics.append(message)
        
        return topics


class UIStateTransitionManager:
    """UI 상태 전환 관리자"""
    
    def __init__(self, ui_generator: AgentUIGenerator):
        self.ui_generator = ui_generator
        self.transition_rules = self._initialize_transition_rules()
    
    def _initialize_transition_rules(self) -> Dict[str, Dict]:
        """상태 전환 규칙 초기화"""
        return {
            "user_input_received": {
                "from_modes": [UIMode.CHAT, UIMode.QUIZ],
                "to_mode": UIMode.LOADING,
                "duration": 2  # 초
            },
            
            "agent_response_ready": {
                "from_modes": [UIMode.LOADING],
                "to_mode": "agent_specific",  # 에이전트에 따라 결정
                "duration": 0
            },
            
            "error_occurred": {
                "from_modes": "any",
                "to_mode": UIMode.ERROR,
                "duration": 0
            },
            
            "quiz_submitted": {
                "from_modes": [UIMode.QUIZ],
                "to_mode": UIMode.LOADING,
                "duration": 1
            }
        }
    
    def handle_transition(self, event: str, current_agent: str, 
                         state: TutorState, context: Optional[Dict] = None) -> UIState:
        """이벤트에 따른 UI 상태 전환 처리"""
        context = context or {}
        
        if event == "user_input_received":
            return self._handle_input_received(current_agent, state, context)
        elif event == "agent_response_ready":
            return self._handle_response_ready(current_agent, state, context)
        elif event == "error_occurred":
            return self._handle_error_occurred(current_agent, state, context)
        elif event == "quiz_submitted":
            return self._handle_quiz_submitted(current_agent, state, context)
        else:
            # 기본 처리: 현재 에이전트에 맞는 UI 생성
            return self.ui_generator.generate_ui_for_agent(current_agent, state, context)
    
    def _handle_input_received(self, agent: str, state: TutorState, context: Dict) -> UIState:
        """사용자 입력 수신 시 처리"""
        loading_context = {
            **context,
            "loading": True,
            "loading_message": "입력을 처리하고 있습니다..."
        }
        return self.ui_generator.ui_manager.switch_mode(UIMode.LOADING, loading_context)
    
    def _handle_response_ready(self, agent: str, state: TutorState, context: Dict) -> UIState:
        """에이전트 응답 준비 완료 시 처리"""
        return self.ui_generator.generate_ui_for_agent(agent, state, context)
    
    def _handle_error_occurred(self, agent: str, state: TutorState, context: Dict) -> UIState:
        """오류 발생 시 처리"""
        error_context = {
            **context,
            "error_message": state.get('system_message', '알 수 없는 오류가 발생했습니다.')
        }
        return self.ui_generator.ui_manager.switch_mode(UIMode.ERROR, error_context)
    
    def _handle_quiz_submitted(self, agent: str, state: TutorState, context: Dict) -> UIState:
        """퀴즈 제출 시 처리"""
        loading_context = {
            **context,
            "loading": True,
            "loading_message": "답변을 평가하고 있습니다..."
        }
        return self.ui_generator.ui_manager.switch_mode(UIMode.LOADING, loading_context)


# 전역 인스턴스들
_global_ui_generator = None
_global_transition_manager = None


def get_agent_ui_generator() -> AgentUIGenerator:
    """전역 에이전트 UI 생성기 인스턴스 반환"""
    global _global_ui_generator
    if _global_ui_generator is None:
        from .ui_mode_service import get_ui_mode_manager
        _global_ui_generator = AgentUIGenerator(get_ui_mode_manager())
    return _global_ui_generator


def get_ui_transition_manager() -> UIStateTransitionManager:
    """전역 UI 전환 관리자 인스턴스 반환"""
    global _global_transition_manager
    if _global_transition_manager is None:
        _global_transition_manager = UIStateTransitionManager(get_agent_ui_generator())
    return _global_transition_manager


def reset_agent_ui_services():
    """전역 인스턴스 초기화 (테스트용)"""
    global _global_ui_generator, _global_transition_manager
    _global_ui_generator = None
    _global_transition_manager = None