# routers/post_theory_router.py
# 개념 설명 후 라우터 - 사용자 의도 파악하여 QnAResolver 또는 QuizGenerator로 라우팅

import re
from typing import Dict, Any, Optional
from workflow.state_management import TutorState, StateManager


class PostTheoryRouter:
    """개념 설명 후 사용자 의도를 파악하여 적절한 에이전트로 라우팅하는 클래스"""
    
    def __init__(self):
        # 질문 패턴 (QnAResolver로 라우팅)
        self.question_patterns = [
            r'.*\?',  # 물음표가 포함된 문장
            r'(뭐|무엇|어떻게|왜|언제|어디서|누가)',  # 의문사 포함
            r'(궁금|모르겠|이해.*안|헷갈|확실하지)',  # 궁금증 표현
            r'(설명.*해|알려.*줘|가르쳐|도움)',  # 설명 요청
            r'(예시|사례|구체적|자세히)',  # 구체적 설명 요청
            r'(차이|다른|비교|구별)',  # 비교/구별 요청
        ]
        
        # 문제 요청 패턴 (QuizGenerator로 라우팅)
        self.quiz_patterns = [
            r'(문제|퀴즈|테스트|시험)',  # 직접적인 문제 요청
            r'(풀어|연습|실습|해보)',  # 실습 요청
            r'(확인|점검|체크)',  # 이해도 확인 요청
            r'(다음|진행|계속|넘어)',  # 진행 요청
            r'(준비.*됐|이해.*했|알겠)',  # 이해 완료 표현
        ]
        
        # 진행 요청 패턴 (기본적으로 QuizGenerator로)
        self.proceed_patterns = [
            r'(^좋아$|^좋습니다$|^네$|^예$|^알겠습니다$|좋아요)',  # 긍정적 응답
            r'(계속|다음|진행|넘어가)',  # 진행 요청
            r'(문제.*주세요|퀴즈.*주세요)',  # 문제 직접 요청
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
            # 메시지가 없으면 기본적으로 문제 출제로
            return self._route_to_quiz(state, "문제를 풀어보시겠어요?")
        
        # 사용자 의도 분석
        intent = self._analyze_user_intent(user_message)
        
        # 라우팅 결정 및 실행
        if intent == "question":
            return self._route_to_qna(state)
        elif intent == "quiz":
            return self._route_to_quiz(state)
        else:
            # 애매한 경우 추가 확인 요청
            return self._request_clarification(state)
    
    def _analyze_user_intent(self, message: str) -> str:
        """
        사용자 메시지에서 의도를 분석
        
        Args:
            message: 사용자 메시지
            
        Returns:
            'question', 'quiz', 또는 'unclear'
        """
        message_lower = message.lower()
        
        # 질문 패턴 확인
        question_score = 0
        for pattern in self.question_patterns:
            if re.search(pattern, message_lower):
                question_score += 1
        
        # 문제 요청 패턴 확인
        quiz_score = 0
        for pattern in self.quiz_patterns:
            if re.search(pattern, message_lower):
                quiz_score += 1
        
        # 진행 요청 패턴 확인 (문제 쪽으로 가중치)
        for pattern in self.proceed_patterns:
            if re.search(pattern, message_lower):
                quiz_score += 2
        
        # 점수 기반 결정
        if question_score > quiz_score:
            return "question"
        elif quiz_score > question_score:
            return "quiz"
        else:
            return "unclear"
    
    def _route_to_qna(self, state: TutorState) -> TutorState:
        """QnAResolver로 라우팅"""
        # 상태 업데이트
        state['current_stage'] = 'qna'
        state['qa_source_router'] = 'post_theory'
        state['ui_mode'] = 'chat'
        
        # 대화 기록 추가
        StateManager.add_conversation(
            state, 
            'PostTheoryRouter',
            user_message=state['user_message'],
            system_response="질문을 QnAResolver로 전달합니다."
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(
            state,
            "질문을 분석하여 답변을 준비하고 있습니다...",
            ui_elements={'type': 'loading', 'message': '답변 준비 중'}
        )
        
        return state
    
    def _route_to_quiz(self, state: TutorState, message: str = None) -> TutorState:
        """QuizGenerator로 라우팅"""
        # 상태 업데이트
        state['current_stage'] = 'quiz'
        state['ui_mode'] = 'quiz'
        
        # 대화 기록 추가
        response_message = message or "문제 출제를 QuizGenerator로 전달합니다."
        StateManager.add_conversation(
            state,
            'PostTheoryRouter',
            user_message=state['user_message'],
            system_response=response_message
        )
        
        # 시스템 메시지 설정
        StateManager.set_system_response(
            state,
            message or "문제를 준비하고 있습니다...",
            ui_elements={'type': 'loading', 'message': '문제 생성 중'}
        )
        
        return state
    
    def _request_clarification(self, state: TutorState) -> TutorState:
        """사용자 의도가 불분명할 때 명확화 요청"""
        clarification_message = (
            "무엇을 도와드릴까요?\n\n"
            "• 궁금한 점이 있으시면 자유롭게 질문해 주세요\n"
            "• 이해도를 확인하고 싶으시면 '문제 주세요' 또는 '퀴즈'라고 말씀해 주세요\n"
            "• 다음 단계로 넘어가고 싶으시면 '다음' 또는 '계속'이라고 말씀해 주세요"
        )
        
        # UI 모드를 채팅으로 유지
        state['ui_mode'] = 'chat'
        
        # 대화 기록 추가
        StateManager.add_conversation(
            state,
            'PostTheoryRouter',
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
                    {'text': '질문하기', 'action': 'question'},
                    {'text': '문제 풀기', 'action': 'quiz'},
                    {'text': '다음 단계', 'action': 'proceed'}
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
            'router': 'PostTheoryRouter',
            'user_message': user_message,
            'detected_intent': intent,
            'next_stage': state.get('current_stage'),
            'ui_mode': state.get('ui_mode'),
            'timestamp': StateManager.add_conversation.__defaults__[0] if hasattr(StateManager.add_conversation, '__defaults__') else None
        }


def create_post_theory_router() -> PostTheoryRouter:
    """PostTheoryRouter 인스턴스 생성 팩토리 함수"""
    return PostTheoryRouter()