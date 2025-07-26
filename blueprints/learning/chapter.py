# blueprints/learning/chapter.py
# 챕터 관리 API 엔드포인트

from flask import request, jsonify, g, Blueprint
from services.learning_service import LearningService
from utils.response_utils import create_response
from utils.jwt_utils import token_required
import logging

logger = logging.getLogger(__name__)

# 챕터 관련 블루프린트 생성
chapter_bp = Blueprint('chapter', __name__)

@chapter_bp.route('/list', methods=['GET'])
@token_required
def get_chapters():
    """
    사용자가 학습 가능한 챕터 목록 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        difficulty (optional): 난이도 필터 (low, medium, high)
        status (optional): 진행 상태 필터 (not_started, in_progress, completed)
    
    Response:
    {
        "success": true,
        "message": "학습 가능한 챕터 목록을 조회했습니다.",
        "data": {
            "chapters": [
                {
                    "chapter_id": 1,
                    "chapter_number": 1,
                    "title": "AI는 무엇인가?",
                    "description": "AI의 기본 개념과 정의를 학습합니다.",
                    "difficulty_level": "low",
                    "estimated_duration": 30,
                    "prerequisites": [],
                    "learning_objectives": {...},
                    "user_progress": {
                        "completion_status": "not_started",
                        "progress_percentage": 0.0,
                        "understanding_score": 0.0,
                        "last_accessed_at": null
                    }
                }
            ],
            "total_available": 5,
            "user_level": "medium",
            "user_type": "business"
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 쿼리 파라미터 추출
        difficulty_filter = request.args.get('difficulty')
        status_filter = request.args.get('status')
        
        # 챕터 목록 조회
        result = LearningService.get_available_chapters(user_id)
        
        if result['success'] and (difficulty_filter or status_filter):
            # 필터 적용
            chapters = result['data']['chapters']
            filtered_chapters = []
            
            for chapter in chapters:
                # 난이도 필터
                if difficulty_filter and chapter['difficulty_level'] != difficulty_filter:
                    continue
                
                # 상태 필터
                if status_filter and chapter['user_progress']['completion_status'] != status_filter:
                    continue
                
                filtered_chapters.append(chapter)
            
            result['data']['chapters'] = filtered_chapters
            result['data']['total_available'] = len(filtered_chapters)
            result['data']['filters_applied'] = {
                'difficulty': difficulty_filter,
                'status': status_filter
            }
        
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"챕터 목록 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chapter_bp.route('/<int:chapter_id>', methods=['GET'])
@token_required
def get_chapter_detail(chapter_id):
    """
    특정 챕터의 상세 정보 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "챕터 상세 정보를 조회했습니다.",
        "data": {
            "chapter": {
                "chapter_id": 1,
                "chapter_number": 1,
                "title": "AI는 무엇인가?",
                "description": "AI의 기본 개념과 정의를 학습합니다.",
                "difficulty_level": "low",
                "estimated_duration": 30,
                "prerequisites": [],
                "learning_objectives": {...},
                "content_metadata": {...}
            },
            "user_progress": {
                "completion_status": "in_progress",
                "progress_percentage": 45.5,
                "understanding_score": 78.0,
                "total_study_time": 25,
                "quiz_attempts_count": 2,
                "average_quiz_score": 85.0,
                "started_at": "2024-01-01T00:00:00",
                "last_accessed_at": "2024-01-01T01:00:00"
            },
            "access_info": {
                "prerequisites_met": true,
                "can_start": true
            },
            "statistics": {
                "completion_stats": {...},
                "quiz_stats": {...}
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 챕터 상세 정보 조회
        result = LearningService.get_chapter_detail(user_id, chapter_id)
        
        status_code = 200 if result['success'] else 404
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code in ['USER_NOT_FOUND', 'CHAPTER_NOT_FOUND']:
                status_code = 404
            else:
                status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"챕터 상세 정보 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chapter_bp.route('/<int:chapter_id>/start', methods=['POST'])
@token_required
def start_chapter(chapter_id):
    """
    챕터 학습 시작 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "챕터 학습을 시작했습니다.",
        "data": {
            "chapter": {
                "chapter_id": 1,
                "title": "AI는 무엇인가?",
                "description": "AI의 기본 개념과 정의를 학습합니다."
            },
            "progress": {
                "completion_status": "in_progress",
                "progress_percentage": 0.0
            },
            "learning_loop": {
                "loop_id": "uuid-string",
                "started_at": "2024-01-01T00:00:00"
            },
            "next_action": {
                "type": "start_theory",
                "message": "AI는 무엇인가? 학습을 시작합니다. 개념 설명부터 시작하겠습니다."
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 챕터 학습 시작
        result = LearningService.start_chapter_learning(user_id, chapter_id)
        
        status_code = 200 if result['success'] else 400
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code in ['USER_NOT_FOUND', 'CHAPTER_NOT_FOUND']:
                status_code = 404
            elif error_code == 'PREREQUISITES_NOT_MET':
                status_code = 403
            else:
                status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"챕터 학습 시작 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chapter_bp.route('/<int:chapter_id>/progress', methods=['GET'])
@token_required
def get_chapter_progress(chapter_id):
    """
    특정 챕터의 학습 진도 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "챕터 학습 진도를 조회했습니다.",
        "data": {
            "chapter_id": 1,
            "chapter_title": "AI는 무엇인가?",
            "progress": {
                "completion_status": "in_progress",
                "progress_percentage": 65.5,
                "understanding_score": 82.0,
                "total_study_time": 45,
                "quiz_attempts_count": 3,
                "average_quiz_score": 88.5,
                "started_at": "2024-01-01T00:00:00",
                "last_accessed_at": "2024-01-01T02:00:00"
            },
            "recent_loops": [
                {
                    "loop_id": "uuid-string",
                    "loop_sequence": 2,
                    "loop_status": "completed",
                    "started_at": "2024-01-01T01:30:00",
                    "completed_at": "2024-01-01T02:00:00"
                }
            ]
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.user import UserLearningProgress
        from models.chapter import Chapter
        from models.learning_loop import LearningLoop
        
        # 챕터 확인
        chapter = Chapter.get_by_id(chapter_id)
        if not chapter:
            return jsonify(create_response(
                success=False,
                message="챕터를 찾을 수 없습니다.",
                error_code="CHAPTER_NOT_FOUND"
            )), 404
        
        # 사용자 진도 조회
        progress = UserLearningProgress.query.filter_by(
            user_id=user_id, 
            chapter_id=chapter_id
        ).first()
        
        if not progress:
            return jsonify(create_response(
                success=False,
                message="해당 챕터의 학습 진도가 없습니다.",
                error_code="PROGRESS_NOT_FOUND"
            )), 404
        
        # 최근 학습 루프 조회 (최대 5개)
        recent_loops = LearningLoop.query.filter_by(
            user_id=user_id,
            chapter_id=chapter_id
        ).order_by(LearningLoop.started_at.desc()).limit(5).all()
        
        recent_loops_data = []
        for loop in recent_loops:
            recent_loops_data.append({
                'loop_id': loop.loop_id,
                'loop_sequence': loop.loop_sequence,
                'loop_status': loop.loop_status,
                'started_at': loop.started_at.isoformat(),
                'completed_at': loop.completed_at.isoformat() if loop.completed_at else None,
                'loop_summary': loop.loop_summary
            })
        
        return jsonify(create_response(
            success=True,
            message="챕터 학습 진도를 조회했습니다.",
            data={
                'chapter_id': chapter.chapter_id,
                'chapter_title': chapter.title,
                'progress': {
                    'completion_status': progress.completion_status,
                    'progress_percentage': float(progress.progress_percentage),
                    'understanding_score': float(progress.understanding_score),
                    'total_study_time': progress.total_study_time,
                    'quiz_attempts_count': progress.quiz_attempts_count,
                    'average_quiz_score': float(progress.average_quiz_score),
                    'started_at': progress.started_at.isoformat() if progress.started_at else None,
                    'last_accessed_at': progress.last_accessed_at.isoformat() if progress.last_accessed_at else None
                },
                'recent_loops': recent_loops_data
            }
        )), 200
        
    except Exception as e:
        logger.error(f"챕터 진도 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chapter_bp.route('/<int:chapter_id>/complete', methods=['POST'])
@token_required
def complete_chapter(chapter_id):
    """
    챕터 완료 처리 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "final_understanding_score": 85.5,
        "completion_notes": "모든 개념을 잘 이해했습니다."
    }
    
    Response:
    {
        "success": true,
        "message": "챕터 학습이 완료되었습니다.",
        "data": {
            "chapter_id": 1,
            "completion_status": "completed",
            "final_score": 85.5,
            "completed_at": "2024-01-01T03:00:00",
            "next_available_chapters": [
                {
                    "chapter_id": 2,
                    "title": "AI의 역사와 발전"
                }
            ]
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 요청 데이터 추출
        data = request.get_json() if request.is_json else {}
        final_understanding_score = data.get('final_understanding_score')
        completion_notes = data.get('completion_notes', '')
        
        from models.user import UserLearningProgress
        from models.chapter import Chapter
        
        # 챕터 확인
        chapter = Chapter.get_by_id(chapter_id)
        if not chapter:
            return jsonify(create_response(
                success=False,
                message="챕터를 찾을 수 없습니다.",
                error_code="CHAPTER_NOT_FOUND"
            )), 404
        
        # 사용자 진도 조회
        progress = UserLearningProgress.query.filter_by(
            user_id=user_id, 
            chapter_id=chapter_id
        ).first()
        
        if not progress:
            return jsonify(create_response(
                success=False,
                message="해당 챕터의 학습 진도가 없습니다.",
                error_code="PROGRESS_NOT_FOUND"
            )), 404
        
        # 이미 완료된 챕터인지 확인
        if progress.completion_status == 'completed':
            return jsonify(create_response(
                success=False,
                message="이미 완료된 챕터입니다.",
                error_code="ALREADY_COMPLETED"
            )), 400
        
        # 챕터 완료 처리
        if final_understanding_score is not None:
            progress.understanding_score = min(100.0, max(0.0, final_understanding_score))
        
        progress.complete_learning()
        
        # 다음 학습 가능한 챕터 조회
        next_chapters = Chapter.get_available_chapters_for_user(user_id)
        next_chapters_data = []
        
        for next_chapter in next_chapters:
            if next_chapter.chapter_id != chapter_id:  # 현재 챕터 제외
                next_progress = next_chapter.get_user_progress(user_id)
                if not next_progress or next_progress.completion_status != 'completed':
                    next_chapters_data.append({
                        'chapter_id': next_chapter.chapter_id,
                        'chapter_number': next_chapter.chapter_number,
                        'title': next_chapter.title,
                        'difficulty_level': next_chapter.difficulty_level
                    })
        
        logger.info(f"챕터 완료 - user_id: {user_id}, chapter_id: {chapter_id}")
        
        return jsonify(create_response(
            success=True,
            message="챕터 학습이 완료되었습니다.",
            data={
                'chapter_id': chapter.chapter_id,
                'chapter_title': chapter.title,
                'completion_status': progress.completion_status,
                'final_score': float(progress.understanding_score),
                'progress_percentage': float(progress.progress_percentage),
                'total_study_time': progress.total_study_time,
                'completed_at': progress.completed_at.isoformat(),
                'completion_notes': completion_notes,
                'next_available_chapters': next_chapters_data
            }
        )), 200
        
    except Exception as e:
        logger.error(f"챕터 완료 처리 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chapter_bp.route('/statistics', methods=['GET'])
@token_required
def get_chapters_statistics():
    """
    전체 챕터 통계 조회 API (관리자용)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "챕터 통계를 조회했습니다.",
        "data": {
            "total_chapters": 5,
            "chapters_stats": [
                {
                    "chapter_id": 1,
                    "title": "AI는 무엇인가?",
                    "completion_stats": {...},
                    "quiz_stats": {...}
                }
            ]
        }
    }
    """
    try:
        from models.chapter import Chapter
        
        # 모든 활성 챕터 조회
        chapters = Chapter.get_active_chapters()
        
        chapters_stats = []
        for chapter in chapters:
            completion_stats = chapter.get_completion_stats()
            quiz_stats = chapter.get_quiz_stats()
            
            chapters_stats.append({
                'chapter_id': chapter.chapter_id,
                'chapter_number': chapter.chapter_number,
                'title': chapter.title,
                'difficulty_level': chapter.difficulty_level,
                'completion_stats': completion_stats,
                'quiz_stats': quiz_stats
            })
        
        return jsonify(create_response(
            success=True,
            message="챕터 통계를 조회했습니다.",
            data={
                'total_chapters': len(chapters),
                'chapters_stats': chapters_stats
            }
        )), 200
        
    except Exception as e:
        logger.error(f"챕터 통계 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500