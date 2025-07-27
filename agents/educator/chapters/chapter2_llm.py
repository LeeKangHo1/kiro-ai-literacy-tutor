# agents/educator/chapters/chapter2_llm.py
# 챕터 2: LLM이란 무엇인가? 콘텐츠 생성

from typing import Dict, List, Any
from .base_chapter import BaseChapter


class Chapter2LLM(BaseChapter):
    """챕터 2: LLM이란 무엇인가? 콘텐츠 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 2
        self.title = 'LLM이란 무엇인가?'
        self.objectives = [
            'LLM(Large Language Model)의 정의와 특징 이해',
            'GPT, BERT, Transformer 구조의 기본 개념 파악',
            'LLM의 발전 과정과 주요 모델들의 차이점 인식'
        ]
        self.key_concepts = [
            'LLM', 'GPT', 'BERT', 'Transformer', '토큰', '파라미터', '사전훈련'
        ]
        self.examples = {
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
    
    def get_chapter_template(self) -> Dict[str, Any]:
        """챕터 2 템플릿 반환"""
        return {
            'title': self.title,
            'objectives': self.objectives,
            'key_concepts': self.key_concepts,
            'examples': self.examples
        }
    
    def generate_section_title(self, objective: str, user_level: str) -> str:
        """섹션 제목 생성"""
        if user_level == 'low':
            # 친근한 제목
            title_map = {
                'LLM(Large Language Model)의 정의와 특징 이해': '🧠 LLM이 뭔가요?',
                'GPT, BERT, Transformer 구조의 기본 개념 파악': '🔧 AI 모델들의 구조',
                'LLM의 발전 과정과 주요 모델들의 차이점 인식': '📈 LLM의 발전 역사'
            }
        else:
            # 전문적인 제목
            title_map = {
                'LLM(Large Language Model)의 정의와 특징 이해': 'Large Language Model 개요',
                'GPT, BERT, Transformer 구조의 기본 개념 파악': '주요 LLM 아키텍처 분석',
                'LLM의 발전 과정과 주요 모델들의 차이점 인식': 'LLM 발전사 및 모델 비교'
            }
        
        return title_map.get(objective, objective)
    
    def generate_section_content(self, objective: str, key_concepts: List[str], 
                                user_type: str, user_level: str) -> str:
        """섹션별 콘텐츠 생성"""
        
        if 'LLM' in objective and '정의' in objective:
            return self._generate_llm_definition_content(user_level)
        elif 'GPT' in objective or 'BERT' in objective or 'Transformer' in objective:
            return self._generate_architecture_content(user_level)
        elif '발전 과정' in objective or '차이점' in objective:
            return self._generate_evolution_content(user_level)
        else:
            return f"{objective}에 대한 상세한 설명이 여기에 들어갑니다."
    
    def _generate_llm_definition_content(self, user_level: str) -> str:
        """LLM 정의 콘텐츠"""
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

**주요 구성 요소**
1. **토큰화 (Tokenization)**
   - 텍스트를 모델이 이해할 수 있는 단위로 분할
   - 단어, 서브워드, 문자 단위로 처리

2. **임베딩 (Embedding)**
   - 토큰을 고차원 벡터로 변환
   - 의미적 유사성을 수치로 표현

3. **어텐션 메커니즘 (Attention Mechanism)**
   - 입력 시퀀스의 중요한 부분에 집중
   - 장거리 의존성 문제 해결

**학습 과정**
1. **사전훈련 (Pre-training)**: 대규모 텍스트 코퍼스로 언어 모델링
2. **파인튜닝 (Fine-tuning)**: 특정 태스크에 맞게 추가 학습
3. **인간 피드백 강화학습 (RLHF)**: 인간 선호도 반영

**성능 지표**
- **Perplexity**: 언어 모델의 예측 정확도
- **BLEU Score**: 번역 품질 평가
- **Human Evaluation**: 인간 평가자의 주관적 평가
            """
    
    def _generate_architecture_content(self, user_level: str) -> str:
        """아키텍처 콘텐츠"""
        if user_level == 'low':
            return """
LLM의 주요 모델들을 쉽게 알아볼까요?

🔧 **Transformer (트랜스포머)**
- 모든 LLM의 기본이 되는 구조
- 2017년 구글에서 발명
- "Attention is All You Need" 논문으로 유명해짐
- 특징: 병렬 처리가 가능해서 빠르고 효율적

🤖 **GPT (Generative Pre-trained Transformer)**
- OpenAI에서 만든 모델
- 특징: 텍스트를 생성하는 데 특화
- 발전 과정: GPT-1 → GPT-2 → GPT-3 → GPT-4
- 활용: ChatGPT의 기반 기술

🔍 **BERT (Bidirectional Encoder Representations)**
- Google에서 만든 모델
- 특징: 텍스트를 이해하는 데 특화
- 양방향으로 문맥을 파악할 수 있어요
- 활용: 검색 엔진, 질문 답변 시스템

💡 **쉬운 비유**
- Transformer = 자동차의 엔진
- GPT = 글쓰기에 특화된 자동차
- BERT = 독해에 특화된 자동차
            """
        else:
            return """
주요 LLM 아키텍처의 기술적 특징을 분석해보겠습니다.

**Transformer 아키텍처**
- **구조**: Encoder-Decoder 또는 Decoder-only
- **핵심 메커니즘**: Self-Attention, Multi-Head Attention
- **장점**: 병렬 처리 가능, 장거리 의존성 포착
- **혁신**: RNN/LSTM의 순차 처리 한계 극복

**GPT (Generative Pre-trained Transformer)**
- **아키텍처**: Decoder-only Transformer
- **학습 방식**: 자기회귀적 언어 모델링 (Autoregressive)
- **특징**:
  - 다음 토큰 예측을 통한 텍스트 생성
  - Causal Masking으로 미래 토큰 차단
  - Zero-shot, Few-shot 학습 능력
- **발전 과정**:
  - GPT-1 (117M 파라미터) → GPT-4 (추정 1.7T 파라미터)
  - 규모 증가에 따른 Emergent Abilities 발현

**BERT (Bidirectional Encoder Representations)**
- **아키텍처**: Encoder-only Transformer
- **학습 방식**: Masked Language Modeling (MLM)
- **특징**:
  - 양방향 컨텍스트 이해
  - [MASK] 토큰을 통한 사전훈련
  - 문장 분류, 개체명 인식 등에 특화
- **변형 모델**: RoBERTa, ALBERT, DeBERTa

**아키텍처 비교**
- **GPT**: 생성 태스크에 최적화, 창의적 텍스트 생성
- **BERT**: 이해 태스크에 최적화, 정확한 분류 및 추출
- **T5**: Encoder-Decoder 구조, Text-to-Text 통합 접근

**최신 동향**
- **Mixture of Experts (MoE)**: 효율적인 대규모 모델
- **Retrieval-Augmented Generation**: 외부 지식 활용
- **Multimodal Models**: 텍스트-이미지 통합 처리
            """
    
    def _generate_evolution_content(self, user_level: str) -> str:
        """발전 과정 콘텐츠"""
        if user_level == 'low':
            return """
LLM이 어떻게 발전해왔는지 알아볼까요?

📈 **LLM의 발전 역사**

**1단계: 초기 언어 모델 (2010년대 초)**
- 간단한 통계 기반 모델
- 단어 예측 정도만 가능
- 예: N-gram 모델

**2단계: 신경망 언어 모델 (2010년대 중반)**
- RNN, LSTM 사용
- 조금 더 자연스러운 텍스트 생성
- 하지만 여전히 한계가 많았어요

**3단계: Transformer 등장 (2017년)**
- 구글이 Transformer 발표
- 모든 것이 바뀌기 시작!
- 병렬 처리로 훨씬 빨라짐

**4단계: GPT 시리즈 (2018년~)**
- GPT-1 (2018): 작지만 가능성 보여줌
- GPT-2 (2019): 너무 위험해서 공개 안 함
- GPT-3 (2020): 세상을 놀라게 함
- GPT-4 (2023): 거의 사람 수준!

**5단계: 대화형 AI 시대 (2022년~)**
- ChatGPT 출시로 대중화
- 누구나 AI와 대화할 수 있게 됨
- 다양한 회사들이 경쟁 시작

🚀 **미래 전망**
- 더 똑똑하고 효율적인 모델들
- 멀티모달 (텍스트 + 이미지 + 음성)
- 개인 맞춤형 AI 어시스턴트
            """
        else:
            return """
LLM의 기술적 발전 과정과 주요 모델들의 차이점을 분석해보겠습니다.

**발전 단계별 분석**

**1세대: 통계적 언어 모델 (2000년대)**
- N-gram 모델, 히든 마르코프 모델
- 제한적인 컨텍스트 이해
- 주요 한계: 장거리 의존성 처리 불가

**2세대: 신경망 언어 모델 (2010년대)**
- RNN, LSTM, GRU 기반 모델
- 순차적 처리로 인한 병렬화 한계
- 대표 모델: ELMo, ULMFiT

**3세대: Transformer 기반 모델 (2017년~)**
- Self-Attention 메커니즘 도입
- 병렬 처리 가능, 효율성 대폭 향상
- 대표 모델: BERT, GPT, T5

**4세대: 대규모 언어 모델 (2019년~)**
- 파라미터 수 급격한 증가
- Emergent Abilities 발현
- 대표 모델: GPT-3, PaLM, LaMDA

**5세대: 인간 피드백 기반 모델 (2022년~)**
- RLHF (Reinforcement Learning from Human Feedback)
- 인간 선호도 반영한 안전하고 유용한 AI
- 대표 모델: ChatGPT, GPT-4, Claude

**주요 모델 비교**

| 모델 | 출시년도 | 파라미터 수 | 주요 특징 |
|------|----------|-------------|-----------|
| GPT-1 | 2018 | 117M | 최초의 대규모 사전훈련 |
| BERT | 2018 | 340M | 양방향 인코더, 이해 태스크 특화 |
| GPT-2 | 2019 | 1.5B | 텍스트 생성 품질 대폭 향상 |
| GPT-3 | 2020 | 175B | Few-shot 학습 능력 |
| PaLM | 2022 | 540B | 추론 능력 향상 |
| GPT-4 | 2023 | ~1.7T | 멀티모달, 인간 수준 성능 |

**기술적 혁신 요소**
1. **스케일링 법칙**: 모델 크기 증가에 따른 성능 향상
2. **In-Context Learning**: 추가 학습 없이 예시로 학습
3. **Chain-of-Thought**: 단계별 추론 능력
4. **Instruction Tuning**: 명령어 따르기 능력
5. **Constitutional AI**: 안전하고 도움이 되는 AI

**미래 연구 방향**
- **효율성**: 더 적은 자원으로 더 나은 성능
- **멀티모달리티**: 텍스트, 이미지, 음성 통합
- **추론 능력**: 논리적 사고 및 수학적 추론
- **안전성**: AI 정렬 및 위험 완화
- **개인화**: 사용자 맞춤형 AI 어시스턴트
            """