# agents/quiz/question_generator_new.py
# 리팩토링된 문제 생성 모듈 - 챕터별 분리

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from workflow.state_management import TutorState, StateManager
from .chapters.chapter1_quiz import Chapter1Quiz
from .chapters.chapter2_quiz import Chapter2Quiz
from .chapters.chapter3_quiz import Chapter3Quiz
from .chapters.chapter4_quiz import Chapter4Quiz
from .chapters.chapter5_quiz import Chapter5Quiz


class QuestionGenerator:
    """문제 생성 클래스 - 객관식 및 프롬프트 문제 생성 (리팩토링 버전)"""
    
    def __init__(self):
        # 챕터별 퀴즈 생성기 인스턴스
        self.quiz_generators = {
            1: Chapter1Quiz(),
            2: Chapter2Quiz(),
            3: Chapter3Quiz(),
            4: Chapter4Quiz(),
            5: Chapter5Quiz()
        }
        
        # 레거시 문제 (모든 챕터가 분리되어 더 이상 필요 없음)
        self.legacy_questions = {}
        
        # 레거시 프롬프트 문제 (현재 없음)
        self.legacy_prompts = {}
    
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
            # 새로운 챕터별 생성기 사용
            if chapter_id in self.quiz_generators:
                generator = self.quiz_generators[chapter_id]
                return generator.generate_multiple_choice_question(user_level, user_type, difficulty)
            
            # 레거시 문제 사용
            elif chapter_id in self.legacy_questions:
                return self._generate_legacy_multiple_choice(chapter_id, user_level, user_type, difficulty)
            
            # 기본 문제 생성
            else:
                return self._generate_default_multiple_choice(chapter_id, user_level, user_type)
                
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
            # 새로운 챕터별 생성기 사용
            if chapter_id in self.quiz_generators:
                generator = self.quiz_generators[chapter_id]
                return generator.generate_prompt_question(user_level, user_type, difficulty)
            
            # 레거시 프롬프트 문제 사용
            elif chapter_id in self.legacy_prompts:
                return self._generate_legacy_prompt_question(chapter_id, user_level, user_type, difficulty)
            
            # 기본 프롬프트 문제 생성
            else:
                return self._generate_default_prompt_question(chapter_id, user_level, user_type)
                
        except Exception as e:
            print(f"프롬프트 문제 생성 오류: {e}")
            return self._generate_default_prompt_question(chapter_id, user_level, user_type)
    
    def _generate_legacy_multiple_choice(self, chapter_id: int, user_level: str, 
                                        user_type: str, difficulty: str) -> Dict[str, Any]:
        """레거시 객관식 문제 생성"""
        question_data = self.legacy_questions[chapter_id]
        
        return {
            "question_id": f"mc_legacy_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "multiple_choice",
            "chapter_id": chapter_id,
            "difficulty": difficulty,
            "question_text": question_data["question"],
            "options": question_data["options"],
            "correct_answer": question_data["correct_answer"],
            "explanation": question_data["explanation"],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_legacy_prompt_question(self, chapter_id: int, user_level: str, 
                                        user_type: str, difficulty: str) -> Dict[str, Any]:
        """레거시 프롬프트 문제 생성"""
        prompt_data = self.legacy_prompts[chapter_id]
        
        return {
            "question_id": f"prompt_legacy_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "prompt_practice",
            "chapter_id": chapter_id,
            "difficulty": difficulty,
            "scenario": prompt_data["scenario"],
            "task_description": prompt_data["task_description"],
            "requirements": prompt_data["requirements"],
            "evaluation_criteria": prompt_data["evaluation_criteria"],
            "sample_prompts": [],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_default_multiple_choice(self, chapter_id: int, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 객관식 문제 생성"""
        return {
            "question_id": f"mc_default_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "multiple_choice",
            "chapter_id": chapter_id,
            "difficulty": "medium",
            "question_text": f"챕터 {chapter_id}에 대한 기본 문제입니다.",
            "options": ["옵션 1", "옵션 2", "옵션 3", "옵션 4"],
            "correct_answer": 0,
            "explanation": f"챕터 {chapter_id}의 기본 설명입니다.",
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_default_prompt_question(self, chapter_id: int, user_level: str, user_type: str) -> Dict[str, Any]:
        """기본 프롬프트 문제 생성"""
        return {
            "question_id": f"prompt_default_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_type": "prompt_practice",
            "chapter_id": chapter_id,
            "difficulty": "medium",
            "scenario": f"챕터 {chapter_id} 학습",
            "task_description": f"챕터 {chapter_id} 내용과 관련된 프롬프트를 작성하세요.",
            "requirements": [
                "명확한 지시사항",
                "구체적인 요구사항",
                "적절한 예시 포함"
            ],
            "evaluation_criteria": [
                "명확성",
                "구체성",
                "실용성"
            ],
            "sample_prompts": [],
            "user_level": user_level,
            "user_type": user_type,
            "created_at": datetime.now().isoformat()
        }
    
    def generate_quiz_with_ui(self, state: TutorState, quiz_type: str = "multiple_choice") -> TutorState:
        """UI 모드 관리와 함께 퀴즈 생성"""
        try:
            # 사용자 입력 수신 이벤트 처리 (로딩 상태로 전환)
            state = StateManager.handle_ui_transition(
                state, "user_input_received", "quiz_generator"
            )
            
            # 퀴즈 생성
            if quiz_type == "multiple_choice":
                quiz_data = self.generate_multiple_choice_question(
                    state['current_chapter'],
                    state['user_level'],
                    state['user_type']
                )
            else:  # prompt_practice
                quiz_data = self.generate_prompt_question(
                    state['current_chapter'],
                    state['user_level'],
                    state['user_type']
                )
            
            # 시스템 메시지 생성
            system_message = self._format_quiz_for_display(quiz_data)
            
            # 상태 업데이트
            state['system_message'] = system_message
            state['current_stage'] = 'quiz'
            
            # 대화 기록 추가
            state = StateManager.add_conversation(
                state,
                "quiz_generator",
                state.get('user_message', ''),
                system_message,
                {'quiz_data': quiz_data}
            )
            
            # UI 상태 업데이트 (퀴즈 모드로 전환)
            ui_context = {
                'quiz_type': quiz_type,
                'question': quiz_data.get('question_text') or quiz_data.get('task_description'),
                'options': quiz_data.get('options', []),
                'hint_available': True,
                'title': '문제 풀이',
                'quiz_info': quiz_data
            }
            
            state = StateManager.handle_ui_transition(
                state, "agent_response_ready", "quiz_generator", ui_context
            )
            
        except Exception as e:
            # 오류 처리
            state['system_message'] = f"퀴즈 생성 중 오류가 발생했습니다: {str(e)}"
            state = StateManager.handle_ui_transition(
                state, "error_occurred", "quiz_generator",
                {'error_message': str(e)}
            )
        
        return state
    
    def _format_quiz_for_display(self, quiz_data: Dict[str, Any]) -> str:
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