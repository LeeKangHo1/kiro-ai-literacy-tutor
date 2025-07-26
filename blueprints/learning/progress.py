# blueprints/learning/progress.py
# 학습 진도 관리 API

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
from utils.auth_middleware import require_auth
from utils.response_utils import success_response, error_response
from utils.validation_utils import validate_required_fields
from services.progress_service import ProgressService
from services.loop_service import LoopService

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__)
progress_service = ProgressService()
loop_service = LoopService()

@progress_bp.route('/chapter/<int:chapter_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_chapter_progress(current_user, chapter_id):
    """챕터별 학습 진도 조회"""
    try:
        user_id = current_user['user_id']
        
        # 챕터 진도 계산
        progress_data = progress_service.calculate_chapter_progress(user_id, chapter_id)
        
        if not progress_data:
            return error_response("진도 정보를 조회할 수 없습니다.", 404)
        
        return success_response(progress_data, "챕터 진도 조회 성공")
        
    except Exception as e:
        logger.error(f"챕터 진도 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/overall', methods=['GET'])
@cross_origin()
@require_auth
def get_overall_progress(current_user):
    """전체 학습 진도 조회"""
    try:
        user_id = current_user['user_id']
        
        # 전체 진도 조회
        overall_data = progress_service.get_user_overall_progress(user_id)
        
        if not overall_data:
            return error_response("전체 진도 정보를 조회할 수 없습니다.", 404)
        
        return success_response(overall_data, "전체 진도 조회 성공")
        
    except Exception as e:
        logger.error(f"전체 진도 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/statistics', methods=['GET'])
@cross_origin()
@require_auth
def get_learning_statistics(current_user):
    """학습 통계 조회"""
    try:
        user_id = current_user['user_id']
        
        # 쿼리 파라미터 처리
        chapter_id = request.args.get('chapter_id', type=int)
        days = request.args.get('days', default=30, type=int)
        
        # 유효성 검사
        if days < 1 or days > 365:
            return error_response("조회 기간은 1일에서 365일 사이여야 합니다.", 400)
        
        # 학습 통계 생성
        statistics = progress_service.get_learning_statistics(
            user_id=user_id,
            chapter_id=chapter_id,
            days=days
        )
        
        if not statistics:
            return error_response("통계 정보를 생성할 수 없습니다.", 404)
        
        return success_response(statistics, "학습 통계 조회 성공")
        
    except Exception as e:
        logger.error(f"학습 통계 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/update', methods=['POST'])
@cross_origin()
@require_auth
def update_progress(current_user):
    """학습 진도 수동 업데이트"""
    try:
        user_id = current_user['user_id']
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['chapter_id']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        chapter_id = data['chapter_id']
        progress_increment = data.get('progress_increment')
        understanding_score = data.get('understanding_score')
        study_time_minutes = data.get('study_time_minutes')
        
        # 유효성 검사
        if progress_increment is not None and (progress_increment < 0 or progress_increment > 100):
            return error_response("진도 증가량은 0-100 사이여야 합니다.", 400)
        
        if understanding_score is not None and (understanding_score < 0 or understanding_score > 100):
            return error_response("이해도 점수는 0-100 사이여야 합니다.", 400)
        
        if study_time_minutes is not None and study_time_minutes < 0:
            return error_response("학습 시간은 0 이상이어야 합니다.", 400)
        
        # 진도 업데이트
        updated_progress = progress_service.update_chapter_progress(
            user_id=user_id,
            chapter_id=chapter_id,
            progress_increment=progress_increment,
            understanding_score=understanding_score,
            study_time_minutes=study_time_minutes
        )
        
        # 업데이트된 진도 정보 반환
        progress_data = progress_service.calculate_chapter_progress(user_id, chapter_id)
        
        return success_response(progress_data, "진도 업데이트 성공")
        
    except Exception as e:
        logger.error(f"진도 업데이트 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/understanding-score/<int:chapter_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_understanding_score(current_user, chapter_id):
    """이해도 점수 조회"""
    try:
        user_id = current_user['user_id']
        
        # 이해도 점수 계산
        understanding_score = progress_service.calculate_understanding_score(user_id, chapter_id)
        
        # 상세 분석 정보도 함께 제공
        progress_data = progress_service.calculate_chapter_progress(user_id, chapter_id)
        
        result = {
            'understanding_score': understanding_score,
            'quiz_success_rate': progress_data.get('quiz_success_rate', 0),
            'skill_areas': progress_data.get('skill_areas', {}),
            'recommendations': progress_data.get('next_recommendations', [])
        }
        
        return success_response(result, "이해도 점수 조회 성공")
        
    except Exception as e:
        logger.error(f"이해도 점수 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/loops/<int:chapter_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_chapter_loops(current_user, chapter_id):
    """챕터별 루프 기록 조회"""
    try:
        user_id = current_user['user_id']
        
        # 쿼리 파라미터 처리
        limit = request.args.get('limit', default=10, type=int)
        status = request.args.get('status')  # 'completed', 'active', 'abandoned'
        
        # 유효성 검사
        if limit < 1 or limit > 100:
            return error_response("조회 개수는 1-100 사이여야 합니다.", 400)
        
        valid_statuses = ['completed', 'active', 'abandoned']
        if status and status not in valid_statuses:
            return error_response(f"상태는 {', '.join(valid_statuses)} 중 하나여야 합니다.", 400)
        
        # 루프 기록 조회
        from models.learning_loop import LearningLoop
        loops = LearningLoop.get_user_loops(
            user_id=user_id,
            chapter_id=chapter_id,
            status=status,
            limit=limit
        )
        
        # 루프 정보 변환
        loop_data = []
        for loop in loops:
            metrics = loop.get_performance_metrics()
            loop_info = {
                'loop_id': loop.loop_id,
                'loop_sequence': loop.loop_sequence,
                'loop_status': loop.loop_status,
                'loop_type': loop.loop_type,
                'started_at': loop.started_at.isoformat() if loop.started_at else None,
                'completed_at': loop.completed_at.isoformat() if loop.completed_at else None,
                'duration_minutes': loop.duration_minutes,
                'interaction_count': loop.interaction_count,
                'loop_summary': loop.loop_summary,
                'performance_metrics': metrics
            }
            loop_data.append(loop_info)
        
        result = {
            'chapter_id': chapter_id,
            'total_loops': len(loop_data),
            'loops': loop_data
        }
        
        return success_response(result, "루프 기록 조회 성공")
        
    except Exception as e:
        logger.error(f"루프 기록 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/loop/<string:loop_id>/conversations', methods=['GET'])
@cross_origin()
@require_auth
def get_loop_conversations(current_user, loop_id):
    """특정 루프의 대화 기록 조회"""
    try:
        user_id = current_user['user_id']
        
        # 루프 소유권 확인
        from models.learning_loop import LearningLoop
        loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
        
        if not loop:
            return error_response("루프를 찾을 수 없습니다.", 404)
        
        if loop.user_id != user_id:
            return error_response("접근 권한이 없습니다.", 403)
        
        # 대화 기록 조회
        conversations = loop.get_conversations()
        
        # 대화 정보 변환
        conversation_data = []
        for conv in conversations:
            conv_info = {
                'conversation_id': conv.conversation_id,
                'agent_name': conv.agent_name,
                'message_type': conv.message_type,
                'user_message': conv.user_message,
                'system_response': conv.system_response,
                'ui_elements': conv.ui_elements,
                'ui_mode': conv.ui_mode,
                'timestamp': conv.timestamp.isoformat(),
                'sequence_order': conv.sequence_order,
                'processing_time_ms': conv.processing_time_ms
            }
            conversation_data.append(conv_info)
        
        # 대화 통계
        from models.conversation import Conversation
        stats = Conversation.get_conversation_stats(loop_id)
        
        result = {
            'loop_id': loop_id,
            'loop_info': {
                'loop_status': loop.loop_status,
                'started_at': loop.started_at.isoformat() if loop.started_at else None,
                'completed_at': loop.completed_at.isoformat() if loop.completed_at else None,
                'duration_minutes': loop.duration_minutes
            },
            'conversation_stats': stats,
            'conversations': conversation_data
        }
        
        return success_response(result, "대화 기록 조회 성공")
        
    except Exception as e:
        logger.error(f"대화 기록 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/recommendations/<int:chapter_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_progress_recommendations(current_user, chapter_id):
    """진도 기반 추천사항 조회"""
    try:
        user_id = current_user['user_id']
        
        # 진도 분석 및 추천사항 생성
        progress_data = progress_service.calculate_chapter_progress(user_id, chapter_id)
        
        if not progress_data:
            return error_response("진도 정보를 조회할 수 없습니다.", 404)
        
        recommendations = progress_data.get('next_recommendations', [])
        
        # 추가 분석 정보
        analysis = {
            'current_progress': progress_data.get('progress_percentage', 0),
            'understanding_score': progress_data.get('understanding_score', 0),
            'learning_efficiency': progress_data.get('learning_efficiency', 0),
            'consistency_score': progress_data.get('learning_consistency', 0),
            'recommendations': recommendations,
            'skill_areas': progress_data.get('skill_areas', {}),
            'learning_patterns': progress_data.get('learning_patterns', {})
        }
        
        return success_response(analysis, "추천사항 조회 성공")
        
    except Exception as e:
        logger.error(f"추천사항 조회 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)

@progress_bp.route('/export', methods=['GET'])
@cross_origin()
@require_auth
def export_learning_data(current_user):
    """학습 데이터 내보내기"""
    try:
        user_id = current_user['user_id']
        
        # 쿼리 파라미터 처리
        format_type = request.args.get('format', default='json')  # json, csv
        chapter_id = request.args.get('chapter_id', type=int)
        days = request.args.get('days', default=30, type=int)
        
        if format_type not in ['json', 'csv']:
            return error_response("지원하지 않는 형식입니다. (json, csv만 지원)", 400)
        
        # 전체 진도 데이터
        overall_progress = progress_service.get_user_overall_progress(user_id)
        
        # 학습 통계
        statistics = progress_service.get_learning_statistics(
            user_id=user_id,
            chapter_id=chapter_id,
            days=days
        )
        
        # 내보낼 데이터 구성
        export_data = {
            'export_info': {
                'user_id': user_id,
                'exported_at': datetime.utcnow().isoformat(),
                'period_days': days,
                'chapter_filter': chapter_id
            },
            'overall_progress': overall_progress,
            'statistics': statistics
        }
        
        if format_type == 'json':
            return success_response(export_data, "학습 데이터 내보내기 성공")
        else:
            # CSV 형식은 추후 구현 (현재는 JSON만 지원)
            return error_response("CSV 형식은 아직 지원하지 않습니다.", 501)
        
    except Exception as e:
        logger.error(f"학습 데이터 내보내기 중 오류: {str(e)}")
        return error_response("서버 오류가 발생했습니다.", 500)