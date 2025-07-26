# demo_ui_system.py
# UI 모드 관리 시스템 데모 스크립트

import json
from datetime import datetime
from services.ui_mode_service import (
    UIModeManager, UIMode, UIStateSerializer, get_ui_mode_manager
)
from services.agent_ui_service import (
    AgentUIGenerator, UIStateTransitionManager,
    get_agent_ui_generator, get_ui_transition_manager
)
from workflow.state_management import StateManager, TutorState
from agents.educator.content_generator import ContentGenerator
from agents.quiz.question_generator import QuestionGenerator


def print_separator(title):
    """구분선 출력"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_ui_state(ui_state, title="UI 상태"):
    """UI 상태를 보기 좋게 출력"""
    print(f"\n📱 {title}:")
    print(f"   모드: {ui_state.mode.value}")
    print(f"   상호작용 타입: {ui_state.interaction_type.value}")
    print(f"   제목: {ui_state.title}")
    print(f"   설명: {ui_state.description}")
    print(f"   레이아웃: {ui_state.layout}")
    print(f"   UI 요소 개수: {len(ui_state.elements)}")
    
    if ui_state.elements:
        print("   UI 요소들:")
        for i, element in enumerate(ui_state.elements, 1):
            print(f"     {i}. {element.element_type} - {element.label} (ID: {element.element_id})")


def demo_basic_ui_modes():
    """기본 UI 모드 데모"""
    print_separator("1. 기본 UI 모드 데모")
    
    ui_manager = UIModeManager()
    print(f"초기 모드: {ui_manager.current_mode.value}")
    
    # 채팅 모드
    chat_ui = ui_manager.switch_mode(UIMode.CHAT, {
        'title': 'AI 학습 튜터',
        'description': '자유롭게 질문해보세요'
    })
    print_ui_state(chat_ui, "채팅 모드")
    
    # 퀴즈 모드
    quiz_ui = ui_manager.switch_mode(UIMode.QUIZ, {
        'quiz_type': 'multiple_choice',
        'question': 'AI의 정의는 무엇인가요?',
        'options': ['인공지능', '자동화 시스템', '데이터베이스', '프로그래밍 언어'],
        'hint_available': True
    })
    print_ui_state(quiz_ui, "퀴즈 모드")
    
    # 오류 모드
    error_ui = ui_manager.switch_mode(UIMode.ERROR, {
        'error_message': '네트워크 연결 오류가 발생했습니다.'
    })
    print_ui_state(error_ui, "오류 모드")
    
    # 이전 모드로 되돌리기
    previous_ui = ui_manager.revert_to_previous_mode()
    print_ui_state(previous_ui, "이전 모드로 복원")


def demo_agent_specific_ui():
    """에이전트별 UI 생성 데모"""
    print_separator("2. 에이전트별 UI 생성 데모")
    
    # 테스트 상태 생성
    test_state = StateManager.create_initial_state("demo_user", "beginner", "low")
    test_state['current_chapter'] = 1
    test_state['user_message'] = "AI에 대해 설명해주세요"
    
    ui_generator = get_agent_ui_generator()
    
    # TheoryEducator UI
    theory_ui = ui_generator.generate_ui_for_agent("theory_educator", test_state)
    print_ui_state(theory_ui, "TheoryEducator UI")
    
    # QuizGenerator UI
    quiz_context = {
        'quiz_type': 'multiple_choice',
        'question': 'AI와 ML의 차이점은?',
        'options': ['AI가 더 넓은 개념', 'ML이 더 넓은 개념', '같은 개념', '관련 없음']
    }
    quiz_ui = ui_generator.generate_ui_for_agent("quiz_generator", test_state, quiz_context)
    print_ui_state(quiz_ui, "QuizGenerator UI")
    
    # PostTheoryRouter UI
    router_ui = ui_generator.generate_ui_for_agent("post_theory_router", test_state)
    print_ui_state(router_ui, "PostTheoryRouter UI")
    
    # QnAResolver UI
    qna_ui = ui_generator.generate_ui_for_agent("qna_resolver", test_state)
    print_ui_state(qna_ui, "QnAResolver UI")


def demo_ui_transitions():
    """UI 전환 데모"""
    print_separator("3. UI 전환 시스템 데모")
    
    test_state = StateManager.create_initial_state("demo_user", "business", "medium")
    transition_manager = get_ui_transition_manager()
    
    # 사용자 입력 수신
    loading_ui = transition_manager.handle_transition(
        "user_input_received", "theory_educator", test_state
    )
    print_ui_state(loading_ui, "사용자 입력 수신 → 로딩 상태")
    
    # 에이전트 응답 준비 완료
    response_ui = transition_manager.handle_transition(
        "agent_response_ready", "theory_educator", test_state, 
        {'title': 'AI 기초 개념', 'show_progress': True}
    )
    print_ui_state(response_ui, "에이전트 응답 준비 → 채팅 모드")
    
    # 퀴즈 제출
    quiz_submit_ui = transition_manager.handle_transition(
        "quiz_submitted", "quiz_generator", test_state
    )
    print_ui_state(quiz_submit_ui, "퀴즈 제출 → 로딩 상태")
    
    # 오류 발생
    error_ui = transition_manager.handle_transition(
        "error_occurred", "system", test_state,
        {'error_message': '서버 연결 실패'}
    )
    print_ui_state(error_ui, "오류 발생 → 오류 모드")


def demo_serialization():
    """UI 상태 직렬화 데모"""
    print_separator("4. UI 상태 직렬화 데모")
    
    ui_manager = UIModeManager()
    
    # 복잡한 UI 상태 생성
    complex_ui = ui_manager.switch_mode(UIMode.QUIZ, {
        'quiz_type': 'prompt_practice',
        'question': '고객 서비스 챗봇을 위한 프롬프트를 작성하세요',
        'requirements': ['친근한 톤', '문제 해결 중심', '추가 도움 제안'],
        'hint_available': True
    })
    
    print_ui_state(complex_ui, "원본 UI 상태")
    
    # 직렬화
    serialized = UIStateSerializer.serialize_ui_state(complex_ui)
    print(f"\n📄 직렬화된 데이터 (JSON):")
    print(json.dumps(serialized, indent=2, ensure_ascii=False))
    
    # 역직렬화
    deserialized_ui = UIStateSerializer.deserialize_ui_state(serialized)
    print_ui_state(deserialized_ui, "역직렬화된 UI 상태")
    
    # 검증
    print(f"\n✅ 직렬화/역직렬화 검증:")
    print(f"   모드 일치: {complex_ui.mode == deserialized_ui.mode}")
    print(f"   제목 일치: {complex_ui.title == deserialized_ui.title}")
    print(f"   요소 개수 일치: {len(complex_ui.elements) == len(deserialized_ui.elements)}")


def demo_content_integration():
    """콘텐츠 생성과 UI 통합 데모"""
    print_separator("5. 콘텐츠 생성과 UI 통합 데모")
    
    # 챕터 2 이론 콘텐츠 생성 (LLM)
    content_generator = ContentGenerator()
    theory_content = content_generator.generate_theory_content(
        chapter=2, 
        user_type="business", 
        user_level="medium",
        context="LLM과 GPT의 차이점에 대해 알고 싶어요"
    )
    
    print(f"📚 생성된 이론 콘텐츠:")
    print(f"   제목: {theory_content['title']}")
    print(f"   섹션 수: {len(theory_content['main_content'])}")
    print(f"   예시 수: {len(theory_content['examples'])}")
    print(f"   핵심 포인트 수: {len(theory_content['key_points'])}")
    
    # 챕터 4 퀴즈 생성 (ChatGPT 활용)
    quiz_generator = QuestionGenerator()
    quiz_data = quiz_generator.generate_multiple_choice_question(
        chapter_id=4,
        user_level="medium",
        user_type="business"
    )
    
    print(f"\n❓ 생성된 퀴즈:")
    print(f"   문제: {quiz_data['question_text']}")
    print(f"   선택지 수: {len(quiz_data['options'])}")
    print(f"   정답: {quiz_data['options'][quiz_data['correct_answer']]}")
    
    # UI와 통합
    test_state = StateManager.create_initial_state("demo_user", "beginner", "low")
    ui_generator = get_agent_ui_generator()
    
    # 이론 설명 UI
    theory_ui = ui_generator.generate_ui_for_agent("theory_educator", test_state, {
        'title': theory_content['title'],
        'show_progress': True,
        'content_type': 'theory'
    })
    print_ui_state(theory_ui, "이론 설명 UI")
    
    # 퀴즈 UI
    quiz_ui = ui_generator.generate_ui_for_agent("quiz_generator", test_state, {
        'quiz_type': 'multiple_choice',
        'question': quiz_data['question_text'],
        'options': quiz_data['options'],
        'quiz_info': quiz_data
    })
    print_ui_state(quiz_ui, "퀴즈 UI")


def demo_state_management_integration():
    """상태 관리 통합 데모"""
    print_separator("6. 상태 관리 통합 데모")
    
    # 초기 상태 생성
    initial_state = StateManager.create_initial_state("demo_user", "business", "high")
    initial_state['user_message'] = "프롬프트 엔지니어링에 대해 알려주세요"
    initial_state['current_chapter'] = 3
    
    print(f"📊 초기 상태:")
    print(f"   사용자 ID: {initial_state['user_id']}")
    print(f"   사용자 타입: {initial_state['user_type']}")
    print(f"   사용자 레벨: {initial_state['user_level']}")
    print(f"   현재 챕터: {initial_state['current_chapter']}")
    print(f"   현재 단계: {initial_state['current_stage']}")
    print(f"   UI 모드: {initial_state['ui_mode']}")
    
    # UI 상태 업데이트
    updated_state = StateManager.update_ui_state_for_agent(
        initial_state, "theory_educator",
        {'title': '프롬프트 엔지니어링', 'show_progress': True}
    )
    
    print(f"\n🔄 UI 상태 업데이트 후:")
    print(f"   UI 모드: {updated_state['ui_mode']}")
    print(f"   UI 요소 존재: {updated_state['ui_elements'] is not None}")
    
    if updated_state['ui_elements']:
        ui_data = updated_state['ui_elements']
        print(f"   UI 제목: {ui_data.get('title', 'N/A')}")
        print(f"   UI 요소 수: {len(ui_data.get('elements', []))}")
    
    # UI 전환 처리
    transition_state = StateManager.handle_ui_transition(
        updated_state, "user_input_received", "quiz_generator"
    )
    
    print(f"\n⚡ UI 전환 후:")
    print(f"   UI 모드: {transition_state['ui_mode']}")
    
    # 대화 기록 추가
    conversation_state = StateManager.add_conversation(
        transition_state,
        "theory_educator",
        "프롬프트 엔지니어링에 대해 알려주세요",
        "프롬프트 엔지니어링은 AI 모델과 효과적으로 소통하기 위한 기술입니다...",
        {'content_type': 'theory', 'chapter': 3}
    )
    
    print(f"\n💬 대화 기록 추가 후:")
    print(f"   대화 수: {len(conversation_state['current_loop_conversations'])}")
    
    if conversation_state['current_loop_conversations']:
        latest_conv = conversation_state['current_loop_conversations'][-1]
        print(f"   최근 대화 에이전트: {latest_conv['agent_name']}")
        print(f"   최근 응답 길이: {len(latest_conv['system_response'])} 문자")


def main():
    """메인 데모 실행"""
    print("🚀 UI 모드 관리 시스템 데모 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        demo_basic_ui_modes()
        demo_agent_specific_ui()
        demo_ui_transitions()
        demo_serialization()
        demo_content_integration()
        demo_state_management_integration()
        
        print_separator("데모 완료")
        print("✅ 모든 데모가 성공적으로 완료되었습니다!")
        print("\n📋 구현된 주요 기능:")
        print("   • 하이브리드 UX 패턴 (채팅/퀴즈/제한/오류/로딩 모드)")
        print("   • 에이전트별 맞춤 UI 생성")
        print("   • UI 상태 전환 관리")
        print("   • UI 상태 직렬화/역직렬화")
        print("   • 콘텐츠 생성과 UI 통합")
        print("   • 상태 관리 시스템 통합")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()