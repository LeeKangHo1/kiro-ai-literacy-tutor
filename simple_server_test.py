# simple_server_test.py
# 간단한 Flask 서버 테스트

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_app():
    """간단한 Flask 애플리케이션 생성"""
    app = Flask(__name__)
    CORS(app)
    
    # 기본 라우트
    @app.route('/')
    def home():
        return jsonify({
            'success': True,
            'message': 'AI Literacy Navigator API 서버가 실행 중입니다.',
            'version': '1.0.0'
        })
    
    # Task 10.1: 인증 관련 API 엔드포인트 (더미 구현)
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '요청 데이터가 없습니다.',
                'error_code': 'NO_DATA'
            }), 400
        
        required_fields = ['username', 'email', 'password', 'user_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}',
                'error_code': 'MISSING_FIELDS'
            }), 400
        
        # 더미 응답
        return jsonify({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'data': {
                'user': {
                    'user_id': 1,
                    'username': data['username'],
                    'email': data['email'],
                    'user_type': data['user_type'],
                    'user_level': 'low'
                },
                'token': 'dummy_jwt_token_here'
            }
        }), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '요청 데이터가 없습니다.',
                'error_code': 'NO_DATA'
            }), 400
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({
                'success': False,
                'message': '사용자명/이메일과 비밀번호를 입력해주세요.',
                'error_code': 'MISSING_CREDENTIALS'
            }), 400
        
        # 더미 로그인 (간단한 검증)
        if username_or_email == 'task10_test_user' and password == 'TestPassword123!':
            return jsonify({
                'success': True,
                'message': '로그인이 완료되었습니다.',
                'data': {
                    'user': {
                        'user_id': 1,
                        'username': 'task10_test_user',
                        'email': 'task10@test.com',
                        'user_type': 'beginner',
                        'user_level': 'low'
                    },
                    'token': 'dummy_jwt_token_here'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '잘못된 인증 정보입니다.',
                'error_code': 'INVALID_CREDENTIALS'
            }), 401
    
    @app.route('/api/auth/verify', methods=['GET'])
    def verify_token():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        token = auth_header.split(' ')[1]
        if token == 'dummy_jwt_token_here':
            return jsonify({
                'success': True,
                'message': '유효한 토큰입니다.',
                'data': {
                    'user': {
                        'user_id': 1,
                        'user_type': 'beginner',
                        'user_level': 'low'
                    },
                    'token_info': {
                        'issued_at': '2024-01-01T00:00:00',
                        'expires_at': '2024-01-01T01:00:00'
                    }
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '유효하지 않은 토큰입니다.',
                'error_code': 'INVALID_TOKEN'
            }), 401
    
    @app.route('/api/auth/check-username', methods=['POST'])
    def check_username():
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '사용자명을 입력해주세요.',
                'error_code': 'MISSING_USERNAME'
            }), 400
        
        # 더미 응답 (항상 사용 가능)
        return jsonify({
            'success': True,
            'message': '사용 가능한 사용자명입니다.',
            'data': {
                'available': True,
                'username': username
            }
        }), 200
    
    # Task 10.2: 학습 관련 API 엔드포인트 (더미 구현)
    @app.route('/api/learning/diagnosis/quiz', methods=['GET'])
    def get_diagnosis_quiz():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '진단 퀴즈를 조회했습니다.',
            'data': {
                'quiz_id': 'diagnosis_1_dummy',
                'title': 'AI 활용 수준 진단',
                'description': '귀하의 AI 활용 수준을 파악하여 맞춤형 학습 과정을 제공합니다.',
                'questions': [
                    {
                        'question_id': 1,
                        'question': 'AI에 대해 얼마나 알고 계신가요?',
                        'options': ['전혀 모름', '조금 알고 있음', '어느 정도 알고 있음', '잘 알고 있음']
                    }
                ],
                'total_questions': 1,
                'estimated_time_minutes': 5
            }
        }), 200
    
    @app.route('/api/learning/chat/message', methods=['POST'])
    def process_message():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'message': '메시지를 입력해주세요.',
                'error_code': 'MISSING_MESSAGE'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '메시지가 처리되었습니다.',
            'data': {
                'response': f'"{message}"에 대한 답변입니다. (더미 응답)',
                'ui_mode': 'chat',
                'ui_elements': None,
                'current_stage': 'theory'
            }
        }), 200
    
    @app.route('/api/learning/chapter/list', methods=['GET'])
    def get_chapters():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '학습 가능한 챕터 목록을 조회했습니다.',
            'data': {
                'chapters': [
                    {
                        'chapter_id': 1,
                        'chapter_number': 1,
                        'title': 'AI는 무엇인가?',
                        'description': 'AI의 기본 개념과 정의를 학습합니다.',
                        'difficulty_level': 'low',
                        'estimated_duration': 30,
                        'user_progress': {
                            'completion_status': 'not_started',
                            'progress_percentage': 0.0
                        }
                    }
                ],
                'total_available': 1,
                'user_level': 'low',
                'user_type': 'beginner'
            }
        }), 200
    
    @app.route('/api/learning/chapter/<int:chapter_id>', methods=['GET'])
    def get_chapter_detail(chapter_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        if chapter_id == 1:
            return jsonify({
                'success': True,
                'message': '챕터 상세 정보를 조회했습니다.',
                'data': {
                    'chapter': {
                        'chapter_id': 1,
                        'title': 'AI는 무엇인가?',
                        'description': 'AI의 기본 개념과 정의를 학습합니다.',
                        'difficulty_level': 'low'
                    },
                    'user_progress': {
                        'completion_status': 'not_started',
                        'progress_percentage': 0.0
                    }
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '챕터를 찾을 수 없습니다.',
                'error_code': 'CHAPTER_NOT_FOUND'
            }), 404
    
    # Task 10.3: 사용자 데이터 관리 API 엔드포인트 (더미 구현)
    @app.route('/api/user/profile/', methods=['GET'])
    def get_profile():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '사용자 프로필을 조회했습니다.',
            'data': {
                'user': {
                    'user_id': 1,
                    'username': 'task10_test_user',
                    'email': 'task10@test.com',
                    'user_type': 'beginner',
                    'user_level': 'low'
                },
                'progress_summary': {
                    'total_chapters': 1,
                    'completed_chapters': 0,
                    'in_progress_chapters': 0,
                    'average_understanding': 0.0,
                    'total_study_time': 0
                }
            }
        }), 200
    
    @app.route('/api/user/profile/', methods=['PUT'])
    def update_profile():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        data = request.get_json()
        user_type = data.get('user_type')
        
        if user_type and user_type not in ['beginner', 'business']:
            return jsonify({
                'success': False,
                'message': '올바른 사용자 유형을 선택해주세요.',
                'error_code': 'INVALID_USER_TYPE'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '프로필이 수정되었습니다.',
            'data': {
                'user': {
                    'user_id': 1,
                    'username': 'task10_test_user',
                    'email': 'task10@test.com',
                    'user_type': user_type or 'beginner',
                    'user_level': 'low'
                }
            }
        }), 200
    
    @app.route('/api/user/stats/overview', methods=['GET'])
    def get_stats_overview():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '학습 통계 개요를 조회했습니다.',
            'data': {
                'overall_progress': {
                    'total_chapters': 1,
                    'completed_chapters': 0,
                    'in_progress_chapters': 0,
                    'average_understanding': 0.0,
                    'total_study_time': 0
                },
                'recent_activity': {
                    'last_7_days': {
                        'study_sessions': 0,
                        'total_time_minutes': 0,
                        'chapters_completed': 0,
                        'quiz_attempts': 0
                    }
                },
                'achievements': {
                    'total_quizzes_completed': 0,
                    'average_quiz_score': 0.0,
                    'longest_study_streak': 0,
                    'current_streak': 0
                }
            }
        }), 200
    
    @app.route('/api/user/stats/quiz', methods=['GET'])
    def get_quiz_stats():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '인증 토큰이 필요합니다.',
                'error_code': 'TOKEN_MISSING'
            }), 401
        
        return jsonify({
            'success': True,
            'message': '퀴즈 통계를 조회했습니다.',
            'data': {
                'overall_stats': {
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'success_rate': 0.0,
                    'average_score': 0.0
                },
                'chapter_stats': []
            }
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("Task 10 API 엔드포인트 테스트 서버 시작...")
    print("서버 주소: http://localhost:5000")
    print("테스트를 위해 다른 터미널에서 'python test_task10_simple.py'를 실행하세요.")
    app.run(debug=True, host='0.0.0.0', port=5000)