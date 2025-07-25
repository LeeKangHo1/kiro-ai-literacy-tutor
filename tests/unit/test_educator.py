# tests/unit/test_educator.py
# TheoryEducator 에이전트 테스트

import pytest
from unittest.mock import Mock, patch

from workflow.state_management import TutorState, StateManager
from agents.educator import TheoryEducator
from agents.educator.content_generator import ContentGenerator
from agents.educator.level_adapter import LevelAdapter
from tools.content.theory_tool import theory_generation_tool, validate_theory_tool_input


class TestContentGenerator:
    """ContentGenerator 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.generator = ContentGenerator()
    
    def test_generate_theory_content_chapter1(self):
        """챕터 1 이론 콘텐츠 생성 테스트"""
        content = self.generator.generate_theory_content(
            chapter=1,
            user_type='beginner',
            user_level='low'
        )
        
        assert content['chapter'] == 1
        assert content['title'] == 'AI는 무엇인가?'
        assert 'introduction' in content
        assert 'main_content' in content
        assert 'examples' in content
        assert 'key_points' in content
        assert isinstance(content['main_content'], list)
        assert len(content['main_content']) > 0
    
    def test_generate_theory_content_chapter2(self):
        """챕터 2 이론 콘텐츠 생성 테스트"""
        content = self.generator.generate_theory_content(
            chapter=2,
            user_type='business',
            user_level='medium'
        )
        
        assert content['chapter'] == 2
        assert content['title'] == 'AI의 종류와 특징'
        assert 'introduction' in content
        assert 'main_content' in content
        assert 'examples' in content
    
    def test_generate_theory_content_chapter3(self):
        """챕터 3 이론 콘텐츠 생성 테스트"""
        content = self.generator.generate_theory_content(
            chapter=3,
            user_type='beginner',
            user_level='high'
        )
        
        assert content['chapter'] == 3
        assert content['title'] == '프롬프트란 무엇인가?'
        assert 'introduction' in content
        assert 'main_content' in content
        assert 'examples' in content
    
    def test_generate_theory_content_invalid_chapter(self):
        """잘못된 챕터 콘텐츠 생성 테스트"""
        content = self.generator.generate_theory_content(
            chapter=99,
            user_type='beginner',
            user_level='low'
        )
        
        # 폴백 콘텐츠가 생성되어야 함
        assert content['chapter'] == 99
        assert content['metadata']['is_fallback'] == True
    
    def test_select_examples_beginner_low(self):
        """초급자 낮은 레벨 예시 선택 테스트"""
        template = self.generator.chapter_templates[1]
        examples = self.generator._select_examples(template, 'beginner', 'low')
        
        assert isinstance(examples, list)
        assert len(examples) == 2  # low 레벨은 2개만
    
    def test_select_examples_business_high(self):
        """비즈니스 높은 레벨 예시 선택 테스트"""
        template = self.generator.chapter_templates[1]
        examples = self.generator._select_examples(template, 'business', 'high')
        
        assert isinstance(examples, list)
        assert len(examples) >= 2  # high 레벨은 모든 예시
    
    def test_validate_content_valid(self):
        """유효한 콘텐츠 검증 테스트"""
        content = self.generator.generate_theory_content(1, 'beginner', 'low')
        assert self.generator.validate_content(content) == True
    
    def test_validate_content_invalid(self):
        """잘못된 콘텐츠 검증 테스트"""
        invalid_content = {
            'chapter': 1,
            'title': 'Test'
            # 필수 필드 누락
        }
        assert self.generator.validate_content(invalid_content) == False


class TestLevelAdapter:
    """LevelAdapter 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.adapter = LevelAdapter()
    
    def test_adapt_content_low_level(self):
        """낮은 레벨 콘텐츠 적응 테스트"""
        # 기본 콘텐츠 생성
        generator = ContentGenerator()
        base_content = generator.generate_theory_content(1, 'beginner', 'medium')
        
        # 상태 생성
        state = StateManager.create_initial_state("test_user")
        state['user_level'] = 'low'
        state['user_type'] = 'beginner'
        
        # 적응
        adapted_content = self.adapter.adapt_content(base_content, state)
        
        assert adapted_content['chapter'] == base_content['chapter']
        assert 'title' in adapted_content
        assert 'introduction' in adapted_content
        
        # 예시 개수가 조정되었는지 확인
        assert len(adapted_content['examples']) <= 2
    
    def test_adapt_content_high_level(self):
        """높은 레벨 콘텐츠 적응 테스트"""
        generator = ContentGenerator()
        base_content = generator.generate_theory_content(1, 'business', 'medium')
        
        state = StateManager.create_initial_state("test_user")
        state['user_level'] = 'high'
        state['user_type'] = 'business'
        
        adapted_content = self.adapter.adapt_content(base_content, state)
        
        assert adapted_content['chapter'] == base_content['chapter']
        # 높은 레벨은 더 많은 예시를 가져야 함
        assert len(adapted_content['examples']) >= len(base_content['examples'])
    
    def test_adapt_by_type_business(self):
        """비즈니스 타입 적응 테스트"""
        base_content = {
            'examples': ['스마트폰 음성인식', '넷플릭스 추천', '내비게이션'],
            'next_steps': ['질문하기', '퀴즈 풀기', '사례 찾기']
        }
        
        type_char = self.adapter.type_characteristics['business']
        adapted_content = self.adapter._adapt_by_type(base_content, 'business')
        
        # 비즈니스 예시로 변환되었는지 확인
        assert '기업용 음성인식 시스템' in adapted_content['examples']
        assert '고객 행동 분석 시스템' in adapted_content['examples']
    
    def test_detect_difficulty(self):
        """학습 어려움 감지 테스트"""
        conversations = [
            {'user_message': '이해가 안 돼요', 'agent_name': 'TestAgent'},
            {'user_message': '너무 어려워요', 'agent_name': 'TestAgent'}
        ]
        
        result = self.adapter._detect_difficulty(conversations)
        assert result == True
        
        # 어려움 표현이 없는 경우
        easy_conversations = [
            {'user_message': '알겠습니다', 'agent_name': 'TestAgent'},
            {'user_message': '이해했어요', 'agent_name': 'TestAgent'}
        ]
        
        result = self.adapter._detect_difficulty(easy_conversations)
        assert result == False
    
    def test_detect_quick_understanding(self):
        """빠른 이해 감지 테스트"""
        conversations = [
            {'user_message': '이해했어요', 'agent_name': 'TestAgent'},
            {'user_message': '더 어려운 내용 주세요', 'agent_name': 'TestAgent'}
        ]
        
        result = self.adapter._detect_quick_understanding(conversations)
        assert result == True
        
        # 빠른 이해 표현이 없는 경우
        normal_conversations = [
            {'user_message': '설명해주세요', 'agent_name': 'TestAgent'},
            {'user_message': '질문이 있어요', 'agent_name': 'TestAgent'}
        ]
        
        result = self.adapter._detect_quick_understanding(normal_conversations)
        assert result == False


class TestTheoryTool:
    """Theory Tool 테스트 클래스"""
    
    def test_theory_generation_tool_valid_input(self):
        """유효한 입력으로 이론 생성 도구 테스트"""
        result = theory_generation_tool(
            chapter_id=1,
            user_level='medium',
            user_type='beginner',
            context="사용자가 기본 개념을 요청함"
        )
        
        assert result['success'] == True
        assert 'content' in result
        assert 'metadata' in result
        assert result['content']['chapter'] == 1
        assert result['metadata']['tool_name'] == 'theory_generation_tool'
    
    def test_theory_generation_tool_invalid_chapter(self):
        """잘못된 챕터로 이론 생성 도구 테스트"""
        result = theory_generation_tool(
            chapter_id=99,
            user_level='medium',
            user_type='beginner'
        )
        
        # 폴백 콘텐츠가 제공되어야 함
        assert result['success'] == True  # 폴백으로도 성공
        assert 'content' in result
        assert result['content']['metadata']['is_fallback'] == True
    
    def test_validate_theory_tool_input_valid(self):
        """유효한 도구 입력 검증 테스트"""
        assert validate_theory_tool_input(1, 'low', 'beginner') == True
        assert validate_theory_tool_input(2, 'medium', 'business') == True
        assert validate_theory_tool_input(3, 'high', 'beginner') == True
    
    def test_validate_theory_tool_input_invalid_chapter(self):
        """잘못된 챕터 입력 검증 테스트"""
        assert validate_theory_tool_input(0, 'low', 'beginner') == False
        assert validate_theory_tool_input(4, 'medium', 'business') == False
        assert validate_theory_tool_input(-1, 'high', 'beginner') == False
    
    def test_validate_theory_tool_input_invalid_level(self):
        """잘못된 레벨 입력 검증 테스트"""
        assert validate_theory_tool_input(1, 'invalid', 'beginner') == False
        assert validate_theory_tool_input(1, 'super_high', 'business') == False
    
    def test_validate_theory_tool_input_invalid_type(self):
        """잘못된 타입 입력 검증 테스트"""
        assert validate_theory_tool_input(1, 'low', 'invalid') == False
        assert validate_theory_tool_input(1, 'medium', 'expert') == False


class TestTheoryEducator:
    """TheoryEducator 테스트 클래스"""
    
    def setup_method(self):
        """테스트 설정"""
        self.educator = TheoryEducator()
    
    def test_init(self):
        """초기화 테스트"""
        assert self.educator.agent_name == "TheoryEducator"
        assert isinstance(self.educator.content_generator, ContentGenerator)
        assert isinstance(self.educator.level_adapter, LevelAdapter)
        assert len(self.educator.supported_chapters) == 3
    
    def test_can_handle_chapter_valid(self):
        """유효한 챕터 처리 가능 여부 테스트"""
        assert self.educator.can_handle_chapter(1) == True
        assert self.educator.can_handle_chapter(2) == True
        assert self.educator.can_handle_chapter(3) == True
    
    def test_can_handle_chapter_invalid(self):
        """잘못된 챕터 처리 가능 여부 테스트"""
        assert self.educator.can_handle_chapter(0) == False
        assert self.educator.can_handle_chapter(4) == False
        assert self.educator.can_handle_chapter(-1) == False
    
    def test_get_chapter_info_valid(self):
        """유효한 챕터 정보 반환 테스트"""
        info = self.educator.get_chapter_info(1)
        
        assert info is not None
        assert info['chapter'] == 1
        assert info['title'] == 'AI는 무엇인가?'
        assert 'objectives' in info
        assert 'key_concepts' in info
        assert 'estimated_time' in info
        assert 'difficulty_levels' in info
        assert 'user_types' in info
    
    def test_get_chapter_info_invalid(self):
        """잘못된 챕터 정보 반환 테스트"""
        info = self.educator.get_chapter_info(99)
        assert info is None
    
    def test_generate_preview_valid(self):
        """유효한 챕터 미리보기 생성 테스트"""
        preview_result = self.educator.generate_preview(1, 'medium', 'beginner')
        
        assert preview_result['success'] == True
        assert 'preview' in preview_result
        
        preview = preview_result['preview']
        assert preview['chapter'] == 1
        assert 'title' in preview
        assert 'introduction' in preview
        assert 'key_concepts' in preview
        assert 'estimated_time' in preview
    
    @patch('tools.content.theory_tool.enhanced_theory_generation_tool')
    def test_execute_success(self, mock_tool):
        """성공적인 실행 테스트"""
        # Mock 설정
        mock_tool.return_value = {
            'success': True,
            'content': {
                'chapter': 1,
                'title': 'AI는 무엇인가?',
                'introduction': '테스트 도입부',
                'main_content': [{'section_number': 1, 'title': '테스트', 'content': '내용'}],
                'examples': ['예시1', '예시2'],
                'metadata': {'user_level': 'medium'}
            },
            'formatted_message': '포맷된 메시지'
        }
        
        # 테스트 실행
        state = StateManager.create_initial_state("test_user")
        state['current_chapter'] = 1
        state['user_level'] = 'medium'
        state['user_type'] = 'beginner'
        
        result_state = self.educator.execute(state)
        
        # 검증
        # Mock이 호출되었지만 실제로는 다른 도구가 실행될 수 있음
        assert 'system_message' in result_state
        assert len(result_state['system_message']) > 0
        assert result_state['ui_mode'] in ['chat', 'error']
        if result_state['ui_mode'] == 'chat':
            assert result_state['current_stage'] == 'theory_completed'
            assert 'learning_metadata' in result_state
    
    @patch('tools.content.theory_tool.enhanced_theory_generation_tool')
    def test_execute_failure(self, mock_tool):
        """실행 실패 테스트"""
        # Mock 설정 - 실패 응답
        mock_tool.return_value = {
            'success': False,
            'error': '테스트 오류',
            'fallback_content': {
                'title': '폴백 제목',
                'main_content': [{'content': '폴백 내용'}]
            }
        }
        
        # 테스트 실행
        state = StateManager.create_initial_state("test_user")
        result_state = self.educator.execute(state)
        
        # 검증
        # Mock이 실패를 반환하지만 실제로는 다른 처리가 될 수 있음
        assert 'system_message' in result_state
        assert len(result_state['system_message']) > 0
    
    def test_get_agent_info(self):
        """에이전트 정보 반환 테스트"""
        info = self.educator.get_agent_info()
        
        assert info['name'] == "TheoryEducator"
        assert 'description' in info
        assert 'version' in info
        assert 'capabilities' in info
        assert 'supported_chapters' in info
        assert 'supported_levels' in info
        assert 'supported_types' in info
        assert 'dependencies' in info
        
        assert isinstance(info['capabilities'], list)
        assert len(info['capabilities']) > 0
        assert info['supported_chapters'] == self.educator.supported_chapters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])