# agents/supervisor/loop_manager.py
# 루프 완료 처리 및 요약 생성 기능

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from workflow.state_management import TutorState, StateManager
from services.loop_service import LoopService
from models.learning_loop import LearningLoop
from models.conversation import Conversation

logger = logging.getLogger(__name__)

class LoopManager:
    """학습 루프 관리를 담당하는 클래스"""
    
    def __init__(self):
        self.loop_service = LoopService()
        self.max_loop_conversations = 50  # 루프당 최대 대화 수
        self.max_loop_duration_minutes = 60  # 루프당 최대 지속 시간 (분)
    
    def should_complete_loop(self, state: TutorState) -> Tuple[bool, str]:
        """루프 완료 여부 판단"""
        try:
            conversations = state.get('current_loop_conversations', [])
            loop_start_time = state.get('loop_start_time', '')
            
            # 1. 대화 수 기준
            if len(conversations) >= self.max_loop_conversations:
                return True, "대화 수 한계 도달"
            
            # 2. 시간 기준
            if loop_start_time:
                start_time = datetime.fromisoformat(loop_start_time)
                duration_minutes = (datetime.now() - start_time).total_seconds() / 60
                if duration_minutes >= self.max_loop_duration_minutes:
                    return True, "시간 한계 도달"
            
            # 3. 학습 완료 기준
            completion_signals = self._check_completion_signals(conversations)
            if completion_signals['should_complete']:
                return True, completion_signals['reason']
            
            # 4. 사용자 명시적 완료 요청
            if self._user_requested_completion(conversations):
                return True, "사용자 완료 요청"
            
            return False, "계속 진행"
            
        except Exception as e:
            logger.error(f"루프 완료 판단 중 오류: {str(e)}")
            return False, "오류로 인한 계속 진행"
    
    def _check_completion_signals(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """학습 완료 신호 확인"""
        if not conversations:
            return {'should_complete': False, 'reason': ''}
        
        # 최근 대화 분석
        recent_conversations = conversations[-5:] if len(conversations) >= 5 else conversations
        
        # 완료 신호 패턴
        completion_patterns = [
            "다음 챕터",
            "완료했습니다",
            "이해했습니다",
            "충분히 학습했습니다",
            "다음으로 넘어가",
            "끝내고 싶습니다"
        ]
        
        # 반복 질문 패턴 (같은 내용 반복)
        user_messages = [
            conv.get('user_message', '') for conv in recent_conversations 
            if conv.get('user_message')
        ]
        
        # 완료 신호 확인
        for conv in recent_conversations:
            user_msg = conv.get('user_message', '').lower()
            for pattern in completion_patterns:
                if pattern.lower() in user_msg:
                    return {'should_complete': True, 'reason': f'완료 신호 감지: {pattern}'}
        
        # 반복 질문 확인 (학습 정체)
        if len(user_messages) >= 3:
            similar_count = 0
            for i in range(len(user_messages) - 1):
                for j in range(i + 1, len(user_messages)):
                    if self._are_similar_messages(user_messages[i], user_messages[j]):
                        similar_count += 1
            
            if similar_count >= 2:
                return {'should_complete': True, 'reason': '반복 질문으로 인한 학습 정체'}
        
        # 에이전트 순환 완료 확인
        agents_in_recent = [conv.get('agent_name', '') for conv in recent_conversations]
        required_agents = ['TheoryEducator', 'QuizGenerator', 'EvaluationFeedbackAgent']
        
        if all(agent in agents_in_recent for agent in required_agents):
            return {'should_complete': True, 'reason': '주요 에이전트 순환 완료'}
        
        return {'should_complete': False, 'reason': ''}
    
    def _are_similar_messages(self, msg1: str, msg2: str) -> bool:
        """두 메시지가 유사한지 확인"""
        if not msg1 or not msg2:
            return False
        
        # 간단한 유사도 검사 (실제로는 더 정교한 방법 사용 가능)
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity > 0.6  # 60% 이상 유사하면 같은 질문으로 간주
    
    def _user_requested_completion(self, conversations: List[Dict[str, Any]]) -> bool:
        """사용자가 명시적으로 완료를 요청했는지 확인"""
        if not conversations:
            return False
        
        # 최근 사용자 메시지 확인
        recent_user_messages = [
            conv.get('user_message', '') for conv in conversations[-3:]
            if conv.get('user_message')
        ]
        
        completion_requests = [
            "끝",
            "완료",
            "그만",
            "다음",
            "넘어가",
            "종료"
        ]
        
        for msg in recent_user_messages:
            for request in completion_requests:
                if request in msg:
                    return True
        
        return False
    
    def complete_current_loop(self, state: TutorState, reason: str = "자동 완료") -> TutorState:
        """현재 루프 완료 처리"""
        try:
            current_loop_id = state.get('current_loop_id')
            if not current_loop_id:
                logger.warning("완료할 루프 ID가 없습니다")
                return state
            
            # 루프 요약 생성
            summary = self.generate_comprehensive_summary(state)
            
            # DB에서 루프 완료 처리
            completed_loop = self.loop_service.complete_loop(
                loop_id=current_loop_id,
                summary=summary,
                auto_summary=False
            )
            
            # State에서 루프 완료 처리
            state = StateManager.complete_current_loop(state, summary)
            
            logger.info(f"루프 완료: {current_loop_id}, 사유: {reason}")
            
            # 완료 메시지 설정
            completion_message = self._generate_completion_message(completed_loop, reason)
            state = StateManager.set_system_response(state, completion_message)
            
            return state
            
        except Exception as e:
            logger.error(f"루프 완료 처리 중 오류: {str(e)}")
            return state
    
    def generate_comprehensive_summary(self, state: TutorState) -> str:
        """포괄적인 루프 요약 생성"""
        try:
            conversations = state.get('current_loop_conversations', [])
            if not conversations:
                return "대화 내용이 없는 루프입니다."
            
            # 기본 정보
            loop_id = state.get('current_loop_id', 'unknown')
            chapter = state.get('current_chapter', 1)
            user_level = state.get('user_level', 'unknown')
            user_type = state.get('user_type', 'unknown')
            
            # 시간 정보
            start_time = state.get('loop_start_time', '')
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                duration = (datetime.now() - start_dt).total_seconds() / 60
            else:
                duration = 0
            
            # 대화 분석
            analysis = self._analyze_conversations_for_summary(conversations)
            
            # 요약 생성
            summary_parts = [
                f"=== 루프 {loop_id[:8]} 완료 요약 ===",
                f"챕터: {chapter} | 사용자: {user_type}/{user_level}",
                f"지속시간: {duration:.1f}분 | 대화수: {len(conversations)}",
                "",
                "주요 활동:",
                f"- 이론 학습: {'완료' if analysis['has_theory'] else '미완료'}",
                f"- 퀴즈 풀이: {'완료' if analysis['has_quiz'] else '미완료'}",
                f"- 질문 답변: {analysis['qna_count']}회",
                f"- 사용 에이전트: {', '.join(analysis['agents_used'])}",
                ""
            ]
            
            # 주요 질문들
            if analysis['key_questions']:
                summary_parts.append("주요 질문:")
                for i, question in enumerate(analysis['key_questions'][:3], 1):
                    summary_parts.append(f"{i}. {question}")
                summary_parts.append("")
            
            # 학습 성과
            if analysis['learning_outcomes']:
                summary_parts.append("학습 성과:")
                for outcome in analysis['learning_outcomes']:
                    summary_parts.append(f"- {outcome}")
                summary_parts.append("")
            
            # 다음 단계 추천
            next_steps = self._generate_next_steps(analysis, state)
            if next_steps:
                summary_parts.append("다음 단계 추천:")
                for step in next_steps:
                    summary_parts.append(f"- {step}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"요약 생성 중 오류: {str(e)}")
            return f"요약 생성 실패: {str(e)}"
    
    def _analyze_conversations_for_summary(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """요약을 위한 대화 분석"""
        analysis = {
            'has_theory': False,
            'has_quiz': False,
            'qna_count': 0,
            'agents_used': set(),
            'key_questions': [],
            'learning_outcomes': []
        }
        
        for conv in conversations:
            agent_name = conv.get('agent_name', '')
            analysis['agents_used'].add(agent_name)
            
            # 에이전트별 활동 확인
            if agent_name == 'TheoryEducator':
                analysis['has_theory'] = True
            elif agent_name == 'QuizGenerator':
                analysis['has_quiz'] = True
            elif agent_name == 'QnAResolver':
                analysis['qna_count'] += 1
            
            # 사용자 질문 수집
            user_msg = conv.get('user_message', '')
            if user_msg and len(user_msg) > 10:  # 의미있는 질문만
                analysis['key_questions'].append(user_msg[:100])
            
            # 학습 성과 추출 (시스템 응답에서)
            system_response = conv.get('system_response', '')
            if system_response and '이해' in system_response:
                # 간단한 성과 추출 로직
                if '개념' in system_response:
                    analysis['learning_outcomes'].append('개념 이해 향상')
                if '실습' in system_response:
                    analysis['learning_outcomes'].append('실습 경험 획득')
        
        analysis['agents_used'] = list(analysis['agents_used'])
        return analysis
    
    def _generate_next_steps(self, analysis: Dict[str, Any], state: TutorState) -> List[str]:
        """다음 단계 추천 생성"""
        next_steps = []
        
        # 이론 학습이 없었다면
        if not analysis['has_theory']:
            next_steps.append("기본 개념 학습 진행")
        
        # 퀴즈가 없었다면
        if not analysis['has_quiz']:
            next_steps.append("학습 내용 확인을 위한 퀴즈 풀이")
        
        # 질문이 적었다면
        if analysis['qna_count'] < 2:
            next_steps.append("궁금한 점에 대한 적극적인 질문")
        
        # 챕터 진행 상황에 따라
        current_chapter = state.get('current_chapter', 1)
        if current_chapter < 3:  # 마지막 챕터가 아니라면
            next_steps.append(f"챕터 {current_chapter + 1} 학습 준비")
        
        return next_steps
    
    def _generate_completion_message(self, loop: LearningLoop, reason: str) -> str:
        """루프 완료 메시지 생성"""
        try:
            metrics = loop.get_performance_metrics()
            
            message_parts = [
                f"🎉 학습 루프가 완료되었습니다!",
                "",
                f"📊 학습 성과:",
                f"• 소요 시간: {metrics['duration_minutes']}분",
                f"• 상호작용: {metrics['interaction_count']}회",
                f"• 퀴즈 성공률: {metrics['quiz_success_rate']:.1f}%",
                "",
                f"완료 사유: {reason}",
                "",
                "계속해서 다음 학습을 진행하거나 질문해 주세요! 😊"
            ]
            
            return "\n".join(message_parts)
            
        except Exception as e:
            logger.error(f"완료 메시지 생성 중 오류: {str(e)}")
            return "학습 루프가 완료되었습니다. 계속 학습을 진행해 주세요!"
    
    def start_new_loop_if_needed(self, state: TutorState) -> TutorState:
        """필요시 새 루프 시작"""
        try:
            current_loop_id = state.get('current_loop_id')
            user_id = int(state.get('user_id', 0))
            chapter_id = state.get('current_chapter', 1)
            
            # 현재 루프가 없거나 완료된 경우 새 루프 시작
            if not current_loop_id or not state.get('current_loop_conversations'):
                new_loop, updated_state = self.loop_service.start_new_loop(
                    user_id=user_id,
                    chapter_id=chapter_id,
                    loop_type='mixed',
                    state=state
                )
                
                logger.info(f"새 루프 시작: {new_loop.loop_id}")
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"새 루프 시작 중 오류: {str(e)}")
            return state
    
    def optimize_loop_state(self, state: TutorState) -> TutorState:
        """루프 상태 최적화"""
        try:
            # State 크기 최적화
            state = self.loop_service.optimize_state_size(state)
            
            # 메모리 사용량 확인 및 정리
            conversations = state.get('current_loop_conversations', [])
            if len(conversations) > 100:  # 너무 많은 대화가 쌓인 경우
                logger.warning(f"대화 수가 너무 많음: {len(conversations)}")
                # 강제 루프 완료
                state = self.complete_current_loop(state, "메모리 최적화를 위한 강제 완료")
                state = self.start_new_loop_if_needed(state)
            
            return state
            
        except Exception as e:
            logger.error(f"루프 상태 최적화 중 오류: {str(e)}")
            return state
    
    def get_loop_status_info(self, state: TutorState) -> Dict[str, Any]:
        """현재 루프 상태 정보 반환"""
        try:
            conversations = state.get('current_loop_conversations', [])
            loop_start_time = state.get('loop_start_time', '')
            
            # 지속 시간 계산
            duration_minutes = 0
            if loop_start_time:
                start_time = datetime.fromisoformat(loop_start_time)
                duration_minutes = (datetime.now() - start_time).total_seconds() / 60
            
            # 에이전트 사용 현황
            agents_used = set()
            for conv in conversations:
                agents_used.add(conv.get('agent_name', ''))
            
            return {
                'loop_id': state.get('current_loop_id', ''),
                'conversation_count': len(conversations),
                'duration_minutes': round(duration_minutes, 1),
                'agents_used': list(agents_used),
                'should_complete': self.should_complete_loop(state)[0],
                'completion_reason': self.should_complete_loop(state)[1]
            }
            
        except Exception as e:
            logger.error(f"루프 상태 정보 조회 중 오류: {str(e)}")
            return {}