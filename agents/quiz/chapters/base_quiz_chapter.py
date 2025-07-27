# agents/quiz/chapters/base_quiz_chapter.py
# 퀴즈 챕터 기본 클래스

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import random


class BaseQuizChapter(ABC):
    """퀴즈 챕터 기본 클래스"""
    
    def __init__(self):
        self.chapter_id = None
        self.title = None
        self.key_concepts = []
        self.multiple_choice_questions = []
        self.prompt_practice_questions = []
    
    @abstractmethod
    def get_multiple_choice_templates(self) -> List[Dict[str, Any]]:
        """객관식 문제 템플릿 반환"""
        pass
    
    @abstractmethod
    def get_prompt_practice_templates(self) -> List[Dict[str, Any]]:
        """프롬프트 실습 문제 템플릿 반환"""
        pass
    
    def generate_multiple_choice_question(self, user_level: str, user_type: str, 
                                        difficulty: str = "medium") -> Dict[str, Any]:
        """객관식 문제 생성"""
        try:
            templates = self.get_multiple_choice_templates()
            
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
                "question_id": f"mc_{self.chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question_type": "multiple_choice",
                "chapter_id": self.chapter_id,
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
            return self._generate_default_multiple_choice(user_level, user_type)
    
    def generate_prompt_question(self, user_level: str, user_type: str, 
                                difficulty: str = "medium") -> Dict[str, Any]:
        """프롬프트 실습 문제 생성"""
        try:
            templates = self.get_prompt_practice_templates()
            
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
                "question_id": f"prompt_{self.chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "question_type": "prompt_practice",
                "chapter_id": self.chapter_id,
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
            return self._generate_default_prompt_question(user_level, user_type)
    
    @abstractmethod
    def _generate_default_multiple_choice(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        pass
    
    @abstractmethod
    def _generate_default_prompt_question(self, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        pass
    
    def format_quiz_for_display(self, quiz_data: Dict[str, Any]) -> str:
        """퀴즈를 표시용 텍스트로 포맷팅"""
        formatted_parts = []
        
        if quiz_data['question_type'] == 'multiple_choice':
            # 객관식 문제 포맷팅
            formatted_parts.append(f"## 📝 객관식 문제\n")
            formatted_parts.append(f"**문제:** {quiz_data['question_text']}\n")
            
            for i, option in enumerate(quiz_data['options']):
                formatted_parts.append(f"{i+1}. {option}")
            
            formatted_parts.append("\n정답을 선택해주세요.")
            
        else:  # prompt_practice
            # 프롬프트 실습 문제 포맷팅
            formatted_parts.append(f"## ✍️ 프롬프트 작성 실습\n")
            formatted_parts.append(f"**상황:** {quiz_data['scenario']}\n")
            formatted_parts.append(f"**과제:** {quiz_data['task_description']}\n")
            
            if quiz_data.get('requirements'):
                formatted_parts.append("**요구사항:**")
                for req in quiz_data['requirements']:
                    formatted_parts.append(f"• {req}")
            
            formatted_parts.append("\n프롬프트를 작성해주세요.")
        
        return "\n".join(formatted_parts)