-- migrations/init_schema.sql
-- AI 활용 맞춤형 학습 튜터 데이터베이스 초기 스키마

-- 데이터베이스 생성 (필요시)
-- CREATE DATABASE IF NOT EXISTS ai_literacy_navigator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE ai_literacy_navigator;

-- 사용자 정보 테이블
CREATE TABLE IF NOT EXISTS USERS (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('beginner', 'business') NOT NULL,
    user_level ENUM('low', 'medium', 'high') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 인덱스 생성
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_user_type (user_type),
    INDEX idx_user_level (user_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 챕터 정보 테이블
CREATE TABLE IF NOT EXISTS CHAPTERS (
    chapter_id INT PRIMARY KEY AUTO_INCREMENT,
    chapter_number INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty_level ENUM('low', 'medium', 'high') NOT NULL,
    estimated_duration INT DEFAULT 30, -- 예상 소요 시간 (분)
    prerequisites JSON, -- 선수 챕터 정보
    learning_objectives JSON, -- 학습 목표
    content_metadata JSON, -- 콘텐츠 메타데이터
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 인덱스 생성
    UNIQUE KEY uk_chapter_number (chapter_number),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 사용자 학습 진도 테이블
CREATE TABLE IF NOT EXISTS USER_LEARNING_PROGRESS (
    progress_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    chapter_id INT NOT NULL,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00, -- 진도율 (0.00 ~ 100.00)
    understanding_score DECIMAL(5,2) DEFAULT 0.00, -- 이해도 점수 (0.00 ~ 100.00)
    completion_status ENUM('not_started', 'in_progress', 'completed', 'skipped') DEFAULT 'not_started',
    started_at DATETIME,
    completed_at DATETIME,
    last_accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_study_time INT DEFAULT 0, -- 총 학습 시간 (분)
    quiz_attempts_count INT DEFAULT 0, -- 퀴즈 시도 횟수
    average_quiz_score DECIMAL(5,2) DEFAULT 0.00, -- 평균 퀴즈 점수
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES CHAPTERS(chapter_id) ON DELETE CASCADE,
    
    -- 복합 인덱스 및 일반 인덱스
    UNIQUE KEY uk_user_chapter (user_id, chapter_id),
    INDEX idx_completion_status (completion_status),
    INDEX idx_progress_percentage (progress_percentage),
    INDEX idx_understanding_score (understanding_score),
    INDEX idx_last_accessed_at (last_accessed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 학습 루프 테이블
CREATE TABLE IF NOT EXISTS LEARNING_LOOPS (
    loop_id VARCHAR(100) PRIMARY KEY,
    user_id INT NOT NULL,
    chapter_id INT NOT NULL,
    loop_sequence INT NOT NULL, -- 해당 챕터에서의 루프 순서
    loop_status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    loop_summary TEXT, -- 루프 요약 (압축된 대화 내용)
    loop_type ENUM('theory', 'quiz', 'qna', 'mixed') DEFAULT 'mixed', -- 루프 유형
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    duration_minutes INT DEFAULT 0, -- 루프 소요 시간 (분)
    interaction_count INT DEFAULT 0, -- 상호작용 횟수
    metadata JSON, -- 추가 메타데이터
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES CHAPTERS(chapter_id) ON DELETE CASCADE,
    
    -- 인덱스 생성
    INDEX idx_user_chapter (user_id, chapter_id),
    INDEX idx_loop_status (loop_status),
    INDEX idx_loop_sequence (loop_sequence),
    INDEX idx_started_at (started_at),
    INDEX idx_completed_at (completed_at),
    UNIQUE KEY uk_user_chapter_sequence (user_id, chapter_id, loop_sequence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 대화 기록 테이블
CREATE TABLE IF NOT EXISTS CONVERSATIONS (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    loop_id VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100) NOT NULL, -- 에이전트 이름
    message_type ENUM('user', 'system', 'tool', 'router') NOT NULL,
    user_message TEXT, -- 사용자 메시지
    system_response TEXT, -- 시스템 응답
    ui_elements JSON, -- UI 요소 정보
    ui_mode ENUM('chat', 'quiz', 'restricted', 'error') DEFAULT 'chat', -- UI 모드
    processing_time_ms INT DEFAULT 0, -- 처리 시간 (밀리초)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sequence_order INT NOT NULL, -- 루프 내 순서
    metadata JSON, -- 추가 메타데이터
    
    -- 외래키 제약조건
    FOREIGN KEY (loop_id) REFERENCES LEARNING_LOOPS(loop_id) ON DELETE CASCADE,
    
    -- 인덱스 생성
    INDEX idx_loop_id (loop_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_message_type (message_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_sequence_order (sequence_order),
    UNIQUE KEY uk_loop_sequence (loop_id, sequence_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 퀴즈 시도 테이블
CREATE TABLE IF NOT EXISTS QUIZ_ATTEMPTS (
    attempt_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    chapter_id INT NOT NULL,
    loop_id VARCHAR(100), -- 해당 루프 ID (선택적)
    quiz_type ENUM('multiple_choice', 'prompt_practice', 'diagnostic') NOT NULL,
    question_content JSON NOT NULL, -- 문제 내용 (JSON 형태)
    user_answer TEXT, -- 사용자 답변
    correct_answer TEXT, -- 정답
    is_correct BOOLEAN DEFAULT FALSE, -- 정답 여부
    score DECIMAL(5,2) DEFAULT 0.00, -- 점수 (0.00 ~ 100.00)
    hint_used BOOLEAN DEFAULT FALSE, -- 힌트 사용 여부
    hint_content TEXT, -- 사용된 힌트 내용
    feedback TEXT, -- 피드백 내용
    time_taken_seconds INT DEFAULT 0, -- 소요 시간 (초)
    difficulty_level ENUM('low', 'medium', 'high') NOT NULL,
    attempt_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON, -- 추가 메타데이터
    
    -- 외래키 제약조건
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES CHAPTERS(chapter_id) ON DELETE CASCADE,
    FOREIGN KEY (loop_id) REFERENCES LEARNING_LOOPS(loop_id) ON DELETE SET NULL,
    
    -- 인덱스 생성
    INDEX idx_user_chapter (user_id, chapter_id),
    INDEX idx_quiz_type (quiz_type),
    INDEX idx_is_correct (is_correct),
    INDEX idx_score (score),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_attempt_timestamp (attempt_timestamp),
    INDEX idx_loop_id (loop_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 초기 챕터 데이터 삽입
INSERT INTO CHAPTERS (chapter_number, title, description, difficulty_level, estimated_duration, learning_objectives) VALUES
(1, 'AI는 무엇인가?', 'AI, ML, DL의 개념과 차이점을 학습합니다.', 'low', 30, 
 JSON_OBJECT('objectives', JSON_ARRAY('AI의 정의 이해', 'ML과 DL의 차이점 구분', '실생활 AI 사례 파악'))),
(2, '머신러닝의 기초', '머신러닝의 기본 개념과 종류를 학습합니다.', 'medium', 45,
 JSON_OBJECT('objectives', JSON_ARRAY('지도학습과 비지도학습 구분', '머신러닝 알고리즘 종류 이해', '데이터의 중요성 인식'))),
(3, '프롬프트란 무엇인가?', '효과적인 프롬프트 작성법을 학습합니다.', 'medium', 40,
 JSON_OBJECT('objectives', JSON_ARRAY('프롬프트 구조 이해', '효과적인 프롬프트 작성법 습득', 'ChatGPT API 활용 실습'))),
(4, 'AI 윤리와 한계', 'AI의 윤리적 고려사항과 한계를 학습합니다.', 'high', 35,
 JSON_OBJECT('objectives', JSON_ARRAY('AI 편향성 이해', '개인정보 보호 중요성 인식', 'AI 한계점 파악')));

-- 성능 최적화를 위한 추가 인덱스
CREATE INDEX idx_users_active_type ON USERS(is_active, user_type);
CREATE INDEX idx_progress_user_status ON USER_LEARNING_PROGRESS(user_id, completion_status);
CREATE INDEX idx_loops_user_status ON LEARNING_LOOPS(user_id, loop_status);
CREATE INDEX idx_conversations_loop_agent ON CONVERSATIONS(loop_id, agent_name);
CREATE INDEX idx_quiz_user_correct ON QUIZ_ATTEMPTS(user_id, is_correct);

-- 데이터베이스 통계 업데이트
ANALYZE TABLE USERS, CHAPTERS, USER_LEARNING_PROGRESS, LEARNING_LOOPS, CONVERSATIONS, QUIZ_ATTEMPTS;