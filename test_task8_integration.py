# test_task8_integration.py
# Task 8 통합 테스트 (실제 API 키 필요)

import os
import sys
import logging
from datetime import datetime
import time

# 프로젝트 루트를 Python 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_api_keys():
    """API 키 설정 확인"""
    print("=== API 키 설정 확인 ===")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    google_engine = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    print(f"OPENAI_API_KEY: {'✅ 설정됨' if openai_key else '❌ 설정되지 않음'}")
    print(f"GOOGLE_SEARCH_API_KEY: {'✅ 설정됨' if google_key else '❌ 설정되지 않음'}")
    print(f"GOOGLE_SEARCH_ENGINE_ID: {'✅ 설정됨' if google_engine else '❌ 설정되지 않음'}")
    
    return {
        'openai': bool(openai_key),
        'google_search': bool(google_key and google_engine)
    }

def test_chatgpt_integration():
    """ChatGPT API 통합 테스트"""
    print("\n=== ChatGPT API 통합 테스트 ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않아 테스트를 건너뜁니다.")
        return False
    
    try:
        from tools.external.chatgpt_tool import chatgpt_api_tool, get_api_status
        
        # 1. API 상태 확인
        print("1. API 상태 확인...")
        status = get_api_status()
        print(f"   API 상태: {status['api_health']}")
        
        # 2. 간단한 질문 테스트
        print("\n2. 간단한 질문 테스트...")
        result = chatgpt_api_tool(
            prompt="AI에 대해 한 문장으로 설명해주세요.",
            temperature=0.3
        )
        
        if result["success"]:
            print(f"   ✅ 성공: {result['content']}")
            print(f"   응답 시간: {result['response_time']:.2f}초")
            print(f"   토큰 사용량: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            if "quality_score" in result:
                print(f"   품질 점수: {result['quality_score']:.2f}")
        else:
            print(f"   ❌ 실패: {result.get('error_message', '알 수 없는 오류')}")
            return False
        
        # 3. 복잡한 프롬프트 테스트
        print("\n3. 복잡한 프롬프트 테스트...")
        complex_result = chatgpt_api_tool(
            prompt="""
            AI 기술의 발전이 교육 분야에 미치는 영향을 다음과 같이 분석해주세요:
            1. 긍정적 영향 3가지
            2. 부정적 영향 3가지
            3. 향후 전망
            각 항목을 구체적인 예시와 함께 설명해주세요.
            """,
            temperature=0.5
        )
        
        if complex_result["success"]:
            print(f"   ✅ 복잡한 프롬프트 성공")
            print(f"   응답 길이: {len(complex_result['content'])}자")
            print(f"   품질 점수: {complex_result.get('quality_score', 'N/A')}")
        else:
            print(f"   ❌ 복잡한 프롬프트 실패: {complex_result.get('error_message')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ChatGPT 통합 테스트 실패: {str(e)}")
        return False

def test_prompt_practice_integration():
    """프롬프트 실습 통합 테스트"""
    print("\n=== 프롬프트 실습 통합 테스트 ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않아 테스트를 건너뜁니다.")
        return False
    
    try:
        from tools.external.prompt_practice_tool import prompt_practice_tool, get_practice_scenarios
        
        # 1. 시나리오 확인
        print("1. 실습 시나리오 확인...")
        scenarios = get_practice_scenarios()
        print(f"   사용 가능한 시나리오: {list(scenarios['scenarios'].keys())}")
        
        # 2. 각 시나리오별 테스트
        test_prompts = {
            "basic": "AI의 정의에 대해 초보자가 이해하기 쉽게 설명해주세요.",
            "creative": "AI 학습에 대한 재미있는 비유를 사용해서 블로그 글을 작성해주세요.",
            "analytical": "머신러닝과 딥러닝의 차이점을 표로 정리하고 각각의 장단점을 분석해주세요.",
            "roleplay": "당신은 AI 전문가입니다. 비전공자에게 ChatGPT 활용법을 설명해주세요."
        }
        
        results = {}
        for scenario_type, test_prompt in test_prompts.items():
            print(f"\n2.{list(test_prompts.keys()).index(scenario_type) + 1} {scenario_type} 시나리오 테스트...")
            
            result = prompt_practice_tool(
                user_prompt=test_prompt,
                scenario_type=scenario_type
            )
            
            if result["success"]:
                score = result['performance_metrics']['overall_score']
                results[scenario_type] = score
                print(f"   ✅ {scenario_type}: 점수 {score:.2f}")
                print(f"   피드백: {result['feedback'][:100]}...")
            else:
                print(f"   ❌ {scenario_type} 실패: {result.get('error_message')}")
                results[scenario_type] = 0.0
        
        # 3. 결과 요약
        print(f"\n3. 실습 결과 요약:")
        avg_score = sum(results.values()) / len(results) if results else 0
        print(f"   평균 점수: {avg_score:.2f}")
        
        for scenario, score in results.items():
            status = "우수" if score >= 0.8 else "양호" if score >= 0.6 else "개선 필요"
            print(f"   {scenario}: {score:.2f} ({status})")
        
        return avg_score > 0.5
        
    except Exception as e:
        print(f"   ❌ 프롬프트 실습 통합 테스트 실패: {str(e)}")
        return False

def test_chromadb_integration():
    """ChromaDB 통합 테스트"""
    print("\n=== ChromaDB 통합 테스트 ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY가 설정되지 않아 임베딩 생성이 불가능합니다.")
        return False
    
    try:
        from tools.external.chromadb_tool import add_learning_content, search_knowledge_base, chromadb_tool
        
        # 1. 컬렉션 상태 확인
        print("1. ChromaDB 컬렉션 상태 확인...")
        stats = chromadb_tool.get_collection_stats()
        
        if "error" in stats:
            print(f"   ❌ 컬렉션 오류: {stats['error']}")
            return False
        
        print(f"   ✅ 컬렉션 상태: {stats['status']}")
        print(f"   기존 문서 수: {stats['total_documents']}")
        
        # 2. 테스트 콘텐츠 추가
        print("\n2. 테스트 콘텐츠 추가...")
        test_contents = [
            {
                "content": "인공지능(AI)은 인간의 지능을 모방하여 학습, 추론, 인식 등의 작업을 수행하는 컴퓨터 시스템입니다. AI는 머신러닝, 딥러닝, 자연어처리 등 다양한 기술을 포함합니다.",
                "chapter_id": 1,
                "content_type": "theory",
                "topic": "AI 기초"
            },
            {
                "content": "머신러닝은 데이터를 통해 컴퓨터가 자동으로 학습하고 성능을 향상시키는 AI의 한 분야입니다. 지도학습, 비지도학습, 강화학습으로 구분됩니다.",
                "chapter_id": 2,
                "content_type": "theory",
                "topic": "머신러닝"
            },
            {
                "content": "ChatGPT는 OpenAI에서 개발한 대화형 AI 모델로, 자연어 처리를 통해 다양한 질문에 답변하고 텍스트를 생성할 수 있습니다.",
                "chapter_id": 3,
                "content_type": "example",
                "topic": "ChatGPT"
            }
        ]
        
        added_count = 0
        for content_data in test_contents:
            success = add_learning_content(**content_data)
            if success:
                added_count += 1
                print(f"   ✅ 콘텐츠 추가 성공: {content_data['topic']}")
            else:
                print(f"   ❌ 콘텐츠 추가 실패: {content_data['topic']}")
        
        print(f"   총 {added_count}/{len(test_contents)}개 콘텐츠 추가됨")
        
        # 3. 검색 테스트
        print("\n3. 지식베이스 검색 테스트...")
        search_queries = [
            "AI란 무엇인가요?",
            "머신러닝의 종류는?",
            "ChatGPT 사용법",
            "딥러닝과 머신러닝의 차이"
        ]
        
        search_results = {}
        for query in search_queries:
            results = search_knowledge_base(query, max_results=3)
            search_results[query] = len(results)
            
            if results:
                print(f"   ✅ '{query}': {len(results)}개 결과")
                best_result = max(results, key=lambda x: x['similarity_score'])
                print(f"      최고 유사도: {best_result['similarity_score']:.3f}")
            else:
                print(f"   ❌ '{query}': 결과 없음")
        
        # 4. 결과 요약
        total_searches = len(search_queries)
        successful_searches = sum(1 for count in search_results.values() if count > 0)
        
        print(f"\n4. 검색 결과 요약:")
        print(f"   성공한 검색: {successful_searches}/{total_searches}")
        print(f"   평균 결과 수: {sum(search_results.values()) / total_searches:.1f}")
        
        return successful_searches >= total_searches * 0.7  # 70% 이상 성공
        
    except Exception as e:
        print(f"   ❌ ChromaDB 통합 테스트 실패: {str(e)}")
        return False

def test_web_search_integration():
    """웹 검색 통합 테스트"""
    print("\n=== 웹 검색 통합 테스트 ===")
    
    try:
        from tools.external.web_search_tool import search_web_for_answer, search_general_web, web_search_tool
        
        # 1. 검색 모드 확인
        print(f"1. 웹 검색 모드: {'더미 모드' if web_search_tool.dummy_mode else '실제 API'}")
        
        if web_search_tool.dummy_mode:
            print("   ⚠️ Google Search API 키가 설정되지 않아 더미 모드로 테스트합니다.")
        
        # 2. AI 관련 검색 테스트
        print("\n2. AI 관련 검색 테스트...")
        ai_queries = [
            "인공지능이란 무엇인가요?",
            "머신러닝 알고리즘 종류",
            "ChatGPT 활용 방법"
        ]
        
        ai_results = {}
        for query in ai_queries:
            results = search_web_for_answer(query, max_results=3)
            ai_results[query] = len(results)
            
            if results:
                print(f"   ✅ '{query}': {len(results)}개 결과")
                if not web_search_tool.dummy_mode:
                    # 실제 API인 경우 AI 관련성 점수 확인
                    avg_relevance = sum(r.get('ai_relevance_score', 0) for r in results) / len(results)
                    print(f"      평균 AI 관련성: {avg_relevance:.3f}")
            else:
                print(f"   ❌ '{query}': 결과 없음")
        
        # 3. 일반 웹 검색 테스트
        print("\n3. 일반 웹 검색 테스트...")
        general_queries = [
            "Python 프로그래밍 기초",
            "데이터 사이언스 입문"
        ]
        
        general_results = {}
        for query in general_queries:
            results = search_general_web(query, max_results=2)
            general_results[query] = len(results)
            
            if results:
                print(f"   ✅ '{query}': {len(results)}개 결과")
            else:
                print(f"   ❌ '{query}': 결과 없음")
        
        # 4. 결과 요약
        total_queries = len(ai_queries) + len(general_queries)
        successful_queries = sum(1 for count in {**ai_results, **general_results}.values() if count > 0)
        
        print(f"\n4. 웹 검색 결과 요약:")
        print(f"   성공한 검색: {successful_queries}/{total_queries}")
        
        return successful_queries >= total_queries * 0.8  # 80% 이상 성공
        
    except Exception as e:
        print(f"   ❌ 웹 검색 통합 테스트 실패: {str(e)}")
        return False

def test_error_handling_integration():
    """오류 처리 통합 테스트"""
    print("\n=== 오류 처리 통합 테스트 ===")
    
    try:
        from tools.external.service_monitor_tool import (
            get_service_health_status,
            get_error_report,
            test_service_connectivity
        )
        
        # 1. 서비스 건강 상태 확인
        print("1. 서비스 건강 상태 확인...")
        health_status = get_service_health_status.invoke({})
        
        print(f"   전체 건강도: {health_status['overall_health']}")
        print(f"   정상 서비스: {health_status['healthy_services']}/{health_status['total_services']}")
        
        for service_name, service_info in health_status['services'].items():
            status_icon = "✅" if service_info['status'] == 'healthy' else "⚠️" if service_info['status'] == 'degraded' else "❌"
            print(f"   {status_icon} {service_name}: {service_info['status']}")
        
        # 2. 서비스 연결 테스트
        print("\n2. 서비스 연결 테스트...")
        connectivity_test = test_service_connectivity.invoke({})
        
        print(f"   연결 테스트 결과: {connectivity_test['overall_status']}")
        print(f"   연결된 서비스: {connectivity_test['connected_services']}/{connectivity_test['total_services']}")
        
        for service_name, test_result in connectivity_test['service_tests'].items():
            status_icon = "✅" if test_result['status'] == 'connected' else "⚠️" if test_result['status'] == 'limited' else "❌"
            print(f"   {status_icon} {service_name}: {test_result['status']}")
            
            if 'error' in test_result:
                print(f"      오류: {test_result['error']}")
        
        # 3. 오류 리포트 생성
        print("\n3. 오류 리포트 생성...")
        error_report = get_error_report.invoke({"hours": 1})
        
        print(f"   최근 1시간 오류 수: {error_report['error_statistics']['total_errors']}")
        
        if error_report['error_statistics']['statistics']:
            stats = error_report['error_statistics']['statistics']
            
            if 'by_service' in stats:
                print("   서비스별 오류:")
                for service, count in stats['by_service'].items():
                    print(f"     - {service}: {count}개")
            
            if 'by_severity' in stats:
                print("   심각도별 오류:")
                for severity, count in stats['by_severity'].items():
                    print(f"     - {severity}: {count}개")
        
        # 4. 권장사항 확인
        if error_report.get('recommendations'):
            print("\n4. 시스템 권장사항:")
            for i, recommendation in enumerate(error_report['recommendations'], 1):
                print(f"   {i}. {recommendation}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류 처리 통합 테스트 실패: {str(e)}")
        return False

def main():
    """메인 통합 테스트 함수"""
    print("🚀 Task 8 외부 API 연동 통합 테스트 시작")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API 키 확인
    api_keys = check_api_keys()
    
    # 테스트 실행
    test_results = []
    
    # ChatGPT API 테스트
    if api_keys['openai']:
        test_results.append(("ChatGPT API 통합", test_chatgpt_integration()))
        test_results.append(("프롬프트 실습 통합", test_prompt_practice_integration()))
        test_results.append(("ChromaDB 통합", test_chromadb_integration()))
    else:
        print("\n⚠️ OPENAI_API_KEY가 설정되지 않아 ChatGPT 관련 테스트를 건너뜁니다.")
        test_results.append(("ChatGPT API 통합", None))
        test_results.append(("프롬프트 실습 통합", None))
        test_results.append(("ChromaDB 통합", None))
    
    # 웹 검색 테스트 (더미 모드로도 가능)
    test_results.append(("웹 검색 통합", test_web_search_integration()))
    
    # 오류 처리 테스트 (항상 가능)
    test_results.append(("오류 처리 통합", test_error_handling_integration()))
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 통합 테스트 결과 요약")
    print("="*60)
    
    passed = 0
    total = 0
    skipped = 0
    
    for test_name, result in test_results:
        if result is None:
            status = "⏭️ 건너뜀"
            skipped += 1
        elif result:
            status = "✅ 통과"
            passed += 1
            total += 1
        else:
            status = "❌ 실패"
            total += 1
        
        print(f"{test_name:25} : {status}")
    
    print(f"\n전체 결과: {passed}/{total} 테스트 통과 ({passed/total*100 if total > 0 else 0:.1f}%)")
    if skipped > 0:
        print(f"건너뛴 테스트: {skipped}개 (API 키 미설정)")
    
    if total > 0 and passed == total:
        print("🎉 모든 통합 테스트가 성공적으로 완료되었습니다!")
        print("\n✅ Task 8 외부 API 연동이 완벽하게 작동합니다!")
    elif total > 0:
        print("⚠️ 일부 통합 테스트가 실패했습니다.")
    else:
        print("⚠️ API 키가 설정되지 않아 대부분의 테스트를 실행할 수 없습니다.")
    
    print(f"\n테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()