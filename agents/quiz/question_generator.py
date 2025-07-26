# agents/quiz/question_generator.py
# 문제 생성 모듈

from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from workflow.state_management import TutorState, StateManager


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
            2: {  # LLM이란 무엇인가?
                "question": "LLM(Large Language Model)의 특징으로 가장 적절한 것은?",
                "options": [
                    "이미지만 처리할 수 있는 모델",
                    "대규모 텍스트 데이터로 훈련된 언어 모델",
                    "음성 인식만 가능한 모델",
                    "숫자 계산만 수행하는 모델"
                ],
                "correct_answer": 1,
                "explanation": "LLM은 대규모 텍스트 데이터로 사전훈련된 언어 모델로, 다양한 자연어 처리 태스크를 수행할 수 있습니다."
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
            },
            4: {  # ChatGPT로 할 수 있는 것들
                "question": "ChatGPT의 주요 활용 분야가 아닌 것은?",
                "options": [
                    "텍스트 요약 및 번역",
                    "창작 및 아이디어 생성",
                    "실시간 주식 거래",
                    "질문 답변 및 설명"
                ],
                "correct_answer": 2,
                "explanation": "ChatGPT는 텍스트 기반 작업에 특화되어 있으며, 실시간 주식 거래와 같은 금융 거래는 직접 수행할 수 없습니다."
            },
            5: {  # AI 시대의 문해력
                "question": "AI 시대에 필요한 문해력으로 가장 중요한 것은?",
                "options": [
                    "AI가 생성한 정보를 무조건 신뢰하기",
                    "AI 도구를 비판적으로 활용하는 능력",
                    "AI 기술을 완전히 배제하기",
                    "AI에 모든 결정을 맡기기"
                ],
                "correct_answer": 1,
                "explanation": "AI 시대의 문해력은 AI 도구를 비판적으로 평가하고 윤리적으로 활용하는 능력이 핵심입니다."
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
            },
            4: {  # ChatGPT로 할 수 있는 것들
                "scenario": "업무 효율성 향상",
                "task_description": "긴 회의록을 요약하고 주요 액션 아이템을 추출하는 프롬프트를 작성하세요.",
                "requirements": [
                    "요약 형식과 길이 지정",
                    "액션 아이템 구조화 요청",
                    "담당자와 마감일 포함"
                ],
                "evaluation_criteria": [
                    "구조화된 출력 요청",
                    "실무 적용 가능성",
                    "명확한 지시사항"
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
            "chapter_2": {
                "multiple_choice": [
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
            },
            "chapter_4": {
                "multiple_choice": [
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
                    }
                ],
                "prompt_practice": [
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
            2: {
                "title": "LLM이란 무엇인가?",
                "key_concepts": ["LLM", "GPT", "BERT", "Transformer", "토큰", "파라미터"]
            },
            3: {
                "title": "프롬프트란 무엇인가?",
                "key_concepts": ["프롬프트 엔지니어링", "명령어 구조", "맥락 제공", "출력 형식"]
            },
            4: {
                "title": "ChatGPT로 할 수 있는 것들",
                "key_concepts": ["텍스트 생성", "요약", "번역", "질문 생성", "업무 자동화"]
            },
            5: {
                "title": "AI 시대의 문해력",
                "key_concepts": ["AI 윤리", "편향성", "개인정보보호", "디지털 리터러시"]
            }
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