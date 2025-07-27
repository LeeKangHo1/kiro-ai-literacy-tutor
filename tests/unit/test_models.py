# tests/unit/test_models.py
"""
SQLAlchemy 모델 단위 테스트
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from models import db, User, Chapter, UserLearningProgress, LearningLoop, Conversation, QuizAttempt
from config import Config


class TestModels:
    """모델 테스트 클래스"""
    
    @pytest.fixture
    def app(self):
        """테스트용 Flask 앱 생성"""
        from flask import Flask
        import uuid
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        # 각 테스트마다 고유한 메모리 DB 사용
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///:memory:?cache=shared&uri=true&test_id={uuid.uuid4().hex}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # SQLAlchemy 초기화
        db.init_app(app)
        
        with app.app_context():
            try:
                db.create_all()
                yield app
            finally:
                db.session.rollback()
                try:
                    db.drop_all()
                except:
                    pass  # 이미 삭제된 경우 무시
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트 생성"""
        return app.test_client()
    
    def test_user_model_creation(self, app):
        """User 모델 생성 테스트"""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                password="password123",
                user_type="beginner",
                user_level="low"
            )
            
            db.session.add(user)
            db.session.commit()
            
            # 검증
            saved_user = User.query.filter_by(username="testuser").first()
            assert saved_user is not None
            assert saved_user.email == "test@example.com"
            assert saved_user.user_type == "beginner"
            assert saved_user.user_level == "low"
            assert saved_user.created_at is not None
            print("✅ User 모델 생성 테스트 통과")
    
    def test_user_model_validation(self, app):
        """User 모델 유효성 검사 테스트"""
        with app.app_context():
            # 필수 필드 누락 테스트 - User 모델은 필수 인자가 있음
            try:
                user = User()  # 필수 인자 없이 생성 시도
                pytest.fail("필수 인자 없이 User 생성이 성공하면 안됩니다")
            except TypeError:
                # 예상된 동작: 필수 인자가 없으면 TypeError 발생
                pass
            
            print("✅ User 모델 유효성 검사 테스트 통과")
    
    def test_chapter_model_creation(self, app):
        """Chapter 모델 생성 테스트"""
        with app.app_context():
            chapter = Chapter(
                chapter_number=1,
                title="AI 기초",
                description="인공지능의 기본 개념",
                difficulty_level="low"
            )
            
            db.session.add(chapter)
            db.session.commit()
            
            # 검증
            saved_chapter = Chapter.query.filter_by(title="AI 기초").first()
            assert saved_chapter is not None
            assert saved_chapter.chapter_number == 1
            assert saved_chapter.created_at is not None
            print("✅ Chapter 모델 생성 테스트 통과")
    
    def test_user_learning_progress_model(self, app):
        """UserLearningProgress 모델 테스트"""
        with app.app_context():
            # 사용자와 챕터 생성
            user = User(
                username="progressuser",
                email="progress@example.com",
                password="password123",
                user_type="beginner",
                user_level="low"
            )
            
            chapter = Chapter(
                chapter_number=1,
                title="진도 테스트 챕터",
                description="진도 테스트용",
                difficulty_level="low"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            # 학습 진도 생성
            progress = UserLearningProgress(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                progress_percentage=50.0,
                understanding_score=75.0
            )
            
            db.session.add(progress)
            db.session.commit()
            
            # 검증
            saved_progress = UserLearningProgress.query.filter_by(user_id=user.user_id).first()
            assert saved_progress is not None
            assert saved_progress.progress_percentage == 50.0
            assert saved_progress.understanding_score == 75.0
            print("✅ UserLearningProgress 모델 테스트 통과")
    
    def test_learning_loop_model(self, app):
        """LearningLoop 모델 테스트"""
        with app.app_context():
            # 사용자와 챕터 생성
            user = User(
                username="loopuser",
                email="loop@example.com",
                password="password123",
                user_type="beginner"
            )
            
            chapter = Chapter(
                chapter_number=1,
                title="루프 테스트 챕터",
                description="루프 테스트용",
                difficulty_level="low"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            # 학습 루프 생성
            loop = LearningLoop(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                loop_type="mixed"
            )
            
            db.session.add(loop)
            db.session.commit()
            
            # 검증
            saved_loop = LearningLoop.query.filter_by(user_id=user.user_id).first()
            assert saved_loop is not None
            assert saved_loop.loop_sequence == 1
            assert saved_loop.loop_status == "active"
            assert saved_loop.loop_type == "mixed"
            print("✅ LearningLoop 모델 테스트 통과")
    
    def test_conversation_model(self, app):
        """Conversation 모델 테스트"""
        with app.app_context():
            # 사용자와 루프 생성
            user = User(
                username="chatuser",
                email="chat@example.com",
                password="password123",
                user_type="beginner"
            )
            
            chapter = Chapter(
                chapter_number=1,
                title="대화 테스트 챕터",
                description="대화 테스트용",
                difficulty_level="low"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            loop = LearningLoop(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                loop_type="mixed"
            )
            
            db.session.add(loop)
            db.session.commit()
            
            # 대화 생성
            conversation = Conversation(
                loop_id=loop.loop_id,
                agent_name="TheoryEducator",
                message_type="user",
                sequence_order=1,
                user_message="AI가 무엇인가요?"
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            # 검증
            saved_conversation = Conversation.query.filter_by(loop_id=loop.loop_id).first()
            assert saved_conversation is not None
            assert saved_conversation.message_type == "user"
            assert saved_conversation.user_message == "AI가 무엇인가요?"
            assert saved_conversation.agent_name == "TheoryEducator"
            print("✅ Conversation 모델 테스트 통과")
    
    def test_quiz_attempt_model(self, app):
        """QuizAttempt 모델 테스트"""
        with app.app_context():
            # 사용자와 루프 생성
            user = User(
                username="quizuser",
                email="quiz@example.com",
                password="password123",
                user_type="beginner"
            )
            
            chapter = Chapter(
                chapter_number=1,
                title="퀴즈 테스트 챕터",
                description="퀴즈 테스트용",
                difficulty_level="low"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            loop = LearningLoop(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                loop_type="quiz"
            )
            
            db.session.add(loop)
            db.session.commit()
            
            # 퀴즈 시도 생성
            quiz_attempt = QuizAttempt(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                loop_id=loop.loop_id,
                quiz_type="multiple_choice",
                question_content={"question": "AI의 정의는 무엇인가요?", "options": ["인공지능", "자동화", "로봇", "컴퓨터"]},
                difficulty_level="low",
                user_answer="인공지능",
                correct_answer="인공지능",
                hint_used=False
            )
            
            db.session.add(quiz_attempt)
            db.session.commit()
            
            # 검증
            saved_attempt = QuizAttempt.query.filter_by(loop_id=loop.loop_id).first()
            assert saved_attempt is not None
            assert saved_attempt.quiz_type == "multiple_choice"
            assert saved_attempt.user_answer == "인공지능"
            assert saved_attempt.hint_used == False
            print("✅ QuizAttempt 모델 테스트 통과")
    
    def test_model_relationships(self, app):
        """모델 간 관계 테스트"""
        with app.app_context():
            # 사용자와 챕터 생성
            user = User(
                username="relationuser",
                email="relation@example.com",
                password="password123",
                user_type="beginner"
            )
            
            chapter = Chapter(
                chapter_number=1,
                title="관계 테스트 챕터",
                description="관계 테스트용",
                difficulty_level="low"
            )
            
            db.session.add(user)
            db.session.add(chapter)
            db.session.commit()
            
            # 학습 루프 생성
            loop = LearningLoop(
                user_id=user.user_id,
                chapter_id=chapter.chapter_id,
                loop_type="mixed"
            )
            
            db.session.add(loop)
            db.session.commit()
            
            # 관계 검증
            assert loop.user_id == user.user_id
            assert loop.chapter_id == chapter.chapter_id
            
            # 백레퍼런스 관계 테스트 (관계가 설정되어 있다면)
            user_loops = user.learning_loops.all()
            assert len(user_loops) == 1
            assert user_loops[0].loop_id == loop.loop_id
            
            print("✅ 모델 관계 테스트 통과")
    
    def test_model_timestamps(self, app):
        """모델 타임스탬프 테스트"""
        with app.app_context():
            user = User(
                username="timestampuser",
                email="timestamp@example.com",
                password="password123",
                user_type="beginner"
            )
            
            before_creation = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            after_creation = datetime.utcnow()
            
            # created_at이 올바른 시간 범위에 있는지 확인
            assert before_creation <= user.created_at <= after_creation
            
            # updated_at 테스트
            original_updated = user.updated_at
            
            # 사용자 정보 업데이트
            user.user_level = "medium"
            db.session.commit()
            
            # updated_at이 변경되었는지 확인
            assert user.updated_at >= original_updated
            
            print("✅ 모델 타임스탬프 테스트 통과")


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])