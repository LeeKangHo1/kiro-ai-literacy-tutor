# services/performance_service.py
"""
성능 최적화 및 모니터링 서비스
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from functools import wraps
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from models import db
from models.user import User, UserLearningProgress
from models.learning_loop import LearningLoop
from models.conversation import Conversation
from models.quiz_attempt import QuizAttempt

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics = {}
        self.query_stats = {}
        self.api_stats = {}
    
    def record_query_time(self, query_name: str, execution_time: float):
        """쿼리 실행 시간 기록"""
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            }
        
        stats = self.query_stats[query_name]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
    
    def record_api_time(self, endpoint: str, execution_time: float, status_code: int):
        """API 응답 시간 기록"""
        if endpoint not in self.api_stats:
            self.api_stats[endpoint] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf'),
                'success_count': 0,
                'error_count': 0
            }
        
        stats = self.api_stats[endpoint]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
        
        if 200 <= status_code < 300:
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            }
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return {}
    
    def get_database_metrics(self) -> Dict[str, Any]:
        """데이터베이스 메트릭 수집"""
        try:
            engine = db.engine
            pool = engine.pool
            
            # 연결 풀 상태
            pool_status = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            } if isinstance(pool, QueuePool) else {}
            
            # 테이블별 레코드 수
            table_counts = {}
            try:
                table_counts['users'] = User.query.count()
                table_counts['learning_loops'] = LearningLoop.query.count()
                table_counts['conversations'] = Conversation.query.count()
                table_counts['quiz_attempts'] = QuizAttempt.query.count()
                table_counts['user_learning_progress'] = UserLearningProgress.query.count()
            except Exception as e:
                logger.warning(f"테이블 카운트 조회 실패: {e}")
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'connection_pool': pool_status,
                'table_counts': table_counts,
                'query_stats': self.query_stats,
                'slow_queries': self.get_slow_queries()
            }
        except Exception as e:
            logger.error(f"데이터베이스 메트릭 수집 실패: {e}")
            return {}
    
    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """느린 쿼리 목록 반환"""
        slow_queries = []
        for query_name, stats in self.query_stats.items():
            if stats['avg_time'] > threshold:
                slow_queries.append({
                    'query_name': query_name,
                    'avg_time': stats['avg_time'],
                    'max_time': stats['max_time'],
                    'count': stats['count']
                })
        
        return sorted(slow_queries, key=lambda x: x['avg_time'], reverse=True)
    
    def get_api_performance(self) -> Dict[str, Any]:
        """API 성능 통계"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': self.api_stats,
            'slow_endpoints': self.get_slow_endpoints()
        }
    
    def get_slow_endpoints(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """느린 API 엔드포인트 목록"""
        slow_endpoints = []
        for endpoint, stats in self.api_stats.items():
            if stats['avg_time'] > threshold:
                slow_endpoints.append({
                    'endpoint': endpoint,
                    'avg_time': stats['avg_time'],
                    'max_time': stats['max_time'],
                    'count': stats['count'],
                    'error_rate': (stats['error_count'] / stats['count']) * 100 if stats['count'] > 0 else 0
                })
        
        return sorted(slow_endpoints, key=lambda x: x['avg_time'], reverse=True)
    
    def reset_stats(self):
        """통계 초기화"""
        self.query_stats.clear()
        self.api_stats.clear()


# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()


def monitor_query_performance(query_name: str):
    """쿼리 성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                performance_monitor.record_query_time(query_name, execution_time)
                
                if execution_time > 1.0:  # 1초 이상 걸린 쿼리 로깅
                    logger.warning(f"느린 쿼리 감지: {query_name} - {execution_time:.2f}초")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_query_time(f"{query_name}_error", execution_time)
                logger.error(f"쿼리 실행 오류: {query_name} - {e}")
                raise
        return wrapper
    return decorator


def monitor_api_performance(endpoint: str):
    """API 성능 모니터링 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                
                # Flask Response 객체에서 상태 코드 추출
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                execution_time = time.time() - start_time
                performance_monitor.record_api_time(endpoint, execution_time, status_code)
                
                if execution_time > 2.0:  # 2초 이상 걸린 API 로깅
                    logger.warning(f"느린 API 감지: {endpoint} - {execution_time:.2f}초")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_api_time(endpoint, execution_time, 500)
                logger.error(f"API 실행 오류: {endpoint} - {e}")
                raise
        return wrapper
    return decorator


class DatabaseOptimizer:
    """데이터베이스 최적화 클래스"""
    
    @staticmethod
    def create_indexes():
        """성능 최적화를 위한 인덱스 생성"""
        try:
            # 복합 인덱스 생성
            indexes = [
                # 사용자 관련 인덱스
                "CREATE INDEX IF NOT EXISTS idx_users_type_level ON USERS(user_type, user_level)",
                "CREATE INDEX IF NOT EXISTS idx_users_active_created ON USERS(is_active, created_at)",
                
                # 학습 진도 관련 인덱스
                "CREATE INDEX IF NOT EXISTS idx_progress_user_status ON USER_LEARNING_PROGRESS(user_id, completion_status)",
                "CREATE INDEX IF NOT EXISTS idx_progress_chapter_status ON USER_LEARNING_PROGRESS(chapter_id, completion_status)",
                "CREATE INDEX IF NOT EXISTS idx_progress_last_accessed ON USER_LEARNING_PROGRESS(last_accessed_at DESC)",
                
                # 학습 루프 관련 인덱스
                "CREATE INDEX IF NOT EXISTS idx_loops_user_chapter_status ON LEARNING_LOOPS(user_id, chapter_id, loop_status)",
                "CREATE INDEX IF NOT EXISTS idx_loops_started_at ON LEARNING_LOOPS(started_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_loops_completed_at ON LEARNING_LOOPS(completed_at DESC)",
                
                # 대화 관련 인덱스
                "CREATE INDEX IF NOT EXISTS idx_conversations_loop_sequence ON CONVERSATIONS(loop_id, sequence_order)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON CONVERSATIONS(timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_agent ON CONVERSATIONS(agent_name, message_type)",
                
                # 퀴즈 시도 관련 인덱스
                "CREATE INDEX IF NOT EXISTS idx_quiz_user_chapter ON QUIZ_ATTEMPTS(user_id, chapter_id)",
                "CREATE INDEX IF NOT EXISTS idx_quiz_loop_score ON QUIZ_ATTEMPTS(loop_id, score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_quiz_attempted_at ON QUIZ_ATTEMPTS(attempted_at DESC)"
            ]
            
            for index_sql in indexes:
                try:
                    db.session.execute(text(index_sql))
                    logger.info(f"인덱스 생성 완료: {index_sql}")
                except Exception as e:
                    logger.warning(f"인덱스 생성 실패: {index_sql} - {e}")
            
            db.session.commit()
            logger.info("모든 성능 최적화 인덱스 생성 완료")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"인덱스 생성 중 오류 발생: {e}")
    
    @staticmethod
    def analyze_table_performance():
        """테이블 성능 분석"""
        try:
            # MySQL의 경우 ANALYZE TABLE 실행
            tables = ['USERS', 'USER_LEARNING_PROGRESS', 'LEARNING_LOOPS', 
                     'CONVERSATIONS', 'QUIZ_ATTEMPTS', 'CHAPTERS']
            
            for table in tables:
                try:
                    db.session.execute(text(f"ANALYZE TABLE {table}"))
                    logger.info(f"테이블 분석 완료: {table}")
                except Exception as e:
                    logger.warning(f"테이블 분석 실패: {table} - {e}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"테이블 성능 분석 중 오류: {e}")
    
    @staticmethod
    def get_table_sizes():
        """테이블 크기 정보 조회"""
        try:
            query = text("""
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                    table_rows
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY (data_length + index_length) DESC
            """)
            
            result = db.session.execute(query)
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"테이블 크기 조회 실패: {e}")
            return []
    
    @staticmethod
    def optimize_tables():
        """테이블 최적화 실행"""
        try:
            tables = ['USERS', 'USER_LEARNING_PROGRESS', 'LEARNING_LOOPS', 
                     'CONVERSATIONS', 'QUIZ_ATTEMPTS', 'CHAPTERS']
            
            for table in tables:
                try:
                    db.session.execute(text(f"OPTIMIZE TABLE {table}"))
                    logger.info(f"테이블 최적화 완료: {table}")
                except Exception as e:
                    logger.warning(f"테이블 최적화 실패: {table} - {e}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"테이블 최적화 중 오류: {e}")


class StateOptimizer:
    """State 관리 메모리 최적화 클래스"""
    
    @staticmethod
    def optimize_tutor_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """TutorState 메모리 사용량 최적화"""
        optimized_state = state.copy()
        
        # 현재 루프 대화 최적화 (최대 50개 메시지로 제한)
        if 'current_loop_conversations' in optimized_state:
            conversations = optimized_state['current_loop_conversations']
            if len(conversations) > 50:
                # 최근 50개만 유지
                optimized_state['current_loop_conversations'] = conversations[-50:]
                logger.info(f"대화 기록 최적화: {len(conversations)} -> 50개")
        
        # 최근 루프 요약 최적화 (최대 5개로 제한)
        if 'recent_loops_summary' in optimized_state:
            summaries = optimized_state['recent_loops_summary']
            if len(summaries) > 5:
                optimized_state['recent_loops_summary'] = summaries[-5:]
                logger.info(f"루프 요약 최적화: {len(summaries)} -> 5개")
        
        # 긴 메시지 내용 압축
        StateOptimizer._compress_long_messages(optimized_state)
        
        return optimized_state
    
    @staticmethod
    def _compress_long_messages(state: Dict[str, Any], max_length: int = 1000):
        """긴 메시지 내용 압축"""
        if 'current_loop_conversations' in state:
            for conversation in state['current_loop_conversations']:
                if 'user_message' in conversation and conversation['user_message']:
                    if len(conversation['user_message']) > max_length:
                        conversation['user_message'] = conversation['user_message'][:max_length] + "...[압축됨]"
                
                if 'system_response' in conversation and conversation['system_response']:
                    if len(conversation['system_response']) > max_length:
                        conversation['system_response'] = conversation['system_response'][:max_length] + "...[압축됨]"
        
        if 'recent_loops_summary' in state:
            for summary in state['recent_loops_summary']:
                if 'summary' in summary and len(summary['summary']) > max_length:
                    summary['summary'] = summary['summary'][:max_length] + "...[압축됨]"
    
    @staticmethod
    def calculate_state_size(state: Dict[str, Any]) -> Dict[str, Any]:
        """State 크기 계산"""
        import sys
        
        total_size = sys.getsizeof(state)
        component_sizes = {}
        
        for key, value in state.items():
            component_sizes[key] = sys.getsizeof(value)
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'component_sizes': component_sizes,
            'largest_components': sorted(
                component_sizes.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }


class PerformanceService:
    """성능 관리 통합 서비스"""
    
    def __init__(self):
        self.monitor = performance_monitor
        self.db_optimizer = DatabaseOptimizer()
        self.state_optimizer = StateOptimizer()
    
    def initialize_performance_optimizations(self):
        """성능 최적화 초기화"""
        try:
            logger.info("성능 최적화 초기화 시작")
            
            # 데이터베이스 인덱스 생성
            self.db_optimizer.create_indexes()
            
            # 테이블 분석
            self.db_optimizer.analyze_table_performance()
            
            logger.info("성능 최적화 초기화 완료")
            
        except Exception as e:
            logger.error(f"성능 최적화 초기화 실패: {e}")
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """종합 성능 메트릭 수집"""
        return {
            'system': self.monitor.get_system_metrics(),
            'database': self.monitor.get_database_metrics(),
            'api': self.monitor.get_api_performance(),
            'table_sizes': self.db_optimizer.get_table_sizes()
        }
    
    def optimize_system_performance(self):
        """시스템 성능 최적화 실행"""
        try:
            logger.info("시스템 성능 최적화 시작")
            
            # 데이터베이스 최적화
            self.db_optimizer.optimize_tables()
            
            # 통계 초기화 (메모리 정리)
            self.monitor.reset_stats()
            
            logger.info("시스템 성능 최적화 완료")
            
        except Exception as e:
            logger.error(f"시스템 성능 최적화 실패: {e}")
    
    def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """성능 알림 확인"""
        alerts = []
        
        try:
            # 시스템 메트릭 확인
            system_metrics = self.monitor.get_system_metrics()
            if system_metrics.get('cpu_percent', 0) > 80:
                alerts.append({
                    'type': 'system',
                    'level': 'warning',
                    'message': f"CPU 사용률 높음: {system_metrics['cpu_percent']}%"
                })
            
            if system_metrics.get('memory', {}).get('percent', 0) > 85:
                alerts.append({
                    'type': 'system',
                    'level': 'warning',
                    'message': f"메모리 사용률 높음: {system_metrics['memory']['percent']}%"
                })
            
            # 느린 쿼리 확인
            slow_queries = self.monitor.get_slow_queries(threshold=1.0)
            if slow_queries:
                alerts.append({
                    'type': 'database',
                    'level': 'warning',
                    'message': f"느린 쿼리 {len(slow_queries)}개 감지",
                    'details': slow_queries[:3]  # 상위 3개만
                })
            
            # 느린 API 확인
            slow_endpoints = self.monitor.get_slow_endpoints(threshold=2.0)
            if slow_endpoints:
                alerts.append({
                    'type': 'api',
                    'level': 'warning',
                    'message': f"느린 API 엔드포인트 {len(slow_endpoints)}개 감지",
                    'details': slow_endpoints[:3]  # 상위 3개만
                })
            
        except Exception as e:
            logger.error(f"성능 알림 확인 실패: {e}")
            alerts.append({
                'type': 'system',
                'level': 'error',
                'message': f"성능 모니터링 오류: {e}"
            })
        
        return alerts


# 전역 성능 서비스 인스턴스
performance_service = PerformanceService()