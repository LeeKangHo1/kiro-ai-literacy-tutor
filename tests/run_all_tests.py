# tests/run_all_tests.py
"""
모든 테스트를 실행하는 메인 테스트 러너
"""

import pytest
import os
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_database_connection():
    """데이터베이스 연결 확인"""
    try:
        from config import Config
        from sqlalchemy import create_engine, text
        
        engine = create_engine(Config.DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

def check_virtual_environment():
    """가상환경 활성화 확인"""
    venv_path = project_root / "venv"
    if venv_path.exists():
        if sys.prefix != sys.base_prefix:
            print("✅ 가상환경이 활성화되어 있습니다.")
            return True
        else:
            print("⚠️ 가상환경이 비활성화되어 있습니다. 활성화 후 다시 실행하세요.")
            return False
    else:
        print("⚠️ 가상환경을 찾을 수 없습니다.")
        return False

def install_test_dependencies():
    """테스트 의존성 설치"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"], 
                      check=True, capture_output=True)
        print("✅ 테스트 의존성 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 테스트 의존성 설치 실패: {e}")
        return False

def run_unit_tests():
    """단위 테스트 실행"""
    print("\n" + "="*50)
    print("단위 테스트 실행 중...")
    print("="*50)
    
    unit_test_files = [
        "tests/unit/test_database_connection.py",
        "tests/unit/test_models.py",
        "tests/unit/test_agents.py",
        "tests/unit/test_tools.py"
    ]
    
    for test_file in unit_test_files:
        if os.path.exists(test_file):
            print(f"\n🧪 {test_file} 실행 중...")
            result = pytest.main([test_file, "-v", "--tb=short"])
            if result != 0:
                print(f"❌ {test_file} 테스트 실패")
            else:
                print(f"✅ {test_file} 테스트 성공")
        else:
            print(f"⚠️ {test_file} 파일을 찾을 수 없습니다.")

def run_integration_tests():
    """통합 테스트 실행"""
    print("\n" + "="*50)
    print("통합 테스트 실행 중...")
    print("="*50)
    
    integration_test_files = [
        "tests/integration/test_api.py",
        "tests/integration/test_workflow.py"
    ]
    
    for test_file in integration_test_files:
        if os.path.exists(test_file):
            print(f"\n🧪 {test_file} 실행 중...")
            result = pytest.main([test_file, "-v", "--tb=short"])
            if result != 0:
                print(f"❌ {test_file} 테스트 실패")
            else:
                print(f"✅ {test_file} 테스트 성공")
        else:
            print(f"⚠️ {test_file} 파일을 찾을 수 없습니다.")

def run_coverage_report():
    """테스트 커버리지 리포트 생성"""
    print("\n" + "="*50)
    print("테스트 커버리지 리포트 생성 중...")
    print("="*50)
    
    try:
        result = pytest.main([
            "tests/",
            "--cov=models",
            "--cov=agents",
            "--cov=tools",
            "--cov=workflow",
            "--cov=blueprints",
            "--cov=services",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "-v"
        ])
        
        if result == 0:
            print("✅ 커버리지 리포트 생성 완료")
            print("📊 HTML 리포트: htmlcov/index.html")
        else:
            print("❌ 커버리지 리포트 생성 실패")
            
    except Exception as e:
        print(f"❌ 커버리지 리포트 생성 중 오류: {e}")

def main():
    """메인 테스트 실행 함수"""
    print("🚀 AI Literacy Navigator 테스트 시작")
    print("="*60)
    
    # 1. 환경 확인
    print("1. 환경 확인 중...")
    if not check_virtual_environment():
        return
    
    # 2. 테스트 의존성 설치
    print("\n2. 테스트 의존성 확인 중...")
    if not install_test_dependencies():
        return
    
    # 3. 데이터베이스 연결 확인
    print("\n3. 데이터베이스 연결 확인 중...")
    if not check_database_connection():
        print("⚠️ 데이터베이스 연결에 실패했지만 테스트를 계속 진행합니다.")
    
    # 4. 단위 테스트 실행
    run_unit_tests()
    
    # 5. 통합 테스트 실행
    run_integration_tests()
    
    # 6. 커버리지 리포트 생성
    run_coverage_report()
    
    print("\n" + "="*60)
    print("🎉 모든 테스트 실행 완료!")
    print("="*60)

if __name__ == "__main__":
    main()