# insert_initial_data.py
"""
초기 데이터 삽입 스크립트
"""

from app import create_app
from models import db, Chapter
import json

def insert_initial_data():
    """초기 챕터 데이터 삽입"""
    app = create_app()
    db.init_app(app)
    
    with app.app_context():
        print("초기 데이터 삽입 중...")
        
        # 기존 챕터가 있는지 확인
        existing_chapters = Chapter.query.count()
        if existing_chapters > 0:
            print(f"이미 {existing_chapters}개의 챕터가 존재합니다.")
            return
        
        # 초기 챕터 데이터
        chapters_data = [
            {
                'chapter_number': 1,
                'title': 'AI는 무엇인가?',
                'description': 'AI, ML, DL의 개념과 차이점을 학습합니다.',
                'difficulty_level': 'low',
                'estimated_duration': 30,
                'learning_objectives': {
                    'objectives': ['AI의 정의 이해', 'ML과 DL의 차이점 구분', '실생활 AI 사례 파악']
                }
            },
            {
                'chapter_number': 2,
                'title': '머신러닝의 기초',
                'description': '머신러닝의 기본 개념과 종류를 학습합니다.',
                'difficulty_level': 'medium',
                'estimated_duration': 45,
                'learning_objectives': {
                    'objectives': ['지도학습과 비지도학습 구분', '머신러닝 알고리즘 종류 이해', '데이터의 중요성 인식']
                }
            },
            {
                'chapter_number': 3,
                'title': '프롬프트란 무엇인가?',
                'description': '효과적인 프롬프트 작성법을 학습합니다.',
                'difficulty_level': 'medium',
                'estimated_duration': 40,
                'learning_objectives': {
                    'objectives': ['프롬프트 구조 이해', '효과적인 프롬프트 작성법 습득', 'ChatGPT API 활용 실습']
                }
            },
            {
                'chapter_number': 4,
                'title': 'AI 윤리와 한계',
                'description': 'AI의 윤리적 고려사항과 한계를 학습합니다.',
                'difficulty_level': 'high',
                'estimated_duration': 35,
                'learning_objectives': {
                    'objectives': ['AI 편향성 이해', '개인정보 보호 중요성 인식', 'AI 한계점 파악']
                }
            }
        ]
        
        # 챕터 생성 및 저장
        for chapter_data in chapters_data:
            chapter = Chapter(
                chapter_number=chapter_data['chapter_number'],
                title=chapter_data['title'],
                description=chapter_data['description'],
                difficulty_level=chapter_data['difficulty_level'],
                estimated_duration=chapter_data['estimated_duration'],
                learning_objectives=chapter_data['learning_objectives']
            )
            db.session.add(chapter)
        
        db.session.commit()
        
        print("✅ 초기 챕터 데이터 삽입 완료!")
        
        # 삽입된 챕터 확인
        chapters = Chapter.query.order_by(Chapter.chapter_number).all()
        print(f"\n📚 삽입된 챕터 목록:")
        for chapter in chapters:
            print(f"  {chapter.chapter_number}. {chapter.title} ({chapter.difficulty_level})")
        
        print(f"\n총 {len(chapters)}개의 챕터가 삽입되었습니다.")

if __name__ == "__main__":
    insert_initial_data()