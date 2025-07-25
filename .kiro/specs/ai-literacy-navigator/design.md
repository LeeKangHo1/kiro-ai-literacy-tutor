# 설계 문서

## 개요

AI 활용 맞춤형 학습 튜터 (AI Literacy Navigator)는 LangGraph 기반의 멀티에이전트 시스템으로 구현되는 지능형 튜터링 플랫폼입니다. 6개의 핵심 에이전트와 2개의 라우터가 협력하여 개인화된 AI 학습 경험을 제공하며, 1루프 기반 대화 관리 시스템을 통해 효율적인 학습 진행을 지원합니다.

## 아키텍처

### 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chat UI       │  │  Quiz UI        │  │  Progress UI    │ │
│  │  (자유 대화)      │  │  (제한 UI)       │  │  (학습 기록)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                         REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Flask)                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              LangGraph Workflow                         │ │
│  │                                                         │ │
│  │  LearningSupervisor (조장)                               │ │
│  │         │                                               │ │
│  │  ┌──────┴──────┐                                        │ │
│  │  │ TheoryEducator │ → PostTheoryRouter                  │ │
│  │  └─────────────┘         │                             │ │
│  │                          ├─→ QnAResolver               │ │
│  │                          └─→ QuizGenerator              │ │
│  │                                    │                   │ │
│  │                          EvaluationFeedbackAgent       │ │
│  │                                    │                   │ │
│  │                          PostFeedbackRouter            │ │
│  │                                    │                   │ │
│  │                          ├─→ QnAResolver               │ │
│  │                          └─→ LearningSupervisor        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼────┐ ┌──▼──────┐
            │  MySQL   │ │ChromaDB│ │ChatGPT  │
            │    DB    │ │Vector  │ │  API    │
            │          │ │   DB   │ │         │
            └──────────┘ └────────┘ └─────────┘
```

### 멀티에이전트 시스템 (MAS) 설계

#### 에이전트 계층 구조
```
LearningSupervisor (학습 진행 총괄 조장)
├── TheoryEducator (개념 설명 전문가)
├── PostTheoryRouter (개념 설명 후 라우터)
├── QuizGenerator (문제 출제 전문가)
├── EvaluationFeedbackAgent (평가 및 피드백 전문가)
├── PostFeedbackRouter (피드백 후 라우터)
└── QnAResolver (실시간 질문 답변 전문가)
```

#### 학습 루프 워크플로우
```
1. LearningSupervisor → 학습 시작 및 진도 관리
2. TheoryEducator → 개념 설명 제공
3. PostTheoryRouter → 사용자 의도 파악 (질문 vs 문제)
4. QnAResolver 또는 QuizGenerator → 질문 답변 또는 문제 출제
5. EvaluationFeedbackAgent → 답변 평가 및 피드백
6. PostFeedbackRouter → 다음 행동 결정 (추가 질문 vs 진행)
7. LearningSupervisor → 루프 완료 처리 및 다음 단계 결정
```

## 컴포넌트 및 인터페이스

### 백엔드 컴포넌트

#### 1. Flask REST API 서버
```python
# app.py - 메인 애플리케이션
from flask import Flask
from flask_cors import CORS
from blueprints.auth import auth_bp
from blueprints.learning import learning_bp
from blueprints.user import user_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(learning_bp, url_prefix='/api/learning')
app.register_blueprint(user_bp, url_prefix='/api/user')
```

#### 2. LangGraph 워크플로우 관리자
```python
# workflow/tutor_workflow.py
from langgraph import StateGraph
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class TutorState(TypedDict):
    # 기본 정보
    user_id: str
    user_message: str
    current_chapter: int
    current_stage: str
    user_level: str
    user_type: str
    
    # 라우팅 관리
    qa_source_router: str
    ui_mode: str
    
    # 현재 루프 대화 (임시)
    current_loop_conversations: List[Dict[str, Any]]
    
    # 최근 루프 요약 (최대 5개)
    recent_loops_summary: List[Dict[str, str]]
    
    # 현재 루프 메타정보
    current_loop_id: str
    loop_start_time: datetime
    
    # 시스템 응답
    system_message: str
    ui_elements: Optional[Dict[str, Any]]
```

#### 3. 에이전트 구현
```python
# agents/learning_supervisor.py
class LearningSupervisor:
    def __init__(self):
        self.tools = [learning_analysis_tool]
    
    def execute(self, state: TutorState) -> TutorState:
        # 학습 진도 분석 및 다음 단계 결정
        pass

# agents/theory_educator.py
class TheoryEducator:
    def __init__(self):
        self.tools = [theory_generation_tool]
    
    def execute(self, state: TutorState) -> TutorState:
        # 사용자 레벨별 맞춤 개념 설명 생성
        pass
```

#### 4. 도구(Tools) 시스템
```python
# tools/content_generation.py
def theory_generation_tool(chapter_id: int, user_level: str, user_type: str) -> str:
    """사용자 레벨별 맞춤 설명 생성"""
    pass

def quiz_generation_tool(chapter_id: int, user_level: str, quiz_type: str) -> Dict:
    """객관식/프롬프트 문제 생성"""
    pass

# tools/external_integration.py
def prompt_practice_tool(user_prompt: str) -> Dict:
    """ChatGPT API 실제 테스트"""
    pass

def qna_search_tool(question: str, context: str) -> str:
    """ChromaDB 벡터 검색 + 웹 검색"""
    pass
```

### 데이터베이스 설계

#### 핵심 테이블 구조
```sql
-- 사용자 정보
CREATE TABLE USERS (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('beginner', 'business') NOT NULL,
    user_level ENUM('low', 'medium', 'high') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 학습 루프
CREATE TABLE LEARNING_LOOPS (
    loop_id VARCHAR(100) PRIMARY KEY,
    user_id INT NOT NULL,
    chapter_id INT NOT NULL,
    loop_sequence INT NOT NULL,
    loop_status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    loop_summary TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- 대화 기록
CREATE TABLE CONVERSATIONS (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    loop_id VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    message_type ENUM('user', 'system', 'tool') NOT NULL,
    user_message TEXT,
    system_response TEXT,
    ui_elements JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sequence_order INT NOT NULL,
    FOREIGN KEY (loop_id) REFERENCES LEARNING_LOOPS(loop_id)
);
```

### 프론트엔드 컴포넌트

#### Vue 3 컴포넌트 구조
```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatInterface.vue      # 자유 대화 UI
│   │   ├── MessageBubble.vue      # 메시지 표시
│   │   └── InputArea.vue          # 입력 영역
│   ├── Quiz/
│   │   ├── QuizInterface.vue      # 문제 풀이 UI
│   │   ├── MultipleChoice.vue     # 객관식 문제
│   │   └── PromptPractice.vue     # 프롬프트 실습
│   └── Progress/
│       ├── ProgressTracker.vue    # 진도 추적
│       └── LearningStats.vue      # 학습 통계
├── stores/
│   ├── authStore.js              # 인증 상태 관리
│   ├── learningStore.js          # 학습 상태 관리
│   └── uiStore.js                # UI 모드 관리
└── services/
    ├── authService.js            # 인증 API
    ├── learningService.js        # 학습 API
    └── websocketService.js       # 실시간 통신
```

## 데이터 모델

### State 관리 모델
```python
class TutorState(TypedDict):
    # 사용자 식별 및 기본 정보
    user_id: str                    # 사용자 고유 ID
    user_message: str               # 현재 사용자 메시지
    current_chapter: int            # 현재 학습 중인 챕터
    current_stage: str              # 현재 학습 단계
    user_level: str                 # 사용자 수준 (low/medium/high)
    user_type: str                  # 사용자 유형 (beginner/business)
    
    # 라우팅 및 UI 관리
    qa_source_router: str           # 질문 출처 라우터 식별
    ui_mode: str                    # UI 모드 (chat/quiz/restricted)
    
    # 대화 관리 (1루프 기반)
    current_loop_conversations: List[Dict[str, Any]]  # 현재 루프 대화
    recent_loops_summary: List[Dict[str, str]]        # 최근 5개 루프 요약
    
    # 루프 메타데이터
    current_loop_id: str            # 현재 루프 고유 ID
    loop_start_time: datetime       # 루프 시작 시간
    
    # 시스템 응답
    system_message: str             # 시스템 메시지
    ui_elements: Optional[Dict[str, Any]]  # UI 요소 정보
```

### 데이터베이스 관계 모델
```
USERS (1) ──── (N) USER_LEARNING_PROGRESS
  │                      │
  │                      │
  └── (N) LEARNING_LOOPS ─┘
           │
           ├── (N) CONVERSATIONS
           └── (N) QUIZ_ATTEMPTS

CHAPTERS (1) ──── (N) USER_LEARNING_PROGRESS
    │
    └── (N) LEARNING_LOOPS
```

## 오류 처리

### 에이전트 레벨 오류 처리
```python
class AgentErrorHandler:
    @staticmethod
    def handle_tool_error(tool_name: str, error: Exception, state: TutorState):
        """도구 실행 오류 처리"""
        error_message = f"{tool_name} 실행 중 오류가 발생했습니다."
        state["system_message"] = error_message
        state["ui_mode"] = "error"
        return state
    
    @staticmethod
    def handle_routing_error(router_name: str, state: TutorState):
        """라우팅 오류 처리"""
        state["system_message"] = "죄송합니다. 다시 말씀해 주세요."
        return state
```

### API 레벨 오류 처리
```python
# error_handlers.py
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': '인증이 필요합니다.'}), 401

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500
```

### 외부 서비스 오류 처리
```python
class ExternalServiceHandler:
    @staticmethod
    def handle_chatgpt_api_error(error):
        """ChatGPT API 오류 처리"""
        return {
            'success': False,
            'message': 'ChatGPT 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.'
        }
    
    @staticmethod
    def handle_chromadb_error(error):
        """ChromaDB 오류 처리"""
        return {
            'success': False,
            'message': '검색 서비스에 문제가 있습니다. 기본 답변을 제공합니다.'
        }
```

## 테스트 전략

### 단위 테스트
```python
# tests/test_agents.py
class TestTheoryEducator:
    def test_generate_theory_for_beginner(self):
        """초보자용 이론 생성 테스트"""
        pass
    
    def test_generate_theory_for_business(self):
        """실무자용 이론 생성 테스트"""
        pass

# tests/test_tools.py
class TestTools:
    def test_quiz_generation_tool(self):
        """퀴즈 생성 도구 테스트"""
        pass
    
    def test_prompt_practice_tool(self):
        """프롬프트 실습 도구 테스트"""
        pass
```

### 통합 테스트
```python
# tests/test_workflow.py
class TestTutorWorkflow:
    def test_complete_learning_loop(self):
        """완전한 학습 루프 테스트"""
        pass
    
    def test_routing_logic(self):
        """라우팅 로직 테스트"""
        pass
```

### 성능 테스트
```python
# tests/test_performance.py
class TestPerformance:
    def test_state_management_efficiency(self):
        """State 관리 효율성 테스트"""
        pass
    
    def test_database_query_performance(self):
        """데이터베이스 쿼리 성능 테스트"""
        pass
```

### E2E 테스트
```javascript
// tests/e2e/learning_flow.spec.js
describe('학습 플로우 E2E 테스트', () => {
  test('사용자 진단부터 첫 번째 챕터 완료까지', async () => {
    // 로그인 → 진단 → 학습 → 평가 전체 플로우 테스트
  });
  
  test('질문 답변 기능 테스트', async () => {
    // 자유 대화 모드에서 질문 답변 테스트
  });
});
```