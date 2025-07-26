# agents/educator/content_generator.py
# 기본 콘텐츠 생성 로직 구현

from typing import Dict, List, Any, Optional
from workflow.state_management import TutorState, StateManager


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
                'title': 'LLM이란 무엇인가?',
                'objectives': [
                    'LLM(Large Language Model)의 정의와 특징 이해',
                    'GPT, BERT, Transformer 구조의 기본 개념 파악',
                    'LLM의 발전 과정과 주요 모델들의 차이점 인식'
                ],
                'key_concepts': ['LLM', 'GPT', 'BERT', 'Transformer', '토큰', '파라미터', '사전훈련'],
                'examples': {
                    'beginner': [
                        'ChatGPT - 대화형 AI 어시스턴트',
                        'Google Bard - 구글의 대화형 AI',
                        'Claude - Anthropic의 AI 어시스턴트'
                    ],
                    'business': [
                        '문서 자동 생성 및 편집 도구',
                        '고객 서비스 자동화 시스템',
                        '코드 생성 및 리뷰 도구 (GitHub Copilot)'
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
            },
            4: {
                'title': 'ChatGPT로 할 수 있는 것들',
                'objectives': [
                    'ChatGPT의 주요 활용 분야와 기능 이해',
                    '요약, 번역, 질문 생성 등 실용적 기능 체험',
                    '업무 효율성 향상을 위한 ChatGPT 활용법 학습'
                ],
                'key_concepts': ['텍스트 생성', '요약', '번역', '질문 생성', '코드 작성', '창작', '분석'],
                'examples': {
                    'beginner': [
                        '긴 글 요약하기: "이 기사를 3줄로 요약해줘"',
                        '언어 번역하기: "이 문장을 영어로 번역해줘"',
                        '아이디어 생성하기: "여행 계획 아이디어 10개 알려줘"'
                    ],
                    'business': [
                        '회의록 요약 및 액션 아이템 추출',
                        '마케팅 카피 및 제안서 초안 작성',
                        '데이터 분석 결과 해석 및 보고서 생성'
                    ]
                }
            },
            5: {
                'title': 'AI 시대의 문해력',
                'objectives': [
                    'AI 기술의 윤리적 고려사항 이해',
                    'AI의 현재 한계와 미래 발전 방향 파악',
                    'AI 시대에 필요한 새로운 역량과 진로 탐색'
                ],
                'key_concepts': ['AI 윤리', '편향성', '개인정보보호', '일자리 변화', '디지털 리터러시', '창의성'],
                'examples': {
                    'beginner': [
                        'AI가 만든 가짜 뉴스 구별하기',
                        'AI 도구를 활용한 학습 방법',
                        'AI와 함께 일하는 새로운 직업들'
                    ],
                    'business': [
                        'AI 도입 시 윤리적 가이드라인 수립',
                        'AI 기반 의사결정의 투명성 확보',
                        'AI 시대의 인재 육성 전략'
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
                '실제 프롬프트 작성 및 테스트 경험': '🧪 직접 프롬프트 만들어보기',
                'LLM(Large Language Model)의 정의와 특징 이해': '🧠 LLM이 뭔가요?',
                'GPT, BERT, Transformer 구조의 기본 개념 파악': '🔧 AI 모델들의 구조',
                'LLM의 발전 과정과 주요 모델들의 차이점 인식': '📈 LLM의 발전 역사',
                'ChatGPT의 주요 활용 분야와 기능 이해': '🚀 ChatGPT 활용법',
                '요약, 번역, 질문 생성 등 실용적 기능 체험': '⚡ 실용적 기능들',
                '업무 효율성 향상을 위한 ChatGPT 활용법 학습': '💼 업무에 활용하기',
                'AI 기술의 윤리적 고려사항 이해': '⚖️ AI 윤리',
                'AI의 현재 한계와 미래 발전 방향 파악': '🔮 AI의 한계와 미래',
                'AI 시대에 필요한 새로운 역량과 진로 탐색': '💪 미래 역량 기르기'
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
                '실제 프롬프트 작성 및 테스트 경험': '프롬프트 작성 실습 및 최적화',
                'LLM(Large Language Model)의 정의와 특징 이해': 'Large Language Model 개요',
                'GPT, BERT, Transformer 구조의 기본 개념 파악': '주요 LLM 아키텍처 분석',
                'LLM의 발전 과정과 주요 모델들의 차이점 인식': 'LLM 발전사 및 모델 비교',
                'ChatGPT의 주요 활용 분야와 기능 이해': 'ChatGPT 기능 및 활용 분야',
                '요약, 번역, 질문 생성 등 실용적 기능 체험': '핵심 기능별 활용 전략',
                '업무 효율성 향상을 위한 ChatGPT 활용법 학습': '비즈니스 프로세스 최적화',
                'AI 기술의 윤리적 고려사항 이해': 'AI 윤리 및 책임감 있는 AI',
                'AI의 현재 한계와 미래 발전 방향 파악': 'AI 기술의 현재 한계와 발전 전망',
                'AI 시대에 필요한 새로운 역량과 진로 탐색': '미래 인재 역량 및 진로 개발'
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
        
        elif 'LLM' in objective or 'GPT' in objective or 'BERT' in objective or 'Transformer' in objective:
            if user_level == 'low':
                return """
LLM은 'Large Language Model'의 줄임말로, 아주 큰 언어 모델이라는 뜻입니다.

🧠 **LLM이란?**
- 엄청나게 많은 텍스트를 학습한 AI 모델
- 사람처럼 자연스럽게 글을 읽고 쓸 수 있어요
- 예: ChatGPT, Google Bard, Claude

📚 **주요 LLM 모델들**
- **GPT**: OpenAI에서 만든 대화형 AI (ChatGPT의 기반)
- **BERT**: Google에서 만든 텍스트 이해 전문 AI
- **Transformer**: 모든 LLM의 기본이 되는 구조

🔧 **어떻게 작동하나요?**
1. 인터넷의 수많은 글을 읽고 학습
2. 단어들 사이의 관계를 파악
3. 새로운 질문에 적절한 답변 생성

💡 **왜 대단한가요?**
- 번역, 요약, 창작 등 다양한 일을 한 번에!
- 사람과 자연스럽게 대화 가능
                """
            else:
                return """
Large Language Model(LLM)은 대규모 텍스트 데이터로 사전훈련된 신경망 모델입니다.

**LLM의 핵심 특징**
- **규모**: 수십억~수조 개의 파라미터로 구성
- **사전훈련**: 인터넷 텍스트로 언어의 통계적 패턴 학습
- **범용성**: 다양한 자연어 처리 태스크에 적용 가능

**주요 아키텍처**
1. **Transformer**: 어텐션 메커니즘 기반의 기본 구조
   - 병렬 처리 가능, 장거리 의존성 포착
   - Encoder-Decoder 또는 Decoder-only 구조

2. **GPT (Generative Pre-trained Transformer)**
   - Decoder-only 구조, 자기회귀적 텍스트 생성
   - 대화형 AI의 기반 모델

3. **BERT (Bidirectional Encoder Representations)**
   - Encoder-only 구조, 양방향 컨텍스트 이해
   - 텍스트 분류, 질의응답에 특화

**발전 과정**
- GPT-1 (2018) → GPT-2 (2019) → GPT-3 (2020) → GPT-4 (2023)
- 파라미터 수와 성능의 지속적 향상
- Few-shot, Zero-shot 학습 능력 획득
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
        
        elif 'ChatGPT' in objective or '요약' in objective or '번역' in objective or '질문 생성' in objective:
            if user_level == 'low':
                return """
ChatGPT는 정말 다양한 일을 할 수 있는 만능 AI 도우미입니다!

📝 **텍스트 작업**
- **요약하기**: 긴 글을 짧게 정리해줘요
  - "이 기사를 3줄로 요약해줘"
- **번역하기**: 다른 언어로 번역해줘요
  - "이 문장을 영어로 번역해줘"
- **글쓰기**: 이메일, 편지, 보고서 등을 써줘요
  - "감사 인사 이메일 써줘"

🤔 **아이디어 도우미**
- **질문 만들기**: 공부할 때 문제를 만들어줘요
- **아이디어 생성**: 창의적인 아이디어를 제안해줘요
- **계획 세우기**: 여행, 공부 계획을 도와줘요

💻 **실용적 활용**
- **설명하기**: 어려운 개념을 쉽게 설명
- **검토하기**: 내가 쓴 글을 확인하고 개선점 제안
- **대화하기**: 궁금한 것을 자유롭게 물어보기

💡 **팁**: 구체적으로 요청할수록 더 좋은 결과를 얻을 수 있어요!
                """
            else:
                return """
ChatGPT는 다양한 비즈니스 태스크에서 생산성을 크게 향상시킬 수 있는 도구입니다.

**핵심 활용 분야**

1. **문서 작업 자동화**
   - 회의록 요약 및 액션 아이템 추출
   - 보고서 초안 작성 및 구조화
   - 이메일 템플릿 생성 및 개인화

2. **콘텐츠 생성 및 편집**
   - 마케팅 카피 및 제안서 작성
   - 블로그 포스트 및 소셜미디어 콘텐츠
   - 프레젠테이션 스크립트 개발

3. **데이터 분석 지원**
   - 복잡한 데이터 해석 및 인사이트 도출
   - 차트 및 그래프 설명 생성
   - 트렌드 분석 및 예측 보고서

4. **고객 서비스 향상**
   - FAQ 자동 생성 및 업데이트
   - 고객 문의 응답 템플릿 작성
   - 다국어 고객 지원 콘텐츠 번역

**효과적 활용 전략**
- **명확한 역할 정의**: "마케팅 전문가로서..." 등 역할 부여
- **구체적 요구사항**: 형식, 길이, 톤앤매너 명시
- **반복적 개선**: 피드백을 통한 점진적 품질 향상
                """
        
        elif 'AI 윤리' in objective or '한계' in objective or '미래' in objective or '문해력' in objective:
            if user_level == 'low':
                return """
AI가 발전하면서 우리가 알아야 할 중요한 것들이 있어요.

⚖️ **AI 윤리 - 공정하게 사용하기**
- AI도 편견을 가질 수 있어요 (학습 데이터의 편향)
- 개인정보를 보호해야 해요
- AI가 만든 내용임을 밝혀야 해요

🚫 **AI의 한계**
- 항상 정확하지는 않아요 (할루시네이션)
- 최신 정보를 모를 수 있어요
- 감정이나 창의성에는 한계가 있어요

🔮 **미래의 변화**
- 새로운 직업들이 생겨날 거예요
- AI와 함께 일하는 능력이 중요해져요
- 평생학습이 더욱 중요해져요

💪 **우리가 준비해야 할 것**
- AI 도구 사용법 익히기
- 비판적 사고력 기르기
- 창의성과 소통 능력 개발하기

🌟 **AI 시대의 문해력**
- AI가 만든 정보를 구별할 수 있는 능력
- AI를 도구로 활용하는 능력
- 윤리적으로 AI를 사용하는 능력
                """
            else:
                return """
AI 기술의 급속한 발전은 사회 전반에 걸쳐 근본적인 변화를 가져오고 있습니다.

**AI 윤리의 핵심 이슈**

1. **알고리즘 편향성 (Algorithmic Bias)**
   - 훈련 데이터의 편향이 AI 결과에 반영
   - 성별, 인종, 연령 등에 대한 차별적 결과 가능
   - 공정성 확보를 위한 다양성 있는 데이터셋 필요

2. **개인정보보호 및 프라이버시**
   - 대규모 개인 데이터 수집 및 활용
   - GDPR, 개인정보보호법 등 규제 준수
   - 데이터 최소화 및 목적 제한 원칙

3. **투명성 및 설명가능성**
   - 블랙박스 문제: AI 의사결정 과정의 불투명성
   - 설명가능한 AI(XAI) 기술 개발 필요
   - 알고리즘 감사 및 책임성 확보

**현재 기술의 한계**
- **할루시네이션**: 그럴듯하지만 잘못된 정보 생성
- **컨텍스트 이해 부족**: 상황적 맥락 파악의 한계
- **일관성 부족**: 유사한 질문에 다른 답변

**미래 전망 및 대응 전략**
- **인간-AI 협업 모델**: AI가 인간을 대체하는 것이 아닌 보완
- **새로운 역량 요구**: 디지털 리터러시, AI 리터러시
- **지속적 학습**: 기술 변화에 적응하는 평생학습 체계
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