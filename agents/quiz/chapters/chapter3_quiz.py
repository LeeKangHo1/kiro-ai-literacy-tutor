# agents/quiz/chapters/chapter3_quiz.py
# 챕터 3: 프롬프트란 무엇인가? 퀴즈 생성

from typing import Dict, List, Any
from .base_quiz_chapter import BaseQuizChapter


class Chapter3Quiz(BaseQuizChapter):
    """챕터 3: 프롬프트란 무엇인가? 퀴즈 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 3
        self.title = "프롬프트란 무엇인가?"
        self.key_concepts = ["프롬프트", "프롬프트 엔지니어링", "Few-shot", "Chain-of-Thought", "역할 부여"]
    
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "question": "프롬프트란 무엇인가요?",
                "options": ["AI에게 주는 명령이나 질문", "컴퓨터 프로그램", "데이터베이스", "웹사이트"],
                "correct_answer": 0,
                "explanation": "프롬프트는 AI에게 원하는 작업을 수행하도록 하는 명령이나 질문입니다."
            },
            {
                "level": "low",
                "user_type": "beginner",
                "question": "좋은 프롬프트의 특징이 아닌 것은?",
                "options": ["명확하고 구체적", "적절한 예시 포함", "모호하고 추상적", "역할 정의 포함"],
                "correct_answer": 2,
                "explanation": "좋은 프롬프트는 명확하고 구체적이어야 하며, 모호하고 추상적인 표현은 피해야 합니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "프롬프트에서 '역할 부여'의 예시로 적절한 것은?",
                "options": ["글을 써줘", "너는 친절한 선생님이야", "500자로 써줘", "목록으로 정리해줘"],
                "correct_answer": 1,
                "explanation": "'너는 친절한 선생님이야'는 AI에게 특정 역할을 부여하는 프롬프트 기법입니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "프롬프트 엔지니어링에서 'Few-shot Learning'이란?",
                "options": ["한 번만 질문하기", "몇 개의 예시를 제공하기", "짧게 질문하기", "여러 번 반복하기"],
                "correct_answer": 1,
                "explanation": "Few-shot Learning은 AI가 패턴을 학습할 수 있도록 몇 개의 예시를 제공하는 기법입니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "비즈니스에서 프롬프트 표준화의 주요 이점은?",
                "options": ["비용 절감만", "일관된 결과 보장", "속도 향상만", "개인화 증대"],
                "correct_answer": 1,
                "explanation": "프롬프트 표준화는 팀 내에서 일관된 품질의 결과를 보장하는 주요 이점이 있습니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "Chain-of-Thought 프롬프트 기법의 핵심은?",
                "options": ["빠른 답변 유도", "단계별 사고 과정 유도", "짧은 응답 생성", "감정적 반응 유도"],
                "correct_answer": 1,
                "explanation": "Chain-of-Thought는 AI가 단계별로 사고하도록 유도하여 복잡한 문제 해결에 효과적인 기법입니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "프롬프트 최적화에서 가장 중요한 평가 기준은?",
                "options": ["응답 속도", "토큰 사용량", "정확성과 관련성", "응답 길이"],
                "correct_answer": 2,
                "explanation": "프롬프트 최적화에서는 응답의 정확성과 요구사항과의 관련성이 가장 중요한 평가 기준입니다."
            }
        ]
    
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "scenario": "학습 도우미",
                "task_description": "어려운 수학 개념을 쉽게 설명해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 수학 개념 명시",
                    "설명 대상 연령 지정",
                    "쉬운 예시 요청 포함"
                ],
                "evaluation_criteria": [
                    "명확한 요구사항 명시",
                    "적절한 난이도 설정",
                    "이해하기 쉬운 설명 요청"
                ]
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "scenario": "창작 활동",
                "task_description": "특정 주제로 짧은 이야기를 써달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 주제와 설정 제공",
                    "이야기 길이 지정",
                    "톤앤매너 명시"
                ],
                "evaluation_criteria": [
                    "창의성 유도 요소",
                    "구체적인 지시사항",
                    "적절한 제약 조건"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "마케팅 캠페인 기획",
                "task_description": "신제품 출시를 위한 마케팅 캠페인 아이디어를 생성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "타겟 고객층 명시",
                    "제품 특징 포함",
                    "창의적인 아이디어 요청",
                    "예산 범위 고려"
                ],
                "evaluation_criteria": [
                    "구체성과 명확성",
                    "창의성 유도 요소",
                    "실행 가능성",
                    "비즈니스 맥락 고려"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "고객 서비스 개선",
                "task_description": "고객 불만 처리를 위한 표준 응답 템플릿을 생성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "공감적 톤 요청",
                    "해결 방안 포함",
                    "브랜드 가치 반영",
                    "후속 조치 안내"
                ],
                "evaluation_criteria": [
                    "고객 중심적 접근",
                    "전문적 톤앤매너",
                    "실용적 해결책",
                    "브랜드 일관성"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "데이터 분석 보고서",
                "task_description": "복잡한 데이터 분석 결과를 경영진에게 보고하는 요약문을 작성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "핵심 인사이트 강조",
                    "비즈니스 임팩트 명시",
                    "액션 아이템 포함",
                    "경영진 수준의 언어 사용"
                ],
                "evaluation_criteria": [
                    "전략적 관점 반영",
                    "명확한 구조화",
                    "의사결정 지원 정보",
                    "전문적 커뮤니케이션"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "AI 도구 활용 가이드",
                "task_description": "팀원들을 위한 ChatGPT 활용 가이드라인을 작성하는 프롬프트를 작성하세요.",
                "requirements": [
                    "업무별 활용 사례",
                    "주의사항 및 제한사항",
                    "품질 관리 방법",
                    "윤리적 고려사항"
                ],
                "evaluation_criteria": [
                    "포괄적 가이드라인",
                    "실무 적용 가능성",
                    "리스크 관리 고려",
                    "지속 가능한 활용 방안"
                ]
            }
        ]
    
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_3_{self.chapter_id}",
            "question_type": "multiple_choice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "question_text": "프롬프트란 무엇인가요?",
            "options": ["AI에게 주는 명령이나 질문", "컴퓨터 프로그램", "데이터베이스", "웹사이트"],
            "correct_answer": 0,
            "explanation": "프롬프트는 AI에게 원하는 작업을 수행하도록 하는 명령이나 질문입니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_3_{self.chapter_id}",
            "question_type": "prompt_practice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "scenario": "학습 지원 서비스",
            "task_description": "학생들의 학습 질문에 답변하는 친절한 튜터 역할을 하는 프롬프트를 작성하세요.",
            "requirements": [
                "학습자 수준에 맞는 설명",
                "단계별 설명 방식",
                "이해도 확인 질문 포함",
                "격려와 동기부여 메시지"
            ],
            "evaluation_criteria": [
                "교육적 접근법의 적절성",
                "학습자 중심적 설계",
                "명확한 역할 정의",
                "상호작용 유도 요소"
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