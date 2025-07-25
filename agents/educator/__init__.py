# agents/educator/__init__.py
# TheoryEducator 에이전트 패키지

from typing import Dict, Any, Optional
from workflow.state_management import TutorState, StateManager
from .content_generator import ContentGenerator
from .level_adapter import LevelAdapter
from tools.content.theory_tool import enhanced_theory_generation_tool
from utils.langsmith_config import trace_agent_execution, end_agent_trace


class TheoryEducator:
    """개념 설명을 담당하는 교육자 에이전트"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.level_adapter = LevelAdapter()
        
        # 에이전트 메타데이터
        self.agent_name = "TheoryEducator"
        self.description = "사용자 레벨에 맞는 개념 설명을 제공하는 교육 전문 에이전트"
        self.version = "1.0.0"
        
        # 지원하는 챕터 정보
        self.supported_chapters = {
            1: "AI는 무엇인가?",
            2: "AI의 종류와 특징", 
            3: "프롬프트란 무엇인가?"
        }
    
    def execute(self, state: TutorState) -> TutorState:
        """TheoryEducator 메인 실행 로직"""
        
        # 1. 현재 상태 분석
        current_chapter = state.get('current_chapter', 1)
        user_level = state.get('user_level', 'medium')
        user_type = state.get('user_type', 'beginner')
        user_message = state.get('user_message', '')
        
        # LangSmith 추적 시작
        trace_inputs = {
            "user_id": state.get('user_id', ''),
            "user_message": user_message,
            "current_chapter": current_chapter,
            "user_level": user_level,
            "user_type": user_type
        }
        
        run_id = trace_agent_execution(
            agent_name=self.agent_name,
            inputs=trace_inputs,
            tags=["educator", "content_generation", f"chapter_{current_chapter}"]
        )
        
        try:
            
            # 2. 추가 컨텍스트 생성
            additional_context = self._generate_additional_context(state, user_message)
            
            # 3. 이론 콘텐츠 생성
            theory_result = enhanced_theory_generation_tool(state, additional_context)
            
            if theory_result['success']:
                # 4. 성공적인 콘텐츠 생성
                content = theory_result['content']
                ui_elements = theory_result.get('ui_elements')
                formatted_message = theory_result.get('formatted_message', '')
                
                # 5. 상태 업데이트
                state = StateManager.set_system_response(state, formatted_message, ui_elements)
                state = StateManager.update_ui_mode(state, 'chat')
                state['current_stage'] = 'theory_completed'
                
                # 6. 학습 진행 메타데이터 추가
                self._add_learning_metadata(state, content)
                
                # LangSmith 추적 종료 (성공)
                trace_outputs = {
                    "success": True,
                    "content_title": content.get('title', ''),
                    "content_sections": len(content.get('main_content', [])),
                    "examples_count": len(content.get('examples', [])),
                    "system_message_length": len(formatted_message),
                    "ui_mode": "chat"
                }
                end_agent_trace(run_id, trace_outputs)
                
            else:
                # 7. 오류 처리
                error_message = self._generate_error_message(theory_result, current_chapter)
                state = StateManager.set_system_response(state, error_message)
                state = StateManager.update_ui_mode(state, 'error')
                
                # LangSmith 추적 종료 (실패)
                trace_outputs = {
                    "success": False,
                    "error_message": error_message,
                    "ui_mode": "error"
                }
                end_agent_trace(run_id, trace_outputs, theory_result.get('error', ''))
            
            return state
            
        except Exception as e:
            # 예외 처리
            error_message = f"이론 설명 생성 중 오류가 발생했습니다: {str(e)}"
            state = StateManager.set_system_response(state, error_message)
            state = StateManager.update_ui_mode(state, 'error')
            
            # LangSmith 추적 종료 (예외)
            trace_outputs = {
                "success": False,
                "error_message": error_message,
                "ui_mode": "error"
            }
            end_agent_trace(run_id, trace_outputs, str(e))
            
            return state
    
    def _generate_additional_context(self, state: TutorState, user_message: str) -> str:
        """추가 컨텍스트 생성"""
        
        context_parts = []
        
        # 사용자 메시지에서 특정 요청 감지
        if user_message:
            message_lower = user_message.lower()
            
            if '예시' in message_lower or '사례' in message_lower:
                context_parts.append("사용자가 구체적인 예시를 요청함")
            
            if '쉽게' in message_lower or '간단히' in message_lower:
                context_parts.append("사용자가 쉬운 설명을 요청함")
            
            if '자세히' in message_lower or '상세히' in message_lower:
                context_parts.append("사용자가 상세한 설명을 요청함")
            
            if '비즈니스' in message_lower or '업무' in message_lower or '실무' in message_lower:
                context_parts.append("사용자가 비즈니스 관점의 설명을 요청함")
        
        # 학습 이력 기반 컨텍스트
        recent_loops = state.get('recent_loops_summary', [])
        if recent_loops:
            last_loop = recent_loops[-1]
            if 'key_concepts' in last_loop:
                context_parts.append(f"이전 학습 개념: {last_loop['key_concepts']}")
        
        # 현재 루프에서의 질문 패턴 분석
        current_conversations = state.get('current_loop_conversations', [])
        question_count = sum(1 for conv in current_conversations 
                           if conv.get('agent_name') == 'QnAResolver')
        
        if question_count > 2:
            context_parts.append("사용자가 많은 질문을 하고 있어 추가 설명이 필요할 수 있음")
        
        return " | ".join(context_parts) if context_parts else ""
    
    def _add_learning_metadata(self, state: TutorState, content: Dict[str, Any]):
        """학습 메타데이터 추가"""
        
        # 현재 루프에 학습 정보 추가
        if 'learning_metadata' not in state:
            state['learning_metadata'] = {}
        
        state['learning_metadata'].update({
            'theory_completed': True,
            'chapter': content['chapter'],
            'concepts_covered': content.get('key_concepts', []),
            'examples_provided': len(content.get('examples', [])),
            'user_level_adapted': content['metadata']['user_level'],
            'content_sections': len(content.get('main_content', []))
        })
    
    def _generate_error_message(self, theory_result: Dict[str, Any], chapter: int) -> str:
        """오류 메시지 생성"""
        
        chapter_title = self.supported_chapters.get(chapter, f"챕터 {chapter}")
        
        base_message = f"죄송합니다. {chapter_title} 설명을 준비하는 중에 문제가 발생했습니다."
        
        # 폴백 콘텐츠가 있는 경우
        if 'fallback_content' in theory_result:
            fallback = theory_result['fallback_content']
            fallback_message = f"\n\n기본 설명을 제공해드리겠습니다:\n\n{fallback['title']}\n{fallback['main_content'][0]['content']}"
            return base_message + fallback_message
        
        return base_message + "\n\n잠시 후 다시 시도해주시거나, 구체적인 질문을 해주세요."
    
    def can_handle_chapter(self, chapter: int) -> bool:
        """챕터 처리 가능 여부 확인"""
        return chapter in self.supported_chapters
    
    def get_chapter_info(self, chapter: int) -> Optional[Dict[str, Any]]:
        """챕터 정보 반환"""
        
        if not self.can_handle_chapter(chapter):
            return None
        
        # 챕터별 기본 정보 반환
        chapter_templates = self.content_generator.chapter_templates
        template = chapter_templates.get(chapter, {})
        
        return {
            'chapter': chapter,
            'title': template.get('title', f'챕터 {chapter}'),
            'objectives': template.get('objectives', []),
            'key_concepts': template.get('key_concepts', []),
            'estimated_time': self._estimate_learning_time(template),
            'difficulty_levels': ['low', 'medium', 'high'],
            'user_types': ['beginner', 'business']
        }
    
    def _estimate_learning_time(self, template: Dict[str, Any]) -> str:
        """학습 시간 추정"""
        
        objectives_count = len(template.get('objectives', []))
        concepts_count = len(template.get('key_concepts', []))
        
        # 간단한 시간 추정 로직
        base_time = 10  # 기본 10분
        additional_time = (objectives_count + concepts_count) * 2
        
        total_minutes = base_time + additional_time
        
        if total_minutes <= 15:
            return "10-15분"
        elif total_minutes <= 25:
            return "15-25분"
        else:
            return "25-35분"
    
    def generate_preview(self, chapter: int, user_level: str, user_type: str) -> Dict[str, Any]:
        """챕터 미리보기 생성"""
        
        try:
            # 기본 콘텐츠 생성 (컨텍스트 없이)
            content = self.content_generator.generate_theory_content(
                chapter, user_type, user_level, ""
            )
            
            # 미리보기용으로 축약
            preview = {
                'chapter': chapter,
                'title': content['title'],
                'introduction': content['introduction'][:200] + "...",
                'key_concepts': content.get('key_concepts', [])[:3],
                'example_count': len(content.get('examples', [])),
                'estimated_time': self._estimate_learning_time(
                    self.content_generator.chapter_templates.get(chapter, {})
                )
            }
            
            return {'success': True, 'preview': preview}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_preview': {
                    'chapter': chapter,
                    'title': self.supported_chapters.get(chapter, f'챕터 {chapter}'),
                    'introduction': '이 챕터에서는 기본 개념을 학습합니다.',
                    'estimated_time': '15-20분'
                }
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        
        return {
            'name': self.agent_name,
            'description': self.description,
            'version': self.version,
            'capabilities': [
                '사용자 레벨별 맞춤 설명',
                '다양한 예시 제공',
                '개념 시각화',
                '학습 진도 추적',
                '컨텍스트 기반 적응'
            ],
            'supported_chapters': self.supported_chapters,
            'supported_levels': ['low', 'medium', 'high'],
            'supported_types': ['beginner', 'business'],
            'dependencies': [
                'ContentGenerator',
                'LevelAdapter',
                'theory_generation_tool'
            ]
        }


# 패키지 레벨에서 사용할 수 있도록 export
__all__ = ['TheoryEducator', 'ContentGenerator', 'LevelAdapter']