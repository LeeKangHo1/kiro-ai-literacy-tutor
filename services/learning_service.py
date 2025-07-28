# services/learning_service.py
# 학습 서비스

from models.user import User, UserLearningProgress
from models.chapter import Chapter
from models.learning_loop import LearningLoop
from models.conversation import Conversation
from models.quiz_attempt import QuizAttempt
from utils.response_utils import create_response
from services.database_service import DatabaseService
from workflow.graph_builder import TutorWorkflow
from workflow.state_management import TutorState, StateManager
from services.ui_mode_service import UIStateSerializer
from services.websocket_service import get_websocket_manager
from utils.error_handler import (
    BusinessLogicError, DatabaseError, ValidationError,
    handle_errors, ErrorCategory, ErrorSeverity
)
from utils.logging_config import LoggingConfig, log_function_call
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = LoggingConfig.get_contextual_logger('learning_service')

class LearningService:
    """학습 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    @staticmethod
    @handle_errors(ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.MEDIUM)
    @log_function_call('learning_service')
    def get_diagnosis_quiz(user_id: int) -> Dict[str, Any]:
        """
        사용자 진단 퀴즈 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            진단 퀴즈 데이터
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            # 진단 퀴즈 문제 생성 (기본 AI 지식 수준 측정)
            diagnosis_questions = [
                {
                    "question_id": 1,
                    "question": "AI(인공지능)에 대한 설명으로 가장 적절한 것은?",
                    "type": "multiple_choice",
                    "options": [
                        "컴퓨터가 인간처럼 생각하고 학습할 수 있도록 하는 기술",
                        "단순히 프로그래밍된 명령을 실행하는 소프트웨어",
                        "인터넷에서 정보를 검색하는 도구",
                        "데이터를 저장하는 데이터베이스 시스템"
                    ],
                    "correct_answer": 0,
                    "difficulty": "low"
                },
                {
                    "question_id": 2,
                    "question": "ChatGPT와 같은 대화형 AI를 업무에서 활용해본 경험이 있나요?",
                    "type": "multiple_choice",
                    "options": [
                        "전혀 사용해본 적이 없다",
                        "몇 번 시도해봤지만 잘 모르겠다",
                        "가끔 사용하지만 기본적인 질문만 한다",
                        "자주 사용하며 다양한 업무에 활용한다"
                    ],
                    "correct_answer": None,  # 경험 측정용
                    "difficulty": "medium"
                },
                {
                    "question_id": 3,
                    "question": "프롬프트(Prompt)란 무엇인가요?",
                    "type": "multiple_choice",
                    "options": [
                        "AI에게 주는 명령이나 질문",
                        "AI가 생성한 결과물",
                        "AI 모델의 학습 데이터",
                        "AI 소프트웨어의 이름"
                    ],
                    "correct_answer": 0,
                    "difficulty": "medium"
                },
                {
                    "question_id": 4,
                    "question": "다음 중 AI 활용 목적으로 가장 관심 있는 분야는?",
                    "type": "multiple_choice",
                    "options": [
                        "업무 자동화 및 효율성 향상",
                        "창작 활동 (글쓰기, 아이디어 생성)",
                        "학습 및 교육 지원",
                        "일상생활 편의성 향상"
                    ],
                    "correct_answer": None,  # 관심사 측정용
                    "difficulty": "low"
                }
            ]
            
            return create_response(
                success=True,
                message="진단 퀴즈를 조회했습니다.",
                data={
                    'quiz_id': f"diagnosis_{user_id}_{int(datetime.utcnow().timestamp())}",
                    'title': "AI 활용 수준 진단",
                    'description': "귀하의 AI 활용 수준을 파악하여 맞춤형 학습 과정을 제공합니다.",
                    'questions': diagnosis_questions,
                    'total_questions': len(diagnosis_questions),
                    'estimated_time_minutes': 5
                }
            )
            
        except Exception as e:
            logger.error(f"진단 퀴즈 조회 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="진단 퀴즈 조회 중 오류가 발생했습니다.",
                error_code="DIAGNOSIS_QUIZ_ERROR"
            )
    
    @staticmethod
    def submit_diagnosis_quiz(user_id: int, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        진단 퀴즈 제출 및 사용자 레벨 결정
        
        Args:
            user_id: 사용자 ID
            quiz_data: 퀴즈 답변 데이터
            
        Returns:
            진단 결과 및 추천 학습 경로
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            answers = quiz_data.get('answers', [])
            if not answers:
                return create_response(
                    success=False,
                    message="퀴즈 답변이 제공되지 않았습니다.",
                    error_code="NO_ANSWERS"
                )
            
            # 답변 분석 및 레벨 결정
            score = 0
            experience_level = 0
            
            for answer in answers:
                question_id = answer.get('question_id')
                selected_option = answer.get('selected_option')
                
                if question_id == 1 and selected_option == 0:  # AI 기본 개념
                    score += 25
                elif question_id == 2:  # 경험 수준
                    experience_level = selected_option
                elif question_id == 3 and selected_option == 0:  # 프롬프트 개념
                    score += 25
            
            # 경험 수준에 따른 추가 점수
            if experience_level >= 2:
                score += 30
            elif experience_level == 1:
                score += 15
            
            # 사용자 레벨 결정
            if score >= 70:
                user_level = 'high'
                recommended_type = 'business'
            elif score >= 40:
                user_level = 'medium'
                recommended_type = 'business' if experience_level >= 2 else 'beginner'
            else:
                user_level = 'low'
                recommended_type = 'beginner'
            
            # 사용자 정보 업데이트
            user.user_level = user_level
            if user.user_type != recommended_type:
                user.user_type = recommended_type
            user.save()
            
            # 추천 학습 경로 생성
            recommended_chapters = LearningService._get_recommended_chapters(user_level, recommended_type)
            
            logger.info(f"진단 완료 - user_id: {user_id}, level: {user_level}, type: {recommended_type}")
            
            return create_response(
                success=True,
                message="진단이 완료되었습니다.",
                data={
                    'diagnosis_result': {
                        'score': score,
                        'user_level': user_level,
                        'user_type': recommended_type,
                        'level_description': LearningService._get_level_description(user_level),
                        'type_description': LearningService._get_type_description(recommended_type)
                    },
                    'recommended_chapters': recommended_chapters,
                    'next_steps': {
                        'action': 'start_learning',
                        'recommended_chapter': recommended_chapters[0] if recommended_chapters else None
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"진단 퀴즈 제출 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="진단 퀴즈 제출 중 오류가 발생했습니다.",
                error_code="DIAGNOSIS_SUBMIT_ERROR"
            )
    
    @staticmethod
    async def process_chat_message(user_id: int, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        채팅 메시지 처리 (LangGraph 워크플로우 실행 + UI 모드 관리)
        
        Args:
            user_id: 사용자 ID
            message: 사용자 메시지
            context: 추가 컨텍스트 정보
            
        Returns:
            AI 응답 및 UI 상태
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            # 현재 학습 상태 조회 또는 생성
            current_context = context or {}
            current_chapter = current_context.get('current_chapter', 1)
            current_stage = current_context.get('stage', 'theory')
            loop_id = current_context.get('loop_id')
            
            # 기존 상태가 있으면 복원, 없으면 새로 생성
            if loop_id:
                state = LearningService._restore_or_create_state(
                    user_id, user, message, current_chapter, current_stage, loop_id
                )
            else:
                state = StateManager.create_initial_state(str(user_id), user.user_type, user.user_level)
                state['user_message'] = message
                state['current_chapter'] = current_chapter
                state['current_stage'] = current_stage
            
            # 사용자 입력 수신 이벤트 처리 (UI를 로딩 상태로 전환)
            state = StateManager.handle_ui_transition(
                state, "user_input_received", current_stage
            )
            
            # WebSocket을 통한 실시간 UI 업데이트
            websocket_manager = get_websocket_manager()
            if state.get('ui_elements'):
                await websocket_manager.broadcast_ui_update(
                    str(user_id), 
                    state['ui_elements'], 
                    current_stage
                )
            
            # LangGraph 워크플로우 실행
            workflow = TutorWorkflow()
            result_state = workflow.execute(state)
            
            # 에이전트 응답 준비 완료 이벤트 처리
            current_agent = result_state.get('current_stage', 'learning_supervisor')
            result_state = StateManager.handle_ui_transition(
                result_state, "agent_response_ready", current_agent
            )
            
            # 최종 UI 상태 브로드캐스트
            if result_state.get('ui_elements'):
                await websocket_manager.broadcast_ui_update(
                    str(user_id),
                    result_state['ui_elements'],
                    current_agent
                )
            
            # 대화 기록 저장
            LearningService._save_conversation_to_db(result_state)
            
            # 응답 구성
            response_data = {
                'response': result_state.get('system_message', ''),
                'ui_mode': result_state.get('ui_mode', 'chat'),
                'ui_elements': result_state.get('ui_elements'),
                'current_stage': result_state.get('current_stage'),
                'current_agent': current_agent,
                'loop_id': result_state.get('current_loop_id'),
                'chapter': result_state.get('current_chapter'),
                'user_context': {
                    'user_type': result_state.get('user_type'),
                    'user_level': result_state.get('user_level')
                }
            }
            
            return create_response(
                success=True,
                message="메시지가 처리되었습니다.",
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"채팅 메시지 처리 중 오류: {str(e)}")
            
            # 오류 발생 시 UI를 오류 상태로 전환
            try:
                error_state = StateManager.create_initial_state(str(user_id))
                error_state = StateManager.handle_ui_transition(
                    error_state, "error_occurred", "system",
                    {'error_message': str(e)}
                )
                
                # 오류 상태 브로드캐스트
                websocket_manager = get_websocket_manager()
                if error_state.get('ui_elements'):
                    await websocket_manager.broadcast_ui_update(
                        str(user_id),
                        error_state['ui_elements'],
                        "system"
                    )
            except:
                pass  # 오류 처리 중 추가 오류 발생 시 무시
            
            return create_response(
                success=False,
                message="메시지 처리 중 오류가 발생했습니다.",
                error_code="CHAT_PROCESSING_ERROR",
                data={
                    'ui_mode': 'error',
                    'ui_elements': {
                        'mode': 'error',
                        'title': '오류 발생',
                        'description': '메시지 처리 중 오류가 발생했습니다. 다시 시도해주세요.',
                        'elements': [
                            {
                                'element_type': 'button',
                                'element_id': 'retry_button',
                                'label': '다시 시도',
                                'style': {'variant': 'primary'}
                            }
                        ]
                    }
                }
            )
    
    @staticmethod
    def _restore_or_create_state(user_id: int, user: User, message: str, 
                               chapter: int, stage: str, loop_id: str) -> TutorState:
        """기존 상태 복원 또는 새 상태 생성"""
        try:
            # 데이터베이스에서 기존 루프 조회
            existing_loop = LearningLoop.query.filter_by(
                loop_id=loop_id, 
                user_id=user_id
            ).first()
            
            if existing_loop and existing_loop.loop_status == 'active':
                # 기존 대화 기록 조회
                conversations = Conversation.query.filter_by(
                    loop_id=loop_id
                ).order_by(Conversation.sequence_order).all()
                
                # 상태 복원
                state = StateManager.create_initial_state(str(user_id), user.user_type, user.user_level)
                state['current_loop_id'] = loop_id
                state['current_chapter'] = chapter
                state['current_stage'] = stage
                state['user_message'] = message
                
                # 대화 기록 복원
                current_conversations = []
                for conv in conversations:
                    current_conversations.append({
                        'agent_name': conv.agent_name,
                        'user_message': conv.user_message,
                        'system_response': conv.system_response,
                        'ui_elements': conv.ui_elements,
                        'timestamp': conv.timestamp.isoformat(),
                        'sequence_order': conv.sequence_order
                    })
                
                state['current_loop_conversations'] = current_conversations
                
                return state
            
        except Exception as e:
            logger.warning(f"상태 복원 실패, 새 상태 생성: {e}")
        
        # 복원 실패 시 새 상태 생성
        state = StateManager.create_initial_state(str(user_id), user.user_type, user.user_level)
        state['user_message'] = message
        state['current_chapter'] = chapter
        state['current_stage'] = stage
        
        return state
    
    @staticmethod
    def _save_conversation_to_db(state: TutorState):
        """대화 기록을 데이터베이스에 저장"""
        try:
            loop_id = state.get('current_loop_id')
            user_id = int(state.get('user_id'))
            
            # 학습 루프 확인/생성
            existing_loop = LearningLoop.query.filter_by(loop_id=loop_id).first()
            if not existing_loop:
                new_loop = LearningLoop(
                    loop_id=loop_id,
                    user_id=user_id,
                    chapter_id=state.get('current_chapter'),
                    loop_sequence=1,  # 실제로는 계산 필요
                    loop_status='active'
                )
                DatabaseService.save(new_loop)
            
            # 현재 루프의 새로운 대화만 저장
            current_conversations = state.get('current_loop_conversations', [])
            if current_conversations:
                latest_conversation = current_conversations[-1]
                
                # 이미 저장된 대화인지 확인
                existing_conv = Conversation.query.filter_by(
                    loop_id=loop_id,
                    sequence_order=latest_conversation.get('sequence_order')
                ).first()
                
                if not existing_conv:
                    new_conversation = Conversation(
                        loop_id=loop_id,
                        agent_name=latest_conversation.get('agent_name'),
                        message_type='system',
                        user_message=latest_conversation.get('user_message'),
                        system_response=latest_conversation.get('system_response'),
                        ui_elements=latest_conversation.get('ui_elements'),
                        sequence_order=latest_conversation.get('sequence_order')
                    )
                    DatabaseService.save(new_conversation)
            
        except Exception as e:
            logger.error(f"대화 기록 저장 실패: {e}")
    
    @staticmethod
    def get_available_chapters(user_id: int) -> Dict[str, Any]:
        """
        사용자가 학습 가능한 챕터 목록 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            학습 가능한 챕터 목록
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            # 사용자가 학습 가능한 챕터 조회
            available_chapters = Chapter.get_available_chapters_for_user(user_id)
            
            chapters_data = []
            for chapter in available_chapters:
                user_progress = chapter.get_user_progress(user_id)
                
                chapters_data.append({
                    'chapter_id': chapter.chapter_id,
                    'chapter_number': chapter.chapter_number,
                    'title': chapter.title,
                    'description': chapter.description,
                    'difficulty_level': chapter.difficulty_level,
                    'estimated_duration': chapter.estimated_duration,
                    'prerequisites': chapter.get_prerequisites(),
                    'learning_objectives': chapter.get_learning_objectives(),
                    'user_progress': {
                        'completion_status': user_progress.completion_status if user_progress else 'not_started',
                        'progress_percentage': float(user_progress.progress_percentage) if user_progress else 0.0,
                        'understanding_score': float(user_progress.understanding_score) if user_progress else 0.0,
                        'last_accessed_at': user_progress.last_accessed_at.isoformat() if user_progress and user_progress.last_accessed_at else None
                    }
                })
            
            return create_response(
                success=True,
                message="학습 가능한 챕터 목록을 조회했습니다.",
                data={
                    'chapters': chapters_data,
                    'total_available': len(chapters_data),
                    'user_level': user.user_level,
                    'user_type': user.user_type
                }
            )
            
        except Exception as e:
            logger.error(f"챕터 목록 조회 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="챕터 목록 조회 중 오류가 발생했습니다.",
                error_code="CHAPTERS_FETCH_ERROR"
            )
    
    @staticmethod
    def get_chapter_detail(user_id: int, chapter_id: int) -> Dict[str, Any]:
        """
        특정 챕터의 상세 정보 조회
        
        Args:
            user_id: 사용자 ID
            chapter_id: 챕터 ID
            
        Returns:
            챕터 상세 정보
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            chapter = Chapter.get_by_id(chapter_id)
            if not chapter:
                return create_response(
                    success=False,
                    message="챕터를 찾을 수 없습니다.",
                    error_code="CHAPTER_NOT_FOUND"
                )
            
            # 선수 조건 확인
            prerequisites_met = chapter.check_prerequisites_met(user_id)
            
            # 사용자 진도 조회
            user_progress = chapter.get_user_progress(user_id)
            
            # 챕터 통계
            completion_stats = chapter.get_completion_stats()
            quiz_stats = chapter.get_quiz_stats()
            
            return create_response(
                success=True,
                message="챕터 상세 정보를 조회했습니다.",
                data={
                    'chapter': {
                        'chapter_id': chapter.chapter_id,
                        'chapter_number': chapter.chapter_number,
                        'title': chapter.title,
                        'description': chapter.description,
                        'difficulty_level': chapter.difficulty_level,
                        'estimated_duration': chapter.estimated_duration,
                        'prerequisites': chapter.get_prerequisites(),
                        'learning_objectives': chapter.get_learning_objectives(),
                        'content_metadata': chapter.get_content_metadata()
                    },
                    'user_progress': {
                        'completion_status': user_progress.completion_status if user_progress else 'not_started',
                        'progress_percentage': float(user_progress.progress_percentage) if user_progress else 0.0,
                        'understanding_score': float(user_progress.understanding_score) if user_progress else 0.0,
                        'total_study_time': user_progress.total_study_time if user_progress else 0,
                        'quiz_attempts_count': user_progress.quiz_attempts_count if user_progress else 0,
                        'average_quiz_score': float(user_progress.average_quiz_score) if user_progress else 0.0,
                        'started_at': user_progress.started_at.isoformat() if user_progress and user_progress.started_at else None,
                        'last_accessed_at': user_progress.last_accessed_at.isoformat() if user_progress and user_progress.last_accessed_at else None
                    },
                    'access_info': {
                        'prerequisites_met': prerequisites_met,
                        'can_start': prerequisites_met and (not user_progress or user_progress.completion_status != 'completed')
                    },
                    'statistics': {
                        'completion_stats': completion_stats,
                        'quiz_stats': quiz_stats
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"챕터 상세 정보 조회 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="챕터 상세 정보 조회 중 오류가 발생했습니다.",
                error_code="CHAPTER_DETAIL_ERROR"
            )
    
    @staticmethod
    def start_chapter_learning(user_id: int, chapter_id: int) -> Dict[str, Any]:
        """
        챕터 학습 시작
        
        Args:
            user_id: 사용자 ID
            chapter_id: 챕터 ID
            
        Returns:
            학습 시작 결과
        """
        try:
            user = User.get_by_id(user_id)
            if not user:
                return create_response(
                    success=False,
                    message="사용자를 찾을 수 없습니다.",
                    error_code="USER_NOT_FOUND"
                )
            
            chapter = Chapter.get_by_id(chapter_id)
            if not chapter:
                return create_response(
                    success=False,
                    message="챕터를 찾을 수 없습니다.",
                    error_code="CHAPTER_NOT_FOUND"
                )
            
            # 선수 조건 확인
            if not chapter.check_prerequisites_met(user_id):
                return create_response(
                    success=False,
                    message="선수 조건을 만족하지 않습니다.",
                    error_code="PREREQUISITES_NOT_MET"
                )
            
            # 사용자 진도 생성 또는 조회
            progress = UserLearningProgress.get_or_create(user_id, chapter_id)
            
            # 학습 시작 처리
            if progress.completion_status == 'not_started':
                progress.start_learning()
            
            # 초기 학습 루프 생성
            loop_id = str(uuid.uuid4())
            learning_loop = LearningLoop(
                loop_id=loop_id,
                user_id=user_id,
                chapter_id=chapter_id,
                loop_sequence=1,
                loop_status='active',
                started_at=datetime.utcnow()
            )
            learning_loop.save()
            
            logger.info(f"챕터 학습 시작 - user_id: {user_id}, chapter_id: {chapter_id}")
            
            return create_response(
                success=True,
                message="챕터 학습을 시작했습니다.",
                data={
                    'chapter': {
                        'chapter_id': chapter.chapter_id,
                        'title': chapter.title,
                        'description': chapter.description
                    },
                    'progress': {
                        'completion_status': progress.completion_status,
                        'progress_percentage': float(progress.progress_percentage)
                    },
                    'learning_loop': {
                        'loop_id': loop_id,
                        'started_at': learning_loop.started_at.isoformat()
                    },
                    'next_action': {
                        'type': 'start_theory',
                        'message': f"{chapter.title} 학습을 시작합니다. 개념 설명부터 시작하겠습니다."
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"챕터 학습 시작 중 오류: {str(e)}")
            return create_response(
                success=False,
                message="챕터 학습 시작 중 오류가 발생했습니다.",
                error_code="START_LEARNING_ERROR"
            )
    
    @staticmethod
    def _get_recommended_chapters(user_level: str, user_type: str) -> List[Dict[str, Any]]:
        """사용자 레벨과 타입에 따른 추천 챕터 목록"""
        # 기본 추천 챕터 (실제로는 데이터베이스에서 조회)
        all_chapters = [
            {'chapter_id': 1, 'title': 'AI는 무엇인가?', 'difficulty': 'low'},
            {'chapter_id': 2, 'title': 'AI의 역사와 발전', 'difficulty': 'low'},
            {'chapter_id': 3, 'title': '프롬프트란 무엇인가?', 'difficulty': 'medium'},
            {'chapter_id': 4, 'title': '효과적인 프롬프트 작성법', 'difficulty': 'medium'},
            {'chapter_id': 5, 'title': 'ChatGPT 실무 활용', 'difficulty': 'high'}
        ]
        
        if user_level == 'low':
            return [ch for ch in all_chapters if ch['difficulty'] in ['low']]
        elif user_level == 'medium':
            return [ch for ch in all_chapters if ch['difficulty'] in ['low', 'medium']]
        else:
            return all_chapters
    
    @staticmethod
    def _get_level_description(user_level: str) -> str:
        """사용자 레벨 설명"""
        descriptions = {
            'low': 'AI 초보자 - 기본 개념부터 차근차근 학습하시면 됩니다.',
            'medium': 'AI 중급자 - 기본 지식이 있으니 실용적인 활용법을 중심으로 학습하세요.',
            'high': 'AI 고급자 - 고급 기능과 실무 활용에 집중하여 학습하시면 좋겠습니다.'
        }
        return descriptions.get(user_level, '레벨을 확인할 수 없습니다.')
    
    @staticmethod
    def _get_type_description(user_type: str) -> str:
        """사용자 타입 설명"""
        descriptions = {
            'beginner': '입문자 과정 - AI의 기본 개념과 원리를 이해하는 데 중점을 둡니다.',
            'business': '실무자 과정 - 업무에서 바로 활용할 수 있는 실용적인 기술을 학습합니다.'
        }
        return descriptions.get(user_type, '타입을 확인할 수 없습니다.')