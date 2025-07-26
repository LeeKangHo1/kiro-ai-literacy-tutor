# tools/external/advanced_search_tool.py
# 고급 검색 및 결과 랭킹 시스템

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import re
import math

# 기본 검색 도구 임포트
from .chromadb_tool import search_knowledge_base
from .web_search_tool import search_web_for_answer

logger = logging.getLogger(__name__)

class AdvancedSearchTool:
    """고급 검색 및 결과 랭킹 시스템"""
    
    def __init__(self):
        """고급 검색 도구 초기화"""
        self.ranking_weights = {
            'similarity_score': 0.4,      # 유사도 점수
            'source_reliability': 0.2,    # 소스 신뢰도
            'content_freshness': 0.1,     # 콘텐츠 신선도
            'chapter_relevance': 0.15,    # 챕터 관련성
            'content_completeness': 0.1,  # 콘텐츠 완성도
            'user_level_match': 0.05      # 사용자 레벨 매칭
        }
        
        self.source_reliability_scores = {
            'chromadb': 0.9,              # 내부 지식베이스 높은 신뢰도
            'web_search': 0.6,            # 웹 검색 중간 신뢰도
            'web_search_dummy': 0.3       # 더미 검색 낮은 신뢰도
        }
    
    def advanced_search(self, query: str, context: Dict[str, Any], 
                       search_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """고급 검색 실행
        
        Args:
            query: 검색 쿼리
            context: 검색 맥락 (사용자 정보, 챕터 등)
            search_options: 검색 옵션
            
        Returns:
            Dict: 고급 검색 결과
        """
        try:
            logger.info(f"고급 검색 시작: {query[:50]}...")
            
            # 검색 옵션 기본값 설정
            options = search_options or {}
            max_results = options.get('max_results', 8)
            enable_reranking = options.get('enable_reranking', True)
            include_web_search = options.get('include_web_search', True)
            
            # 1. 다중 소스 검색 실행
            search_results = self._execute_multi_source_search(
                query, context, include_web_search
            )
            
            # 2. 결과 전처리 및 정규화
            processed_results = self._preprocess_results(search_results, context)
            
            # 3. 고급 랭킹 적용
            if enable_reranking:
                ranked_results = self._apply_advanced_ranking(
                    processed_results, query, context
                )
            else:
                ranked_results = processed_results
            
            # 4. 결과 후처리 및 메타데이터 추가
            final_results = self._postprocess_results(
                ranked_results[:max_results], query, context
            )
            
            # 5. 검색 품질 평가
            quality_score = self._evaluate_search_quality(final_results, query)
            
            # 최종 결과 구성
            advanced_result = {
                'query': query,
                'total_found': len(search_results),
                'returned_count': len(final_results),
                'results': final_results,
                'search_quality_score': quality_score,
                'search_metadata': {
                    'context_used': context,
                    'ranking_applied': enable_reranking,
                    'web_search_included': include_web_search,
                    'search_timestamp': datetime.now().isoformat()
                }
            }
            
            logger.info(f"고급 검색 완료: {len(final_results)}개 결과, 품질점수 {quality_score:.2f}")
            return advanced_result
            
        except Exception as e:
            logger.error(f"고급 검색 실패: {e}")
            return self._get_error_result(query, str(e))
    
    def _execute_multi_source_search(self, query: str, context: Dict[str, Any], 
                                   include_web: bool) -> List[Dict[str, Any]]:
        """다중 소스 검색 실행
        
        Args:
            query: 검색 쿼리
            context: 검색 맥락
            include_web: 웹 검색 포함 여부
            
        Returns:
            List[Dict]: 통합 검색 결과
        """
        all_results = []
        
        try:
            # 1. ChromaDB 검색 (현재 챕터 우선)
            current_chapter = context.get('current_chapter')
            if current_chapter:
                kb_results_current = search_knowledge_base(
                    query=query,
                    chapter_id=current_chapter,
                    max_results=4
                )
                all_results.extend(kb_results_current)
            
            # 2. ChromaDB 검색 (전체 챕터)
            kb_results_all = search_knowledge_base(
                query=query,
                chapter_id=None,
                max_results=3
            )
            all_results.extend(kb_results_all)
            
            # 3. 웹 검색 (옵션)
            if include_web:
                web_results = search_web_for_answer(query, max_results=3)
                all_results.extend(web_results)
            
            # 중복 제거 (URL 또는 내용 기준)
            unique_results = self._remove_duplicates(all_results)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"다중 소스 검색 실패: {e}")
            return []
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 결과 제거
        
        Args:
            results: 원본 결과 리스트
            
        Returns:
            List[Dict]: 중복 제거된 결과
        """
        seen_contents = set()
        unique_results = []
        
        for result in results:
            # 내용 기반 중복 체크 (첫 100자)
            content = result.get('content', '')[:100].strip().lower()
            
            if content and content not in seen_contents:
                seen_contents.add(content)
                unique_results.append(result)
        
        return unique_results
    
    def _preprocess_results(self, results: List[Dict[str, Any]], 
                          context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """검색 결과 전처리 및 정규화
        
        Args:
            results: 원본 검색 결과
            context: 검색 맥락
            
        Returns:
            List[Dict]: 전처리된 결과
        """
        processed_results = []
        
        for result in results:
            processed_result = result.copy()
            
            # 1. 기본 점수 정규화
            similarity_score = result.get('similarity_score', 0.5)
            processed_result['normalized_similarity'] = min(max(similarity_score, 0), 1)
            
            # 2. 소스 신뢰도 점수 추가
            source = result.get('source', 'unknown')
            processed_result['source_reliability'] = self.source_reliability_scores.get(source, 0.5)
            
            # 3. 콘텐츠 완성도 점수 계산
            content = result.get('content', '')
            processed_result['content_completeness'] = self._calculate_completeness_score(content)
            
            # 4. 챕터 관련성 점수 계산
            processed_result['chapter_relevance'] = self._calculate_chapter_relevance(
                result, context.get('current_chapter', 1)
            )
            
            # 5. 사용자 레벨 매칭 점수 계산
            processed_result['user_level_match'] = self._calculate_level_match(
                result, context.get('user_level', 'medium')
            )
            
            # 6. 콘텐츠 신선도 점수 (웹 검색 결과에 유리)
            processed_result['content_freshness'] = self._calculate_freshness_score(result)
            
            processed_results.append(processed_result)
        
        return processed_results
    
    def _calculate_completeness_score(self, content: str) -> float:
        """콘텐츠 완성도 점수 계산
        
        Args:
            content: 콘텐츠 텍스트
            
        Returns:
            float: 완성도 점수 (0-1)
        """
        if not content:
            return 0.0
        
        # 길이 기반 점수 (50-500자가 적정)
        length = len(content)
        if length < 50:
            length_score = length / 50
        elif length > 500:
            length_score = max(0.5, 1 - (length - 500) / 1000)
        else:
            length_score = 1.0
        
        # 구조 기반 점수 (문장 구조, 구두점 등)
        sentences = content.split('.')
        structure_score = min(len(sentences) / 5, 1.0)  # 적정 문장 수
        
        # 정보 밀도 점수 (키워드 밀도)
        info_keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '프롬프트', 'ChatGPT']
        keyword_count = sum(1 for keyword in info_keywords if keyword in content)
        info_density = min(keyword_count / 3, 1.0)
        
        # 가중 평균
        completeness = (length_score * 0.4 + structure_score * 0.3 + info_density * 0.3)
        return min(completeness, 1.0)
    
    def _calculate_chapter_relevance(self, result: Dict[str, Any], current_chapter: int) -> float:
        """챕터 관련성 점수 계산
        
        Args:
            result: 검색 결과
            current_chapter: 현재 챕터
            
        Returns:
            float: 관련성 점수 (0-1)
        """
        metadata = result.get('metadata', {})
        
        if isinstance(metadata, dict):
            result_chapter = metadata.get('chapter_id')
            if result_chapter == current_chapter:
                return 1.0
            elif result_chapter and abs(result_chapter - current_chapter) <= 1:
                return 0.7  # 인접 챕터
            elif result_chapter:
                return 0.4  # 다른 챕터
        
        # 메타데이터가 없는 경우 콘텐츠 기반 추정
        content = result.get('content', '').lower()
        chapter_keywords = {
            1: ['ai', '인공지능', '머신러닝', '딥러닝'],
            3: ['프롬프트', 'prompt', 'chatgpt', 'gpt']
        }
        
        if current_chapter in chapter_keywords:
            keyword_matches = sum(1 for keyword in chapter_keywords[current_chapter] 
                                if keyword in content)
            return min(keyword_matches / len(chapter_keywords[current_chapter]), 1.0)
        
        return 0.5  # 기본값
    
    def _calculate_level_match(self, result: Dict[str, Any], user_level: str) -> float:
        """사용자 레벨 매칭 점수 계산
        
        Args:
            result: 검색 결과
            user_level: 사용자 레벨 (low, medium, high)
            
        Returns:
            float: 매칭 점수 (0-1)
        """
        metadata = result.get('metadata', {})
        
        if isinstance(metadata, dict):
            content_level = metadata.get('level', 'medium')
            if content_level == user_level:
                return 1.0
            elif (user_level == 'medium' and content_level in ['low', 'high']) or \
                 (user_level in ['low', 'high'] and content_level == 'medium'):
                return 0.7
            else:
                return 0.4
        
        # 메타데이터가 없는 경우 콘텐츠 복잡도 기반 추정
        content = result.get('content', '')
        complexity_indicators = {
            'high': ['전문적', '고급', '심화', '복잡한', '상세한'],
            'low': ['쉽게', '간단히', '기본', '초보', '입문']
        }
        
        content_lower = content.lower()
        
        if user_level == 'high':
            high_matches = sum(1 for indicator in complexity_indicators['high'] 
                             if indicator in content_lower)
            return min(high_matches / 3, 1.0) if high_matches > 0 else 0.5
        elif user_level == 'low':
            low_matches = sum(1 for indicator in complexity_indicators['low'] 
                            if indicator in content_lower)
            return min(low_matches / 3, 1.0) if low_matches > 0 else 0.5
        
        return 0.7  # medium 레벨 기본값
    
    def _calculate_freshness_score(self, result: Dict[str, Any]) -> float:
        """콘텐츠 신선도 점수 계산
        
        Args:
            result: 검색 결과
            
        Returns:
            float: 신선도 점수 (0-1)
        """
        source = result.get('source', '')
        
        # 웹 검색 결과는 더 신선하다고 가정
        if 'web_search' in source:
            return 0.9
        elif source == 'chromadb':
            return 0.6  # 내부 데이터는 상대적으로 오래됨
        else:
            return 0.5
    
    def _apply_advanced_ranking(self, results: List[Dict[str, Any]], 
                              query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """고급 랭킹 알고리즘 적용
        
        Args:
            results: 전처리된 결과
            query: 원본 쿼리
            context: 검색 맥락
            
        Returns:
            List[Dict]: 랭킹된 결과
        """
        for result in results:
            # 각 요소별 점수 계산
            similarity_score = result.get('normalized_similarity', 0.5)
            source_reliability = result.get('source_reliability', 0.5)
            content_freshness = result.get('content_freshness', 0.5)
            chapter_relevance = result.get('chapter_relevance', 0.5)
            content_completeness = result.get('content_completeness', 0.5)
            user_level_match = result.get('user_level_match', 0.5)
            
            # 가중 평균으로 최종 점수 계산
            final_score = (
                similarity_score * self.ranking_weights['similarity_score'] +
                source_reliability * self.ranking_weights['source_reliability'] +
                content_freshness * self.ranking_weights['content_freshness'] +
                chapter_relevance * self.ranking_weights['chapter_relevance'] +
                content_completeness * self.ranking_weights['content_completeness'] +
                user_level_match * self.ranking_weights['user_level_match']
            )
            
            result['advanced_ranking_score'] = min(final_score, 1.0)
        
        # 점수 기준으로 정렬
        return sorted(results, key=lambda x: x.get('advanced_ranking_score', 0), reverse=True)
    
    def _postprocess_results(self, results: List[Dict[str, Any]], 
                           query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """결과 후처리 및 메타데이터 추가
        
        Args:
            results: 랭킹된 결과
            query: 원본 쿼리
            context: 검색 맥락
            
        Returns:
            List[Dict]: 후처리된 결과
        """
        processed_results = []
        
        for i, result in enumerate(results):
            processed_result = result.copy()
            
            # 순위 정보 추가
            processed_result['rank'] = i + 1
            
            # 신뢰도 레벨 추가
            score = result.get('advanced_ranking_score', 0.5)
            if score >= 0.8:
                processed_result['confidence_level'] = 'high'
            elif score >= 0.6:
                processed_result['confidence_level'] = 'medium'
            else:
                processed_result['confidence_level'] = 'low'
            
            # 추천 이유 생성
            processed_result['recommendation_reason'] = self._generate_recommendation_reason(result)
            
            processed_results.append(processed_result)
        
        return processed_results
    
    def _generate_recommendation_reason(self, result: Dict[str, Any]) -> str:
        """추천 이유 생성
        
        Args:
            result: 검색 결과
            
        Returns:
            str: 추천 이유
        """
        reasons = []
        
        # 높은 점수 요소들 확인
        if result.get('chapter_relevance', 0) >= 0.8:
            reasons.append("현재 학습 챕터와 직접 관련")
        
        if result.get('source_reliability', 0) >= 0.8:
            reasons.append("신뢰할 수 있는 내부 자료")
        
        if result.get('user_level_match', 0) >= 0.8:
            reasons.append("사용자 수준에 적합")
        
        if result.get('content_completeness', 0) >= 0.8:
            reasons.append("상세하고 완성도 높은 내용")
        
        if result.get('content_freshness', 0) >= 0.8:
            reasons.append("최신 정보 포함")
        
        if not reasons:
            reasons.append("검색 쿼리와 관련성 높음")
        
        return ", ".join(reasons)
    
    def _evaluate_search_quality(self, results: List[Dict[str, Any]], query: str) -> float:
        """검색 품질 평가
        
        Args:
            results: 최종 검색 결과
            query: 원본 쿼리
            
        Returns:
            float: 품질 점수 (0-1)
        """
        if not results:
            return 0.0
        
        # 상위 결과들의 평균 점수
        top_scores = [r.get('advanced_ranking_score', 0.5) for r in results[:3]]
        avg_top_score = sum(top_scores) / len(top_scores)
        
        # 결과 다양성 점수 (서로 다른 소스)
        sources = set(r.get('source', 'unknown') for r in results)
        diversity_score = min(len(sources) / 3, 1.0)
        
        # 전체 품질 점수
        quality_score = (avg_top_score * 0.7 + diversity_score * 0.3)
        
        return min(quality_score, 1.0)
    
    def _get_error_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """오류 결과 반환
        
        Args:
            query: 원본 쿼리
            error_message: 오류 메시지
            
        Returns:
            Dict: 오류 결과
        """
        return {
            'query': query,
            'total_found': 0,
            'returned_count': 0,
            'results': [],
            'search_quality_score': 0.0,
            'error': True,
            'error_message': error_message,
            'search_metadata': {
                'search_timestamp': datetime.now().isoformat()
            }
        }

# 전역 고급 검색 도구 인스턴스
advanced_search_tool = AdvancedSearchTool()

def perform_advanced_search(query: str, context: Dict[str, Any], 
                          options: Dict[str, Any] = None) -> Dict[str, Any]:
    """고급 검색 수행 (편의 함수)
    
    Args:
        query: 검색 쿼리
        context: 검색 맥락
        options: 검색 옵션
        
    Returns:
        Dict: 고급 검색 결과
    """
    return advanced_search_tool.advanced_search(query, context, options)