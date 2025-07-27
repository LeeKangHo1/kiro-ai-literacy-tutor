# agents/quiz/chapters/chapter1_quiz.py
# 챕터 1: AI는 무엇인가? 퀴즈 생성

from typing import Dict, List, Any
from .base_quiz_chapter import BaseQuizChapter


class Chapter1Quiz(BaseQuizChapter):
    """챕터 1: AI는 무엇인가? 퀴즈 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 1
        self.title = "AI는 무엇인가?"
        self.key_concepts = ["AI", "ML", "DL", "약한 AI", "강한 AI", "지도학습", "비지도학습", "강화학습"]
    
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "question": "AI가 무엇의 줄임말인가요?",
                "options": ["Artificial Intelligence", "Advanced Internet", "Automatic Information", "Applied Integration"],
                "correct_answer": 0,
                "explanation": "AI는 Artificial Intelligence(인공지능)의 줄임말입니다."
            },
            {
                "level": "low",
                "user_type": "beginner",
                "question": "다음 중 AI, ML, DL의 관계를 올바르게 나타낸 것은?",
                "options": ["AI = ML = DL", "AI > ML > DL", "DL > ML > AI", "ML > AI > DL"],
                "correct_answer": 1,
                "explanation": "AI가 가장 큰 개념이고, 그 안에 ML(머신러닝)이 있으며, ML 안에 DL(딥러닝)이 포함됩니다."
            },
            {
                "level": "low",
                "user_type": "beginner",
                "question": "다음 중 약한 AI의 예시가 아닌 것은?",
                "options": ["체스 게임 AI", "음성 인식 AI", "번역 AI", "모든 일을 할 수 있는 AI"],
                "correct_answer": 3,
                "explanation": "약한 AI는 특정 작업에만 특화된 AI입니다. 모든 일을 할 수 있는 AI는 강한 AI(AGI)로, 아직 존재하지 않습니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "머신러닝에서 '지도학습'의 특징은 무엇인가요?",
                "options": ["정답이 없는 데이터로 학습", "보상과 벌점으로 학습", "정답이 있는 데이터로 학습", "사람이 직접 가르침"],
                "correct_answer": 2,
                "explanation": "지도학습은 입력과 정답(레이블)이 쌍으로 제공된 데이터를 사용하여 학습하는 방법입니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "강화학습이 주로 사용되는 분야는?",
                "options": ["이메일 분류", "고객 그룹 분석", "게임 AI", "번역"],
                "correct_answer": 2,
                "explanation": "강화학습은 시행착오를 통해 최적의 행동을 학습하는 방법으로, 게임 AI에서 많이 활용됩니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "비즈니스에서 AI 활용의 주요 장점은 무엇인가요?",
                "options": ["비용 절감", "업무 자동화", "데이터 기반 의사결정", "모든 것"],
                "correct_answer": 3,
                "explanation": "AI는 비용 절감, 업무 자동화, 데이터 기반 의사결정 등 다양한 비즈니스 가치를 제공합니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "제조업에서 AI를 활용한 품질 관리의 주요 방법은?",
                "options": ["수작업 검사", "컴퓨터 비전을 통한 자동 검출", "랜덤 샘플링", "고객 피드백 분석"],
                "correct_answer": 1,
                "explanation": "제조업에서는 컴퓨터 비전 기술을 활용하여 제품의 결함을 자동으로 검출하는 AI 품질 관리 시스템을 사용합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "금융 분야에서 AI 기반 사기 탐지 시스템의 핵심 원리는?",
                "options": ["규칙 기반 필터링", "거래 패턴 분석을 통한 이상 탐지", "고객 신용도 평가", "시장 동향 분석"],
                "correct_answer": 1,
                "explanation": "AI 사기 탐지 시스템은 정상적인 거래 패턴을 학습하고, 이와 다른 이상한 패턴을 탐지하여 사기를 방지합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "의료 분야에서 AI 활용 시 가장 중요한 고려사항은?",
                "options": ["처리 속도", "비용 효율성", "정확성과 안전성", "사용 편의성"],
                "correct_answer": 2,
                "explanation": "의료 분야에서는 환자의 생명과 직결되므로 AI 시스템의 정확성과 안전성이 가장 중요한 고려사항입니다."
            }
        ]
    
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "scenario": "AI 개념 학습",
                "task_description": "친구에게 AI와 머신러닝의 차이점을 쉽게 설명해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "쉬운 언어 사용 요청",
                    "구체적인 예시 포함 요청",
                    "친근한 톤으로 설명 요청"
                ],
                "evaluation_criteria": [
                    "명확하고 이해하기 쉬운 설명 요청",
                    "적절한 예시 활용",
                    "친근한 톤 지정"
                ]
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "scenario": "AI 활용 사례 탐색",
                "task_description": "일상생활에서 AI가 사용되는 사례 10가지를 찾아달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 개수 지정 (10가지)",
                    "일상생활 범위 명시",
                    "각 사례별 간단한 설명 요청"
                ],
                "evaluation_criteria": [
                    "구체적인 요구사항 명시",
                    "범위 제한의 적절성",
                    "출력 형식 지정"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "비즈니스 AI 도입 계획",
                "task_description": "소규모 온라인 쇼핑몰에서 AI를 도입할 수 있는 방안을 제안해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "비즈니스 규모 명시 (소규모)",
                    "업종 명시 (온라인 쇼핑몰)",
                    "구체적인 도입 방안과 기대 효과 요청",
                    "예산과 기술적 제약 고려 요청"
                ],
                "evaluation_criteria": [
                    "비즈니스 맥락 제공",
                    "실용적인 제안 요청",
                    "제약 조건 고려",
                    "구체적인 결과물 요청"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "AI 윤리 가이드라인 수립",
                "task_description": "회사에서 AI 도입 시 고려해야 할 윤리적 가이드라인을 작성해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "기업 환경에서의 AI 윤리 중점",
                    "구체적인 가이드라인 항목 요청",
                    "실행 가능한 방안 포함",
                    "법적, 사회적 책임 고려"
                ],
                "evaluation_criteria": [
                    "전문적인 관점 요청",
                    "포괄적인 윤리 이슈 다룸",
                    "실행 가능성 고려",
                    "구조화된 출력 요청"
                ]
            }
        ]
    
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_1_{self.chapter_id}",
            "question_type": "multiple_choice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "question_text": "다음 중 AI, 머신러닝, 딥러닝의 관계를 가장 정확하게 설명한 것은?",
            "options": [
                "세 개념은 모두 동일한 의미이다",
                "AI > 머신러닝 > 딥러닝 순서로 포함관계이다",
                "딥러닝 > 머신러닝 > AI 순서로 포함관계이다",
                "세 개념은 서로 독립적이다"
            ],
            "correct_answer": 1,
            "explanation": "AI가 가장 큰 개념이고, 그 안에 머신러닝이 포함되며, 머신러닝 안에 딥러닝이 포함되는 포함관계입니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_1_{self.chapter_id}",
            "question_type": "prompt_practice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "scenario": "AI 개념 설명",
            "task_description": "AI의 기본 개념을 초보자에게 설명하는 프롬프트를 작성하세요.",
            "requirements": [
                "쉬운 언어 사용",
                "구체적인 예시 포함",
                "단계별 설명 요청"
            ],
            "evaluation_criteria": [
                "명확성과 이해도",
                "적절한 예시 활용",
                "체계적인 구성"
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