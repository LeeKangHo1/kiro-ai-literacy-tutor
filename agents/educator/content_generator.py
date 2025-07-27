# agents/educator/content_generator_new.py
# 리팩토링된 콘텐츠 생성기 - 챕터별 분리

from typing import Dict, List, Any, Optional
from workflow.state_management import TutorState, StateManager
from .chapters.chapter1_ai_basics import Chapter1AIBasics
from .chapters.chapter2_llm import Chapter2LLM
from .chapters.chapter3_prompts import Chapter3Prompts
from .chapters.chapter4_chatgpt import Chapter4ChatGPT
from .chapters.chapter5_literacy import Chapter5Literacy


class ContentGenerator:
    """이론 콘텐츠 생성을 담당하는 클래스 (리팩토링 버전)"""
    
    def __init__(self):
        # 챕터별 생성기 인스턴스
        self.chapter_generators = {
            1: Chapter1AIBasics(),
            2: Chapter2LLM(),
            3: Chapter3Prompts(),
            4: Chapter4ChatGPT(),
            5: Chapter5Literacy()
        }
        
        # 레거시 템플릿 (모든 챕터가 분리되어 더 이상 필요 없음)
        self.legacy_templates = {}
        
        # 난이도별 설명 스타일
        self.explanation_styles = {
            'low': {
                'tone': '친근하고 쉬운',
                'vocabulary': '일상 용어 중심',
                'examples': '생활 밀착형',
                'length': '간결하고 핵심적'
            },
            'medium': {
                'tone': '체계적이고 명확한',
                'vocabulary': '기술 용어 + 설명',
                'examples': '실무 중심',
                'length': '적당한 상세도'
            },
            'high': {
                'tone': '전문적이고 심화된',
                'vocabulary': '기술 용어 활용',
                'examples': '고급 사례',
                'length': '상세하고 포괄적'
            }
        }
    
    def generate_theory_content(self, chapter: int, user_type: str, 
                               user_level: str, context: str = "") -> Dict[str, Any]:
        """이론 콘텐츠 생성"""
        
        # 새로운 챕터별 생성기 사용
        if chapter in self.chapter_generators:
            generator = self.chapter_generators[chapter]
            return generator.generate_content(user_type, user_level, context)
        
        # 레거시 템플릿 사용 (챕터 5만)
        elif chapter in self.legacy_templates:
            return self._generate_legacy_content(chapter, user_type, user_level, context)
        
        # 폴백 콘텐츠
        else:
            return self._generate_fallback_content(chapter, user_type, user_level)
    
    def _generate_legacy_content(self, chapter: int, user_type: str, 
                                user_level: str, context: str) -> Dict[str, Any]:
        """레거시 템플릿을 사용한 콘텐츠 생성"""
        template = self.legacy_templates[chapter]
        style = self.explanation_styles.get(user_level, self.explanation_styles['medium'])
        
        content = {
            'chapter': chapter,
            'title': template['title'],
            'introduction': self._generate_legacy_introduction(template, user_type, user_level),
            'main_content': self._generate_legacy_main_content(template, user_type, user_level, context),
            'examples': self._select_legacy_examples(template, user_type, user_level),
            'key_points': self._generate_legacy_key_points(template, user_level),
            'next_steps': self._generate_legacy_next_steps(template, user_type),
            'metadata': {
                'user_type': user_type,
                'user_level': user_level,
                'style': style,
                'generated_at': self._get_current_timestamp()
            }
        }
        
        return content
    
    def _generate_legacy_introduction(self, template: Dict[str, Any], 
                                     user_type: str, user_level: str) -> str:
        """레거시 도입부 생성"""
        title = template['title']
        
        if user_type == 'beginner':
            if user_level == 'low':
                return f"안녕하세요! 오늘은 '{title}'에 대해 쉽고 재미있게 알아보겠습니다. 어려운 용어는 최대한 피하고, 일상생활에서 볼 수 있는 예시들로 설명해드릴게요."
            else:
                return f"'{title}'에 대해 체계적으로 학습해보겠습니다. 기본 개념부터 차근차근 설명하여 확실히 이해할 수 있도록 도와드리겠습니다."
        
        else:  # business
            if user_level == 'low':
                return f"비즈니스 관점에서 '{title}'를 살펴보겠습니다. 실무에 바로 적용할 수 있는 내용들을 중심으로 설명해드리겠습니다."
            else:
                return f"'{title}'에 대한 심화 학습을 시작하겠습니다. 비즈니스 활용 사례와 실전 적용 방법을 포함하여 포괄적으로 다루겠습니다."
    
    def _generate_legacy_main_content(self, template: Dict[str, Any], 
                                     user_type: str, user_level: str, context: str) -> List[Dict[str, str]]:
        """레거시 메인 콘텐츠 생성"""
        objectives = template['objectives']
        content_sections = []
        
        # 각 학습 목표별로 섹션 생성
        for i, objective in enumerate(objectives):
            section = {
                'section_number': i + 1,
                'title': objective,
                'content': f"{objective}에 대한 상세한 설명이 여기에 들어갑니다. 사용자 레벨({user_level})과 타입({user_type})에 맞춰 조정된 내용입니다.",
                'concepts': []
            }
            content_sections.append(section)
        
        return content_sections
    
    def _select_legacy_examples(self, template: Dict[str, Any], 
                               user_type: str, user_level: str) -> List[str]:
        """레거시 예시 선택"""
        examples = template.get('examples', {})
        user_examples = examples.get(user_type, [])
        
        # 레벨에 따라 예시 개수 조정
        if user_level == 'low':
            return user_examples[:2]  # 간단히 2개만
        elif user_level == 'medium':
            return user_examples[:3]  # 3개
        else:
            return user_examples  # 모든 예시
    
    def _generate_legacy_key_points(self, template: Dict[str, Any], user_level: str) -> List[str]:
        """레거시 핵심 포인트 생성"""
        key_concepts = template.get('key_concepts', [])
        objectives = template.get('objectives', [])
        
        key_points = []
        
        # 주요 개념들을 핵심 포인트로 변환
        for concept in key_concepts[:3]:  # 최대 3개
            if user_level == 'low':
                key_points.append(f"💡 {concept}의 기본 개념 이해")
            else:
                key_points.append(f"📌 {concept}의 정의와 특징 파악")
        
        # 학습 목표를 핵심 포인트로 추가
        for objective in objectives[:2]:  # 최대 2개
            key_points.append(f"🎯 {objective}")
        
        return key_points
    
    def _generate_legacy_next_steps(self, template: Dict[str, Any], user_type: str) -> List[str]:
        """레거시 다음 단계 제안"""
        if user_type == 'beginner':
            return [
                "🤔 궁금한 점이 있으면 언제든 질문해보세요",
                "📝 학습한 내용을 확인하는 퀴즈를 풀어보세요",
                "💡 실생활에서 관련 사례를 찾아보세요"
            ]
        else:  # business
            return [
                "💼 비즈니스 적용 방안을 구체적으로 생각해보세요",
                "📊 실무 사례를 통한 문제 해결 연습을 해보세요",
                "🔍 심화 학습을 위한 추가 질문을 해보세요"
            ]
    
    def generate_theory_with_ui(self, state: TutorState) -> TutorState:
        """UI 모드 관리와 함께 이론 콘텐츠 생성"""
        try:
            # 사용자 입력 수신 이벤트 처리 (로딩 상태로 전환)
            state = StateManager.handle_ui_transition(
                state, "user_input_received", "theory_educator"
            )
            
            # 이론 콘텐츠 생성
            content = self.generate_theory_content(
                state['current_chapter'],
                state['user_type'],
                state['user_level'],
                state.get('user_message', '')
            )
            
            # 시스템 메시지 생성
            system_message = self._format_content_for_display(content)
            
            # 상태 업데이트
            state['system_message'] = system_message
            state['current_stage'] = 'theory_complete'
            
            # 대화 기록 추가
            state = StateManager.add_conversation(
                state, 
                "theory_educator",
                state.get('user_message', ''),
                system_message,
                {'content_data': content}
            )
            
            # UI 상태 업데이트 (에이전트 응답 준비 완료)
            ui_context = {
                'title': content['title'],
                'description': '개념 설명이 완료되었습니다. 질문하거나 문제를 풀어보세요.',
                'show_progress': True,
                'progress_value': self._calculate_progress(state),
                'content_type': 'theory'
            }
            
            state = StateManager.handle_ui_transition(
                state, "agent_response_ready", "theory_educator", ui_context
            )
            
        except Exception as e:
            # 오류 처리
            state['system_message'] = f"이론 콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
            state = StateManager.handle_ui_transition(
                state, "error_occurred", "theory_educator", 
                {'error_message': str(e)}
            )
        
        return state
    
    def _generate_fallback_content(self, chapter: int, user_type: str, user_level: str) -> Dict[str, Any]:
        """기본 콘텐츠 생성 (템플릿이 없는 경우)"""
        return {
            'chapter': chapter,
            'title': f'챕터 {chapter} 학습',
            'introduction': f'챕터 {chapter}의 내용을 학습해보겠습니다.',
            'main_content': [{
                'section_number': 1,
                'title': '기본 개념',
                'content': f'챕터 {chapter}의 기본 개념에 대해 설명합니다.',
                'concepts': []
            }],
            'examples': ['예시 1', '예시 2'],
            'key_points': ['핵심 포인트 1', '핵심 포인트 2'],
            'next_steps': ['다음 단계 1', '다음 단계 2'],
            'metadata': {
                'user_type': user_type,
                'user_level': user_level,
                'is_fallback': True,
                'generated_at': self._get_current_timestamp()
            }
        }
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """생성된 콘텐츠 유효성 검증"""
        required_fields = ['chapter', 'title', 'introduction', 'main_content', 'examples']
        
        for field in required_fields:
            if field not in content:
                return False
        
        # main_content가 리스트이고 비어있지 않은지 확인
        if not isinstance(content['main_content'], list) or not content['main_content']:
            return False
        
        return True
    
    def _format_content_for_display(self, content: Dict[str, Any]) -> str:
        """콘텐츠를 표시용 텍스트로 포맷팅"""
        formatted_parts = []
        
        # 제목과 도입부
        formatted_parts.append(f"# {content['title']}\n")
        formatted_parts.append(f"{content['introduction']}\n")
        
        # 메인 콘텐츠
        for section in content['main_content']:
            formatted_parts.append(f"## {section['title']}\n")
            formatted_parts.append(f"{section['content']}\n")
        
        # 예시
        if content['examples']:
            formatted_parts.append("## 📚 주요 예시\n")
            for i, example in enumerate(content['examples'], 1):
                formatted_parts.append(f"{i}. {example}\n")
        
        # 핵심 포인트
        if content['key_points']:
            formatted_parts.append("## 🎯 핵심 포인트\n")
            for point in content['key_points']:
                formatted_parts.append(f"• {point}\n")
        
        # 다음 단계
        if content['next_steps']:
            formatted_parts.append("## 🚀 다음 단계\n")
            for step in content['next_steps']:
                formatted_parts.append(f"• {step}\n")
        
        return "\n".join(formatted_parts)
    
    def _calculate_progress(self, state: TutorState) -> int:
        """학습 진행률 계산"""
        # 현재 챕터와 단계를 기반으로 진행률 계산
        chapter = state['current_chapter']
        stage = state['current_stage']
        
        # 간단한 진행률 계산 로직
        base_progress = (chapter - 1) * 25  # 챕터당 25%
        
        stage_progress = {
            'theory': 5,
            'theory_complete': 10,
            'quiz': 15,
            'feedback': 20,
            'complete': 25
        }
        
        current_stage_progress = stage_progress.get(stage, 0)
        
        return min(100, base_progress + current_stage_progress)