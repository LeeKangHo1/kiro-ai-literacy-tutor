# blueprints/learning/chat.py
# 메시지 처리 API 엔드포인트

from flask import request, jsonify, g, Blueprint
from services.learning_service import LearningService
from utils.response_utils import create_response
from utils.jwt_utils import token_required
import logging

logger = logging.getLogger(__name__)

# 채팅 관련 블루프린트 생성
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
@token_required
def process_message():
    """
    채팅 메시지 처리 API (LangGraph 워크플로우 실행)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "message": "AI에 대해 설명해주세요",
        "context": {
            "current_chapter": 1,
            "loop_id": "uuid-string",
            "stage": "theory"
        }
    }
    
    Response:
    {
        "success": true,
        "message": "메시지가 처리되었습니다.",
        "data": {
            "response": "AI는 인공지능의 줄임말로...",
            "ui_mode": "chat",
            "ui_elements": null,
            "current_stage": "theory",
            "loop_id": "uuid-string"
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # Content-Type 확인
        if not request.is_json:
            return jsonify(create_response(
                success=False,
                message="Content-Type은 application/json이어야 합니다.",
                error_code="INVALID_CONTENT_TYPE"
            )), 400
        
        # 요청 데이터 추출
        data = request.get_json()
        if not data:
            return jsonify(create_response(
                success=False,
                message="요청 데이터가 없습니다.",
                error_code="NO_DATA"
            )), 400
        
        # 필수 필드 확인
        message = data.get('message', '').strip()
        if not message:
            return jsonify(create_response(
                success=False,
                message="메시지를 입력해주세요.",
                error_code="MISSING_MESSAGE"
            )), 400
        
        # 컨텍스트 정보 추출
        context = data.get('context', {})
        
        # 메시지 처리
        result = LearningService.process_chat_message(user_id, message, context)
        
        status_code = 200 if result['success'] else 500
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code == 'USER_NOT_FOUND':
                status_code = 404
            elif error_code == 'MISSING_MESSAGE':
                status_code = 400
            else:
                status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"메시지 처리 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chat_bp.route('/conversation/<string:loop_id>', methods=['GET'])
@token_required
def get_conversation_history(loop_id):
    """
    대화 기록 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "대화 기록을 조회했습니다.",
        "data": {
            "loop_id": "uuid-string",
            "conversations": [
                {
                    "conversation_id": 1,
                    "agent_name": "TheoryEducator",
                    "message_type": "system",
                    "user_message": null,
                    "system_response": "AI는 인공지능의 줄임말로...",
                    "timestamp": "2024-01-01T00:00:00",
                    "sequence_order": 1
                }
            ],
            "total_messages": 10
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.conversation import Conversation
        from models.learning_loop import LearningLoop
        
        # 학습 루프 확인 및 권한 검증
        learning_loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
        if not learning_loop:
            return jsonify(create_response(
                success=False,
                message="학습 루프를 찾을 수 없습니다.",
                error_code="LOOP_NOT_FOUND"
            )), 404
        
        if learning_loop.user_id != user_id:
            return jsonify(create_response(
                success=False,
                message="해당 대화 기록에 접근할 권한이 없습니다.",
                error_code="ACCESS_DENIED"
            )), 403
        
        # 대화 기록 조회
        conversations = Conversation.query.filter_by(
            loop_id=loop_id
        ).order_by(Conversation.sequence_order).all()
        
        conversations_data = []
        for conv in conversations:
            conversations_data.append({
                'conversation_id': conv.conversation_id,
                'agent_name': conv.agent_name,
                'message_type': conv.message_type,
                'user_message': conv.user_message,
                'system_response': conv.system_response,
                'ui_elements': conv.ui_elements,
                'timestamp': conv.timestamp.isoformat(),
                'sequence_order': conv.sequence_order
            })
        
        return jsonify(create_response(
            success=True,
            message="대화 기록을 조회했습니다.",
            data={
                'loop_id': loop_id,
                'loop_info': {
                    'chapter_id': learning_loop.chapter_id,
                    'loop_sequence': learning_loop.loop_sequence,
                    'loop_status': learning_loop.loop_status,
                    'started_at': learning_loop.started_at.isoformat(),
                    'completed_at': learning_loop.completed_at.isoformat() if learning_loop.completed_at else None
                },
                'conversations': conversations_data,
                'total_messages': len(conversations_data)
            }
        )), 200
        
    except Exception as e:
        logger.error(f"대화 기록 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chat_bp.route('/loops', methods=['GET'])
@token_required
def get_learning_loops():
    """
    사용자의 학습 루프 목록 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        chapter_id (optional): 특정 챕터의 루프만 조회
        status (optional): 특정 상태의 루프만 조회 (active, completed, abandoned)
        limit (optional): 조회할 루프 수 제한 (기본값: 20)
        offset (optional): 조회 시작 위치 (기본값: 0)
    
    Response:
    {
        "success": true,
        "message": "학습 루프 목록을 조회했습니다.",
        "data": {
            "loops": [
                {
                    "loop_id": "uuid-string",
                    "chapter_id": 1,
                    "chapter_title": "AI는 무엇인가?",
                    "loop_sequence": 1,
                    "loop_status": "completed",
                    "loop_summary": "AI의 기본 개념을 학습했습니다.",
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": "2024-01-01T01:00:00",
                    "conversation_count": 15
                }
            ],
            "total_loops": 5,
            "pagination": {
                "limit": 20,
                "offset": 0,
                "has_more": false
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 쿼리 파라미터 추출
        chapter_id = request.args.get('chapter_id', type=int)
        status = request.args.get('status')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # 제한값 검증
        limit = min(max(1, limit), 100)  # 1-100 사이로 제한
        offset = max(0, offset)
        
        from models.learning_loop import LearningLoop
        from models.chapter import Chapter
        
        # 기본 쿼리 구성
        query = LearningLoop.query.filter_by(user_id=user_id)
        
        # 필터 적용
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        if status and status in ['active', 'completed', 'abandoned']:
            query = query.filter_by(loop_status=status)
        
        # 전체 개수 조회
        total_loops = query.count()
        
        # 페이지네이션 적용 및 정렬
        loops = query.order_by(
            LearningLoop.started_at.desc()
        ).offset(offset).limit(limit).all()
        
        # 응답 데이터 구성
        loops_data = []
        for loop in loops:
            # 챕터 정보 조회
            chapter = Chapter.get_by_id(loop.chapter_id)
            
            # 대화 수 조회
            from models.conversation import Conversation
            conversation_count = Conversation.query.filter_by(loop_id=loop.loop_id).count()
            
            loops_data.append({
                'loop_id': loop.loop_id,
                'chapter_id': loop.chapter_id,
                'chapter_title': chapter.title if chapter else '알 수 없는 챕터',
                'loop_sequence': loop.loop_sequence,
                'loop_status': loop.loop_status,
                'loop_summary': loop.loop_summary,
                'started_at': loop.started_at.isoformat(),
                'completed_at': loop.completed_at.isoformat() if loop.completed_at else None,
                'conversation_count': conversation_count
            })
        
        return jsonify(create_response(
            success=True,
            message="학습 루프 목록을 조회했습니다.",
            data={
                'loops': loops_data,
                'total_loops': total_loops,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_loops
                },
                'filters': {
                    'chapter_id': chapter_id,
                    'status': status
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"학습 루프 목록 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@chat_bp.route('/loop/<string:loop_id>/summary', methods=['GET'])
@token_required
def get_loop_summary(loop_id):
    """
    특정 학습 루프 요약 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "학습 루프 요약을 조회했습니다.",
        "data": {
            "loop_id": "uuid-string",
            "loop_summary": "AI의 기본 개념을 학습했습니다...",
            "chapter_info": {
                "chapter_id": 1,
                "title": "AI는 무엇인가?"
            },
            "statistics": {
                "total_messages": 15,
                "duration_minutes": 45,
                "agents_involved": ["TheoryEducator", "QnAResolver"]
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.learning_loop import LearningLoop
        from models.chapter import Chapter
        from models.conversation import Conversation
        
        # 학습 루프 조회 및 권한 확인
        learning_loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
        if not learning_loop:
            return jsonify(create_response(
                success=False,
                message="학습 루프를 찾을 수 없습니다.",
                error_code="LOOP_NOT_FOUND"
            )), 404
        
        if learning_loop.user_id != user_id:
            return jsonify(create_response(
                success=False,
                message="해당 학습 루프에 접근할 권한이 없습니다.",
                error_code="ACCESS_DENIED"
            )), 403
        
        # 챕터 정보 조회
        chapter = Chapter.get_by_id(learning_loop.chapter_id)
        
        # 대화 통계 계산
        conversations = Conversation.query.filter_by(loop_id=loop_id).all()
        
        # 소요 시간 계산
        duration_minutes = 0
        if learning_loop.completed_at and learning_loop.started_at:
            duration = learning_loop.completed_at - learning_loop.started_at
            duration_minutes = int(duration.total_seconds() / 60)
        
        # 참여한 에이전트 목록
        agents_involved = list(set([conv.agent_name for conv in conversations if conv.agent_name]))
        
        return jsonify(create_response(
            success=True,
            message="학습 루프 요약을 조회했습니다.",
            data={
                'loop_id': loop_id,
                'loop_summary': learning_loop.loop_summary or "요약이 생성되지 않았습니다.",
                'loop_status': learning_loop.loop_status,
                'chapter_info': {
                    'chapter_id': learning_loop.chapter_id,
                    'title': chapter.title if chapter else '알 수 없는 챕터'
                },
                'time_info': {
                    'started_at': learning_loop.started_at.isoformat(),
                    'completed_at': learning_loop.completed_at.isoformat() if learning_loop.completed_at else None,
                    'duration_minutes': duration_minutes
                },
                'statistics': {
                    'total_messages': len(conversations),
                    'agents_involved': agents_involved,
                    'loop_sequence': learning_loop.loop_sequence
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"학습 루프 요약 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500