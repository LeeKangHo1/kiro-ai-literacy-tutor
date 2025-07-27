# tests/run_all_tests_comprehensive.py
# 포괄적인 테스트 실행 스크립트

import os
import sys
import subprocess
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  실행 시간: {duration:.2f}초")
        
        if result.returncode == 0:
            print(f"✅ {description} 성공")
            if result.stdout:
                print("\n📊 결과:")
                print(result.stdout)
        else:
            print(f"❌ {description} 실패 (종료 코드: {result.returncode})")
            if result.stderr:
                print("\n🚨 오류:")
                print(result.stderr)
            if result.stdout:
                print("\n📊 출력:")
                print(result.stdout)
        
        return result.returncode == 0, duration
        
    except Exception as e:
        print(f"❌ {description} 실행 중 예외 발생: {str(e)}")
        return False, 0

def main():
    """메인 테스트 실행 함수"""
    print("🚀 AI 활용 맞춤형 학습 튜터 - 포괄적 테스트 실행")
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 가상환경 활성화 명령어 (Windows)
    venv_activate = "venv\\Scripts\\activate"
    
    # 테스트 명령어 목록
    test_commands = [
        # 1. 단위 테스트
        {
            'command': f'{venv_activate} && python -m pytest tests/unit/test_agents.py -v --tb=short',
            'description': '에이전트 단위 테스트'
        },
        {
            'command': f'{venv_activate} && python -m pytest tests/unit/test_tools.py -v --tb=short',
            'description': '도구 단위 테스트'
        },
        {
            'command': f'{venv_activate} && python -m pytest tests/unit/test_models_simple.py -v --tb=short',
            'description': '모델 단위 테스트 (간단)'
        },
        
        # 2. 통합 테스트
        {
            'command': f'{venv_activate} && python -m pytest tests/integration/test_external_services.py -v --tb=short',
            'description': '외부 서비스 통합 테스트'
        },
        
        # 3. 전체 단위 테스트 실행
        {
            'command': f'{venv_activate} && python -m pytest tests/unit/ -v --tb=short --maxfail=5',
            'description': '전체 단위 테스트'
        },
        
        # 4. 전체 통합 테스트 실행 (기존 파일들)
        {
            'command': f'{venv_activate} && python -m pytest tests/integration/ -v --tb=short --maxfail=3',
            'description': '전체 통합 테스트'
        },
        
        # 5. 커버리지 포함 전체 테스트
        {
            'command': f'{venv_activate} && python -m pytest tests/ --cov=. --cov-report=term-missing --tb=short',
            'description': '커버리지 포함 전체 테스트'
        }
    ]
    
    # 테스트 결과 저장
    results = []
    total_duration = 0
    
    # 각 테스트 실행
    for test_config in test_commands:
        success, duration = run_command(
            test_config['command'],
            test_config['description']
        )
        
        results.append({
            'description': test_config['description'],
            'success': success,
            'duration': duration
        })
        
        total_duration += duration
        
        # 실패한 테스트가 있어도 계속 진행
        time.sleep(1)  # 잠시 대기
    
    # 최종 결과 요약
    print(f"\n{'='*60}")
    print("📋 테스트 실행 결과 요약")
    print(f"{'='*60}")
    
    success_count = sum(1 for result in results if result['success'])
    total_count = len(results)
    
    print(f"📊 전체 테스트: {total_count}개")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {total_count - success_count}개")
    print(f"⏱️  총 실행 시간: {total_duration:.2f}초")
    print(f"📈 성공률: {(success_count/total_count)*100:.1f}%")
    
    print(f"\n{'='*60}")
    print("📝 상세 결과")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{i}. {status} {result['description']} ({result['duration']:.2f}초)")
    
    # 실패한 테스트가 있으면 추가 정보 제공
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n{'='*60}")
        print("🔍 실패한 테스트 분석")
        print(f"{'='*60}")
        
        for failed_test in failed_tests:
            print(f"❌ {failed_test['description']}")
            print("   - 가능한 원인:")
            print("     • 의존성 모듈 누락")
            print("     • 환경 변수 미설정")
            print("     • 데이터베이스 연결 문제")
            print("     • 외부 서비스 연결 문제")
            print()
    
    # 권장사항 제공
    print(f"\n{'='*60}")
    print("💡 권장사항")
    print(f"{'='*60}")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
        print("✨ 코드 품질이 우수합니다.")
    elif success_count >= total_count * 0.8:
        print("👍 대부분의 테스트가 성공했습니다.")
        print("🔧 실패한 테스트를 개별적으로 확인해보세요.")
    else:
        print("⚠️  많은 테스트가 실패했습니다.")
        print("🔍 다음 사항을 확인해보세요:")
        print("   • 가상환경이 올바르게 활성화되었는지")
        print("   • 필요한 패키지가 모두 설치되었는지")
        print("   • 환경 변수가 올바르게 설정되었는지")
        print("   • 데이터베이스 연결이 정상인지")
    
    print(f"\n{'='*60}")
    print("🏁 테스트 실행 완료")
    print(f"📅 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 성공률에 따른 종료 코드 반환
    if success_count == total_count:
        return 0  # 모든 테스트 성공
    elif success_count >= total_count * 0.8:
        return 1  # 대부분 성공
    else:
        return 2  # 많은 테스트 실패

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)