# routers/post_feedback_router.py
# 피드백 후 라우터 - 사용자 의도 파악하여 QnAResolver 또는 LearningSupervisor로 라우팅

import re
from typing import Dict, Any, Optional
from workflow.state_management import TutorState, StateManager


class PostFeedbackRouter:
    """피드백 후 사용자 의도를 파악하여 적절한 에이전트로 라우팅하는 클래스"""
    
    def __init__(self):
        # 추가 질문 패턴 (QnAResolver로 라우팅)
        self.question_patterns = [
            r'.*\?$',  # 물음표로 끝나는 문장
            r'^(뭐|무엇|어떻게|왜|언제|어디서|누가)',  # 의문사로 시작
            r'(궁금|모르겠|이해.*안|헷갈|확실하지|애매)',  # 궁금증/이해 부족 표현
            r'(설명.*해|알려.*줘|가르쳐|자세히)',  # 설명 요청
            r'(예시|사례|구체적|더.*알려|더.*설명|추가)',  # 추가 정보 요청
            r'(차이.*뭐|비교|구별|관련)',  # 비교/관련 질문 (다른 제외)
            r'(틀렸|잘못|실수|오답)',  # 오답 관련 질문
        ]
        
        # 진행 요청 패턴 (LearningSupervisor로 라우팅)
        self.proceed_patterns = [
            r'(다음|진행|계속|넘어|이어서)',  # 직접적인 진행 요청
            r'(^좋아$|^좋습니다$|^네$|^예$|^알겠습니다$|좋아요|감사)',  # 긍정적 응답
            r'(이해.*했|알겠|됐|완료|끝)',  # 이해 완료 표현
            r'(그만|충분|괜찮|됐어)',  # 만족 표현
            r'(새로운.*문제|다른.*문제|또.*문제)',  # 새 문제 요청
            r'(루프.*완료|루프.*끝|마무리)',  # 루프 완료 의사
        ]
        
        # 재시도/반복 패턴 (현재 단계 유지 또는 특별 처리)
        self.retry_patterns = [
            r'(다시|재시도|한번.*더|또.*해)',  # 재시도 요청
            r'(못.*했|실패|안.*됐)',  # 실패 표현
            r'(힌트|도움|쉽게)',  # 도움 요청
        ]
    
    def execute(self, state: TutorState) -> TutorState:
        """
        사용자 메시지를 분석하여 적절한 다음 에이전트를 결정
        
        Args:
            state: 현재 튜터 상태
            
        Returns:
            업데이트된 튜터 상태
        """
        user_message = state.get('user_message', '').strip()
        
        if not user_message:
            # 메시지가 없으면 기본적으로 진행으로
            return self._route_to_supervisor(state, "다음 단계로 진행하겠습니다.")
        
        # 사용자 의도 분석
        intent = self._analyze_user_intent(user_message)
        
        # 라우팅 결정 및 실행
        if intent == "question":
            return self._route_to_qna(state)
        elif intent == "proceed":
            return self._route_to_supervisor(state)
        elif intent == "retry":
            return self._handle_retry_request(state)
        else:
            # 애매한 경우 추가 확인 요청
            return self._request_clarification(state)
    
    def _analyze_user_intent(self, message: str) -> str:
        """
        사용자 메시지에서 의도를 분석
        
        Args:
            message: 사용자 메시지
            
        Returns:
            'question', 'proceed', 'retry', 또는 'unclear'
        """
        message_lower = message.lower()
        
        # 각 패턴별 점수 계산
        question_score = 0
        proceed_score = 0
        retry_score = 0
        
        # 질문 패턴 확인
        for pattern in self.question_patterns:
            if re.search(pattern, message_lower):
                question_score += 1
        
        # 진행 패턴 확인
        for pattern in self.proceed_patterns:
            if re.search(pattern, message_lower):
                proceed_score += 1
        
        # 재시도 패턴 확인
        for pattern in self.retry_patterns:
            if re.search(pattern, message_lower):
                retry_score += 1
        
        # 점수 기반 결정
        max_score = max(question_score, proceed_score, retry_score)
        
        if max_score == 0:
            return "unclear"
        elif question_score == max_score:
            return "question"
        elif proceed_score == max_score:
            return "proceed"
        else:
            return "retry"
    
    def _route_to_qna(self, state: TutorState) -> TutorState:
        """QnAResolver로 라우팅"""
        # 상태 업데이트
        state['current_stage'] = 'qna'
        state['qa_source_router'] = 'post_feedback'
        state['ui_mode'] = 'chat'
        
        # 대화 기록 추가
        StateManager.add_conversation(
            state,
            'PostFeedbackRouter',
            user_message=state['user_message'],
            system_response="추가 질문을 QnAResolver로 전달합니다."
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(
            state,
            "질문을 분석하여 답변을 준비하고 있습니다...",
            ui_elements={'type': 'loading', 'message': '답변 준비 중'}
        )
        
        return state
    
    def _route_to_supervisor(self, state: TutorState, message: str = None) -> TutorState:
        """LearningSupervisor로 라우팅"""
        # 상태 업데이트
        state['current_stage'] = 'supervision'
        state['ui_mode'] = 'chat'
        
        # 대화 기록 추가
        response_message = message or "학습 진행을 LearningSupervisor로 전달합니다."
        StateManager.add_conversation(
            state,
            'PostFeedbackRouter',
            user_message=state['user_message'],
            system_response=response_message
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(
            state,
            message or "학습 진도를 분석하고 다음 단계를 준비하고 있습니다...",
            ui_elements={'type': 'loading', 'message': '다음 단계 준비 중'}
        )
        
        return state
    
    def _handle_retry_request(self, state: TutorState) -> TutorState:
        """재시도 요청 처리"""
        # 현재 단계에 따라 다른 처리
        current_stage = state.get('current_stage', '')
        
        if current_stage == 'quiz':
            # 퀴즈 단계에서 재시도 - QuizGenerator로 다시 라우팅
            state['current_stage'] = 'quiz'
            state['ui_mode'] = 'quiz'
            
            response_message = "다시 문제를 준비해 드리겠습니다."
            ui_elements = {'type': 'loading', 'message': '새 문제 준비 중'}
            
        else:
            # 기타 경우 - 도움말 제공 후 QnA로 라우팅
            state['current_stage'] = 'qna'
            state['qa_source_router'] = 'post_feedback'
            state['ui_mode'] = 'chat'
            
            response_message = "어떤 부분이 어려우신지 구체적으로 질문해 주세요."
            ui_elements = {'type': 'help', 'message': '도움이 필요한 부분을 알려주세요'}
        
        # 대화 기록 추가
        StateManager.add_conversation(
            state,
            'PostFeedbackRouter',
            user_message=state['user_message'],
            system_response=response_message
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(state, response_message, ui_elements)
        
        return state
    
    def _request_clarification(self, state: TutorState) -> TutorState:
        """사용자 의도가 불분명할 때 명확화 요청"""
        clarification_message = (
            "어떻게 도와드릴까요?\n\n"
            "• 추가로 궁금한 점이 있으시면 자유롭게 질문해 주세요\n"
            "• 이해가 되셨다면 '다음' 또는 '계속'이라고 말씀해 주세요\n"
            "• 다시 시도하고 싶으시면 '다시' 또는 '재시도'라고 말씀해 주세요"
        )
        
        # UI 모드를 채팅으로 유지
        state['ui_mode'] = 'chat'
        
        # 대화 기록 추가
        StateManager.add_conversation(
            state,
            'PostFeedbackRouter',
            user_message=state['user_message'],
            system_response=clarification_message
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(
            state,
            clarification_message,
            ui_elements={
                'type': 'clarification',
                'options': [
                    {'text': '추가 질문', 'action': 'question'},
                    {'text': '다음 단계', 'action': 'proceed'},
                    {'text': '다시 시도', 'action': 'retry'}
                ]
            }
        )
        
        return state
    
    def get_routing_decision(self, state: TutorState) -> Dict[str, Any]:
        """
        라우팅 결정 정보를 반환 (디버깅/로깅용)
        
        Args:
            state: 현재 튜터 상태
            
        Returns:
            라우팅 결정 정보
        """
        user_message = state.get('user_message', '')
        intent = self._analyze_user_intent(user_message)
        
        return {
            'router': 'PostFeedbackRouter',
            'user_message': user_message,
            'detected_intent': intent,
            'previous_stage': state.get('current_stage'),
            'next_stage': self._get_next_stage_for_intent(intent),
            'ui_mode': state.get('ui_mode'),
            'qa_source_router': state.get('qa_source_router')
        }
    
    def _get_next_stage_for_intent(self, intent: str) -> str:
        """의도에 따른 다음 단계 반환"""
        intent_to_stage = {
            'question': 'qna',
            'proceed': 'supervision',
            'retry': 'quiz',  # 기본값, 실제로는 현재 단계에 따라 달라짐
            'unclear': 'clarification'
        }
        return intent_to_stage.get(intent, 'unknown')


def create_post_feedback_router() -> PostFeedbackRouter:
    """PostFeedbackRouter 인스턴스 생성 팩토리 함수"""
    return PostFeedbackRouter()