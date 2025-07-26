# test_task8_offline.py
# Task 8 오프라인 테스트 (API 키 없이 테스트 가능)

import os
import sys
import logging
from datetime import datetime
import unittest
from unittest.mock import Mock, patch

# 프로젝트 루트를 Python 경로에 추가
sys.path.append('.')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestTask8Offline(unittest.TestCase):
    """Task 8 오프라인 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_start_time = datetime.now()
        print(f"\n테스트 시작: {self.test_start_time.strftime('%H:%M:%S')}")
    
    def test_error_handler_functionality(self):
        """오류 처리 시스템 기능 테스트"""
        print("=== 오류 처리 시스템 기능 테스트 ===")
        
        from tools.external.error_handler import (
            handle_service_error, 
            get_all_service_status, 
            ServiceType, 
            ErrorSeverity,
            error_handler
        )
        
        # 1. 서비스 상태 조회
        status = get_all_service_status()
        self.assertIsInstance(status, dict)
        self.assertIn('services', status)
        print(f"✅ 서비스 상태 조회 성공: {len(status['services'])}개 서비스")
        
        # 2. 테스트 오류 생성 및 처리
        error_result = handle_service_error(
            service_type=ServiceType.CHATGPT_API,
            error_code="test_error",
            error_message="테스트 오류",
            context={"test": True},
            severity=ErrorSeverity.LOW
        )
        
        self.assertIsInstance(error_result, dict)
        print("✅ 오류 처리 기능 정상 작동")
        
        # 3. 오류 통계 확인
        from tools.external.error_handler import get_error_stats
        stats = get_error_stats(hours=1)
        self.assertIsInstance(stats, dict)
        self.assertIn('statistics', stats)
        print("✅ 오류 통계 기능 정상 작동")
    
    def test_api_monitor_functionality(self):
        """API 모니터링 시스템 기능 테스트"""
        print("=== API 모니터링 시스템 기능 테스트 ===")
        
        from tools.external.api_monitor import (
            api_monitor,
            log_api_call,
            check_rate_limit,
            rate_limiter
        )
        
        # 1. Rate limit 확인
        can_call = check_rate_limit()
        self.assertIsInstance(can_call, bool)
        print(f"✅ Rate limit 확인: {can_call}")
        
        # 2. API 호출 로깅
        log_api_call(
            endpoint="test/endpoint",
            success=True,
            response_time=0.5,
            token_usage={"total_tokens": 100},
            model="test-model"
        )
        
        # 3. 메트릭 조회
        metrics = api_monitor.get_current_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_calls', metrics)
        print(f"✅ API 메트릭 조회: {metrics['total_calls']}회 호출")
        
        # 4. 최근 호출 기록 조회
        recent_calls = api_monitor.get_recent_calls(minutes=60)
        self.assertIsInstance(recent_calls, list)
        print(f"✅ 최근 호출 기록: {len(recent_calls)}개")
    
    def test_prompt_quality_analyzer(self):
        """프롬프트 품질 분석기 테스트"""
        print("=== 프롬프트 품질 분석기 테스트 ===")
        
        from tools.external.chatgpt_tool import PromptQualityAnalyzer
        
        analyzer = PromptQualityAnalyzer()
        
        # 1. 좋은 프롬프트 테스트
        good_prompt = "AI 기술의 발전이 사회에 미치는 영향을 구체적인 예시와 함께 단계별로 분석해주세요. 긍정적 측면과 부정적 측면을 모두 고려하여 설명해주세요."
        good_analysis = analyzer.analyze_prompt_quality(good_prompt)
        
        self.assertIsInstance(good_analysis, dict)
        self.assertIn('overall_score', good_analysis)
        self.assertGreater(good_analysis['overall_score'], 0.5)
        print(f"✅ 좋은 프롬프트 분석: 점수 {good_analysis['overall_score']:.2f}")
        
        # 2. 나쁜 프롬프트 테스트
        bad_prompt = "AI"
        bad_analysis = analyzer.analyze_prompt_quality(bad_prompt)
        
        self.assertLess(bad_analysis['overall_score'], 0.5)
        self.assertGreater(len(bad_analysis['suggestions']), 0)
        print(f"✅ 나쁜 프롬프트 분석: 점수 {bad_analysis['overall_score']:.2f}, 제안 {len(bad_analysis['suggestions'])}개")
    
    def test_web_search_dummy_mode(self):
        """웹 검색 더미 모드 테스트"""
        print("=== 웹 검색 더미 모드 테스트 ===")
        
        from tools.external.web_search_tool import web_search_tool, search_web_for_answer
        
        # 1. 더미 모드 확인
        self.assertTrue(web_search_tool.dummy_mode)
        print("✅ 더미 모드 활성화 확인")
        
        # 2. 더미 검색 결과 테스트
        results = search_web_for_answer("AI란 무엇인가요?", max_results=3)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        for result in results:
            self.assertIn('title', result)
            self.assertIn('snippet', result)
            self.assertIn('source', result)
        
        print(f"✅ 더미 검색 결과: {len(results)}개")
    
    def test_fallback_strategies(self):
        """대체 전략 테스트"""
        print("=== 대체 전략 테스트 ===")
        
        from tools.external.error_handler import (
            ChatGPTFallbackStrategy,
            ChromaDBFallbackStrategy,
            WebSearchFallbackStrategy,
            ServiceError,
            ServiceType,
            ErrorSeverity
        )
        from datetime import datetime
        
        # 1. ChatGPT 대체 전략 테스트
        chatgpt_strategy = ChatGPTFallbackStrategy()
        chatgpt_error = ServiceError(
            service_type=ServiceType.CHATGPT_API,
            error_code="api_unavailable",
            error_message="API 서비스 중단",
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            context={"request_type": "theory_explanation"}
        )
        
        self.assertTrue(chatgpt_strategy.is_applicable(chatgpt_error))
        chatgpt_result = chatgpt_strategy.execute({"request_type": "theory_explanation"})
        
        self.assertIsInstance(chatgpt_result, dict)
        self.assertIn('is_fallback', chatgpt_result)
        self.assertTrue(chatgpt_result['is_fallback'])
        print("✅ ChatGPT 대체 전략 테스트 성공")
        
        # 2. ChromaDB 대체 전략 테스트
        chromadb_strategy = ChromaDBFallbackStrategy()
        chromadb_error = ServiceError(
            service_type=ServiceType.CHROMADB,
            error_code="connection_failed",
            error_message="DB 연결 실패",
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            context={"query": "AI란 무엇인가요?"}
        )
        
        self.assertTrue(chromadb_strategy.is_applicable(chromadb_error))
        chromadb_result = chromadb_strategy.execute({"query": "AI란 무엇인가요?"})
        
        self.assertIsInstance(chromadb_result, dict)
        self.assertIn('results', chromadb_result)
        self.assertGreater(len(chromadb_result['results']), 0)
        print("✅ ChromaDB 대체 전략 테스트 성공")
        
        # 3. 웹 검색 대체 전략 테스트
        websearch_strategy = WebSearchFallbackStrategy()
        websearch_error = ServiceError(
            service_type=ServiceType.WEB_SEARCH,
            error_code="api_limit_exceeded",
            error_message="API 한도 초과",
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            context={"query": "머신러닝"}
        )
        
        self.assertTrue(websearch_strategy.is_applicable(websearch_error))
        websearch_result = websearch_strategy.execute({"query": "머신러닝"})
        
        self.assertIsInstance(websearch_result, dict)
        self.assertIn('is_fallback', websearch_result)
        print("✅ 웹 검색 대체 전략 테스트 성공")
    
    def test_alert_system_functionality(self):
        """알림 시스템 기능 테스트"""
        print("=== 알림 시스템 기능 테스트 ===")
        
        from tools.external.alert_system import AlertSystem, AlertRule, AlertChannel
        
        # 새로운 알림 시스템 인스턴스 생성 (테스트용)
        test_alert_system = AlertSystem()
        
        # 1. 기본 규칙 확인
        active_rules = test_alert_system.get_active_rules()
        self.assertIsInstance(active_rules, list)
        self.assertGreater(len(active_rules), 0)
        print(f"✅ 기본 알림 규칙: {len(active_rules)}개")
        
        # 2. 테스트 규칙 추가
        test_rule = AlertRule(
            name="test_rule",
            condition=lambda data: data.get("test") is True,
            message_template="테스트 알림: {message}",
            channels=[AlertChannel.LOG, AlertChannel.CONSOLE]
        )
        
        test_alert_system.add_rule(test_rule)
        updated_rules = test_alert_system.get_active_rules()
        self.assertEqual(len(updated_rules), len(active_rules) + 1)
        print("✅ 알림 규칙 추가 성공")
        
        # 3. 알림 이력 확인
        alert_history = test_alert_system.get_alert_history()
        self.assertIsInstance(alert_history, list)
        print(f"✅ 알림 이력 조회: {len(alert_history)}개")
    
    def test_service_integration(self):
        """서비스 통합 테스트"""
        print("=== 서비스 통합 테스트 ===")
        
        # 1. 모든 도구 import 테스트
        try:
            from tools.external import (
                search_knowledge_base,
                search_web_for_answer,
                chatgpt_api_tool,
                get_service_health_status,
                prompt_practice_tool
            )
            print("✅ 모든 도구 import 성공")
        except ImportError as e:
            self.fail(f"도구 import 실패: {str(e)}")
        
        # 2. 오류 처리 통합 테스트
        from tools.external.error_handler import get_all_service_status
        
        # 여러 오류 생성하여 시스템 반응 테스트
        from tools.external.error_handler import handle_service_error, ServiceType, ErrorSeverity
        
        for i in range(3):
            handle_service_error(
                service_type=ServiceType.CHATGPT_API,
                error_code=f"test_error_{i}",
                error_message=f"테스트 오류 {i}",
                context={"test_batch": True},
                severity=ErrorSeverity.LOW
            )
        
        status = get_all_service_status()
        self.assertGreater(status['total_errors_24h'], 0)
        print(f"✅ 통합 오류 처리: {status['total_errors_24h']}개 오류 기록")
    
    def test_performance_metrics(self):
        """성능 메트릭 테스트"""
        print("=== 성능 메트릭 테스트 ===")
        
        from tools.external.api_monitor import api_monitor
        import time
        
        # 1. 여러 API 호출 시뮬레이션
        start_time = time.time()
        
        for i in range(5):
            from tools.external.api_monitor import log_api_call
            log_api_call(
                endpoint="test/performance",
                success=i % 4 != 0,  # 25% 실패율
                response_time=0.1 + (i * 0.05),
                token_usage={"total_tokens": 50 + i * 10},
                model="test-model"
            )
        
        # 2. 메트릭 확인
        metrics = api_monitor.get_current_metrics()
        
        self.assertGreaterEqual(metrics['total_calls'], 5)
        self.assertGreater(metrics['success_rate'], 0.5)
        self.assertGreater(metrics['average_response_time'], 0)
        
        print(f"✅ 성능 메트릭 - 총 호출: {metrics['total_calls']}, 성공률: {metrics['success_rate']:.1%}")
        
        # 3. 최근 호출 기록 확인
        recent_calls = api_monitor.get_recent_calls(minutes=1)
        self.assertGreaterEqual(len(recent_calls), 5)
        print(f"✅ 최근 호출 기록: {len(recent_calls)}개")

def run_comprehensive_test():
    """포괄적인 테스트 실행"""
    print("🚀 Task 8 포괄적인 오프라인 테스트 시작")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 환경 정보 출력
    print(f"\nPython 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")
    
    # 테스트 실행
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask8Offline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 포괄적인 테스트 결과 요약")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"총 테스트: {total_tests}")
    print(f"성공: {passed}")
    print(f"실패: {failures}")
    print(f"오류: {errors}")
    print(f"성공률: {passed/total_tests*100:.1f}%")
    
    if failures == 0 and errors == 0:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n✅ Task 8 구현이 정상적으로 작동합니다:")
        print("   - 오류 처리 시스템 ✅")
        print("   - API 모니터링 시스템 ✅")
        print("   - 프롬프트 품질 분석 ✅")
        print("   - 대체 전략 시스템 ✅")
        print("   - 알림 시스템 ✅")
        print("   - 서비스 통합 ✅")
        print("   - 성능 메트릭 ✅")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        if failures:
            print("\n실패한 테스트:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        if errors:
            print("\n오류가 발생한 테스트:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print(f"\n테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total_tests

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)