# tools/content/theory_tool.py
# theory_generation_tool 구현

from typing import Dict, Any, Optional
from agents.educator.content_generator import ContentGenerator
from agents.educator.level_adapter import LevelAdapter
from workflow.state_management import TutorState, StateManager


def theory_generation_tool(chapter_id: int, user_level: str, user_type: str, 
                          context: str = "") -> Dict[str, Any]:
    """
    사용자 레벨별 맞춤 이론 설명 생성 도구
    
    Args:
        chapter_id: 챕터 번호 (1, 2, 3)
        user_level: 사용자 레벨 ('low', 'medium', 'high')
        user_type: 사용자 타입 ('beginner', 'business')
        context: 추가 컨텍스트 정보
    
    Returns:
        생성된 이론 콘텐츠 딕셔너리
    """
    
    try:
        # 콘텐츠 생성기 초기화
        content_generator = ContentGenerator()
        level_adapter = LevelAdapter()
        
        # 기본 콘텐츠 생성
        base_content = content_generator.generate_theory_content(
            chapter=chapter_id,
            user_type=user_type,
            user_level=user_level,
            context=context
        )
        
        # 임시 상태 생성 (레벨 적응을 위해)
        temp_state = {
            'user_level': user_level,
            'user_type': user_type,
            'current_chapter': chapter_id,
            'recent_loops_summary': [],
            'current_loop_conversations': []
        }
        
        # 레벨별 적응
        adapted_content = level_adapter.adapt_content(base_content, temp_state)
        
        # 콘텐츠 유효성 검증
        if not content_generator.validate_content(adapted_content):
            raise ValueError("생성된 콘텐츠가 유효하지 않습니다.")
        
        # 성공 응답
        return {
            'success': True,
            'content': adapted_content,
            'metadata': {
                'tool_name': 'theory_generation_tool',
                'chapter_id': chapter_id,
                'user_level': user_level,
                'user_type': user_type,
                'context_provided': bool(context),
                'generated_at': adapted_content['metadata']['generated_at']
            }
        }
        
    except Exception as e:
        # 오류 처리
        return {
            'success': False,
            'error': str(e),
            'fallback_content': _generate_fallback_theory(chapter_id, user_level, user_type),
            'metadata': {
                'tool_name': 'theory_generation_tool',
                'error_occurred': True,
                'chapter_id': chapter_id,
                'user_level': user_level,
                'user_type': user_type
            }
        }


def enhanced_theory_generation_tool(state: TutorState, additional_context: str = "") -> Dict[str, Any]:
    """
    상태 정보를 활용한 향상된 이론 생성 도구
    
    Args:
        state: 현재 튜터 상태
        additional_context: 추가 컨텍스트
    
    Returns:
        생성된 이론 콘텐츠와 UI 요소
    """
    
    try:
        # 상태에서 필요한 정보 추출
        chapter_id = state.get('current_chapter', 1)
        user_level = state.get('user_level', 'medium')
        user_type = state.get('user_type', 'beginner')
        
        # 기존 학습 컨텍스트 생성
        context_parts = []
        
        # 최근 루프 요약에서 컨텍스트 추출
        recent_loops = state.get('recent_loops_summary', [])
        if recent_loops:
            last_loop = recent_loops[-1]
            context_parts.append(f"이전 학습: {last_loop.get('main_topics', '')}")
        
        # 현재 루프 대화에서 컨텍스트 추출
        current_conversations = state.get('current_loop_conversations', [])
        if current_conversations:
            recent_questions = [
                conv.get('user_message', '') for conv in current_conversations[-2:]
                if conv.get('user_message', '').strip()
            ]
            if recent_questions:
                context_parts.append(f"최근 질문: {' | '.join(recent_questions)}")
        
        # 추가 컨텍스트 포함
        if additional_context:
            context_parts.append(additional_context)
        
        full_context = ' / '.join(context_parts)
        
        # 기본 도구 호출
        result = theory_generation_tool(chapter_id, user_level, user_type, full_context)
        
        if result['success']:
            content = result['content']
            
            # UI 요소 생성
            ui_elements = _generate_theory_ui_elements(content, state)
            
            # 결과에 UI 요소 추가
            result['ui_elements'] = ui_elements
            result['formatted_message'] = _format_theory_message(content)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f"향상된 이론 생성 중 오류: {str(e)}",
            'fallback_content': _generate_fallback_theory(
                state.get('current_chapter', 1),
                state.get('user_level', 'medium'),
                state.get('user_type', 'beginner')
            )
        }


def _generate_fallback_theory(chapter_id: int, user_level: str, user_type: str) -> Dict[str, Any]:
    """기본 이론 콘텐츠 생성 (오류 시 사용)"""
    
    fallback_content = {
        1: {
            'title': 'AI 기초 개념',
            'content': 'AI(인공지능)는 컴퓨터가 인간의 지능을 모방하여 학습하고 판단하는 기술입니다.',
            'examples': ['음성인식', '이미지 인식', '번역 서비스']
        },
        2: {
            'title': 'AI의 종류',
            'content': 'AI는 약한 AI와 강한 AI로 구분되며, 학습 방법에 따라 지도학습, 비지도학습, 강화학습으로 나뉩니다.',
            'examples': ['분류 시스템', '클러스터링', '게임 AI']
        },
        3: {
            'title': '프롬프트 기초',
            'content': '프롬프트는 AI에게 주는 명령어로, 명확하고 구체적으로 작성해야 좋은 결과를 얻을 수 있습니다.',
            'examples': ['질문하기', '번역 요청', '요약 요청']
        }
    }
    
    chapter_content = fallback_content.get(chapter_id, fallback_content[1])
    
    return {
        'chapter': chapter_id,
        'title': chapter_content['title'],
        'introduction': f"{chapter_content['title']}에 대해 알아보겠습니다.",
        'main_content': [{
            'section_number': 1,
            'title': '기본 개념',
            'content': chapter_content['content'],
            'concepts': []
        }],
        'examples': chapter_content['examples'],
        'key_points': [f"{chapter_content['title']} 이해"],
        'next_steps': ['질문하기', '퀴즈 풀기'],
        'metadata': {
            'user_type': user_type,
            'user_level': user_level,
            'is_fallback': True
        }
    }


def _generate_theory_ui_elements(content: Dict[str, Any], state: TutorState) -> Dict[str, Any]:
    """이론 콘텐츠용 UI 요소 생성"""
    
    ui_elements = {
        'type': 'theory_display',
        'chapter': content['chapter'],
        'title': content['title'],
        'sections': []
    }
    
    # 메인 콘텐츠를 UI 섹션으로 변환
    for section in content['main_content']:
        ui_section = {
            'section_id': f"section_{section['section_number']}",
            'title': section['title'],
            'content': section['content'],
            'concepts': section.get('concepts', [])
        }
        ui_elements['sections'].append(ui_section)
    
    # 예시 섹션 추가
    if content.get('examples'):
        ui_elements['examples'] = {
            'title': '실제 예시',
            'items': content['examples']
        }
    
    # 핵심 포인트 섹션 추가
    if content.get('key_points'):
        ui_elements['key_points'] = {
            'title': '핵심 포인트',
            'items': content['key_points']
        }
    
    # 다음 단계 버튼
    if content.get('next_steps'):
        ui_elements['action_buttons'] = [
            {'text': '질문하기', 'action': 'ask_question'},
            {'text': '퀴즈 풀기', 'action': 'start_quiz'},
            {'text': '다음 진행', 'action': 'continue'}
        ]
    
    # 진도 표시
    ui_elements['progress'] = {
        'chapter': content['chapter'],
        'total_chapters': 3,
        'current_step': 'theory'
    }
    
    return ui_elements


def _format_theory_message(content: Dict[str, Any]) -> str:
    """이론 콘텐츠를 메시지 형태로 포맷팅"""
    
    message_parts = []
    
    # 제목과 도입부
    message_parts.append(f"# {content['title']}")
    message_parts.append(content['introduction'])
    message_parts.append("")
    
    # 메인 콘텐츠
    for section in content['main_content']:
        message_parts.append(f"## {section['title']}")
        message_parts.append(section['content'])
        message_parts.append("")
    
    # 예시
    if content.get('examples'):
        message_parts.append("## 📝 실제 예시")
        for i, example in enumerate(content['examples'], 1):
            message_parts.append(f"{i}. {example}")
        message_parts.append("")
    
    # 핵심 포인트
    if content.get('key_points'):
        message_parts.append("## 🎯 핵심 포인트")
        for point in content['key_points']:
            message_parts.append(f"• {point}")
        message_parts.append("")
    
    # 다음 단계
    if content.get('next_steps'):
        message_parts.append("## 🚀 다음 단계")
        for step in content['next_steps']:
            message_parts.append(f"• {step}")
    
    return "\n".join(message_parts)


def validate_theory_tool_input(chapter_id: int, user_level: str, user_type: str) -> bool:
    """이론 생성 도구 입력 유효성 검증"""
    
    # 챕터 ID 검증
    if not isinstance(chapter_id, int) or chapter_id < 1 or chapter_id > 3:
        return False
    
    # 사용자 레벨 검증
    if user_level not in ['low', 'medium', 'high']:
        return False
    
    # 사용자 타입 검증
    if user_type not in ['beginner', 'business']:
        return False
    
    return True


# 도구 메타데이터
THEORY_TOOL_METADATA = {
    'name': 'theory_generation_tool',
    'description': '사용자 레벨별 맞춤 이론 설명 생성',
    'version': '1.0.0',
    'parameters': {
        'chapter_id': {'type': 'int', 'required': True, 'range': [1, 3]},
        'user_level': {'type': 'str', 'required': True, 'options': ['low', 'medium', 'high']},
        'user_type': {'type': 'str', 'required': True, 'options': ['beginner', 'business']},
        'context': {'type': 'str', 'required': False}
    },
    'returns': {
        'success': 'bool',
        'content': 'dict',
        'ui_elements': 'dict',
        'metadata': 'dict'
    }
}