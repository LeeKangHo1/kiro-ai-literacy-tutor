# agents/educator/content_generator.py
# 기본 콘텐츠 생성 로직 구현

from typing import Dict, List, Any, Optional
from workflow.state_management import TutorState


class ContentGenerator:
    """이론 콘텐츠 생성을 담당하는 클래스"""
    
    def __init__(self):
        # 챕터별 기본 콘텐츠 템플릿
        self.chapter_templates = {
            1: {
                'title': 'AI는 무엇인가?',
                'objectives': [
                    'AI, ML, DL의 개념과 차이점 이해',
                    'AI의 실생활 적용 사례 파악',
                    'AI 기술의 한계와 가능성 인식'
                ],
                'key_concepts': ['AI', 'Machine Learning', 'Deep Learning', '알고리즘', '데이터'],
                'examples': {
                    'beginner': [
                        '스마트폰의 음성인식 (Siri, 구글 어시스턴트)',
                        '넷플릭스의 영화 추천 시스템',
                        '자동차의 내비게이션 시스템'
                    ],
                    'business': [
                        '고객 행동 예측 분석',
                        '자동화된 고객 서비스 챗봇',
                        '공급망 최적화 시스템'
                    ]
                }
            },
            2: {
                'title': 'AI의 종류와 특징',
                'objectives': [
                    '약한 AI와 강한 AI의 구분',
                    '지도학습, 비지도학습, 강화학습 이해',
                    '각 AI 유형의 활용 분야 파악'
                ],
                'key_concepts': ['약한 AI', '강한 AI', '지도학습', '비지도학습', '강화학습'],
                'examples': {
                    'beginner': [
                        '이미지 분류 (고양이/개 구분)',
                        '번역 서비스 (구글 번역)',
                        '게임 AI (알파고)'
                    ],
                    'business': [
                        '이상 거래 탐지 시스템',
                        '고객 세분화 분석',
                        '동적 가격 책정 시스템'
                    ]
                }
            },
            3: {
                'title': '프롬프트란 무엇인가?',
                'objectives': [
                    '프롬프트의 정의와 중요성 이해',
                    '효과적인 프롬프트 작성 원칙 학습',
                    '실제 프롬프트 작성 및 테스트 경험'
                ],
                'key_concepts': ['프롬프트', 'LLM', 'ChatGPT', '명령어', '컨텍스트'],
                'examples': {
                    'beginner': [
                        '간단한 질문하기: "오늘 날씨 어때?"',
                        '번역 요청: "Hello를 한국어로 번역해줘"',
                        '요약 요청: "이 글을 3줄로 요약해줘"'
                    ],
                    'business': [
                        '보고서 작성: "분기별 매출 보고서 초안 작성"',
                        '이메일 작성: "고객 불만 처리 이메일 작성"',
                        '아이디어 생성: "신제품 마케팅 전략 아이디어 10개"'
                    ]
                }
            }
        }
        
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
        
        if chapter not in self.chapter_templates:
            return self._generate_fallback_content(chapter, user_type, user_level)
        
        template = self.chapter_templates[chapter]
        style = self.explanation_styles.get(user_level, self.explanation_styles['medium'])
        
        content = {
            'chapter': chapter,
            'title': template['title'],
            'introduction': self._generate_introduction(template, user_type, user_level),
            'main_content': self._generate_main_content(template, user_type, user_level, context),
            'examples': self._select_examples(template, user_type, user_level),
            'key_points': self._generate_key_points(template, user_level),
            'next_steps': self._generate_next_steps(template, user_type),
            'metadata': {
                'user_type': user_type,
                'user_level': user_level,
                'style': style,
                'generated_at': self._get_current_timestamp()
            }
        }
        
        return content
    
    def _generate_introduction(self, template: Dict[str, Any], 
                              user_type: str, user_level: str) -> str:
        """도입부 생성"""
        
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
    
    def _generate_main_content(self, template: Dict[str, Any], 
                              user_type: str, user_level: str, context: str) -> List[Dict[str, str]]:
        """메인 콘텐츠 생성"""
        
        objectives = template['objectives']
        key_concepts = template['key_concepts']
        
        content_sections = []
        
        # 각 학습 목표별로 섹션 생성
        for i, objective in enumerate(objectives):
            section = {
                'section_number': i + 1,
                'title': self._generate_section_title(objective, user_level),
                'content': self._generate_section_content(objective, key_concepts, user_type, user_level),
                'concepts': [concept for concept in key_concepts if self._is_concept_relevant(concept, objective)]
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
    
    def _generate_section_title(self, objective: str, user_level: str) -> str:
        """섹션 제목 생성"""
        
        if user_level == 'low':
            # 친근한 제목
            title_map = {
                'AI, ML, DL의 개념과 차이점 이해': '🤖 AI, 머신러닝, 딥러닝이 뭔가요?',
                'AI의 실생활 적용 사례 파악': '📱 우리 주변의 AI 찾아보기',
                'AI 기술의 한계와 가능성 인식': '🔮 AI가 할 수 있는 것과 없는 것',
                '약한 AI와 강한 AI의 구분': '💪 약한 AI vs 강한 AI',
                '지도학습, 비지도학습, 강화학습 이해': '📚 AI가 학습하는 방법들',
                '각 AI 유형의 활용 분야 파악': '🎯 어떤 AI를 언제 사용할까?',
                '프롬프트의 정의와 중요성 이해': '💬 프롬프트가 뭐길래?',
                '효과적인 프롬프트 작성 원칙 학습': '✍️ 좋은 프롬프트 작성법',
                '실제 프롬프트 작성 및 테스트 경험': '🧪 직접 프롬프트 만들어보기'
            }
        else:
            # 전문적인 제목
            title_map = {
                'AI, ML, DL의 개념과 차이점 이해': '인공지능, 머신러닝, 딥러닝의 개념 정의',
                'AI의 실생활 적용 사례 파악': '인공지능의 실생활 적용 사례 분석',
                'AI 기술의 한계와 가능성 인식': '인공지능 기술의 현재 한계와 미래 가능성',
                '약한 AI와 강한 AI의 구분': '약한 인공지능과 강한 인공지능의 차이점',
                '지도학습, 비지도학습, 강화학습 이해': '머신러닝의 주요 학습 방법론',
                '각 AI 유형의 활용 분야 파악': 'AI 유형별 적용 분야 및 활용 사례',
                '프롬프트의 정의와 중요성 이해': '프롬프트 엔지니어링의 기초',
                '효과적인 프롬프트 작성 원칙 학습': '효과적인 프롬프트 설계 원칙',
                '실제 프롬프트 작성 및 테스트 경험': '프롬프트 작성 실습 및 최적화'
            }
        
        return title_map.get(objective, objective)
    
    def _generate_section_content(self, objective: str, key_concepts: List[str], 
                                 user_type: str, user_level: str) -> str:
        """섹션 콘텐츠 생성"""
        
        # 간단한 템플릿 기반 콘텐츠 생성
        # 실제 구현에서는 더 정교한 콘텐츠 생성 로직 필요
        
        if 'AI, ML, DL' in objective:
            if user_level == 'low':
                return """
AI(인공지능)는 컴퓨터가 사람처럼 생각하고 판단할 수 있게 하는 기술입니다.

🤖 **AI (인공지능)**: 컴퓨터가 사람처럼 똑똑하게 행동하는 것
- 예: 스마트폰 음성인식, 번역 앱

📊 **ML (머신러닝)**: AI의 한 방법으로, 컴퓨터가 데이터를 보고 스스로 학습하는 것
- 예: 넷플릭스가 내가 좋아할 영화를 추천하는 것

🧠 **DL (딥러닝)**: 머신러닝의 한 방법으로, 사람의 뇌를 모방한 방식
- 예: 사진에서 얼굴을 찾아내는 것

쉽게 말해서: AI > ML > DL 순서로 포함관계입니다!
                """
            else:
                return """
인공지능(AI), 머신러닝(ML), 딥러닝(DL)은 서로 연관되어 있지만 구별되는 개념입니다.

**인공지능 (Artificial Intelligence)**
- 정의: 인간의 지능을 모방하여 학습, 추론, 판단 등을 수행하는 컴퓨터 시스템
- 범위: 가장 넓은 개념으로 모든 지능적 행동을 포함

**머신러닝 (Machine Learning)**
- 정의: 명시적 프로그래밍 없이 데이터로부터 패턴을 학습하는 AI의 하위 분야
- 특징: 경험을 통해 성능이 향상되는 알고리즘

**딥러닝 (Deep Learning)**
- 정의: 인공신경망을 기반으로 한 머신러닝의 특수한 형태
- 특징: 다층 신경망을 통해 복잡한 패턴 인식 가능

**관계**: AI ⊃ ML ⊃ DL (포함관계)
                """
        
        elif '프롬프트' in objective:
            if user_level == 'low':
                return """
프롬프트는 AI에게 주는 '명령어'나 '질문'입니다.

💬 **프롬프트란?**
- AI(ChatGPT 같은)에게 무엇을 해달라고 말하는 것
- 예: "오늘 날씨 어때?", "이메일 써줘"

✨ **왜 중요한가요?**
- 프롬프트를 잘 쓰면 → AI가 더 좋은 답변을 해줘요
- 프롬프트를 대충 쓰면 → AI가 엉뚱한 답변을 할 수 있어요

📝 **좋은 프롬프트의 특징**
1. 명확하게: "뭔가 써줘" ❌ → "회의 요약 이메일 써줘" ✅
2. 구체적으로: "글 써줘" ❌ → "500자 블로그 글 써줘" ✅
3. 예시 포함: "이런 식으로 써줘: [예시]"
                """
            else:
                return """
프롬프트 엔지니어링은 LLM과의 효과적인 상호작용을 위한 핵심 기술입니다.

**프롬프트의 정의**
- Large Language Model(LLM)에 입력하는 텍스트 명령어
- 모델의 출력을 제어하고 원하는 결과를 얻기 위한 인터페이스

**프롬프트의 중요성**
1. **출력 품질 결정**: 동일한 모델도 프롬프트에 따라 결과가 크게 달라짐
2. **효율성 향상**: 적절한 프롬프트로 원하는 결과를 빠르게 획득
3. **비용 최적화**: 효과적인 프롬프트로 API 호출 횟수 감소

**프롬프트 설계 원칙**
- **명확성**: 모호하지 않은 구체적 지시사항
- **맥락 제공**: 충분한 배경 정보와 예시
- **구조화**: 논리적 순서와 명확한 형식
- **제약 조건**: 출력 길이, 형식, 톤 등의 명시
                """
        
        # 기본 템플릿
        return f"{objective}에 대한 상세한 설명이 여기에 들어갑니다. 사용자 레벨({user_level})과 타입({user_type})에 맞춰 조정된 내용입니다."
    
    def _select_examples(self, template: Dict[str, Any], 
                        user_type: str, user_level: str) -> List[str]:
        """사용자 타입에 맞는 예시 선택"""
        
        examples = template.get('examples', {})
        user_examples = examples.get(user_type, [])
        
        # 레벨에 따라 예시 개수 조정
        if user_level == 'low':
            return user_examples[:2]  # 간단히 2개만
        elif user_level == 'medium':
            return user_examples[:3]  # 3개
        else:
            return user_examples  # 모든 예시
    
    def _generate_key_points(self, template: Dict[str, Any], user_level: str) -> List[str]:
        """핵심 포인트 생성"""
        
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
    
    def _generate_next_steps(self, template: Dict[str, Any], user_type: str) -> List[str]:
        """다음 단계 제안"""
        
        next_steps = []
        
        if user_type == 'beginner':
            next_steps = [
                "🤔 궁금한 점이 있으면 언제든 질문해보세요",
                "📝 학습한 내용을 확인하는 퀴즈를 풀어보세요",
                "💡 실생활에서 관련 사례를 찾아보세요"
            ]
        else:  # business
            next_steps = [
                "💼 비즈니스 적용 방안을 구체적으로 생각해보세요",
                "📊 실무 사례를 통한 문제 해결 연습을 해보세요",
                "🔍 심화 학습을 위한 추가 질문을 해보세요"
            ]
        
        return next_steps
    
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
    
    def _generate_context_based_content(self, context: str, user_type: str, user_level: str) -> str:
        """컨텍스트 기반 추가 콘텐츠 생성"""
        
        # 간단한 컨텍스트 분석 및 콘텐츠 생성
        if '질문' in context or '궁금' in context:
            return f"앞서 학습한 내용과 관련하여 추가 설명을 드리겠습니다: {context}"
        elif '예시' in context or '사례' in context:
            return f"구체적인 예시를 통해 더 자세히 알아보겠습니다: {context}"
        else:
            return f"관련 내용에 대한 보충 설명입니다: {context}"
    
    def _is_concept_relevant(self, concept: str, objective: str) -> bool:
        """개념이 목표와 관련있는지 확인"""
        
        # 간단한 키워드 매칭
        return concept.lower() in objective.lower()
    
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