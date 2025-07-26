# tools/external/web_search_tool.py
# 웹 검색 도구

import requests
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import quote_plus
import json
import os
from datetime import datetime
from .error_handler import handle_service_error, ServiceType, ErrorSeverity

logger = logging.getLogger(__name__)

class WebSearchTool:
    """웹 검색 도구 (Google Custom Search API 사용)"""
    
    def __init__(self):
        """웹 검색 도구 초기화"""
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # API 키가 없는 경우 더미 모드로 동작
        self.dummy_mode = not (self.api_key and self.search_engine_id)
        
        if self.dummy_mode:
            logger.warning("Google Search API 키가 설정되지 않음. 더미 모드로 동작합니다.")
    
    def search_web(self, query: str, num_results: int = 5, 
                   language: str = 'ko') -> List[Dict[str, Any]]:
        """웹에서 정보 검색
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 수 (최대 10)
            language: 검색 언어
            
        Returns:
            List[Dict]: 검색 결과
        """
        try:
            if self.dummy_mode:
                return self._get_dummy_results(query, num_results)
            
            # API 파라미터 설정
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10),  # Google API 최대 10개
                'lr': f'lang_{language}',
                'safe': 'active'
            }
            
            # API 호출
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 결과 포맷팅
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'source': 'web_search',
                        'search_query': query,
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.info(f"웹 검색 완료: {len(results)}개 결과 반환")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"웹 검색 API 호출 실패: {e}")
            
            # 오류 처리 시스템에 기록 및 대체 응답 반환
            fallback_result = handle_service_error(
                service_type=ServiceType.WEB_SEARCH,
                error_code="api_request_failed",
                error_message=str(e),
                context={"operation": "web_search", "query": query, "num_results": num_results},
                severity=ErrorSeverity.MEDIUM
            )
            
            # 대체 응답이 있으면 반환
            if fallback_result.get("is_fallback") and fallback_result.get("results"):
                return fallback_result["results"]
            
            return self._get_fallback_results(query)
            
        except Exception as e:
            logger.error(f"웹 검색 실패: {e}")
            
            # 오류 처리 시스템에 기록 및 대체 응답 반환
            fallback_result = handle_service_error(
                service_type=ServiceType.WEB_SEARCH,
                error_code="search_failed",
                error_message=str(e),
                context={"operation": "web_search", "query": query, "num_results": num_results},
                severity=ErrorSeverity.MEDIUM
            )
            
            # 대체 응답이 있으면 반환
            if fallback_result.get("is_fallback") and fallback_result.get("results"):
                return fallback_result["results"]
            
            return self._get_fallback_results(query)
    
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
    
    def _get_dummy_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """더미 검색 결과 생성 (API 키가 없을 때)
        
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
                'snippet': f'{query}와 관련된 유용한 정보입니다. 이는 더미 데이터이며, 실제 웹 검색을 위해서는 Google Search API 키가 필요합니다.',
                'link': f'https://example.com/search-result-{i+1}',
                'source': 'web_search_dummy',
                'search_query': query,
                'timestamp': datetime.now().isoformat(),
                'note': 'Google Search API 키가 설정되지 않아 더미 결과입니다.'
            })
        
        return dummy_results
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        """검색 실패 시 대체 결과
        
        Args:
            query: 검색 쿼리
            
        Returns:
            List[Dict]: 대체 결과
        """
        return [{
            'title': '검색 서비스 일시 중단',
            'snippet': f'"{query}"에 대한 웹 검색이 일시적으로 불가능합니다. 나중에 다시 시도해주세요.',
            'link': '',
            'source': 'web_search_fallback',
            'search_query': query,
            'timestamp': datetime.now().isoformat(),
            'error': True
        }]

# 전역 웹 검색 도구 인스턴스
web_search_tool = WebSearchTool()

def search_web_for_answer(question: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """질문에 대한 웹 검색 수행
    
    Args:
        question: 검색할 질문
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    return web_search_tool.search_ai_related(question, max_results)

def search_general_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """일반 웹 검색 수행
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        
    Returns:
        List[Dict]: 검색 결과
    """
    return web_search_tool.search_web(query, max_results)