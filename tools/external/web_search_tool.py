# tools/external/web_search_tool.py
# 웹 검색 도구 (Tavily + DuckDuckGo)

import requests
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import quote_plus
import json
import os
from datetime import datetime
from .error_handler import handle_service_error, ServiceType, ErrorSeverity

# Tavily 패키지 임포트 (선택적)
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("tavily-python 패키지가 설치되지 않음. requests로 직접 API 호출합니다.")

logger = logging.getLogger(__name__)

class WebSearchTool:
    """웹 검색 도구 (DuckDuckGo 우선, Tavily API 보완)"""
    
    def __init__(self):
        """웹 검색 도구 초기화"""
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.tavily_base_url = "https://api.tavily.com/search"
        
        # Tavily API 키 확인
        self.tavily_available = bool(
            self.tavily_api_key and 
            self.tavily_api_key != 'your_tavily_api_key_here' and
            TAVILY_AVAILABLE
        )
        
        # Tavily 클라이언트 초기화 (가능한 경우)
        self.tavily_client = None
        if self.tavily_available and TAVILY_AVAILABLE:
            try:
                self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
                logger.info("Tavily 클라이언트 초기화 완료")
            except Exception as e:
                logger.error(f"Tavily 클라이언트 초기화 실패: {e}")
                self.tavily_available = False
        
        if not self.tavily_available:
            logger.warning("Tavily API를 사용할 수 없습니다. DuckDuckGo만 사용합니다.")
        
        # DuckDuckGo는 별도 설정 불필요
        logger.info("웹 검색 도구 초기화 완료 (DuckDuckGo 우선, Tavily 보완)")
    
    def search_web(self, query: str, num_results: int = 5, 
                   language: str = 'ko') -> List[Dict[str, Any]]:
        """웹에서 정보 검색 (DuckDuckGo 우선, Tavily 보완)
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            language: 검색 언어
            
        Returns:
            List[Dict]: 검색 결과
        """
        results = []
        
        # 1. DuckDuckGo 검색 먼저 시도 (무료)
        try:
            ddg_results = self._search_duckduckgo(query, num_results)
            results.extend(ddg_results)
            logger.info(f"DuckDuckGo 검색 완료: {len(ddg_results)}개 결과")
            
            # DuckDuckGo 결과 품질 평가
            quality_score = self._evaluate_search_quality(ddg_results, query)
            logger.info(f"DuckDuckGo 검색 품질 점수: {quality_score:.2f}")
            
            # 품질이 좋으면 DuckDuckGo 결과만 사용
            if quality_score >= 0.6 and len(ddg_results) >= min(num_results, 3):
                logger.info("DuckDuckGo 검색 결과 품질이 충분합니다.")
                return results[:num_results]
                
        except Exception as e:
            logger.error(f"DuckDuckGo 검색 실패: {e}")
        
        # 2. DuckDuckGo 결과가 부족하거나 품질이 낮으면 Tavily로 보완
        if self.tavily_available:
            remaining_results = num_results - len(results)
            if remaining_results > 0 or len(results) == 0:
                try:
                    tavily_results = self._search_tavily(query, max(remaining_results, 3))
                    
                    # 중복 제거하면서 추가
                    unique_tavily_results = self._remove_duplicate_results(tavily_results, results)
                    results.extend(unique_tavily_results)
                    logger.info(f"Tavily 검색으로 보완: {len(unique_tavily_results)}개 결과 추가")
                    
                except Exception as e:
                    logger.error(f"Tavily 검색 실패: {e}")
        
        # 3. 결과가 없으면 대체 결과 반환
        if not results:
            return self._get_fallback_results(query)
        
        logger.info(f"웹 검색 완료: 총 {len(results)}개 결과 반환")
        return results[:num_results]
    
    def _search_tavily(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Tavily API를 사용한 검색
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            List[Dict]: Tavily 검색 결과
        """
        try:
            # Tavily 클라이언트가 있으면 사용
            if self.tavily_client:
                response = self.tavily_client.search(
                    query=query,
                    search_depth="basic",
                    include_answer=True,
                    include_images=False,
                    include_raw_content=False,
                    max_results=num_results
                )
                
                results = []
                if 'results' in response:
                    for item in response['results']:
                        results.append({
                            'title': item.get('title', ''),
                            'snippet': item.get('content', ''),
                            'link': item.get('url', ''),
                            'source': 'tavily',
                            'search_query': query,
                            'timestamp': datetime.now().isoformat(),
                            'score': item.get('score', 0.0)
                        })
                
                return results
            
            # 클라이언트가 없으면 직접 API 호출
            else:
                headers = {
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'api_key': self.tavily_api_key,
                    'query': query,
                    'search_depth': 'basic',
                    'include_answer': True,
                    'include_images': False,
                    'include_raw_content': False,
                    'max_results': num_results,
                    'include_domains': [],
                    'exclude_domains': []
                }
                
                response = requests.post(
                    self.tavily_base_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                # Tavily 결과 포맷팅
                if 'results' in data:
                    for item in data['results']:
                        results.append({
                            'title': item.get('title', ''),
                            'snippet': item.get('content', ''),
                            'link': item.get('url', ''),
                            'source': 'tavily',
                            'search_query': query,
                            'timestamp': datetime.now().isoformat(),
                            'score': item.get('score', 0.0)
                        })
                
                return results
            
        except Exception as e:
            logger.error(f"Tavily 검색 실패: {e}")
            raise
    
    def _search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """DuckDuckGo를 사용한 검색 (개선된 버전)
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            List[Dict]: DuckDuckGo 검색 결과
        """
        try:
            results = []
            
            # 1. DuckDuckGo Instant Answer API 사용
            ddg_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(ddg_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Abstract 정보가 있으면 추가 (고품질 결과)
            if data.get('Abstract') and len(data.get('Abstract', '').strip()) > 50:
                results.append({
                    'title': data.get('Heading', query),
                    'snippet': data.get('Abstract', ''),
                    'link': data.get('AbstractURL', ''),
                    'source': 'duckduckgo_abstract',
                    'search_query': query,
                    'timestamp': datetime.now().isoformat(),
                    'quality_score': 0.8  # Abstract는 높은 품질
                })
            
            # Answer 정보가 있으면 추가
            if data.get('Answer') and len(data.get('Answer', '').strip()) > 20:
                results.append({
                    'title': f"{query} - 답변",
                    'snippet': data.get('Answer', ''),
                    'link': data.get('AnswerURL', ''),
                    'source': 'duckduckgo_answer',
                    'search_query': query,
                    'timestamp': datetime.now().isoformat(),
                    'quality_score': 0.9  # Answer는 최고 품질
                })
            
            # Definition 정보가 있으면 추가
            if data.get('Definition') and len(data.get('Definition', '').strip()) > 30:
                results.append({
                    'title': f"{query} - 정의",
                    'snippet': data.get('Definition', ''),
                    'link': data.get('DefinitionURL', ''),
                    'source': 'duckduckgo_definition',
                    'search_query': query,
                    'timestamp': datetime.now().isoformat(),
                    'quality_score': 0.7
                })
            
            # Related Topics 추가 (품질 필터링)
            for topic in data.get('RelatedTopics', [])[:num_results-len(results)]:
                if isinstance(topic, dict) and 'Text' in topic:
                    text = topic.get('Text', '').strip()
                    if len(text) > 30:  # 최소 길이 필터
                        # 제목 추출 (첫 번째 문장 또는 100자)
                        title = text.split('.')[0] if '.' in text else text[:100]
                        if len(title) < 20:
                            title = text[:100]
                        
                        results.append({
                            'title': title + ('...' if len(title) == 100 else ''),
                            'snippet': text,
                            'link': topic.get('FirstURL', ''),
                            'source': 'duckduckgo_related',
                            'search_query': query,
                            'timestamp': datetime.now().isoformat(),
                            'quality_score': 0.5
                        })
            
            # Results 섹션도 확인 (추가 결과)
            for result in data.get('Results', [])[:num_results-len(results)]:
                if isinstance(result, dict) and result.get('Text'):
                    text = result.get('Text', '').strip()
                    if len(text) > 30:
                        results.append({
                            'title': text[:100] + ('...' if len(text) > 100 else ''),
                            'snippet': text,
                            'link': result.get('FirstURL', ''),
                            'source': 'duckduckgo_results',
                            'search_query': query,
                            'timestamp': datetime.now().isoformat(),
                            'quality_score': 0.6
                        })
            
            # 품질 점수로 정렬
            results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            # 결과가 여전히 부족하면 한국어 특화 검색 시도
            if len(results) < 2:
                korean_results = self._search_duckduckgo_korean(query, num_results - len(results))
                results.extend(korean_results)
            
            return results[:num_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo 검색 실패: {e}")
            # DuckDuckGo 실패 시 한국어 특화 검색 시도
            try:
                return self._search_duckduckgo_korean(query, num_results)
            except:
                return self._get_duckduckgo_dummy_results(query, num_results)
    
    def _search_duckduckgo_korean(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """한국어 특화 DuckDuckGo 검색
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            List[Dict]: 한국어 특화 검색 결과
        """
        try:
            # 한국어 키워드 추가
            korean_query = f"{query} 한국어 설명"
            
            ddg_url = "https://api.duckduckgo.com/"
            params = {
                'q': korean_query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(ddg_url, params=params, timeout=8)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # 한국어 결과 우선 처리
            if data.get('Abstract'):
                results.append({
                    'title': f"{query} (한국어 정보)",
                    'snippet': data.get('Abstract', ''),
                    'link': data.get('AbstractURL', ''),
                    'source': 'duckduckgo_korean',
                    'search_query': query,
                    'timestamp': datetime.now().isoformat(),
                    'quality_score': 0.6
                })
            
            return results[:num_results]
            
        except Exception as e:
            logger.error(f"한국어 특화 DuckDuckGo 검색 실패: {e}")
            return []
    
    def _get_duckduckgo_dummy_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo 더미 검색 결과 생성
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            List[Dict]: 더미 검색 결과
        """
        dummy_results = []
        
        for i in range(min(num_results, 3)):
            dummy_results.append({
                'title': f'{query} 관련 정보 {i+1}',
                'snippet': f'{query}에 대한 유용한 정보를 찾을 수 있습니다. DuckDuckGo 검색 결과입니다.',
                'link': f'https://duckduckgo.com/?q={quote_plus(query)}',
                'source': 'duckduckgo_dummy',
                'search_query': query,
                'timestamp': datetime.now().isoformat(),
                'note': 'DuckDuckGo API 제한으로 인한 더미 결과입니다.'
            })
        
        return dummy_results
    
    def search_ai_related(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """AI 관련 정보 특화 검색
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: AI 관련 검색 결과
        """
        # AI 관련 키워드 추가
        enhanced_query = f"{query} AI 인공지능 머신러닝"
        
        results = self.search_web(enhanced_query, num_results)
        
        # AI 관련성 점수 추가
        for result in results:
            result['ai_relevance_score'] = self._calculate_ai_relevance(
                result.get('title', '') + ' ' + result.get('snippet', '')
            )
        
        # AI 관련성 점수로 정렬
        results.sort(key=lambda x: x.get('ai_relevance_score', 0), reverse=True)
        
        return results
    
    def search_with_tavily_only(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Tavily만 사용한 검색 (고품질 결과 필요시)
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: Tavily 검색 결과
        """
        if not self.tavily_available:
            logger.warning("Tavily API를 사용할 수 없습니다. 일반 검색으로 대체합니다.")
            return self.search_web(query, num_results)
        
        try:
            return self._search_tavily(query, num_results)
        except Exception as e:
            logger.error(f"Tavily 전용 검색 실패: {e}")
            return self._get_fallback_results(query)
    
    def search_with_duckduckgo_only(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """DuckDuckGo만 사용한 검색 (무료 검색)
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: DuckDuckGo 검색 결과
        """
        try:
            return self._search_duckduckgo(query, num_results)
        except Exception as e:
            logger.error(f"DuckDuckGo 전용 검색 실패: {e}")
            return self._get_fallback_results(query)
    
    def get_search_strategy_recommendation(self, query: str, context: Dict[str, Any] = None) -> str:
        """검색 쿼리에 따른 최적 전략 추천
        
        Args:
            query: 검색 쿼리
            context: 추가 컨텍스트 정보
            
        Returns:
            str: 추천 검색 전략
        """
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.get_search_strategy_recommendation(query, context)
    
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
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.search_with_strategy(query, strategy, num_results)
    
    def analyze_search_performance(self, results: List[Dict[str, Any]], 
                                 query: str) -> Dict[str, Any]:
        """검색 성능 분석
        
        Args:
            results: 검색 결과
            query: 검색 쿼리
            
        Returns:
            Dict: 성능 분석 결과
        """
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.analyze_search_performance(results, query)
    
    def search_adaptive(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """적응형 검색 (품질에 따라 전략 조정)
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수
            
        Returns:
            List[Dict]: 최적화된 검색 결과
        """
        # 적응형 검색 전략 클래스에 위임
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.search_adaptive(query, num_results)
    
    def _evaluate_search_quality(self, results: List[Dict[str, Any]], query: str) -> float:
        """검색 결과 품질 평가 (적응형 검색 전략에 위임)
        
        Args:
            results: 검색 결과 리스트
            query: 원본 검색 쿼리
            
        Returns:
            float: 품질 점수 (0-1)
        """
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.evaluate_search_quality(results, query)
    
    def _remove_duplicate_results(self, new_results: List[Dict[str, Any]], 
                                existing_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """중복 검색 결과 제거 (적응형 검색 전략에 위임)
        
        Args:
            new_results: 새로운 검색 결과
            existing_results: 기존 검색 결과
            
        Returns:
            List[Dict]: 중복이 제거된 새로운 결과
        """
        if not hasattr(self, '_adaptive_strategy'):
            from .adaptive_search_strategy import AdaptiveSearchStrategy
            self._adaptive_strategy = AdaptiveSearchStrategy(self)
        
        return self._adaptive_strategy.remove_duplicate_results(new_results, existing_results)
    
    def _calculate_ai_relevance(self, text: str) -> float:
        """텍스트의 AI 관련성 점수 계산
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            float: 관련성 점수 (0-1)
        """
        ai_keywords = [
            'AI', '인공지능', '머신러닝', '딥러닝', 'ChatGPT', 'GPT',
            '프롬프트', '언어모델', 'LLM', '자연어처리', 'NLP',
            '신경망', '알고리즘', '데이터', '학습', '예측'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in ai_keywords if keyword.lower() in text_lower)
        
        # 키워드 밀도 기반 점수 계산
        relevance_score = min(keyword_count / len(ai_keywords), 1.0)
        
        return relevance_score
    
    def _get_combined_dummy_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """통합 더미 검색 결과 생성 (모든 검색이 실패했을 때)
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            List[Dict]: 더미 검색 결과
        """
        dummy_results = []
        
        for i in range(min(num_results, 3)):
            dummy_results.append({
                'title': f'{query}에 대한 정보 {i+1}',
                'snippet': f'{query}와 관련된 유용한 정보입니다. Tavily 또는 DuckDuckGo 검색 서비스를 통해 더 정확한 정보를 얻을 수 있습니다.',
                'link': f'https://duckduckgo.com/?q={quote_plus(query)}',
                'source': 'web_search_dummy',
                'search_query': query,
                'timestamp': datetime.now().isoformat(),
                'note': '검색 서비스 일시 중단으로 인한 더미 결과입니다.'
            })
        
        return dummy_results
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        """검색 실패 시 대체 결과
        
        Args:
            query: 검색 쿼리
            
        Returns:
            List[Dict]: 대체 결과
        """
        try:
            # 오류 처리 시스템에 기록
            fallback_result = handle_service_error(
                service_type=ServiceType.WEB_SEARCH,
                error_code="all_search_failed",
                error_message="Tavily와 DuckDuckGo 검색 모두 실패",
                context={"operation": "web_search_fallback", "query": query},
                severity=ErrorSeverity.MEDIUM
            )
            
            # 대체 응답이 있으면 반환
            if fallback_result.get("is_fallback") and fallback_result.get("results"):
                return fallback_result["results"]
        except:
            pass
        
        # 기본 대체 결과
        return [{
            'title': '검색 서비스 일시 중단',
            'snippet': f'"{query}"에 대한 웹 검색이 일시적으로 불가능합니다. Tavily API 키를 설정하거나 나중에 다시 시도해주세요.',
            'link': f'https://duckduckgo.com/?q={quote_plus(query)}',
            'source': 'web_search_fallback',
            'search_query': query,
            'timestamp': datetime.now().isoformat(),
            'error': True,
            'suggestion': 'Tavily API 키를 .env 파일에 설정하면 더 나은 검색 결과를 얻을 수 있습니다.'
        }]

# 전역 웹 검색 도구 인스턴스
web_search_tool = WebSearchTool()

def search_web_for_answer(question: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """질문에 대한 웹 검색 수행 (AI 관련 특화)
    
    Args:
        question: 검색할 질문
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    return web_search_tool.search_ai_related(question, max_results)

def search_general_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """일반 웹 검색 수행 (적응형 검색)
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    return web_search_tool.search_adaptive(query, max_results)

def search_with_recommended_strategy(query: str, max_results: int = 5, 
                                   context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """추천 전략으로 웹 검색 수행
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        context: 추가 컨텍스트 정보
        
    Returns:
        List[Dict]: 검색 결과
    """
    strategy = web_search_tool.get_search_strategy_recommendation(query, context)
    return web_search_tool.search_with_strategy(query, strategy, max_results)