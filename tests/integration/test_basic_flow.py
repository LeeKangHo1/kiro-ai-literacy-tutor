# tests/integration/test_basic_flow.py
"""
기본 기능 플로우 통합 테스트
로그인 → 채팅 → 퀴즈 → 피드백 기본 플로우 테스트
"""

import pytest
import json
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app
from models.user import User
from models.chapter import Chapter
from models.learning_loop import LearningLoop
from models.conversation import Conversation
from models.quiz_attempt import QuizAttempt
from services.database_service import DatabaseService
from utils.jwt_utils import generate_token, verify_token


class TestBasicFlow:
    """기본 기능 플로우 테스트 클래스"""
    
    @pytest.fixture
    def client(self):
        """Flask 테스트 클라이언트 설정"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                # 테스트용 데이터베이스 초기화
                try:
                    DatabaseService.init_db()
                except Exception:
                    # 데이터베이스 초기화 실패 시 기본 설정으로 진행
                    pass
                yield client
    
    @pytest.fixture
    def test_user_data(self):
        """테스트용 사용자 데이터"""
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'user_type': 'beginner',
            'user_level': 'low'
        }
    
    @pytest.fixture
    def auth_headers(self, client, test_user_data):
        """인증된 사용자의 헤더"""
        # 사용자 등록
        client.post('/api/auth/register', 
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        # 로그인
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'username': test_user_data['username'],
                                       'password': test_user_data['password']
                                   }),
                                   content_type='application/json')
        
        token = json.loads(login_response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_user_registration_flow(self, client, test_user_data):
        """사용자 회원가입 플로우 테스트"""
        # 회원가입 요청
        response = client.post('/api/auth/register',
                             data=json.dumps(test_user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '회원가입이 완료되었습니다.'
        assert 'user_id' in data
        
        # 중복 회원가입 시도
        response = client.post('/api/auth/register',
                             data=json.dumps(test_user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert '이미 존재하는' in data['error']
    
    def test_user_login_flow(self, client, test_user_data):
        """사용자 로그인 플로우 테스트"""
        # 먼저 회원가입
        client.post('/api/auth/register',
                   data=json.dumps(test_user_data),
                   content_type='application/json')
        
        # 로그인 요청
        login_data = {
            'username': test_user_data['username'],
            'password': test_user_data['password']
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user_info' in data
        assert data['user_info']['username'] == test_user_data['username']
        
        # JWT 토큰 검증 (실제 토큰 검증은 스킵하고 구조만 확인)
        token = data['access_token']
        assert token is not None
        assert len(token) > 0
    
    def test_jwt_authentication(self, client, auth_headers):
        """JWT 인증 테스트"""
        # 인증이 필요한 엔드포인트 호출
        response = client.get('/api/user/profile', headers=auth_headers)
        assert response.status_code == 200
        
        # 잘못된 토큰으로 요청
        invalid_headers = {'Authorization': 'Bearer invalid-token'}
        response = client.get('/api/user/profile', headers=invalid_headers)
        assert response.status_code == 401
        
        # 토큰 없이 요청
        response = client.get('/api/user/profile')
        assert response.status_code == 401
    
    @patch('agents.supervisor.LearningSupervisor.execute')
    @patch('workflow.graph_builder.create_tutor_workflow')
    def test_chat_message_flow(self, mock_workflow, mock_supervisor, client, auth_headers):
        """채팅 메시지 처리 플로우 테스트"""
        # Mock 워크플로우 설정
        mock_graph = MagicMock()
        mock_workflow.return_value = mock_graph
        
        # Mock 응답 설정
        mock_response = {
            'system_message': '안녕하세요! AI 학습을 시작해보겠습니다.',
            'ui_mode': 'chat',
            'current_stage': 'theory_explanation',
            'ui_elements': None
        }
        mock_graph.invoke.return_value = mock_response
        
        # 채팅 메시지 전송
        message_data = {
            'message': '안녕하세요, AI에 대해 배우고 싶습니다.',
            'chapter_id': 1
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(message_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'system_message' in data
        assert 'ui_mode' in data
        assert data['ui_mode'] == 'chat'
        
        # 워크플로우가 호출되었는지 확인
        mock_graph.invoke.assert_called_once()
    
    @patch('agents.quiz.QuizGenerator.execute')
    @patch('workflow.graph_builder.create_tutor_workflow')
    def test_quiz_generation_flow(self, mock_workflow, mock_quiz_generator, client, auth_headers):
        """퀴즈 생성 플로우 테스트"""
        # Mock 워크플로우 설정
        mock_graph = MagicMock()
        mock_workflow.return_value = mock_graph
        
        # Mock 퀴즈 응답 설정
        mock_quiz_response = {
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
        }
        mock_graph.invoke.return_value = mock_quiz_response
        
        # 퀴즈 요청
        quiz_request = {
            'message': '문제를 내주세요',
            'chapter_id': 1
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(quiz_request),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ui_mode'] == 'quiz'
        assert 'ui_elements' in data
        assert data['ui_elements']['quiz_type'] == 'multiple_choice'
        assert 'question' in data['ui_elements']
        assert 'options' in data['ui_elements']
    
    @patch('agents.evaluator.EvaluationFeedbackAgent.execute')
    @patch('workflow.graph_builder.create_tutor_workflow')
    def test_quiz_evaluation_flow(self, mock_workflow, mock_evaluator, client, auth_headers):
        """퀴즈 평가 및 피드백 플로우 테스트"""
        # Mock 워크플로우 설정
        mock_graph = MagicMock()
        mock_workflow.return_value = mock_graph
        
        # Mock 평가 응답 설정
        mock_feedback_response = {
            'system_message': '정답입니다! 잘 이해하고 계시네요.',
            'ui_mode': 'feedback',
            'current_stage': 'feedback_provided',
            'ui_elements': {
                'is_correct': True,
                'score': 100,
                'feedback': '완벽한 답변입니다. AI의 정의를 정확히 이해하고 계십니다.',
                'explanation': 'AI는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.'
            }
        }
        mock_graph.invoke.return_value = mock_feedback_response
        
        # 퀴즈 답변 제출
        answer_data = {
            'message': '1번',
            'chapter_id': 1,
            'quiz_answer': {
                'question_id': 'test_question_1',
                'selected_option': 0,
                'quiz_type': 'multiple_choice'
            }
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(answer_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ui_mode'] == 'feedback'
        assert 'ui_elements' in data
        assert data['ui_elements']['is_correct'] == True
        assert 'feedback' in data['ui_elements']
        assert 'score' in data['ui_elements']
    
    @patch('agents.qna.QnAResolver.execute')
    @patch('workflow.graph_builder.create_tutor_workflow')
    def test_qna_flow(self, mock_workflow, mock_qna, client, auth_headers):
        """질문 답변 플로우 테스트"""
        # Mock 워크플로우 설정
        mock_graph = MagicMock()
        mock_workflow.return_value = mock_graph
        
        # Mock QnA 응답 설정
        mock_qna_response = {
            'system_message': 'AI는 인공지능(Artificial Intelligence)의 줄임말로...',
            'ui_mode': 'chat',
            'current_stage': 'qna_answered',
            'ui_elements': None
        }
        mock_graph.invoke.return_value = mock_qna_response
        
        # 질문 전송
        question_data = {
            'message': 'AI가 정확히 무엇인가요?',
            'chapter_id': 1
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(question_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ui_mode'] == 'chat'
        assert 'system_message' in data
        assert len(data['system_message']) > 0
    
    def test_learning_progress_tracking(self, client, auth_headers):
        """학습 진도 추적 테스트"""
        # 학습 진도 조회
        response = client.get('/api/learning/progress', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'chapters' in data
        assert 'overall_progress' in data
        assert 'current_chapter' in data
    
    def test_user_profile_management(self, client, auth_headers):
        """사용자 프로필 관리 테스트"""
        # 프로필 조회
        response = client.get('/api/user/profile', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'username' in data
        assert 'email' in data
        assert 'user_type' in data
        assert 'user_level' in data
        
        # 프로필 업데이트
        update_data = {
            'user_level': 'medium'
        }
        
        response = client.put('/api/user/profile',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_level'] == 'medium'
    
    @patch('workflow.graph_builder.create_tutor_workflow')
    def test_complete_learning_flow(self, mock_workflow, client, auth_headers):
        """완전한 학습 플로우 테스트 (로그인 → 채팅 → 퀴즈 → 피드백)"""
        # Mock 워크플로우 설정
        mock_graph = MagicMock()
        mock_workflow.return_value = mock_graph
        
        # 1단계: 이론 설명 요청
        mock_graph.invoke.return_value = {
            'system_message': 'AI에 대해 설명드리겠습니다...',
            'ui_mode': 'chat',
            'current_stage': 'theory_explanation'
        }
        
        theory_request = {
            'message': 'AI에 대해 배우고 싶습니다',
            'chapter_id': 1
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(theory_request),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        assert json.loads(response.data)['ui_mode'] == 'chat'
        
        # 2단계: 퀴즈 요청
        mock_graph.invoke.return_value = {
            'system_message': '문제를 풀어보세요',
            'ui_mode': 'quiz',
            'current_stage': 'quiz_solving',
            'ui_elements': {
                'quiz_type': 'multiple_choice',
                'question': 'AI의 정의는?',
                'options': ['인공지능', '자동화', '프로그램', '도구']
            }
        }
        
        quiz_request = {
            'message': '문제를 내주세요',
            'chapter_id': 1
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(quiz_request),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ui_mode'] == 'quiz'
        assert 'ui_elements' in data
        
        # 3단계: 답변 제출 및 피드백
        mock_graph.invoke.return_value = {
            'system_message': '정답입니다!',
            'ui_mode': 'feedback',
            'current_stage': 'feedback_provided',
            'ui_elements': {
                'is_correct': True,
                'score': 100,
                'feedback': '완벽합니다!'
            }
        }
        
        answer_request = {
            'message': '1번',
            'chapter_id': 1,
            'quiz_answer': {
                'selected_option': 0,
                'quiz_type': 'multiple_choice'
            }
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(answer_request),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ui_mode'] == 'feedback'
        assert data['ui_elements']['is_correct'] == True
        
        # 모든 단계가 성공적으로 완료되었는지 확인
        assert mock_graph.invoke.call_count == 3
    
    def test_error_handling(self, client, auth_headers):
        """오류 처리 테스트"""
        # 잘못된 데이터 형식
        invalid_data = "invalid json"
        response = client.post('/api/learning/chat',
                             data=invalid_data,
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        
        # 존재하지 않는 엔드포인트
        response = client.get('/api/nonexistent', headers=auth_headers)
        assert response.status_code == 404
        
        # 필수 필드 누락
        incomplete_data = {
            'chapter_id': 1
            # message 필드 누락
        }
        
        response = client.post('/api/learning/chat',
                             data=json.dumps(incomplete_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])