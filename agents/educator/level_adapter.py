# agents/educator/level_adapter.py
# 사용자 레벨별 콘텐츠 적응 로직 구현

from typing import Dict, List, Any, Optional
from workflow.state_management import TutorState


class LevelAdapter:
    """사용자 레벨에 따른 콘텐츠 적응을 담당하는 클래스"""
    
    def __init__(self):
        # 레벨별 특성 정의
        self.level_characteristics = {
            'low': {
                'vocabulary_complexity': 'simple',
                'explanation_depth': 'basic',
                'example_count': 2,
                'technical_terms': 'minimal',
                'interaction_style': 'friendly',
                'content_length': 'short',
                'visual_aids': 'emoji_heavy'
            },
            'medium': {
                'vocabulary_complexity': 'moderate',
                'explanation_depth': 'detailed',
                'example_count': 3,
                'technical_terms': 'explained',
                'interaction_style': 'professional',
                'content_length': 'medium',
                'visual_aids': 'structured'
            },
            'high': {
                'vocabulary_complexity': 'advanced',
                'explanation_depth': 'comprehensive',
                'example_count': 4,
                'technical_terms': 'frequent',
                'interaction_style': 'expert',
                'content_length': 'detailed',
                'visual_aids': 'minimal'
            }
        }
        
        # 사용자 타입별 특성
        self.type_characteristics = {
            'beginner': {
                'focus': 'understanding',
                'examples': 'daily_life',
                'approach': 'step_by_step',
                'motivation': 'curiosity'
            },
            'business': {
                'focus': 'application',
                'examples': 'business_cases',
                'approach': 'practical',
                'motivation': 'efficiency'
            }
        }
    
    def adapt_content(self, content: Dict[str, Any], state: TutorState) -> Dict[str, Any]:
        """사용자 레벨에 맞게 콘텐츠 적응"""
        
        user_level = state.get('user_level', 'medium')
        user_type = state.get('user_type', 'beginner')
        
        # 기본 콘텐츠 복사
        adapted_content = content.copy()
        
        # 레벨별 적응
        adapted_content = self._adapt_by_level(adapted_content, user_level)
        
        # 타입별 적응
        adapted_content = self._adapt_by_type(adapted_content, user_type)
        
        # 개인화 적응
        adapted_content = self._personalize_content(adapted_content, state)
        
        return adapted_content
    
    def _adapt_by_level(self, content: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """레벨에 따른 콘텐츠 적응"""
        
        level_char = self.level_characteristics.get(user_level, self.level_characteristics['medium'])
        
        # 제목 적응
        content['title'] = self._adapt_title(content['title'], level_char)
        
        # 도입부 적응
        content['introduction'] = self._adapt_introduction(content['introduction'], level_char)
        
        # 메인 콘텐츠 적응
        content['main_content'] = self._adapt_main_content(content['main_content'], level_char)
        
        # 예시 개수 조정
        content['examples'] = self._adjust_examples(content['examples'], level_char)
        
        # 핵심 포인트 적응
        if 'key_points' in content:
            content['key_points'] = self._adapt_key_points(content['key_points'], level_char)
        
        return content
    
    def _adapt_by_type(self, content: Dict[str, Any], user_type: str) -> Dict[str, Any]:
        """사용자 타입에 따른 콘텐츠 적응"""
        
        type_char = self.type_characteristics.get(user_type, self.type_characteristics['beginner'])
        
        # 예시를 타입에 맞게 조정
        content['examples'] = self._adapt_examples_by_type(content['examples'], type_char)
        
        # 다음 단계를 타입에 맞게 조정
        if 'next_steps' in content:
            content['next_steps'] = self._adapt_next_steps_by_type(content['next_steps'], type_char)
        
        return content
    
    def _personalize_content(self, content: Dict[str, Any], state: TutorState) -> Dict[str, Any]:
        """개인화된 콘텐츠 적응"""
        
        # 학습 이력 기반 적응
        recent_loops = state.get('recent_loops_summary', [])
        current_conversations = state.get('current_loop_conversations', [])
        
        # 반복 학습 감지
        if self._detect_repeated_concepts(recent_loops, content):
            content = self._add_reinforcement_content(content)
        
        # 어려움 감지
        if self._detect_difficulty(current_conversations):
            content = self._simplify_content(content)
        
        # 빠른 이해 감지
        if self._detect_quick_understanding(current_conversations):
            content = self._add_advanced_content(content)
        
        return content
    
    def _adapt_title(self, title: str, level_char: Dict[str, Any]) -> str:
        """제목 적응"""
        
        visual_style = level_char['visual_aids']
        
        if visual_style == 'emoji_heavy':
            # 이모지 추가
            emoji_map = {
                'AI': '🤖',
                '프롬프트': '💬',
                '학습': '📚',
                '종류': '🔍',
                '특징': '⭐'
            }
            
            for keyword, emoji in emoji_map.items():
                if keyword in title and emoji not in title:
                    title = f"{emoji} {title}"
                    break
        
        return title
    
    def _adapt_introduction(self, introduction: str, level_char: Dict[str, Any]) -> str:
        """도입부 적응"""
        
        interaction_style = level_char['interaction_style']
        
        if interaction_style == 'friendly':
            # 친근한 톤으로 변경
            if not introduction.startswith('안녕'):
                introduction = f"안녕하세요! {introduction}"
            
            # 격려 문구 추가
            if '함께' not in introduction:
                introduction += " 함께 차근차근 알아보아요!"
        
        elif interaction_style == 'expert':
            # 전문적인 톤으로 변경
            introduction = introduction.replace('쉽게', '체계적으로')
            introduction = introduction.replace('재미있게', '심도 있게')
        
        return introduction
    
    def _adapt_main_content(self, main_content: List[Dict[str, str]], 
                           level_char: Dict[str, Any]) -> List[Dict[str, str]]:
        """메인 콘텐츠 적응"""
        
        depth = level_char['explanation_depth']
        length = level_char['content_length']
        
        adapted_content = []
        
        for section in main_content:
            adapted_section = section.copy()
            
            # 내용 길이 조정
            if length == 'short':
                adapted_section['content'] = self._shorten_content(section['content'])
            elif length == 'detailed':
                adapted_section['content'] = self._expand_content(section['content'])
            
            # 설명 깊이 조정
            if depth == 'basic':
                adapted_section['content'] = self._simplify_explanation(adapted_section['content'])
            elif depth == 'comprehensive':
                adapted_section['content'] = self._deepen_explanation(adapted_section['content'])
            
            adapted_content.append(adapted_section)
        
        return adapted_content
    
    def _adjust_examples(self, examples: List[str], level_char: Dict[str, Any]) -> List[str]:
        """예시 개수 조정"""
        
        target_count = level_char['example_count']
        
        if len(examples) > target_count:
            return examples[:target_count]
        elif len(examples) < target_count:
            # 부족한 경우 기본 예시 추가
            additional_examples = [
                f"추가 예시 {i+1}" for i in range(target_count - len(examples))
            ]
            return examples + additional_examples
        
        return examples
    
    def _adapt_key_points(self, key_points: List[str], level_char: Dict[str, Any]) -> List[str]:
        """핵심 포인트 적응"""
        
        visual_style = level_char['visual_aids']
        
        if visual_style == 'emoji_heavy':
            # 이모지가 없는 포인트에 추가
            adapted_points = []
            emojis = ['💡', '📌', '🎯', '⭐', '🔑']
            
            for i, point in enumerate(key_points):
                if not any(emoji in point for emoji in emojis):
                    emoji = emojis[i % len(emojis)]
                    point = f"{emoji} {point}"
                adapted_points.append(point)
            
            return adapted_points
        
        return key_points
    
    def _adapt_examples_by_type(self, examples: List[str], type_char: Dict[str, Any]) -> List[str]:
        """타입별 예시 적응"""
        
        example_focus = type_char['examples']
        
        if example_focus == 'business_cases':
            # 비즈니스 사례로 변환
            business_examples = []
            for example in examples:
                if '스마트폰' in example:
                    business_examples.append('기업용 음성인식 시스템')
                elif '넷플릭스' in example:
                    business_examples.append('고객 행동 분석 시스템')
                elif '내비게이션' in example:
                    business_examples.append('물류 최적화 시스템')
                else:
                    business_examples.append(example)
            return business_examples
        
        return examples
    
    def _adapt_next_steps_by_type(self, next_steps: List[str], type_char: Dict[str, Any]) -> List[str]:
        """타입별 다음 단계 적응"""
        
        focus = type_char['focus']
        
        if focus == 'application':
            # 실용적인 다음 단계로 변경
            practical_steps = []
            for step in next_steps:
                if '질문' in step:
                    practical_steps.append('💼 실무 적용 방안에 대해 질문해보세요')
                elif '퀴즈' in step:
                    practical_steps.append('📊 비즈니스 사례 문제를 풀어보세요')
                elif '사례' in step:
                    practical_steps.append('🔍 업계별 적용 사례를 찾아보세요')
                else:
                    practical_steps.append(step)
            return practical_steps
        
        return next_steps
    
    def _detect_repeated_concepts(self, recent_loops: List[Dict[str, str]], 
                                 content: Dict[str, Any]) -> bool:
        """반복 학습 개념 감지"""
        
        current_concepts = content.get('key_concepts', [])
        
        for loop in recent_loops[-2:]:  # 최근 2개 루프 확인
            loop_concepts = loop.get('key_concepts', '').split(', ')
            
            # 공통 개념이 있는지 확인
            if any(concept in loop_concepts for concept in current_concepts):
                return True
        
        return False
    
    def _detect_difficulty(self, conversations: List[Dict[str, Any]]) -> bool:
        """학습 어려움 감지"""
        
        difficulty_indicators = [
            '어려워', '모르겠', '이해가 안', '복잡해', '헷갈려'
        ]
        
        recent_messages = conversations[-3:] if len(conversations) >= 3 else conversations
        
        for conv in recent_messages:
            user_message = conv.get('user_message', '').lower()
            if any(indicator in user_message for indicator in difficulty_indicators):
                return True
        
        return False
    
    def _detect_quick_understanding(self, conversations: List[Dict[str, Any]]) -> bool:
        """빠른 이해 감지"""
        
        understanding_indicators = [
            '이해했', '알겠', '쉽네', '간단하', '더 어려운', '심화'
        ]
        
        recent_messages = conversations[-2:] if len(conversations) >= 2 else conversations
        
        for conv in recent_messages:
            user_message = conv.get('user_message', '').lower()
            if any(indicator in user_message for indicator in understanding_indicators):
                return True
        
        return False
    
    def _add_reinforcement_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """강화 학습 콘텐츠 추가"""
        
        content['introduction'] += "\n\n🔄 이전에 학습한 내용과 연결하여 더 깊이 이해해보겠습니다."
        
        return content
    
    def _simplify_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """콘텐츠 단순화"""
        
        # 메인 콘텐츠 단순화
        for section in content['main_content']:
            section['content'] = self._simplify_explanation(section['content'])
        
        # 예시 개수 줄이기
        content['examples'] = content['examples'][:2]
        
        return content
    
    def _add_advanced_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """고급 콘텐츠 추가"""
        
        # 추가 섹션 생성
        advanced_section = {
            'section_number': len(content['main_content']) + 1,
            'title': '🚀 심화 학습',
            'content': '더 깊이 있는 내용을 살펴보겠습니다.',
            'concepts': []
        }
        
        content['main_content'].append(advanced_section)
        
        return content
    
    def _shorten_content(self, text: str) -> str:
        """텍스트 단축"""
        
        # 문장을 나누고 핵심 문장만 유지
        sentences = text.split('.')
        core_sentences = sentences[:2] if len(sentences) > 2 else sentences
        
        return '.'.join(core_sentences) + '.' if core_sentences else text
    
    def _expand_content(self, text: str) -> str:
        """텍스트 확장"""
        
        # 기본 텍스트에 추가 설명 붙이기
        expanded = text
        
        if '정의:' in text:
            expanded += "\n\n**상세 설명**: 이 개념은 실무에서 다양하게 활용되며, 구체적인 적용 사례를 통해 더 잘 이해할 수 있습니다."
        
        return expanded
    
    def _simplify_explanation(self, text: str) -> str:
        """설명 단순화"""
        
        # 복잡한 용어를 쉬운 용어로 대체
        replacements = {
            '알고리즘': '방법',
            '최적화': '개선',
            '파라미터': '설정값',
            '인터페이스': '연결부분',
            '아키텍처': '구조'
        }
        
        simplified = text
        for complex_term, simple_term in replacements.items():
            simplified = simplified.replace(complex_term, simple_term)
        
        return simplified
    
    def _deepen_explanation(self, text: str) -> str:
        """설명 심화"""
        
        # 기술적 세부사항 추가
        if '머신러닝' in text:
            text += "\n\n**기술적 세부사항**: 머신러닝은 통계학적 방법론을 기반으로 하며, 경사하강법, 정규화, 교차검증 등의 기법을 활용합니다."
        
        return text