# tests/integration/test_api.py
"""
REST API 통합 테스트
"""

import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from models import db, User, Chapter, LearningLoop
from config import Config
import jwt
from datetime import datetime, timedelta


class TestAPIIntegration:
    """API 통합 테스트 클래스"""
    
    @pytest.fixture
    def app(self):
        """테스트용 Flask 앱 생성"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.rollback()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트 생성"""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        """인증 헤더 생성"""
        with app.app_context():
            # 테스트 사용자 생성
            test_user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password",
                level="beginner"
            )
            db.session.add(test_user)
            db.session.commit()
            
            # JWT 토큰 생성
            payload = {
                'user_id': test_user.id,
                'username': test_user.username,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }
            token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
    
    def test_health_check_endpoint(self, client):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        print("✅ 헬스 체크 엔드포인트 테스트 통과")
    
    def test_user_registration(self, client):
        """사용자 회원가입 테스트"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'level': 'beginner'
        }
        
        response = client.post('/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['username'] == 'newuser'
        print("✅ 사용자 회원가입 테스트 통과")
    
    def test_user_login(self, client, app):
        """사용자 로그인 테스트"""
        with app.app_context():
            # 테스트 사용자 생성
            from werkzeug.security import generate_password_hash
            test_user = User(
                username="loginuser",
                email="login@example.com",
                password_hash=generate_password_hash("password123"),
                level="beginner"
            )
            db.session.add(test_user)
            db.session.commit()
        
        login_data = {
            'username': 'loginuser',
            'password': 'password123'
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['username'] == 'loginuser'
        print("✅ 사용자 로그인 테스트 통과")
    
    def test_protected_endpoint_without_token(self, client):
        """토큰 없이 보호된 엔드포인트 접근 테스트"""
        response = client.get('/user/profile')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ 토큰 없이 보호된 엔드포인트 접근 테스트 통과")
    
    def test_user_profile_endpoint(self, client, auth_headers):
        """사용자 프로필 조회 테스트"""
        response = client.get('/user/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'username' in data
        assert 'email' in data
        assert 'level' in data
        print("✅ 사용자 프로필 조회 테스트 통과")
    
    def test_chapters_list_endpoint(self, client, auth_headers, app):
        """챕터 목록 조회 테스트"""
        with app.app_context():
            # 테스트 챕터 생성
            chapter1 = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            chapter2 = Chapter(
                title="머신러닝",
                description="머신러닝 개념",
                order_index=2,
                content="머신러닝 내용"
            )
            db.session.add(chapter1)
            db.session.add(chapter2)
            db.session.commit()
        
        response = client.get('/learning/chapters', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'chapters' in data
        assert len(data['chapters']) == 2
        print("✅ 챕터 목록 조회 테스트 통과")
    
    def test_chapter_detail_endpoint(self, client, auth_headers, app):
        """챕터 상세 조회 테스트"""
        with app.app_context():
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            db.session.add(chapter)
            db.session.commit()
            chapter_id = chapter.id
        
        response = client.get(f'/learning/chapters/{chapter_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == "AI 기초"
        assert data['description'] == "AI의 기본 개념"
        print("✅ 챕터 상세 조회 테스트 통과")
    
    @patch('workflow.graph_builder.create_workflow_graph')
    def test_chat_message_endpoint(self, mock_workflow, client, auth_headers, app):
        """채팅 메시지 처리 테스트"""
        with app.app_context():
            # 테스트 챕터 생성
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            db.session.add(chapter)
            db.session.commit()
            chapter_id = chapter.id
        
        # Mock 워크플로우 응답 설정
        mock_workflow.return_value.invoke.return_value = {
            'messages': [
                {
                    'type': 'ai',
                    'content': 'AI는 인공지능을 의미합니다.',
                    'agent_type': 'theory_educator'
                }
            ],
            'ui_mode': 'chat',
            'next_action': 'continue_chat'
        }
        
        message_data = {
            'message': 'AI가 무엇인가요?',
            'chapter_id': chapter_id
        }
        
        response = client.post('/learning/chat',
                             data=json.dumps(message_data),
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert 'ui_mode' in data
        print("✅ 채팅 메시지 처리 테스트 통과")
    
    def test_learning_progress_endpoint(self, client, auth_headers, app):
        """학습 진도 조회 테스트"""
        with app.app_context():
            # 테스트 데이터 생성
            user = User.query.filter_by(username="testuser").first()
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            db.session.add(chapter)
            db.session.commit()
            
            from models.learning_loop import UserLearningProgress
            progress = UserLearningProgress(
                user_id=user.id,
                chapter_id=chapter.id,
                progress_percentage=50.0,
                understanding_score=75.0,
                completed_loops=2
            )
            db.session.add(progress)
            db.session.commit()
        
        response = client.get('/learning/progress', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'progress' in data
        print("✅ 학습 진도 조회 테스트 통과")
    
    def test_quiz_generation_endpoint(self, client, auth_headers, app):
        """퀴즈 생성 테스트"""
        with app.app_context():
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            db.session.add(chapter)
            db.session.commit()
            chapter_id = chapter.id
        
        quiz_data = {
            'chapter_id': chapter_id,
            'difficulty': 'beginner',
            'question_type': 'multiple_choice'
        }
        
        with patch('agents.quiz.question_generator.QuestionGenerator.generate_question') as mock_quiz:
            mock_quiz.return_value = {
                'question': 'AI의 정의는?',
                'options': ['A) 인공지능', 'B) 자동화'],
                'correct_answer': 'A) 인공지능'
            }
            
            response = client.post('/learning/quiz',
                                 data=json.dumps(quiz_data),
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'question' in data
            print("✅ 퀴즈 생성 테스트 통과")
    
    def test_quiz_submission_endpoint(self, client, auth_headers, app):
        """퀴즈 답안 제출 테스트"""
        with app.app_context():
            # 테스트 데이터 생성
            user = User.query.filter_by(username="testuser").first()
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            db.session.add(chapter)
            db.session.commit()
            
            loop = LearningLoop(
                user_id=user.id,
                chapter_id=chapter.id,
                loop_number=1,
                status="active"
            )
            db.session.add(loop)
            db.session.commit()
            loop_id = loop.id
        
        submission_data = {
            'loop_id': loop_id,
            'question': 'AI의 정의는?',
            'user_answer': '인공지능',
            'correct_answer': '인공지능'
        }
        
        with patch('agents.evaluator.answer_evaluator.AnswerEvaluator.evaluate_answer') as mock_eval:
            mock_eval.return_value = {
                'is_correct': True,
                'score': 100.0,
                'feedback': '정확한 답변입니다!'
            }
            
            response = client.post('/learning/quiz/submit',
                                 data=json.dumps(submission_data),
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['is_correct'] == True
            assert 'feedback' in data
            print("✅ 퀴즈 답안 제출 테스트 통과")
    
    def test_error_handling(self, client, auth_headers):
        """API 오류 처리 테스트"""
        # 존재하지 않는 챕터 조회
        response = client.get('/learning/chapters/999', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ API 오류 처리 테스트 통과")
    
    def test_invalid_json_request(self, client, auth_headers):
        """잘못된 JSON 요청 테스트"""
        response = client.post('/learning/chat',
                             data="invalid json",
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ 잘못된 JSON 요청 테스트 통과")
    
    def test_rate_limiting(self, client, auth_headers):
        """API 속도 제한 테스트 (구현되어 있다면)"""
        # 여러 번 빠르게 요청
        responses = []
        for i in range(10):
            response = client.get('/user/profile', headers=auth_headers)
            responses.append(response.status_code)
        
        # 대부분의 요청이 성공해야 함 (속도 제한이 없다면)
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 8  # 최소 8개는 성공해야 함
        print("✅ API 속도 제한 테스트 통과")


class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""
    
    @pytest.fixture
    def app(self):
        """테스트용 Flask 앱 생성"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.rollback()
            db.drop_all()
    
    def test_database_connection_through_api(self, app):
        """API를 통한 데이터베이스 연결 테스트"""
        with app.app_context():
            client = app.test_client()
            
            # 데이터베이스 연결이 필요한 엔드포인트 호출
            response = client.get('/health')
            
            assert response.status_code == 200
            print("✅ API를 통한 데이터베이스 연결 테스트 통과")
    
    def test_transaction_rollback_on_error(self, app):
        """오류 시 트랜잭션 롤백 테스트"""
        with app.app_context():
            client = app.test_client()
            
            # 잘못된 데이터로 사용자 생성 시도
            invalid_user_data = {
                'username': '',  # 빈 사용자명
                'email': 'invalid-email',  # 잘못된 이메일
                'password': '123',  # 너무 짧은 비밀번호
                'level': 'invalid_level'  # 잘못된 레벨
            }
            
            response = client.post('/auth/register',
                                 data=json.dumps(invalid_user_data),
                                 content_type='application/json')
            
            # 요청이 실패해야 함
            assert response.status_code in [400, 422]
            
            # 데이터베이스에 잘못된 데이터가 저장되지 않았는지 확인
            user_count = User.query.count()
            assert user_count == 0
            
            print("✅ 오류 시 트랜잭션 롤백 테스트 통과")


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])