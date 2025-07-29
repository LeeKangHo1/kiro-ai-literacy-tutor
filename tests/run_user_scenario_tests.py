# tests/run_user_scenario_tests.py
"""
사용자 시나리오 테스트 실행 스크립트
- 백엔드 사용자 시나리오 테스트
- 프론트엔드 E2E 사용자 시나리오 테스트
- 통합 결과 보고서 생성
"""

import subprocess
import sys
import os
import json
from datetime import datetime
import time

def run_backend_scenario_tests():
    """백엔드 사용자 시나리오 테스트 실행"""
    print("=" * 60)
    print("백엔드 사용자 시나리오 테스트 실행 중...")
    print("=" * 60)
    
    try:
        # 가상환경 활성화 확인
        if not os.path.exists('venv'):
            print("❌ 가상환경이 존재하지 않습니다. 먼저 가상환경을 생성하세요.")
            return False
        
        # pytest 실행
        cmd = [
            sys.executable, '-m', 'pytest', 
            'tests/integration/test_user_scenario.py',
            '-v', '--tb=short', '--no-header'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print("백엔드 테스트 결과:")
        print(result.stdout)
        
        if result.stderr:
            print("오류 메시지:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 백엔드 테스트 실행 중 오류 발생: {e}")
        return False

def run_frontend_scenario_tests():
    """프론트엔드 E2E 사용자 시나리오 테스트 실행"""
    print("=" * 60)
    print("프론트엔드 E2E 사용자 시나리오 테스트 실행 중...")
    print("=" * 60)
    
    try:
        # 프론트엔드 디렉토리로 이동
        frontend_dir = 'frontend'
        if not os.path.exists(frontend_dir):
            print("❌ 프론트엔드 디렉토리가 존재하지 않습니다.")
            return False
        
        # package.json 확인
        package_json_path = os.path.join(frontend_dir, 'package.json')
        if not os.path.exists(package_json_path):
            print("❌ package.json이 존재하지 않습니다.")
            return False
        
        # Playwright 브라우저 설치 확인
        print("Playwright 브라우저 설치 확인 중...")
        install_cmd = ['npx', 'playwright', 'install', '--with-deps']
        install_result = subprocess.run(install_cmd, cwd=frontend_dir, capture_output=True, text=True)
        
        if install_result.returncode != 0:
            print("⚠️ Playwright 브라우저 설치 중 문제가 발생했습니다.")
            print(install_result.stderr)
        
        # E2E 테스트 실행
        print("E2E 테스트 실행 중...")
        cmd = ['npx', 'playwright', 'test', 'e2e/user-scenario.spec.ts', '--reporter=line']
        
        result = subprocess.run(cmd, cwd=frontend_dir, capture_output=True, text=True)
        
        print("프론트엔드 E2E 테스트 결과:")
        print(result.stdout)
        
        if result.stderr:
            print("오류 메시지:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 프론트엔드 E2E 테스트 실행 중 오류 발생: {e}")
        return False

def generate_test_report(backend_success, frontend_success):
    """테스트 결과 보고서 생성"""
    report = {
        'test_date': datetime.now().isoformat(),
        'test_type': '사용자 시나리오 테스트 (16.2)',
        'backend_tests': {
            'success': backend_success,
            'test_file': 'tests/integration/test_user_scenario.py'
        },
        'frontend_tests': {
            'success': frontend_success,
            'test_file': 'frontend/e2e/user-scenario.spec.ts'
        },
        'overall_success': backend_success and frontend_success
    }
    
    # 보고서 파일 생성
    report_file = f'tests/test_results_16_2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 16.2 사용자 시나리오 테스트 결과 보고서\n\n")
        f.write(f"## 테스트 개요\n")
        f.write(f"- **테스트 일시**: {report['test_date']}\n")
        f.write(f"- **테스트 유형**: {report['test_type']}\n")
        f.write(f"- **전체 성공 여부**: {'✅ 성공' if report['overall_success'] else '❌ 실패'}\n\n")
        
        f.write(f"## 테스트 결과 요약\n\n")
        f.write(f"| 테스트 영역 | 결과 | 파일 |\n")
        f.write(f"|------------|------|------|\n")
        f.write(f"| 백엔드 사용자 시나리오 | {'✅ 성공' if backend_success else '❌ 실패'} | {report['backend_tests']['test_file']} |\n")
        f.write(f"| 프론트엔드 E2E 시나리오 | {'✅ 성공' if frontend_success else '❌ 실패'} | {report['frontend_tests']['test_file']} |\n\n")
        
        f.write(f"## 테스트 상세 내용\n\n")
        f.write(f"### 백엔드 사용자 시나리오 테스트\n")
        f.write(f"- **1개 챕터 완전 학습 시나리오**: 로그인 → 이론 학습 → 질문 답변 → 퀴즈 → 평가 → 진도 업데이트\n")
        f.write(f"- **멀티에이전트 워크플로우 연동**: TheoryEducator, QnAResolver, QuizGenerator, EvaluationFeedbackAgent 연동\n")
        f.write(f"- **오류 상황 처리**: API 오류, 외부 서비스 오류, 네트워크 오류, DB 오류 처리\n")
        f.write(f"- **학습 루프 관리**: 루프 시작, 진행, 완료 및 요약 생성\n")
        f.write(f"- **UI 모드 전환**: chat, quiz, feedback 모드 전환\n")
        f.write(f"- **성능 및 안정성**: 응답 시간, 동시 요청 처리\n")
        f.write(f"- **데이터 지속성**: 학습 데이터 저장 및 복구\n\n")
        
        f.write(f"### 프론트엔드 E2E 사용자 시나리오 테스트\n")
        f.write(f"- **완전 학습 플로우**: 로그인부터 챕터 완료까지 전체 E2E 테스트\n")
        f.write(f"- **멀티에이전트 UI 연동**: 각 에이전트별 UI 모드 전환 확인\n")
        f.write(f"- **오류 처리 UI**: API 오류, 네트워크 오류, 인증 오류 시 UI 처리\n")
        f.write(f"- **UI 모드 상호작용**: 자유 대화, 퀴즈, 피드백 모드 전환\n")
        f.write(f"- **학습 진도 UI**: 진도 저장 및 조회 UI 테스트\n\n")
        
        f.write(f"## 요구사항 검증\n\n")
        f.write(f"### 요구사항 1.1 - 사용자 유형 진단 및 맞춤형 커리큘럼\n")
        f.write(f"- 진단 퀴즈 제공 및 사용자 유형 분류 테스트\n")
        f.write(f"- 맞춤형 커리큘럼 생성 테스트\n\n")
        
        f.write(f"### 요구사항 1.2 - 사용자 수준별 맞춤 설명\n")
        f.write(f"- 초보자/실무자별 설명 제공 테스트\n")
        f.write(f"- 수준별 예시 및 콘텐츠 적응 테스트\n\n")
        
        f.write(f"### 요구사항 2.1 - 체계적 개념 학습\n")
        f.write(f"- TheoryEducator 에이전트 개념 설명 테스트\n")
        f.write(f"- 챕터별 체계적 학습 진행 테스트\n\n")
        
        f.write(f"### 요구사항 2.2 - 실습 및 평가 시스템\n")
        f.write(f"- QuizGenerator 문제 생성 테스트\n")
        f.write(f"- EvaluationFeedbackAgent 평가 및 피드백 테스트\n")
        f.write(f"- PostTheoryRouter, PostFeedbackRouter 라우팅 테스트\n\n")
        
        f.write(f"## 개선사항 및 권장사항\n\n")
        
        if not backend_success:
            f.write(f"### 백엔드 개선 필요사항\n")
            f.write(f"- 누락된 서비스 메서드 구현 완료\n")
            f.write(f"- 데이터베이스 연결 안정화\n")
            f.write(f"- 외부 API 연동 오류 처리 강화\n\n")
        
        if not frontend_success:
            f.write(f"### 프론트엔드 개선 필요사항\n")
            f.write(f"- Playwright 브라우저 환경 구성\n")
            f.write(f"- E2E 테스트 환경 안정화\n")
            f.write(f"- UI 컴포넌트 구현 완료\n\n")
        
        f.write(f"## 결론\n\n")
        if report['overall_success']:
            f.write(f"🎉 **16.2 사용자 시나리오 테스트가 성공적으로 완료되었습니다!**\n\n")
            f.write(f"- 1개 챕터 완전 학습 시나리오가 정상적으로 동작합니다\n")
            f.write(f"- 멀티에이전트 워크플로우와 UI 연동이 원활합니다\n")
            f.write(f"- 다양한 오류 상황에 대한 적절한 처리가 구현되었습니다\n")
        else:
            f.write(f"⚠️ **16.2 사용자 시나리오 테스트에서 일부 문제가 발견되었습니다.**\n\n")
            f.write(f"- 위의 개선사항을 참고하여 문제를 해결해주세요\n")
            f.write(f"- 핵심 기능은 대부분 구현되어 있으나 세부 조정이 필요합니다\n")
    
    print(f"\n📋 테스트 결과 보고서가 생성되었습니다: {report_file}")
    return report_file

def main():
    """메인 실행 함수"""
    print("🚀 16.2 사용자 시나리오 테스트 시작")
    print("=" * 80)
    
    start_time = time.time()
    
    # 백엔드 테스트 실행
    backend_success = run_backend_scenario_tests()
    
    # 프론트엔드 테스트 실행
    frontend_success = run_frontend_scenario_tests()
    
    # 결과 보고서 생성
    report_file = generate_test_report(backend_success, frontend_success)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("🏁 16.2 사용자 시나리오 테스트 완료")
    print(f"⏱️ 총 실행 시간: {duration:.2f}초")
    print(f"📊 백엔드 테스트: {'✅ 성공' if backend_success else '❌ 실패'}")
    print(f"📊 프론트엔드 테스트: {'✅ 성공' if frontend_success else '❌ 실패'}")
    print(f"📋 보고서: {report_file}")
    
    if backend_success and frontend_success:
        print("\n🎉 모든 사용자 시나리오 테스트가 성공했습니다!")
        return 0
    else:
        print("\n⚠️ 일부 테스트에서 문제가 발견되었습니다. 보고서를 확인해주세요.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)