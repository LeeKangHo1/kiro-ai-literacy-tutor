# initialize_system.py
"""
시스템 초기화 스크립트
성능 최적화 및 오류 처리 시스템 설정
"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.logging_config import LoggingConfig
from services.performance_service import performance_service
from utils.error_handler import global_error_handler


def initialize_directories():
    """필요한 디렉토리 생성"""
    directories = [
        'logs',
        'logs/archive',
        'data/backups',
        'data/exports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 디렉토리 생성/확인: {directory}")


def initialize_logging():
    """로깅 시스템 초기화"""
    try:
        LoggingConfig.setup_logging(
            log_level=Config.LOG_LEVEL,
            log_file=Config.LOG_FILE
        )
        print("✓ 로깅 시스템 초기화 완료")
        
        # 초기화 로그 기록
        logger = logging.getLogger('system_init')
        logger.info("시스템 초기화 시작")
        
    except Exception as e:
        print(f"✗ 로깅 시스템 초기화 실패: {e}")
        return False
    
    return True


def initialize_database_optimizations():
    """데이터베이스 최적화 초기화"""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # 성능 최적화 초기화
            performance_service.initialize_performance_optimizations()
            print("✓ 데이터베이스 성능 최적화 완료")
            
    except Exception as e:
        print(f"✗ 데이터베이스 최적화 실패: {e}")
        return False
    
    return True


def initialize_error_handling():
    """오류 처리 시스템 초기화"""
    try:
        # 오류 알림 설정 확인
        smtp_server = os.environ.get('SMTP_SERVER')
        admin_emails = os.environ.get('ADMIN_EMAILS')
        
        if smtp_server and admin_emails:
            print("✓ 오류 알림 시스템 설정 확인됨")
        else:
            print("⚠ 오류 알림 설정이 없습니다. 환경 변수를 확인하세요.")
        
        print("✓ 오류 처리 시스템 초기화 완료")
        
    except Exception as e:
        print(f"✗ 오류 처리 시스템 초기화 실패: {e}")
        return False
    
    return True


def check_system_requirements():
    """시스템 요구사항 확인"""
    requirements_met = True
    
    # Python 버전 확인
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"✗ Python 3.8 이상이 필요합니다. 현재: {python_version.major}.{python_version.minor}")
        requirements_met = False
    else:
        print(f"✓ Python 버전: {python_version.major}.{python_version.minor}")
    
    # 필수 환경 변수 확인
    required_env_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'JWT_SECRET_KEY',
        'OPENAI_API_KEY'
    ]
    
    for var in required_env_vars:
        if not os.environ.get(var):
            print(f"✗ 필수 환경 변수 누락: {var}")
            requirements_met = False
        else:
            print(f"✓ 환경 변수 설정됨: {var}")
    
    # 선택적 환경 변수 확인
    optional_env_vars = [
        'SMTP_SERVER',
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'ADMIN_EMAILS'
    ]
    
    for var in optional_env_vars:
        if os.environ.get(var):
            print(f"✓ 선택적 환경 변수 설정됨: {var}")
        else:
            print(f"⚠ 선택적 환경 변수 미설정: {var}")
    
    return requirements_met


def run_system_tests():
    """기본 시스템 테스트 실행"""
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # 데이터베이스 연결 테스트
            from models import db
            db.session.execute("SELECT 1")
            print("✓ 데이터베이스 연결 테스트 통과")
            
            # 성능 모니터링 테스트
            metrics = performance_service.get_comprehensive_metrics()
            if metrics:
                print("✓ 성능 모니터링 시스템 테스트 통과")
            
    except Exception as e:
        print(f"✗ 시스템 테스트 실패: {e}")
        return False
    
    return True


def create_admin_user():
    """관리자 사용자 생성 (선택적)"""
    try:
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if not all([admin_username, admin_email, admin_password]):
            print("⚠ 관리자 계정 환경 변수가 설정되지 않았습니다.")
            return True
        
        from app import create_app
        from models.user import User
        
        app = create_app()
        with app.app_context():
            # 기존 관리자 확인
            existing_admin = User.get_by_username(admin_username)
            if existing_admin:
                print(f"✓ 관리자 계정이 이미 존재합니다: {admin_username}")
                return True
            
            # 관리자 계정 생성
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                user_type='business',
                user_level='high'  # 관리자는 high 레벨
            )
            
            if admin_user.save():
                print(f"✓ 관리자 계정 생성 완료: {admin_username}")
            else:
                print(f"✗ 관리자 계정 생성 실패")
                return False
        
    except Exception as e:
        print(f"✗ 관리자 계정 생성 중 오류: {e}")
        return False
    
    return True


def main():
    """메인 초기화 함수"""
    print("=" * 60)
    print("AI Literacy Navigator 시스템 초기화")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = True
    
    # 1. 시스템 요구사항 확인
    print("\n1. 시스템 요구사항 확인")
    if not check_system_requirements():
        print("시스템 요구사항을 만족하지 않습니다.")
        return False
    
    # 2. 디렉토리 초기화
    print("\n2. 디렉토리 초기화")
    initialize_directories()
    
    # 3. 로깅 시스템 초기화
    print("\n3. 로깅 시스템 초기화")
    if not initialize_logging():
        success = False
    
    # 4. 데이터베이스 최적화
    print("\n4. 데이터베이스 최적화")
    if not initialize_database_optimizations():
        success = False
    
    # 5. 오류 처리 시스템 초기화
    print("\n5. 오류 처리 시스템 초기화")
    if not initialize_error_handling():
        success = False
    
    # 6. 관리자 계정 생성
    print("\n6. 관리자 계정 설정")
    if not create_admin_user():
        success = False
    
    # 7. 시스템 테스트
    print("\n7. 시스템 테스트")
    if not run_system_tests():
        success = False
    
    # 결과 출력
    print("\n" + "=" * 60)
    if success:
        print("✓ 시스템 초기화가 성공적으로 완료되었습니다!")
        print("\n다음 단계:")
        print("1. 애플리케이션 실행: python app.py")
        print("2. 모니터링 대시보드: http://localhost:5000/api/monitoring/health")
        print("3. 로그 확인: logs/app.log")
    else:
        print("✗ 시스템 초기화 중 일부 오류가 발생했습니다.")
        print("로그를 확인하고 문제를 해결한 후 다시 시도하세요.")
    
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)