# tools/external/adaptive_search_strategy.py
# 적응형 검색 전략 관리

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AdaptiveSearchStrategy:
    """적응형 검색 전략 클래스"""
    
    def __init__(self, web_search_tool):
        """적응형 검색 전략 초기화
        
        Args:
            web_search_tool: WebSearchTool 인스턴스
        """
        self.web_search_tool = web_search_tool
        
    def search_adaptive(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """적응형 검색 (품질에 따라 전략 조정)
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: 최적화된 검색 결과
        """
        # 1. DuckDuckGo로 빠른 검색
        ddg_results = []
        try:
            ddg_results = self.web_search_tool._search_duckduckgo(query, min(num_results, 3))
            quality_score = self.evaluate_search_quality(ddg_results, query)
            logger.info(f"DuckDuckGo 적응형 검색 품질: {quality_score:.2f}")
            
            # 품질이 매우 좋으면 DuckDuckGo 결과만 사용
            if quality_score >= 0.8:
                logger.info("DuckDuckGo 결과 품질이 우수하여 Tavily 검색 생략")
                return ddg_results[:num_results]
                
        except Exception as e:
            logger.error(f"적응형 검색 - DuckDuckGo 실패: {e}")
        
        # 2. 품질이 부족하면 Tavily로 보완 또는 대체
        if self.web_search_tool.tavily_available:
            try:
                if ddg_results and self.evaluate_search_quality(ddg_results, query) >= 0.4:
                    # DuckDuckGo 결과가 어느 정도 있으면 Tavily로 보완
                    remaining = num_results - len(ddg_results)
                    if remaining > 0:
                        tavily_results = self.web_search_tool._search_tavily(query, remaining)
                        unique_tavily = self.remove_duplicate_results(tavily_results, ddg_results)
                        ddg_results.extend(unique_tavily)
                        logger.info("DuckDuckGo + Tavily 하이브리드 검색 완료")
                else:
                    # DuckDuckGo 결과가 부족하면 Tavily 위주로 검색
                    tavily_results = self.web_search_tool._search_tavily(query, num_results)
                    if tavily_results:
                        logger.info("Tavily 위주 검색으로 전환")
                        return tavily_results[:num_results]
                        
            except Exception as e:
                logger.error(f"적응형 검색 - Tavily 실패: {e}")
        
        # 3. 결과 반환
        if ddg_results:
            return ddg_results[:num_results]
        else:
            return self.web_search_tool._get_fallback_results(query)
    
    def evaluate_search_quality(self, results: List[Dict[str, Any]], query: str) -> float:
        """검색 결과 품질 평가
        
        Args:
            results: 검색 결과 리스트
            query: 원본 검색 쿼리
            
        Returns:
            float: 품질 점수 (0-1)
        """
        if not results:
            return 0.0
        
        total_score = 0.0
        valid_results = 0
        
        for result in results:
            score = 0.0
            
            # 1. 제목과 스니펫이 있는지 확인
            title = result.get('title', '').strip()
            snippet = result.get('snippet', '').strip()
            link = result.get('link', '').strip()
            
            if title and len(title) > 10:
                score += 0.3
            if snippet and len(snippet) > 20:
                score += 0.3
            if link and link.startswith('http'):
                score += 0.2
            
            # 2. 더미 결과가 아닌지 확인
            source = result.get('source', '')
            if 'dummy' not in source and 'fallback' not in source:
                score += 0.2
            
            # 3. 쿼리와의 관련성 확인 (간단한 키워드 매칭)
            query_words = query.lower().split()
            text_content = (title + ' ' + snippet).lower()
            
            matching_words = sum(1 for word in query_words if word in text_content)
            if query_words:
                relevance = matching_words / len(query_words)
                score += relevance * 0.3
            
            total_score += min(score, 1.0)
            valid_results += 1
        
        # 평균 품질 점수 계산
        if valid_results > 0:
            avg_score = total_score / valid_results
            
            # 결과 수에 따른 보너스 (최소 3개 이상이면 보너스)
            if len(results) >= 3:
                avg_score += 0.1
            
            return min(avg_score, 1.0)
        
        return 0.0
    
    def remove_duplicate_results(self, new_results: List[Dict[str, Any]], 
                                existing_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 검색 결과 제거
        
        Args:
            new_results: 새로운 검색 결과
            existing_results: 기존 검색 결과
            
        Returns:
            List[Dict]: 중복이 제거된 새로운 결과
        """
        if not existing_results:
            return new_results
        
        # 기존 결과의 링크와 제목 수집
        existing_links = {result.get('link', '').lower() for result in existing_results}
        existing_titles = {result.get('title', '').lower() for result in existing_results}
        
        unique_results = []
        
        for result in new_results:
            link = result.get('link', '').lower()
            title = result.get('title', '').lower()
            
            # 링크나 제목이 중복되지 않으면 추가
            if link not in existing_links and title not in existing_titles:
                unique_results.append(result)
                existing_links.add(link)
                existing_titles.add(title)
        
        return unique_results
    
    def get_search_strategy_recommendation(self, query: str, context: Dict[str, Any] = None) -> str:
        """검색 쿼리에 따른 최적 전략 추천
        
        Args:
            query: 검색 쿼리
            context: 추가 컨텍스트 정보
            
        Returns:
            str: 추천 검색 전략 ('adaptive', 'tavily_only', 'duckduckgo_only')
        """
        query_lower = query.lower()
        
        # AI 관련 쿼리는 Tavily 우선
        ai_keywords = ['ai', '인공지능', 'chatgpt', 'gpt', '머신러닝', '딥러닝', 'llm']
        if any(keyword in query_lower for keyword in ai_keywords):
            if self.web_search_tool.tavily_available:
                return 'tavily_only'
        
        # 최신 정보가 필요한 쿼리는 Tavily 우선
        recent_keywords = ['최신', '2024', '2025', '뉴스', '업데이트', '새로운']
        if any(keyword in query_lower for keyword in recent_keywords):
            if self.web_search_tool.tavily_available:
                return 'tavily_only'
        
        # 일반적인 정보 검색은 적응형
        return 'adaptive'
    
    def search_with_strategy(self, query: str, strategy: str = 'adaptive', 
                           num_results: int = 5) -> List[Dict[str, Any]]:
        """지정된 전략으로 검색 수행
        
        Args:
            query: 검색 쿼리
            strategy: 검색 전략 ('adaptive', 'tavily_only', 'duckduckgo_only')
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        if strategy == 'tavily_only':
            return self.web_search_tool.search_with_tavily_only(query, num_results)
        elif strategy == 'duckduckgo_only':
            return self.web_search_tool.search_with_duckduckgo_only(query, num_results)
        else:  # adaptive
            return self.search_adaptive(query, num_results)
    
    def analyze_search_performance(self, results: List[Dict[str, Any]], 
                                 query: str) -> Dict[str, Any]:
        """검색 성능 분석
        
        Args:
            results: 검색 결과
            query: 검색 쿼리
            
        Returns:
            Dict: 성능 분석 결과
        """
        if not results:
            return {
                'quality_score': 0.0,
                'result_count': 0,
                'sources': [],
                'has_errors': True,
                'recommendation': 'try_different_query'
            }
        
        # 소스별 결과 수 계산
        sources = {}
        error_count = 0
        
        for result in results:
            source = result.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            
            if result.get('error', False):
                error_count += 1
        
        quality_score = self.evaluate_search_quality(results, query)
        
        # 추천사항 결정
        recommendation = 'good'
        if quality_score < 0.3:
            recommendation = 'try_tavily_search'
        elif quality_score < 0.6:
            recommendation = 'try_different_keywords'
        
        return {
            'quality_score': quality_score,
            'result_count': len(results),
            'sources': sources,
            'has_errors': error_count > 0,
            'error_count': error_count,
            'recommendation': recommendation,
            'avg_snippet_length': sum(len(r.get('snippet', '')) for r in results) / len(results) if results else 0
        }