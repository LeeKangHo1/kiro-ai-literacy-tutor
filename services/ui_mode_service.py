# services/ui_mode_service.py
# UI 모드 관리 서비스 - 하이브리드 UX 패턴 구현

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import json


class UIMode(Enum):
    """UI 모드 열거형"""
    CHAT = "chat"                    # 자유 대화 모드
    QUIZ = "quiz"                    # 문제 풀이 모드 (제한 UI)
    RESTRICTED = "restricted"        # 제한된 상호작용 모드
    ERROR = "error"                  # 오류 상태 모드
    LOADING = "loading"              # 로딩 상태 모드


class InteractionType(Enum):
    """상호작용 유형 열거형"""
    FREE_TEXT = "free_text"          # 자유 텍스트 입력
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식 선택
    BUTTON_CLICK = "button_click"    # 버튼 클릭
    PROMPT_PRACTICE = "prompt_practice"  # 프롬프트 실습
    HINT_REQUEST = "hint_request"    # 힌트 요청


@dataclass
class UIElement:
    """UI 요소 데이터 클래스"""
    element_type: str               # 요소 타입 (button, input, select 등)
    element_id: str                 # 요소 고유 ID
    label: str                      # 표시 라벨
    value: Any = None              # 기본값
    options: Optional[List[Dict]] = None  # 선택 옵션 (select용)
    placeholder: Optional[str] = None     # 플레이스홀더
    disabled: bool = False         # 비활성화 여부
    required: bool = False         # 필수 입력 여부
    validation: Optional[Dict] = None     # 검증 규칙
    style: Optional[Dict] = None   # 스타일 정보
    events: Optional[List[str]] = None    # 이벤트 리스트


@dataclass
class UIState:
    """UI 상태 데이터 클래스"""
    mode: UIMode                    # 현재 UI 모드
    interaction_type: InteractionType  # 상호작용 유형
    elements: List[UIElement]       # UI 요소 리스트
    layout: str                     # 레이아웃 타입
    title: Optional[str] = None     # 화면 제목
    description: Optional[str] = None  # 설명 텍스트
    progress: Optional[Dict] = None    # 진행률 정보
    metadata: Optional[Dict] = None    # 추가 메타데이터


class UIModeManager:
    """UI 모드 관리자 클래스"""
    
    def __init__(self):
        self.current_mode = UIMode.CHAT
        self.mode_history = []
        self.element_templates = self._initialize_element_templates()
    
    def _initialize_element_templates(self) -> Dict[str, Dict]:
        """UI 요소 템플릿 초기화"""
        return {
            # 자유 대화 모드 템플릿
            "chat_input": {
                "element_type": "textarea",
                "label": "메시지를 입력하세요",
                "placeholder": "궁금한 점을 자유롭게 질문해보세요...",
                "required": True,
                "validation": {"max_length": 1000}
            },
            
            # 객관식 문제 템플릿
            "multiple_choice": {
                "element_type": "radio_group",
                "label": "정답을 선택하세요",
                "required": True,
                "validation": {"required": True}
            },
            
            # 프롬프트 실습 템플릿
            "prompt_practice": {
                "element_type": "code_editor",
                "label": "프롬프트를 작성하세요",
                "placeholder": "여기에 프롬프트를 작성해주세요...",
                "required": True,
                "validation": {"min_length": 10}
            },
            
            # 힌트 요청 버튼 템플릿
            "hint_button": {
                "element_type": "button",
                "label": "힌트 보기",
                "style": {"variant": "secondary"},
                "events": ["click"]
            },
            
            # 제출 버튼 템플릿
            "submit_button": {
                "element_type": "button",
                "label": "제출",
                "style": {"variant": "primary"},
                "events": ["click"]
            },
            
            # 다음 단계 버튼 템플릿
            "next_button": {
                "element_type": "button",
                "label": "다음 단계",
                "style": {"variant": "primary"},
                "events": ["click"]
            },
            
            # 진행률 표시 템플릿
            "progress_bar": {
                "element_type": "progress",
                "label": "학습 진행률"
            }
        }
    
    def switch_mode(self, new_mode: UIMode, context: Optional[Dict] = None) -> UIState:
        """UI 모드 전환"""
        # 이전 모드 기록
        self.mode_history.append(self.current_mode)
        
        # 모드 전환
        self.current_mode = new_mode
        
        # 모드별 UI 상태 생성
        ui_state = self._create_ui_state_for_mode(new_mode, context)
        
        return ui_state
    
    def _create_ui_state_for_mode(self, mode: UIMode, context: Optional[Dict] = None) -> UIState:
        """모드별 UI 상태 생성"""
        context = context or {}
        
        if mode == UIMode.CHAT:
            return self._create_chat_ui_state(context)
        elif mode == UIMode.QUIZ:
            return self._create_quiz_ui_state(context)
        elif mode == UIMode.RESTRICTED:
            return self._create_restricted_ui_state(context)
        elif mode == UIMode.ERROR:
            return self._create_error_ui_state(context)
        elif mode == UIMode.LOADING:
            return self._create_loading_ui_state(context)
        else:
            return self._create_default_ui_state()
    
    def _create_chat_ui_state(self, context: Dict) -> UIState:
        """자유 대화 모드 UI 상태 생성"""
        elements = []
        
        # 메시지 입력 영역
        chat_input = self._create_element_from_template(
            "chat_input",
            element_id="user_message_input"
        )
        elements.append(chat_input)
        
        # 제출 버튼
        submit_button = self._create_element_from_template(
            "submit_button",
            element_id="submit_message",
            label="전송"
        )
        elements.append(submit_button)
        
        # 진행률 표시 (선택적)
        if context.get("show_progress"):
            progress_bar = self._create_element_from_template(
                "progress_bar",
                element_id="learning_progress",
                value=context.get("progress_value", 0)
            )
            elements.append(progress_bar)
        
        return UIState(
            mode=UIMode.CHAT,
            interaction_type=InteractionType.FREE_TEXT,
            elements=elements,
            layout="chat_layout",
            title=context.get("title", "AI 학습 튜터"),
            description=context.get("description", "자유롭게 질문하고 대화해보세요.")
        )
    
    def _create_quiz_ui_state(self, context: Dict) -> UIState:
        """문제 풀이 모드 UI 상태 생성"""
        elements = []
        quiz_type = context.get("quiz_type", "multiple_choice")
        
        if quiz_type == "multiple_choice":
            # 객관식 문제
            quiz_element = self._create_element_from_template(
                "multiple_choice",
                element_id="quiz_answer",
                options=context.get("options", [])
            )
            elements.append(quiz_element)
            
            interaction_type = InteractionType.MULTIPLE_CHOICE
            
        elif quiz_type == "prompt_practice":
            # 프롬프트 실습
            prompt_element = self._create_element_from_template(
                "prompt_practice",
                element_id="prompt_input"
            )
            elements.append(prompt_element)
            
            interaction_type = InteractionType.PROMPT_PRACTICE
        
        # 힌트 버튼 (선택적)
        if context.get("hint_available"):
            hint_button = self._create_element_from_template(
                "hint_button",
                element_id="request_hint"
            )
            elements.append(hint_button)
        
        # 제출 버튼
        submit_button = self._create_element_from_template(
            "submit_button",
            element_id="submit_answer"
        )
        elements.append(submit_button)
        
        return UIState(
            mode=UIMode.QUIZ,
            interaction_type=interaction_type,
            elements=elements,
            layout="quiz_layout",
            title=context.get("title", "문제 풀이"),
            description=context.get("question", "문제를 풀어보세요."),
            metadata={"quiz_type": quiz_type}
        )
    
    def _create_restricted_ui_state(self, context: Dict) -> UIState:
        """제한된 상호작용 모드 UI 상태 생성"""
        elements = []
        
        # 제한된 버튼들만 제공
        available_actions = context.get("available_actions", ["next"])
        
        for action in available_actions:
            if action == "next":
                button = self._create_element_from_template(
                    "next_button",
                    element_id="next_action"
                )
                elements.append(button)
            elif action == "hint":
                button = self._create_element_from_template(
                    "hint_button",
                    element_id="request_hint"
                )
                elements.append(button)
        
        return UIState(
            mode=UIMode.RESTRICTED,
            interaction_type=InteractionType.BUTTON_CLICK,
            elements=elements,
            layout="restricted_layout",
            title=context.get("title", "학습 진행"),
            description=context.get("description", "다음 단계로 진행하세요.")
        )
    
    def _create_error_ui_state(self, context: Dict) -> UIState:
        """오류 상태 모드 UI 상태 생성"""
        elements = []
        
        # 재시도 버튼
        retry_button = UIElement(
            element_type="button",
            element_id="retry_action",
            label="다시 시도",
            style={"variant": "primary"},
            events=["click"]
        )
        elements.append(retry_button)
        
        return UIState(
            mode=UIMode.ERROR,
            interaction_type=InteractionType.BUTTON_CLICK,
            elements=elements,
            layout="error_layout",
            title="오류 발생",
            description=context.get("error_message", "오류가 발생했습니다. 다시 시도해주세요.")
        )
    
    def _create_loading_ui_state(self, context: Dict) -> UIState:
        """로딩 상태 모드 UI 상태 생성"""
        elements = []
        
        # 로딩 스피너
        loading_element = UIElement(
            element_type="spinner",
            element_id="loading_spinner",
            label="처리 중..."
        )
        elements.append(loading_element)
        
        return UIState(
            mode=UIMode.LOADING,
            interaction_type=InteractionType.BUTTON_CLICK,  # 상호작용 불가
            elements=elements,
            layout="loading_layout",
            title="처리 중",
            description=context.get("loading_message", "요청을 처리하고 있습니다...")
        )
    
    def _create_default_ui_state(self) -> UIState:
        """기본 UI 상태 생성"""
        return self._create_chat_ui_state({})
    
    def _create_element_from_template(self, template_name: str, element_id: str, **overrides) -> UIElement:
        """템플릿으로부터 UI 요소 생성"""
        template = self.element_templates.get(template_name, {})
        
        # 템플릿 속성과 오버라이드 병합
        element_data = {**template, **overrides}
        element_data["element_id"] = element_id
        
        return UIElement(**element_data)
    
    def get_current_mode(self) -> UIMode:
        """현재 UI 모드 반환"""
        return self.current_mode
    
    def get_previous_mode(self) -> Optional[UIMode]:
        """이전 UI 모드 반환"""
        return self.mode_history[-1] if self.mode_history else None
    
    def revert_to_previous_mode(self, context: Optional[Dict] = None) -> UIState:
        """이전 모드로 되돌리기"""
        if self.mode_history:
            previous_mode = self.mode_history.pop()
            self.current_mode = previous_mode
            return self._create_ui_state_for_mode(previous_mode, context)
        else:
            return self._create_chat_ui_state(context or {})


class UIStateSerializer:
    """UI 상태 직렬화/역직렬화 클래스"""
    
    @staticmethod
    def serialize_ui_state(ui_state: UIState) -> Dict[str, Any]:
        """UI 상태를 딕셔너리로 직렬화"""
        return {
            "mode": ui_state.mode.value,
            "interaction_type": ui_state.interaction_type.value,
            "elements": [UIStateSerializer._serialize_element(elem) for elem in ui_state.elements],
            "layout": ui_state.layout,
            "title": ui_state.title,
            "description": ui_state.description,
            "progress": ui_state.progress,
            "metadata": ui_state.metadata
        }
    
    @staticmethod
    def _serialize_element(element: UIElement) -> Dict[str, Any]:
        """UI 요소를 딕셔너리로 직렬화"""
        return {
            "element_type": element.element_type,
            "element_id": element.element_id,
            "label": element.label,
            "value": element.value,
            "options": element.options,
            "placeholder": element.placeholder,
            "disabled": element.disabled,
            "required": element.required,
            "validation": element.validation,
            "style": element.style,
            "events": element.events
        }
    
    @staticmethod
    def deserialize_ui_state(data: Dict[str, Any]) -> UIState:
        """딕셔너리로부터 UI 상태 역직렬화"""
        elements = [UIStateSerializer._deserialize_element(elem_data) 
                   for elem_data in data.get("elements", [])]
        
        return UIState(
            mode=UIMode(data["mode"]),
            interaction_type=InteractionType(data["interaction_type"]),
            elements=elements,
            layout=data["layout"],
            title=data.get("title"),
            description=data.get("description"),
            progress=data.get("progress"),
            metadata=data.get("metadata")
        )
    
    @staticmethod
    def _deserialize_element(data: Dict[str, Any]) -> UIElement:
        """딕셔너리로부터 UI 요소 역직렬화"""
        return UIElement(
            element_type=data["element_type"],
            element_id=data["element_id"],
            label=data["label"],
            value=data.get("value"),
            options=data.get("options"),
            placeholder=data.get("placeholder"),
            disabled=data.get("disabled", False),
            required=data.get("required", False),
            validation=data.get("validation"),
            style=data.get("style"),
            events=data.get("events")
        )


# 전역 UI 모드 관리자 인스턴스
_global_ui_manager = None


def get_ui_mode_manager() -> UIModeManager:
    """전역 UI 모드 관리자 인스턴스 반환"""
    global _global_ui_manager
    if _global_ui_manager is None:
        _global_ui_manager = UIModeManager()
    return _global_ui_manager


def reset_ui_manager():
    """전역 UI 관리자 초기화 (테스트용)"""
    global _global_ui_manager
    _global_ui_manager = None