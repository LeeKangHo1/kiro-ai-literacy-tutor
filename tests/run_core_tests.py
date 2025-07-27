# tests/run_core_tests.py
# 핵심 테스트만 실행하는 스크립트

import os
import sys
import subprocess
import time
from datetime import datetime

def run_test(test_path, description):
    """개별 테스트 실행"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        # Windows 환경에서 가상환경 활성화 후 테스트 실행
        command = f"venv\\Scripts\\activate && python -m pytest {test_path} -v --tb=short"
        
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
            # 성공한 테스트의 요약만 출력
            lines = result.stdout.split('\n')
            summary_lines = [line for line in lines if 'passed' in line or 'failed' in line or 'error' in line]
            if summary_lines:
                print("📊 결과 요약:")
                for line in summary_lines[-3:]:  # 마지막 3줄만 출력
                    if line.strip():
                        print(f"   {line}")
        else:
            print(f"❌ {description} 실패")
            # 실패한 경우 오류 정보 출력
            if result.stderr:
                print("🚨 오류:")
                print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        
        return result.returncode == 0, duration
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 예외: {str(e)}")
        return False, 0

def main():
    """핵심 테스트 실행"""
    print("🚀 핵심 테스트 실행")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 핵심 테스트 목록 (성공 가능성이 높은 순서)
    core_tests = [
        ("tests/unit/test_models_simple.py", "모델 구조 테스트"),
        ("tests/unit/test_agents.py", "에이전트 단위 테스트"),
        ("tests/unit/test_tools.py", "도구 단위 테스트"),
        ("tests/integration/test_external_services.py", "외부 서비스 통합 테스트"),
    ]
    
    results = []
    total_duration = 0
    
    # 각 테스트 실행
    for test_path, description in core_tests:
        success, duration = run_test(test_path, description)
        results.append({
            'test': description,
            'success': success,
            'duration': duration
        })
        total_duration += duration
        
        # 잠시 대기
        time.sleep(0.5)
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("📋 핵심 테스트 결과 요약")
    print(f"{'='*50}")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"📊 전체: {total_count}개")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {total_count - success_count}개")
    print(f"⏱️  총 시간: {total_duration:.2f}초")
    print(f"📈 성공률: {(success_count/total_count)*100:.1f}%")
    
    print(f"\n📝 상세 결과:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"{i}. {status} {result['test']} ({result['duration']:.2f}초)")
    
    if success_count == total_count:
        print(f"\n🎉 모든 핵심 테스트가 성공했습니다!")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count}개 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)