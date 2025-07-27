# agents/quiz/chapters/chapter2_quiz.py
# 챕터 2: LLM이란 무엇인가? 퀴즈 생성

from typing import Dict, List, Any
from .base_quiz_chapter import BaseQuizChapter


class Chapter2Quiz(BaseQuizChapter):
    """챕터 2: LLM이란 무엇인가? 퀴즈 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 2
        self.title = "LLM이란 무엇인가?"
        self.key_concepts = ["LLM", "GPT", "BERT", "Transformer", "토큰", "파라미터", "사전훈련"]
    
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "question": "LLM은 무엇의 줄임말인가요?",
                "options": ["Large Language Model", "Long Learning Method", "Latest Logic Machine", "Limited Language Mode"],
                "correct_answer": 0,
                "explanation": "LLM은 Large Language Model(대규모 언어 모델)의 줄임말입니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "다음 중 GPT의 특징으로 가장 적절한 것은?",
                "options": ["이미지만 처리 가능", "텍스트 생성에 특화", "음성 인식 전용", "계산만 수행"],
                "correct_answer": 1,
                "explanation": "GPT는 Generative Pre-trained Transformer로 텍스트 생성에 특화된 모델입니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "비즈니스에서 LLM 활용의 주요 이점은?",
                "options": ["문서 자동화", "고객 서비스 개선", "코드 생성 지원", "모든 것"],
                "correct_answer": 3,
                "explanation": "LLM은 문서 자동화, 고객 서비스, 코드 생성 등 다양한 비즈니스 영역에서 활용 가능합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "Transformer 아키텍처의 핵심 혁신은?",
                "options": ["순차 처리 방식", "Self-Attention 메커니즘", "RNN 구조", "CNN 활용"],
                "correct_answer": 1,
                "explanation": "Transformer의 핵심 혁신은 Self-Attention 메커니즘으로, 병렬 처리와 장거리 의존성 포착을 가능하게 했습니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "BERT와 GPT의 주요 차이점은?",
                "options": ["파라미터 수", "양방향 vs 단방향 처리", "학습 데이터 크기", "처리 속도"],
                "correct_answer": 1,
                "explanation": "BERT는 양방향으로 컨텍스트를 처리하여 이해에 특화되고, GPT는 단방향으로 처리하여 생성에 특화됩니다."
            }
        ]
    
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        return [
            {
                "level": "medium",
                "user_type": "beginner",
                "scenario": "LLM 학습 도우미",
                "task_description": "LLM의 개념을 중학생에게 쉽게 설명해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "중학생 수준에 맞는 언어 사용",
                    "일상생활 예시 포함",
                    "단계별 설명 요청"
                ],
                "evaluation_criteria": [
                    "연령대 적합성",
                    "이해하기 쉬운 설명",
                    "적절한 예시 활용"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "기술 도입 검토",
                "task_description": "회사에서 LLM 기술 도입을 검토하기 위한 분석 보고서를 작성해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "기술적 장단점 분석",
                    "비즈니스 활용 사례",
                    "도입 시 고려사항",
                    "ROI 예상 효과"
                ],
                "evaluation_criteria": [
                    "포괄적인 분석",
                    "비즈니스 관점 반영",
                    "실행 가능성",
                    "구체적인 데이터 요청"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "기술 전략 수립",
                "task_description": "LLM 기반 제품 개발 전략을 수립하는 프롬프트를 작성하세요.",
                "requirements": [
                    "시장 분석 포함",
                    "기술적 차별화 요소",
                    "경쟁사 대비 우위",
                    "개발 로드맵 제시"
                ],
                "evaluation_criteria": [
                    "전략적 사고",
                    "기술 이해도",
                    "시장 통찰력",
                    "실행 계획의 구체성"
                ]
            }
        ]
    
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_2_{self.chapter_id}",
            "question_type": "multiple_choice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "question_text": "LLM의 특징으로 가장 적절한 것은?",
            "options": [
                "이미지만 처리할 수 있는 모델",
                "대규모 텍스트 데이터로 훈련된 언어 모델",
                "음성 인식만 가능한 모델",
                "숫자 계산만 수행하는 모델"
            ],
            "correct_answer": 1,
            "explanation": "LLM은 대규모 텍스트 데이터로 사전훈련된 언어 모델로, 다양한 자연어 처리 태스크를 수행할 수 있습니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_2_{self.chapter_id}",
            "question_type": "prompt_practice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "scenario": "LLM 기술 설명",
            "task_description": "LLM 기술의 장점과 한계를 균형있게 설명하는 프롬프트를 작성하세요.",
            "requirements": [
                "기술적 장점 명시",
                "현재 한계점 포함",
                "객관적 관점 유지",
                "구체적 예시 요청"
            ],
            "evaluation_criteria": [
                "균형잡힌 시각",
                "기술 이해도",
                "명확한 설명",
                "실용적 관점"
            ],
            "sample_prompts": [],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()