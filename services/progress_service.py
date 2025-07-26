# services/progress_service.py
# 학습 진도 추적 및 기록 서비스

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy import func, and_, or_
from models.user import User, UserLearningProgress
from models.learning_loop import LearningLoop
from models.conversation import Conversation
from models.quiz_attempt import QuizAttempt
from models.chapter import Chapter
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class ProgressService:
    """학습 진도 추적 및 기록 서비스"""
    
    def __init__(self):
        self.db_service = DatabaseService()
    
    def calculate_chapter_progress(self, user_id: int, chapter_id: int) -> Dict[str, Any]:
        """챕터별 진도 계산"""
        try:
            # 사용자 학습 진도 조회
            progress = UserLearningProgress.get_or_create(user_id, chapter_id)
            
            # 루프 기반 진도 계산
            loops = LearningLoop.get_user_loops(
                user_id=user_id,
                chapter_id=chapter_id,
                status='completed'
            )
            
            # 기본 진도 정보
            base_progress = {
                'user_id': user_id,
                'chapter_id': chapter_id,
                'progress_percentage': progress.progress_percentage,
                'understanding_score': progress.understanding_score,
                'study_time_minutes': progress.study_time_minutes,
                'last_studied': progress.last_studied.isoformat() if progress.last_studied else None,
                'is_completed': progress.is_completed,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
            }
            
            # 상세 진도 분석
            detailed_analysis = self._analyze_detailed_progress(user_id, chapter_id, loops)
            
            # 진도 계산 결과 통합
            result = {
                **base_progress,
                **detailed_analysis,
                'loops_completed': len(loops),
                'total_interactions': sum(loop.interaction_count for loop in loops),
                'average_loop_duration': self._calculate_average_loop_duration(loops),
                'learning_consistency': self._calculate_learning_consistency(loops),
                'next_recommendations': self._generate_progress_recommendations(user_id, chapter_id)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"챕터 진도 계산 중 오류: {str(e)}")
            return {}
    
    def _analyze_detailed_progress(self, user_id: int, chapter_id: int, 
                                 loops: List[LearningLoop]) -> Dict[str, Any]:
        """상세 진도 분석"""
        if not loops:
            return {
                'theory_completion': 0,
                'quiz_completion': 0,
                'qna_engagement': 0,
                'skill_areas': {},
                'learning_patterns': {}
            }
        
        # 활동별 완료도 분석
        theory_count = 0
        quiz_count = 0
        qna_count = 0
        
        for loop in loops:
            conversations = loop.get_conversations()
            for conv in conversations:
                agent_name = conv.agent_name
                if agent_name == 'TheoryEducator':
                    theory_count += 1
                elif agent_name == 'QuizGenerator':
                    quiz_count += 1
                elif agent_name == 'QnAResolver':
                    qna_count += 1
        
        # 퀴즈 성과 분석
        quiz_attempts = QuizAttempt.query.join(LearningLoop).filter(
            LearningLoop.user_id == user_id,
            LearningLoop.chapter_id == chapter_id
        ).all()
        
        quiz_success_rate = 0
        if quiz_attempts:
            correct_attempts = len([q for q in quiz_attempts if q.is_correct])
            quiz_success_rate = (correct_attempts / len(quiz_attempts)) * 100
        
        # 스킬 영역별 분석
        skill_areas = self._analyze_skill_areas(quiz_attempts)
        
        # 학습 패턴 분석
        learning_patterns = self._analyze_learning_patterns(loops)
        
        return {
            'theory_completion': min(100, theory_count * 20),  # 이론 학습 완료도
            'quiz_completion': min(100, quiz_count * 25),      # 퀴즈 완료도
            'qna_engagement': min(100, qna_count * 15),        # 질문 참여도
            'quiz_success_rate': quiz_success_rate,
            'skill_areas': skill_areas,
            'learning_patterns': learning_patterns
        }
    
    def _analyze_skill_areas(self, quiz_attempts: List[QuizAttempt]) -> Dict[str, Any]:
        """스킬 영역별 분석"""
        if not quiz_attempts:
            return {}
        
        # 문제 유형별 성과 분석 (메타데이터에서 추출)
        skill_performance = {}
        
        for attempt in quiz_attempts:
            attempt_metadata = getattr(attempt, 'quiz_metadata', None) or {}
            question_type = attempt_metadata.get('question_type', 'general')
            skill_area = attempt_metadata.get('skill_area', 'general')
            
            if skill_area not in skill_performance:
                skill_performance[skill_area] = {
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'average_score': 0,
                    'improvement_trend': 0
                }
            
            skill_performance[skill_area]['total_attempts'] += 1
            if attempt.is_correct:
                skill_performance[skill_area]['correct_attempts'] += 1
            skill_performance[skill_area]['average_score'] += attempt.score
        
        # 평균 점수 계산
        for skill_area in skill_performance:
            total = skill_performance[skill_area]['total_attempts']
            if total > 0:
                skill_performance[skill_area]['average_score'] /= total
                skill_performance[skill_area]['success_rate'] = (
                    skill_performance[skill_area]['correct_attempts'] / total * 100
                )
        
        return skill_performance
    
    def _analyze_learning_patterns(self, loops: List[LearningLoop]) -> Dict[str, Any]:
        """학습 패턴 분석"""
        if not loops:
            return {}
        
        # 시간대별 학습 패턴
        hourly_activity = {}
        daily_activity = {}
        
        for loop in loops:
            if loop.started_at:
                hour = loop.started_at.hour
                day = loop.started_at.strftime('%A')
                
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                daily_activity[day] = daily_activity.get(day, 0) + 1
        
        # 학습 지속성 분석
        study_dates = [loop.started_at.date() for loop in loops if loop.started_at]
        study_dates.sort()
        
        consecutive_days = 0
        max_consecutive = 0
        
        if study_dates:
            current_streak = 1
            for i in range(1, len(study_dates)):
                if (study_dates[i] - study_dates[i-1]).days == 1:
                    current_streak += 1
                else:
                    max_consecutive = max(max_consecutive, current_streak)
                    current_streak = 1
            max_consecutive = max(max_consecutive, current_streak)
        
        # 학습 효율성 분석
        efficiency_score = self._calculate_learning_efficiency(loops)
        
        return {
            'preferred_study_hours': hourly_activity,
            'preferred_study_days': daily_activity,
            'max_consecutive_days': max_consecutive,
            'total_study_days': len(set(study_dates)),
            'learning_efficiency': efficiency_score,
            'average_session_length': self._calculate_average_loop_duration(loops)
        }
    
    def _calculate_learning_efficiency(self, loops: List[LearningLoop]) -> float:
        """학습 효율성 점수 계산 (0-100)"""
        if not loops:
            return 0.0
        
        total_score = 0
        factors = 0
        
        # 루프 완료율
        completed_loops = len([l for l in loops if l.loop_status == 'completed'])
        completion_rate = completed_loops / len(loops) * 100
        total_score += completion_rate
        factors += 1
        
        # 평균 상호작용 수 (적절한 범위: 5-15)
        avg_interactions = sum(l.interaction_count for l in loops) / len(loops)
        interaction_score = min(100, max(0, (avg_interactions - 5) / 10 * 100))
        total_score += interaction_score
        factors += 1
        
        # 평균 루프 지속 시간 (적절한 범위: 10-30분)
        avg_duration = sum(l.duration_minutes or 0 for l in loops) / len(loops)
        if 10 <= avg_duration <= 30:
            duration_score = 100
        elif avg_duration < 10:
            duration_score = avg_duration / 10 * 100
        else:
            duration_score = max(0, 100 - (avg_duration - 30) / 30 * 50)
        
        total_score += duration_score
        factors += 1
        
        return total_score / factors if factors > 0 else 0.0
    
    def _calculate_average_loop_duration(self, loops: List[LearningLoop]) -> float:
        """평균 루프 지속 시간 계산"""
        if not loops:
            return 0.0
        
        total_duration = sum(loop.duration_minutes or 0 for loop in loops)
        return total_duration / len(loops)
    
    def _calculate_learning_consistency(self, loops: List[LearningLoop]) -> float:
        """학습 일관성 점수 계산 (0-100)"""
        if len(loops) < 2:
            return 100.0
        
        # 루프 간격의 일관성 측정
        intervals = []
        sorted_loops = sorted(loops, key=lambda x: x.started_at or datetime.min)
        
        for i in range(1, len(sorted_loops)):
            if sorted_loops[i].started_at and sorted_loops[i-1].started_at:
                interval = (sorted_loops[i].started_at - sorted_loops[i-1].started_at).total_seconds() / 3600
                intervals.append(interval)
        
        if not intervals:
            return 100.0
        
        # 표준편차를 이용한 일관성 측정
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # 일관성 점수 (표준편차가 낮을수록 높은 점수)
        consistency_score = max(0, 100 - (std_dev / mean_interval * 100))
        return min(100, consistency_score)
    
    def _generate_progress_recommendations(self, user_id: int, chapter_id: int) -> List[str]:
        """진도 기반 추천사항 생성"""
        try:
            progress = UserLearningProgress.get_or_create(user_id, chapter_id)
            loops = LearningLoop.get_user_loops(user_id, chapter_id, limit=5)
            
            recommendations = []
            
            # 진도율 기반 추천
            if progress.progress_percentage < 30:
                recommendations.append("기본 개념 학습에 더 집중해보세요.")
            elif progress.progress_percentage < 70:
                recommendations.append("문제 풀이를 통해 이해도를 높여보세요.")
            elif progress.progress_percentage < 100:
                recommendations.append("마지막 단계입니다. 조금만 더 노력하세요!")
            
            # 이해도 점수 기반 추천
            if progress.understanding_score < 60:
                recommendations.append("기본 개념을 다시 한번 복습해보세요.")
            elif progress.understanding_score < 80:
                recommendations.append("실습 문제를 더 풀어보시는 것을 권장합니다.")
            
            # 최근 활동 기반 추천
            if loops:
                recent_loop = loops[0]
                if recent_loop.loop_status == 'abandoned':
                    recommendations.append("학습을 완료하지 못한 부분이 있습니다. 다시 도전해보세요.")
                
                # 루프 지속 시간 분석
                avg_duration = self._calculate_average_loop_duration(loops)
                if avg_duration < 5:
                    recommendations.append("학습 시간을 조금 더 늘려보세요.")
                elif avg_duration > 45:
                    recommendations.append("적절한 휴식을 취하며 학습하세요.")
            
            # 기본 추천사항
            if not recommendations:
                recommendations.append("현재 학습 진도가 양호합니다. 계속 진행해주세요.")
            
            return recommendations[:3]  # 최대 3개 추천사항
            
        except Exception as e:
            logger.error(f"추천사항 생성 중 오류: {str(e)}")
            return ["학습을 계속 진행해주세요."]
    
    def update_chapter_progress(self, user_id: int, chapter_id: int, 
                              progress_increment: float = None,
                              understanding_score: float = None,
                              study_time_minutes: int = None) -> UserLearningProgress:
        """챕터 진도 업데이트"""
        try:
            progress = UserLearningProgress.get_or_create(user_id, chapter_id)
            
            # 진도율 업데이트
            if progress_increment is not None:
                new_progress = min(100.0, progress.progress_percentage + progress_increment)
                progress.progress_percentage = new_progress
                
                # 100% 완료시 완료 처리
                if new_progress >= 100.0 and not progress.is_completed:
                    progress.is_completed = True
                    progress.completed_at = datetime.utcnow()
            
            # 이해도 점수 업데이트
            if understanding_score is not None:
                # 가중 평균으로 업데이트 (기존 70%, 새로운 30%)
                if progress.understanding_score > 0:
                    progress.understanding_score = (
                        progress.understanding_score * 0.7 + understanding_score * 0.3
                    )
                else:
                    progress.understanding_score = understanding_score
            
            # 학습 시간 업데이트
            if study_time_minutes is not None:
                progress.study_time_minutes += study_time_minutes
            
            # 마지막 학습 시간 업데이트
            progress.last_studied = datetime.utcnow()
            progress.save()
            
            logger.info(f"진도 업데이트: 사용자 {user_id}, 챕터 {chapter_id}, 진도 {progress.progress_percentage}%")
            return progress
            
        except Exception as e:
            logger.error(f"진도 업데이트 중 오류: {str(e)}")
            raise
    
    def calculate_understanding_score(self, user_id: int, chapter_id: int) -> float:
        """이해도 점수 산출"""
        try:
            # 퀴즈 결과 기반 이해도 계산
            quiz_attempts = QuizAttempt.query.join(LearningLoop).filter(
                LearningLoop.user_id == user_id,
                LearningLoop.chapter_id == chapter_id
            ).all()
            
            if not quiz_attempts:
                return 0.0
            
            # 최근 시도들에 더 높은 가중치 부여
            sorted_attempts = sorted(quiz_attempts, key=lambda x: x.attempted_at)
            total_weighted_score = 0
            total_weight = 0
            
            for i, attempt in enumerate(sorted_attempts):
                # 최근 시도일수록 높은 가중치 (1.0 ~ 2.0)
                weight = 1.0 + (i / len(sorted_attempts))
                total_weighted_score += attempt.score * weight
                total_weight += weight
            
            base_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # 힌트 사용 패널티 적용
            hint_penalty = 0
            for attempt in quiz_attempts:
                if attempt.hint_used:
                    hint_penalty += 5  # 힌트 사용시 5점 감점
            
            # 시도 횟수 보너스 (학습 노력 반영)
            attempt_bonus = min(10, len(quiz_attempts) * 2)  # 최대 10점 보너스
            
            final_score = max(0, min(100, base_score - hint_penalty + attempt_bonus))
            return round(final_score, 1)
            
        except Exception as e:
            logger.error(f"이해도 점수 계산 중 오류: {str(e)}")
            return 0.0
    
    def get_learning_statistics(self, user_id: int, chapter_id: int = None, 
                              days: int = 30) -> Dict[str, Any]:
        """학습 통계 생성"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 기본 쿼리
            query = LearningLoop.query.filter(
                LearningLoop.user_id == user_id,
                LearningLoop.started_at >= start_date
            )
            
            if chapter_id:
                query = query.filter(LearningLoop.chapter_id == chapter_id)
            
            loops = query.all()
            
            # 기본 통계
            total_loops = len(loops)
            completed_loops = len([l for l in loops if l.loop_status == 'completed'])
            total_study_time = sum(l.duration_minutes or 0 for l in loops)
            total_interactions = sum(l.interaction_count for l in loops)
            
            # 일별 활동
            daily_stats = {}
            for loop in loops:
                if loop.started_at:
                    date_key = loop.started_at.strftime('%Y-%m-%d')
                    if date_key not in daily_stats:
                        daily_stats[date_key] = {
                            'loops': 0,
                            'study_time': 0,
                            'interactions': 0
                        }
                    daily_stats[date_key]['loops'] += 1
                    daily_stats[date_key]['study_time'] += loop.duration_minutes or 0
                    daily_stats[date_key]['interactions'] += loop.interaction_count
            
            # 챕터별 통계
            chapter_stats = {}
            if not chapter_id:  # 전체 챕터 통계
                for loop in loops:
                    ch_id = loop.chapter_id
                    if ch_id not in chapter_stats:
                        chapter_stats[ch_id] = {
                            'loops': 0,
                            'completed_loops': 0,
                            'study_time': 0,
                            'progress': 0
                        }
                    chapter_stats[ch_id]['loops'] += 1
                    if loop.loop_status == 'completed':
                        chapter_stats[ch_id]['completed_loops'] += 1
                    chapter_stats[ch_id]['study_time'] += loop.duration_minutes or 0
                
                # 각 챕터의 진도 조회
                for ch_id in chapter_stats:
                    progress = UserLearningProgress.get_or_create(user_id, ch_id)
                    chapter_stats[ch_id]['progress'] = progress.progress_percentage
            
            return {
                'period_days': days,
                'total_loops': total_loops,
                'completed_loops': completed_loops,
                'completion_rate': (completed_loops / total_loops * 100) if total_loops > 0 else 0,
                'total_study_time_minutes': total_study_time,
                'total_interactions': total_interactions,
                'average_loop_duration': total_study_time / total_loops if total_loops > 0 else 0,
                'average_interactions_per_loop': total_interactions / total_loops if total_loops > 0 else 0,
                'daily_activity': daily_stats,
                'chapter_statistics': chapter_stats,
                'learning_efficiency': self._calculate_learning_efficiency(loops),
                'consistency_score': self._calculate_learning_consistency(loops)
            }
            
        except Exception as e:
            logger.error(f"학습 통계 생성 중 오류: {str(e)}")
            return {}
    
    def get_user_overall_progress(self, user_id: int) -> Dict[str, Any]:
        """사용자 전체 진도 조회"""
        try:
            # 모든 챕터의 진도 조회
            all_progress = UserLearningProgress.query.filter_by(user_id=user_id).all()
            
            # 전체 챕터 수 (Chapter 테이블에서 조회)
            total_chapters = Chapter.query.count()
            
            chapter_details = []
            total_progress = 0
            completed_chapters = 0
            total_study_time = 0
            
            for progress in all_progress:
                chapter_info = {
                    'chapter_id': progress.chapter_id,
                    'progress_percentage': progress.progress_percentage,
                    'understanding_score': progress.understanding_score,
                    'study_time_minutes': progress.study_time_minutes,
                    'is_completed': progress.is_completed,
                    'last_studied': progress.last_studied.isoformat() if progress.last_studied else None,
                    'completed_at': progress.completed_at.isoformat() if progress.completed_at else None
                }
                
                chapter_details.append(chapter_info)
                total_progress += progress.progress_percentage
                total_study_time += progress.study_time_minutes
                
                if progress.is_completed:
                    completed_chapters += 1
            
            # 전체 진도율 계산
            overall_progress = total_progress / total_chapters if total_chapters > 0 else 0
            
            # 평균 이해도 계산
            understanding_scores = [p.understanding_score for p in all_progress if p.understanding_score > 0]
            average_understanding = sum(understanding_scores) / len(understanding_scores) if understanding_scores else 0
            
            return {
                'user_id': user_id,
                'overall_progress_percentage': round(overall_progress, 1),
                'completed_chapters': completed_chapters,
                'total_chapters': total_chapters,
                'completion_rate': (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
                'total_study_time_minutes': total_study_time,
                'average_understanding_score': round(average_understanding, 1),
                'chapter_details': chapter_details,
                'last_activity': max([p.last_studied for p in all_progress if p.last_studied], default=None),
                'learning_streak': self._calculate_learning_streak(user_id)
            }
            
        except Exception as e:
            logger.error(f"전체 진도 조회 중 오류: {str(e)}")
            return {}
    
    def _calculate_learning_streak(self, user_id: int) -> int:
        """학습 연속일 계산"""
        try:
            # 최근 30일간의 학습 활동 조회
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=30)
            
            # 일별 학습 활동 조회
            daily_activity = LearningLoop.query.filter(
                LearningLoop.user_id == user_id,
                func.date(LearningLoop.started_at) >= start_date
            ).with_entities(
                func.date(LearningLoop.started_at).label('study_date')
            ).distinct().order_by(
                func.date(LearningLoop.started_at).desc()
            ).all()
            
            if not daily_activity:
                return 0
            
            # 연속 학습일 계산
            streak = 0
            current_date = end_date
            
            for activity in daily_activity:
                study_date = activity.study_date
                
                if study_date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif study_date == current_date - timedelta(days=1):
                    streak += 1
                    current_date = study_date - timedelta(days=1)
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"학습 연속일 계산 중 오류: {str(e)}")
            return 0