# blueprints/ui_sync.py
# UI 상태 동기화 및 실시간 업데이트 API

from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional
import json
from datetime import datetime

from services.ui_mode_service import get_ui_mode_manager, UIStateSerializer
from services.agent_ui_service import get_agent_ui_generator, get_ui_transition_manager
from workflow.state_management import StateManager, TutorState
from utils.auth_middleware import require_auth
from utils.response_utils import success_response, error_response

ui_sync_bp = Blueprint('ui_sync', __name__)


@ui_sync_bp.route('/ui/state', methods=['GET'])
@require_auth
def get_ui_state():
    """현재 UI 상태 조회"""
    try:
        user_id = session.get('user_id')
        
        # 현재 사용자의 상태 조회 (실제로는 Redis나 DB에서 조회)
        # 여기서는 세션에서 임시로 조회
        state_data = session.get('tutor_state')
        if not state_data:
            # 기본 상태 생성
            state = StateManager.create_initial_state(user_id)
            session['tutor_state'] = state
        else:
            state = TutorState(state_data)
        
        # UI 상태 생성
        ui_generator = get_agent_ui_generator()
        current_agent = state.get('current_stage', 'learning_supervisor')
        
        ui_state = ui_generator.generate_ui_for_agent(current_agent, state)
        serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
        
        return success_response({
            'ui_state': serialized_ui,
            'current_agent': current_agent,
            'user_context': {
                'user_id': user_id,
                'chapter': state['current_chapter'],
                'stage': state['current_stage'],
                'level': state['user_level'],
                'type': state['user_type']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 상태 조회 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/transition', methods=['POST'])
@require_auth
def handle_ui_transition():
    """UI 전환 이벤트 처리"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        event = data.get('event')
        agent_name = data.get('agent_name')
        context = data.get('context', {})
        
        if not event or not agent_name:
            return error_response("event와 agent_name이 필요합니다.", 400)
        
        # 현재 상태 조회
        state_data = session.get('tutor_state')
        if not state_data:
            state = StateManager.create_initial_state(user_id)
        else:
            state = TutorState(state_data)
        
        # UI 전환 처리
        transition_manager = get_ui_transition_manager()
        ui_state = transition_manager.handle_transition(event, agent_name, state, context)
        
        # 상태 업데이트
        state = StateManager.handle_ui_transition(state, event, agent_name, context)
        session['tutor_state'] = state
        
        # 응답 생성
        serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
        
        return success_response({
            'ui_state': serialized_ui,
            'transition_event': event,
            'target_agent': agent_name,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 전환 처리 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/elements/update', methods=['POST'])
@require_auth
def update_ui_elements():
    """특정 UI 요소 업데이트"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        element_updates = data.get('elements', [])
        agent_name = data.get('agent_name')
        
        if not element_updates or not agent_name:
            return error_response("elements와 agent_name이 필요합니다.", 400)
        
        # 현재 상태 조회
        state_data = session.get('tutor_state')
        if not state_data:
            return error_response("사용자 상태를 찾을 수 없습니다.", 404)
        
        state = TutorState(state_data)
        
        # UI 요소 업데이트
        ui_generator = get_agent_ui_generator()
        ui_state = ui_generator.generate_ui_for_agent(agent_name, state)
        
        # 특정 요소들 업데이트
        for update in element_updates:
            element_id = update.get('element_id')
            new_properties = update.get('properties', {})
            
            # UI 상태에서 해당 요소 찾아서 업데이트
            for element in ui_state.elements:
                if element.element_id == element_id:
                    for prop, value in new_properties.items():
                        if hasattr(element, prop):
                            setattr(element, prop, value)
        
        # 업데이트된 UI 상태 직렬화
        serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
        
        # 상태에 UI 정보 저장
        state['ui_elements'] = serialized_ui
        session['tutor_state'] = state
        
        return success_response({
            'updated_ui_state': serialized_ui,
            'updated_elements': element_updates,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 요소 업데이트 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/mode', methods=['POST'])
@require_auth
def switch_ui_mode():
    """UI 모드 전환"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        if not data:
            return error_response("요청 데이터가 없습니다.", 400)
        
        new_mode = data.get('mode')
        context = data.get('context', {})
        
        if not new_mode:
            return error_response("mode가 필요합니다.", 400)
        
        # 유효한 모드인지 확인
        valid_modes = ['chat', 'quiz', 'restricted', 'error', 'loading']
        if new_mode not in valid_modes:
            return error_response(f"유효하지 않은 모드입니다. 가능한 모드: {valid_modes}", 400)
        
        # UI 모드 전환
        ui_manager = get_ui_mode_manager()
        from services.ui_mode_service import UIMode
        ui_mode = UIMode(new_mode)
        
        ui_state = ui_manager.switch_mode(ui_mode, context)
        serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
        
        # 사용자 상태 업데이트
        state_data = session.get('tutor_state')
        if state_data:
            state = TutorState(state_data)
            state['ui_mode'] = new_mode
            state['ui_elements'] = serialized_ui
            session['tutor_state'] = state
        
        return success_response({
            'ui_state': serialized_ui,
            'previous_mode': ui_manager.get_previous_mode().value if ui_manager.get_previous_mode() else None,
            'current_mode': new_mode,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 모드 전환 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/sync/status', methods=['GET'])
@require_auth
def get_sync_status():
    """UI 동기화 상태 확인"""
    try:
        user_id = session.get('user_id')
        
        # 현재 상태 조회
        state_data = session.get('tutor_state')
        if not state_data:
            return success_response({
                'sync_status': 'no_state',
                'message': '사용자 상태가 없습니다.',
                'timestamp': datetime.now().isoformat()
            })
        
        state = TutorState(state_data)
        
        # 동기화 상태 정보 생성
        sync_info = {
            'sync_status': 'active',
            'user_id': user_id,
            'current_agent': state.get('current_stage', 'unknown'),
            'ui_mode': state.get('ui_mode', 'chat'),
            'last_update': state.get('loop_start_time', datetime.now().isoformat()),
            'conversation_count': len(state.get('current_loop_conversations', [])),
            'loop_id': state.get('current_loop_id'),
            'chapter': state.get('current_chapter'),
            'stage': state.get('current_stage'),
            'timestamp': datetime.now().isoformat()
        }
        
        return success_response(sync_info)
        
    except Exception as e:
        return error_response(f"동기화 상태 확인 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/reset', methods=['POST'])
@require_auth
def reset_ui_state():
    """UI 상태 초기화"""
    try:
        user_id = session.get('user_id')
        
        # 새로운 초기 상태 생성
        state = StateManager.create_initial_state(user_id)
        session['tutor_state'] = state
        
        # 기본 UI 상태 생성
        ui_generator = get_agent_ui_generator()
        ui_state = ui_generator.generate_ui_for_agent('learning_supervisor', state)
        serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
        
        # 상태에 UI 정보 저장
        state['ui_elements'] = serialized_ui
        session['tutor_state'] = state
        
        return success_response({
            'message': 'UI 상태가 초기화되었습니다.',
            'ui_state': serialized_ui,
            'reset_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 상태 초기화 실패: {str(e)}", 500)


@ui_sync_bp.route('/ui/history', methods=['GET'])
@require_auth
def get_ui_history():
    """UI 상태 변경 이력 조회"""
    try:
        user_id = session.get('user_id')
        
        # 현재 상태에서 대화 이력 조회
        state_data = session.get('tutor_state')
        if not state_data:
            return success_response({
                'history': [],
                'message': '이력이 없습니다.'
            })
        
        state = TutorState(state_data)
        
        # 대화 이력을 UI 이력으로 변환
        ui_history = []
        conversations = state.get('current_loop_conversations', [])
        
        for conv in conversations:
            ui_event = {
                'agent_name': conv.get('agent_name'),
                'timestamp': conv.get('timestamp'),
                'ui_elements': conv.get('ui_elements'),
                'user_message': conv.get('user_message', ''),
                'system_response': conv.get('system_response', '')[:100] + '...' if len(conv.get('system_response', '')) > 100 else conv.get('system_response', '')
            }
            ui_history.append(ui_event)
        
        return success_response({
            'history': ui_history,
            'total_events': len(ui_history),
            'current_loop_id': state.get('current_loop_id'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f"UI 이력 조회 실패: {str(e)}", 500)


# WebSocket 지원을 위한 이벤트 핸들러 (선택적)
class UIEventEmitter:
    """실시간 UI 이벤트 발송을 위한 클래스"""
    
    def __init__(self):
        self.subscribers = {}  # user_id -> callback 매핑
    
    def subscribe(self, user_id: str, callback):
        """사용자 구독 등록"""
        self.subscribers[user_id] = callback
    
    def unsubscribe(self, user_id: str):
        """사용자 구독 해제"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
    
    def emit_ui_change(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """UI 변경 이벤트 발송"""
        if user_id in self.subscribers:
            callback = self.subscribers[user_id]
            try:
                callback({
                    'event_type': event_type,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"UI 이벤트 발송 실패: {e}")


# 전역 이벤트 에미터 인스턴스
ui_event_emitter = UIEventEmitter()


def get_ui_event_emitter() -> UIEventEmitter:
    """전역 UI 이벤트 에미터 반환"""
    return ui_event_emitter