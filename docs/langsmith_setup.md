# LangSmith 설정 가이드

이 문서는 AI Literacy Navigator 프로젝트에서 LangSmith를 설정하고 사용하는 방법을 설명합니다.

## 📋 목차

1. [LangSmith란?](#langsmith란)
2. [설정 방법](#설정-방법)
3. [환경 변수 설정](#환경-변수-설정)
4. [사용 방법](#사용-방법)
5. [API 엔드포인트](#api-엔드포인트)
6. [모니터링 및 디버깅](#모니터링-및-디버깅)
7. [문제 해결](#문제-해결)

## 🔍 LangSmith란?

LangSmith는 LangChain 애플리케이션의 모니터링, 디버깅, 테스팅을 위한 플랫폼입니다.

### 주요 기능
- **실행 추적**: 에이전트 실행 과정을 상세히 추적
- **성능 모니터링**: 응답 시간, 토큰 사용량 등 성능 지표 수집
- **오류 디버깅**: 실행 중 발생한 오류를 상세히 분석
- **사용자 피드백**: 사용자 평가 및 피드백 수집
- **A/B 테스팅**: 다양한 프롬프트 및 모델 성능 비교

## ⚙️ 설정 방법

### 1. LangSmith 계정 생성

1. [LangSmith 웹사이트](https://smith.langchain.com)에 접속
2. 계정 생성 또는 로그인
3. 새 프로젝트 생성 (예: `ai-literacy-navigator`)
4. API 키 생성

### 2. 패키지 설치

```bash
pip install langsmith
```

### 3. 환경 변수 설정

`.env` 파일에 다음 변수들을 추가하세요:

```env
# LangSmith 설정
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langsmith-api-key-here
LANGCHAIN_PROJECT=ai-literacy-navigator
```

## 🔧 환경 변수 설정

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `LANGCHAIN_TRACING_V2` | LangSmith 추적 활성화 | `false` | ✅ |
| `LANGCHAIN_API_KEY` | LangSmith API 키 | - | ✅ |
| `LANGCHAIN_PROJECT` | 프로젝트 이름 | `ai-literacy-navigator` | ❌ |
| `LANGCHAIN_ENDPOINT` | LangSmith API 엔드포인트 | `https://api.smith.langchain.com` | ❌ |

## 🚀 사용 방법

### 자동 추적

에이전트 실행 시 자동으로 추적이 시작됩니다:

```python
from agents.supervisor import LearningSupervisor
from workflow.state_management import StateManager

# 상태 생성
state = StateManager.create_initial_state("user123")
state['user_message'] = "AI에 대해 설명해주세요"

# 에이전트 실행 (자동으로 LangSmith에 추적됨)
supervisor = LearningSupervisor()
result = supervisor.execute(state)
```

### 수동 추적

필요한 경우 수동으로 추적을 시작할 수 있습니다:

```python
from utils.langsmith_config import trace_agent_execution, end_agent_trace

# 추적 시작
run_id = trace_agent_execution(
    agent_name="CustomAgent",
    inputs={"user_input": "Hello"},
    tags=["custom", "test"]
)

# 작업 수행
result = perform_some_work()

# 추적 종료
end_agent_trace(
    run_id=run_id,
    outputs={"result": result},
    error=None
)
```

### 사용자 피드백 수집

```python
from utils.langsmith_config import log_user_feedback

# 사용자 피드백 로깅
log_user_feedback(
    run_id="run-id-from-trace",
    rating=4,  # 1-5 점수
    comment="좋은 답변이었습니다"
)
```

## 🌐 API 엔드포인트

### 피드백 제출

```http
POST /api/feedback/submit
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
    "run_id": "실행-추적-ID",
    "rating": 4,
    "comment": "피드백 내용"
}
```

### 실행 정보 조회

```http
GET /api/feedback/runs/<run_id>
Authorization: Bearer <jwt-token>
```

### LangSmith 상태 확인

```http
GET /api/feedback/status
```

## 📊 모니터링 및 디버깅

### LangSmith 대시보드에서 확인할 수 있는 정보

1. **실행 추적**
   - 에이전트별 실행 시간
   - 입력/출력 데이터
   - 실행 단계별 상세 정보

2. **성능 지표**
   - 평균 응답 시간
   - 토큰 사용량
   - 성공/실패율

3. **사용자 피드백**
   - 평점 분포
   - 피드백 코멘트
   - 시간별 만족도 변화

4. **오류 분석**
   - 오류 발생 빈도
   - 오류 유형별 분류
   - 스택 트레이스

### 주요 태그 시스템

프로젝트에서 사용하는 주요 태그들:

- `supervisor`: LearningSupervisor 에이전트
- `educator`: TheoryEducator 에이전트
- `decision_making`: 의사결정 관련
- `content_generation`: 콘텐츠 생성 관련
- `chapter_1`, `chapter_2`, `chapter_3`: 챕터별 분류
- `agent_execution`: 에이전트 실행

## 🔧 문제 해결

### 일반적인 문제들

#### 1. LangSmith가 초기화되지 않음

**증상**: "LangSmith 설정이 비활성화되어 있습니다" 메시지

**해결방법**:
```bash
# 환경 변수 확인
echo $LANGCHAIN_TRACING_V2
echo $LANGCHAIN_API_KEY

# .env 파일 확인
cat .env | grep LANGCHAIN
```

#### 2. API 키 오류

**증상**: 인증 실패 오류

**해결방법**:
1. LangSmith 웹사이트에서 API 키 재생성
2. `.env` 파일의 `LANGCHAIN_API_KEY` 업데이트
3. 애플리케이션 재시작

#### 3. 추적 데이터가 표시되지 않음

**해결방법**:
1. 프로젝트 이름 확인: `LANGCHAIN_PROJECT`
2. 네트워크 연결 확인
3. LangSmith 서비스 상태 확인

### 디버깅 모드

개발 중 디버깅을 위해 로컬에서 추적 정보를 출력하려면:

```python
import os
os.environ['LANGCHAIN_VERBOSE'] = 'true'
```

### 로그 확인

애플리케이션 로그에서 LangSmith 관련 메시지 확인:

```bash
# 로그 파일 확인
tail -f app.log | grep -i langsmith

# 실시간 로그 모니터링
python app.py 2>&1 | grep -i langsmith
```

## 📈 성능 최적화

### 추적 데이터 최적화

1. **불필요한 데이터 제외**: 민감한 정보나 큰 데이터는 추적에서 제외
2. **태그 활용**: 적절한 태그를 사용하여 데이터 분류
3. **배치 처리**: 대량의 피드백은 배치로 처리

### 비용 최적화

1. **선택적 추적**: 중요한 실행만 추적
2. **데이터 보존 기간**: 필요에 따라 데이터 보존 기간 조정
3. **샘플링**: 높은 트래픽 환경에서는 샘플링 적용

## 🔒 보안 고려사항

1. **API 키 보안**: API 키를 코드에 하드코딩하지 말고 환경 변수 사용
2. **데이터 필터링**: 개인정보나 민감한 데이터는 추적에서 제외
3. **접근 권한**: LangSmith 프로젝트 접근 권한을 적절히 관리

## 📚 추가 자료

- [LangSmith 공식 문서](https://docs.smith.langchain.com/)
- [LangChain 문서](https://python.langchain.com/docs/get_started/introduction)
- [API 참조](https://api.smith.langchain.com/docs)

## 🆘 지원

문제가 발생하면 다음 채널을 통해 지원을 받을 수 있습니다:

1. **프로젝트 이슈**: GitHub Issues
2. **LangSmith 지원**: [LangSmith 지원 센터](https://support.langchain.com/)
3. **커뮤니티**: [LangChain Discord](https://discord.gg/langchain)