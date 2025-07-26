# services/loop_service.py
# 학습 루프 관리 서비스

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from models.learning_loop import LearningLoop
from models.conversation import Conversation
from models.user import UserLearningProgress
from workflow.state_management import TutorState, StateManager
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class LoopService:
    """학습 루프 관리 서비스"""
    
    def __init__(self):
        self.db_service = DatabaseService()
    
    def start_new_loop(self, user_id: int, chapter_id: int, 
                      loop_type: str = 'mixed', 
                      state: Optional[TutorState] = None) -> Tuple[LearningLoop, TutorState]:
        """새로운 학습 루프 시작"""
        try:
            # 기존 활성 루프가 있다면 완료 처리
            active_loop = LearningLoop.get_active_loop(user_id, chapter_id)
            if active_loop:
                logger.info(f"기존 활성 루프 {active_loop.loop_id} 완료 처리")
                self.complete_loop(active_loop.loop_id, auto_summary=True)
            
            # 새 루프 생성
            new_loop = LearningLoop(
                user_id=user_id,
                chapter_id=chapter_id,
                loop_type=loop_type,
                metadata={'created_by': 'loop_service'}
            )
            new_loop.start_loop()
            
            logger.info(f"새 루프 시작: {new_loop.loop_id}")
            
            # State 업데이트
            if state:
                state = StateManager.start_new_loop(state)
                state['current_loop_id'] = new_loop.loop_id
                state['current_chapter'] = chapter_id
                state['loop_start_time'] = new_loop.started_at.isoformat()
            
            return new_loop, state
            
        except Exception as e:
            logger.error(f"루프 시작 중 오류: {str(e)}")
            raise
    
    def complete_loop(self, loop_id: str, summary: Optional[str] = None, 
                     auto_summary: bool = False) -> LearningLoop:
        """학습 루프 완료"""
        try:
            loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
            if not loop:
                raise ValueError(f"루프를 찾을 수 없습니다: {loop_id}")
            
            if loop.loop_status != 'active':
                logger.warning(f"이미 완료된 루프: {loop_id}")
                return loop
            
            # 요약 생성
            if auto_summary and not summary:
                summary = self.generate_loop_summary(loop_id)
            
            # 루프 완료 처리
            loop.complete_loop(summary)
            
            logger.info(f"루프 완료: {loop_id}")
            return loop
            
        except Exception as e:
            logger.error(f"루프 완료 중 오류: {str(e)}")
            raise
    
    def abandon_loop(self, loop_id: str, reason: str = "사용자 중단") -> LearningLoop:
        """학습 루프 중단"""
        try:
            loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
            if not loop:
                raise ValueError(f"루프를 찾을 수 없습니다: {loop_id}")
            
            loop.abandon_loop(reason)
            
            logger.info(f"루프 중단: {loop_id}, 사유: {reason}")
            return loop
            
        except Exception as e:
            logger.error(f"루프 중단 중 오류: {str(e)}")
            raise
    
    def add_conversation_to_loop(self, loop_id: str, agent_name: str, 
                               message_type: str, user_message: str = None,
                               system_response: str = None, 
                               ui_elements: Optional[Dict[str, Any]] = None,
                               ui_mode: str = 'chat',
                               processing_time_ms: int = 0) -> Conversation:
        """루프에 대화 추가"""
        try:
            loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
            if not loop:
                raise ValueError(f"루프를 찾을 수 없습니다: {loop_id}")
            
            conversation = loop.add_conversation(
                agent_name=agent_name,
                message_type=message_type,
                user_message=user_message,
                system_response=system_response,
                ui_elements=ui_elements,
                ui_mode=ui_mode
            )
            
            # 처리 시간 업데이트
            if processing_time_ms > 0:
                conversation.processing_time_ms = processing_time_ms
                conversation.save()
            
            logger.debug(f"대화 추가: {loop_id} - {agent_name}")
            return conversation
            
        except Exception as e:
            logger.error(f"대화 추가 중 오류: {str(e)}")
            raise
    
    def update_state_with_conversation(self, state: TutorState, agent_name: str,
                                     user_message: str = "", system_response: str = "",
                                     ui_elements: Optional[Dict[str, Any]] = None) -> TutorState:
        """State에 대화 내용 추가"""
        try:
            state = StateManager.add_conversation(
                state=state,
                agent_name=agent_name,
                user_message=user_message,
                system_response=system_response,
                ui_elements=ui_elements
            )
            
            # 동시에 DB에도 저장
            if state.get('current_loop_id'):
                self.add_conversation_to_loop(
                    loop_id=state['current_loop_id'],
                    agent_name=agent_name,
                    message_type='user' if user_message else 'system',
                    user_message=user_message,
                    system_response=system_response,
                    ui_elements=ui_elements,
                    ui_mode=state.get('ui_mode', 'chat')
                )
            
            return state
            
        except Exception as e:
            logger.error(f"State 대화 업데이트 중 오류: {str(e)}")
            raise
    
    def generate_loop_summary(self, loop_id: str) -> str:
        """루프 요약 생성"""
        try:
            loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
            if not loop:
                return "루프를 찾을 수 없습니다."
            
            conversations = loop.get_conversations()
            if not conversations:
                return "대화 내용이 없습니다."
            
            # 기본 정보
            summary_parts = [
                f"=== 루프 {loop_id[:8]} 요약 ===",
                f"챕터: {loop.chapter_id}",
                f"시작: {loop.started_at.strftime('%Y-%m-%d %H:%M')}",
                f"종료: {loop.completed_at.strftime('%Y-%m-%d %H:%M') if loop.completed_at else '진행중'}",
                f"대화 수: {len(conversations)}",
                ""
            ]
            
            # 주요 활동 요약
            agents_used = set()
            user_questions = []
            system_responses = []
            
            for conv in conversations:
                agents_used.add(conv.agent_name)
                
                if conv.message_type == 'user' and conv.user_message:
                    user_questions.append(conv.user_message[:100])
                elif conv.message_type == 'system' and conv.system_response:
                    system_responses.append(f"{conv.agent_name}: {conv.system_response[:100]}")
            
            summary_parts.append(f"사용된 에이전트: {', '.join(agents_used)}")
            
            if user_questions:
                summary_parts.append("\n주요 사용자 질문:")
                for i, question in enumerate(user_questions[:3], 1):
                    summary_parts.append(f"{i}. {question}...")
            
            if system_responses:
                summary_parts.append("\n주요 시스템 응답:")
                for i, response in enumerate(system_responses[:3], 1):
                    summary_parts.append(f"{i}. {response}...")
            
            # 성과 지표
            metrics = loop.get_performance_metrics()
            summary_parts.extend([
                "",
                f"소요 시간: {metrics['duration_minutes']}분",
                f"퀴즈 시도: {metrics['quiz_attempts_count']}회",
                f"퀴즈 성공률: {metrics['quiz_success_rate']:.1f}%"
            ])
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"루프 요약 생성 중 오류: {str(e)}")
            return f"요약 생성 실패: {str(e)}"
    
    def get_loop_context_for_state(self, user_id: int, chapter_id: int, 
                                  current_loop_id: str = None) -> Dict[str, Any]:
        """State 관리를 위한 루프 컨텍스트 조회"""
        try:
            # 최근 완료된 루프들의 요약
            recent_summaries = LearningLoop.get_recent_loops_summary(
                user_id=user_id,
                chapter_id=chapter_id,
                limit=5
            )
            
            # 현재 활성 루프의 대화
            current_conversations = []
            if current_loop_id:
                current_loop = LearningLoop.query.filter_by(loop_id=current_loop_id).first()
                if current_loop:
                    conversations = current_loop.get_conversations(limit=20)  # 최근 20개
                    current_conversations = [
                        {
                            'agent_name': conv.agent_name,
                            'user_message': conv.user_message,
                            'system_response': conv.system_response,
                            'ui_elements': conv.ui_elements,
                            'timestamp': conv.timestamp.isoformat(),
                            'sequence_order': conv.sequence_order
                        }
                        for conv in conversations
                    ]
            
            return {
                'recent_loops_summary': recent_summaries,
                'current_loop_conversations': current_conversations
            }
            
        except Exception as e:
            logger.error(f"루프 컨텍스트 조회 중 오류: {str(e)}")
            return {
                'recent_loops_summary': [],
                'current_loop_conversations': []
            }
    
    def optimize_state_size(self, state: TutorState) -> TutorState:
        """State 크기 최적화"""
        try:
            # 현재 루프 대화가 너무 많으면 압축
            if len(state['current_loop_conversations']) > 50:
                # 최근 30개만 유지하고 나머지는 요약으로 압축
                recent_conversations = state['current_loop_conversations'][-30:]
                older_conversations = state['current_loop_conversations'][:-30]
                
                # 이전 대화들을 간단히 요약
                summary_text = self._compress_conversations(older_conversations)
                
                # 요약을 첫 번째 대화로 추가
                summary_conversation = {
                    'agent_name': 'system',
                    'user_message': '',
                    'system_response': f"[이전 대화 요약] {summary_text}",
                    'ui_elements': None,
                    'timestamp': older_conversations[0]['timestamp'] if older_conversations else datetime.now().isoformat(),
                    'sequence_order': 0
                }
                
                state['current_loop_conversations'] = [summary_conversation] + recent_conversations
            
            # 최근 루프 요약도 최대 5개로 제한
            if len(state['recent_loops_summary']) > 5:
                state['recent_loops_summary'] = state['recent_loops_summary'][-5:]
            
            return state
            
        except Exception as e:
            logger.error(f"State 최적화 중 오류: {str(e)}")
            return state
    
    def _compress_conversations(self, conversations: List[Dict[str, Any]]) -> str:
        """대화 목록을 압축된 요약으로 변환"""
        if not conversations:
            return "대화 내용 없음"
        
        # 간단한 압축 로직
        user_messages = []
        system_responses = []
        
        for conv in conversations:
            if conv.get('user_message'):
                user_messages.append(conv['user_message'][:50])
            if conv.get('system_response'):
                system_responses.append(f"{conv['agent_name']}: {conv['system_response'][:50]}")
        
        summary_parts = []
        if user_messages:
            summary_parts.append(f"사용자 질문 {len(user_messages)}개")
        if system_responses:
            summary_parts.append(f"시스템 응답 {len(system_responses)}개")
        
        return " | ".join(summary_parts)
    
    def get_loop_statistics(self, user_id: int, chapter_id: int = None, 
                           days: int = 30) -> Dict[str, Any]:
        """루프 통계 조회"""
        try:
            # 기간 설정
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 기본 쿼리
            query = LearningLoop.query.filter(
                LearningLoop.user_id == user_id,
                LearningLoop.started_at >= start_date
            )
            
            if chapter_id:
                query = query.filter(LearningLoop.chapter_id == chapter_id)
            
            loops = query.all()
            
            # 통계 계산
            total_loops = len(loops)
            completed_loops = len([l for l in loops if l.loop_status == 'completed'])
            abandoned_loops = len([l for l in loops if l.loop_status == 'abandoned'])
            
            total_study_time = sum([l.duration_minutes or 0 for l in loops])
            avg_loop_duration = total_study_time / total_loops if total_loops > 0 else 0
            
            # 일별 활동
            daily_activity = {}
            for loop in loops:
                date_key = loop.started_at.strftime('%Y-%m-%d')
                if date_key not in daily_activity:
                    daily_activity[date_key] = 0
                daily_activity[date_key] += 1
            
            return {
                'period_days': days,
                'total_loops': total_loops,
                'completed_loops': completed_loops,
                'abandoned_loops': abandoned_loops,
                'completion_rate': (completed_loops / total_loops * 100) if total_loops > 0 else 0,
                'total_study_time_minutes': total_study_time,
                'average_loop_duration_minutes': round(avg_loop_duration, 1),
                'daily_activity': daily_activity
            }
            
        except Exception as e:
            logger.error(f"루프 통계 조회 중 오류: {str(e)}")
            return {}
    
    def cleanup_old_loops(self, days_to_keep: int = 90):
        """오래된 루프 정리"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            old_loops = LearningLoop.query.filter(
                LearningLoop.started_at < cutoff_date,
                LearningLoop.loop_status.in_(['completed', 'abandoned'])
            ).all()
            
            deleted_count = 0
            for loop in old_loops:
                # 중요한 루프는 보존 (예: 높은 성과를 보인 루프)
                metrics = loop.get_performance_metrics()
                if metrics.get('quiz_success_rate', 0) < 80:  # 성공률 80% 미만만 삭제
                    loop.delete()
                    deleted_count += 1
            
            logger.info(f"오래된 루프 {deleted_count}개 정리 완료")
            return deleted_count
            
        except Exception as e:
            logger.error(f"루프 정리 중 오류: {str(e)}")
            return 0