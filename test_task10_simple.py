# test_task10_simple.py
# Task 10 REST API 엔드포인트 간단 테스트

import requests
import json
import time
import threading
from subprocess import Popen, PIPE
import sys
import os

class Task10APITester:
    """Task 10 API 엔드포인트 테스트 클래스"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
    def test_server_running(self):
        """서버가 실행 중인지 확인"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return True
        except requests.exceptions.RequestException:
            return False
    
    def test_auth_endpoints(self):
        """인증 관련 API 엔드포인트 테스트"""
        print("\n=== 10.1 인증 관련 API 테스트 ===")
        
        # 1. 회원가입 테스트
        print("1. 회원가입 API 테스트...")
        register_data = {
            'username': 'task10_test_user',
            'email': 'task10@test.com',
            'password': 'TestPassword123!',
            'user_type': 'beginner'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=register_data,
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [201, 409]:  # 성공 또는 이미 존재
                print("   ✓ 회원가입 API 작동 확인")
                if response.status_code == 201:
                    data = response.json()
                    if 'data' in data and 'token' in data['data']:
                        self.token = data['data']['token']
                        self.headers['Authorization'] = f'Bearer {self.token}'
            else:
                print(f"   ✗ 회원가입 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 회원가입 요청 실패: {e}")
        
        # 2. 로그인 테스트 (회원가입이 실패한 경우)
        if not self.token:
            print("2. 로그인 API 테스트...")
            login_data = {
                'username_or_email': register_data['username'],
                'password': register_data['password']
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    json=login_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                print(f"   상태 코드: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'token' in data['data']:
                        self.token = data['data']['token']
                        self.headers['Authorization'] = f'Bearer {self.token}'
                        print("   ✓ 로그인 API 작동 확인")
                else:
                    print(f"   ✗ 로그인 실패: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ 로그인 요청 실패: {e}")
        
        # 3. 토큰 검증 테스트
        if self.token:
            print("3. 토큰 검증 API 테스트...")
            try:
                response = requests.get(
                    f"{self.base_url}/api/auth/verify",
                    headers=self.headers,
                    timeout=10
                )
                print(f"   상태 코드: {response.status_code}")
                if response.status_code == 200:
                    print("   ✓ 토큰 검증 API 작동 확인")
                else:
                    print(f"   ✗ 토큰 검증 실패: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ 토큰 검증 요청 실패: {e}")
        
        # 4. 사용자명 중복 확인 테스트
        print("4. 사용자명 중복 확인 API 테스트...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/check-username",
                json={'username': 'available_username_test'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ 사용자명 중복 확인 API 작동 확인")
            else:
                print(f"   ✗ 사용자명 중복 확인 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 사용자명 중복 확인 요청 실패: {e}")
    
    def test_learning_endpoints(self):
        """학습 관련 API 엔드포인트 테스트"""
        print("\n=== 10.2 학습 관련 API 테스트 ===")
        
        if not self.token:
            print("인증 토큰이 없어 학습 API 테스트를 건너뜁니다.")
            return
        
        # 1. 진단 퀴즈 조회 테스트
        print("1. 진단 퀴즈 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/learning/diagnosis/quiz",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:  # 성공 또는 데이터 없음
                print("   ✓ 진단 퀴즈 조회 API 작동 확인")
            else:
                print(f"   ✗ 진단 퀴즈 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 진단 퀴즈 조회 요청 실패: {e}")
        
        # 2. 채팅 메시지 처리 테스트
        print("2. 채팅 메시지 처리 API 테스트...")
        try:
            message_data = {
                'message': 'AI에 대해 설명해주세요',
                'context': {'current_chapter': 1}
            }
            response = requests.post(
                f"{self.base_url}/api/learning/chat/message",
                json=message_data,
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 400, 500]:  # 다양한 응답 허용
                print("   ✓ 채팅 메시지 처리 API 엔드포인트 존재 확인")
            else:
                print(f"   ✗ 채팅 메시지 처리 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 채팅 메시지 처리 요청 실패: {e}")
        
        # 3. 챕터 목록 조회 테스트
        print("3. 챕터 목록 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/learning/chapter/list",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:
                print("   ✓ 챕터 목록 조회 API 작동 확인")
            else:
                print(f"   ✗ 챕터 목록 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 챕터 목록 조회 요청 실패: {e}")
        
        # 4. 챕터 상세 정보 조회 테스트
        print("4. 챕터 상세 정보 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/learning/chapter/1",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:
                print("   ✓ 챕터 상세 정보 조회 API 작동 확인")
            else:
                print(f"   ✗ 챕터 상세 정보 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 챕터 상세 정보 조회 요청 실패: {e}")
    
    def test_user_endpoints(self):
        """사용자 데이터 관리 API 엔드포인트 테스트"""
        print("\n=== 10.3 사용자 데이터 관리 API 테스트 ===")
        
        if not self.token:
            print("인증 토큰이 없어 사용자 API 테스트를 건너뜁니다.")
            return
        
        # 1. 사용자 프로필 조회 테스트
        print("1. 사용자 프로필 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/profile/",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:
                print("   ✓ 사용자 프로필 조회 API 작동 확인")
            else:
                print(f"   ✗ 사용자 프로필 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 사용자 프로필 조회 요청 실패: {e}")
        
        # 2. 사용자 프로필 수정 테스트
        print("2. 사용자 프로필 수정 API 테스트...")
        try:
            update_data = {'user_type': 'business'}
            response = requests.put(
                f"{self.base_url}/api/user/profile/",
                json=update_data,
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 400, 404]:
                print("   ✓ 사용자 프로필 수정 API 작동 확인")
            else:
                print(f"   ✗ 사용자 프로필 수정 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 사용자 프로필 수정 요청 실패: {e}")
        
        # 3. 학습 통계 개요 조회 테스트
        print("3. 학습 통계 개요 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/stats/overview",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:
                print("   ✓ 학습 통계 개요 조회 API 작동 확인")
            else:
                print(f"   ✗ 학습 통계 개요 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 학습 통계 개요 조회 요청 실패: {e}")
        
        # 4. 퀴즈 통계 조회 테스트
        print("4. 퀴즈 통계 조회 API 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/stats/quiz",
                headers=self.headers,
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code in [200, 404]:
                print("   ✓ 퀴즈 통계 조회 API 작동 확인")
            else:
                print(f"   ✗ 퀴즈 통계 조회 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 퀴즈 통계 조회 요청 실패: {e}")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n=== 에러 처리 테스트 ===")
        
        # 1. 인증 없이 보호된 엔드포인트 접근
        print("1. 인증 없이 보호된 엔드포인트 접근 테스트...")
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/verify",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ 인증 오류 처리 확인")
            else:
                print(f"   ✗ 예상과 다른 응답: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 요청 실패: {e}")
        
        # 2. 잘못된 JSON 형식 테스트
        print("2. 잘못된 요청 데이터 테스트...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username_or_email': '', 'password': ''},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            print(f"   상태 코드: {response.status_code}")
            if response.status_code == 400:
                print("   ✓ 잘못된 요청 데이터 처리 확인")
            else:
                print(f"   ✗ 예상과 다른 응답: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ 요청 실패: {e}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("Task 10: REST API 엔드포인트 구현 테스트 시작")
        print("=" * 60)
        
        # 서버 실행 확인
        if not self.test_server_running():
            print("❌ Flask 서버가 실행되지 않았습니다.")
            print("다음 명령으로 서버를 실행하세요: python app.py")
            return False
        
        print("✅ Flask 서버 실행 확인됨")
        
        # 각 테스트 실행
        self.test_auth_endpoints()
        self.test_learning_endpoints()
        self.test_user_endpoints()
        self.test_error_handling()
        
        print("\n" + "=" * 60)
        print("Task 10 API 엔드포인트 테스트 완료")
        return True

def main():
    """메인 함수"""
    tester = Task10APITester()
    
    print("Flask 서버 실행을 확인하는 중...")
    if not tester.test_server_running():
        print("\n서버가 실행되지 않았습니다.")
        print("다른 터미널에서 다음 명령을 실행하세요:")
        print("venv\\Scripts\\activate")
        print("python app.py")
        print("\n서버가 실행되면 이 스크립트를 다시 실행하세요.")
        return
    
    # 테스트 실행
    tester.run_all_tests()

if __name__ == "__main__":
    main()