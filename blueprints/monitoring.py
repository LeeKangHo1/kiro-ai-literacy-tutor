# blueprints/monitoring.py
"""
성능 모니터링 및 시스템 상태 API
"""

from flask import Blueprint, jsonify, request
from utils.auth_middleware import token_required, admin_required
from utils.performance_middleware import performance_monitoring, health_checker
from services.performance_service import performance_service
from utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/health', methods=['GET'])
@performance_monitoring('GET /monitoring/health')
def health_check():
    """시스템 상태 확인"""
    try:
        health_status = health_checker.get_system_health()
        
        # HTTP 상태 코드 결정
        if health_status['overall_status'] == 'healthy':
            status_code = 200
        elif health_status['overall_status'] == 'degraded':
            status_code = 200  # 일부 서비스만 문제가 있는 경우
        else:
            status_code = 503  # 서비스 사용 불가
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        return error_response("상태 확인 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/metrics', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/metrics')
def get_metrics():
    """성능 메트릭 조회 (관리자 전용)"""
    try:
        metrics = performance_service.get_comprehensive_metrics()
        return success_response("성능 메트릭 조회 성공", metrics)
        
    except Exception as e:
        logger.error(f"메트릭 조회 실패: {e}")
        return error_response("메트릭 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/metrics/system', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/metrics/system')
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        system_metrics = performance_service.monitor.get_system_metrics()
        return success_response("시스템 메트릭 조회 성공", system_metrics)
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 실패: {e}")
        return error_response("시스템 메트릭 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/metrics/database', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/metrics/database')
def get_database_metrics():
    """데이터베이스 메트릭 조회"""
    try:
        db_metrics = performance_service.monitor.get_database_metrics()
        return success_response("데이터베이스 메트릭 조회 성공", db_metrics)
        
    except Exception as e:
        logger.error(f"데이터베이스 메트릭 조회 실패: {e}")
        return error_response("데이터베이스 메트릭 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/metrics/api', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/metrics/api')
def get_api_metrics():
    """API 성능 메트릭 조회"""
    try:
        api_metrics = performance_service.monitor.get_api_performance()
        return success_response("API 메트릭 조회 성공", api_metrics)
        
    except Exception as e:
        logger.error(f"API 메트릭 조회 실패: {e}")
        return error_response("API 메트릭 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/alerts', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/alerts')
def get_performance_alerts():
    """성능 알림 조회"""
    try:
        alerts = performance_service.check_performance_alerts()
        return success_response("성능 알림 조회 성공", {
            'alerts': alerts,
            'alert_count': len(alerts),
            'has_critical_alerts': any(alert['level'] == 'error' for alert in alerts)
        })
        
    except Exception as e:
        logger.error(f"성능 알림 조회 실패: {e}")
        return error_response("성능 알림 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/optimize', methods=['POST'])
@token_required
@admin_required
@performance_monitoring('POST /monitoring/optimize')
def optimize_performance():
    """성능 최적화 실행"""
    try:
        performance_service.optimize_system_performance()
        return success_response("성능 최적화가 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"성능 최적화 실패: {e}")
        return error_response("성능 최적화 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/database/tables', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/database/tables')
def get_table_info():
    """데이터베이스 테이블 정보 조회"""
    try:
        table_sizes = performance_service.db_optimizer.get_table_sizes()
        return success_response("테이블 정보 조회 성공", {
            'tables': table_sizes,
            'total_tables': len(table_sizes)
        })
        
    except Exception as e:
        logger.error(f"테이블 정보 조회 실패: {e}")
        return error_response("테이블 정보 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/database/optimize', methods=['POST'])
@token_required
@admin_required
@performance_monitoring('POST /monitoring/database/optimize')
def optimize_database():
    """데이터베이스 최적화 실행"""
    try:
        performance_service.db_optimizer.optimize_tables()
        return success_response("데이터베이스 최적화가 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"데이터베이스 최적화 실패: {e}")
        return error_response("데이터베이스 최적화 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/stats/reset', methods=['POST'])
@token_required
@admin_required
@performance_monitoring('POST /monitoring/stats/reset')
def reset_stats():
    """성능 통계 초기화"""
    try:
        performance_service.monitor.reset_stats()
        return success_response("성능 통계가 초기화되었습니다.")
        
    except Exception as e:
        logger.error(f"통계 초기화 실패: {e}")
        return error_response("통계 초기화 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/slow-queries', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/slow-queries')
def get_slow_queries():
    """느린 쿼리 목록 조회"""
    try:
        threshold = float(request.args.get('threshold', 1.0))
        slow_queries = performance_service.monitor.get_slow_queries(threshold)
        
        return success_response("느린 쿼리 조회 성공", {
            'slow_queries': slow_queries,
            'threshold_seconds': threshold,
            'count': len(slow_queries)
        })
        
    except Exception as e:
        logger.error(f"느린 쿼리 조회 실패: {e}")
        return error_response("느린 쿼리 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/slow-endpoints', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/slow-endpoints')
def get_slow_endpoints():
    """느린 API 엔드포인트 목록 조회"""
    try:
        threshold = float(request.args.get('threshold', 2.0))
        slow_endpoints = performance_service.monitor.get_slow_endpoints(threshold)
        
        return success_response("느린 엔드포인트 조회 성공", {
            'slow_endpoints': slow_endpoints,
            'threshold_seconds': threshold,
            'count': len(slow_endpoints)
        })
        
    except Exception as e:
        logger.error(f"느린 엔드포인트 조회 실패: {e}")
        return error_response("느린 엔드포인트 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/state/analyze', methods=['POST'])
@token_required
@admin_required
@performance_monitoring('POST /monitoring/state/analyze')
def analyze_state_size():
    """State 크기 분석"""
    try:
        # 요청 본문에서 State 데이터 받기
        state_data = request.get_json()
        if not state_data:
            return error_response("State 데이터가 필요합니다.", 400)
        
        size_info = performance_service.state_optimizer.calculate_state_size(state_data)
        return success_response("State 크기 분석 완료", size_info)
        
    except Exception as e:
        logger.error(f"State 크기 분석 실패: {e}")
        return error_response("State 크기 분석 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/state/optimize', methods=['POST'])
@token_required
@admin_required
@performance_monitoring('POST /monitoring/state/optimize')
def optimize_state():
    """State 최적화"""
    try:
        # 요청 본문에서 State 데이터 받기
        state_data = request.get_json()
        if not state_data:
            return error_response("State 데이터가 필요합니다.", 400)
        
        # 최적화 전 크기
        original_size = performance_service.state_optimizer.calculate_state_size(state_data)
        
        # 최적화 실행
        optimized_state = performance_service.state_optimizer.optimize_tutor_state(state_data)
        
        # 최적화 후 크기
        optimized_size = performance_service.state_optimizer.calculate_state_size(optimized_state)
        
        return success_response("State 최적화 완료", {
            'original_size_mb': original_size['total_size_mb'],
            'optimized_size_mb': optimized_size['total_size_mb'],
            'reduction_mb': original_size['total_size_mb'] - optimized_size['total_size_mb'],
            'reduction_percentage': ((original_size['total_size_mb'] - optimized_size['total_size_mb']) / original_size['total_size_mb']) * 100 if original_size['total_size_mb'] > 0 else 0,
            'optimized_state': optimized_state
        })
        
    except Exception as e:
        logger.error(f"State 최적화 실패: {e}")
        return error_response("State 최적화 중 오류가 발생했습니다.", 500)


@monitoring_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return error_response("요청한 리소스를 찾을 수 없습니다.", 404)


@monitoring_bp.route('/logs/analyze', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/logs/analyze')
def analyze_logs():
    """로그 분석"""
    try:
        from utils.logging_config import LogAnalyzer
        
        hours = int(request.args.get('hours', 24))
        log_file = request.args.get('log_file', 'app.log')
        
        analysis = LogAnalyzer.analyze_log_file(log_file, hours)
        return success_response("로그 분석 완료", analysis)
        
    except Exception as e:
        logger.error(f"로그 분석 실패: {e}")
        return error_response("로그 분석 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/logs/errors', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/logs/errors')
def get_recent_log_errors():
    """최근 로그 에러 조회"""
    try:
        from utils.logging_config import LogAnalyzer
        
        hours = int(request.args.get('hours', 1))
        limit = int(request.args.get('limit', 50))
        log_file = request.args.get('log_file', 'app.log')
        
        errors = LogAnalyzer.get_recent_errors(log_file, hours, limit)
        return success_response("최근 에러 로그 조회 성공", {
            'errors': errors,
            'count': len(errors),
            'period_hours': hours
        })
        
    except Exception as e:
        logger.error(f"에러 로그 조회 실패: {e}")
        return error_response("에러 로그 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/errors/statistics', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/errors/statistics')
def get_error_statistics():
    """오류 통계 조회"""
    try:
        from utils.error_handler import global_error_handler
        
        hours = int(request.args.get('hours', 24))
        stats = global_error_handler.error_tracker.get_error_statistics(hours)
        
        return success_response("오류 통계 조회 성공", stats)
        
    except Exception as e:
        logger.error(f"오류 통계 조회 실패: {e}")
        return error_response("오류 통계 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.route('/errors/recent', methods=['GET'])
@token_required
@admin_required
@performance_monitoring('GET /monitoring/errors/recent')
def get_recent_errors():
    """최근 오류 목록 조회"""
    try:
        from utils.error_handler import global_error_handler
        
        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')
        
        errors = global_error_handler.error_tracker.get_recent_errors(limit, severity)
        
        return success_response("최근 오류 조회 성공", {
            'errors': errors,
            'count': len(errors),
            'severity_filter': severity
        })
        
    except Exception as e:
        logger.error(f"최근 오류 조회 실패: {e}")
        return error_response("최근 오류 조회 중 오류가 발생했습니다.", 500)


@monitoring_bp.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return error_response("요청한 리소스를 찾을 수 없습니다.", 404)


@monitoring_bp.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"모니터링 API 내부 오류: {error}")
    return error_response("서버 내부 오류가 발생했습니다.", 500)