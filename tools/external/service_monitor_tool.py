# tools/external/service_monitor_tool.py
# 서비스 상태 모니터링 도구

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain.tools import tool
from .error_handler import get_all_service_status, get_error_stats, error_handler
from .api_monitor import api_monitor

# 로깅 설정
logger = logging.getLogger(__name__)

def _parse_timestamp(timestamp):
    """타임스탬프 파싱 헬퍼 함수"""
    if isinstance(timestamp, str):
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            return datetime.now()
    elif isinstance(timestamp, datetime):
        return timestamp
    else:
        return datetime.now()

@tool
def get_service_health_status() -> Dict[str, Any]:
    """
    모든 외부 서비스의 건강 상태를 조회합니다.
    
    Returns:
        서비스 상태 정보 딕셔너리
    """
    try:
        # 서비스 상태 조회
        service_status = get_all_service_status()
        
        # API 메트릭 조회
        api_metrics = api_monitor.get_current_metrics()
        
        # 전체 건강도 계산
        healthy_services = sum(1 for service in service_status["services"].values() 
                             if service["status"] == "healthy")
        total_services = len(service_status["services"])
        overall_health = "healthy" if healthy_services == total_services else "degraded"
        
        if service_status["circuit_breakers_active"] > 0:
            overall_health = "critical"
        
        return {
            "overall_health": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": service_status["services"],
            "api_metrics": {
                "success_rate": api_metrics.get("success_rate", 0.0),
                "avg_response_time": api_metrics.get("average_response_time", 0.0),
                "total_calls": api_metrics.get("total_calls", 0),
                "current_status": api_metrics.get("current_status", "unknown")
            },
            "circuit_breakers_active": service_status["circuit_breakers_active"],
            "total_errors_24h": service_status["total_errors_24h"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"서비스 상태 조회 중 오류: {str(e)}")
        return {
            "overall_health": "unknown",
            "error": f"상태 조회 중 오류가 발생했습니다: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@tool
def get_error_report(hours: int = 24) -> Dict[str, Any]:
    """
    지정된 시간 동안의 오류 리포트를 생성합니다.
    
    Args:
        hours: 조회할 시간 범위 (기본값: 24시간)
    
    Returns:
        오류 리포트 딕셔너리
    """
    try:
        # 오류 통계 조회
        error_stats = get_error_stats(hours)
        
        # API 호출 기록 조회
        api_calls = api_monitor.get_recent_calls(minutes=hours * 60)
        
        # 상태 변경 이력 조회
        status_history = api_monitor.get_status_history()
        
        # 최근 상태 변경 필터링
        recent_status_changes = []
        for change in status_history:
            try:
                if isinstance(change["timestamp"], str):
                    change_time = datetime.fromisoformat(change["timestamp"])
                else:
                    change_time = change["timestamp"]
                
                if change_time > datetime.now() - timedelta(hours=hours):
                    recent_status_changes.append(change)
            except (ValueError, KeyError, TypeError):
                # 날짜 파싱 실패 시 건너뛰기
                continue
        
        return {
            "period_hours": hours,
            "error_statistics": error_stats,
            "api_call_summary": {
                "total_calls": len(api_calls),
                "failed_calls": len([call for call in api_calls if not call["success"]]),
                "success_rate": (len([call for call in api_calls if call["success"]]) / len(api_calls) * 100) if api_calls else 0
            },
            "status_changes": len(recent_status_changes),
            "recent_status_changes": recent_status_changes[-5:],  # 최근 5개만
            "recommendations": _generate_recommendations(error_stats),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"오류 리포트 생성 중 오류: {str(e)}")
        return {
            "error": f"리포트 생성 중 오류가 발생했습니다: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def _generate_recommendations(error_stats: Dict[str, Any]) -> List[str]:
    """오류 통계를 바탕으로 권장사항 생성"""
    recommendations = []
    
    if not error_stats.get("statistics"):
        return ["현재 오류가 없습니다. 시스템이 정상적으로 작동하고 있습니다."]
    
    stats = error_stats["statistics"]
    
    # 가장 문제가 많은 서비스 확인
    most_problematic = error_stats.get("most_problematic_service")
    if most_problematic:
        recommendations.append(f"{most_problematic} 서비스의 오류가 가장 많습니다. 해당 서비스 상태를 점검해보세요.")
    
    # 심각도별 권장사항
    if stats.get("by_severity", {}).get("critical", 0) > 0:
        recommendations.append("심각한 오류가 발생했습니다. 즉시 시스템 관리자에게 알려주세요.")
    
    if stats.get("by_severity", {}).get("high", 0) > 5:
        recommendations.append("높은 심각도의 오류가 많이 발생했습니다. 서비스 설정을 확인해보세요.")
    
    # 서비스별 권장사항
    service_errors = stats.get("by_service", {})
    
    if service_errors.get("chatgpt_api", 0) > 10:
        recommendations.append("ChatGPT API 오류가 많습니다. API 키와 사용량을 확인해보세요.")
    
    if service_errors.get("chromadb", 0) > 5:
        recommendations.append("ChromaDB 연결 문제가 있습니다. 데이터베이스 상태를 확인해보세요.")
    
    if service_errors.get("web_search", 0) > 5:
        recommendations.append("웹 검색 서비스에 문제가 있습니다. 네트워크 연결을 확인해보세요.")
    
    if not recommendations:
        recommendations.append("시스템이 안정적으로 작동하고 있습니다.")
    
    return recommendations

@tool
def reset_service_errors() -> Dict[str, Any]:
    """
    서비스 오류 기록을 초기화합니다.
    
    Returns:
        초기화 결과 딕셔너리
    """
    try:
        # 오류 처리기 메트릭 초기화
        old_status = get_all_service_status()
        error_handler.reset_metrics() if hasattr(error_handler, 'reset_metrics') else None
        
        # API 모니터 메트릭 초기화
        old_api_metrics = api_monitor.get_current_metrics()
        api_monitor.reset_metrics()
        
        return {
            "success": True,
            "message": "서비스 오류 기록이 성공적으로 초기화되었습니다.",
            "previous_total_errors": old_status.get("total_errors_24h", 0),
            "previous_api_calls": old_api_metrics.get("total_calls", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"서비스 오류 초기화 중 오류: {str(e)}")
        return {
            "success": False,
            "message": f"초기화 중 오류가 발생했습니다: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@tool
def test_service_connectivity() -> Dict[str, Any]:
    """
    모든 외부 서비스의 연결 상태를 테스트합니다.
    
    Returns:
        연결 테스트 결과 딕셔너리
    """
    try:
        test_results = {}
        
        # ChatGPT API 테스트
        try:
            from .chatgpt_tool import api_manager
            test_response = api_manager.call_chatgpt_api(
                prompt="테스트",
                system_message="간단히 '테스트 성공'이라고만 답변해주세요.",
                analyze_quality=False
            )
            test_results["chatgpt_api"] = {
                "status": "connected" if test_response.success else "failed",
                "response_time": test_response.response_time,
                "error": test_response.error_message if not test_response.success else None
            }
        except Exception as e:
            test_results["chatgpt_api"] = {
                "status": "error",
                "error": str(e)
            }
        
        # ChromaDB 테스트
        try:
            from .chromadb_tool import chromadb_tool
            stats = chromadb_tool.get_collection_stats()
            test_results["chromadb"] = {
                "status": "connected" if "error" not in stats else "failed",
                "collection_status": stats.get("status", "unknown"),
                "total_documents": stats.get("total_documents", 0),
                "error": stats.get("error")
            }
        except Exception as e:
            test_results["chromadb"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 웹 검색 테스트
        try:
            from .web_search_tool import web_search_tool
            search_results = web_search_tool.search_web("테스트", num_results=1)
            test_results["web_search"] = {
                "status": "connected" if search_results and not search_results[0].get("error") else "limited",
                "dummy_mode": web_search_tool.dummy_mode,
                "results_count": len(search_results)
            }
        except Exception as e:
            test_results["web_search"] = {
                "status": "error",
                "error": str(e)
            }
        
        # 전체 상태 평가
        connected_services = sum(1 for result in test_results.values() 
                               if result["status"] == "connected")
        total_services = len(test_results)
        
        overall_status = "healthy" if connected_services == total_services else "degraded"
        if connected_services == 0:
            overall_status = "critical"
        
        return {
            "overall_status": overall_status,
            "connected_services": connected_services,
            "total_services": total_services,
            "service_tests": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"서비스 연결 테스트 중 오류: {str(e)}")
        return {
            "overall_status": "error",
            "error": f"연결 테스트 중 오류가 발생했습니다: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }