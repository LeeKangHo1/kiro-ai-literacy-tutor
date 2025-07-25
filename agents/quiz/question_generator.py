# agents/quiz/question_generator.py
# 문제 생성 모듈

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime


class QuestionGenerator:
    """문제 생성 클래스 - 객관식 및 프롬프트 문제 생성"""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.chapter_content = self._load_chapter_content()
    
    def generate_multiple_choice_question(
        self, 
        chapter_id: int, 
        user_level: str, 
        user_type: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        객관식 문제 생성
        
        Args:
            chapter_id: 챕터 ID
            user_level: 사용자 수준 (low/medium/high)
            user_type: 사용자 유형 (beginner/business)
            difficulty: 난이도 (easy/medium/hard)
            
        Returns:
            Dict: 객관식 문제 데이터
        """
        try:
            # 챕터별 문제 템플릿 선택
            templates = self.question_templates.get(f"chapter_{chapter_id}", {}).get("multiple_choice", [])
            if not templates:
                return self._generate_default_multiple_choice(chapter_id, user_level, user_type)
            
            # 사용자 레벨과 유형에 맞는 템플릿 필터링
            suitable_templates = [
                t for t in templates 
                if t.get("level") == user_level and t.get("user_type") == user_type
            ]
            
            if not suitable_templates:
                suitable_templates = templates  # 적합한 템플릿이 없으면 전체에서 선택
            
            # 랜덤하게 템플릿 선택
            template = random.choice(suitable_templates)
            
            # 문제 생성
            question_data = {
                "question_id": f"mc_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question_type": "multiple_choice",
                "chapter_id": chapter_id,
                "difficulty": difficulty,
                "question_text": template["question"],
                "options": template["options"],
                "correct_answer": template["correct_answer"],
                "explanation": template["explanation"],
                "user_level": user_level,
                "user_type": user_type,
                "created_at": datetime.now().isoformat()
            }
            
            return question_data
            
        except Exception as e:
            print(f"객관식 문제 생성 오류: {e}")
            return self._generate_default_multiple_choice(chapter_id, user_level, user_type)
    
    def generate_prompt_question(
        self, 
        chapter_id: int, 
        user_level: str, 
        user_type: str,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        프롬프트 작성 문제 생성
        
        Args:
            chapter_id: 챕터 ID
            user_level: 사용자 수준 (low/medium/high)
            user_type: 사용자 유형 (beginner/business)
            difficulty: 난이도 (easy/medium/hard)
            
        Returns:
            Dict: 프롬프트 문제 데이터
        """
        try:
            # 챕터별 프롬프트 문제 템플릿 선택
            templates = self.question_templates.get(f"chapter_{chapter_id}", {}).get("prompt_practice", [])
            if not templates:
                return self._generate_default_prompt_question(chapter_id, user_level, user_type)
            
            # 사용자 레벨과 유형에 맞는 템플릿 필터링
            suitable_templates = [
                t for t in templates 
                if t.get("level") == user_level and t.get("user_type") == user_type
            ]
            
            if not suitable_templates:
                suitable_templates = templates
            
            # 랜덤하게 템플릿 선택
            template = random.choice(suitable_templates)
            
            # 프롬프트 문제 생성
            question_data = {
                "question_id": f"prompt_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question_type": "prompt_practice",
                "chapter_id": chapter_id,
                "difficulty": difficulty,
                "scenario": template["scenario"],
                "task_description": template["task_description"],
                "requirements": template["requirements"],
                "evaluation_criteria": template["evaluation_criteria"],
                "sample_prompts": template.get("sample_prompts", []),
                "user_level": user_level,
                "user_type": user_type,
                "created_at": datetime.now().isoformat()
            }
            
            return question_data
            
        except Exception as e:
            print(f"프롬프트 문제 생성 오류: {e}")
            return self._generate_default_prompt_question(chapter_id, user_level, user_type)
    
    def _generate_default_multiple_choice(self, chapter_id: int, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        default_questions = {
            1: {  # AI는 무엇인가?
                "question": "다음 중 AI(인공지능)에 대한 설명으로 가장 적절한 것은?",
                "options": [
                    "컴퓨터가 인간처럼 생각하고 학습할 수 있는 기술",
                    "단순히 프로그래밍된 명령을 실행하는 소프트웨어",
                    "인터넷에 연결된 모든 컴퓨터 시스템",
                    "데이터를 저장하고 관리하는 데이터베이스"
                ],
                "correct_answer": 0,
                "explanation": "AI는 컴퓨터가 인간의 지능적 행동을 모방하여 학습, 추론, 문제해결 등을 수행할 수 있는 기술입니다."
            },
            3: {  # 프롬프트란 무엇인가?
                "question": "효과적인 프롬프트 작성을 위한 핵심 요소가 아닌 것은?",
                "options": [
                    "명확하고 구체적인 지시사항",
                    "적절한 맥락 정보 제공",
                    "복잡하고 어려운 전문용어 사용",
                    "원하는 출력 형식 명시"
                ],
                "correct_answer": 2,
                "explanation": "효과적인 프롬프트는 명확하고 이해하기 쉬운 언어를 사용해야 하며, 불필요하게 복잡한 전문용어는 피해야 합니다."
            }
        }
        
        default_q = default_questions.get(chapter_id, default_questions[1])
        
        return {
            "question_id": f"mc_default_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "multiple_choice",
            "chapter_id": chapter_id,
            "difficulty": "medium",
            "question_text": default_q["question"],
            "options": default_q["options"],
            "correct_answer": default_q["correct_answer"],
            "explanation": default_q["explanation"],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_default_prompt_question(self, chapter_id: int, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        default_prompts = {
            3: {  # 프롬프트란 무엇인가?
                "scenario": "온라인 쇼핑몰 고객 서비스",
                "task_description": "고객의 불만사항을 해결하는 친절한 고객서비스 담당자 역할을 하는 프롬프트를 작성하세요.",
                "requirements": [
                    "친근하고 공감적인 톤 사용",
                    "구체적인 해결책 제시",
                    "고객 만족을 위한 추가 서비스 제안"
                ],
                "evaluation_criteria": [
                    "역할 정의의 명확성",
                    "톤과 스타일의 적절성",
                    "문제 해결 접근법의 체계성"
                ]
            }
        }
        
        default_p = default_prompts.get(chapter_id, default_prompts[3])
        
        return {
            "question_id": f"prompt_default_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "prompt_practice",
            "chapter_id": chapter_id,
            "difficulty": "medium",
            "scenario": default_p["scenario"],
            "task_description": default_p["task_description"],
            "requirements": default_p["requirements"],
            "evaluation_criteria": default_p["evaluation_criteria"],
            "sample_prompts": [],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _load_question_templates(self) -> Dict[str, Any]:
        """문제 템플릿 로드 (향후 외부 파일에서 로드 가능)"""
        return {
            "chapter_1": {
                "multiple_choice": [
                    {
                        "level": "low",
                        "user_type": "beginner",
                        "question": "AI가 무엇의 줄임말인가요?",
                        "options": ["Artificial Intelligence", "Advanced Internet", "Automatic Information", "Applied Integration"],
                        "correct_answer": 0,
                        "explanation": "AI는 Artificial Intelligence(인공지능)의 줄임말입니다."
                    },
                    {
                        "level": "medium",
                        "user_type": "business",
                        "question": "비즈니스에서 AI 활용의 주요 장점은 무엇인가요?",
                        "options": ["비용 절감", "업무 자동화", "데이터 기반 의사결정", "모든 것"],
                        "correct_answer": 3,
                        "explanation": "AI는 비용 절감, 업무 자동화, 데이터 기반 의사결정 등 다양한 비즈니스 가치를 제공합니다."
                    }
                ]
            },
            "chapter_3": {
                "multiple_choice": [
                    {
                        "level": "low",
                        "user_type": "beginner",
                        "question": "프롬프트란 무엇인가요?",
                        "options": ["AI에게 주는 명령이나 질문", "컴퓨터 프로그램", "데이터베이스", "웹사이트"],
                        "correct_answer": 0,
                        "explanation": "프롬프트는 AI에게 원하는 작업을 수행하도록 하는 명령이나 질문입니다."
                    }
                ],
                "prompt_practice": [
                    {
                        "level": "medium",
                        "user_type": "business",
                        "scenario": "마케팅 캠페인 기획",
                        "task_description": "신제품 출시를 위한 마케팅 캠페인 아이디어를 생성하는 프롬프트를 작성하세요.",
                        "requirements": [
                            "타겟 고객층 명시",
                            "제품 특징 포함",
                            "창의적인 아이디어 요청"
                        ],
                        "evaluation_criteria": [
                            "구체성과 명확성",
                            "창의성 유도 요소",
                            "실행 가능성"
                        ]
                    }
                ]
            }
        }
    
    def _load_chapter_content(self) -> Dict[str, Any]:
        """챕터 콘텐츠 정보 로드"""
        return {
            1: {
                "title": "AI는 무엇인가?",
                "key_concepts": ["인공지능", "머신러닝", "딥러닝", "AI vs ML vs DL"]
            },
            3: {
                "title": "프롬프트란 무엇인가?",
                "key_concepts": ["프롬프트 엔지니어링", "명령어 구조", "맥락 제공", "출력 형식"]
            }
        }