# blueprints/learning/diagnosis.py
# 진단 퀴즈 API 엔드포인트

from flask import request, jsonify, g, Blueprint
from services.learning_service import LearningService
from utils.response_utils import create_response
from utils.jwt_utils import token_required
import logging

logger = logging.getLogger(__name__)

# 진단 관련 블루프린트 생성
diagnosis_bp = Blueprint('diagnosis', __name__)

@diagnosis_bp.route('/quiz', methods=['GET'])
@token_required
def get_diagnosis_quiz():
    """
    사용자 진단 퀴즈 조회 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "진단 퀴즈를 조회했습니다.",
        "data": {
            "quiz_id": "diagnosis_1_1640995200",
            "title": "AI 활용 수준 진단",
            "description": "귀하의 AI 활용 수준을 파악하여 맞춤형 학습 과정을 제공합니다.",
            "questions": [...],
            "total_questions": 4,
            "estimated_time_minutes": 5
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        # 진단 퀴즈 조회
        result = LearningService.get_diagnosis_quiz(user_id)
        
        status_code = 200 if result['success'] else 404
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"진단 퀴즈 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@diagnosis_bp.route('/quiz/submit', methods=['POST'])
@token_required
def submit_diagnosis_quiz():
    """
    진단 퀴즈 제출 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
    {
        "quiz_id": "diagnosis_1_1640995200",
        "answers": [
            {
                "question_id": 1,
                "selected_option": 0
            },
            {
                "question_id": 2,
                "selected_option": 2
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "message": "진단이 완료되었습니다.",
        "data": {
            "diagnosis_result": {
                "score": 75,
                "user_level": "high",
                "user_type": "business",
                "level_description": "AI 고급자 - 고급 기능과 실무 활용에 집중하여 학습하시면 좋겠습니다.",
                "type_description": "실무자 과정 - 업무에서 바로 활용할 수 있는 실용적인 기술을 학습합니다."
            },
            "recommended_chapters": [...],
            "next_steps": {
                "action": "start_learning",
                "recommended_chapter": {...}
            }
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
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', [])
        
        if not quiz_id:
            return jsonify(create_response(
                success=False,
                message="퀴즈 ID가 필요합니다.",
                error_code="MISSING_QUIZ_ID"
            )), 400
        
        if not answers:
            return jsonify(create_response(
                success=False,
                message="퀴즈 답변이 필요합니다.",
                error_code="MISSING_ANSWERS"
            )), 400
        
        # 답변 형식 검증
        for answer in answers:
            if not isinstance(answer, dict) or 'question_id' not in answer or 'selected_option' not in answer:
                return jsonify(create_response(
                    success=False,
                    message="답변 형식이 올바르지 않습니다.",
                    error_code="INVALID_ANSWER_FORMAT"
                )), 400
        
        # 진단 퀴즈 제출 처리
        quiz_data = {
            'quiz_id': quiz_id,
            'answers': answers
        }
        
        result = LearningService.submit_diagnosis_quiz(user_id, quiz_data)
        
        status_code = 200 if result['success'] else 400
        
        # 에러 코드별 상태 코드 조정
        if not result['success']:
            error_code = result.get('error_code', '')
            if error_code == 'USER_NOT_FOUND':
                status_code = 404
            elif error_code in ['NO_ANSWERS', 'INVALID_ANSWER_FORMAT']:
                status_code = 400
            else:
                status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"진단 퀴즈 제출 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@diagnosis_bp.route('/result/<int:user_id>', methods=['GET'])
@token_required
def get_diagnosis_result(user_id):
    """
    진단 결과 조회 API (관리자용 또는 본인 조회)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "진단 결과를 조회했습니다.",
        "data": {
            "user_id": 1,
            "current_level": "high",
            "current_type": "business",
            "diagnosis_date": "2024-01-01T00:00:00",
            "recommended_chapters": [...]
        }
    }
    """
    try:
        current_user_id = g.current_user['user_id']
        
        # 본인 또는 관리자만 조회 가능 (현재는 본인만)
        if current_user_id != user_id:
            return jsonify(create_response(
                success=False,
                message="본인의 진단 결과만 조회할 수 있습니다.",
                error_code="ACCESS_DENIED"
            )), 403
        
        from models.user import User
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 추천 챕터 조회
        recommended_chapters = LearningService._get_recommended_chapters(user.user_level, user.user_type)
        
        return jsonify(create_response(
            success=True,
            message="진단 결과를 조회했습니다.",
            data={
                'user_id': user.user_id,
                'current_level': user.user_level,
                'current_type': user.user_type,
                'level_description': LearningService._get_level_description(user.user_level),
                'type_description': LearningService._get_type_description(user.user_type),
                'diagnosis_date': user.updated_at.isoformat(),
                'recommended_chapters': recommended_chapters
            }
        )), 200
        
    except Exception as e:
        logger.error(f"진단 결과 조회 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500


@diagnosis_bp.route('/retake', methods=['POST'])
@token_required
def retake_diagnosis():
    """
    진단 재실시 API
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response:
    {
        "success": true,
        "message": "진단을 재실시할 수 있습니다.",
        "data": {
            "quiz_id": "diagnosis_1_1640995200",
            "previous_result": {
                "level": "medium",
                "type": "beginner"
            }
        }
    }
    """
    try:
        user_id = g.current_user['user_id']
        
        from models.user import User
        user = User.get_by_id(user_id)
        if not user:
            return jsonify(create_response(
                success=False,
                message="사용자를 찾을 수 없습니다.",
                error_code="USER_NOT_FOUND"
            )), 404
        
        # 이전 진단 결과 저장
        previous_result = {
            'level': user.user_level,
            'type': user.user_type
        }
        
        # 새로운 진단 퀴즈 생성
        quiz_result = LearningService.get_diagnosis_quiz(user_id)
        
        if quiz_result['success']:
            quiz_result['data']['previous_result'] = previous_result
            quiz_result['message'] = "진단을 재실시할 수 있습니다."
        
        status_code = 200 if quiz_result['success'] else 500
        
        return jsonify(quiz_result), status_code
        
    except Exception as e:
        logger.error(f"진단 재실시 API 오류: {str(e)}")
        return jsonify(create_response(
            success=False,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_ERROR"
        )), 500