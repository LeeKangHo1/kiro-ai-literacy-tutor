# tests/integration/test_workflow.py
"""
LangGraph 워크플로우 통합 테스트
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from workflow.graph_builder import create_workflow_graph
from workflow.state_management import TutorState
from models import db, User, Chapter, LearningLoop
from app import create_app
from config import Config


class TestWorkflowIntegration:
    """워크플로우 통합 테스트 클래스"""
    
    @pytest.fixture
    def app(self):
        """테스트용 Flask 앱 생성"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.rollback()
            db.drop_all()
    
    @pytest.fixture
    def sample_state(self, app):
        """테스트용 상태 생성"""
        with app.app_context():
            # 테스트 사용자와 챕터 생성
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password",
                level="beginner"
            )
            
            chapter = Chapter(
                title="AI 기초",
                description="AI의 기본 개념",
                order_index=1,
                content="AI 기초 내용"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            # 학습 루프 생성
            loop = LearningLoop(
                user_id=user.id,
                chapter_id=chapter.id,
                loop_number=1,
                status="active"
            )
            db.session.add(loop)
            db.session.commit()
            
            # TutorState 생성
            state = TutorState(
                user_id=user.id,
                chapter_id=chapter.id,
                current_loop_id=loop.id,
                user_level="beginner",
                messages=[
                    {
                        'type': 'user',
                        'content': 'AI가 무엇인가요?',
                        'timestamp': '2024-01-01T10:00:00Z'
                    }
                ],
                ui_mode="chat",
                current_agent="learning_supervisor"
            )
            
            return state
    
    @patch('agents.supervisor.progress_analyzer.ProgressAnalyzer.analyze_progress')
    @patch('agents.supervisor.decision_maker.DecisionMaker.decide_next_step')
    def test_learning_supervisor_workflow(self, mock_decide, mock_analyze, app, sample_state):
        """LearningSupervisor 워크플로우 테스트"""
        # Mock 설정
        mock_analyze.return_value = {
            'progress_percentage': 30.0,
            'understanding_score': 60.0,
            'completed_loops': 1,
            'needs_review': False
        }
        
        mock_decide.return_value = {
            'next_action': 'theory_education',
            'reason': '새로운 개념 학습 필요',
            'confidence': 0.9
        }
        
        with app.app_context():
            # 워크플로우 그래프 생성
            workflow = create_workflow_graph()
            
            # 워크플로우 실행
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            assert 'current_agent' in result
            assert 'messages' in result
            
            print("✅ LearningSupervisor 워크플로우 테스트 통과")
    
    @patch('agents.educator.content_generator.ContentGenerator.generate_content')
    @patch('agents.educator.level_adapter.LevelAdapter.adapt_content')
    def test_theory_educator_workflow(self, mock_adapt, mock_generate, app, sample_state):
        """TheoryEducator 워크플로우 테스트"""
        # Mock 설정
        mock_generate.return_value = {
            'content': 'AI는 인공지능을 의미합니다...',
            'content_type': 'theory',
            'difficulty_level': 'intermediate'
        }
        
        mock_adapt.return_value = {
            'adapted_content': '초보자를 위한 AI 설명...',
            'target_level': 'beginner'
        }
        
        with app.app_context():
            # 상태를 theory_educator로 설정
            sample_state['current_agent'] = 'theory_educator'
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            assert len(result['messages']) > len(sample_state['messages'])
            
            # AI 응답이 추가되었는지 확인
            ai_messages = [msg for msg in result['messages'] if msg['type'] == 'ai']
            assert len(ai_messages) > 0
            
            print("✅ TheoryEducator 워크플로우 테스트 통과")
    
    @patch('agents.quiz.question_generator.QuestionGenerator.generate_question')
    def test_quiz_generator_workflow(self, mock_generate, app, sample_state):
        """QuizGenerator 워크플로우 테스트"""
        # Mock 설정
        mock_generate.return_value = {
            'question': 'AI의 정의는 무엇인가요?',
            'question_type': 'multiple_choice',
            'options': ['A) 인공지능', 'B) 자동화', 'C) 로봇', 'D) 컴퓨터'],
            'correct_answer': 'A) 인공지능',
            'difficulty': 'beginner'
        }
        
        with app.app_context():
            # 상태를 quiz_generator로 설정
            sample_state['current_agent'] = 'quiz_generator'
            sample_state['messages'].append({
                'type': 'user',
                'content': '문제를 내주세요',
                'timestamp': '2024-01-01T10:01:00Z'
            })
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            assert result['ui_mode'] == 'quiz'
            
            # 퀴즈 메시지가 추가되었는지 확인
            quiz_messages = [msg for msg in result['messages'] 
                           if msg['type'] == 'quiz']
            assert len(quiz_messages) > 0
            
            print("✅ QuizGenerator 워크플로우 테스트 통과")
    
    @patch('agents.evaluator.answer_evaluator.AnswerEvaluator.evaluate_answer')
    @patch('agents.evaluator.feedback_generator.FeedbackGenerator.generate_feedback')
    def test_evaluation_feedback_workflow(self, mock_feedback, mock_evaluate, app, sample_state):
        """EvaluationFeedbackAgent 워크플로우 테스트"""
        # Mock 설정
        mock_evaluate.return_value = {
            'is_correct': True,
            'score': 95.0,
            'understanding_level': 'excellent',
            'detailed_feedback': '정확한 답변입니다.'
        }
        
        mock_feedback.return_value = {
            'feedback_message': '훌륭합니다! 정확한 답변이에요.',
            'encouragement': '계속 이런 식으로 학습하세요.',
            'next_steps': '다음 개념으로 넘어가볼까요?',
            'tone': 'positive'
        }
        
        with app.app_context():
            # 상태를 evaluation_feedback로 설정
            sample_state['current_agent'] = 'evaluation_feedback'
            sample_state['quiz_data'] = {
                'question': 'AI의 정의는?',
                'correct_answer': '인공지능'
            }
            sample_state['messages'].append({
                'type': 'user',
                'content': '인공지능',
                'timestamp': '2024-01-01T10:02:00Z'
            })
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            
            # 피드백 메시지가 추가되었는지 확인
            feedback_messages = [msg for msg in result['messages'] 
                               if msg['type'] == 'feedback']
            assert len(feedback_messages) > 0
            
            print("✅ EvaluationFeedbackAgent 워크플로우 테스트 통과")
    
    @patch('agents.qna.search_handler.SearchHandler.search_knowledge')
    @patch('agents.qna.context_integrator.ContextIntegrator.integrate_context')
    def test_qna_resolver_workflow(self, mock_integrate, mock_search, app, sample_state):
        """QnAResolver 워크플로우 테스트"""
        # Mock 설정
        mock_search.return_value = {
            'results': [
                {'content': 'AI 관련 정보 1', 'score': 0.9},
                {'content': 'AI 관련 정보 2', 'score': 0.8}
            ],
            'total_results': 2
        }
        
        mock_integrate.return_value = {
            'integrated_answer': 'AI는 인공지능으로...',
            'context_sources': ['knowledge_base'],
            'confidence': 0.85
        }
        
        with app.app_context():
            # 상태를 qna_resolver로 설정
            sample_state['current_agent'] = 'qna_resolver'
            sample_state['messages'].append({
                'type': 'user',
                'content': 'AI에 대해 더 자세히 알려주세요',
                'timestamp': '2024-01-01T10:03:00Z'
            })
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            
            # QnA 응답이 추가되었는지 확인
            qna_messages = [msg for msg in result['messages'] 
                          if msg['type'] == 'ai' and msg.get('agent_type') == 'qna_resolver']
            assert len(qna_messages) > 0
            
            print("✅ QnAResolver 워크플로우 테스트 통과")
    
    @patch('routers.post_theory_router.PostTheoryRouter.route_user_intent')
    def test_post_theory_router_workflow(self, mock_route, app, sample_state):
        """PostTheoryRouter 워크플로우 테스트"""
        # Mock 설정
        mock_route.return_value = {
            'next_agent': 'quiz_generator',
            'routing_reason': '사용자가 문제 요청',
            'confidence': 0.9
        }
        
        with app.app_context():
            # 상태를 post_theory_router로 설정
            sample_state['current_agent'] = 'post_theory_router'
            sample_state['messages'].append({
                'type': 'user',
                'content': '이제 문제를 풀어보고 싶어요',
                'timestamp': '2024-01-01T10:04:00Z'
            })
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            assert result['current_agent'] == 'quiz_generator'
            
            print("✅ PostTheoryRouter 워크플로우 테스트 통과")
    
    @patch('routers.post_feedback_router.PostFeedbackRouter.route_user_intent')
    def test_post_feedback_router_workflow(self, mock_route, app, sample_state):
        """PostFeedbackRouter 워크플로우 테스트"""
        # Mock 설정
        mock_route.return_value = {
            'next_agent': 'learning_supervisor',
            'routing_reason': '사용자가 다음 단계 요청',
            'confidence': 0.85
        }
        
        with app.app_context():
            # 상태를 post_feedback_router로 설정
            sample_state['current_agent'] = 'post_feedback_router'
            sample_state['messages'].append({
                'type': 'user',
                'content': '다음으로 넘어가주세요',
                'timestamp': '2024-01-01T10:05:00Z'
            })
            
            workflow = create_workflow_graph()
            result = workflow.invoke(sample_state)
            
            # 결과 검증
            assert result is not None
            assert result['current_agent'] == 'learning_supervisor'
            
            print("✅ PostFeedbackRouter 워크플로우 테스트 통과")
    
    def test_complete_learning_loop_workflow(self, app, sample_state):
        """완전한 학습 루프 워크플로우 테스트"""
        with app.app_context():
            # 여러 에이전트를 거치는 완전한 워크플로우 시뮬레이션
            with patch.multiple(
                'agents.supervisor.progress_analyzer.ProgressAnalyzer',
                analyze_progress=MagicMock(return_value={
                    'progress_percentage': 25.0,
                    'understanding_score': 70.0
                })
            ), patch.multiple(
                'agents.supervisor.decision_maker.DecisionMaker',
                decide_next_step=MagicMock(return_value={
                    'next_action': 'theory_education',
                    'reason': '새로운 개념 학습'
                })
            ), patch.multiple(
                'agents.educator.content_generator.ContentGenerator',
                generate_content=MagicMock(return_value={
                    'content': 'AI 이론 설명...',
                    'content_type': 'theory'
                })
            ):
                workflow = create_workflow_graph()
                
                # 초기 상태로 워크플로우 시작
                result = workflow.invoke(sample_state)
                
                # 결과 검증
                assert result is not None
                assert 'messages' in result
                assert len(result['messages']) >= len(sample_state['messages'])
                
                print("✅ 완전한 학습 루프 워크플로우 테스트 통과")
    
    def test_workflow_state_persistence(self, app, sample_state):
        """워크플로우 상태 지속성 테스트"""
        with app.app_context():
            workflow = create_workflow_graph()
            
            # 첫 번째 실행
            with patch('agents.supervisor.decision_maker.DecisionMaker.decide_next_step') as mock_decide:
                mock_decide.return_value = {
                    'next_action': 'theory_education',
                    'reason': '이론 학습 필요'
                }
                
                result1 = workflow.invoke(sample_state)
                
                # 상태가 업데이트되었는지 확인
                assert result1['current_agent'] != sample_state['current_agent']
                
                # 두 번째 실행 (업데이트된 상태로)
                result2 = workflow.invoke(result1)
                
                # 상태가 지속되고 발전했는지 확인
                assert len(result2['messages']) >= len(result1['messages'])
                
                print("✅ 워크플로우 상태 지속성 테스트 통과")
    
    def test_workflow_error_handling(self, app, sample_state):
        """워크플로우 오류 처리 테스트"""
        with app.app_context():
            workflow = create_workflow_graph()
            
            # 에이전트에서 예외 발생 시뮬레이션
            with patch('agents.supervisor.decision_maker.DecisionMaker.decide_next_step') as mock_decide:
                mock_decide.side_effect = Exception("에이전트 오류")
                
                try:
                    result = workflow.invoke(sample_state)
                    # 오류가 적절히 처리되었는지 확인
                    assert result is not None
                    # 오류 메시지가 포함되었는지 확인
                    error_messages = [msg for msg in result.get('messages', []) 
                                    if 'error' in msg.get('content', '').lower()]
                    assert len(error_messages) > 0 or 'error' in result
                    
                except Exception as e:
                    # 예외가 발생했다면 적절한 예외인지 확인
                    assert "에이전트 오류" in str(e)
                
                print("✅ 워크플로우 오류 처리 테스트 통과")
    
    def test_workflow_performance(self, app, sample_state):
        """워크플로우 성능 테스트"""
        import time
        
        with app.app_context():
            workflow = create_workflow_graph()
            
            # 간단한 Mock으로 빠른 응답 설정
            with patch('agents.supervisor.decision_maker.DecisionMaker.decide_next_step') as mock_decide:
                mock_decide.return_value = {
                    'next_action': 'theory_education',
                    'reason': '빠른 응답'
                }
                
                start_time = time.time()
                result = workflow.invoke(sample_state)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # 실행 시간이 합리적인 범위 내인지 확인 (5초 이내)
                assert execution_time < 5.0
                assert result is not None
                
                print(f"✅ 워크플로우 성능 테스트 통과 (실행 시간: {execution_time:.2f}초)")


class TestWorkflowStateManagement:
    """워크플로우 상태 관리 테스트"""
    
    def test_tutor_state_validation(self):
        """TutorState 유효성 검사 테스트"""
        # 유효한 상태 생성
        valid_state = TutorState(
            user_id=1,
            chapter_id=1,
            current_loop_id=1,
            user_level="beginner",
            messages=[],
            ui_mode="chat",
            current_agent="learning_supervisor"
        )
        
        assert valid_state['user_id'] == 1
        assert valid_state['user_level'] == "beginner"
        assert valid_state['ui_mode'] == "chat"
        
        print("✅ TutorState 유효성 검사 테스트 통과")
    
    def test_state_message_management(self):
        """상태 메시지 관리 테스트"""
        state = TutorState(
            user_id=1,
            chapter_id=1,
            current_loop_id=1,
            user_level="beginner",
            messages=[],
            ui_mode="chat",
            current_agent="learning_supervisor"
        )
        
        # 메시지 추가
        state['messages'].append({
            'type': 'user',
            'content': '안녕하세요',
            'timestamp': '2024-01-01T10:00:00Z'
        })
        
        state['messages'].append({
            'type': 'ai',
            'content': '안녕하세요! 무엇을 도와드릴까요?',
            'agent_type': 'learning_supervisor',
            'timestamp': '2024-01-01T10:00:01Z'
        })
        
        assert len(state['messages']) == 2
        assert state['messages'][0]['type'] == 'user'
        assert state['messages'][1]['type'] == 'ai'
        
        print("✅ 상태 메시지 관리 테스트 통과")
    
    def test_state_ui_mode_transitions(self):
        """상태 UI 모드 전환 테스트"""
        state = TutorState(
            user_id=1,
            chapter_id=1,
            current_loop_id=1,
            user_level="beginner",
            messages=[],
            ui_mode="chat",
            current_agent="learning_supervisor"
        )
        
        # UI 모드 전환
        state['ui_mode'] = "quiz"
        assert state['ui_mode'] == "quiz"
        
        state['ui_mode'] = "feedback"
        assert state['ui_mode'] == "feedback"
        
        state['ui_mode'] = "chat"
        assert state['ui_mode'] == "chat"
        
        print("✅ 상태 UI 모드 전환 테스트 통과")


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])