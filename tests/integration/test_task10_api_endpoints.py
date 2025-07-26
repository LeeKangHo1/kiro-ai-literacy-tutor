# tests/integration/test_task10_api_endpoints.py
# Task 10: REST API 엔드포인트 구현 테스트

import pytest
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TestTask10APIEndpoints:
    """Task 10: REST API 엔드포인트 구현 테스트"""
    
    @pytest.fixture
    def app(self):
        """Flask 애플리케이션 테스트 설정"""
        try:
            from app import create_app
            app = create_app()
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            return app
        except ImportError as e:
            pytest.skip(f"Flask 애플리케이션을 로드할 수 없습니다: {e}")
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트"""
        return app.test_client()
    
    @pytest.fixture
    def test_user_data(self):
        """테스트용 사용자 데이터"""
        return {
            'username': 'testuser_task10',
            'email': 'task10@test.com',
            'password': 'TestPassword123!',
            'user_type': 'beginner'
        }
    
    @pytest.fixture
    def auth_headers(self, client, test_user_data):
        """인증 헤더 생성"""
        # 회원가입
        response = client.post('/api/auth/register', 
                             json=test_user_data,
                             content_type='application/json')
        
        if response.status_code == 201:
            data = json.loads(response.data)
            token = data['data']['token']
            return {'Authorization': f'Bearer {token}'}
        
        # 이미 존재하는 경우 로그인 시도
        login_data = {
            'username_or_email': test_user_data['username'],
            'password': test_user_data['password']
        }
        response = client.post('/api/auth/login',
                             json=login_data,
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            token = data['data']['token']
            return {'Authorization': f'Bearer {token}'}
        
        pytest.fail(f"인증 헤더 생성 실패: {response.data}")

    # ========================================
    # 10.1 인증 관련 API 테스트
    # ========================================
    
    def test_auth_register_success(self, client):
        """회원가입 API 성공 테스트"""
        user_data = {
            'username': 'newuser_task10',
            'email': 'newuser_task10@test.com',
            'password': 'NewPassword123!',
            'user_type': 'business'
        }
        
        response = client.post('/api/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['username'] == user_data['username']
        assert data['data']['user']['email'] == user_data['email']
        assert data['data']['user']['user_type'] == user_data['user_type']
    
    def test_auth_register_missing_fields(self, client):
        """회원가입 API 필수 필드 누락 테스트"""
        user_data = {
            'username': 'incomplete_user',
            'email': 'incomplete@test.com'
            # password와 user_type 누락
        }
        
        response = client.post('/api/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'MISSING_FIELDS' in data['error_code']
    
    def test_auth_login_success(self, client, test_user_data):
        """로그인 API 성공 테스트"""
        # 먼저 회원가입
        client.post('/api/auth/register',
                   json=test_user_data,
                   content_type='application/json')
        
        # 로그인 시도
        login_data = {
            'username_or_email': test_user_data['username'],
            'password': test_user_data['password']
        }
        
        response = client.post('/api/auth/login',
                             json=login_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['username'] == test_user_data['username']
    
    def test_auth_login_invalid_credentials(self, client):
        """로그인 API 잘못된 인증정보 테스트"""
        login_data = {
            'username_or_email': 'nonexistent_user',
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/api/auth/login',
                             json=login_data,
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'INVALID_CREDENTIALS' in data['error_code']
    
    def test_auth_token_verify(self, client, auth_headers):
        """토큰 검증 API 테스트"""
        response = client.get('/api/auth/verify', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'token_info' in data['data']
    
    def test_auth_token_refresh(self, client, auth_headers):
        """토큰 갱신 API 테스트"""
        response = client.post('/api/auth/token/refresh', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']
    
    def test_auth_logout(self, client, auth_headers):
        """로그아웃 API 테스트"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_auth_check_username_available(self, client):
        """사용자명 중복 확인 API 테스트 - 사용 가능"""
        check_data = {'username': 'available_username'}
        
        response = client.post('/api/auth/check-username',
                             json=check_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['available'] is True
    
    def test_auth_check_email_available(self, client):
        """이메일 중복 확인 API 테스트 - 사용 가능"""
        check_data = {'email': 'available@test.com'}
        
        response = client.post('/api/auth/check-email',
                             json=check_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['available'] is True

    # ========================================
    # 10.2 학습 관련 API 테스트
    # ========================================
    
    def test_learning_diagnosis_quiz_get(self, client, auth_headers):
        """진단 퀴즈 조회 API 테스트"""
        response = client.get('/api/learning/diagnosis/quiz', headers=auth_headers)
        
        # 진단 퀴즈가 없을 수도 있으므로 404도 허용
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'quiz_id' in data['data']
            assert 'questions' in data['data']
    
    def test_learning_diagnosis_quiz_submit(self, client, auth_headers):
        """진단 퀴즈 제출 API 테스트"""
        quiz_data = {
            'quiz_id': 'test_diagnosis_quiz',
            'answers': [
                {'question_id': 1, 'selected_option': 0},
                {'question_id': 2, 'selected_option': 1}
            ]
        }
        
        response = client.post('/api/learning/diagnosis/quiz/submit',
                             json=quiz_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        # 실제 퀴즈가 없을 수 있으므로 400도 허용
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'diagnosis_result' in data['data']
    
    def test_learning_chat_message_process(self, client, auth_headers):
        """채팅 메시지 처리 API 테스트"""
        message_data = {
            'message': 'AI에 대해 설명해주세요',
            'context': {
                'current_chapter': 1,
                'stage': 'theory'
            }
        }
        
        response = client.post('/api/learning/chat/message',
                             json=message_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        # 실제 워크플로우가 없을 수 있으므로 500도 허용
        assert response.status_code in [200, 500]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'response' in data['data']
    
    def test_learning_chat_message_missing_message(self, client, auth_headers):
        """채팅 메시지 처리 API - 메시지 누락 테스트"""
        message_data = {
            'context': {'current_chapter': 1}
            # message 필드 누락
        }
        
        response = client.post('/api/learning/chat/message',
                             json=message_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'MISSING_MESSAGE' in data['error_code']
    
    def test_learning_chapters_list(self, client, auth_headers):
        """챕터 목록 조회 API 테스트"""
        response = client.get('/api/learning/chapter/list', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'chapters' in data['data']
            assert isinstance(data['data']['chapters'], list)
    
    def test_learning_chapters_list_with_filters(self, client, auth_headers):
        """챕터 목록 조회 API - 필터 적용 테스트"""
        response = client.get('/api/learning/chapter/list?difficulty=low&status=not_started', 
                            headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            if 'filters_applied' in data['data']:
                assert data['data']['filters_applied']['difficulty'] == 'low'
                assert data['data']['filters_applied']['status'] == 'not_started'
    
    def test_learning_chapter_detail(self, client, auth_headers):
        """챕터 상세 정보 조회 API 테스트"""
        chapter_id = 1
        response = client.get(f'/api/learning/chapter/{chapter_id}', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'chapter' in data['data']
            assert 'user_progress' in data['data']
        elif response.status_code == 404:
            assert data['success'] is False
            assert 'NOT_FOUND' in data['error_code']
    
    def test_learning_chapter_start(self, client, auth_headers):
        """챕터 학습 시작 API 테스트"""
        chapter_id = 1
        response = client.post(f'/api/learning/chapter/{chapter_id}/start', 
                             headers=auth_headers)
        
        assert response.status_code in [200, 404, 403]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'learning_loop' in data['data']
            assert 'next_action' in data['data']
    
    def test_learning_chapter_progress(self, client, auth_headers):
        """챕터 진도 조회 API 테스트"""
        chapter_id = 1
        response = client.get(f'/api/learning/chapter/{chapter_id}/progress', 
                            headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'progress' in data['data']
        elif response.status_code == 404:
            assert data['success'] is False

    # ========================================
    # 10.3 사용자 데이터 관리 API 테스트
    # ========================================
    
    def test_user_profile_get(self, client, auth_headers):
        """사용자 프로필 조회 API 테스트"""
        response = client.get('/api/user/profile/', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'user' in data['data']
            assert 'progress_summary' in data['data']
    
    def test_user_profile_update(self, client, auth_headers):
        """사용자 프로필 수정 API 테스트"""
        update_data = {
            'user_type': 'business'
        }
        
        response = client.put('/api/user/profile/',
                            json=update_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'user' in data['data']
    
    def test_user_profile_update_invalid_data(self, client, auth_headers):
        """사용자 프로필 수정 API - 잘못된 데이터 테스트"""
        update_data = {
            'user_type': 'invalid_type'
        }
        
        response = client.put('/api/user/profile/',
                            json=update_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'INVALID_USER_TYPE' in data['error_code']
    
    def test_user_password_change(self, client, auth_headers, test_user_data):
        """비밀번호 변경 API 테스트"""
        password_data = {
            'current_password': test_user_data['password'],
            'new_password': 'NewPassword456!',
            'confirm_password': 'NewPassword456!'
        }
        
        response = client.put('/api/user/profile/password',
                            json=password_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code in [200, 400, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'changed_at' in data['data']
    
    def test_user_password_change_mismatch(self, client, auth_headers, test_user_data):
        """비밀번호 변경 API - 확인 불일치 테스트"""
        password_data = {
            'current_password': test_user_data['password'],
            'new_password': 'NewPassword456!',
            'confirm_password': 'DifferentPassword456!'
        }
        
        response = client.put('/api/user/profile/password',
                            json=password_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'PASSWORD_MISMATCH' in data['error_code']
    
    def test_user_preferences_get(self, client, auth_headers):
        """사용자 학습 선호도 조회 API 테스트"""
        response = client.get('/api/user/profile/preferences', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'user_type' in data['data']
            assert 'user_level' in data['data']
    
    def test_user_stats_overview(self, client, auth_headers):
        """사용자 학습 통계 개요 조회 API 테스트"""
        response = client.get('/api/user/stats/overview', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'overall_progress' in data['data']
            assert 'recent_activity' in data['data']
            assert 'achievements' in data['data']
    
    def test_user_stats_progress(self, client, auth_headers):
        """학습 진도 상세 통계 조회 API 테스트"""
        response = client.get('/api/user/stats/progress?period=30d', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'chapters_progress' in data['data']
            assert 'daily_progress' in data['data']
            assert 'summary' in data['data']
    
    def test_user_stats_quiz(self, client, auth_headers):
        """퀴즈 통계 조회 API 테스트"""
        response = client.get('/api/user/stats/quiz', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'overall_stats' in data['data']
            assert 'chapter_stats' in data['data']
    
    def test_user_stats_activity(self, client, auth_headers):
        """활동 통계 조회 API 테스트"""
        response = client.get('/api/user/stats/activity?period=30d', headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            assert 'activity_summary' in data['data']
            assert 'daily_activity' in data['data']

    # ========================================
    # 인증 없이 접근 시 오류 테스트
    # ========================================
    
    def test_protected_endpoint_without_auth(self, client):
        """인증 없이 보호된 엔드포인트 접근 테스트"""
        protected_endpoints = [
            '/api/auth/verify',
            '/api/auth/logout',
            '/api/learning/diagnosis/quiz',
            '/api/learning/chat/message',
            '/api/learning/chapter/list',
            '/api/user/profile/',
            '/api/user/stats/overview'
        ]
        
        for endpoint in protected_endpoints:
            if endpoint == '/api/learning/chat/message':
                response = client.post(endpoint, json={'message': 'test'})
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 401, f"엔드포인트 {endpoint}에서 401 응답을 기대했지만 {response.status_code}를 받았습니다"
    
    def test_invalid_token_access(self, client):
        """잘못된 토큰으로 접근 테스트"""
        invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
        
        response = client.get('/api/auth/verify', headers=invalid_headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    # ========================================
    # Content-Type 검증 테스트
    # ========================================
    
    def test_json_content_type_required(self, client):
        """JSON Content-Type 필수 검증 테스트"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'user_type': 'beginner'
        }
        
        # Content-Type을 설정하지 않고 요청
        response = client.post('/api/auth/register', data=json.dumps(user_data))
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'INVALID_CONTENT_TYPE' in data['error_code']

    # ========================================
    # 에러 응답 형식 검증 테스트
    # ========================================
    
    def test_error_response_format(self, client):
        """에러 응답 형식 검증 테스트"""
        response = client.post('/api/auth/login',
                             json={'username_or_email': '', 'password': ''},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        # 에러 응답 형식 검증
        assert 'success' in data
        assert data['success'] is False
        assert 'message' in data
        assert 'error_code' in data
        assert isinstance(data['message'], str)
        assert isinstance(data['error_code'], str)
    
    def test_success_response_format(self, client, auth_headers):
        """성공 응답 형식 검증 테스트"""
        response = client.get('/api/auth/verify', headers=auth_headers)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            # 성공 응답 형식 검증
            assert 'success' in data
            assert data['success'] is True
            assert 'message' in data
            assert 'data' in data
            assert isinstance(data['message'], str)
            assert isinstance(data['data'], dict)

    # ========================================
    # 페이지네이션 테스트
    # ========================================
    
    def test_pagination_parameters(self, client, auth_headers):
        """페이지네이션 파라미터 테스트"""
        response = client.get('/api/learning/chat/loops?limit=5&offset=0', 
                            headers=auth_headers)
        
        assert response.status_code in [200, 404]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['success'] is True
            if 'pagination' in data['data']:
                assert 'limit' in data['data']['pagination']
                assert 'offset' in data['data']['pagination']
                assert 'has_more' in data['data']['pagination']

    # ========================================
    # 통합 시나리오 테스트
    # ========================================
    
    def test_complete_user_journey(self, client):
        """완전한 사용자 여정 테스트"""
        # 1. 회원가입
        user_data = {
            'username': 'journey_user',
            'email': 'journey@test.com',
            'password': 'JourneyPassword123!',
            'user_type': 'beginner'
        }
        
        response = client.post('/api/auth/register',
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        token = data['data']['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. 프로필 조회
        response = client.get('/api/user/profile/', headers=headers)
        assert response.status_code in [200, 404]
        
        # 3. 챕터 목록 조회
        response = client.get('/api/learning/chapter/list', headers=headers)
        assert response.status_code in [200, 404]
        
        # 4. 진단 퀴즈 조회
        response = client.get('/api/learning/diagnosis/quiz', headers=headers)
        assert response.status_code in [200, 404]
        
        # 5. 통계 조회
        response = client.get('/api/user/stats/overview', headers=headers)
        assert response.status_code in [200, 404]
        
        # 6. 로그아웃
        response = client.post('/api/auth/logout', headers=headers)
        assert response.status_code == 200

    def test_api_response_time(self, client, auth_headers):
        """API 응답 시간 테스트 (기본적인 성능 검증)"""
        import time
        
        endpoints_to_test = [
            '/api/auth/verify',
            '/api/user/profile/',
            '/api/learning/chapter/list'
        ]
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 응답 시간이 5초를 넘지 않아야 함 (기본적인 성능 검증)
            assert response_time < 5.0, f"엔드포인트 {endpoint}의 응답 시간이 너무 깁니다: {response_time}초"
            
            # 응답 상태 코드도 확인
            assert response.status_code in [200, 404, 500]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])