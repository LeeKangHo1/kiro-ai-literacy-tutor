# tests/fixtures/test_data.py
"""
테스트용 Mock 데이터 및 픽스처
"""

from datetime import datetime, timedelta
import json

# 테스트용 사용자 데이터
TEST_USERS = {
    'beginner_user': {
        'user_id': 1,
        'username': 'beginner_test',
        'email': 'beginner@test.com',
        'password': 'testpassword123',
        'user_type': 'beginner',
        'user_level': 'low',
        'created_at': datetime.now(),
        'is_active': True
    },
    'business_user': {
        'user_id': 2,
        'username': 'business_test',
        'email': 'business@test.com',
        'password': 'testpassword123',
        'user_type': 'business',
        'user_level': 'medium',
        'created_at': datetime.now(),
        'is_active': True
    }
}

# 테스트용 챕터 데이터
TEST_CHAPTERS = [
    {
        'chapter_id': 1,
        'title': 'AI는 무엇인가?',
        'description': 'AI의 기본 개념과 정의를 학습합니다.',
        'content': {
            'beginner': {
                'theory': 'AI(인공지능)는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.',
                'examples': ['음성 인식', '이미지 분류', '번역 서비스'],
                'key_points': ['학습 능력', '추론 능력', '문제 해결 능력']
            },
            'business': {
                'theory': 'AI는 머신러닝, 딥러닝 등의 기술을 활용하여 데이터로부터 패턴을 학습하고 예측하는 시스템입니다.',
                'examples': ['추천 시스템', '예측 분석', '자동화 솔루션'],
                'key_points': ['데이터 기반 학습', '패턴 인식', '예측 모델링']
            }
        },
        'order': 1,
        'is_active': True
    },
    {
        'chapter_id': 2,
        'title': 'LLM이란 무엇인가?',
        'description': 'Large Language Model의 개념과 특징을 학습합니다.',
        'content': {
            'beginner': {
                'theory': 'LLM은 대량의 텍스트 데이터로 훈련된 거대한 언어 모델입니다.',
                'examples': ['ChatGPT', 'GPT-4', 'Claude'],
                'key_points': ['대화형 AI', '텍스트 생성', '질문 답변']
            },
            'business': {
                'theory': 'LLM은 Transformer 아키텍처를 기반으로 한 대규모 신경망 모델로, 자연어 처리 작업에 특화되어 있습니다.',
                'examples': ['문서 요약', '코드 생성', '번역'],
                'key_points': ['Transformer 구조', '사전 훈련', '파인튜닝']
            }
        },
        'order': 2,
        'is_active': True
    }
]

# 테스트용 퀴즈 데이터
TEST_QUIZZES = {
    'chapter_1_beginner': [
        {
            'quiz_id': 'q1_1',
            'chapter_id': 1,
            'quiz_type': 'multiple_choice',
            'question': 'AI의 정의는 무엇인가요?',
            'options': [
                '인공지능(Artificial Intelligence)',
                '자동화 시스템',
                '컴퓨터 프로그램',
                '데이터 분석 도구'
            ],
            'correct_answer': 0,
            'explanation': 'AI는 인공지능(Artificial Intelligence)의 줄임말로, 인간의 지능을 모방하는 기술입니다.',
            'difficulty': 'easy'
        },
        {
            'quiz_id': 'q1_2',
            'chapter_id': 1,
            'quiz_type': 'multiple_choice',
            'question': 'AI의 주요 특징이 아닌 것은?',
            'options': [
                '학습 능력',
                '추론 능력',
                '감정 표현',
                '문제 해결 능력'
            ],
            'correct_answer': 2,
            'explanation': '현재 AI는 감정을 실제로 느끼거나 표현하지는 않습니다.',
            'difficulty': 'medium'
        }
    ],
    'chapter_1_business': [
        {
            'quiz_id': 'q1_b1',
            'chapter_id': 1,
            'quiz_type': 'multiple_choice',
            'question': '머신러닝과 딥러닝의 관계는?',
            'options': [
                '머신러닝이 딥러닝을 포함한다',
                '딥러닝이 머신러닝을 포함한다',
                '둘은 완전히 다른 기술이다',
                '둘은 같은 기술이다'
            ],
            'correct_answer': 0,
            'explanation': '딥러닝은 머신러닝의 한 분야로, 신경망을 기반으로 합니다.',
            'difficulty': 'medium'
        }
    ]
}

# 테스트용 대화 데이터
TEST_CONVERSATIONS = [
    {
        'conversation_id': 1,
        'loop_id': 'loop_001',
        'agent_name': 'TheoryEducator',
        'message_type': 'system',
        'user_message': None,
        'system_response': 'AI에 대해 설명드리겠습니다. AI는 인공지능의 줄임말로...',
        'ui_elements': None,
        'timestamp': datetime.now(),
        'sequence_order': 1
    },
    {
        'conversation_id': 2,
        'loop_id': 'loop_001',
        'agent_name': 'PostTheoryRouter',
        'message_type': 'user',
        'user_message': '문제를 내주세요',
        'system_response': None,
        'ui_elements': None,
        'timestamp': datetime.now(),
        'sequence_order': 2
    }
]

# 테스트용 학습 루프 데이터
TEST_LEARNING_LOOPS = [
    {
        'loop_id': 'loop_001',
        'user_id': 1,
        'chapter_id': 1,
        'loop_sequence': 1,
        'loop_status': 'completed',
        'loop_summary': '사용자가 AI의 기본 개념을 학습하고 퀴즈를 완료했습니다.',
        'started_at': datetime.now() - timedelta(hours=1),
        'completed_at': datetime.now(),
        'metadata': {
            'quiz_score': 100,
            'understanding_level': 'high',
            'topics_covered': ['AI 정의', 'AI 특징']
        }
    }
]

# 테스트용 API 응답 데이터
API_RESPONSES = {
    'login_success': {
        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token',
        'user_info': TEST_USERS['beginner_user']
    },
    'login_failure': {
        'error': '잘못된 사용자명 또는 비밀번호입니다.'
    },
    'chat_theory_response': {
        'system_message': 'AI(인공지능)는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.',
        'ui_mode': 'chat',
        'current_stage': 'theory_explanation',
        'ui_elements': None
    },
    'chat_quiz_response': {
        'system_message': '다음 문제를 풀어보세요.',
        'ui_mode': 'quiz',
        'current_stage': 'quiz_solving',
        'ui_elements': {
            'quiz_type': 'multiple_choice',
            'question': 'AI의 정의는 무엇인가요?',
            'options': [
                '인공지능(Artificial Intelligence)',
                '자동화 시스템',
                '컴퓨터 프로그램',
                '데이터 분석 도구'
            ],
            'correct_answer': 0
        }
    },
    'chat_feedback_response': {
        'system_message': '정답입니다! 잘 이해하고 계시네요.',
        'ui_mode': 'feedback',
        'current_stage': 'feedback_provided',
        'ui_elements': {
            'is_correct': True,
            'score': 100,
            'feedback': '완벽한 답변입니다. AI의 정의를 정확히 이해하고 계십니다.',
            'explanation': 'AI는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.'
        }
    },
    'progress_response': {
        'chapters': [
            {'chapter_id': 1, 'title': 'AI는 무엇인가?', 'progress': 25},
            {'chapter_id': 2, 'title': 'LLM이란 무엇인가?', 'progress': 0}
        ],
        'overall_progress': 12.5,
        'current_chapter': 1
    }
}

# 테스트용 State 데이터
TEST_TUTOR_STATE = {
    'user_id': '1',
    'user_message': '안녕하세요, AI에 대해 배우고 싶습니다.',
    'current_chapter': 1,
    'current_stage': 'theory_explanation',
    'user_level': 'low',
    'user_type': 'beginner',
    'qa_source_router': 'post_theory',
    'ui_mode': 'chat',
    'current_loop_conversations': [],
    'recent_loops_summary': [],
    'current_loop_id': 'loop_001',
    'loop_start_time': datetime.now(),
    'system_message': '',
    'ui_elements': None
}

# 테스트용 JWT 토큰
TEST_JWT_TOKENS = {
    'valid_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjo5OTk5OTk5OTk5fQ.test-signature',
    'expired_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxfQ.test-signature',
    'invalid_token': 'invalid.token.format'
}

# 테스트용 오류 응답
ERROR_RESPONSES = {
    'network_error': {
        'error': '네트워크 연결을 확인해주세요.',
        'code': 'NETWORK_ERROR'
    },
    'server_error': {
        'error': '서버 내부 오류가 발생했습니다.',
        'code': 'INTERNAL_SERVER_ERROR'
    },
    'unauthorized_error': {
        'error': '인증이 필요합니다.',
        'code': 'UNAUTHORIZED'
    },
    'validation_error': {
        'error': '입력 데이터가 올바르지 않습니다.',
        'code': 'VALIDATION_ERROR'
    }
}

def get_test_user(user_type='beginner'):
    """테스트용 사용자 데이터 반환"""
    if user_type == 'business':
        return TEST_USERS['business_user'].copy()
    return TEST_USERS['beginner_user'].copy()

def get_test_chapter(chapter_id=1):
    """테스트용 챕터 데이터 반환"""
    for chapter in TEST_CHAPTERS:
        if chapter['chapter_id'] == chapter_id:
            return chapter.copy()
    return None

def get_test_quiz(chapter_id=1, user_type='beginner'):
    """테스트용 퀴즈 데이터 반환"""
    key = f'chapter_{chapter_id}_{user_type}'
    return TEST_QUIZZES.get(key, [])

def get_api_response(response_type):
    """테스트용 API 응답 데이터 반환"""
    return API_RESPONSES.get(response_type, {})

def get_error_response(error_type):
    """테스트용 오류 응답 데이터 반환"""
    return ERROR_RESPONSES.get(error_type, {})

def create_mock_state(**kwargs):
    """Mock TutorState 생성"""
    state = TEST_TUTOR_STATE.copy()
    state.update(kwargs)
    return state

def create_mock_jwt_payload(username='testuser', exp=None):
    """Mock JWT 페이로드 생성"""
    if exp is None:
        exp = datetime.now() + timedelta(hours=1)
    
    return {
        'username': username,
        'user_id': 1,
        'exp': int(exp.timestamp()),
        'iat': int(datetime.now().timestamp())
    }