# agents/quiz/chapters/chapter5_quiz.py
# 챕터 5: AI 시대의 문해력 퀴즈 생성

from typing import Dict, List, Any
from .base_quiz_chapter import BaseQuizChapter


class Chapter5Quiz(BaseQuizChapter):
    """챕터 5: AI 시대의 문해력 퀴즈 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.chapter_id = 5
        self.title = "AI 시대의 문해력"
        self.key_concepts = ["AI 윤리", "편향성", "개인정보보호", "인간-AI 협업", "디지털 리터러시"]
    
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "question": "AI 시대에 필요한 문해력으로 가장 중요한 것은?",
                "options": ["AI가 생성한 정보를 무조건 신뢰하기", "AI 도구를 비판적으로 활용하는 능력", "AI 기술을 완전히 배제하기", "AI에 모든 결정을 맡기기"],
                "correct_answer": 1,
                "explanation": "AI 시대의 문해력은 AI 도구를 비판적으로 평가하고 윤리적으로 활용하는 능력이 핵심입니다."
            },
            {
                "level": "low",
                "user_type": "beginner",
                "question": "AI 편향성이 발생하는 주요 원인은?",
                "options": ["AI가 너무 똑똑해서", "편향된 데이터로 학습해서", "AI가 감정이 있어서", "컴퓨터가 고장나서"],
                "correct_answer": 1,
                "explanation": "AI 편향성은 주로 편향된 데이터로 학습하거나 개발 과정에서 편견이 반영되어 발생합니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "개인정보를 보호하기 위해 AI 서비스 사용 시 주의할 점은?",
                "options": ["모든 정보를 자유롭게 공유", "개인정보를 AI에게 입력하지 않기", "AI만 믿고 사용", "개인정보 설정 무시"],
                "correct_answer": 1,
                "explanation": "AI 서비스 사용 시 개인정보나 민감한 정보를 입력하지 않는 것이 중요합니다."
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "question": "인간-AI 협업에서 인간이 더 잘할 수 있는 것은?",
                "options": ["빠른 계산", "대량 데이터 처리", "창의적 사고와 윤리적 판단", "24시간 작업"],
                "correct_answer": 2,
                "explanation": "인간은 창의적 사고, 윤리적 판단, 감정 이해 등에서 AI보다 뛰어난 능력을 가지고 있습니다."
            },
            {
                "level": "medium",
                "user_type": "business",
                "question": "기업에서 AI 윤리를 실천하기 위한 방법이 아닌 것은?",
                "options": ["AI 윤리 위원회 설치", "알고리즘 편향성 정기 감사", "AI 결과에 대한 무조건적 신뢰", "투명한 AI 개발 프로세스"],
                "correct_answer": 2,
                "explanation": "AI 결과에 대한 무조건적 신뢰는 위험하며, 지속적인 검증과 개선이 필요합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "알고리즘 편향성을 완화하기 위한 기술적 접근법은?",
                "options": ["데이터 다양성 확보", "공정성 제약 조건 통합", "편향성 탐지 도구 활용", "모든 것"],
                "correct_answer": 3,
                "explanation": "알고리즘 편향성 완화를 위해서는 데이터 다양성, 공정성 제약 조건, 탐지 도구 등 다양한 기술적 접근이 필요합니다."
            },
            {
                "level": "high",
                "user_type": "business",
                "question": "개인정보보호를 위한 프라이버시 보존 기술이 아닌 것은?",
                "options": ["차분 프라이버시", "동형 암호화", "연합 학습", "데이터 복제"],
                "correct_answer": 3,
                "explanation": "데이터 복제는 프라이버시 보존 기술이 아니며, 오히려 개인정보 유출 위험을 증가시킬 수 있습니다."
            }
        ]
    
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        return [
            {
                "level": "low",
                "user_type": "beginner",
                "scenario": "AI 윤리 학습",
                "task_description": "AI를 윤리적으로 사용하는 방법에 대해 설명해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 예시 포함 요청",
                    "일상생활에서 적용 가능한 방법",
                    "쉬운 언어로 설명 요청"
                ],
                "evaluation_criteria": [
                    "실용적인 가이드라인 요청",
                    "이해하기 쉬운 설명",
                    "구체적인 행동 방안"
                ]
            },
            {
                "level": "medium",
                "user_type": "beginner",
                "scenario": "개인정보 보호",
                "task_description": "AI 서비스 사용 시 개인정보를 보호하는 방법을 알려달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "구체적인 보호 방법 나열",
                    "위험 상황 예시 포함",
                    "실천 가능한 팁 제공"
                ],
                "evaluation_criteria": [
                    "실용성과 적용 가능성",
                    "포괄적인 보호 방안",
                    "명확한 지시사항"
                ]
            },
            {
                "level": "medium",
                "user_type": "business",
                "scenario": "AI 편향성 대응",
                "task_description": "기업에서 AI 편향성을 방지하고 대응하는 방안을 제시해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "편향성 탐지 방법",
                    "예방 및 완화 전략",
                    "조직적 대응 방안",
                    "지속적 모니터링 체계"
                ],
                "evaluation_criteria": [
                    "체계적인 접근법",
                    "실행 가능한 방안",
                    "비즈니스 맥락 고려",
                    "장기적 관점"
                ]
            },
            {
                "level": "high",
                "user_type": "business",
                "scenario": "AI 거버넌스 체계",
                "task_description": "조직의 AI 거버넌스 체계를 구축하기 위한 종합적인 계획을 수립해달라는 프롬프트를 작성하세요.",
                "requirements": [
                    "거버넌스 구조 및 역할",
                    "정책 및 가이드라인",
                    "위험 관리 체계",
                    "성과 측정 지표"
                ],
                "evaluation_criteria": [
                    "전략적 관점",
                    "포괄적 체계 설계",
                    "실행 가능성",
                    "지속 가능성"
                ]
            }
        ]
    
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_5_{self.chapter_id}",
            "question_type": "multiple_choice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "question_text": "AI 시대에 필요한 문해력으로 가장 중요한 것은?",
            "options": [
                "AI가 생성한 정보를 무조건 신뢰하기",
                "AI 도구를 비판적으로 활용하는 능력",
                "AI 기술을 완전히 배제하기",
                "AI에 모든 결정을 맡기기"
            ],
            "correct_answer": 1,
            "explanation": "AI 시대의 문해력은 AI 도구를 비판적으로 평가하고 윤리적으로 활용하는 능력이 핵심입니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": self._get_current_timestamp()
        }
    
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_5_{self.chapter_id}",
            "question_type": "prompt_practice",
            "chapter_id": self.chapter_id,
            "difficulty": "medium",
            "scenario": "AI 윤리 교육",
            "task_description": "AI를 윤리적으로 사용하는 방법에 대한 가이드를 작성해달라는 프롬프트를 작성하세요.",
            "requirements": [
                "구체적인 실천 방안",
                "일상생활 적용 가능",
                "윤리적 원칙 포함"
            ],
            "evaluation_criteria": [
                "실용성",
                "포괄성",
                "명확성"
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