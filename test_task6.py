# test_task6.py
# 작업 6 테스트 실행 스크립트

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """작업 6 관련 테스트 실행"""
    
    print("=" * 60)
    print("작업 6: 문제 출제 및 평가 시스템 테스트 실행")
    print("=" * 60)
    
    # 프로젝트 루트 디렉토리 설정
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Python 경로에 프로젝트 루트 추가
    sys.path.insert(0, str(project_root))
    
    test_files = [
        "tests/unit/test_quiz_generator.py",
        "tests/unit/test_evaluation_feedback.py", 
        "tests/integration/test_quiz_evaluation_integration.py"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f"\n📝 실행 중: {test_file}")
        print("-" * 50)
        
        try:
            # pytest 실행
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, cwd=project_root)
            
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ 경고/오류:")
                print(result.stderr)
            
            # 결과 파싱
            if result.returncode == 0:
                print(f"✅ {test_file} - 모든 테스트 통과")
                # stdout에서 통과한 테스트 수 추출 (간단한 방법)
                passed_count = result.stdout.count(" PASSED")
                total_passed += passed_count
            else:
                print(f"❌ {test_file} - 일부 테스트 실패")
                failed_count = result.stdout.count(" FAILED")
                passed_count = result.stdout.count(" PASSED")
                total_passed += passed_count
                total_failed += failed_count
                
        except Exception as e:
            print(f"❌ 테스트 실행 오류: {e}")
            total_failed += 1
    
    # 전체 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"✅ 통과: {total_passed}개")
    print(f"❌ 실패: {total_failed}개")
    print(f"📊 성공률: {total_passed/(total_passed+total_failed)*100:.1f}%" if (total_passed+total_failed) > 0 else "📊 성공률: 0%")
    
    if total_failed == 0:
        print("\n🎉 모든 테스트가 성공적으로 통과했습니다!")
        print("작업 6의 QuizGenerator와 EvaluationFeedbackAgent가 올바르게 구현되었습니다.")
    else:
        print(f"\n⚠️ {total_failed}개의 테스트가 실패했습니다.")
        print("실패한 테스트를 확인하고 코드를 수정해주세요.")
    
    return total_failed == 0


def run_simple_demo():
    """간단한 데모 실행"""
    print("\n" + "=" * 60)
    print("작업 6 간단한 데모 실행")
    print("=" * 60)
    
    try:
        # 프로젝트 루트를 Python 경로에 추가
        sys.path.insert(0, str(Path(__file__).parent))
        
        from agents.quiz import QuizGenerator
        from agents.evaluator import EvaluationFeedbackAgent
        
        print("\n1. QuizGenerator 테스트")
        print("-" * 30)
        
        quiz_agent = QuizGenerator()
        
        # 객관식 문제 생성 테스트
        state = {
            "user_message": "객관식 문제를 내주세요",
            "current_chapter": 1,
            "user_level": "medium",
            "user_type": "beginner",
            "user_id": "demo_user",
            "current_loop_conversations": []
        }
        
        quiz_result = quiz_agent.execute(state)
        print(f"✅ 퀴즈 생성 성공: {quiz_result['ui_mode']}")
        print(f"📝 시스템 메시지 길이: {len(quiz_result['system_message'])}자")
        
        print("\n2. EvaluationFeedbackAgent 테스트")
        print("-" * 30)
        
        eval_agent = EvaluationFeedbackAgent()
        
        # 퀴즈 데이터 추출
        quiz_data = None
        for conv in quiz_result["current_loop_conversations"]:
            if "quiz_data" in conv:
                quiz_data = conv["quiz_data"]
                break
        
        if quiz_data:
            # 정답으로 답변 설정
            quiz_result["user_answer"] = quiz_data["correct_answer"]
            quiz_result["hint_used"] = False
            quiz_result["response_time"] = 45
            
            eval_result = eval_agent.execute(quiz_result)
            print(f"✅ 평가 및 피드백 생성 성공: {eval_result['ui_mode']}")
            print(f"📊 평가 결과: {eval_result.get('last_evaluation', {}).get('is_correct', 'Unknown')}")
            print(f"💬 피드백 메시지 길이: {len(eval_result['system_message'])}자")
        
        print("\n🎉 데모 실행 완료!")
        
    except Exception as e:
        print(f"❌ 데모 실행 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("작업 6: 문제 출제 및 평가 시스템 테스트")
    print("QuizGenerator와 EvaluationFeedbackAgent 구현 검증")
    
    # 명령행 인수 처리
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_simple_demo()
    else:
        success = run_tests()
        
        # 테스트 성공 시 데모도 실행
        if success:
            run_simple_demo()
        
        sys.exit(0 if success else 1)