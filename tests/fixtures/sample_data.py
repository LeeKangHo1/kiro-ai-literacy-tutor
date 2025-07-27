# tests/fixtures/sample_data.py
"""
테스트용 샘플 데이터 및 픽스처
"""

import pytest
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# 환경변수에서 모델명 가져오기
from config import Config
EXPECTED_MODEL = Config.OPENAI_MODEL


class SampleUsers:
    """테스트용 사용자 데이터"""
    
    BEGINNER_USER = {
        'username': 'beginner_user',
        'email': 'beginner@example.com',
        'password': 'password123',
        'password_hash': generate_password_hash('password123'),
        'level': 'beginner',
        'created_at': datetime.utcnow()
    }
    
    INTERMEDIATE_USER = {
        'username': 'intermediate_user',
        'email': 'intermediate@example.com',
        'password': 'password123',
        'password_hash': generate_password_hash('password123'),
        'level': 'intermediate',
        'created_at': datetime.utcnow()
    }
    
    ADVANCED_USER = {
        'username': 'advanced_user',
        'email': 'advanced@example.com',
        'password': 'password123',
        'password_hash': generate_password_hash('password123'),
        'level': 'advanced',
        'created_at': datetime.utcnow()
    }


class SampleChapters:
    """테스트용 챕터 데이터"""
    
    CHAPTER_1 = {
        'title': 'AI는 무엇인가?',
        'description': 'AI의 기본 개념과 정의를 학습합니다.',
        'order_index': 1,
        'content': '''
        # AI는 무엇인가?
        
        인공지능(AI, Artificial Intelligence)은 인간의 지능을 모방하여 
        학습, 추론, 인식 등의 작업을 수행할 수 있는 컴퓨터 시스템입니다.
        
        ## 주요 개념
        - 머신러닝(Machine Learning)
        - 딥러닝(Deep Learning)
        - 자연어처리(NLP)
        ''',
        'created_at': datetime.utcnow()
    }
    
    CHAPTER_2 = {
        'title': 'LLM이란 무엇인가?',
        'description': '대규모 언어 모델의 개념과 특징을 학습합니다.',
        'order_index': 2,
        'content': '''
        # LLM이란 무엇인가?
        
        대규모 언어 모델(LLM, Large Language Model)은 방대한 텍스트 데이터로 
        훈련된 인공지능 모델입니다.
        
        ## 주요 특징
        - 자연어 이해 및 생성
        - 문맥 파악 능력
        - 다양한 작업 수행
        ''',
        'created_at': datetime.utcnow()
    }
    
    CHAPTER_3 = {
        'title': '프롬프트란 무엇인가?',
        'description': '효과적인 프롬프트 작성법을 학습합니다.',
        'order_index': 3,
        'content': '''
        # 프롬프트란 무엇인가?
        
        프롬프트(Prompt)는 AI 모델에게 주는 명령이나 질문입니다.
        
        ## 좋은 프롬프트의 특징
        - 명확하고 구체적
        - 적절한 맥락 제공
        - 원하는 출력 형식 명시
        ''',
        'created_at': datetime.utcnow()
    }


class SampleQuizzes:
    """테스트용 퀴즈 데이터"""
    
    AI_BASIC_QUIZ = {
        'question': 'AI의 정의는 무엇인가요?',
        'question_type': 'multiple_choice',
        'options': [
            'A) 인공지능(Artificial Intelligence)',
            'B) 자동화(Automation)',
            'C) 로봇공학(Robotics)',
            'D) 컴퓨터 과학(Computer Science)'
        ],
        'correct_answer': 'A) 인공지능(Artificial Intelligence)',
        'explanation': 'AI는 Artificial Intelligence의 줄임말로 인공지능을 의미합니다.',
        'difficulty': 'beginner',
        'chapter_id': 1
    }
    
    LLM_QUIZ = {
        'question': 'LLM의 주요 특징이 아닌 것은?',
        'question_type': 'multiple_choice',
        'options': [
            'A) 자연어 이해',
            'B) 문맥 파악',
            'C) 이미지 생성',
            'D) 텍스트 생성'
        ],
        'correct_answer': 'C) 이미지 생성',
        'explanation': 'LLM은 주로 언어 모델이므로 이미지 생성은 주요 특징이 아닙니다.',
        'difficulty': 'intermediate',
        'chapter_id': 2
    }
    
    PROMPT_QUIZ = {
        'question': '효과적인 프롬프트 작성을 위해 가장 중요한 것은?',
        'question_type': 'short_answer',
        'correct_answer': '명확하고 구체적인 지시사항',
        'explanation': '프롬프트는 명확하고 구체적일수록 원하는 결과를 얻을 수 있습니다.',
        'difficulty': 'beginner',
        'chapter_id': 3
    }


class SampleConversations:
    """테스트용 대화 데이터"""
    
    BASIC_CONVERSATION = [
        {
            'type': 'user',
            'content': 'AI가 무엇인가요?',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'type': 'ai',
            'content': 'AI는 인공지능(Artificial Intelligence)의 줄임말로, 인간의 지능을 모방하여 학습, 추론, 인식 등의 작업을 수행할 수 있는 컴퓨터 시스템입니다.',
            'agent_type': 'theory_educator',
            'timestamp': (datetime.utcnow() + timedelta(seconds=1)).isoformat()
        },
        {
            'type': 'user',
            'content': '더 자세히 설명해주세요',
            'timestamp': (datetime.utcnow() + timedelta(seconds=30)).isoformat()
        },
        {
            'type': 'ai',
            'content': 'AI는 크게 세 가지 분야로 나눌 수 있습니다:\n1. 머신러닝: 데이터로부터 패턴을 학습\n2. 딥러닝: 신경망을 이용한 학습\n3. 자연어처리: 인간의 언어를 이해하고 생성',
            'agent_type': 'theory_educator',
            'timestamp': (datetime.utcnow() + timedelta(seconds=31)).isoformat()
        }
    ]
    
    QUIZ_CONVERSATION = [
        {
            'type': 'ai',
            'content': '이제 퀴즈를 풀어보겠습니다.',
            'agent_type': 'quiz_generator',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'type': 'quiz',
            'content': 'AI의 정의는 무엇인가요?',
            'quiz_data': SampleQuizzes.AI_BASIC_QUIZ,
            'timestamp': (datetime.utcnow() + timedelta(seconds=1)).isoformat()
        },
        {
            'type': 'user',
            'content': 'A) 인공지능(Artificial Intelligence)',
            'timestamp': (datetime.utcnow() + timedelta(seconds=30)).isoformat()
        },
        {
            'type': 'feedback',
            'content': '정답입니다! 훌륭해요. AI는 인공지능을 의미합니다.',
            'evaluation_result': {
                'is_correct': True,
                'score': 100.0,
                'understanding_level': 'excellent'
            },
            'agent_type': 'evaluation_feedback',
            'timestamp': (datetime.utcnow() + timedelta(seconds=31)).isoformat()
        }
    ]


class SampleStates:
    """테스트용 상태 데이터"""
    
    INITIAL_STATE = {
        'user_id': 1,
        'chapter_id': 1,
        'current_loop_id': 1,
        'user_level': 'beginner',
        'messages': [],
        'ui_mode': 'chat',
        'current_agent': 'learning_supervisor',
        'quiz_data': None,
        'loop_summary': None,
        'context': {
            'chapter_title': 'AI는 무엇인가?',
            'learning_objectives': ['AI 정의 이해', '기본 개념 학습']
        }
    }
    
    THEORY_LEARNING_STATE = {
        'user_id': 1,
        'chapter_id': 1,
        'current_loop_id': 1,
        'user_level': 'beginner',
        'messages': SampleConversations.BASIC_CONVERSATION,
        'ui_mode': 'chat',
        'current_agent': 'theory_educator',
        'quiz_data': None,
        'loop_summary': None,
        'context': {
            'chapter_title': 'AI는 무엇인가?',
            'current_topic': 'AI 기본 개념',
            'learning_progress': 30.0
        }
    }
    
    QUIZ_STATE = {
        'user_id': 1,
        'chapter_id': 1,
        'current_loop_id': 1,
        'user_level': 'beginner',
        'messages': SampleConversations.QUIZ_CONVERSATION,
        'ui_mode': 'quiz',
        'current_agent': 'quiz_generator',
        'quiz_data': SampleQuizzes.AI_BASIC_QUIZ,
        'loop_summary': None,
        'context': {
            'chapter_title': 'AI는 무엇인가?',
            'quiz_count': 1,
            'correct_answers': 0
        }
    }


class SampleAPIResponses:
    """테스트용 API 응답 데이터"""
    
    CHATGPT_RESPONSE = {
        'response': 'AI는 인공지능으로, 인간의 지능을 모방하는 기술입니다.',
        'model_used': EXPECTED_MODEL,
        'tokens_used': 150,
        'response_time': 1.2,
        'finish_reason': 'stop'
    }
    
    CHROMADB_SEARCH_RESULT = {
        'results': [
            {
                'content': 'AI는 인공지능을 의미하며...',
                'metadata': {'source': 'chapter1.md', 'chapter_id': 1},
                'score': 0.95
            },
            {
                'content': '머신러닝은 AI의 한 분야로...',
                'metadata': {'source': 'chapter1.md', 'chapter_id': 1},
                'score': 0.87
            }
        ],
        'query': 'AI 정의',
        'total_results': 2
    }
    
    WEB_SEARCH_RESULT = {
        'results': [
            {
                'title': '인공지능 - 위키백과',
                'url': 'https://ko.wikipedia.org/wiki/인공지능',
                'snippet': '인공지능은 인간의 지능을 모방하여...',
                'score': 0.9
            }
        ],
        'search_query': 'AI 인공지능 정의',
        'search_engine': 'tavily',
        'total_results': 1
    }


class SampleErrors:
    """테스트용 오류 데이터"""
    
    API_ERROR = {
        'error': 'API_ERROR',
        'message': 'OpenAI API 호출 실패',
        'details': 'Rate limit exceeded',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    DATABASE_ERROR = {
        'error': 'DATABASE_ERROR',
        'message': '데이터베이스 연결 실패',
        'details': 'Connection timeout',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    VALIDATION_ERROR = {
        'error': 'VALIDATION_ERROR',
        'message': '입력 데이터 유효성 검사 실패',
        'details': 'Required field missing: username',
        'timestamp': datetime.utcnow().isoformat()
    }


# pytest 픽스처 정의
@pytest.fixture
def sample_user():
    """샘플 사용자 픽스처"""
    return SampleUsers.BEGINNER_USER.copy()

@pytest.fixture
def sample_chapter():
    """샘플 챕터 픽스처"""
    return SampleChapters.CHAPTER_1.copy()

@pytest.fixture
def sample_quiz():
    """샘플 퀴즈 픽스처"""
    return SampleQuizzes.AI_BASIC_QUIZ.copy()

@pytest.fixture
def sample_conversation():
    """샘플 대화 픽스처"""
    return SampleConversations.BASIC_CONVERSATION.copy()

@pytest.fixture
def sample_state():
    """샘플 상태 픽스처"""
    return SampleStates.INITIAL_STATE.copy()

@pytest.fixture
def sample_api_response():
    """샘플 API 응답 픽스처"""
    return SampleAPIResponses.CHATGPT_RESPONSE.copy()

@pytest.fixture
def multiple_users():
    """여러 사용자 픽스처"""
    return [
        SampleUsers.BEGINNER_USER.copy(),
        SampleUsers.INTERMEDIATE_USER.copy(),
        SampleUsers.ADVANCED_USER.copy()
    ]

@pytest.fixture
def multiple_chapters():
    """여러 챕터 픽스처"""
    return [
        SampleChapters.CHAPTER_1.copy(),
        SampleChapters.CHAPTER_2.copy(),
        SampleChapters.CHAPTER_3.copy()
    ]

@pytest.fixture
def quiz_session():
    """퀴즈 세션 픽스처"""
    return {
        'state': SampleStates.QUIZ_STATE.copy(),
        'quiz': SampleQuizzes.AI_BASIC_QUIZ.copy(),
        'conversation': SampleConversations.QUIZ_CONVERSATION.copy()
    }