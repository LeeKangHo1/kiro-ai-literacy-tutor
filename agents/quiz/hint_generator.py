# agents/quiz/hint_generator.py
# 힌트 생성 모듈

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class HintGenerator:
    """힌트 생성 클래스 - 문제별 맞춤 힌트 생성"""
    
    def __init__(self):
        self.hint_templates = self._load_hint_templates()
    
    def generate_hint(
        self, 
        question_data: Dict[str, Any], 
        hint_level: int = 1,
        user_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        문제별 맞춤 힌트 생성
        
        Args:
            question_data: 문제 데이터
            hint_level: 힌트 단계 (1: 가벼운 힌트, 2: 중간 힌트, 3: 강한 힌트)
            user_level: 사용자 수준
            
        Returns:
            Dict: 힌트 데이터
        """
        try:
            question_type = question_data.get("question_type", "multiple_choice")
            chapter_id = question_data.get("chapter_id", 1)
            
            if question_type == "multiple_choice":
                return self._generate_multiple_choice_hint(question_data, hint_level, user_level)
            elif question_type == "prompt_practice":
                return self._generate_prompt_hint(question_data, hint_level, user_level)
            else:
                return self._generate_default_hint(question_data, hint_level)
                
        except Exception as e:
            print(f"힌트 생성 오류: {e}")
            return self._generate_default_hint(question_data, hint_level)
    
    def _generate_multiple_choice_hint(
        self, 
        question_data: Dict[str, Any], 
        hint_level: int,
        user_level: str
    ) -> Dict[str, Any]:
        """객관식 문제 힌트 생성"""
        question_text = question_data.get("question_text", "")
        options = question_data.get("options", [])
        correct_answer = question_data.get("correct_answer", 0)
        chapter_id = question_data.get("chapter_id", 1)
        
        # 힌트 레벨별 전략
        if hint_level == 1:
            # 가벼운 힌트: 문제 해결 접근법 제시
            hint_text = self._get_approach_hint(chapter_id, question_text, user_level)
        elif hint_level == 2:
            # 중간 힌트: 잘못된 선택지 일부 제거
            hint_text = self._get_elimination_hint(options, correct_answer)
        else:
            # 강한 힌트: 정답에 가까운 설명
            hint_text = self._get_direct_hint(question_data)
        
        return {
            "hint_id": f"hint_{question_data.get('question_id', 'unknown')}_{hint_level}",
            "question_id": question_data.get("question_id"),
            "hint_level": hint_level,
            "hint_text": hint_text,
            "hint_type": "multiple_choice",
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_prompt_hint(
        self, 
        question_data: Dict[str, Any], 
        hint_level: int,
        user_level: str
    ) -> Dict[str, Any]:
        """프롬프트 문제 힌트 생성"""
        scenario = question_data.get("scenario", "")
        requirements = question_data.get("requirements", [])
        chapter_id = question_data.get("chapter_id", 3)
        
        # 힌트 레벨별 전략
        if hint_level == 1:
            # 가벼운 힌트: 프롬프트 구조 가이드
            hint_text = self._get_structure_hint(scenario, user_level)
        elif hint_level == 2:
            # 중간 힌트: 구체적인 요소 제안
            hint_text = self._get_element_hint(requirements, scenario)
        else:
            # 강한 힌트: 예시 프롬프트 일부 제공
            hint_text = self._get_example_hint(question_data)
        
        return {
            "hint_id": f"hint_{question_data.get('question_id', 'unknown')}_{hint_level}",
            "question_id": question_data.get("question_id"),
            "hint_level": hint_level,
            "hint_text": hint_text,
            "hint_type": "prompt_practice",
            "created_at": datetime.now().isoformat()
        }
    
    def _get_approach_hint(self, chapter_id: int, question_text: str, user_level: str) -> str:
        """문제 접근법 힌트"""
        approach_hints = {
            1: {  # AI는 무엇인가?
                "low": "AI의 기본 정의를 생각해보세요. 인공지능이 무엇을 할 수 있는지 떠올려보세요.",
                "medium": "AI, ML, DL의 관계를 생각해보고, 각각의 특징을 비교해보세요.",
                "high": "AI의 핵심 기능과 한계를 고려하여 가장 포괄적이고 정확한 정의를 찾아보세요."
            },
            3: {  # 프롬프트란 무엇인가?
                "low": "프롬프트가 AI와 소통하는 방법이라는 점을 생각해보세요.",
                "medium": "효과적인 프롬프트의 구성 요소들을 하나씩 생각해보세요.",
                "high": "프롬프트 엔지니어링의 핵심 원칙들을 고려해보세요."
            }
        }
        
        return approach_hints.get(chapter_id, {}).get(user_level, 
            "문제를 차근차근 읽어보고 핵심 키워드를 찾아보세요.")
    
    def _get_elimination_hint(self, options: List[str], correct_answer: int) -> str:
        """선택지 제거 힌트"""
        if len(options) <= 2:
            return "남은 선택지들을 신중히 비교해보세요."
        
        # 정답이 아닌 선택지 중 하나를 제거 힌트로 제공
        wrong_options = [i for i in range(len(options)) if i != correct_answer]
        if wrong_options:
            eliminate_idx = wrong_options[0]  # 첫 번째 오답 제거
            return f"선택지 {eliminate_idx + 1}번은 정답이 아닙니다. 나머지 선택지들을 다시 검토해보세요."
        
        return "각 선택지를 문제와 연결해서 생각해보세요."
    
    def _get_direct_hint(self, question_data: Dict[str, Any]) -> str:
        """직접적인 힌트"""
        explanation = question_data.get("explanation", "")
        if explanation:
            # 설명의 일부를 힌트로 제공
            return f"힌트: {explanation[:50]}..."
        
        correct_answer = question_data.get("correct_answer", 0)
        options = question_data.get("options", [])
        
        if correct_answer < len(options):
            return f"정답은 '{options[correct_answer]}'와 관련이 있습니다."
        
        return "문제의 핵심 개념을 다시 한 번 생각해보세요."
    
    def _get_structure_hint(self, scenario: str, user_level: str) -> str:
        """프롬프트 구조 힌트"""
        structure_hints = {
            "low": """
프롬프트 작성 기본 구조:
1. 역할 정의: "당신은 ~입니다"
2. 상황 설명: 주어진 시나리오 포함
3. 구체적 요청: 무엇을 해달라고 할지 명확히
4. 출력 형식: 어떤 형태로 답변받고 싶은지
            """,
            "medium": """
효과적인 프롬프트 요소들:
- 명확한 역할과 맥락 설정
- 구체적이고 측정 가능한 요구사항
- 예상 출력 형식 및 길이 지정
- 제약사항이나 주의사항 명시
            """,
            "high": """
고급 프롬프트 엔지니어링 기법:
- Chain of Thought 적용
- Few-shot learning 예시 활용
- 단계별 추론 과정 요청
- 검증 및 자기 평가 요소 포함
            """
        }
        
        return structure_hints.get(user_level, structure_hints["medium"])
    
    def _get_element_hint(self, requirements: List[str], scenario: str) -> str:
        """구체적 요소 힌트"""
        if not requirements:
            return "주어진 시나리오에 맞는 구체적인 요소들을 포함해보세요."
        
        hint_text = "다음 요소들을 프롬프트에 포함해보세요:\n"
        for i, req in enumerate(requirements[:2], 1):  # 처음 2개 요구사항만 힌트로
            hint_text += f"{i}. {req}\n"
        
        if len(requirements) > 2:
            hint_text += f"그리고 {len(requirements) - 2}개의 추가 요소도 고려해보세요."
        
        return hint_text
    
    def _get_example_hint(self, question_data: Dict[str, Any]) -> str:
        """예시 프롬프트 힌트"""
        scenario = question_data.get("scenario", "")
        task_description = question_data.get("task_description", "")
        
        example_start = f"""
예시 프롬프트 시작 부분:
"당신은 {scenario}에서 일하는 전문가입니다. 
{task_description[:30]}...
        """
        
        return example_start + "\n\n이런 식으로 시작해서 구체적인 요구사항을 추가해보세요."
    
    def _generate_default_hint(self, question_data: Dict[str, Any], hint_level: int) -> Dict[str, Any]:
        """기본 힌트 생성"""
        default_hints = {
            1: "문제를 천천히 다시 읽어보고 핵심 키워드를 찾아보세요.",
            2: "각 선택지나 요구사항을 하나씩 검토해보세요.",
            3: "문제에서 요구하는 것이 정확히 무엇인지 다시 생각해보세요."
        }
        
        return {
            "hint_id": f"hint_default_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "question_id": question_data.get("question_id", "unknown"),
            "hint_level": hint_level,
            "hint_text": default_hints.get(hint_level, default_hints[1]),
            "hint_type": "default",
            "created_at": datetime.now().isoformat()
        }
    
    def _load_hint_templates(self) -> Dict[str, Any]:
        """힌트 템플릿 로드"""
        return {
            "multiple_choice": {
                "level_1": "문제의 핵심 개념을 파악해보세요.",
                "level_2": "각 선택지를 문제와 연결해서 생각해보세요.",
                "level_3": "정답과 가장 관련이 깊은 개념을 찾아보세요."
            },
            "prompt_practice": {
                "level_1": "프롬프트의 기본 구조를 생각해보세요.",
                "level_2": "구체적인 요구사항들을 하나씩 포함해보세요.",
                "level_3": "예시를 참고하여 완성해보세요."
            }
        }