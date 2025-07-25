# agents/supervisor/progress_analyzer.py
# 학습 진도 분석 로직 구현

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from workflow.state_management import TutorState


class ProgressAnalyzer:
    """학습 진도 분석을 담당하는 클래스"""
    
    def __init__(self):
        self.chapter_requirements = {
            1: {"min_conversations": 5, "required_quiz": True, "min_understanding": 70},
            2: {"min_conversations": 6, "required_quiz": True, "min_understanding": 75},
            3: {"min_conversations": 8, "required_quiz": True, "min_understanding": 80}
        }
    
    def analyze_current_progress(self, state: TutorState) -> Dict[str, Any]:
        """현재 학습 진도 분석"""
        
        current_chapter = state.get('current_chapter', 1)
        conversations = state.get('current_loop_conversations', [])
        recent_loops = state.get('recent_loops_summary', [])
        
        analysis = {
            'chapter': current_chapter,
            'current_loop_progress': self._analyze_current_loop(conversations),
            'overall_progress': self._analyze_overall_progress(recent_loops, current_chapter),
            'completion_status': self._check_completion_status(state),
            'recommendations': self._generate_recommendations(state)
        }
        
        return analysis
    
    def _analyze_current_loop(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """현재 루프의 진도 분석"""
        
        if not conversations:
            return {
                'conversation_count': 0,
                'agents_involved': [],
                'has_theory': False,
                'has_quiz': False,
                'has_qna': False,
                'loop_duration': 0
            }
        
        # 참여한 에이전트 분석
        agents_involved = set()
        has_theory = False
        has_quiz = False
        has_qna = False
        
        for conv in conversations:
            agent_name = conv.get('agent_name', '')
            agents_involved.add(agent_name)
            
            if agent_name == 'TheoryEducator':
                has_theory = True
            elif agent_name == 'QuizGenerator':
                has_quiz = True
            elif agent_name == 'QnAResolver':
                has_qna = True
        
        # 루프 지속 시간 계산
        if conversations:
            first_time = datetime.fromisoformat(conversations[0]['timestamp'])
            last_time = datetime.fromisoformat(conversations[-1]['timestamp'])
            duration_minutes = (last_time - first_time).total_seconds() / 60
        else:
            duration_minutes = 0
        
        return {
            'conversation_count': len(conversations),
            'agents_involved': list(agents_involved),
            'has_theory': has_theory,
            'has_quiz': has_quiz,
            'has_qna': has_qna,
            'loop_duration': duration_minutes
        }
    
    def _analyze_overall_progress(self, recent_loops: List[Dict[str, str]], 
                                current_chapter: int) -> Dict[str, Any]:
        """전체 학습 진도 분석"""
        
        # 현재 챕터의 루프들만 필터링
        chapter_loops = [
            loop for loop in recent_loops 
            if int(loop.get('chapter', '0')) == current_chapter
        ]
        
        total_conversations = sum(
            int(loop.get('conversation_count', '0')) for loop in chapter_loops
        )
        
        # 사용된 에이전트 분석
        all_agents = set()
        for loop in chapter_loops:
            agents_str = loop.get('agents_used', '')
            if agents_str:
                all_agents.update(agents_str.split(', '))
        
        return {
            'chapter_loops_count': len(chapter_loops),
            'total_conversations': total_conversations,
            'agents_used': list(all_agents),
            'average_loop_duration': self._calculate_average_duration(chapter_loops),
            'learning_consistency': self._calculate_consistency(chapter_loops)
        }
    
    def _calculate_average_duration(self, loops: List[Dict[str, str]]) -> float:
        """평균 루프 지속 시간 계산"""
        if not loops:
            return 0.0
        
        total_duration = 0
        valid_loops = 0
        
        for loop in loops:
            try:
                start_time = datetime.fromisoformat(loop.get('start_time', ''))
                end_time = datetime.fromisoformat(loop.get('end_time', ''))
                duration = (end_time - start_time).total_seconds() / 60
                total_duration += duration
                valid_loops += 1
            except:
                continue
        
        return total_duration / valid_loops if valid_loops > 0 else 0.0
    
    def _calculate_consistency(self, loops: List[Dict[str, str]]) -> float:
        """학습 일관성 점수 계산 (0-100)"""
        if len(loops) < 2:
            return 100.0  # 루프가 적으면 일관성 높음으로 간주
        
        # 루프 간 대화 수의 일관성 측정
        conversation_counts = [
            int(loop.get('conversation_count', '0')) for loop in loops
        ]
        
        if not conversation_counts:
            return 100.0
        
        # 표준편차를 이용한 일관성 측정
        mean_count = sum(conversation_counts) / len(conversation_counts)
        variance = sum((x - mean_count) ** 2 for x in conversation_counts) / len(conversation_counts)
        std_dev = variance ** 0.5
        
        # 일관성 점수 (표준편차가 낮을수록 높은 점수)
        consistency_score = max(0, 100 - (std_dev * 10))
        return min(100, consistency_score)
    
    def _check_completion_status(self, state: TutorState) -> Dict[str, Any]:
        """챕터 완료 상태 확인"""
        
        current_chapter = state.get('current_chapter', 1)
        requirements = self.chapter_requirements.get(current_chapter, {})
        
        # 현재 진도 확인
        conversations = state.get('current_loop_conversations', [])
        recent_loops = state.get('recent_loops_summary', [])
        
        # 총 대화 수 계산
        total_conversations = len(conversations)
        for loop in recent_loops:
            if int(loop.get('chapter', '0')) == current_chapter:
                total_conversations += int(loop.get('conversation_count', '0'))
        
        # 퀴즈 완료 여부 확인
        has_quiz = any(
            'QuizGenerator' in conv.get('agent_name', '') 
            for conv in conversations
        )
        
        # 완료 조건 확인
        min_conversations = requirements.get('min_conversations', 5)
        required_quiz = requirements.get('required_quiz', True)
        
        is_complete = (
            total_conversations >= min_conversations and
            (not required_quiz or has_quiz)
        )
        
        return {
            'is_complete': is_complete,
            'total_conversations': total_conversations,
            'min_required': min_conversations,
            'has_quiz': has_quiz,
            'quiz_required': required_quiz,
            'completion_percentage': min(100, (total_conversations / min_conversations) * 100)
        }
    
    def _generate_recommendations(self, state: TutorState) -> List[str]:
        """학습 진도에 따른 추천사항 생성"""
        
        recommendations = []
        
        # 현재 루프 분석
        conversations = state.get('current_loop_conversations', [])
        current_loop_analysis = self._analyze_current_loop(conversations)
        
        # 대화 수가 적은 경우
        if current_loop_analysis['conversation_count'] < 3:
            recommendations.append("더 많은 질문과 상호작용을 통해 학습을 깊이 있게 진행해보세요.")
        
        # 이론 학습이 없는 경우
        if not current_loop_analysis['has_theory']:
            recommendations.append("기본 개념 학습을 먼저 진행하는 것을 권장합니다.")
        
        # 퀴즈가 없는 경우
        if not current_loop_analysis['has_quiz'] and current_loop_analysis['conversation_count'] > 3:
            recommendations.append("학습한 내용을 확인하기 위해 퀴즈를 풀어보세요.")
        
        # 질문이 없는 경우
        if not current_loop_analysis['has_qna'] and current_loop_analysis['conversation_count'] > 2:
            recommendations.append("궁금한 점이 있으면 언제든 질문해보세요.")
        
        # 루프 지속 시간이 너무 긴 경우
        if current_loop_analysis['loop_duration'] > 30:
            recommendations.append("학습 효율을 위해 적절한 휴식을 취하는 것을 권장합니다.")
        
        # 완료 상태 확인
        completion_status = self._check_completion_status(state)
        if completion_status['is_complete']:
            recommendations.append("현재 챕터 학습이 완료되었습니다. 다음 챕터로 진행할 수 있습니다.")
        elif completion_status['completion_percentage'] > 80:
            recommendations.append("챕터 완료가 거의 다 되었습니다. 조금만 더 학습해보세요.")
        
        return recommendations if recommendations else ["현재 학습 진도가 양호합니다. 계속 진행해주세요."]
    
    def should_advance_chapter(self, state: TutorState) -> bool:
        """다음 챕터로 진행해야 하는지 판단"""
        
        completion_status = self._check_completion_status(state)
        return completion_status['is_complete']
    
    def get_next_recommended_action(self, state: TutorState) -> str:
        """다음 권장 행동 반환"""
        
        current_loop_analysis = self._analyze_current_loop(
            state.get('current_loop_conversations', [])
        )
        
        # 이론 학습이 없으면 이론부터
        if not current_loop_analysis['has_theory']:
            return 'theory'
        
        # 이론은 있지만 퀴즈가 없으면 퀴즈
        if current_loop_analysis['has_theory'] and not current_loop_analysis['has_quiz']:
            return 'quiz'
        
        # 완료 조건 확인
        if self.should_advance_chapter(state):
            return 'advance_chapter'
        
        # 기본적으로 계속 학습
        return 'continue_learning'