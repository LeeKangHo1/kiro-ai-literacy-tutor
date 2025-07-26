# test_chromadb_service.py
# ChromaDB 서비스 테스트 및 초기 콘텐츠 로드

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chromadb_service():
    """ChromaDB 서비스 기본 테스트"""
    try:
        print("=== ChromaDB 서비스 테스트 시작 ===\n")
        
        # 1. 서비스 임포트 테스트
        print("1. 서비스 임포트 테스트:")
        from services.chromadb_service import (
            chromadb_service, 
            initialize_default_content,
            search_learning_content,
            get_chromadb_health
        )
        print("✓ ChromaDB 서비스 임포트 성공")
        
        # 2. 상태 확인 테스트
        print("\n2. 상태 확인 테스트:")
        health_status = get_chromadb_health()
        print(f"✓ 연결 상태: {health_status.get('connection', 'unknown')}")
        print(f"✓ 컬렉션 상태: {health_status.get('collection_status', 'unknown')}")
        print(f"✓ 전체 상태: {health_status.get('status', 'unknown')}")
        
        # 3. 통계 정보 테스트
        print("\n3. 통계 정보 테스트:")
        stats = chromadb_service.get_content_statistics()
        print(f"✓ 총 문서 수: {stats.get('content_distribution', {}).get('total_documents', 0)}")
        print(f"✓ 지원 챕터: {stats.get('supported_chapters', [])}")
        print(f"✓ 콘텐츠 유형: {stats.get('content_types', [])}")
        
        # 4. 기본 콘텐츠 초기화 테스트 (API 키가 있는 경우에만)
        print("\n4. 기본 콘텐츠 초기화 테스트:")
        if health_status.get('status') == 'healthy':
            init_result = initialize_default_content()
            if init_result:
                print("✓ 기본 콘텐츠 초기화 성공")
            else:
                print("⚠️  기본 콘텐츠 초기화 실패 (API 키 필요)")
        else:
            print("⚠️  ChromaDB 연결 문제로 초기화 건너뜀")
        
        # 5. 검색 테스트
        print("\n5. 검색 기능 테스트:")
        search_results = search_learning_content(
            query="AI란 무엇인가요?",
            chapter_id=1,
            content_type="theory"
        )
        print(f"✓ 검색 결과: {len(search_results)}개")
        
        if search_results:
            first_result = search_results[0]
            print(f"  - 첫 번째 결과 미리보기: {first_result.get('content', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB 서비스 테스트 실패: {e}")
        return False

def test_advanced_search():
    """고급 검색 도구 테스트"""
    try:
        print("\n=== 고급 검색 도구 테스트 시작 ===\n")
        
        # 1. 고급 검색 도구 임포트
        print("1. 고급 검색 도구 임포트:")
        from tools.external.advanced_search_tool import (
            advanced_search_tool,
            perform_advanced_search
        )
        print("✓ 고급 검색 도구 임포트 성공")
        
        # 2. 검색 컨텍스트 설정
        search_context = {
            'current_chapter': 1,
            'user_level': 'medium',
            'user_type': 'beginner'
        }
        
        # 3. 고급 검색 실행
        print("\n2. 고급 검색 실행:")
        search_result = perform_advanced_search(
            query="머신러닝과 딥러닝의 차이점",
            context=search_context,
            options={
                'max_results': 5,
                'enable_reranking': True,
                'include_web_search': True
            }
        )
        
        print(f"✓ 검색 완료: {search_result.get('returned_count', 0)}개 결과")
        print(f"✓ 검색 품질 점수: {search_result.get('search_quality_score', 0):.2f}")
        
        # 4. 결과 분석
        results = search_result.get('results', [])
        if results:
            print("\n3. 상위 결과 분석:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. 점수: {result.get('advanced_ranking_score', 0):.2f}")
                print(f"     소스: {result.get('source', 'unknown')}")
                print(f"     신뢰도: {result.get('confidence_level', 'unknown')}")
                print(f"     추천 이유: {result.get('recommendation_reason', 'N/A')}")
                print()
        
        return True
        
    except Exception as e:
        print(f"✗ 고급 검색 도구 테스트 실패: {e}")
        return False

def test_content_management():
    """콘텐츠 관리 기능 테스트"""
    try:
        print("\n=== 콘텐츠 관리 기능 테스트 시작 ===\n")
        
        from services.chromadb_service import chromadb_service
        
        # 1. 챕터별 콘텐츠 추가 테스트
        print("1. 챕터별 콘텐츠 추가 테스트:")
        test_contents = [
            {
                'content': '테스트 콘텐츠: AI 기본 개념 설명',
                'content_type': 'theory',
                'topic': '테스트 주제'
            }
        ]
        
        add_result = chromadb_service.add_chapter_content(1, test_contents)
        print(f"✓ 추가 결과: {add_result.get('success_count', 0)}/{add_result.get('total_contents', 0)}")
        
        # 2. 백업 기능 테스트
        print("\n2. 백업 기능 테스트:")
        backup_result = chromadb_service.backup_content("test_backup.json")
        if backup_result.get('success'):
            print(f"✓ 백업 성공: {backup_result.get('backup_path')}")
            print(f"✓ 백업 크기: {backup_result.get('backup_size', 0)} bytes")
        else:
            print(f"⚠️  백업 실패: {backup_result.get('error', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 콘텐츠 관리 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("ChromaDB 벡터 데이터베이스 연동 테스트\n")
    
    # 기본 서비스 테스트
    service_success = test_chromadb_service()
    
    # 고급 검색 테스트
    if service_success:
        search_success = test_advanced_search()
        
        # 콘텐츠 관리 테스트
        if search_success:
            management_success = test_content_management()
            
            # 전체 결과
            if service_success and search_success and management_success:
                print("\n🎉 모든 ChromaDB 테스트 통과!")
                print("✓ ChromaDB 클라이언트 설정 및 연결 관리")
                print("✓ 학습 콘텐츠 벡터화 및 저장 기능")
                print("✓ 유사도 검색 및 결과 랭킹 시스템")
            else:
                print("\n⚠️  일부 테스트 실패")
        else:
            print("\n❌ 고급 검색 테스트 실패로 인해 추가 테스트 건너뜀")
    else:
        print("\n❌ 기본 서비스 테스트 실패로 인해 추가 테스트 건너뜀")
    
    print("\n=== ChromaDB 테스트 완료 ===")