# agents/supervisor/__init__.py
# LearningSupervisor 에이전트 패키지

from typing import Dict, Any, Optional, List
from workflow.state_management import TutorState, StateManager
from .progress_analyzer import ProgressAnalyzer
from .loop_manager import LoopManager
from .decision_maker import DecisionMaker
from utils.langsmith_config import trace_agent_execution, end_agent_trace


class LearningSupervisor:
    """학습 진행을 총괄하는 슈퍼바이저 에이전트"""
    
    def __init__(self):
        self.progress_analyzer = ProgressAnalyzer()
        self.loop_manager = LoopManager()
        self.decision_maker = DecisionMaker()
        
        # 에이전트 메타데이터
        self.agent_name = "LearningSupervisor"
        self.description = "학습 진행을 총괄하고 다음 단계를 결정하는 슈퍼바이저"
        self.version = "1.0.0"
    
    def execute(self, state: TutorState) -> TutorState:
        """LearningSupervisor 메인 실행 로직"""
        
        # LangSmith 추적 시작
        trace_inputs = {
            "user_id": state.get('user_id', ''),
            "user_message": state.get('user_message', ''),
            "current_chapter": state.get('current_chapter', 1),
            "current_stage": state.get('current_stage', ''),
            "user_level": state.get('user_level', ''),
            "user_type": state.get('user_type', '')
        }
        
        run_id = trace_agent_execution(
            agent_name=self.agent_name,
            inputs=trace_inputs,
            tags=["supervisor", "decision_making"]
        )
        
        try:
            # 1. 현재 진도 분석
            progress_analysis = self.progress_analyzer.analyze_current_progress(state)
            
            # 2. 루프 관리 (필요시 완료 처리)
            if self.loop_manager.should_complete_current_loop(state):
                state = self.loop_manager.complete_current_loop(state)
                
                # 루프 완료 메시지 생성
                completion_message = self._generate_loop_completion_message(progress_analysis)
                state = StateManager.set_system_response(state, completion_message)
            
            # 3. 다음 단계 결정
            next_step_decision = self.decision_maker.decide_next_step(state)
            
            # 4. 상태 업데이트
            state = self._update_state_based_on_decision(state, next_step_decision)
            
            # 5. 응답 메시지 생성 (루프 완료 메시지가 없는 경우에만)
            if not state.get('system_message'):
                response_message = self._generate_response_message(
                    state, progress_analysis, next_step_decision
                )
                state = StateManager.set_system_response(state, response_message)
            
            # 6. UI 요소 설정
            ui_elements = self._generate_ui_elements(state, next_step_decision)
            if ui_elements:
                state['ui_elements'] = ui_elements
            
            # LangSmith 추적 종료 (성공)
            trace_outputs = {
                "system_message": state.get('system_message', ''),
                "current_stage": state.get('current_stage', ''),
                "ui_mode": state.get('ui_mode', ''),
                "next_step": next_step_decision.get('next_step', ''),
                "decision_reason": next_step_decision.get('reason', '')
            }
            end_agent_trace(run_id, trace_outputs)
            
            return state
            
        except Exception as e:
            # 오류 처리
            error_message = f"LearningSupervisor 실행 중 오류가 발생했습니다: {str(e)}"
            state = StateManager.set_system_response(state, error_message)
            state['ui_mode'] = 'error'
            
            # LangSmith 추적 종료 (오류)
            trace_outputs = {
                "system_message": error_message,
                "ui_mode": "error"
            }
            end_agent_trace(run_id, trace_outputs, str(e))
            
            return state
    
    def _generate_loop_completion_message(self, progress_analysis: Dict[str, Any]) -> str:
        """루프 완료 메시지 생성"""
        
        current_loop_progress = progress_analysis['current_loop_progress']
        completion_status = progress_analysis['completion_status']
        
        message_parts = ["🎉 학습 루프가 완료되었습니다!"]
        
        # 활동 요약
        activities = []
        if current_loop_progress['has_theory']:
            activities.append("개념 학습")
        if current_loop_progress['has_quiz']:
            activities.append("문제 풀이")
        if current_loop_progress['has_qna']:
            activities.append("질문 답변")
        
        if activities:
            message_parts.append(f"✅ 완료된 활동: {', '.join(activities)}")
        
        # 진도 정보
        completion_percentage = completion_status['completion_percentage']
        message_parts.append(f"📊 현재 챕터 진도: {completion_percentage:.0f}%")
        
        # 추천사항
        recommendations = progress_analysis['recommendations']
        if recommendations:
            message_parts.append(f"💡 추천: {recommendations[0]}")
        
        return "\n".join(message_parts)
    
    def _update_state_based_on_decision(self, state: TutorState, 
                                       decision: Dict[str, Any]) -> TutorState:
        """결정에 따른 상태 업데이트"""
        
        # 단계 업데이트
        if 'stage' in decision:
            state['current_stage'] = decision['stage']
        
        # UI 모드 업데이트
        if 'ui_mode' in decision:
            state = StateManager.update_ui_mode(state, decision['ui_mode'])
        
        # 챕터 진행
        if decision.get('next_step') == 'advance_chapter':
            new_chapter = decision.get('new_chapter', state.get('current_chapter', 1) + 1)
            state['current_chapter'] = new_chapter
            state['current_stage'] = 'theory'
            
            # 새 루프 시작
            state = self.loop_manager.start_new_loop(state, f"chapter_{new_chapter}_start")
        
        # 과정 완료
        elif decision.get('next_step') == 'course_complete':
            state['current_stage'] = 'completed'
            state = StateManager.update_ui_mode(state, 'chat')
        
        return state
    
    def _generate_response_message(self, state: TutorState, 
                                  progress_analysis: Dict[str, Any],
                                  decision: Dict[str, Any]) -> str:
        """응답 메시지 생성"""
        
        next_step = decision.get('next_step', 'continue')
        reason = decision.get('reason', '')
        current_chapter = state.get('current_chapter', 1)
        
        # 다음 단계별 메시지
        if next_step == 'theory_educator':
            return f"📚 챕터 {current_chapter}의 개념을 학습해보겠습니다. {reason}"
        
        elif next_step == 'quiz_generator':
            return f"📝 학습한 내용을 확인하기 위해 문제를 출제하겠습니다. {reason}"
        
        elif next_step == 'qna_resolver':
            return f"❓ 질문에 답변해드리겠습니다. {reason}"
        
        elif next_step == 'advance_chapter':
            new_chapter = decision.get('new_chapter', current_chapter + 1)
            return f"🎯 챕터 {current_chapter} 완료! 이제 챕터 {new_chapter}로 진행하겠습니다."
        
        elif next_step == 'course_complete':
            return "🏆 축하합니다! 모든 학습 과정을 완료하셨습니다. AI 활용 능력이 크게 향상되었을 것입니다."
        
        elif next_step == 'continue_learning':
            return f"📖 학습을 계속 진행하겠습니다. {reason}"
        
        else:
            # 기본 메시지
            completion_status = progress_analysis['completion_status']
            progress_percent = completion_status['completion_percentage']
            
            return f"현재 챕터 {current_chapter} 진도: {progress_percent:.0f}%. 어떤 도움이 필요하신가요?"
    
    def _generate_ui_elements(self, state: TutorState, 
                             decision: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """UI 요소 생성"""
        
        next_step = decision.get('next_step', '')
        
        # 진도 표시가 필요한 경우
        if self.decision_maker.should_show_progress(state):
            progress_analysis = self.progress_analyzer.analyze_current_progress(state)
            completion_status = progress_analysis['completion_status']
            
            return {
                'type': 'progress_display',
                'chapter': state.get('current_chapter', 1),
                'progress_percentage': completion_status['completion_percentage'],
                'completed_activities': self._get_completed_activities(progress_analysis),
                'next_activities': self._get_next_activities(state)
            }
        
        # 학습 경로 표시
        elif next_step == 'advance_chapter':
            learning_path = self.decision_maker.generate_learning_path(state)
            
            return {
                'type': 'learning_path',
                'current_chapter': state.get('current_chapter', 1),
                'path': learning_path[:3]  # 다음 3단계만 표시
            }
        
        # 과정 완료 축하
        elif next_step == 'course_complete':
            loop_stats = self.loop_manager.get_loop_statistics(state)
            
            return {
                'type': 'completion_celebration',
                'total_loops': loop_stats['total_loops'],
                'total_conversations': loop_stats['total_conversations'],
                'most_used_agent': loop_stats['most_used_agent'],
                'consistency_score': loop_stats['learning_consistency']
            }
        
        return None
    
    def _get_completed_activities(self, progress_analysis: Dict[str, Any]) -> List[str]:
        """완료된 활동 목록 반환"""
        
        current_loop_progress = progress_analysis['current_loop_progress']
        activities = []
        
        if current_loop_progress['has_theory']:
            activities.append("개념 학습")
        if current_loop_progress['has_quiz']:
            activities.append("문제 풀이")
        if current_loop_progress['has_qna']:
            activities.append("질문 답변")
        
        return activities
    
    def _get_next_activities(self, state: TutorState) -> List[str]:
        """다음 활동 목록 반환"""
        
        learning_path = self.decision_maker.generate_learning_path(state)
        return [step['description'] for step in learning_path[:2]]  # 다음 2개 활동
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        
        return {
            'name': self.agent_name,
            'description': self.description,
            'version': self.version,
            'capabilities': [
                '학습 진도 분석',
                '루프 관리',
                '다음 단계 결정',
                '학습 경로 생성',
                '진도 추적'
            ],
            'dependencies': [
                'ProgressAnalyzer',
                'LoopManager', 
                'DecisionMaker'
            ]
        }


# 패키지 레벨에서 사용할 수 있도록 export
__all__ = ['LearningSupervisor', 'ProgressAnalyzer', 'LoopManager', 'DecisionMaker']