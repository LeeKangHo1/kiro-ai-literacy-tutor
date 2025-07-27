# tests/run_final_tests.py
# 최종 테스트 실행 스크립트

import os
import sys
import subprocess
import time
from datetime import datetime

def run_critical_tests():
    """중요한 테스트들만 실행"""
    print("🚀 최종 중요 테스트 실행")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 중요한 테스트들 (반드시 통과해야 하는 것들)
    critical_tests = [
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/unit/test_models_simple.py -v',
            'name': '모델 구조 테스트',
            'required': True
        },
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/unit/test_agents.py -v',
            'name': '에이전트 단위 테스트',
            'required': True
        },
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/unit/test_tools.py -v',
            'name': '도구 단위 테스트',
            'required': True
        },
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/integration/test_external_services.py -v',
            'name': '외부 서비스 통합 테스트',
            'required': True
        },
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/unit/test_workflow_basic.py -v',
            'name': '기본 워크플로우 테스트',
            'required': False
        },
        {
            'command': 'venv\\Scripts\\activate && python -m pytest tests/unit/test_ui_mode_service.py -v',
            'name': 'UI 모드 서비스 테스트',
            'required': False
        }
    ]
    
    results = []
    total_duration = 0
    required_passed = 0
    required_total = 0
    
    for test in critical_tests:
        print(f"\n{'='*50}")
        print(f"🔄 {test['name']}")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                test['command'],
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            )
            
            duration = time.time() - start_time
            total_duration += duration
            
            success = result.returncode == 0
            
            if success:
                print(f"✅ {test['name']} 성공 ({duration:.2f}초)")
                if test['required']:
                    required_passed += 1
            else:
                print(f"❌ {test['name']} 실패 ({duration:.2f}초)")
                if result.stderr:
                    print(f"오류: {result.stderr[:200]}...")
            
            if test['required']:
                required_total += 1
            
            results.append({
                'name': test['name'],
                'success': success,
                'duration': duration,
                'required': test['required']
            })
            
        except Exception as e:
            print(f"❌ {test['name']} 실행 중 예외: {str(e)}")
            results.append({
                'name': test['name'],
                'success': False,
                'duration': 0,
                'required': test['required']
            })
            if test['required']:
                required_total += 1
        
        time.sleep(0.5)
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📋 최종 테스트 결과")
    print(f"{'='*60}")
    
    total_tests = len(results)
    total_passed = sum(1 for r in results if r['success'])
    
    print(f"📊 전체 테스트: {total_tests}개")
    print(f"✅ 성공: {total_passed}개")
    print(f"❌ 실패: {total_tests - total_passed}개")
    print(f"⏱️  총 실행 시간: {total_duration:.2f}초")
    print(f"📈 전체 성공률: {(total_passed/total_tests)*100:.1f}%")
    
    print(f"\n🎯 필수 테스트: {required_total}개 중 {required_passed}개 성공")
    print(f"📈 필수 테스트 성공률: {(required_passed/required_total)*100:.1f}%")
    
    print(f"\n📝 상세 결과:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        required_mark = "🎯" if result['required'] else "📋"
        print(f"{i}. {status} {required_mark} {result['name']} ({result['duration']:.2f}초)")
    
    # 성공 기준
    if required_passed == required_total:
        print(f"\n🎉 모든 필수 테스트가 성공했습니다!")
        if total_passed == total_tests:
            print("✨ 모든 테스트가 완벽하게 통과했습니다!")
        return 0
    else:
        print(f"\n⚠️  {required_total - required_passed}개의 필수 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    exit_code = run_critical_tests()
    sys.exit(exit_code)