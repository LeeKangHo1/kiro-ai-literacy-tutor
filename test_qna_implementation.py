# test_qna_implementation.py
# QnAResolver 구현 테스트

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모든 모듈이 올바르게 임포트되는지 테스트"""
    try:
        # ChromaDB 도구 테스트
        from tools.external.chromadb_tool import chromadb_tool, search_knowledge_base
        print("✓ ChromaDB 도구 임포트 성공")
        
        # 웹 검색 도구 테스트
        from tools.external.web_search_tool import web_search_tool, search_web_for_answer
        print("✓ 웹 검색 도구 임포트 성공")
        
        # 검색 핸들러 테스트
        from agents.qna.search_handler import search_handler, search_for_question_answer
        print("✓ 검색 핸들러 임포트 성공")
        
        # 맥락 통합기 테스트
        from agents.qna.context_integrator import context_integrator, generate_contextual_answer
        print("✓ 맥락 통합기 임포트 성공")
        
        # 메인 QnA 에이전트 테스트
        from agents.qna.qna_resolver import qna_resolver, resolve_user_question
        print("✓ QnA 에이전트 임포트 성공")
        
        # 패키지 레벨 임포트 테스트
        from agents.qna import qna_resolver as qna_from_package
        from tools.external import chromadb_tool as chromadb_from_package
        print("✓ 패키지 레벨 임포트 성공")
        
        return True
        
    except ImportError as e:
        print(f"✗ 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"✗ 예상치 못한 오류: {e}")
        return False

def test_basic_functionality():
    """기본 기능 테스트"""
    try:
        # 웹 검색 도구 기본 테스트 (더미 모드)
        from tools.external.web_search_tool import web_search_tool
        
        # 더미 검색 실행
        results = web_search_tool.search_web("AI란 무엇인가", num_results=2)
        print(f"✓ 웹 검색 테스트 성공: {len(results)}개 결과")
        
        # 검색 핸들러 기본 테스트
        from agents.qna.search_handler import search_for_question_answer
        
        search_result = search_for_question_answer(
            question="AI란 무엇인가요?",
            current_chapter=1,
            user_level="medium",
            user_type="beginner"
        )
        print(f"✓ 검색 핸들러 테스트 성공: {search_result.get('total_results', 0)}개 결과")
        
        # 맥락 통합기 기본 테스트
        from agents.qna.context_integrator import generate_contextual_answer
        
        dummy_search_results = {
            'results': [{
                'content': 'AI는 인공지능을 의미합니다.',
                'source': 'web_search_dummy',
                'final_score': 0.8
            }]
        }
        
        answer = generate_contextual_answer(
            question="AI란 무엇인가요?",
            search_results=dummy_search_results,
            current_chapter=1,
            user_level="medium",
            user_type="beginner"
        )
        print(f"✓ 맥락 통합기 테스트 성공: 신뢰도 {answer.get('confidence_score', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 기능 테스트 실패: {e}")
        return False

def test_agent_info():
    """에이전트 정보 테스트"""
    try:
        from agents.qna.qna_resolver import qna_resolver
        
        agent_info = qna_resolver.get_agent_info()
        print(f"✓ 에이전트 정보: {agent_info['agent_name']}")
        print(f"  - 지원 질문 유형: {len(agent_info['supported_question_types'])}개")
        print(f"  - 검색 기능: {len(agent_info['search_capabilities'])}개")
        
        return True
        
    except Exception as e:
        print(f"✗ 에이전트 정보 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== QnAResolver 구현 테스트 시작 ===\n")
    
    # 임포트 테스트
    print("1. 모듈 임포트 테스트:")
    import_success = test_imports()
    print()
    
    if import_success:
        # 기본 기능 테스트
        print("2. 기본 기능 테스트:")
        functionality_success = test_basic_functionality()
        print()
        
        # 에이전트 정보 테스트
        print("3. 에이전트 정보 테스트:")
        info_success = test_agent_info()
        print()
        
        # 전체 결과
        if import_success and functionality_success and info_success:
            print("🎉 모든 테스트 통과! QnAResolver 구현이 완료되었습니다.")
        else:
            print("⚠️  일부 테스트 실패. 구현을 확인해 주세요.")
    else:
        print("❌ 임포트 실패로 인해 추가 테스트를 건너뜁니다.")
    
    print("\n=== 테스트 완료 ===")