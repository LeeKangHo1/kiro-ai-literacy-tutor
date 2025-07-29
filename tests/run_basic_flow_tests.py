# tests/run_basic_flow_tests.py
"""
기본 기능 플로우 테스트 실행 스크립트
로그인 → 채팅 → 퀴즈 → 피드백 기본 플로우 테스트 실행
"""

import sys
import os
import subprocess
import pytest
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_test_environment():
    """테스트 환경 설정"""
    print("🔧 테스트 환경 설정 중...")
    
    # 환경 변수 설정
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-basic-flow-tests'
    
    # 테스트용 설정
    os.environ['TESTING'] = 'True'
    os.environ['WTF_CSRF_ENABLED'] = 'False'
    
    print("✅ 테스트 환경 설정 완료")

def run_backend_tests():
    """백엔드 통합 테스트 실행"""
    print("\n🚀 백엔드 기본 기능 플로우 테스트 실행 중...")
    
    # pytest 실행 옵션
    pytest_args = [
        'tests/integration/test_basic_flow.py',
        '-v',  # verbose 출력
        '--tb=short',  # 짧은 traceback
        '--color=yes',  # 컬러 출력
        '--disable-warnings',  # 경고 비활성화
        '-x',  # 첫 번째 실패 시 중단
        '--durations=10',  # 가장 느린 10개 테스트 표시
    ]
    
    try:
        result = pytest.main(pytest_args)
        
        if result == 0:
            print("✅ 백엔드 테스트 성공!")
            return True
        else:
            print("❌ 백엔드 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"❌ 백엔드 테스트 실행 중 오류 발생: {e}")
        return False

def run_frontend_unit_tests():
    """프론트엔드 단위 테스트 실행"""
    print("\n🚀 프론트엔드 단위 테스트 실행 중...")
    
    frontend_dir = project_root / 'frontend'
    
    try:
        # Vitest 실행
        result = subprocess.run([
            'npm', 'run', 'test:unit', '--', '--run'
        ], cwd=frontend_dir, capture_output=True, text=True)
        
        print("📋 프론트엔드 단위 테스트 출력:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 프론트엔드 단위 테스트 경고/오류:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 프론트엔드 단위 테스트 성공!")
            return True
        else:
            print("❌ 프론트엔드 단위 테스트 실패!")
            return False
            
    except FileNotFoundError:
        print("⚠️ npm이 설치되지 않았거나 frontend 디렉토리에 node_modules가 없습니다.")
        print("   다음 명령어를 실행해주세요:")
        print("   cd frontend && npm install")
        return False
    except Exception as e:
        print(f"❌ 프론트엔드 단위 테스트 실행 중 오류 발생: {e}")
        return False

def run_e2e_tests():
    """E2E 테스트 실행"""
    print("\n🚀 E2E 테스트 실행 중...")
    
    frontend_dir = project_root / 'frontend'
    
    try:
        # Playwright 테스트 실행
        result = subprocess.run([
            'npm', 'run', 'test:e2e', '--', '--headed'
        ], cwd=frontend_dir, capture_output=True, text=True)
        
        print("📋 E2E 테스트 출력:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ E2E 테스트 경고/오류:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ E2E 테스트 성공!")
            return True
        else:
            print("❌ E2E 테스트 실패!")
            return False
            
    except FileNotFoundError:
        print("⚠️ npm이 설치되지 않았거나 Playwright가 설치되지 않았습니다.")
        print("   다음 명령어를 실행해주세요:")
        print("   cd frontend && npm install && npx playwright install")
        return False
    except Exception as e:
        print(f"❌ E2E 테스트 실행 중 오류 발생: {e}")
        return False

def check_dependencies():
    """필요한 의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    # Python 패키지 확인
    required_packages = ['flask', 'pytest', 'sqlalchemy', 'pyjwt']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 누락된 Python 패키지: {', '.join(missing_packages)}")
        print("   다음 명령어를 실행해주세요:")
        print("   pip install -r requirements.txt")
        return False
    
    # Node.js 프로젝트 확인
    frontend_node_modules = project_root / 'frontend' / 'node_modules'
    if not frontend_node_modules.exists():
        print("❌ 프론트엔드 의존성이 설치되지 않았습니다.")
        print("   다음 명령어를 실행해주세요:")
        print("   cd frontend && npm install")
        return False
    
    print("✅ 모든 의존성이 설치되어 있습니다.")
    return True

def generate_test_report(backend_result, frontend_result, e2e_result):
    """테스트 결과 리포트 생성"""
    print("\n" + "="*60)
    print("📊 기본 기능 플로우 테스트 결과 리포트")
    print("="*60)
    
    print(f"🔧 백엔드 통합 테스트: {'✅ 성공' if backend_result else '❌ 실패'}")
    print(f"🎨 프론트엔드 단위 테스트: {'✅ 성공' if frontend_result else '❌ 실패'}")
    print(f"🌐 E2E 테스트: {'✅ 성공' if e2e_result else '❌ 실패'}")
    
    total_tests = 3
    passed_tests = sum([backend_result, frontend_result, e2e_result])
    
    print(f"\n📈 전체 결과: {passed_tests}/{total_tests} 테스트 통과")
    
    if passed_tests == total_tests:
        print("🎉 모든 기본 기능 플로우 테스트가 성공했습니다!")
        print("\n✨ 다음 기능들이 정상적으로 작동합니다:")
        print("   - 사용자 인증 (회원가입/로그인)")
        print("   - JWT 토큰 기반 인증")
        print("   - 채팅 인터페이스")
        print("   - 퀴즈 생성 및 평가")
        print("   - 피드백 시스템")
        print("   - Flask API와 Vue 3 프론트엔드 연동")
        print("   - Axios 통신")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 위의 결과를 확인해주세요.")
        return False

def main():
    """메인 실행 함수"""
    print("🧪 AI Literacy Navigator - 기본 기능 플로우 테스트")
    print("="*60)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 테스트 환경 설정
    setup_test_environment()
    
    # 테스트 실행
    backend_result = run_backend_tests()
    frontend_result = run_frontend_unit_tests()
    e2e_result = run_e2e_tests()
    
    # 결과 리포트 생성
    success = generate_test_report(backend_result, frontend_result, e2e_result)
    
    # 종료 코드 설정
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()