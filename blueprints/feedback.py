# blueprints/feedback.py
# 사용자 피드백 수집 API

from flask import Blueprint, request, jsonify
from utils.langsmith_config import log_user_feedback, langsmith_config
from utils.auth_middleware import token_required

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/submit', methods=['POST'])
@token_required
def submit_feedback(current_user):
    """사용자 피드백 제출"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['run_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        run_id = data['run_id']
        rating = data['rating']
        comment = data.get('comment', '')
        
        # 평점 유효성 검증 (1-5)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'message': '평점은 1-5 사이의 정수여야 합니다.'
            }), 400
        
        # LangSmith에 피드백 전송
        if langsmith_config.is_enabled():
            log_user_feedback(run_id, rating, comment)
            
            return jsonify({
                'success': True,
                'message': '피드백이 성공적으로 제출되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'LangSmith가 비활성화되어 있습니다.'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'피드백 제출 중 오류가 발생했습니다: {str(e)}'
        }), 500


@feedback_bp.route('/runs/<run_id>', methods=['GET'])
@token_required
def get_run_info(current_user, run_id):
    """실행 정보 조회"""
    try:
        if not langsmith_config.is_enabled():
            return jsonify({
                'success': False,
                'message': 'LangSmith가 비활성화되어 있습니다.'
            }), 503
        
        # LangSmith에서 실행 정보 조회
        client = langsmith_config.client
        if not client:
            return jsonify({
                'success': False,
                'message': 'LangSmith 클라이언트를 사용할 수 없습니다.'
            }), 503
        
        try:
            run = client.read_run(run_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'id': str(run.id),
                    'name': run.name,
                    'run_type': run.run_type,
                    'start_time': run.start_time.isoformat() if run.start_time else None,
                    'end_time': run.end_time.isoformat() if run.end_time else None,
                    'status': run.status,
                    'inputs': run.inputs,
                    'outputs': run.outputs,
                    'tags': run.tags
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'실행 정보를 찾을 수 없습니다: {str(e)}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'실행 정보 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@feedback_bp.route('/status', methods=['GET'])
def get_langsmith_status():
    """LangSmith 상태 확인"""
    try:
        is_enabled = langsmith_config.is_enabled()
        project_name = langsmith_config.project_name
        
        return jsonify({
            'success': True,
            'data': {
                'enabled': is_enabled,
                'project_name': project_name,
                'endpoint': langsmith_config.client.api_url if langsmith_config.client else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'상태 확인 중 오류가 발생했습니다: {str(e)}'
        }), 500