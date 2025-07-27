# agents/quiz/chapters/chapter4_quiz.py
# 챕터 4: ChatGPT로 할 수 있는 것들 퀴즈 생성

from typing import Dict, List, Any
from .base_quiz_chapter import BaseQuizChapter


class Chapter4Quiz(BaseQuizChapter):
    """챕터 4: ChatGPT로 할 수 있는 것들 퀴즈 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 4
        self.title = "ChatGPT로 할 수 있는 것들"
        self.key_concepts = ["텍스트 생성", "요약", "번역", "질문 생성", "코드 작성", "창작", "분석"]
    
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "question": "ChatGPT로 할 수 없는 것은?",
                "options": ["텍스트 요약", "언어 번역", "실시간 인터넷 검색", "질문 답변"],
                "correct_answer": 2,
                "explanation": "ChatGPT는 실시간 인터넷 검색은 기본적으로 지원하지 않습니다. (플러그인 제외)"
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "ChatGPT를 활용한 학습에서 가장 효과적인 방법은?",
                "options": ["모든 답을 그대로 믿기", "구체적으로 질문하기", "짧게만 질문하기", "한 번만 질문하기"],
                "correct_answer": 1,
                "explanation": "구체적이고 명확한 질문을 할 때 ChatGPT로부터 더 유용한 답변을 얻을 수 있습니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "업무에서 ChatGPT 활용 시 주의사항은?",
                "options": ["개인정보 입력 금지", "결과 검증 필요", "저작권 고려", "모든 것"],
                "correct_answer": 3,
                "explanation": "업무에서 ChatGPT 사용 시 개인정보 보호, 결과 검증, 저작권 등 모든 사항을 고려해야 합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "ChatGPT를 활용한 콘텐츠 마케팅의 핵심 전략은?",
                "options": ["완전 자동화", "브랜드 일관성 유지", "대량 생산", "비용 절감만 추구"],
                "correct_answer": 1,
                "explanation": "ChatGPT 활용 시에도 브랜드의 톤앤매너와 가치를 일관되게 유지하는 것이 가장 중요합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "ChatGPT 기반 고객 서비스 구축 시 가장 중요한 요소는?",
                "options": ["응답 속도", "정확성과 안전성", "비용 효율성", "자동화 수준"],
                "correct_answer": 1,
                "explanation": "고객 서비스에서는 잘못된 정보 제공이 큰 문제가 될 수 있으므로 정확성과 안전성이 최우선입니다."
            }
        ]
    
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "scenario": "학습 도우미",
                "task_description": "어려운 개념을 쉽게 설명해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 개념 명시",
                    "설명 수준 지정",
                    "예시 요청 포함"
                ],
                "evaluation_criteria": [
                    "명확성",
                    "구체성",
                    "이해하기 쉬운 표현"
                ]
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "scenario": "창작 활동",
                "task_description": "특정 주제의 블로그 글을 써달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "주제와 타겟 독자 명시",
                    "글의 길이와 구조 지정",
                    "톤앤매너 설정"
                ],
                "evaluation_criteria": [
                    "구체적인 지시사항",
                    "창작 가이드라인",
                    "품질 기준 제시"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "업무 효율화",
                "task_description": "회의록을 요약하고 액션 아이템을 추출하는 프롬프트를 작성하세요.",
                "requirements": [
                    "요약 형식 지정",
                    "액션 아이템 구조화",
                    "우선순위 표시 요청"
                ],
                "evaluation_criteria": [
                    "구조화된 출력",
                    "실용성",
                    "완성도"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "마케팅 자동화",
                "task_description": "다양한 채널별 마케팅 콘텐츠를 일관성 있게 생성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "채널별 특성 고려",
                    "브랜드 가이드라인 반영",
                    "타겟 오디언스 세분화",
                    "성과 측정 가능한 요소 포함"
                ],
                "evaluation_criteria": [
                    "전략적 사고",
                    "브랜드 일관성",
                    "채널 최적화",
                    "측정 가능성"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "데이터 분석 보고",
                "task_description": "복잡한 비즈니스 데이터를 분석하여 경영진 보고서를 작성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "핵심 인사이트 도출",
                    "비즈니스 임팩트 분석",
                    "액션 플랜 제시",
                    "리스크 요소 식별"
                ],
                "evaluation_criteria": [
                    "분석적 사고",
                    "비즈니스 이해도",
                    "의사결정 지원",
                    "전략적 제안"
                ]
            }
        ]
    
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_4_{self.chapter_id}",
            "question_type": "multiple_choice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "question_text": "ChatGPT의 주요 활용 분야가 아닌 것은?",
            "options": [
                "텍스트 요약 및 번역",
                "창작 및 아이디어 생성",
                "실시간 주식 거래",
                "질문 답변 및 설명"
            ],
            "correct_answer": 2,
            "explanation": "ChatGPT는 텍스트 기반 작업에 특화되어 있으며, 실시간 주식 거래와 같은 금융 거래는 직접 수행할 수 없습니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_4_{self.chapter_id}",
            "question_type": "prompt_practice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "scenario": "업무 효율화",
            "task_description": "회의록을 요약하고 액션 아이템을 추출하는 프롬프트를 작성하세요.",
            "requirements": [
                "요약 형식 지정",
                "액션 아이템 구조화",
                "우선순위 표시 요청"
            ],
            "evaluation_criteria": [
                "구조화된 출력 요청",
                "실무 적용 가능성",
                "명확한 지시사항"
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