# agents/educator/chapters/base_chapter.py
# 챕터 기본 클래스 및 공통 기능

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime


class BaseChapter(ABC):
    """챕터 기본 클래스"""
    
    def __init__(self):
        self.chapter_id = None
        self.title = None
        self.objectives = []
        self.key_concepts = []
        self.examples = {'beginner': [], 'business': []}
        
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
    
    @abstractmethod
    def get_chapter_template(self) -> Dict[str, Any]:
        """챕터 템플릿 반환"""
        pass
    
    @abstractmethod
    def generate_section_content(self, objective: str, key_concepts: List[str], 
                                user_type: str, user_level: str) -> str:
        """섹션별 콘텐츠 생성"""
        pass
    
    def generate_introduction(self, user_type: str, user_level: str) -> str:
        """도입부 생성"""
        title = self.title
        
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
    
    def generate_section_title(self, objective: str, user_level: str) -> str:
        """섹션 제목 생성 - 각 챕터에서 오버라이드 가능"""
        return objective
    
    def select_examples(self, user_type: str, user_level: str) -> List[str]:
        """사용자 타입에 맞는 예시 선택"""
        examples = self.examples.get(user_type, [])
        
        # 레벨에 따라 예시 개수 조정
        if user_level == 'low':
            return examples[:2]  # 간단히 2개만
        elif user_level == 'medium':
            return examples[:3]  # 3개
        else:
            return examples  # 모든 예시
    
    def generate_key_points(self, user_level: str) -> List[str]:
        """핵심 포인트 생성"""
        key_points = []
        
        # 주요 개념들을 핵심 포인트로 변환
        for concept in self.key_concepts[:3]:  # 최대 3개
            if user_level == 'low':
                key_points.append(f"💡 {concept}의 기본 개념 이해")
            else:
                key_points.append(f"📌 {concept}의 정의와 특징 파악")
        
        # 학습 목표를 핵심 포인트로 추가
        for objective in self.objectives[:2]:  # 최대 2개
            key_points.append(f"🎯 {objective}")
        
        return key_points
    
    def generate_next_steps(self, user_type: str) -> List[str]:
        """다음 단계 제안"""
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
    
    def generate_main_content(self, user_type: str, user_level: str, context: str = "") -> List[Dict[str, str]]:
        """메인 콘텐츠 생성"""
        content_sections = []
        
        # 각 학습 목표별로 섹션 생성
        for i, objective in enumerate(self.objectives):
            section = {
                'section_number': i + 1,
                'title': self.generate_section_title(objective, user_level),
                'content': self.generate_section_content(objective, self.key_concepts, user_type, user_level),
                'concepts': [concept for concept in self.key_concepts if self._is_concept_relevant(concept, objective)]
            }
            content_sections.append(section)
        
        # 컨텍스트가 있는 경우 추가 섹션 생성
        if context:
            context_section = {
                'section_number': len(content_sections) + 1,
                'title': '추가 설명',
                'content': self._generate_context_based_content(context, user_type, user_level),
                'concepts': []
            }
            content_sections.append(context_section)
        
        return content_sections
    
    def _is_concept_relevant(self, concept: str, objective: str) -> bool:
        """개념이 목표와 관련있는지 확인"""
        return concept.lower() in objective.lower()
    
    def _generate_context_based_content(self, context: str, user_type: str, user_level: str) -> str:
        """컨텍스트 기반 추가 콘텐츠 생성"""
        if '질문' in context or '궁금' in context:
            return f"앞서 학습한 내용과 관련하여 추가 설명을 드리겠습니다: {context}"
        elif '예시' in context or '사례' in context:
            return f"구체적인 예시를 통해 더 자세히 알아보겠습니다: {context}"
        else:
            return f"관련 내용에 대한 보충 설명입니다: {context}"
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
    
    def generate_content(self, user_type: str, user_level: str, context: str = "") -> Dict[str, Any]:
        """전체 콘텐츠 생성"""
        template = self.get_chapter_template()
        style = self.explanation_styles.get(user_level, self.explanation_styles['medium'])
        
        content = {
            'chapter': self.chapter_id,
            'title': self.title,
            'introduction': self.generate_introduction(user_type, user_level),
            'main_content': self.generate_main_content(user_type, user_level, context),
            'examples': self.select_examples(user_type, user_level),
            'key_points': self.generate_key_points(user_level),
            'next_steps': self.generate_next_steps(user_type),
            'metadata': {
                'user_type': user_type,
                'user_level': user_level,
                'style': style,
                'generated_at': self._get_current_timestamp()
            }
        }
        
        return content