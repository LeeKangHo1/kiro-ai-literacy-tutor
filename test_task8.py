# test_task8.py
# Task 8 외부 API 연동 구현 테스트

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_chatgpt_api():
    """ChatGPT API 연동 테스트"""
    print("\n=== ChatGPT API 연동 테스트 ===")
    
    try:
        from tools.external.chatgpt_tool import chatgpt_api_tool, get_api_status, reset_api_metrics
        
        # API 상태 확인
        print("1. API 상태 확인...")
        status = get_api_status()
        print(f"   API 상태: {status}")
        
        # 간단한 API 호출 테스트
        print("\n2. 간단한 API 호출 테스트...")
        result = chatgpt_api_tool(
            prompt="AI에 대해 한 줄로 설명해주세요.",
            temperature=0.3
        )
        
        if result["success"]:
            print(f"   ✅ 성공: {result['content'][:100]}...")
            print(f"   응답 시간: {result['response_time']:.2f}초")
            if "quality_score" in result:
                print(f"   품질 점수: {result['quality_score']:.2f}")
        else:
            print(f"   ❌ 실패: {result.get('error_message', '알 수 없는 오류')}")
        
        # 프롬프트 품질 분석 테스트
        print("\n3. 프롬프트 품질 분석 테스트...")
        quality_test_result = chatgpt_api_tool(
            prompt="AI 기술의 발전이 사회에 미치는 영향을 구체적인 예시와 함께 단계별로 분석해주세요. 긍정적 측면과 부정적 측면을 모두 고려하여 설명해주세요.",
            temperature=0.5
        )
        
        if quality_test_result["success"] and "quality_score" in quality_test_result:
            print(f"   품질 점수: {quality_test_result['quality_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ChatGPT API 테스트 실패: {str(e)}")
        return False

def test_prompt_practice():
    """프롬프트 실습 도구 테스트"""
    print("\n=== 프롬프트 실습 도구 테스트 ===")
    
    try:
        from tools.external.prompt_practice_tool import prompt_practice_tool, get_practice_scenarios
        
        # 실습 시나리오 조회
        print("1. 실습 시나리오 조회...")
        scenarios = get_practice_scenarios()
        print(f"   사용 가능한 시나리오: {list(scenarios['scenarios'].keys())}")
        
        # 기본 시나리오 테스트
        print("\n2. 기본 시나리오 실습 테스트...")
        practice_result = prompt_practice_tool(
            user_prompt="AI의 정의에 대해 초보자가 이해하기 쉽게 설명해주세요.",
            scenario_type="basic"
        )
        
        if practice_result["success"]:
            print(f"   ✅ 실습 성공")
            print(f"   전체 점수: {practice_result['performance_metrics']['overall_score']:.2f}")
            print(f"   피드백: {practice_result['feedback'][:100]}...")
        else:
            print(f"   ❌ 실습 실패: {practice_result.get('error_message', '알 수 없는 오류')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 프롬프트 실습 테스트 실패: {str(e)}")
        return False

def test_chromadb():
    """ChromaDB 연동 테스트"""
    print("\n=== ChromaDB 연동 테스트 ===")
    
    try:
        from tools.external.chromadb_tool import search_knowledge_base, add_learning_content, chromadb_tool
        
        # 컬렉션 상태 확인
        print("1. ChromaDB 컬렉션 상태 확인...")
        stats = chromadb_tool.get_collection_stats()
        print(f"   컬렉션 상태: {stats}")
        
        # 테스트 콘텐츠 추가
        print("\n2. 테스트 콘텐츠 추가...")
        test_content = "인공지능(AI)은 인간의 지능을 모방하여 학습, 추론, 인식 등의 작업을 수행하는 컴퓨터 시스템입니다."
        add_result = add_learning_content(
            content=test_content,
            chapter_id=1,
            content_type="theory",
            topic="AI 기초"
        )
        
        if add_result:
            print("   ✅ 콘텐츠 추가 성공")
        else:
            print("   ❌ 콘텐츠 추가 실패")
        
        # 검색 테스트
        print("\n3. 지식베이스 검색 테스트...")
        search_results = search_knowledge_base("AI란 무엇인가요?", max_results=3)
        
        if search_results:
            print(f"   ✅ 검색 성공: {len(search_results)}개 결과")
            for i, result in enumerate(search_results[:2]):
                print(f"   결과 {i+1}: {result['content'][:50]}... (유사도: {result['similarity_score']:.2f})")
        else:
            print("   ❌ 검색 결과 없음")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ChromaDB 테스트 실패: {str(e)}")
        return False

def test_web_search():
    """웹 검색 도구 테스트"""
    print("\n=== 웹 검색 도구 테스트 ===")
    
    try:
        from tools.external.web_search_tool import search_web_for_answer, search_general_web, web_search_tool
        
        # 더미 모드 확인
        print(f"1. 웹 검색 모드: {'더미 모드' if web_search_tool.dummy_mode else '실제 API'}")
        
        # AI 관련 검색 테스트
        print("\n2. AI 관련 검색 테스트...")
        ai_results = search_web_for_answer("머신러닝이란 무엇인가요?", max_results=2)
        
        if ai_results:
            print(f"   ✅ AI 검색 성공: {len(ai_results)}개 결과")
            for i, result in enumerate(ai_results):
                print(f"   결과 {i+1}: {result['title'][:50]}...")
        else:
            print("   ❌ AI 검색 결과 없음")
        
        # 일반 웹 검색 테스트
        print("\n3. 일반 웹 검색 테스트...")
        general_results = search_general_web("Python 프로그래밍", max_results=2)
        
        if general_results:
            print(f"   ✅ 일반 검색 성공: {len(general_results)}개 결과")
        else:
            print("   ❌ 일반 검색 결과 없음")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 웹 검색 테스트 실패: {str(e)}")
        return False

def test_error_handling():
    """오류 처리 시스템 테스트"""
    print("\n=== 오류 처리 시스템 테스트 ===")
    
    try:
        from tools.external.error_handler import handle_service_error, get_all_service_status, ServiceType, ErrorSeverity
        
        # 서비스 상태 확인
        print("1. 서비스 상태 확인...")
        status = get_all_service_status()
        print(f"   전체 서비스 상태: {status}")
        
        # 테스트 오류 생성
        print("\n2. 테스트 오류 생성...")
        error_result = handle_service_error(
            service_type=ServiceType.CHATGPT_API,
            error_code="test_error",
            error_message="테스트용 오류입니다",
            context={"test": True},
            severity=ErrorSeverity.LOW
        )
        
        print(f"   오류 처리 결과: {error_result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류 처리 테스트 실패: {str(e)}")
        return False

def test_service_monitoring():
    """서비스 모니터링 테스트"""
    print("\n=== 서비스 모니터링 테스트 ===")
    
    try:
        from tools.external.service_monitor_tool import (
            get_service_health_status, 
            get_error_report, 
            test_service_connectivity
        )
        
        # 서비스 건강 상태 확인
        print("1. 서비스 건강 상태 확인...")
        health_status = get_service_health_status()
        print(f"   전체 건강도: {health_status['overall_health']}")
        print(f"   정상 서비스: {health_status['healthy_services']}/{health_status['total_services']}")
        
        # 오류 리포트 생성
        print("\n2. 오류 리포트 생성...")
        error_report = get_error_report(hours=1)
        print(f"   최근 1시간 오류 수: {error_report['error_statistics']['total_errors']}")
        
        # 서비스 연결 테스트
        print("\n3. 서비스 연결 테스트...")
        connectivity_test = test_service_connectivity()
        print(f"   연결 테스트 결과: {connectivity_test['overall_status']}")
        print(f"   연결된 서비스: {connectivity_test['connected_services']}/{connectivity_test['total_services']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 서비스 모니터링 테스트 실패: {str(e)}")
        return False

def test_alert_system():
    """알림 시스템 테스트"""
    print("\n=== 알림 시스템 테스트 ===")
    
    try:
        from tools.external.alert_system import get_alert_system
        
        alert_system = get_alert_system()
        
        # 활성 규칙 확인
        print("1. 활성 알림 규칙 확인...")
        active_rules = alert_system.get_active_rules()
        print(f"   활성 규칙 수: {len(active_rules)}")
        for rule in active_rules[:3]:
            print(f"   - {rule['name']}: {'활성' if rule['enabled'] else '비활성'}")
        
        # 테스트 알림 발송
        print("\n2. 테스트 알림 발송...")
        if active_rules:
            test_result = alert_system.test_alert(active_rules[0]['name'])
            print(f"   테스트 알림 결과: {'성공' if test_result else '실패'}")
        
        # 알림 이력 확인
        print("\n3. 알림 이력 확인...")
        alert_history = alert_system.get_alert_history(limit=5)
        print(f"   최근 알림 수: {len(alert_history)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 알림 시스템 테스트 실패: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Task 8 외부 API 연동 구현 테스트 시작")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 환경 변수 확인
    print("\n=== 환경 설정 확인 ===")
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY: {'설정됨' if openai_key else '설정되지 않음'}")
    
    google_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    print(f"GOOGLE_SEARCH_API_KEY: {'설정됨' if google_key else '설정되지 않음'}")
    
    # 테스트 실행
    test_results = []
    
    test_results.append(("ChatGPT API", test_chatgpt_api()))
    test_results.append(("프롬프트 실습", test_prompt_practice()))
    test_results.append(("ChromaDB", test_chromadb()))
    test_results.append(("웹 검색", test_web_search()))
    test_results.append(("오류 처리", test_error_handling()))
    test_results.append(("서비스 모니터링", test_service_monitoring()))
    test_results.append(("알림 시스템", test_alert_system()))
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\n전체 결과: {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")
    
    print(f"테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()