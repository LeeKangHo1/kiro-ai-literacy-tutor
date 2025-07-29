# 구현 계획

- [x] 1. 프로젝트 기본 구조 및 환경 설정






  - Python 가상환경 생성 및 활성화 (python -m venv venv)
  - Flask 프로젝트 디렉토리 구조 생성 및 기본 설정 파일 작성
  - 필요한 Python 패키지 의존성 정의 (requirements.txt)
  - 환경 변수 설정 파일(.env) 및 설정 관리 모듈 구현
  - 프로젝트 구조 예시:
    ```
    ai-literacy-navigator/
    ├── venv/                     # 가상환경
    ├── app.py                    # Flask 메인 애플리케이션 (간소화)
    ├── config.py                 # 설정 관리
    ├── requirements.txt          # Python 패키지 의존성
    ├── .env                      # 환경 변수
    ├── .gitignore               # Git 무시 파일
    ├── blueprints/              # Flask Blueprint (기능별 분할)
    │   ├── __init__.py
    │   ├── auth/                # 인증 관련 API 분할
    │   │   ├── __init__.py
    │   │   ├── login.py         # 로그인 API
    │   │   ├── register.py      # 회원가입 API
    │   │   └── token.py         # 토큰 관리 API
    │   ├── learning/            # 학습 관련 API 분할
    │   │   ├── __init__.py
    │   │   ├── diagnosis.py     # 진단 퀴즈 API
    │   │   ├── chat.py          # 메시지 처리 API
    │   │   ├── progress.py      # 진도 관리 API
    │   │   └── chapter.py       # 챕터 관리 API
    │   └── user/                # 사용자 관련 API 분할
    │       ├── __init__.py
    │       ├── profile.py       # 프로필 관리
    │       └── stats.py         # 학습 통계
    ├── models/                  # SQLAlchemy 모델
    │   ├── __init__.py
    │   ├── user.py
    │   ├── chapter.py
    │   ├── learning_loop.py
    │   ├── conversation.py
    │   └── quiz_attempt.py
    ├── agents/                  # LangGraph 에이전트 (기능별 분할)
    │   ├── __init__.py
    │   ├── supervisor/          # LearningSupervisor 분할
    │   │   ├── __init__.py
    │   │   ├── progress_analyzer.py    # 진도 분석
    │   │   ├── loop_manager.py         # 루프 관리
    │   │   └── decision_maker.py       # 다음 단계 결정
    │   ├── educator/            # TheoryEducator 분할
    │   │   ├── __init__.py
    │   │   ├── content_generator.py    # 콘텐츠 생성
    │   │   └── level_adapter.py        # 레벨별 적응
    │   ├── quiz/                # QuizGenerator 분할
    │   │   ├── __init__.py
    │   │   ├── question_generator.py   # 문제 생성
    │   │   ├── hint_generator.py       # 힌트 생성
    │   │   └── difficulty_manager.py   # 난이도 관리
    │   ├── evaluator/           # EvaluationFeedbackAgent 분할
    │   │   ├── __init__.py
    │   │   ├── answer_evaluator.py     # 답변 평가
    │   │   └── feedback_generator.py   # 피드백 생성
    │   └── qna/                 # QnAResolver 분할
    │       ├── __init__.py
    │       ├── search_handler.py       # 검색 처리
    │       └── context_integrator.py   # 맥락 통합
    ├── routers/                 # 라우팅 에이전트
    │   ├── __init__.py
    │   ├── post_theory_router.py
    │   └── post_feedback_router.py
    ├── tools/                   # LangGraph 도구 (기능별 분할)
    │   ├── __init__.py
    │   ├── content/             # 콘텐츠 생성 도구 분할
    │   │   ├── __init__.py
    │   │   ├── theory_tool.py          # 이론 생성 도구
    │   │   ├── quiz_tool.py            # 퀴즈 생성 도구
    │   │   └── hint_tool.py            # 힌트 생성 도구
    │   ├── external/            # 외부 연동 도구 분할
    │   │   ├── __init__.py
    │   │   ├── chatgpt_tool.py         # ChatGPT API 도구
    │   │   ├── chromadb_tool.py        # ChromaDB 도구
    │   │   └── web_search_tool.py      # 웹 검색 도구
    │   └── evaluation/          # 평가 도구 분할
    │       ├── __init__.py
    │       ├── answer_eval_tool.py     # 답변 평가 도구
    │       └── feedback_tool.py        # 피드백 도구
    ├── workflow/                # LangGraph 워크플로우 (분할)
    │   ├── __init__.py
    │   ├── graph_builder.py     # StateGraph 구성
    │   ├── node_definitions.py  # 노드 정의
    │   ├── edge_conditions.py   # 엣지 조건
    │   └── state_management.py  # State 관리
    ├── services/                # 비즈니스 로직
    │   ├── __init__.py
    │   ├── auth_service.py
    │   ├── learning_service.py
    │   ├── database_service.py
    │   └── content_service.py   # 콘텐츠 관리 서비스
    ├── utils/                   # 유틸리티
    │   ├── __init__.py
    │   ├── jwt_utils.py
    │   ├── password_utils.py
    │   ├── response_utils.py
    │   └── validation_utils.py  # 검증 유틸리티
    ├── tests/                   # 테스트 코드 (분할)
    │   ├── __init__.py
    │   ├── unit/                # 단위 테스트
    │   │   ├── test_agents.py
    │   │   ├── test_tools.py
    │   │   └── test_models.py
    │   ├── integration/         # 통합 테스트
    │   │   ├── test_workflow.py
    │   │   └── test_api.py
    │   └── fixtures/            # 테스트 데이터
    │       └── sample_data.py
    └── migrations/              # 데이터베이스 마이그레이션
        └── init_schema.sql
    ```
  - _요구사항: 6.1, 6.2, 6.3_

- [x] 2. 데이터베이스 스키마 및 모델 구현




  - [x] 2.1 MySQL 데이터베이스 스키마 생성


    - USERS, CHAPTERS, USER_LEARNING_PROGRESS, LEARNING_LOOPS, CONVERSATIONS, QUIZ_ATTEMPTS 테이블 생성
    - 인덱스 및 외래키 제약조건 설정
    - _요구사항: 5.2, 5.3, 5.4_

  - [x] 2.2 SQLAlchemy ORM 모델 클래스 구현


    - User, Chapter, UserLearningProgress, LearningLoop, Conversation, QuizAttempt 모델 클래스 작성
    - 모델 간 관계 설정 및 기본 CRUD 메서드 구현
    - _요구사항: 5.2, 5.3, 5.4_

- [x] 3. 인증 및 사용자 관리 시스템 구현





  - [x] 3.1 JWT 기반 인증 시스템 구현


    - JWT 토큰 생성, 검증, 갱신 기능 구현
    - 인증 데코레이터 및 미들웨어 작성
    - _요구사항: 6.1, 6.2, 6.3_

  - [x] 3.2 사용자 회원가입 및 로그인 API 구현


    - 회원가입 엔드포인트 (bcrypt 비밀번호 암호화 포함)
    - 로그인 엔드포인트 (JWT 토큰 발급)
    - 사용자 정보 조회 및 수정 엔드포인트
    - _요구사항: 6.1, 6.2, 6.3_

- [x] 4. LangGraph 기반 멀티에이전트 시스템 구현




  - [x] 4.1 워크플로우 기본 구조 구현 (분할)


    - graph_builder.py: StateGraph 구성 및 노드 연결
    - node_definitions.py: 각 에이전트 노드 정의
    - edge_conditions.py: 조건부 라우팅 엣지 정의
    - state_management.py: TutorState 관리 및 검증
    - _요구사항: 5.1, 5.2, 5.3_

  - [x] 4.2 LearningSupervisor 에이전트 구현 (분할)


    - progress_analyzer.py: 학습 진도 분석 로직 구현
    - loop_manager.py: 루프 완료 처리 및 요약 생성 기능
    - decision_maker.py: 다음 단계 결정 로직 구현
    - _요구사항: 5.1, 5.2_

  - [x] 4.3 TheoryEducator 에이전트 구현 (분할)


    - content_generator.py: 기본 콘텐츠 생성 로직 구현
    - level_adapter.py: 사용자 레벨별 콘텐츠 적응 로직 구현
    - theory_tool.py: theory_generation_tool 구현
    - _요구사항: 2.1, 2.2_

- [x] 5. 라우팅 시스템 구현





  - [x] 5.1 PostTheoryRouter 구현


    - 개념 설명 후 사용자 의도 파악 로직 (질문 vs 문제 요청)
    - 패턴 매칭 기반 라우팅 규칙 구현
    - QnAResolver 또는 QuizGenerator로의 라우팅 처리
    - _요구사항: 2.2, 3.1_

  - [x] 5.2 PostFeedbackRouter 구현


    - 피드백 후 사용자 의도 파악 로직 (추가 질문 vs 진행 요청)
    - 진행 패턴 및 질문 패턴 매칭 구현
    - QnAResolver 또는 LearningSupervisor로의 라우팅 처리
    - _요구사항: 3.2, 5.1_

- [x] 6. 문제 출제 및 평가 시스템 구현





  - [x] 6.1 QuizGenerator 에이전트 구현 (분할)


    - question_generator.py: 객관식/프롬프트 문제 생성 로직
    - hint_generator.py: 문제별 맞춤 힌트 생성 로직
    - difficulty_manager.py: 난이도 조절 및 관리 기능
    - quiz_tool.py, hint_tool.py: 관련 도구 구현
    - _요구사항: 2.3, 7.1, 7.2_

  - [x] 6.2 EvaluationFeedbackAgent 에이전트 구현 (분할)


    - answer_evaluator.py: 답변 채점 및 이해도 측정 로직
    - feedback_generator.py: 개인화된 피드백 생성 로직
    - answer_eval_tool.py, feedback_tool.py: 관련 도구 구현
    - 힌트 사용 고려한 평가 로직 통합
    - _요구사항: 2.4, 7.3_

- [x] 7. 실시간 질문 답변 시스템 구현










 

  - [x] 7.1 QnAResolver 에이전트 구현 (분할)



    - search_handler.py: ChromaDB 벡터 검색 및 웹 검색 처리
    - context_integrator.py: 학습 맥락 연결 및 답변 생성 로직
    - chromadb_tool.py, web_search_tool.py: 관련 도구 구현
    - _요구사항: 3.1, 3.2, 3.3_

  - [x] 7.2 ChromaDB 벡터 데이터베이스 연동


    - ChromaDB 클라이언트 설정 및 연결 관리
    - 학습 콘텐츠 벡터화 및 저장 기능
    - 유사도 검색 및 결과 랭킹 시스템
    - _요구사항: 3.1, 3.3_

- [x] 8. 외부 API 연동 구현




  - [x] 8.1 ChatGPT API 연동 구현 (분할)


    - chatgpt_tool.py: ChatGPT API 호출 및 기본 처리 로직
    - API 호출 관리 및 오류 처리 로직 구현
    - 프롬프트 품질 평가 및 결과 분석 기능 구현
    - _요구사항: 4.1, 4.2, 4.3_

  - [x] 8.2 외부 서비스 오류 처리 시스템


    - ChatGPT API 오류 처리 및 대체 응답 로직
    - ChromaDB 연결 오류 처리 및 기본 답변 제공
    - 서비스 상태 모니터링 및 알림 시스템
    - _요구사항: 4.1, 3.1_

- [x] 9. 학습 루프 관리 시스템 구현





  - [x] 9.1 1루프 기반 대화 관리 구현


    - 루프 시작, 진행, 완료 처리 로직 구현
    - 대화 내용 임시 저장 및 DB 저장 기능
    - 루프 요약 생성 및 State 크기 최적화
    - _요구사항: 5.1, 5.2, 5.3_

  - [x] 9.2 학습 진도 추적 및 기록 시스템


    - 챕터별 진도 계산 및 업데이트 로직
    - 이해도 점수 산출 및 학습 통계 생성
    - 학습 기록 조회 API 구현
    - _요구사항: 5.3, 5.4_

- [x] 10. REST API 엔드포인트 구현 (분할)





  - [x] 10.1 인증 관련 API 구현


    - login.py: 로그인 API 엔드포인트
    - register.py: 회원가입 API 엔드포인트
    - token.py: JWT 토큰 관리 API
    - _요구사항: 6.1, 6.2, 6.3_

  - [x] 10.2 학습 관련 API 구현


    - diagnosis.py: 진단 퀴즈 API 엔드포인트
    - chat.py: 메시지 처리 API 엔드포인트
    - progress.py: 학습 진도 관리 API
    - chapter.py: 챕터 관리 API
    - _요구사항: 1.1, 1.2, 2.1_

  - [x] 10.3 사용자 데이터 관리 API 구현


    - profile.py: 사용자 프로필 관리 API
    - stats.py: 학습 통계 및 기록 API
    - _요구사항: 5.3, 5.4_

- [x] 11. UI 모드 관리 시스템 구현




  - [x] 11.1 하이브리드 UX 패턴 구현


    - 자유 대화 모드와 제한 UI 모드 전환 로직
    - UI 요소 생성 및 상태 관리 시스템
    - 모드별 사용자 상호작용 처리
    - _요구사항: 8.1, 8.2, 8.3_

  - [x] 11.2 UI 요소 및 상태 전달 시스템


    - 에이전트별 UI 요소 정의 및 생성
    - 프론트엔드 상태 동기화 메커니즘
    - 실시간 UI 업데이트 처리
    - _요구사항: 8.1, 8.2, 8.3_

- [x] 12. 챕터 콘텐츠 및 초기 데이터 구현




  - [x] 12.1 챕터 1 "AI는 무엇인가?" 콘텐츠 구현


    - AI/ML/DL 개념 구분 학습 콘텐츠 작성
    - 초보자 및 실무자용 설명 버전 구현
    - 개념 구분 퀴즈 문제 세트 작성
    - _요구사항: 1.2, 2.1, 2.3_

  - [x] 12.2 챕터 2 "LLM이란 무엇인가?" 콘텐츠 구현

    - GPT, BERT, Transformer 구조 이해 학습 콘텐츠 작성
    - 언어 모델의 발전 과정 및 특징 설명
    - LLM 종류별 특성 비교 퀴즈 문제 세트 작성
    - 초보자/실무자별 맞춤 설명 버전 구현
    - _요구사항: 1.2, 2.1, 2.3_

  - [x] 12.3 챕터 3 "프롬프트란 무엇인가?" 콘텐츠 구현


    - 프롬프트 기본 구조 및 작성법 학습 콘텐츠
    - 실제 프롬프트 작성 실습 문제 세트
    - ChatGPT API 연동 실습 환경 구성
    - _요구사항: 1.2, 2.1, 4.1, 4.2_

  - [x] 12.4 챕터 4 "ChatGPT로 할 수 있는 것들" 콘텐츠 구현


    - 요약, 번역, 질문 생성 등 실용적 활용법 학습 콘텐츠
    - 업무별/상황별 ChatGPT 활용 사례 정리
    - 실제 ChatGPT 체험 실습 문제 세트 작성
    - 프롬프트 최적화 기법 및 팁 제공
    - _요구사항: 1.2, 2.1, 4.1, 4.2, 4.3_

  - [x] 12.5 챕터 5 "AI 시대의 문해력" 콘텐츠 구현


    - AI 윤리 및 책임감 있는 AI 사용법 학습 콘텐츠
    - AI 편향성과 공정성 문제 이해 및 대응 방안
    - 개인정보보호와 프라이버시 보호 실천법
    - 인간-AI 협업 모델 및 미래 역량 개발 가이드
    - AI 시대 필요 역량과 새로운 진로 탐색 콘텐츠
    - 초보자/실무자별 맞춤 설명 및 실습 문제 세트
    - _요구사항: 1.2, 2.1, 2.3, 8.1, 8.2_

- [x] 13. 테스트 코드 작성





  - [x] 13.1 단위 테스트 구현


    - 각 에이전트별 기능 테스트 코드 작성
    - 도구(Tools) 기능 테스트 코드 작성
    - 데이터베이스 모델 테스트 코드 작성
    - _요구사항: 모든 요구사항_

  - [x] 13.2 통합 테스트 구현


    - 완전한 학습 루프 통합 테스트
    - API 엔드포인트 통합 테스트
    - 외부 서비스 연동 테스트
    - _요구사항: 모든 요구사항_

- [x] 14. 시스템 통합 및 최적화




  - [x] 14.1 성능 최적화 및 모니터링


    - 데이터베이스 쿼리 최적화 및 인덱스 튜닝
    - State 관리 메모리 사용량 최적화
    - API 응답 시간 모니터링 시스템 구현
    - _요구사항: 5.1, 5.2_

  - [x] 14.2 오류 처리 및 로깅 시스템


    - 전체 시스템 오류 처리 통합
    - 구조화된 로깅 시스템 구현
    - 오류 알림 및 복구 메커니즘 구현
    - _요구사항: 모든 요구사항_

- [ ] 15. Vue 3 프론트엔드 개발 (완전한 기능 구현)




  - [ ] 15.1 Vue 3 프로젝트 초기 설정 및 확장된 구조


    - Vue 3 + Vite + TypeScript + Vue Router + Pinia + Bootstrap + SCSS + Axios 설정
    - 확장된 프로젝트 구조:
      ```
      frontend/
      ├── src/
      │   ├── components/
      │   │   ├── Chat/
      │   │   │   ├── ChatInterface.vue      # 자유 대화 UI
      │   │   │   ├── MessageBubble.vue      # 메시지 표시 컴포넌트
      │   │   │   ├── InputArea.vue          # 입력 영역 컴포넌트
      │   │   │   └── TypingIndicator.vue    # 타이핑 인디케이터
      │   │   ├── Quiz/
      │   │   │   ├── QuizInterface.vue      # 문제 풀이 UI
      │   │   │   ├── MultipleChoice.vue     # 객관식 문제 컴포넌트
      │   │   │   ├── PromptPractice.vue     # 프롬프트 실습 컴포넌트
      │   │   │   ├── HintSystem.vue         # 힌트 시스템 컴포넌트
      │   │   │   └── QuizFeedback.vue       # 퀴즈 피드백 컴포넌트
      │   │   ├── Progress/
      │   │   │   ├── ProgressTracker.vue    # 진도 추적 컴포넌트
      │   │   │   ├── LearningStats.vue      # 학습 통계 컴포넌트
      │   │   │   ├── ChapterNavigation.vue  # 챕터 네비게이션
      │   │   │   └── AchievementBadges.vue  # 성취 배지 시스템
      │   │   ├── Layout/
      │   │   │   ├── AppHeader.vue          # 앱 헤더
      │   │   │   ├── AppSidebar.vue         # 사이드바
      │   │   │   └── AppFooter.vue          # 앱 푸터
      │   │   └── Common/
      │   │       ├── LoadingSpinner.vue     # 로딩 스피너
      │   │       ├── ErrorAlert.vue         # 오류 알림
      │   │       └── ConfirmModal.vue       # 확인 모달
      │   ├── stores/
      │   │   ├── authStore.ts               # 인증 상태 관리
      │   │   ├── learningStore.ts           # 학습 상태 관리
      │   │   ├── uiStore.ts                 # UI 모드 관리
      │   │   ├── progressStore.ts           # 진도 관리
      │   │   └── notificationStore.ts       # 알림 관리
      │   ├── services/
      │   │   ├── apiClient.ts               # Axios API 클라이언트
      │   │   ├── authService.ts             # 인증 서비스
      │   │   ├── learningService.ts         # 학습 서비스
      │   │   ├── progressService.ts         # 진도 서비스
      │   │   └── websocketService.ts        # 실시간 통신 서비스
      │   ├── views/
      │   │   ├── LoginView.vue              # 로그인 페이지
      │   │   ├── RegisterView.vue           # 회원가입 페이지
      │   │   ├── DiagnosisView.vue          # 진단 퀴즈 페이지
      │   │   ├── LearningView.vue           # 메인 학습 페이지
      │   │   ├── ProgressView.vue           # 학습 진도 페이지
      │   │   ├── ProfileView.vue            # 사용자 프로필 페이지
      │   │   └── SettingsView.vue           # 설정 페이지
      │   ├── composables/
      │   │   ├── useAuth.ts                 # 인증 컴포저블
      │   │   ├── useLearning.ts             # 학습 컴포저블
      │   │   ├── useProgress.ts             # 진도 컴포저블
      │   │   └── useNotifications.ts        # 알림 컴포저블
      │   ├── types/
      │   │   ├── auth.ts                    # 인증 타입 정의
      │   │   ├── learning.ts                # 학습 타입 정의
      │   │   └── api.ts                     # API 타입 정의
      │   └── styles/
      │       ├── main.scss                  # 메인 스타일
      │       ├── variables.scss             # SCSS 변수
      │       ├── components.scss            # 컴포넌트 스타일
      │       └── themes.scss                # 테마 스타일
      ```
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 15.2 완전한 인증 시스템 구현


    - LoginView.vue: 완전한 로그인 폼 (유효성 검사, 오류 처리)
    - RegisterView.vue: 회원가입 폼 (사용자 유형 선택 포함)
    - authStore.ts: JWT 토큰 관리, 사용자 정보, 자동 로그인
    - authService.ts: 인증 관련 API 호출 서비스
    - apiClient.ts: Axios 인터셉터로 토큰 자동 첨부 및 갱신
    - Vue Router 가드: 인증 확인 및 리다이렉트
    - useAuth.ts: 인증 관련 컴포저블 (로그인, 로그아웃, 토큰 검증)
    - _요구사항: 6.1, 6.2, 6.3_

  - [ ] 15.3 진단 시스템 구현


    - DiagnosisView.vue: 사용자 유형 진단 퀴즈 페이지
    - 사용자 유형 선택 (AI 입문자 vs 실무 응용형)
    - 수준 진단 퀴즈 (low/medium/high 레벨 판정)
    - 진단 결과 기반 맞춤형 커리큘럼 제시
    - 진단 결과 저장 및 프로필 업데이트
    - _요구사항: 1.1, 1.2_

  - [ ] 15.4 고도화된 학습 인터페이스 구현


    - LearningView.vue: 메인 학습 페이지 (사이드바, 진도 표시)
    - ChatInterface.vue: 자유 대화 모드 UI
      - MessageBubble.vue: 메시지 버블 (사용자/시스템 구분)
      - InputArea.vue: 텍스트 입력 및 음성 입력 지원
      - TypingIndicator.vue: AI 응답 대기 중 표시
    - QuizInterface.vue: 문제 풀이 모드 UI
      - MultipleChoice.vue: 객관식 문제 컴포넌트
      - PromptPractice.vue: 프롬프트 실습 컴포넌트 (ChatGPT API 연동)
      - HintSystem.vue: 힌트 요청 및 표시 시스템
      - QuizFeedback.vue: 답변 평가 및 피드백 표시
    - UI 모드 자동 전환 (chat ↔ quiz ↔ restricted)
    - learningStore.ts: 대화 히스토리, 학습 상태, UI 모드 관리
    - _요구사항: 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3, 8.1, 8.2, 8.3_

  - [ ] 15.5 진도 관리 및 통계 시스템


    - ProgressView.vue: 학습 진도 대시보드
    - ProgressTracker.vue: 챕터별 진도 시각화 (진행률 바)
    - LearningStats.vue: 학습 통계 (시간, 정답률, 이해도 점수)
    - ChapterNavigation.vue: 챕터 네비게이션 (완료/진행중/잠금 상태)
    - AchievementBadges.vue: 성취 배지 시스템 (학습 마일스톤)
    - progressStore.ts: 진도 데이터 관리
    - progressService.ts: 진도 관련 API 호출
    - useProgress.ts: 진도 관련 컴포저블
    - _요구사항: 5.1, 5.2, 5.3, 5.4_

  - [ ] 15.6 실시간 질문 답변 시스템


    - QnAResolver 연동을 위한 실시간 검색 UI
    - 질문 입력 시 자동완성 및 추천 기능
    - ChromaDB 벡터 검색 결과 표시
    - 웹 검색 결과 통합 표시
    - 학습 맥락과 연결된 답변 하이라이팅
    - 질문 히스토리 및 즐겨찾기 기능
    - _요구사항: 3.1, 3.2, 3.3_

  - [ ] 15.7 사용자 프로필 및 설정


    - ProfileView.vue: 사용자 프로필 관리 페이지
    - 사용자 정보 수정 (이름, 이메일, 비밀번호)
    - 학습 선호도 설정 (난이도, 학습 속도)
    - 알림 설정 (학습 리마인더, 성취 알림)
    - SettingsView.vue: 앱 설정 페이지
    - 테마 설정 (라이트/다크 모드)
    - 언어 설정 및 접근성 옵션
    - _요구사항: 6.1, 6.2, 6.3_

  - [ ] 15.8 반응형 디자인 및 UX 최적화


    - 모바일/태블릿/데스크톱 반응형 레이아웃
    - Bootstrap 5 + 커스텀 SCSS 스타일링
    - 다크 모드 지원 및 테마 전환
    - 접근성 준수 (ARIA 라벨, 키보드 네비게이션)
    - 로딩 상태 및 오류 상태 UI
    - 애니메이션 및 트랜지션 효과
    - PWA 지원 (오프라인 기능, 앱 설치)
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 15.9 실시간 통신 및 알림 시스템


    - WebSocket 연결을 통한 실시간 학습 상태 동기화
    - 실시간 알림 시스템 (학습 완료, 새로운 콘텐츠)
    - 푸시 알림 지원 (브라우저 알림 API)
    - 오프라인 상태 감지 및 처리
    - 네트워크 재연결 시 자동 동기화
    - notificationStore.ts: 알림 상태 관리
    - websocketService.ts: WebSocket 연결 관리
    - useNotifications.ts: 알림 관련 컴포저블
    - _요구사항: 8.1, 8.2, 8.3_

- [ ] 16. 포괄적 통합 테스트 및 품질 보증

  - [ ] 16.1 프론트엔드 단위 테스트 구현


    - Vue 3 컴포넌트 단위 테스트 (Vitest + Vue Test Utils)
    - Pinia 스토어 테스트 (상태 관리 로직 검증)
    - 컴포저블 함수 테스트 (useAuth, useLearning 등)
    - API 서비스 모킹 테스트 (MSW 활용)
    - 유틸리티 함수 테스트 (검증, 포맷팅 등)
    - _요구사항: 모든 프론트엔드 기능_

  - [ ] 16.2 프론트엔드 통합 테스트 구현


    - 컴포넌트 간 상호작용 테스트
    - 라우터 네비게이션 테스트
    - 스토어 간 데이터 흐름 테스트
    - API 통신 통합 테스트
    - 오류 상황 처리 테스트
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 16.3 E2E 테스트 구현 (Playwright)


    - 사용자 회원가입 및 로그인 플로우 테스트
    - 진단 퀴즈 완료 플로우 테스트
    - 완전한 학습 루프 E2E 테스트 (이론 → 질문 → 퀴즈 → 피드백)
    - 챕터 진행 및 진도 추적 테스트
    - 실시간 질문 답변 기능 테스트
    - 프롬프트 실습 기능 테스트 (ChatGPT API 연동)
    - 다양한 브라우저 및 디바이스 호환성 테스트
    - _요구사항: 1.1, 1.2, 2.1, 2.2, 3.1, 4.1, 4.2_

  - [ ] 16.4 백엔드-프론트엔드 통합 테스트


    - Flask API와 Vue 3 프론트엔드 연동 테스트
    - JWT 인증 및 토큰 갱신 테스트
    - WebSocket 실시간 통신 테스트
    - 멀티에이전트 워크플로우와 UI 연동 확인
    - 대용량 데이터 처리 및 성능 테스트
    - 동시 사용자 접속 테스트
    - _요구사항: 모든 요구사항_

  - [ ] 16.5 성능 및 부하 테스트


    - 프론트엔드 성능 테스트 (Lighthouse, Web Vitals)
    - API 응답 시간 및 처리량 테스트
    - 데이터베이스 쿼리 성능 테스트
    - ChromaDB 벡터 검색 성능 테스트
    - ChatGPT API 호출 최적화 테스트
    - 메모리 사용량 및 누수 테스트
    - 동시 접속자 부하 테스트 (100명, 500명, 1000명)
    - _요구사항: 5.1, 5.2_

  - [ ] 16.6 보안 테스트


    - JWT 토큰 보안 테스트 (만료, 변조, 탈취)
    - API 엔드포인트 인가 테스트
    - SQL 인젝션 및 XSS 공격 방어 테스트
    - CORS 정책 및 CSP 헤더 테스트
    - 사용자 입력 검증 및 필터링 테스트
    - 비밀번호 암호화 및 저장 보안 테스트
    - _요구사항: 6.1, 6.2, 6.3_

  - [ ] 16.7 접근성 및 사용성 테스트


    - WCAG 2.1 AA 준수 테스트
    - 스크린 리더 호환성 테스트
    - 키보드 네비게이션 테스트
    - 색상 대비 및 시각적 접근성 테스트
    - 다양한 디바이스 및 화면 크기 테스트
    - 사용자 경험 플로우 테스트
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 16.8 오류 처리 및 복구 테스트


    - 네트워크 연결 오류 처리 테스트
    - API 서버 다운 상황 처리 테스트
    - ChatGPT API 오류 처리 테스트
    - ChromaDB 연결 오류 처리 테스트
    - 데이터베이스 연결 오류 처리 테스트
    - 브라우저 새로고침 및 세션 복구 테스트
    - 오프라인 모드 및 재연결 테스트
    - _요구사항: 모든 요구사항_

  - [ ] 16.9 다국어 및 현지화 테스트


    - 한국어 텍스트 표시 및 입력 테스트
    - 다양한 브라우저 언어 설정 테스트
    - 날짜, 시간, 숫자 형식 현지화 테스트
    - RTL 언어 지원 테스트 (향후 확장 대비)
    - 텍스트 길이 변화에 따른 UI 레이아웃 테스트
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 16.10 데이터 무결성 및 백업 테스트


    - 학습 진도 데이터 정확성 테스트
    - 대화 기록 저장 및 복원 테스트
    - 사용자 데이터 백업 및 복구 테스트
    - 데이터베이스 트랜잭션 무결성 테스트
    - 동시 업데이트 충돌 처리 테스트
    - _요구사항: 5.1, 5.2, 5.3, 5.4_

- [ ] 17. 프로덕션 배포 및 운영 준비

  - [ ] 17.1 컨테이너화 및 오케스트레이션


    - Docker 멀티스테이지 빌드 설정 (프론트엔드/백엔드 분리)
    - docker-compose 개발/프로덕션 환경 분리
    - Kubernetes 배포 매니페스트 작성 (선택사항)
    - 컨테이너 이미지 최적화 및 보안 강화
    - 헬스체크 및 리소스 제한 설정
    - _요구사항: 모든 요구사항_

  - [ ] 17.2 CI/CD 파이프라인 구축


    - GitHub Actions 워크플로우 설정
    - 자동 테스트 실행 (단위/통합/E2E 테스트)
    - 코드 품질 검사 (ESLint, Prettier, SonarQube)
    - 보안 취약점 스캔 (Snyk, OWASP)
    - 자동 빌드 및 배포 파이프라인
    - 롤백 및 블루-그린 배포 전략
    - _요구사항: 모든 요구사항_

  - [ ] 17.3 모니터링 및 로깅 시스템


    - 애플리케이션 성능 모니터링 (APM) 설정
    - 로그 수집 및 분석 시스템 (ELK Stack 또는 Fluentd)
    - 메트릭 수집 및 대시보드 (Prometheus + Grafana)
    - 알림 시스템 설정 (Slack, 이메일)
    - 오류 추적 시스템 (Sentry)
    - 사용자 행동 분석 (Google Analytics, Mixpanel)
    - _요구사항: 모든 요구사항_

  - [ ] 17.4 보안 및 인프라 강화


    - HTTPS/TLS 인증서 설정 (Let's Encrypt)
    - 웹 애플리케이션 방화벽 (WAF) 설정
    - 데이터베이스 보안 강화 (암호화, 접근 제어)
    - API 레이트 리미팅 및 DDoS 방어
    - 백업 및 재해 복구 계획 수립
    - 개인정보보호 및 GDPR 준수 설정
    - _요구사항: 6.1, 6.2, 6.3_

  - [ ] 17.5 성능 최적화 및 확장성


    - CDN 설정 및 정적 자산 최적화
    - 데이터베이스 인덱싱 및 쿼리 최적화
    - Redis 캐싱 시스템 구축
    - 로드 밸런서 설정 (Nginx, HAProxy)
    - 오토스케일링 설정 (수평/수직 확장)
    - 데이터베이스 읽기 복제본 설정
    - _요구사항: 5.1, 5.2_

  - [ ] 17.6 종합 문서화


    - REST API 문서 작성 (Swagger/OpenAPI 3.0)
    - GraphQL 스키마 문서 (선택사항)
    - 시스템 아키텍처 다이어그램 업데이트
    - 데이터베이스 ERD 및 스키마 문서
    - 개발자 온보딩 가이드
    - 코드 스타일 가이드 및 컨벤션
    - _요구사항: 모든 요구사항_

  - [ ] 17.7 운영 가이드 및 매뉴얼


    - 시스템 관리자 가이드
    - 배포 및 롤백 절차서
    - 장애 대응 매뉴얼 (Runbook)
    - 모니터링 알림 대응 가이드
    - 데이터베이스 백업/복구 절차
    - 보안 사고 대응 절차
    - _요구사항: 모든 요구사항_

  - [ ] 17.8 사용자 가이드 및 교육 자료


    - 최종 사용자 매뉴얼 (학습자용)
    - 관리자 사용 가이드 (교육자용)
    - 비디오 튜토리얼 제작
    - FAQ 및 문제해결 가이드
    - 접근성 사용 가이드
    - 모바일 앱 사용법 (PWA)
    - _요구사항: 1.1, 1.2, 8.1, 8.2, 8.3_

  - [ ] 17.9 품질 보증 및 최종 검증


    - 프로덕션 환경 최종 테스트
    - 성능 벤치마크 및 부하 테스트
    - 보안 침투 테스트 (Penetration Testing)
    - 사용성 테스트 (실제 사용자 그룹)
    - 접근성 준수 최종 검증
    - 법적 요구사항 준수 확인
    - _요구사항: 모든 요구사항_

  - [ ] 17.10 런치 준비 및 마케팅


    - 베타 테스트 프로그램 운영
    - 사용자 피드백 수집 및 반영
    - 런치 계획 및 일정 수립
    - 마케팅 자료 및 랜딩 페이지 제작
    - 소셜 미디어 및 커뮤니티 홍보
    - 언론 보도자료 작성
    - _요구사항: 모든 요구사항_

- [x] 18. 유지보수 및 향후 개발 계획


  - [ ] 18.1 지속적 개선 시스템 구축


    - 사용자 피드백 수집 시스템 구축
    - A/B 테스트 프레임워크 설정
    - 기능 플래그 관리 시스템 (Feature Flags)
    - 사용자 행동 분석 및 인사이트 도출
    - 정기적 성능 리뷰 및 최적화
    - 기술 부채 관리 및 리팩토링 계획
    - _요구사항: 모든 요구사항_

  - [ ] 18.2 콘텐츠 확장 및 업데이트


    - 새로운 AI 기술 트렌드 반영 (GPT-4, Claude, Gemini 등)
    - 추가 챕터 개발 (RAG, Fine-tuning, AI 에이전트 등)
    - 업계별 맞춤 콘텐츠 개발 (의료, 금융, 교육 등)
    - 다국어 콘텐츠 확장 (영어, 중국어, 일본어)
    - 실시간 AI 뉴스 및 업데이트 통합
    - 커뮤니티 기반 콘텐츠 생성 시스템
    - _요구사항: 1.2, 2.1_

  - [ ] 18.3 고급 기능 개발


    - AI 튜터 개인화 고도화 (학습 스타일 분석)
    - 음성 인식 및 TTS 기능 추가
    - 실시간 화상 튜터링 기능
    - AR/VR 학습 환경 지원
    - 게이미피케이션 요소 강화
    - 소셜 학습 기능 (스터디 그룹, 경쟁)
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 18.4 플랫폼 확장


    - 모바일 네이티브 앱 개발 (React Native/Flutter)
    - 데스크톱 앱 개발 (Electron)
    - API 플랫폼 오픈 (써드파티 통합)
    - 교육기관용 LMS 통합
    - 기업용 대시보드 및 관리 도구
    - 화이트라벨 솔루션 개발
    - _요구사항: 모든 요구사항_

  - [ ] 18.5 AI 모델 고도화


    - 자체 AI 모델 개발 및 파인튜닝
    - 멀티모달 AI 지원 (텍스트+이미지+음성)
    - 실시간 학습 및 적응형 AI 시스템
    - 연합학습 (Federated Learning) 적용
    - AI 윤리 및 편향성 모니터링 강화
    - 설명 가능한 AI (XAI) 기능 추가
    - _요구사항: 2.1, 2.2, 4.1, 4.2_

  - [ ] 18.6 데이터 분석 및 인사이트



    - 학습 효과 측정 및 분석 시스템
    - 예측 분석 (학습 성공률, 이탈률)
    - 개인화 추천 시스템 고도화
    - 학습 패턴 분석 및 최적화
    - 교육 효과성 연구 및 논문 발표
    - 데이터 기반 의사결정 지원 시스템
    - _요구사항: 5.1, 5.2, 5.3, 5.4_

  - [ ] 18.7 커뮤니티 및 생태계 구축

    - 사용자 커뮤니티 플랫폼 구축
    - 전문가 네트워크 및 멘토링 시스템
    - 오픈소스 기여 및 개발자 생태계
    - 교육 파트너십 및 제휴 확대
    - 컨퍼런스 및 워크샵 개최
    - 인증 프로그램 및 자격증 발급
    - _요구사항: 모든 요구사항_

  - [ ] 18.8 글로벌 확장 준비

    - 다국가 법규 준수 (GDPR, CCPA 등)
    - 현지화 및 문화적 적응
    - 글로벌 결제 시스템 통합
    - 다국가 서버 인프라 구축
    - 현지 파트너십 및 마케팅
    - 국제 표준 인증 획득
    - _요구사항: 모든 요구사항_

  - [ ] 18.9 연구개발 및 혁신

    - AI 교육 효과성 연구
    - 새로운 학습 이론 적용 실험
    - 차세대 교육 기술 연구
    - 학술 기관과의 공동 연구
    - 특허 출원 및 지적재산권 관리
    - 혁신적 교육 방법론 개발
    - _요구사항: 모든 요구사항_

  - [ ] 18.10 지속가능성 및 사회적 책임

    - 친환경 서버 인프라 전환
    - 디지털 격차 해소 프로그램
    - 접근성 향상 지속적 개선
    - AI 윤리 가이드라인 준수
    - 사회적 영향 측정 및 보고
    - 교육 기회 균등 프로그램 운영
    - _요구사항: 모든 요구사항_