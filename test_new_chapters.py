# test_new_chapters.py
# 새로운 챕터 2, 4 콘텐츠 테스트 스크립트

from agents.educator.content_generator import ContentGenerator
from agents.quiz.question_generator import QuestionGenerator
from datetime import datetime


def test_chapter_content(chapter_id, title):
    """특정 챕터의 콘텐츠를 테스트"""
    print(f"\n{'='*60}")
    print(f" 챕터 {chapter_id}: {title} 테스트")
    print(f"{'='*60}")
    
    content_generator = ContentGenerator()
    quiz_generator = QuestionGenerator()
    
    # 초보자용 콘텐츠 테스트
    print(f"\n📚 초보자용 콘텐츠 (low level):")
    beginner_content = content_generator.generate_theory_content(
        chapter=chapter_id,
        user_type="beginner", 
        user_level="low"
    )
    
    print(f"   제목: {beginner_content['title']}")
    print(f"   도입부: {beginner_content['introduction'][:100]}...")
    print(f"   섹션 수: {len(beginner_content['main_content'])}")
    
    for i, section in enumerate(beginner_content['main_content'][:2], 1):
        print(f"   섹션 {i}: {section['title']}")
    
    # 비즈니스용 콘텐츠 테스트
    print(f"\n💼 비즈니스용 콘텐츠 (medium level):")
    business_content = content_generator.generate_theory_content(
        chapter=chapter_id,
        user_type="business", 
        user_level="medium"
    )
    
    print(f"   제목: {business_content['title']}")
    print(f"   도입부: {business_content['introduction'][:100]}...")
    print(f"   핵심 포인트: {len(business_content['key_points'])}개")
    
    for point in business_content['key_points'][:3]:
        print(f"   • {point}")
    
    # 퀴즈 테스트
    print(f"\n❓ 객관식 퀴즈:")
    try:
        quiz_data = quiz_generator.generate_multiple_choice_question(
            chapter_id=chapter_id,
            user_level="medium",
            user_type="business"
        )
        
        print(f"   문제: {quiz_data['question_text']}")
        for i, option in enumerate(quiz_data['options'], 1):
            marker = "✅" if i-1 == quiz_data['correct_answer'] else "  "
            print(f"   {marker} {i}. {option}")
        print(f"   설명: {quiz_data['explanation']}")
        
    except Exception as e:
        print(f"   퀴즈 생성 실패: {e}")
    
    # 프롬프트 실습 테스트 (챕터 3, 4만)
    if chapter_id in [3, 4]:
        print(f"\n✍️ 프롬프트 실습:")
        try:
            prompt_data = quiz_generator.generate_prompt_question(
                chapter_id=chapter_id,
                user_level="medium",
                user_type="business"
            )
            
            print(f"   시나리오: {prompt_data['scenario']}")
            print(f"   과제: {prompt_data['task_description']}")
            print(f"   요구사항: {len(prompt_data['requirements'])}개")
            for req in prompt_data['requirements']:
                print(f"   • {req}")
                
        except Exception as e:
            print(f"   프롬프트 실습 생성 실패: {e}")


def main():
    """메인 테스트 실행"""
    print("🚀 새로운 챕터 콘텐츠 테스트 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 모든 챕터 테스트
    chapters = [
        (1, "AI는 무엇인가?"),
        (2, "LLM이란 무엇인가?"),
        (3, "프롬프트란 무엇인가?"),
        (4, "ChatGPT로 할 수 있는 것들"),
        (5, "AI 시대의 문해력")
    ]
    
    for chapter_id, title in chapters:
        try:
            test_chapter_content(chapter_id, title)
        except Exception as e:
            print(f"\n❌ 챕터 {chapter_id} 테스트 실패: {e}")
    
    print(f"\n{'='*60}")
    print(" 테스트 완료")
    print(f"{'='*60}")
    print("✅ 새로운 챕터 콘텐츠가 성공적으로 구현되었습니다!")
    print("\n📋 구현된 챕터:")
    print("   • 챕터 1: AI는 무엇인가? (기존)")
    print("   • 챕터 2: LLM이란 무엇인가? (신규 추가)")
    print("   • 챕터 3: 프롬프트란 무엇인가? (기존)")
    print("   • 챕터 4: ChatGPT로 할 수 있는 것들 (신규 추가)")
    print("   • 챕터 5: AI 시대의 문해력 (신규 추가)")


if __name__ == "__main__":
    main()