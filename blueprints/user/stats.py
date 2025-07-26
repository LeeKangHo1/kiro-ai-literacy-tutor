# blueprints/user/stats.py
# 학습 통계 및 기록 API 엔드포인트

from flask import request, jsonify, g, Blueprint
from utils.response_utils import create_response
from utils.jwt_utils import token_required
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

logger = logging.getLogger(__name__)

# 통계 관련 블루프린트 생성
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/overview', methods=['GET'])
@token_required
def get_stats_overview():
    """
    사용자 학습 통계 개요 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "학습 통계 개요를 조회했습니다.",
        "data": {
            "overall_progress": {
                "total_chapters": 5,
                "completed_chapters": 3,
                "in_progress_chapters": 1,
                "average_understanding": 85.5,
                "total_study_time": 180
            },
            "recent_activity": {
                "last_7_days": {
                    "study_sessions": 12,
                    "total_time_minutes": 240,
                    "chapters_completed": 1,
                    "quiz_attempts": 8
                }
            },
            "achievements": {
                "total_quizzes_completed": 25,
                "average_quiz_score": 88.5,
                "longest_study_streak": 7,
                "current_streak": 3
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.user import User, UserLearningProgress
        from models.learning_loop import LearningLoop
        from models.quiz_attempt import QuizAttempt
        
        # 사용자 조회
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 전체 진도 요약
        overall_progress = user.get_overall_progress()
        
        # 최근 7일 활동 통계
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_loops = LearningLoop.query.filter(
            and_(
                LearningLoop.user_id == user_id,
                LearningLoop.started_at >= seven_days_ago
            )
        ).all()
        
        recent_quizzes = QuizAttempt.query.filter(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.attempted_at >= seven_days_ago
            )
        ).all()
        
        # 최근 완료된 챕터 수
        recent_completed = UserLearningProgress.query.filter(
            and_(
                UserLearningProgress.user_id == user_id,
                UserLearningProgress.completed_at >= seven_days_ago,
                UserLearningProgress.completion_status == 'completed'
            )
        ).count()
        
        # 최근 7일 총 학습 시간 계산
        recent_study_time = 0
        for loop in recent_loops:
            if loop.completed_at and loop.started_at:
                duration = loop.completed_at - loop.started_at
                recent_study_time += int(duration.total_seconds() / 60)
        
        # 전체 퀴즈 통계
        all_quizzes = QuizAttempt.query.filter_by(user_id=user_id).all()
        total_quizzes = len(all_quizzes)
        average_quiz_score = sum([q.score for q in all_quizzes]) / total_quizzes if total_quizzes > 0 else 0
        
        # 학습 연속일 계산 (간단한 버전)
        current_streak = StatsService.calculate_current_streak(user_id)
        longest_streak = StatsService.calculate_longest_streak(user_id)
        
        return jsonify(create_response(
            success=True,
            message="학습 통계 개요를 조회했습니다.",
            data={
                'overall_progress': overall_progress,
                'recent_activity': {
                    'last_7_days': {
                        'study_sessions': len(recent_loops),
                        'total_time_minutes': recent_study_time,
                        'chapters_completed': recent_completed,
                        'quiz_attempts': len(recent_quizzes)
                    }
                },
                'achievements': {
                    'total_quizzes_completed': total_quizzes,
                    'average_quiz_score': round(average_quiz_score, 2),
                    'longest_study_streak': longest_streak,
                    'current_streak': current_streak
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"학습 통계 개요 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@stats_bp.route('/progress', methods=['GET'])
@token_required
def get_progress_stats():
    """
    학습 진도 상세 통계 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        period (optional): 조회 기간 (7d, 30d, 90d, all) - 기본값: 30d
    
    Response:
    {
        "success": true,
        "message": "학습 진도 통계를 조회했습니다.",
        "data": {
            "period": "30d",
            "chapters_progress": [
                {
                    "chapter_id": 1,
                    "chapter_title": "AI는 무엇인가?",
                    "completion_status": "completed",
                    "progress_percentage": 100.0,
                    "understanding_score": 88.5,
                    "study_time_minutes": 45,
                    "completed_at": "2024-01-01T00:00:00"
                }
            ],
            "daily_progress": [
                {
                    "date": "2024-01-01",
                    "study_time_minutes": 60,
                    "chapters_studied": 2,
                    "quiz_attempts": 3
                }
            ],
            "summary": {
                "total_study_time": 180,
                "average_daily_time": 6,
                "most_productive_day": "Monday",
                "completion_rate": 75.0
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 쿼리 파라미터 추출
        period = request.args.get('period', '30d')
        
        # 기간 설정
        if period == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:  # 'all'
            start_date = datetime.min
        
        from models.user import UserLearningProgress
        from models.chapter import Chapter
        from models.learning_loop import LearningLoop
        from models.quiz_attempt import QuizAttempt
        
        # 챕터별 진도 조회
        progress_query = UserLearningProgress.query.filter_by(user_id=user_id)
        if period != 'all':
            progress_query = progress_query.filter(
                UserLearningProgress.last_accessed_at >= start_date
            )
        
        user_progress = progress_query.all()
        
        chapters_progress = []
        for progress in user_progress:
            chapter = Chapter.get_by_id(progress.chapter_id)
            if chapter:
                chapters_progress.append({
                    'chapter_id': progress.chapter_id,
                    'chapter_title': chapter.title,
                    'chapter_number': chapter.chapter_number,
                    'completion_status': progress.completion_status,
                    'progress_percentage': float(progress.progress_percentage),
                    'understanding_score': float(progress.understanding_score),
                    'study_time_minutes': progress.total_study_time,
                    'quiz_attempts_count': progress.quiz_attempts_count,
                    'average_quiz_score': float(progress.average_quiz_score),
                    'started_at': progress.started_at.isoformat() if progress.started_at else None,
                    'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                    'last_accessed_at': progress.last_accessed_at.isoformat() if progress.last_accessed_at else None
                })
        
        # 일별 진도 통계
        daily_progress = StatsService.get_daily_progress(user_id, start_date)
        
        # 요약 통계
        total_study_time = sum([p['study_time_minutes'] for p in chapters_progress])
        days_in_period = (datetime.utcnow() - start_date).days if period != 'all' else 30
        average_daily_time = total_study_time / max(days_in_period, 1)
        
        completed_chapters = len([p for p in chapters_progress if p['completion_status'] == 'completed'])
        total_chapters = len(chapters_progress)
        completion_rate = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        
        # 가장 생산적인 요일 계산
        most_productive_day = StatsService.get_most_productive_day(user_id, start_date)
        
        return jsonify(create_response(
            success=True,
            message="학습 진도 통계를 조회했습니다.",
            data={
                'period': period,
                'date_range': {
                    'start_date': start_date.isoformat() if period != 'all' else None,
                    'end_date': datetime.utcnow().isoformat()
                },
                'chapters_progress': chapters_progress,
                'daily_progress': daily_progress,
                'summary': {
                    'total_study_time': total_study_time,
                    'average_daily_time': round(average_daily_time, 1),
                    'most_productive_day': most_productive_day,
                    'completion_rate': round(completion_rate, 2),
                    'total_chapters': total_chapters,
                    'completed_chapters': completed_chapters
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"학습 진도 통계 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@stats_bp.route('/quiz', methods=['GET'])
@token_required
def get_quiz_stats():
    """
    퀴즈 통계 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        chapter_id (optional): 특정 챕터의 퀴즈 통계만 조회
        period (optional): 조회 기간 (7d, 30d, 90d, all) - 기본값: all
    
    Response:
    {
        "success": true,
        "message": "퀴즈 통계를 조회했습니다.",
        "data": {
            "overall_stats": {
                "total_attempts": 25,
                "correct_attempts": 20,
                "success_rate": 80.0,
                "average_score": 85.5,
                "total_time_spent": 450
            },
            "chapter_stats": [
                {
                    "chapter_id": 1,
                    "chapter_title": "AI는 무엇인가?",
                    "attempts": 8,
                    "correct": 6,
                    "success_rate": 75.0,
                    "average_score": 82.5,
                    "best_score": 95.0,
                    "latest_attempt": "2024-01-01T00:00:00"
                }
            ],
            "performance_trend": [
                {
                    "date": "2024-01-01",
                    "attempts": 3,
                    "average_score": 88.0
                }
            ]
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 쿼리 파라미터 추출
        chapter_id = request.args.get('chapter_id', type=int)
        period = request.args.get('period', 'all')
        
        # 기간 설정
        if period == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:  # 'all'
            start_date = datetime.min
        
        from models.quiz_attempt import QuizAttempt
        from models.chapter import Chapter
        
        # 기본 쿼리 구성
        query = QuizAttempt.query.filter_by(user_id=user_id)
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        if period != 'all':
            query = query.filter(QuizAttempt.attempted_at >= start_date)
        
        quiz_attempts = query.all()
        
        # 전체 통계
        total_attempts = len(quiz_attempts)
        correct_attempts = len([q for q in quiz_attempts if q.is_correct])
        success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        average_score = sum([q.score for q in quiz_attempts]) / total_attempts if total_attempts > 0 else 0
        total_time_spent = sum([q.time_taken_seconds for q in quiz_attempts])
        
        overall_stats = {
            'total_attempts': total_attempts,
            'correct_attempts': correct_attempts,
            'success_rate': round(success_rate, 2),
            'average_score': round(average_score, 2),
            'total_time_spent_seconds': total_time_spent,
            'average_time_per_attempt': round(total_time_spent / total_attempts, 2) if total_attempts > 0 else 0
        }
        
        # 챕터별 통계
        chapter_stats = []
        if not chapter_id:  # 전체 챕터 통계
            chapters_with_attempts = {}
            for attempt in quiz_attempts:
                if attempt.chapter_id not in chapters_with_attempts:
                    chapters_with_attempts[attempt.chapter_id] = []
                chapters_with_attempts[attempt.chapter_id].append(attempt)
            
            for chap_id, attempts in chapters_with_attempts.items():
                chapter = Chapter.get_by_id(chap_id)
                if chapter:
                    chap_correct = len([a for a in attempts if a.is_correct])
                    chap_success_rate = (chap_correct / len(attempts) * 100)
                    chap_avg_score = sum([a.score for a in attempts]) / len(attempts)
                    chap_best_score = max([a.score for a in attempts])
                    latest_attempt = max([a.attempted_at for a in attempts])
                    
                    chapter_stats.append({
                        'chapter_id': chap_id,
                        'chapter_title': chapter.title,
                        'chapter_number': chapter.chapter_number,
                        'attempts': len(attempts),
                        'correct': chap_correct,
                        'success_rate': round(chap_success_rate, 2),
                        'average_score': round(chap_avg_score, 2),
                        'best_score': round(chap_best_score, 2),
                        'latest_attempt': latest_attempt.isoformat()
                    })
        
        # 성과 트렌드 (일별)
        performance_trend = StatsService.get_quiz_performance_trend(user_id, start_date, chapter_id)
        
        return jsonify(create_response(
            success=True,
            message="퀴즈 통계를 조회했습니다.",
            data={
                'period': period,
                'chapter_filter': chapter_id,
                'overall_stats': overall_stats,
                'chapter_stats': chapter_stats,
                'performance_trend': performance_trend
            }
        )), 200
        
    except Exception as e:
        logger.error(f"퀴즈 통계 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@stats_bp.route('/activity', methods=['GET'])
@token_required
def get_activity_stats():
    """
    활동 통계 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        period (optional): 조회 기간 (7d, 30d, 90d) - 기본값: 30d
    
    Response:
    {
        "success": true,
        "message": "활동 통계를 조회했습니다.",
        "data": {
            "period": "30d",
            "activity_summary": {
                "total_sessions": 15,
                "total_time_minutes": 450,
                "average_session_time": 30,
                "most_active_day": "Monday",
                "most_active_hour": 14
            },
            "daily_activity": [
                {
                    "date": "2024-01-01",
                    "sessions": 2,
                    "time_minutes": 60,
                    "chapters_accessed": 2
                }
            ],
            "hourly_distribution": [
                {
                    "hour": 9,
                    "sessions": 3,
                    "average_duration": 25
                }
            ]
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 쿼리 파라미터 추출
        period = request.args.get('period', '30d')
        
        # 기간 설정
        if period == '7d':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == '30d':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == '90d':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)  # 기본값
        
        from models.learning_loop import LearningLoop
        
        # 기간 내 학습 루프 조회
        learning_loops = LearningLoop.query.filter(
            and_(
                LearningLoop.user_id == user_id,
                LearningLoop.started_at >= start_date
            )
        ).all()
        
        # 활동 요약 통계
        total_sessions = len(learning_loops)
        total_time_minutes = 0
        
        for loop in learning_loops:
            if loop.completed_at and loop.started_at:
                duration = loop.completed_at - loop.started_at
                total_time_minutes += int(duration.total_seconds() / 60)
        
        average_session_time = total_time_minutes / total_sessions if total_sessions > 0 else 0
        
        # 가장 활발한 요일과 시간대
        most_active_day = StatsService.get_most_active_day(learning_loops)
        most_active_hour = StatsService.get_most_active_hour(learning_loops)
        
        # 일별 활동
        daily_activity = StatsService.get_daily_activity(learning_loops)
        
        # 시간대별 분포
        hourly_distribution = StatsService.get_hourly_distribution(learning_loops)
        
        activity_summary = {
            'total_sessions': total_sessions,
            'total_time_minutes': total_time_minutes,
            'average_session_time': round(average_session_time, 1),
            'most_active_day': most_active_day,
            'most_active_hour': most_active_hour
        }
        
        return jsonify(create_response(
            success=True,
            message="활동 통계를 조회했습니다.",
            data={
                'period': period,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat()
                },
                'activity_summary': activity_summary,
                'daily_activity': daily_activity,
                'hourly_distribution': hourly_distribution
            }
        )), 200
        
    except Exception as e:
        logger.error(f"활동 통계 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


class StatsService:
    """통계 계산을 위한 헬퍼 클래스"""
    
    @staticmethod
    def calculate_current_streak(user_id: int) -> int:
        """현재 학습 연속일 계산"""
        # 간단한 구현 - 실제로는 더 복잡한 로직 필요
        from models.learning_loop import LearningLoop
        
        today = datetime.utcnow().date()
        current_streak = 0
        
        for i in range(30):  # 최대 30일까지 확인
            check_date = today - timedelta(days=i)
            
            # 해당 날짜에 학습 활동이 있는지 확인
            has_activity = LearningLoop.query.filter(
                and_(
                    LearningLoop.user_id == user_id,
                    func.date(LearningLoop.started_at) == check_date
                )
            ).first() is not None
            
            if has_activity:
                current_streak += 1
            else:
                break
        
        return current_streak
    
    @staticmethod
    def calculate_longest_streak(user_id: int) -> int:
        """최장 학습 연속일 계산"""
        # 간단한 구현 - 실제로는 더 정교한 알고리즘 필요
        return 7  # 임시값
    
    @staticmethod
    def get_daily_progress(user_id: int, start_date: datetime) -> list:
        """일별 진도 통계"""
        # 간단한 구현
        return []
    
    @staticmethod
    def get_most_productive_day(user_id: int, start_date: datetime) -> str:
        """가장 생산적인 요일"""
        return "Monday"  # 임시값
    
    @staticmethod
    def get_quiz_performance_trend(user_id: int, start_date: datetime, chapter_id: int = None) -> list:
        """퀴즈 성과 트렌드"""
        return []  # 임시값
    
    @staticmethod
    def get_most_active_day(learning_loops: list) -> str:
        """가장 활발한 요일"""
        if not learning_loops:
            return "Monday"
        
        day_counts = {}
        for loop in learning_loops:
            day_name = loop.started_at.strftime('%A')
            day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        return max(day_counts, key=day_counts.get) if day_counts else "Monday"
    
    @staticmethod
    def get_most_active_hour(learning_loops: list) -> int:
        """가장 활발한 시간대"""
        if not learning_loops:
            return 14
        
        hour_counts = {}
        for loop in learning_loops:
            hour = loop.started_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return max(hour_counts, key=hour_counts.get) if hour_counts else 14
    
    @staticmethod
    def get_daily_activity(learning_loops: list) -> list:
        """일별 활동 통계"""
        daily_stats = {}
        
        for loop in learning_loops:
            date_str = loop.started_at.strftime('%Y-%m-%d')
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    'date': date_str,
                    'sessions': 0,
                    'time_minutes': 0,
                    'chapters_accessed': set()
                }
            
            daily_stats[date_str]['sessions'] += 1
            daily_stats[date_str]['chapters_accessed'].add(loop.chapter_id)
            
            if loop.completed_at and loop.started_at:
                duration = loop.completed_at - loop.started_at
                daily_stats[date_str]['time_minutes'] += int(duration.total_seconds() / 60)
        
        # set을 길이로 변환
        result = []
        for date_str, stats in sorted(daily_stats.items()):
            result.append({
                'date': stats['date'],
                'sessions': stats['sessions'],
                'time_minutes': stats['time_minutes'],
                'chapters_accessed': len(stats['chapters_accessed'])
            })
        
        return result
    
    @staticmethod
    def get_hourly_distribution(learning_loops: list) -> list:
        """시간대별 분포"""
        hourly_stats = {}
        
        for loop in learning_loops:
            hour = loop.started_at.hour
            if hour not in hourly_stats:
                hourly_stats[hour] = {
                    'sessions': 0,
                    'total_duration': 0
                }
            
            hourly_stats[hour]['sessions'] += 1
            
            if loop.completed_at and loop.started_at:
                duration = loop.completed_at - loop.started_at
                hourly_stats[hour]['total_duration'] += int(duration.total_seconds() / 60)
        
        result = []
        for hour in range(24):
            if hour in hourly_stats:
                stats = hourly_stats[hour]
                avg_duration = stats['total_duration'] / stats['sessions'] if stats['sessions'] > 0 else 0
                result.append({
                    'hour': hour,
                    'sessions': stats['sessions'],
                    'average_duration': round(avg_duration, 1)
                })
            else:
                result.append({
                    'hour': hour,
                    'sessions': 0,
                    'average_duration': 0
                })
        
        return result