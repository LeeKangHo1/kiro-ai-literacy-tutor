# agents/supervisor/decision_maker.py
# 다음 단계 결정 로직 구현

from typing import Dict, List, Any, Optional, Literal
from workflow.state_management import TutorState
from .progress_analyzer import ProgressAnalyzer
from .loop_manager import LoopManager


class DecisionMaker:
    """다음 학습 단계 결정을 담당하는 클래스"""
    
    def __init__(self):
        self.progress_analyzer = ProgressAnalyzer()
        self.loop_manager = LoopManager()
        
        # 챕터별 학습 순서 정의
        self.chapter_flow = {
            1: ["theory", "quiz", "evaluation", "qna"],
            2: ["theory", "quiz", "evaluation", "qna"],
            3: ["theory", "practice", "quiz", "evaluation", "qna"]
        }
        
        # 최대 챕터 수
        self.max_chapter = 3
    
    def decide_next_step(self, state: TutorState) -> Dict[str, Any]:
        """다음 학습 단계 결정"""
        
        # 현재 상태 분석
        progress_analysis = self.progress_analyzer.analyze_current_progress(state)
        
        # 루프 완료 여부 확인
        should_complete_loop = self.loop_manager.should_complete_current_loop(state)
        
        if should_complete_loop:
            return self._decide_after_loop_completion(state, progress_analysis)
        else:
            return self._decide_within_loop(state, progress_analysis)
    
    def _decide_within_loop(self, state: TutorState, 
                           progress_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """루프 내에서의 다음 단계 결정"""
        
        current_loop_progress = progress_analysis['current_loop_progress']
        current_chapter = state.get('current_chapter', 1)
        user_message = state.get('user_message', '').lower()
        
        # 사용자 의도 분석
        user_intent = self._analyze_user_intent(user_message)
        
        # 현재 루프에서 진행된 활동 확인
        has_theory = current_loop_progress['has_theory']
        has_quiz = current_loop_progress['has_quiz']
        has_qna = current_loop_progress['has_qna']
        
        # 결정 로직
        if user_intent == 'question':
            return {
                'next_step': 'qna_resolver',
                'stage': 'question',
                'reason': '사용자 질문 처리',
                'ui_mode': 'chat'
            }
        
        elif user_intent == 'quiz_request':
            return {
                'next_step': 'quiz_generator',
                'stage': 'quiz',
                'reason': '사용자 퀴즈 요청',
                'ui_mode': 'quiz'
            }
        
        elif not has_theory:
            return {
                'next_step': 'theory_educator',
                'stage': 'theory',
                'reason': '기본 개념 학습 필요',
                'ui_mode': 'chat'
            }
        
        elif has_theory and not has_quiz and user_intent != 'continue':
            return {
                'next_step': 'quiz_generator',
                'stage': 'quiz',
                'reason': '이론 학습 후 문제 풀이',
                'ui_mode': 'quiz'
            }
        
        else:
            # 기본적으로 계속 진행
            return {
                'next_step': 'continue',
                'stage': 'continue',
                'reason': '현재 단계 계속 진행',
                'ui_mode': state.get('ui_mode', 'chat')
            }
    
    def _decide_after_loop_completion(self, state: TutorState, 
                                    progress_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """루프 완료 후 다음 단계 결정"""
        
        completion_status = progress_analysis['completion_status']
        current_chapter = state.get('current_chapter', 1)
        
        # 챕터 완료 여부 확인
        if completion_status['is_complete']:
            if current_chapter < self.max_chapter:
                # 다음 챕터로 진행
                return {
                    'next_step': 'advance_chapter',
                    'stage': 'theory',
                    'reason': f'챕터 {current_chapter} 완료, 다음 챕터 진행',
                    'ui_mode': 'chat',
                    'new_chapter': current_chapter + 1
                }
            else:
                # 전체 과정 완료
                return {
                    'next_step': 'course_complete',
                    'stage': 'completed',
                    'reason': '전체 과정 완료',
                    'ui_mode': 'chat'
                }
        else:
            # 현재 챕터 계속 진행
            recommended_action = self.progress_analyzer.get_next_recommended_action(state)
            
            if recommended_action == 'theory':
                return {
                    'next_step': 'theory_educator',
                    'stage': 'theory',
                    'reason': '추가 개념 학습 필요',
                    'ui_mode': 'chat'
                }
            elif recommended_action == 'quiz':
                return {
                    'next_step': 'quiz_generator',
                    'stage': 'quiz',
                    'reason': '문제 풀이를 통한 이해도 확인',
                    'ui_mode': 'quiz'
                }
            else:
                return {
                    'next_step': 'continue_learning',
                    'stage': 'theory',
                    'reason': '학습 계속 진행',
                    'ui_mode': 'chat'
                }
    
    def _analyze_user_intent(self, user_message: str) -> Literal[
        'question', 'quiz_request', 'continue', 'help', 'unknown'
    ]:
        """사용자 의도 분석"""
        
        if not user_message:
            return 'unknown'
        
        message_lower = user_message.lower()
        
        # 질문 패턴
        question_patterns = [
            '?', '뭐', '무엇', '어떻게', '왜', '언제', '어디서', 
            '질문', '궁금', '모르겠', '이해가 안', '설명'
        ]
        if any(pattern in message_lower for pattern in question_patterns):
            return 'question'
        
        # 퀴즈 요청 패턴
        quiz_patterns = [
            '문제', '퀴즈', '테스트', '연습', '실습', '풀어', 
            '출제', '시험', '평가', '확인'
        ]
        if any(pattern in message_lower for pattern in quiz_patterns):
            return 'quiz_request'
        
        # 진행 요청 패턴
        continue_patterns = [
            '다음', '계속', '진행', '넘어가', '완료', '끝', 
            '이어서', '계속해', '다음으로'
        ]
        if any(pattern in message_lower for pattern in continue_patterns):
            return 'continue'
        
        # 도움 요청 패턴
        help_patterns = [
            '도움', '도와', '힌트', '가이드', '안내', '방법'
        ]
        if any(pattern in message_lower for pattern in help_patterns):
            return 'help'
        
        return 'unknown'
    
    def should_provide_hint(self, state: TutorState) -> bool:
        """힌트 제공 여부 결정"""
        
        conversations = state.get('current_loop_conversations', [])
        
        # 최근 대화에서 어려움 표현 감지
        if len(conversations) >= 2:
            recent_messages = [
                conv.get('user_message', '') for conv in conversations[-2:]
            ]
            
            difficulty_indicators = [
                '어려워', '모르겠', '이해가 안', '힘들어', 
                '복잡해', '헷갈려', '잘 모르겠'
            ]
            
            for message in recent_messages:
                if any(indicator in message.lower() for indicator in difficulty_indicators):
                    return True
        
        return False
    
    def determine_difficulty_level(self, state: TutorState) -> Literal['easy', 'medium', 'hard']:
        """난이도 수준 결정"""
        
        user_level = state.get('user_level', 'low')
        user_type = state.get('user_type', 'beginner')
        current_chapter = state.get('current_chapter', 1)
        
        # 사용자 레벨과 타입에 따른 기본 난이도
        base_difficulty = {
            ('beginner', 'low'): 'easy',
            ('beginner', 'medium'): 'easy',
            ('beginner', 'high'): 'medium',
            ('business', 'low'): 'medium',
            ('business', 'medium'): 'medium',
            ('business', 'high'): 'hard'
        }
        
        difficulty = base_difficulty.get((user_type, user_level), 'medium')
        
        # 챕터에 따른 조정
        if current_chapter >= 3:
            if difficulty == 'easy':
                difficulty = 'medium'
            elif difficulty == 'medium':
                difficulty = 'hard'
        
        return difficulty
    
    def generate_learning_path(self, state: TutorState) -> List[Dict[str, str]]:
        """학습 경로 생성"""
        
        current_chapter = state.get('current_chapter', 1)
        progress_analysis = self.progress_analyzer.analyze_current_progress(state)
        
        learning_path = []
        
        # 현재 챕터의 남은 단계들
        chapter_flow = self.chapter_flow.get(current_chapter, ["theory", "quiz"])
        current_loop_progress = progress_analysis['current_loop_progress']
        
        for step in chapter_flow:
            if step == 'theory' and not current_loop_progress['has_theory']:
                learning_path.append({
                    'step': 'theory',
                    'description': '개념 학습',
                    'estimated_time': '10-15분'
                })
            elif step == 'quiz' and not current_loop_progress['has_quiz']:
                learning_path.append({
                    'step': 'quiz',
                    'description': '문제 풀이',
                    'estimated_time': '5-10분'
                })
            elif step == 'qna' and not current_loop_progress['has_qna']:
                learning_path.append({
                    'step': 'qna',
                    'description': '질문 답변',
                    'estimated_time': '5분'
                })
        
        # 다음 챕터들
        for next_chapter in range(current_chapter + 1, self.max_chapter + 1):
            learning_path.append({
                'step': f'chapter_{next_chapter}',
                'description': f'챕터 {next_chapter} 학습',
                'estimated_time': '30-45분'
            })
        
        return learning_path
    
    def should_show_progress(self, state: TutorState) -> bool:
        """진도 표시 여부 결정"""
        
        conversations = state.get('current_loop_conversations', [])
        
        # 일정 대화 수마다 진도 표시
        if len(conversations) > 0 and len(conversations) % 5 == 0:
            return True
        
        # 사용자가 진도 관련 질문을 한 경우
        user_message = state.get('user_message', '').lower()
        progress_keywords = ['진도', '진행', '얼마나', '상황', '현재']
        
        if any(keyword in user_message for keyword in progress_keywords):
            return True
        
        return False