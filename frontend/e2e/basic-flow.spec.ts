// frontend/e2e/basic-flow.spec.ts
/**
 * 기본 기능 플로우 E2E 테스트
 * 로그인 → 채팅 → 퀴즈 → 피드백 기본 플로우 테스트
 */

import { test, expect, Page } from '@playwright/test';

// 테스트용 사용자 데이터
const testUser = {
  username: 'testuser',
  email: 'test@example.com',
  password: 'testpassword123'
};

// API 응답 모킹을 위한 헬퍼 함수
async function mockApiResponses(page: Page) {
  // 로그인 API 모킹
  await page.route('**/api/auth/login', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-jwt-token',
        user_info: {
          user_id: 1,
          username: testUser.username,
          email: testUser.email,
          user_type: 'beginner',
          user_level: 'low'
        }
      })
    });
  });

  // 채팅 API 모킹 - 이론 설명
  await page.route('**/api/learning/chat', async route => {
    const request = route.request();
    const postData = request.postDataJSON();
    
    if (postData.message.includes('AI에 대해')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          system_message: 'AI(인공지능)는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.',
          ui_mode: 'chat',
          current_stage: 'theory_explanation',
          ui_elements: null
        })
      });
    } else if (postData.message.includes('문제')) {
      // 퀴즈 생성 응답
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          system_message: '다음 문제를 풀어보세요.',
          ui_mode: 'quiz',
          current_stage: 'quiz_solving',
          ui_elements: {
            quiz_type: 'multiple_choice',
            question: 'AI의 정의는 무엇인가요?',
            options: [
              '인공지능(Artificial Intelligence)',
              '자동화 시스템',
              '컴퓨터 프로그램',
              '데이터 분석 도구'
            ],
            correct_answer: 0
          }
        })
      });
    } else if (postData.quiz_answer) {
      // 퀴즈 평가 응답
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          system_message: '정답입니다! 잘 이해하고 계시네요.',
          ui_mode: 'feedback',
          current_stage: 'feedback_provided',
          ui_elements: {
            is_correct: true,
            score: 100,
            feedback: '완벽한 답변입니다. AI의 정의를 정확히 이해하고 계십니다.',
            explanation: 'AI는 인간의 지능을 모방하여 학습, 추론, 문제해결 등을 수행하는 기술입니다.'
          }
        })
      });
    }
  });

  // 사용자 프로필 API 모킹
  await page.route('**/api/user/profile', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user_id: 1,
        username: testUser.username,
        email: testUser.email,
        user_type: 'beginner',
        user_level: 'low'
      })
    });
  });

  // 학습 진도 API 모킹
  await page.route('**/api/learning/progress', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        chapters: [
          { chapter_id: 1, title: 'AI는 무엇인가?', progress: 25 },
          { chapter_id: 2, title: 'LLM이란 무엇인가?', progress: 0 }
        ],
        overall_progress: 12.5,
        current_chapter: 1
      })
    });
  });
}

test.describe('기본 기능 플로우 테스트', () => {
  test.beforeEach(async ({ page }) => {
    // API 응답 모킹 설정
    await mockApiResponses(page);
  });

  test('로그인 플로우 테스트', async ({ page }) => {
    // 로그인 페이지로 이동
    await page.goto('/');
    
    // 로그인 폼이 표시되는지 확인
    await expect(page.locator('h2')).toContainText('로그인');
    
    // 로그인 정보 입력
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    
    // 로그인 버튼 클릭
    await page.click('button[type="submit"]');
    
    // 로그인 성공 후 학습 페이지로 리다이렉트 확인
    await expect(page).toHaveURL('/learning');
    
    // 사용자 정보가 표시되는지 확인
    await expect(page.locator('.user-info')).toContainText(testUser.username);
  });

  test('채팅 인터페이스 테스트', async ({ page }) => {
    // 로그인 후 학습 페이지로 직접 이동
    await page.goto('/learning');
    
    // 채팅 인터페이스가 로드되는지 확인
    await expect(page.locator('.chat-interface')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
    
    // 메시지 입력 및 전송
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('AI에 대해 배우고 싶습니다');
    await page.click('button.send-button');
    
    // 시스템 응답 확인
    await expect(page.locator('.message.system').last()).toContainText('AI(인공지능)는');
    
    // UI 모드가 채팅 모드인지 확인
    await expect(page.locator('.chat-interface')).toHaveClass(/chat-mode/);
  });

  test('퀴즈 생성 및 표시 테스트', async ({ page }) => {
    // 학습 페이지로 이동
    await page.goto('/learning');
    
    // 퀴즈 요청
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('문제를 내주세요');
    await page.click('button.send-button');
    
    // 퀴즈 UI가 표시되는지 확인
    await expect(page.locator('.quiz-interface')).toBeVisible();
    await expect(page.locator('.quiz-question')).toContainText('AI의 정의는 무엇인가요?');
    
    // 객관식 선택지가 표시되는지 확인
    const options = page.locator('.quiz-option');
    await expect(options).toHaveCount(4);
    await expect(options.first()).toContainText('인공지능(Artificial Intelligence)');
    
    // UI 모드가 퀴즈 모드로 변경되었는지 확인
    await expect(page.locator('.chat-interface')).toHaveClass(/quiz-mode/);
  });

  test('퀴즈 답변 및 피드백 테스트', async ({ page }) => {
    // 학습 페이지로 이동하고 퀴즈 상태로 설정
    await page.goto('/learning');
    
    // 퀴즈 요청
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('문제를 내주세요');
    await page.click('button.send-button');
    
    // 퀴즈가 로드될 때까지 대기
    await expect(page.locator('.quiz-interface')).toBeVisible();
    
    // 첫 번째 선택지 클릭 (정답)
    await page.click('.quiz-option:first-child');
    
    // 답변 제출 버튼 클릭
    await page.click('button.submit-answer');
    
    // 피드백 UI가 표시되는지 확인
    await expect(page.locator('.feedback-interface')).toBeVisible();
    await expect(page.locator('.feedback-message')).toContainText('정답입니다!');
    await expect(page.locator('.feedback-score')).toContainText('100');
    
    // 상세 피드백 확인
    await expect(page.locator('.feedback-explanation')).toContainText('완벽한 답변입니다');
    
    // UI 모드가 피드백 모드로 변경되었는지 확인
    await expect(page.locator('.chat-interface')).toHaveClass(/feedback-mode/);
  });

  test('완전한 학습 플로우 테스트', async ({ page }) => {
    // 1단계: 로그인
    await page.goto('/');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    
    // 학습 페이지로 이동 확인
    await expect(page).toHaveURL('/learning');
    
    // 2단계: 이론 학습 요청
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('AI에 대해 배우고 싶습니다');
    await page.click('button.send-button');
    
    // 이론 설명 응답 확인
    await expect(page.locator('.message.system').last()).toContainText('AI(인공지능)는');
    
    // 3단계: 퀴즈 요청
    await messageInput.fill('문제를 내주세요');
    await page.click('button.send-button');
    
    // 퀴즈 표시 확인
    await expect(page.locator('.quiz-interface')).toBeVisible();
    await expect(page.locator('.quiz-question')).toContainText('AI의 정의는');
    
    // 4단계: 답변 제출
    await page.click('.quiz-option:first-child');
    await page.click('button.submit-answer');
    
    // 5단계: 피드백 확인
    await expect(page.locator('.feedback-interface')).toBeVisible();
    await expect(page.locator('.feedback-message')).toContainText('정답입니다!');
    
    // 전체 플로우가 성공적으로 완료되었는지 확인
    await expect(page.locator('.feedback-score')).toContainText('100');
  });

  test('JWT 토큰 인증 테스트', async ({ page }) => {
    // 로그인 없이 보호된 페이지 접근 시도
    await page.goto('/learning');
    
    // 로그인 페이지로 리다이렉트되는지 확인
    await expect(page).toHaveURL('/');
    
    // 로그인 후 원래 페이지로 리다이렉트되는지 확인
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/learning');
  });

  test('Axios 통신 오류 처리 테스트', async ({ page }) => {
    // API 오류 응답 모킹
    await page.route('**/api/learning/chat', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '서버 내부 오류가 발생했습니다.'
        })
      });
    });
    
    await page.goto('/learning');
    
    // 메시지 전송
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('테스트 메시지');
    await page.click('button.send-button');
    
    // 오류 메시지가 표시되는지 확인
    await expect(page.locator('.error-message')).toContainText('오류가 발생했습니다');
  });

  test('네트워크 연결 오류 처리 테스트', async ({ page }) => {
    // 네트워크 오류 시뮬레이션
    await page.route('**/api/learning/chat', async route => {
      await route.abort('failed');
    });
    
    await page.goto('/learning');
    
    // 메시지 전송
    const messageInput = page.locator('input.message-input');
    await messageInput.fill('테스트 메시지');
    await page.click('button.send-button');
    
    // 네트워크 오류 메시지가 표시되는지 확인
    await expect(page.locator('.error-message')).toContainText('네트워크 연결을 확인해주세요');
  });

  test('반응형 UI 테스트', async ({ page }) => {
    // 모바일 뷰포트로 설정
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/learning');
    
    // 모바일에서도 채팅 인터페이스가 정상 작동하는지 확인
    await expect(page.locator('.chat-interface')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
    
    // 데스크톱 뷰포트로 변경
    await page.setViewportSize({ width: 1200, height: 800 });
    
    // 데스크톱에서도 정상 작동하는지 확인
    await expect(page.locator('.chat-interface')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
  });

  test('세션 만료 처리 테스트', async ({ page }) => {
    // 만료된 토큰으로 API 응답 모킹
    await page.route('**/api/user/profile', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '토큰이 만료되었습니다.'
        })
      });
    });
    
    await page.goto('/learning');
    
    // 세션 만료 시 로그인 페이지로 리다이렉트되는지 확인
    await expect(page).toHaveURL('/');
    
    // 토큰 만료 알림이 표시되는지 확인
    await expect(page.locator('.alert')).toContainText('세션이 만료되었습니다');
  });
});

test.describe('접근성 테스트', () => {
  test('키보드 네비게이션 테스트', async ({ page }) => {
    await mockApiResponses(page);
    await page.goto('/learning');
    
    // Tab 키로 네비게이션 가능한지 확인
    await page.keyboard.press('Tab');
    await expect(page.locator('.message-input')).toBeFocused();
    
    // Enter 키로 메시지 전송 가능한지 확인
    await page.fill('.message-input', '테스트 메시지');
    await page.keyboard.press('Enter');
    
    // 메시지가 전송되었는지 확인
    await expect(page.locator('.message.user').last()).toContainText('테스트 메시지');
  });

  test('스크린 리더 지원 테스트', async ({ page }) => {
    await mockApiResponses(page);
    await page.goto('/learning');
    
    // ARIA 레이블이 적절히 설정되어 있는지 확인
    await expect(page.locator('.message-input')).toHaveAttribute('aria-label');
    await expect(page.locator('.send-button')).toHaveAttribute('aria-label');
    
    // 메시지 영역에 적절한 role이 설정되어 있는지 확인
    await expect(page.locator('.messages-container')).toHaveAttribute('role', 'log');
  });
});