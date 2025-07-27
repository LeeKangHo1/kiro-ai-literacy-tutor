# tests/unit/test_database_connection.py
"""
데이터베이스 연결 및 기본 기능 테스트
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import Config
from models import db, User, Chapter, LearningLoop, Conversation, QuizAttempt
from app import create_app


class TestDatabaseConnection:
    """데이터베이스 연결 테스트 클래스"""
    
    @pytest.fixture
    def app(self):
        """테스트용 Flask 앱 생성"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
        
        # SQLAlchemy 초기화
        db.init_app(app)
        
        with app.app_context():
            # 테스트 전에 모든 테이블 삭제 후 재생성
            db.drop_all()
            db.create_all()
            yield app
            # 테스트 후 정리
            db.session.rollback()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """테스트 클라이언트 생성"""
        return app.test_client()
    
    def test_database_url_configuration(self):
        """데이터베이스 URL 설정 테스트"""
        assert Config.DATABASE_URL is not None
        assert Config.DATABASE_URL.startswith('mysql://')
        print(f"✅ 데이터베이스 URL 설정 확인: {Config.DATABASE_URL}")
    
    def test_database_connection_basic(self, app):
        """기본 데이터베이스 연결 테스트"""
        try:
            with app.app_context():
                # SQLAlchemy 엔진을 통한 연결 테스트
                engine = create_engine(Config.DATABASE_URL)
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1 as test"))
                    assert result.fetchone()[0] == 1
                    print("✅ 데이터베이스 기본 연결 성공")
        except Exception as e:
            pytest.fail(f"❌ 데이터베이스 연결 실패: {str(e)}")
    
    def test_database_tables_exist(self, app):
        """데이터베이스 테이블 존재 확인 테스트"""
        try:
            with app.app_context():
                db.create_all()  # 테이블이 없으면 생성
                
                # 각 테이블 존재 확인
                tables_to_check = [
                    'users', 'chapters', 'user_learning_progress', 
                    'learning_loops', 'conversations', 'quiz_attempts'
                ]
                
                engine = create_engine(Config.DATABASE_URL)
                with engine.connect() as connection:
                    for table_name in tables_to_check:
                        result = connection.execute(text(f"""
                            SELECT COUNT(*) 
                            FROM information_schema.tables 
                            WHERE table_schema = DATABASE() 
                            AND table_name = '{table_name}'
                        """))
                        count = result.fetchone()[0]
                        assert count == 1, f"테이블 {table_name}이 존재하지 않습니다"
                        print(f"✅ 테이블 {table_name} 존재 확인")
                        
        except Exception as e:
            pytest.fail(f"❌ 테이블 존재 확인 실패: {str(e)}")
    
    def test_model_crud_operations(self, app):
        """모델 CRUD 기본 동작 테스트"""
        try:
            with app.app_context():
                db.create_all()
                
                # User 모델 테스트
                test_user = User(
                    username="test_user",
                    email="test@example.com",
                    password="password123",
                    user_type="beginner",
                    user_level="low"
                )
                
                # Create
                db.session.add(test_user)
                db.session.commit()
                print("✅ User 생성 성공")
                
                # Read
                found_user = User.query.filter_by(username="test_user").first()
                assert found_user is not None
                assert found_user.email == "test@example.com"
                print("✅ User 조회 성공")
                
                # Update
                found_user.user_level = "medium"
                db.session.commit()
                
                updated_user = User.query.filter_by(username="test_user").first()
                assert updated_user.user_level == "medium"
                print("✅ User 업데이트 성공")
                
                # Delete
                db.session.delete(found_user)
                db.session.commit()
                
                deleted_user = User.query.filter_by(username="test_user").first()
                assert deleted_user is None
                print("✅ User 삭제 성공")
                
        except Exception as e:
            pytest.fail(f"❌ 모델 CRUD 테스트 실패: {str(e)}")
        finally:
            # 테스트 데이터 정리
            with app.app_context():
                try:
                    db.session.rollback()
                except:
                    pass
    
    def test_chapter_model_operations(self, app):
        """Chapter 모델 기본 동작 테스트"""
        try:
            with app.app_context():
                db.create_all()
                
                # Chapter 생성 테스트
                test_chapter = Chapter(
                    chapter_number=1,
                    title="테스트 챕터",
                    description="테스트용 챕터 설명",
                    difficulty_level="low"
                )
                
                db.session.add(test_chapter)
                db.session.commit()
                
                # 조회 테스트
                found_chapter = Chapter.query.filter_by(title="테스트 챕터").first()
                assert found_chapter is not None
                assert found_chapter.chapter_number == 1
                print("✅ Chapter 모델 동작 확인")
                
                # 정리
                db.session.delete(found_chapter)
                db.session.commit()
                
        except Exception as e:
            pytest.fail(f"❌ Chapter 모델 테스트 실패: {str(e)}")
        finally:
            with app.app_context():
                try:
                    db.session.rollback()
                except:
                    pass
    
    def test_database_connection_error_handling(self):
        """데이터베이스 연결 오류 처리 테스트"""
        # 잘못된 데이터베이스 URL로 연결 시도
        invalid_url = "mysql://invalid:invalid@localhost:3306/invalid_db"
        
        try:
            engine = create_engine(invalid_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            pytest.fail("잘못된 연결에서 예외가 발생해야 합니다")
        except SQLAlchemyError:
            print("✅ 잘못된 데이터베이스 연결에 대한 오류 처리 확인")
        except Exception as e:
            print(f"✅ 예상된 연결 오류 발생: {type(e).__name__}")
    
    def test_database_transaction_rollback(self, app):
        """데이터베이스 트랜잭션 롤백 테스트"""
        try:
            with app.app_context():
                db.create_all()
                
                # 트랜잭션 시작
                test_user = User(
                    username="rollback_test",
                    email="rollback@example.com",
                    password="password123",
                    user_type="beginner",
                    user_level="low"
                )
                
                db.session.add(test_user)
                # 커밋하지 않고 롤백
                db.session.rollback()
                
                # 롤백 후 데이터가 없는지 확인
                found_user = User.query.filter_by(username="rollback_test").first()
                assert found_user is None
                print("✅ 트랜잭션 롤백 동작 확인")
                
        except Exception as e:
            pytest.fail(f"❌ 트랜잭션 롤백 테스트 실패: {str(e)}")


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])