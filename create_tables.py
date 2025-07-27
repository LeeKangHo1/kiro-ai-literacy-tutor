# create_tables.py
"""
데이터베이스 테이블 생성 스크립트
"""

from app import create_app
from models import db

def create_tables():
    """데이터베이스 테이블 생성"""
    app = create_app()
    
    # SQLAlchemy 초기화
    db.init_app(app)
    
    with app.app_context():
        print("데이터베이스 테이블 생성 중...")
        
        # 모든 테이블 생성
        db.create_all()
        
        print("✅ 데이터베이스 테이블 생성 완료!")
        
        # 생성된 테이블 확인
        from sqlalchemy import text
        result = db.session.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        
        print("\n📋 생성된 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print(f"\n총 {len(tables)}개의 테이블이 생성되었습니다.")

if __name__ == "__main__":
    create_tables()