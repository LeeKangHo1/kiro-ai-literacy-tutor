# docs/web_search_setup.md
# 웹 검색 설정 가이드

## 개요

AI 리터러시 네비게이터의 QnA 에이전트는 Tavily API와 DuckDuckGo를 사용하여 웹 검색을 수행합니다.

## 지원하는 검색 엔진

### 1. Tavily API (권장)
- **장점**: 고품질 검색 결과, AI 최적화된 콘텐츠
- **단점**: API 키 필요, 유료 서비스
- **설정**: `.env` 파일에 `TAVILY_API_KEY` 추가

### 2. DuckDuckGo
- **장점**: 무료, API 키 불필요
- **단점**: 제한된 검색 결과
- **설정**: 별도 설정 불필요

## 설정 방법

### 1. Tavily API 키 설정 (권장)

1. [Tavily 웹사이트](https://tavily.com)에서 계정 생성
2. API 키 발급
3. `.env` 파일에 다음 추가:
```env
TAVILY_API_KEY=your_actual_tavily_api_key_here
```

### 2. 패키지 설치

```bash
pip install tavily-python==0.7.10
```

또는 requirements.txt를 통해:
```bash
pip install -r requirements.txt
```

## 검색 전략

### 적응형 검색 (기본값)
1. DuckDuckGo로 무료 검색 먼저 시도
2. 검색 결과 품질 자동 평가 (0-1 점수)
3. 품질이 낮으면 Tavily API로 보완
4. 중복 결과 자동 제거
5. ChromaDB 지식 베이스와 결합

### 전략 자동 추천 시스템
- **AI 관련 쿼리**: Tavily 우선 사용
- **최신 정보 쿼리**: Tavily 우선 사용  
- **일반 정보 쿼리**: 적응형 검색 사용
- **비용 절약 모드**: DuckDuckGo 전용

### DuckDuckGo 우선 검색
- 무료 검색을 우선적으로 사용
- Abstract, Answer, Definition 등 다양한 결과 타입
- 한국어 특화 검색 지원
- 품질 평가를 통한 자동 보완

### Tavily 전용 검색
- 고품질 AI 최적화 검색 결과
- API 키가 설정된 경우에만 사용 가능
- 유료 서비스이지만 최고 품질

### DuckDuckGo 전용 검색
- 완전 무료 검색
- Tavily API 없이도 사용 가능
- 기본적인 검색 요구사항 충족

## 사용 예시

```python
from tools.external.web_search_tool import WebSearchTool

# 검색 도구 초기화
search_tool = WebSearchTool()

# 적응형 검색 (기본값 - DuckDuckGo 우선, 필요시 Tavily 보완)
results = search_tool.search_adaptive("ChatGPT 사용법", num_results=5)

# 일반 웹 검색 (DuckDuckGo 우선)
results = search_tool.search_web("ChatGPT 사용법", num_results=5)

# AI 관련 특화 검색
ai_results = search_tool.search_ai_related("프롬프트 엔지니어링", num_results=3)

# DuckDuckGo 전용 검색 (무료)
ddg_results = search_tool.search_with_duckduckgo_only("머신러닝 기초", num_results=5)

# Tavily 전용 검색 (고품질)
tavily_results = search_tool.search_with_tavily_only("머신러닝 기초", num_results=5)

# 전략 추천 받기
strategy = search_tool.get_search_strategy_recommendation("최신 AI 뉴스")
print(f"추천 전략: {strategy}")

# 추천 전략으로 검색
recommended_results = search_tool.search_with_strategy("최신 AI 뉴스", strategy, num_results=5)

# 검색 성능 분석
performance = search_tool.analyze_search_performance(results, "ChatGPT 사용법")
print(f"품질 점수: {performance['quality_score']:.2f}")
print(f"소스별 결과: {performance['sources']}")
print(f"추천사항: {performance['recommendation']}")
```

## 검색 결과 형식

```python
{
    'title': '검색 결과 제목',
    'snippet': '검색 결과 요약',
    'link': 'https://example.com',
    'source': 'tavily' | 'duckduckgo_abstract' | 'duckduckgo_related',
    'search_query': '원본 검색 쿼리',
    'timestamp': '2025-01-27T...',
    'score': 0.85,  # Tavily 결과에만 포함
    'ai_relevance_score': 0.75  # AI 관련 검색에만 포함
}
```

## 문제 해결

### Tavily API 오류
- API 키가 올바른지 확인
- API 사용량 한도 확인
- 네트워크 연결 상태 확인

### DuckDuckGo 검색 실패
- 일반적으로 자동으로 더미 결과 반환
- 네트워크 연결 상태 확인

### 검색 결과가 없는 경우
- 검색 쿼리를 더 구체적으로 변경
- 다른 검색 전략 시도
- ChromaDB 지식 베이스 활용

## 성능 최적화

1. **적응형 검색 사용**: DuckDuckGo 우선으로 비용 절약
2. **품질 기반 자동 전환**: 필요할 때만 Tavily API 사용
3. **적절한 결과 수 설정**: 너무 많은 결과는 성능 저하
4. **캐싱 활용**: 동일한 쿼리 반복 검색 방지
5. **중복 제거**: 다양한 소스 결합 시 중복 결과 자동 제거

## 비용 관리

- **DuckDuckGo 우선 전략**: 대부분의 검색을 무료로 처리
- **품질 기반 Tavily 사용**: 필요할 때만 유료 API 호출
- **적응형 검색**: 자동으로 최적의 비용/품질 균형 유지
- **검색 결과 품질 평가**: 불필요한 API 호출 방지