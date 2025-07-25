# agents/supervisor/loop_manager.py
# 루프 완료 처리 및 요약 생성 기능

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from workflow.state_management import TutorState, StateManager


class LoopManager:
    """학습 루프 관리를 담당하는 클래스"""
    
    def __init__(self):
        self.max_recent_loops = 5  # 최대 보관할 최근 루프 수
        self.max_loop_conversations = 20  # 한 루프당 최대 대화 수
    
    def should_complete_current_loop(self, state: TutorState) -> bool:
        """현재 루프를 완료해야 하는지 판단"""
        
        conversations = state.get('current_loop_conversations', [])
        current_stage = state.get('current_stage', '')
        
        # 명시적 완료 요청
        if current_stage == 'completed':
            return True
        
        # 대화 수가 최대치에 도달
        if len(conversations) >= self.max_loop_conversations:
            return True
        
        # 오류 상태
        if state.get('ui_mode') == 'error':
            return True
        
        # 루프 완료 패턴 감지
        if self._detect_completion_pattern(conversations):
            return True
        
        return False
    
    def _detect_completion_pattern(self, conversations: List[Dict[str, Any]]) -> bool:
        """루프 완료 패턴 감지"""
        
        if len(conversations) < 3:
            return False
        
        # 최근 대화에서 완료 신호 감지
        recent_conversations = conversations[-3:]
        
        # 이론 → 퀴즈 → 평가 패턴 완료
        agents_sequence = [conv.get('agent_name', '') for conv in recent_conversations]
        
        completion_patterns = [
            ['TheoryEducator', 'QuizGenerator', 'EvaluationFeedbackAgent'],
            ['QuizGenerator', 'EvaluationFeedbackAgent', 'LearningSupervisor'],
            ['EvaluationFeedbackAgent', 'QnAResolver', 'LearningSupervisor']
        ]
        
        for pattern in completion_patterns:
            if self._matches_pattern(agents_sequence, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, sequence: List[str], pattern: List[str]) -> bool:
        """시퀀스가 패턴과 일치하는지 확인"""
        if len(sequence) < len(pattern):
            return False
        
        # 마지막 부분이 패턴과 일치하는지 확인
        for i, expected_agent in enumerate(reversed(pattern)):
            if sequence[-(i+1)] != expected_agent:
                return False
        
        return True
    
    def complete_current_loop(self, state: TutorState) -> TutorState:
        """현재 루프 완료 처리"""
        
        conversations = state.get('current_loop_conversations', [])
        
        if not conversations:
            return state
        
        # 루프 요약 생성
        loop_summary = self._generate_loop_summary(state)
        
        # 최근 루프 요약에 추가
        recent_loops = state.get('recent_loops_summary', [])
        recent_loops.append(loop_summary)
        
        # 최대 개수 유지
        if len(recent_loops) > self.max_recent_loops:
            recent_loops = recent_loops[-self.max_recent_loops:]
        
        state['recent_loops_summary'] = recent_loops
        
        # 데이터베이스에 저장 (실제 구현에서는 서비스 레이어 호출)
        self._save_loop_to_database(state, loop_summary, conversations)
        
        # 현재 루프 초기화
        state['current_loop_conversations'] = []
        state['current_loop_id'] = str(uuid.uuid4())
        state['loop_start_time'] = datetime.now().isoformat()
        
        return state
    
    def _generate_loop_summary(self, state: TutorState) -> Dict[str, str]:
        """루프 요약 생성"""
        
        conversations = state.get('current_loop_conversations', [])
        
        if not conversations:
            return {}
        
        # 기본 정보
        summary = {
            'loop_id': state.get('current_loop_id', ''),
            'chapter': str(state.get('current_chapter', 1)),
            'start_time': state.get('loop_start_time', ''),
            'end_time': datetime.now().isoformat(),
            'conversation_count': str(len(conversations))
        }
        
        # 참여 에이전트 분석
        agents_used = set()
        user_questions = []
        key_topics = []
        
        for conv in conversations:
            agent_name = conv.get('agent_name', '')
            if agent_name:
                agents_used.add(agent_name)
            
            # 사용자 질문 수집
            user_message = conv.get('user_message', '')
            if user_message and len(user_message.strip()) > 0:
                user_questions.append(user_message[:100])  # 처음 100자만
            
            # 시스템 응답에서 주요 토픽 추출
            system_response = conv.get('system_response', '')
            if system_response:
                key_topics.extend(self._extract_key_topics(system_response))
        
        summary['agents_used'] = ', '.join(sorted(agents_used))
        summary['main_topics'] = ' | '.join(user_questions[:3])  # 최대 3개 질문
        summary['key_concepts'] = ', '.join(list(set(key_topics))[:5])  # 최대 5개 개념
        
        # 학습 성과 요약
        summary['learning_outcome'] = self._summarize_learning_outcome(conversations)
        
        return summary
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """텍스트에서 주요 토픽 추출 (간단한 키워드 기반)"""
        
        # AI 관련 주요 키워드들
        ai_keywords = [
            'AI', '인공지능', '머신러닝', '딥러닝', '프롬프트', 'ChatGPT',
            '알고리즘', '데이터', '모델', '학습', '예측', '분류', '회귀',
            '신경망', '자연어처리', 'NLP', '컴퓨터비전', '강화학습'
        ]
        
        found_topics = []
        text_lower = text.lower()
        
        for keyword in ai_keywords:
            if keyword.lower() in text_lower or keyword in text:
                found_topics.append(keyword)
        
        return found_topics
    
    def _summarize_learning_outcome(self, conversations: List[Dict[str, Any]]) -> str:
        """학습 성과 요약"""
        
        if not conversations:
            return "학습 활동 없음"
        
        # 에이전트별 활동 분석
        agent_activities = {}
        for conv in conversations:
            agent_name = conv.get('agent_name', '')
            if agent_name not in agent_activities:
                agent_activities[agent_name] = 0
            agent_activities[agent_name] += 1
        
        # 학습 성과 문장 생성
        outcome_parts = []
        
        if 'TheoryEducator' in agent_activities:
            outcome_parts.append("개념 학습 완료")
        
        if 'QuizGenerator' in agent_activities:
            outcome_parts.append("문제 풀이 실습")
        
        if 'QnAResolver' in agent_activities:
            outcome_parts.append(f"질문 답변 {agent_activities['QnAResolver']}회")
        
        if 'EvaluationFeedbackAgent' in agent_activities:
            outcome_parts.append("평가 및 피드백 수행")
        
        if not outcome_parts:
            return "기본 학습 활동 수행"
        
        return ", ".join(outcome_parts)
    
    def _save_loop_to_database(self, state: TutorState, loop_summary: Dict[str, str], 
                              conversations: List[Dict[str, Any]]):
        """루프 데이터를 데이터베이스에 저장"""
        
        # 실제 구현에서는 데이터베이스 서비스를 호출
        # 여기서는 로그만 출력
        print(f"루프 저장: {loop_summary['loop_id'][:8]} - {loop_summary['learning_outcome']}")
        
        # TODO: 실제 데이터베이스 저장 로직 구현
        # - LEARNING_LOOPS 테이블에 루프 정보 저장
        # - CONVERSATIONS 테이블에 대화 내용 저장
        pass
    
    def start_new_loop(self, state: TutorState, reason: str = "new_session") -> TutorState:
        """새로운 루프 시작"""
        
        # 현재 루프가 있다면 완료 처리
        if state.get('current_loop_conversations'):
            state = self.complete_current_loop(state)
        
        # 새 루프 초기화
        state['current_loop_id'] = str(uuid.uuid4())
        state['loop_start_time'] = datetime.now().isoformat()
        state['current_loop_conversations'] = []
        
        # 시작 로그
        print(f"새 루프 시작: {state['current_loop_id'][:8]} - {reason}")
        
        return state
    
    def get_loop_statistics(self, state: TutorState) -> Dict[str, Any]:
        """루프 통계 정보 반환"""
        
        recent_loops = state.get('recent_loops_summary', [])
        current_conversations = state.get('current_loop_conversations', [])
        
        if not recent_loops and not current_conversations:
            return {
                'total_loops': 0,
                'total_conversations': 0,
                'average_loop_length': 0,
                'most_used_agent': None,
                'learning_consistency': 0
            }
        
        # 통계 계산
        total_loops = len(recent_loops)
        if current_conversations:
            total_loops += 1
        
        total_conversations = len(current_conversations)
        for loop in recent_loops:
            total_conversations += int(loop.get('conversation_count', '0'))
        
        # 평균 루프 길이
        avg_loop_length = total_conversations / total_loops if total_loops > 0 else 0
        
        # 가장 많이 사용된 에이전트
        agent_usage = {}
        for loop in recent_loops:
            agents_str = loop.get('agents_used', '')
            if agents_str:
                for agent in agents_str.split(', '):
                    agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        most_used_agent = max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None
        
        # 학습 일관성 (루프 길이의 표준편차 기반)
        loop_lengths = [int(loop.get('conversation_count', '0')) for loop in recent_loops]
        if current_conversations:
            loop_lengths.append(len(current_conversations))
        
        consistency = self._calculate_consistency_score(loop_lengths)
        
        return {
            'total_loops': total_loops,
            'total_conversations': total_conversations,
            'average_loop_length': round(avg_loop_length, 1),
            'most_used_agent': most_used_agent,
            'learning_consistency': consistency
        }
    
    def _calculate_consistency_score(self, values: List[int]) -> float:
        """일관성 점수 계산 (0-100)"""
        
        if len(values) < 2:
            return 100.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # 표준편차가 낮을수록 높은 일관성 점수
        consistency_score = max(0, 100 - (std_dev * 5))
        return round(min(100, consistency_score), 1)