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

- [ ] 15. Vue 3 프론트엔드 개발
  - [-] 15.1 Vue 3 프로젝트 초기 설정


    - Vue 3 프로젝트 생성 및 기본 구조 설정
    - TypeScript, Vite, Vue Router, Pinia 설정
    - Tailwind CSS 또는 UI 라이브러리 설정
    - 프로젝트 구조 생성:
      ```
      frontend/
      ├── src/
      │   ├── components/
      │   │   ├── Chat/
      │   │   ├── Quiz/
      │   │   └── Progress/
      │   ├── stores/
      │   ├── services/
      │   ├── views/
      │   └── utils/
      ├── public/
      └── package.json
      ```
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 15.2 인증 및 라우팅 시스템 구현
    - Vue Router 설정 및 라우트 가드 구현
    - 로그인/회원가입 페이지 컴포넌트 작성
    - JWT 토큰 관리 및 자동 갱신 로직
    - Pinia 기반 인증 상태 관리 (authStore.js)
    - 인증 서비스 모듈 (authService.js) 구현
    - _요구사항: 6.1, 6.2, 6.3_

  - [ ] 15.3 채팅 인터페이스 컴포넌트 구현
    - ChatInterface.vue: 메인 채팅 화면 컴포넌트
    - MessageBubble.vue: 메시지 표시 컴포넌트 (사용자/시스템 구분)
    - InputArea.vue: 메시지 입력 영역 컴포넌트
    - 실시간 메시지 전송 및 수신 처리
    - 채팅 히스토리 관리 및 스크롤 처리
    - _요구사항: 8.1, 8.2_

  - [ ] 15.4 퀴즈 인터페이스 컴포넌트 구현
    - QuizInterface.vue: 메인 퀴즈 화면 컴포넌트
    - MultipleChoice.vue: 객관식 문제 컴포넌트
    - PromptPractice.vue: 프롬프트 실습 컴포넌트
    - 힌트 표시 및 답안 제출 처리
    - 퀴즈 결과 및 피드백 표시
    - _요구사항: 2.3, 7.1, 7.2, 8.3_

  - [ ] 15.5 학습 진도 및 통계 컴포넌트 구현
    - ProgressTracker.vue: 학습 진도 추적 컴포넌트
    - LearningStats.vue: 학습 통계 표시 컴포넌트
    - 챕터별 진도 시각화 (프로그레스 바, 차트)
    - 학습 기록 및 성과 통계 표시
    - 대시보드 레이아웃 구성
    - _요구사항: 5.3, 5.4_

  - [ ] 15.6 상태 관리 및 API 연동 구현
    - Pinia 스토어 구현:
      - learningStore.js: 학습 상태 관리
      - uiStore.js: UI 모드 및 상태 관리
    - API 서비스 모듈 구현:
      - learningService.js: 학습 관련 API 호출
      - websocketService.js: 실시간 통신 처리
    - 백엔드 UI 상태 동기화 로직 구현
    - 오류 처리 및 로딩 상태 관리
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 15.7 반응형 디자인 및 UX 최적화
    - 모바일/태블릿/데스크톱 반응형 레이아웃
    - 하이브리드 UX 패턴 구현 (채팅 ↔ 퀴즈 모드 전환)
    - 로딩 상태 및 오류 상태 UI 처리
    - 접근성(Accessibility) 고려사항 적용
    - 사용자 경험 최적화 (애니메이션, 트랜지션)
    - _요구사항: 8.1, 8.2, 8.3_

- [ ] 16. 백엔드-프론트엔드 통합 테스트
  - [ ] 16.1 End-to-End (E2E) 테스트 구현
    - Cypress 또는 Playwright 기반 E2E 테스트 환경 설정
    - 사용자 회원가입부터 학습 완료까지 전체 플로우 테스트
    - 채팅 모드와 퀴즈 모드 간 전환 테스트
    - 실시간 UI 상태 동기화 테스트
    - 다양한 브라우저 및 디바이스 호환성 테스트
    - _요구사항: 모든 요구사항_

  - [ ] 16.2 API-프론트엔드 통합 테스트
    - REST API와 Vue 3 컴포넌트 간 데이터 흐름 테스트
    - WebSocket 실시간 통신 안정성 테스트
    - 하이브리드 UX 패턴 동작 검증 테스트
    - 오류 상황에서의 프론트엔드 복구 테스트
    - 성능 및 로딩 시간 최적화 테스트
    - _요구사항: 8.1, 8.2, 8.3_

  - [ ] 16.3 사용자 시나리오 기반 통합 테스트
    - 초보자 사용자 학습 경로 전체 테스트
    - 실무자 사용자 학습 경로 전체 테스트
    - 멀티에이전트 워크플로우와 UI 연동 테스트
    - 학습 진도 추적 및 통계 표시 정확성 테스트
    - 외부 API (ChatGPT, ChromaDB) 연동 안정성 테스트
    - _요구사항: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4_

  - [ ] 16.4 성능 및 부하 테스트
    - 동시 사용자 접속 시 시스템 안정성 테스트
    - 대용량 대화 데이터 처리 성능 테스트
    - 프론트엔드 렌더링 성능 최적화 검증
    - 메모리 누수 및 리소스 사용량 모니터링
    - 모바일 환경에서의 성능 테스트
    - _요구사항: 5.1, 5.2, 8.1, 8.2_

- [ ] 17. 배포 준비 및 문서화
  - [ ] 17.1 배포 환경 설정
    - Docker 컨테이너화 및 docker-compose 설정
    - 환경별 설정 파일 분리 (개발/스테이징/프로덕션)
    - 데이터베이스 마이그레이션 스크립트 작성
    - 프론트엔드 빌드 및 정적 파일 서빙 설정
    - CI/CD 파이프라인 구성 (GitHub Actions 또는 GitLab CI)
    - _요구사항: 모든 요구사항_

  - [ ] 17.2 API 문서화 및 사용자 가이드
    - REST API 문서 작성 (Swagger/OpenAPI)
    - 시스템 아키텍처 문서 업데이트
    - 개발자 가이드 및 배포 가이드 작성
    - 프론트엔드 개발 가이드 및 컴포넌트 문서
    - 사용자 매뉴얼 및 튜토리얼 작성
    - _요구사항: 모든 요구사항_