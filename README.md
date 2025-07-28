# 아래는 참고용 프로젝트입니다.
 - kiro와 claude와 함께 바이브 코딩한 프로젝트

# AI Literacy Navigator

AI 리터러시 교육을 위한 지능형 학습 플랫폼

## 📋 프로젝트 개요

AI Literacy Navigator는 사용자의 AI 지식 수준에 맞춘 개인화된 학습 경험을 제공하는 지능형 교육 플랫폼입니다. LangGraph 기반의 워크플로우와 다양한 AI 에이전트를 활용하여 효과적인 AI 교육을 제공합니다.

### 주요 특징

- 🎯 **개인화된 학습**: 사용자 수준별 맞춤형 콘텐츠 제공
- 🤖 **AI 에이전트 기반**: 다양한 전문 에이전트가 협력하여 학습 지원
- 📊 **실시간 진도 추적**: 학습 진행 상황 및 이해도 실시간 모니터링
- 🔄 **적응형 학습 루프**: 사용자 반응에 따른 동적 학습 경로 조정
- 💬 **대화형 인터페이스**: 자연스러운 대화를 통한 학습 경험
- 📈 **성능 모니터링**: 시스템 성능 및 오류 실시간 추적

## 🏗️ 시스템 아키텍처

### 핵심 구성 요소

```
AI Literacy Navigator
├── 🎯 사용자 관리 시스템
├── 📚 학습 콘텐츠 관리
├── 🤖 AI 에이전트 워크플로우
├── 💾 데이터베이스 (MySQL)
├── 🔍 벡터 검색 (ChromaDB)
├── 📊 모니터링 시스템
└── 🔐 인증 및 보안
```

### AI 에이전트 구조

- **TutorAgent**: 메인 튜터 에이전트
- **QuizAgent**: 퀴즈 생성 및 평가
- **FeedbackAgent**: 학습 피드백 제공
- **ProgressAgent**: 진도 관리
- **ContentAgent**: 콘텐츠 추천

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd ai-literacy-navigator

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# 기본 설정
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=true
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 데이터베이스
DATABASE_URL=mysql://user:password@localhost/ai_literacy_navigator

# JWT 설정
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# 이메일 알림 (선택사항)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAILS=admin1@example.com,admin2@example.com

# 관리자 계정 (선택사항)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-admin-password
```

### 3. 시스템 초기화

```bash
# 시스템 초기화 실행
python initialize_system.py
```

이 스크립트는 다음 작업을 수행합니다:
- 필요한 디렉토리 생성
- 로깅 시스템 초기화
- 데이터베이스 최적화
- 관리자 계정 생성 (환경 변수 설정 시)
- 시스템 테스트 실행

### 4. 애플리케이션 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## 📚 API 문서

### 인증 API

#### 회원가입
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "user_type": "beginner"
}
```

#### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "username_or_email": "testuser",
  "password": "SecurePass123!"
}
```

### 학습 API

#### 진단 퀴즈 조회
```http
GET /api/learning/diagnosis-quiz
Authorization: Bearer <token>
```

#### 학습 세션 시작
```http
POST /api/learning/start-session
Authorization: Bearer <token>
Content-Type: application/json

{
  "chapter_id": 1,
  "ui_mode": "chat"
}
```

#### 메시지 전송
```http
POST /api/learning/send-message
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_123",
  "message": "AI란 무엇인가요?",
  "ui_mode": "chat"
}
```

### 모니터링 API (관리자 전용)

#### 시스템 상태 확인
```http
GET /api/monitoring/health
```

#### 성능 메트릭 조회
```http
GET /api/monitoring/metrics
Authorization: Bearer <admin-token>
```

#### 오류 통계 조회
```http
GET /api/monitoring/errors/statistics?hours=24
Authorization: Bearer <admin-token>
```

## 🗄️ 데이터베이스 스키마

### 주요 테이블

- **USERS**: 사용자 정보
- **CHAPTERS**: 학습 챕터
- **LEARNING_LOOPS**: 학습 루프 세션
- **CONVERSATIONS**: 대화 기록
- **USER_LEARNING_PROGRESS**: 학습 진도
- **QUIZ_ATTEMPTS**: 퀴즈 시도 기록

### 인덱스 최적화

시스템은 다음 인덱스를 자동으로 생성합니다:
- 사용자 타입/레벨별 인덱스
- 학습 진도 상태별 인덱스
- 대화 시퀀스 인덱스
- 성능 최적화 복합 인덱스

## 🔧 개발 가이드

### 프로젝트 구조

```
ai-literacy-navigator/
├── app.py                      # Flask 애플리케이션 진입점
├── config.py                   # 설정 관리
├── initialize_system.py        # 시스템 초기화 스크립트
├── requirements.txt            # Python 의존성
├── 
├── blueprints/                 # Flask Blueprint
│   ├── auth.py                # 인증 API
│   ├── learning.py            # 학습 API
│   ├── monitoring.py          # 모니터링 API
│   └── ...
├── 
├── models/                     # 데이터베이스 모델
│   ├── user.py                # 사용자 모델
│   ├── learning_loop.py       # 학습 루프 모델
│   └── ...
├── 
├── services/                   # 비즈니스 로직
│   ├── auth_service.py        # 인증 서비스
│   ├── learning_service.py    # 학습 서비스
│   ├── performance_service.py # 성능 모니터링
│   └── ...
├── 
├── utils/                      # 유틸리티
│   ├── error_handler.py       # 오류 처리
│   ├── logging_config.py      # 로깅 설정
│   ├── performance_middleware.py # 성능 미들웨어
│   └── ...
├── 
├── workflow/                   # AI 워크플로우
│   ├── graph_builder.py       # LangGraph 워크플로우
│   ├── agents/                # AI 에이전트
│   └── state_management.py    # 상태 관리
├── 
└── logs/                       # 로그 파일
    ├── app.log                # 애플리케이션 로그
    └── error.log              # 오류 로그
```

### 새로운 에이전트 추가

1. `workflow/agents/` 디렉토리에 새 에이전트 파일 생성
2. `BaseAgent` 클래스를 상속받아 구현
3. `graph_builder.py`에서 워크플로우에 추가

```python
# workflow/agents/new_agent.py
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__("NewAgent")
    
    def process(self, state: TutorState) -> TutorState:
        # 에이전트 로직 구현
        return state
```

### 새로운 API 엔드포인트 추가

1. 적절한 Blueprint에 라우트 추가
2. 서비스 레이어에서 비즈니스 로직 구현
3. 오류 처리 및 로깅 적용

```python
@blueprint.route('/new-endpoint', methods=['POST'])
@token_required
@performance_monitoring('POST /api/new-endpoint')
@handle_errors(ErrorCategory.BUSINESS_LOGIC)
def new_endpoint():
    # 엔드포인트 구현
    pass
```

## 📊 모니터링 및 로깅

### 성능 모니터링

시스템은 다음 메트릭을 자동으로 수집합니다:
- CPU 및 메모리 사용률
- 데이터베이스 연결 풀 상태
- API 응답 시간
- 느린 쿼리 감지

### 로깅 시스템

- **구조화된 JSON 로그**: 검색 및 분석 용이
- **컨텍스트 정보 자동 포함**: 요청 ID, 사용자 ID 등
- **회전 로그 파일**: 자동 아카이브 및 정리
- **실시간 로그 분석**: 오류 패턴 및 성능 이슈 감지

### 오류 처리

- **자동 오류 분류**: 심각도 및 카테고리별 분류
- **오류 복구 메커니즘**: 자동 재시도 및 복구
- **실시간 알림**: 심각한 오류 발생 시 이메일 알림
- **오류 통계**: 오류 발생 패턴 분석

## 🔐 보안

### 인증 및 권한

- **JWT 기반 인증**: 상태 비저장 토큰 인증
- **역할 기반 접근 제어**: 사용자 레벨별 권한 관리
- **토큰 갱신**: 자동 토큰 갱신 메커니즘

### 보안 헤더

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### 요청 제한

- API 요청 속도 제한
- 사용자별 요청 제한

## 🧪 테스트

### 단위 테스트 실행

```bash
python -m pytest tests/ -v
```

### 통합 테스트

```bash
python -m pytest tests/integration/ -v
```

### 성능 테스트

```bash
python -m pytest tests/performance/ -v
```

## 📈 성능 최적화

### 데이터베이스 최적화

- 자동 인덱스 생성
- 쿼리 성능 모니터링
- 연결 풀 최적화

### 메모리 최적화

- State 크기 자동 최적화
- 대화 기록 압축
- 가비지 컬렉션 최적화

### 캐싱

- 자주 사용되는 데이터 캐싱
- API 응답 캐싱
- 세션 데이터 최적화

## 🚀 배포

### Docker를 사용한 배포

```bash
# Docker 이미지 빌드
docker build -t ai-literacy-navigator .

# 컨테이너 실행
docker run -p 5000:5000 --env-file .env ai-literacy-navigator
```

### 프로덕션 설정

1. 환경 변수에서 `FLASK_DEBUG=false` 설정
2. 강력한 `SECRET_KEY` 및 `JWT_SECRET_KEY` 사용
3. HTTPS 설정
4. 데이터베이스 백업 설정
5. 로그 모니터링 설정

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. GitHub Issues에 문제를 보고해주세요
2. 문서를 확인해주세요
3. 로그 파일을 확인해주세요 (`logs/app.log`, `logs/error.log`)

## 🔄 업데이트 로그

### v1.0.0
- 초기 릴리스
- 기본 학습 기능 구현
- AI 에이전트 워크플로우
- 성능 모니터링 시스템
- 오류 처리 및 로깅 시스템

---

**AI Literacy Navigator** - AI 교육의 새로운 패러다임을 제시합니다. 🚀