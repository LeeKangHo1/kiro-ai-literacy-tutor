# services/websocket_service.py
# WebSocket을 통한 실시간 UI 업데이트 서비스

from typing import Dict, Any, Optional, List, Callable
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

from services.ui_mode_service import UIStateSerializer
from services.agent_ui_service import get_agent_ui_generator
from workflow.state_management import TutorState


@dataclass
class WebSocketMessage:
    """WebSocket 메시지 데이터 클래스"""
    message_id: str
    message_type: str  # ui_update, state_change, error, ping, pong
    user_id: str
    data: Dict[str, Any]
    timestamp: str
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        """JSON 문자열에서 생성"""
        data = json.loads(json_str)
        return cls(**data)


class WebSocketConnection:
    """개별 WebSocket 연결 관리 클래스"""
    
    def __init__(self, user_id: str, websocket, connection_id: str = None):
        self.user_id = user_id
        self.websocket = websocket
        self.connection_id = connection_id or str(uuid.uuid4())
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()
        self.is_active = True
        self.subscribed_events = set()  # 구독 중인 이벤트 타입들
    
    async def send_message(self, message: WebSocketMessage):
        """메시지 전송"""
        try:
            if self.is_active:
                await self.websocket.send(message.to_json())
                return True
        except Exception as e:
            print(f"WebSocket 메시지 전송 실패 (user: {self.user_id}): {e}")
            self.is_active = False
            return False
    
    async def close(self):
        """연결 종료"""
        try:
            self.is_active = False
            await self.websocket.close()
        except Exception as e:
            print(f"WebSocket 연결 종료 실패 (user: {self.user_id}): {e}")
    
    def subscribe_to_event(self, event_type: str):
        """이벤트 구독"""
        self.subscribed_events.add(event_type)
    
    def unsubscribe_from_event(self, event_type: str):
        """이벤트 구독 해제"""
        self.subscribed_events.discard(event_type)
    
    def is_subscribed_to(self, event_type: str) -> bool:
        """이벤트 구독 여부 확인"""
        return event_type in self.subscribed_events


class WebSocketManager:
    """WebSocket 연결 및 메시지 관리자"""
    
    def __init__(self):
        self.connections: Dict[str, List[WebSocketConnection]] = {}  # user_id -> connections
        self.connection_by_id: Dict[str, WebSocketConnection] = {}  # connection_id -> connection
        self.message_handlers: Dict[str, Callable] = {}
        self.ui_generator = None
        
        # 기본 메시지 핸들러 등록
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """기본 메시지 핸들러 등록"""
        self.message_handlers.update({
            'ping': self._handle_ping,
            'subscribe': self._handle_subscribe,
            'unsubscribe': self._handle_unsubscribe,
            'ui_request': self._handle_ui_request,
            'state_sync': self._handle_state_sync
        })
    
    async def add_connection(self, user_id: str, websocket) -> WebSocketConnection:
        """새 연결 추가"""
        connection = WebSocketConnection(user_id, websocket)
        
        # 사용자별 연결 목록에 추가
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(connection)
        
        # 연결 ID로 인덱싱
        self.connection_by_id[connection.connection_id] = connection
        
        # 기본 이벤트 구독
        connection.subscribe_to_event('ui_update')
        connection.subscribe_to_event('state_change')
        
        print(f"WebSocket 연결 추가: user={user_id}, connection_id={connection.connection_id}")
        
        # 연결 확인 메시지 전송
        welcome_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='connection_established',
            user_id=user_id,
            data={
                'connection_id': connection.connection_id,
                'connected_at': connection.connected_at.isoformat(),
                'subscribed_events': list(connection.subscribed_events)
            },
            timestamp=datetime.now().isoformat()
        )
        await connection.send_message(welcome_message)
        
        return connection
    
    async def remove_connection(self, connection_id: str):
        """연결 제거"""
        if connection_id in self.connection_by_id:
            connection = self.connection_by_id[connection_id]
            user_id = connection.user_id
            
            # 연결 종료
            await connection.close()
            
            # 인덱스에서 제거
            del self.connection_by_id[connection_id]
            
            # 사용자별 연결 목록에서 제거
            if user_id in self.connections:
                self.connections[user_id] = [
                    conn for conn in self.connections[user_id] 
                    if conn.connection_id != connection_id
                ]
                
                # 사용자의 모든 연결이 제거되면 목록 자체 제거
                if not self.connections[user_id]:
                    del self.connections[user_id]
            
            print(f"WebSocket 연결 제거: user={user_id}, connection_id={connection_id}")
    
    async def handle_message(self, connection_id: str, message_data: str):
        """메시지 처리"""
        try:
            message = WebSocketMessage.from_json(message_data)
            
            # 연결 확인
            if connection_id not in self.connection_by_id:
                print(f"존재하지 않는 연결에서 메시지 수신: {connection_id}")
                return
            
            connection = self.connection_by_id[connection_id]
            
            # 메시지 타입별 핸들러 실행
            handler = self.message_handlers.get(message.message_type)
            if handler:
                await handler(connection, message)
            else:
                print(f"알 수 없는 메시지 타입: {message.message_type}")
                
        except Exception as e:
            print(f"메시지 처리 오류: {e}")
            # 오류 메시지 전송
            if connection_id in self.connection_by_id:
                connection = self.connection_by_id[connection_id]
                error_message = WebSocketMessage(
                    message_id=str(uuid.uuid4()),
                    message_type='error',
                    user_id=connection.user_id,
                    data={'error': str(e), 'original_message': message_data},
                    timestamp=datetime.now().isoformat()
                )
                await connection.send_message(error_message)
    
    async def broadcast_ui_update(self, user_id: str, ui_state_data: Dict[str, Any], 
                                agent_name: str = None):
        """특정 사용자에게 UI 업데이트 브로드캐스트"""
        if user_id not in self.connections:
            return
        
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='ui_update',
            user_id=user_id,
            data={
                'ui_state': ui_state_data,
                'agent_name': agent_name,
                'update_type': 'full_update'
            },
            timestamp=datetime.now().isoformat()
        )
        
        # 해당 사용자의 모든 활성 연결에 전송
        for connection in self.connections[user_id]:
            if connection.is_active and connection.is_subscribed_to('ui_update'):
                await connection.send_message(message)
    
    async def broadcast_state_change(self, user_id: str, state_change_data: Dict[str, Any]):
        """상태 변경 브로드캐스트"""
        if user_id not in self.connections:
            return
        
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='state_change',
            user_id=user_id,
            data=state_change_data,
            timestamp=datetime.now().isoformat()
        )
        
        for connection in self.connections[user_id]:
            if connection.is_active and connection.is_subscribed_to('state_change'):
                await connection.send_message(message)
    
    async def broadcast_element_update(self, user_id: str, element_updates: List[Dict[str, Any]]):
        """특정 UI 요소 업데이트 브로드캐스트"""
        if user_id not in self.connections:
            return
        
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='ui_update',
            user_id=user_id,
            data={
                'element_updates': element_updates,
                'update_type': 'partial_update'
            },
            timestamp=datetime.now().isoformat()
        )
        
        for connection in self.connections[user_id]:
            if connection.is_active and connection.is_subscribed_to('ui_update'):
                await connection.send_message(message)
    
    # 메시지 핸들러들
    async def _handle_ping(self, connection: WebSocketConnection, message: WebSocketMessage):
        """핑 메시지 처리"""
        connection.last_ping = datetime.now()
        
        pong_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='pong',
            user_id=connection.user_id,
            data={'ping_id': message.data.get('ping_id', '')},
            timestamp=datetime.now().isoformat()
        )
        await connection.send_message(pong_message)
    
    async def _handle_subscribe(self, connection: WebSocketConnection, message: WebSocketMessage):
        """이벤트 구독 처리"""
        event_types = message.data.get('event_types', [])
        
        for event_type in event_types:
            connection.subscribe_to_event(event_type)
        
        response_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='subscription_updated',
            user_id=connection.user_id,
            data={
                'subscribed_events': list(connection.subscribed_events),
                'newly_subscribed': event_types
            },
            timestamp=datetime.now().isoformat()
        )
        await connection.send_message(response_message)
    
    async def _handle_unsubscribe(self, connection: WebSocketConnection, message: WebSocketMessage):
        """이벤트 구독 해제 처리"""
        event_types = message.data.get('event_types', [])
        
        for event_type in event_types:
            connection.unsubscribe_from_event(event_type)
        
        response_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='subscription_updated',
            user_id=connection.user_id,
            data={
                'subscribed_events': list(connection.subscribed_events),
                'unsubscribed': event_types
            },
            timestamp=datetime.now().isoformat()
        )
        await connection.send_message(response_message)
    
    async def _handle_ui_request(self, connection: WebSocketConnection, message: WebSocketMessage):
        """UI 상태 요청 처리"""
        try:
            # UI 생성기가 없으면 초기화
            if not self.ui_generator:
                self.ui_generator = get_agent_ui_generator()
            
            # 요청 데이터에서 상태 정보 추출
            state_data = message.data.get('state')
            agent_name = message.data.get('agent_name', 'learning_supervisor')
            
            if state_data:
                state = TutorState(state_data)
                ui_state = self.ui_generator.generate_ui_for_agent(agent_name, state)
                serialized_ui = UIStateSerializer.serialize_ui_state(ui_state)
                
                response_message = WebSocketMessage(
                    message_id=str(uuid.uuid4()),
                    message_type='ui_response',
                    user_id=connection.user_id,
                    data={
                        'ui_state': serialized_ui,
                        'agent_name': agent_name,
                        'request_id': message.data.get('request_id')
                    },
                    timestamp=datetime.now().isoformat()
                )
                await connection.send_message(response_message)
            
        except Exception as e:
            error_message = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                message_type='error',
                user_id=connection.user_id,
                data={
                    'error': f'UI 요청 처리 실패: {str(e)}',
                    'request_id': message.data.get('request_id')
                },
                timestamp=datetime.now().isoformat()
            )
            await connection.send_message(error_message)
    
    async def _handle_state_sync(self, connection: WebSocketConnection, message: WebSocketMessage):
        """상태 동기화 처리"""
        # 클라이언트의 상태와 서버 상태 동기화
        client_state = message.data.get('client_state')
        
        # 실제 구현에서는 서버의 최신 상태와 비교하여 동기화
        sync_response = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type='state_sync_response',
            user_id=connection.user_id,
            data={
                'sync_status': 'completed',
                'server_state': client_state,  # 실제로는 서버의 최신 상태
                'sync_timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
        await connection.send_message(sync_response)
    
    async def cleanup_inactive_connections(self):
        """비활성 연결 정리"""
        current_time = datetime.now()
        inactive_connections = []
        
        for connection_id, connection in self.connection_by_id.items():
            # 5분 이상 핑이 없으면 비활성으로 간주
            if (current_time - connection.last_ping).seconds > 300:
                inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            await self.remove_connection(connection_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """연결 통계 반환"""
        total_connections = len(self.connection_by_id)
        active_connections = sum(1 for conn in self.connection_by_id.values() if conn.is_active)
        users_connected = len(self.connections)
        
        return {
            'total_connections': total_connections,
            'active_connections': active_connections,
            'users_connected': users_connected,
            'connections_per_user': {
                user_id: len(connections) 
                for user_id, connections in self.connections.items()
            }
        }


# 전역 WebSocket 매니저 인스턴스
_global_websocket_manager = None


def get_websocket_manager() -> WebSocketManager:
    """전역 WebSocket 매니저 인스턴스 반환"""
    global _global_websocket_manager
    if _global_websocket_manager is None:
        _global_websocket_manager = WebSocketManager()
    return _global_websocket_manager


def reset_websocket_manager():
    """전역 WebSocket 매니저 초기화 (테스트용)"""
    global _global_websocket_manager
    _global_websocket_manager = None


# Flask-SocketIO 통합을 위한 래퍼 클래스
class SocketIOIntegration:
    """Flask-SocketIO와의 통합을 위한 클래스"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.websocket_manager = get_websocket_manager()
    
    def setup_handlers(self):
        """SocketIO 이벤트 핸들러 설정"""
        
        @self.socketio.on('connect')
        def handle_connect(auth):
            user_id = auth.get('user_id') if auth else None
            if user_id:
                # 연결 정보를 WebSocket 매니저에 등록
                # 실제 WebSocket 객체 대신 SocketIO 세션 사용
                print(f"SocketIO 연결: user_id={user_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("SocketIO 연결 해제")
        
        @self.socketio.on('ui_update_request')
        def handle_ui_update_request(data):
            user_id = data.get('user_id')
            if user_id:
                # UI 업데이트 요청 처리
                self.socketio.emit('ui_update', data, room=user_id)
        
        @self.socketio.on('state_change')
        def handle_state_change(data):
            user_id = data.get('user_id')
            if user_id:
                # 상태 변경 브로드캐스트
                self.socketio.emit('state_updated', data, room=user_id)
    
    def emit_ui_update(self, user_id: str, ui_data: Dict[str, Any]):
        """UI 업데이트 이벤트 발송"""
        self.socketio.emit('ui_update', ui_data, room=user_id)
    
    def emit_state_change(self, user_id: str, state_data: Dict[str, Any]):
        """상태 변경 이벤트 발송"""
        self.socketio.emit('state_change', state_data, room=user_id)