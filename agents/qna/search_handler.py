# agents/qna/search_handler.py
# ChromaDB 벡터 검색 및 웹 검색 처리

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

# 도구 임포트
from tools.external.chromadb_tool import search_knowledge_base
from tools.external.web_search_tool import search_web_for_answer, search_general_web

logger = logging.getLogger(__name__)

class SearchHandler:
    """검색 처리 핸들러 - ChromaDB와 웹 검색을 통합 관리"""
    
    def __init__(self):
        """검색 핸들러 초기화"""
        self.search_strategies = {
            'knowledge_first': self._knowledge_first_search,
            'web_first': self._web_first_search,
            'hybrid': self._hybrid_search
        }
    
    def search_for_answer(self, question: str, context: Dict[str, Any], 
                         strategy: str = 'hybrid') -> Dict[str, Any]:
        """질문에 대한 답변 검색
        
        Args:
            question: 사용자 질문
            context: 현재 학습 맥락 (챕터, 사용자 정보 등)
            strategy: 검색 전략 ('knowledge_first', 'web_first', 'hybrid')
            
        Returns:
            Dict: 검색 결과와 메타데이터
        """
        try:
            logger.info(f"질문 검색 시작: {question[:50]}...")
            
            # 검색 전략 실행
            search_func = self.search_strategies.get(strategy, self._hybrid_search)
            results = search_func(question, context)
            
            # 검색 결과 평가 및 랭킹
            ranked_results = self._rank_search_results(results, question, context)
            
            # 최종 결과 구성
            search_result = {
                'question': question,
                'strategy_used': strategy,
                'total_results': len(ranked_results),
                'results': ranked_results,
                'search_timestamp': datetime.now().isoformat(),
                'context_used': {
                    'chapter_id': context.get('current_chapter'),
                    'user_level': context.get('user_level'),
                    'user_type': context.get('user_type')
                }
            }
            
            logger.info(f"검색 완료: {len(ranked_results)}개 결과")
            return search_result
            
        except Exception as e:
            logger.error(f"검색 처리 실패: {e}")
            return self._get_error_result(question, str(e))
    
    def _knowledge_first_search(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """지식 베이스 우선 검색 전략
        
        Args:
            question: 검색 질문
            context: 학습 맥락
            
        Returns:
            List[Dict]: 검색 결과
        """
        results = []
        
        # 1. ChromaDB에서 관련 콘텐츠 검색
        chapter_id = context.get('current_chapter')
        kb_results = search_knowledge_base(
            query=question,
            chapter_id=chapter_id,
            max_results=5
        )
        
        results.extend(kb_results)
        
        # 2. 지식 베이스 결과가 부족한 경우 웹 검색 보완
        if len(kb_results) < 3:
            web_results = search_web_for_answer(question, max_results=3)
            results.extend(web_results)
        
        return results
    
    def _web_first_search(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """웹 검색 우선 전략
        
        Args:
            question: 검색 질문
            context: 학습 맥락
            
        Returns:
            List[Dict]: 검색 결과
        """
        results = []
        
        # 1. 웹에서 최신 정보 검색
        web_results = search_web_for_answer(question, max_results=4)
        results.extend(web_results)
        
        # 2. 지식 베이스에서 관련 기본 정보 보완
        chapter_id = context.get('current_chapter')
        kb_results = search_knowledge_base(
            query=question,
            chapter_id=chapter_id,
            max_results=2
        )
        results.extend(kb_results)
        
        return results
    
    def _hybrid_search(self, question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """하이브리드 검색 전략 (기본값)
        
        Args:
            question: 검색 질문
            context: 학습 맥락
            
        Returns:
            List[Dict]: 검색 결과
        """
        results = []
        
        # 1. 현재 챕터 관련 지식 베이스 검색
        chapter_id = context.get('current_chapter')
        kb_results = search_knowledge_base(
            query=question,
            chapter_id=chapter_id,
            max_results=3
        )
        results.extend(kb_results)
        
        # 2. 전체 지식 베이스에서 추가 검색 (챕터 제한 없음)
        if len(kb_results) < 2:
            general_kb_results = search_knowledge_base(
                query=question,
                chapter_id=None,
                max_results=2
            )
            results.extend(general_kb_results)
        
        # 3. 웹 검색으로 최신 정보 보완
        web_results = search_web_for_answer(question, max_results=3)
        results.extend(web_results)
        
        return results
    
    def _rank_search_results(self, results: List[Dict[str, Any]], 
                           question: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """검색 결과 랭킹 및 점수 계산
        
        Args:
            results: 원본 검색 결과
            question: 원본 질문
            context: 학습 맥락
            
        Returns:
            List[Dict]: 랭킹된 검색 결과
        """
        try:
            current_chapter = context.get('current_chapter', 0)
            user_level = context.get('user_level', 'medium')
            
            # 각 결과에 점수 계산
            for result in results:
                score = 0.0
                
                # 1. 기본 유사도 점수 (ChromaDB 결과)
                if 'similarity_score' in result:
                    score += result['similarity_score'] * 0.4
                
                # 2. 소스별 가중치
                source = result.get('source', '')
                if source == 'chromadb':
                    score += 0.3  # 내부 지식 베이스 우대
                elif source == 'web_search':
                    score += 0.2  # 웹 검색 결과
                
                # 3. 챕터 관련성 보너스
                if 'metadata' in result:
                    metadata = result['metadata']
                    if isinstance(metadata, dict) and metadata.get('chapter_id') == current_chapter:
                        score += 0.2  # 현재 챕터 관련 보너스
                
                # 4. AI 관련성 점수 (웹 검색 결과)
                if 'ai_relevance_score' in result:
                    score += result['ai_relevance_score'] * 0.1
                
                # 5. 사용자 레벨 적합성 (메타데이터 기반)
                if 'metadata' in result and isinstance(result['metadata'], dict):
                    content_level = result['metadata'].get('level', 'medium')
                    if content_level == user_level:
                        score += 0.1
                
                result['final_score'] = min(score, 1.0)  # 최대 1.0으로 제한
            
            # 점수 기준으로 정렬
            ranked_results = sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)
            
            # 상위 결과만 반환 (최대 8개)
            return ranked_results[:8]
            
        except Exception as e:
            logger.error(f"결과 랭킹 실패: {e}")
            return results[:5]  # 오류 시 상위 5개만 반환
    
    def _get_error_result(self, question: str, error_message: str) -> Dict[str, Any]:
        """오류 발생 시 기본 결과 반환
        
        Args:
            question: 원본 질문
            error_message: 오류 메시지
            
        Returns:
            Dict: 오류 결과
        """
        return {
            'question': question,
            'strategy_used': 'error',
            'total_results': 0,
            'results': [],
            'error': True,
            'error_message': error_message,
            'search_timestamp': datetime.now().isoformat(),
            'fallback_message': '죄송합니다. 검색 중 오류가 발생했습니다. 다시 질문해 주세요.'
        }
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """검색 통계 정보 반환
        
        Returns:
            Dict: 검색 통계
        """
        try:
            # ChromaDB 통계 가져오기
            from tools.external.chromadb_tool import chromadb_tool
            chromadb_stats = chromadb_tool.get_collection_stats()
            
            return {
                'chromadb_stats': chromadb_stats,
                'available_strategies': list(self.search_strategies.keys()),
                'default_strategy': 'hybrid',
                'max_results_per_source': {
                    'knowledge_base': 5,
                    'web_search': 3
                }
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {'error': str(e)}

# 전역 검색 핸들러 인스턴스
search_handler = SearchHandler()

def search_for_question_answer(question: str, current_chapter: int, 
                              user_level: str, user_type: str,
                              strategy: str = 'hybrid') -> Dict[str, Any]:
    """질문에 대한 답변 검색 (편의 함수)
    
    Args:
        question: 사용자 질문
        current_chapter: 현재 챕터
        user_level: 사용자 레벨
        user_type: 사용자 유형
        strategy: 검색 전략
        
    Returns:
        Dict: 검색 결과
    """
    context = {
        'current_chapter': current_chapter,
        'user_level': user_level,
        'user_type': user_type
    }
    
    return search_handler.search_for_answer(question, context, strategy)