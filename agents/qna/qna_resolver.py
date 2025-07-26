# agents/qna/qna_resolver.py
# QnAResolver 메인 에이전트

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# 내부 모듈 임포트
from .search_handler import search_for_question_answer
from .context_integrator import generate_contextual_answer

# 워크플로우 상태 임포트
from workflow.state_management import TutorState

logger = logging.getLogger(__name__)

class QnAResolver:
    """실시간 질문 답변 에이전트
    
    사용자의 질문을 받아 ChromaDB 벡터 검색과 웹 검색을 통해
    학습 맥락에 맞는 답변을 생성하는 에이전트
    """
    
    def __init__(self):
        """QnAResolver 초기화"""
        self.agent_name = "QnAResolver"
        self.supported_question_types = [
            'theory_explanation',
            'practical_example', 
            'troubleshooting',
            'general_question'
        ]
        
    def execute(self, state: TutorState) -> TutorState:
        """QnA 에이전트 실행
        
        Args:
            state: 현재 튜터 상태
            
        Returns:
            TutorState: 업데이트된 상태
        """
        try:
            logger.info(f"QnAResolver 실행 시작: {state.get('user_message', '')[:50]}...")
            
            # 1. 사용자 질문 추출 및 검증
            user_question = state.get('user_message', '').strip()
            if not user_question:
                return self._handle_empty_question(state)
            
            # 2. 학습 맥락 정보 수집
            learning_context = self._extract_learning_context(state)
            
            # 3. 검색 실행
            search_results = self._perform_search(user_question, learning_context)
            
            # 4. 맥락 통합 및 답변 생성
            final_answer = self._generate_final_answer(
                user_question, search_results, learning_context
            )
            
            # 5. 상태 업데이트
            updated_state = self._update_state_with_answer(state, final_answer)
            
            logger.info(f"QnAResolver 실행 완료: 신뢰도 {final_answer.get('confidence_score', 0):.2f}")
            return updated_state
            
        except Exception as e:
            logger.error(f"QnAResolver 실행 실패: {e}")
            return self._handle_error(state, str(e))
    
    def _extract_learning_context(self, state: TutorState) -> Dict[str, Any]:
        """상태에서 학습 맥락 정보 추출
        
        Args:
            state: 현재 튜터 상태
            
        Returns:
            Dict: 학습 맥락 정보
        """
        return {
            'current_chapter': state.get('current_chapter', 1),
            'user_level': state.get('user_level', 'medium'),
            'user_type': state.get('user_type', 'beginner'),
            'current_stage': state.get('current_stage', 'theory'),
            'recent_loops_summary': state.get('recent_loops_summary', []),
            'qa_source_router': state.get('qa_source_router', 'unknown')
        }
    
    def _perform_search(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """질문에 대한 검색 수행
        
        Args:
            question: 사용자 질문
            context: 학습 맥락
            
        Returns:
            Dict: 검색 결과
        """
        try:
            # 검색 전략 결정
            search_strategy = self._determine_search_strategy(question, context)
            
            # 검색 실행
            search_results = search_for_question_answer(
                question=question,
                current_chapter=context['current_chapter'],
                user_level=context['user_level'],
                user_type=context['user_type'],
                strategy=search_strategy
            )
            
            logger.info(f"검색 완료: {search_results.get('total_results', 0)}개 결과")
            return search_results
            
        except Exception as e:
            logger.error(f"검색 실행 실패: {e}")
            return {
                'question': question,
                'total_results': 0,
                'results': [],
                'error': True,
                'error_message': str(e)
            }
    
    def _determine_search_strategy(self, question: str, context: Dict[str, Any]) -> str:
        """질문과 맥락에 따른 검색 전략 결정
        
        Args:
            question: 사용자 질문
            context: 학습 맥락
            
        Returns:
            str: 검색 전략
        """
        # 현재 챕터 관련 질문인지 확인
        current_chapter = context.get('current_chapter', 1)
        chapter_keywords = {
            1: ['ai', '인공지능', '머신러닝', '딥러닝'],
            3: ['프롬프트', 'prompt', 'chatgpt', 'gpt']
        }
        
        question_lower = question.lower()
        
        # 현재 챕터 키워드가 포함된 경우 지식 베이스 우선
        if current_chapter in chapter_keywords:
            if any(keyword in question_lower for keyword in chapter_keywords[current_chapter]):
                return 'knowledge_first'
        
        # 최신 정보가 필요한 질문인지 확인
        recent_keywords = ['최신', '요즘', '현재', '지금', '2024', '2025']
        if any(keyword in question_lower for keyword in recent_keywords):
            return 'web_first'
        
        # 기본적으로 하이브리드 전략 사용
        return 'hybrid'
    
    def _generate_final_answer(self, question: str, search_results: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """최종 답변 생성
        
        Args:
            question: 사용자 질문
            search_results: 검색 결과
            context: 학습 맥락
            
        Returns:
            Dict: 최종 답변
        """
        try:
            # 맥락 통합 및 답변 생성
            final_answer = generate_contextual_answer(
                question=question,
                search_results=search_results,
                current_chapter=context['current_chapter'],
                user_level=context['user_level'],
                user_type=context['user_type'],
                recent_loops=context.get('recent_loops_summary', [])
            )
            
            # QnA 특화 정보 추가
            final_answer['agent_name'] = self.agent_name
            final_answer['search_strategy'] = search_results.get('strategy_used', 'unknown')
            final_answer['qa_source_router'] = context.get('qa_source_router', 'unknown')
            
            return final_answer
            
        except Exception as e:
            logger.error(f"답변 생성 실패: {e}")
            return {
                'question': question,
                'answer': '죄송합니다. 답변 생성 중 오류가 발생했습니다. 다시 질문해 주세요.',
                'answer_type': 'error',
                'confidence_score': 0.0,
                'agent_name': self.agent_name,
                'error': True,
                'error_message': str(e)
            }
    
    def _update_state_with_answer(self, state: TutorState, answer: Dict[str, Any]) -> TutorState:
        """답변으로 상태 업데이트
        
        Args:
            state: 현재 상태
            answer: 생성된 답변
            
        Returns:
            TutorState: 업데이트된 상태
        """
        # 시스템 메시지 설정
        state['system_message'] = answer['answer']
        
        # UI 모드를 자유 대화로 설정
        state['ui_mode'] = 'chat'
        
        # UI 요소 설정 (후속 질문 제안 포함)
        ui_elements = {
            'type': 'qna_response',
            'confidence_score': answer.get('confidence_score', 0.7),
            'answer_type': answer.get('answer_type', 'general_question'),
            'follow_up_suggestions': answer.get('follow_up_suggestions', []),
            'sources_count': len(answer.get('sources_used', [])),
            'show_sources': answer.get('confidence_score', 0.7) > 0.8  # 높은 신뢰도일 때만 출처 표시
        }
        
        state['ui_elements'] = ui_elements
        
        # 현재 루프 대화에 추가
        conversation_entry = {
            'agent_name': self.agent_name,
            'user_message': state.get('user_message', ''),
            'system_response': answer['answer'],
            'ui_elements': ui_elements,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'answer_type': answer.get('answer_type'),
                'confidence_score': answer.get('confidence_score'),
                'search_strategy': answer.get('search_strategy'),
                'sources_used': len(answer.get('sources_used', []))
            }
        }
        
        current_conversations = state.get('current_loop_conversations', [])
        current_conversations.append(conversation_entry)
        state['current_loop_conversations'] = current_conversations
        
        return state
    
    def _handle_empty_question(self, state: TutorState) -> TutorState:
        """빈 질문 처리
        
        Args:
            state: 현재 상태
            
        Returns:
            TutorState: 업데이트된 상태
        """
        state['system_message'] = "질문을 입력해 주세요. 현재 학습 중인 내용에 대해 궁금한 점이 있으시면 언제든 물어보세요."
        state['ui_mode'] = 'chat'
        state['ui_elements'] = {
            'type': 'prompt_for_question',
            'suggestions': [
                f"챕터 {state.get('current_chapter', 1)}에 대해 더 알고 싶어요",
                "실습 예시를 보여주세요",
                "이해가 안 되는 부분이 있어요"
            ]
        }
        
        return state
    
    def _handle_error(self, state: TutorState, error_message: str) -> TutorState:
        """오류 처리
        
        Args:
            state: 현재 상태
            error_message: 오류 메시지
            
        Returns:
            TutorState: 오류 처리된 상태
        """
        state['system_message'] = "죄송합니다. 질문 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
        state['ui_mode'] = 'error'
        state['ui_elements'] = {
            'type': 'error',
            'error_message': error_message,
            'retry_suggestions': [
                "질문을 다시 입력해 주세요",
                "다른 방식으로 질문해 보세요",
                "잠시 후 다시 시도해 주세요"
            ]
        }
        
        logger.error(f"QnAResolver 오류 처리: {error_message}")
        return state
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환
        
        Returns:
            Dict: 에이전트 정보
        """
        return {
            'agent_name': self.agent_name,
            'description': '실시간 질문 답변 에이전트',
            'supported_question_types': self.supported_question_types,
            'search_capabilities': [
                'ChromaDB 벡터 검색',
                '웹 검색 (Google Custom Search)',
                '하이브리드 검색 전략'
            ],
            'context_integration': [
                '학습 맥락 연결',
                '사용자 레벨별 답변 조정',
                '후속 질문 제안'
            ]
        }

# 전역 QnAResolver 인스턴스
qna_resolver = QnAResolver()

def resolve_user_question(state: TutorState) -> TutorState:
    """사용자 질문 해결 (편의 함수)
    
    Args:
        state: 현재 튜터 상태
        
    Returns:
        TutorState: 업데이트된 상태
    """
    return qna_resolver.execute(state)