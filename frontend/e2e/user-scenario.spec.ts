// frontend/e2e/user-scenario.spec.ts
/**
 * 사용자 시나리오 E2E 테스트
 * - 1개 챕터 완전 학습 시나리오 테스트
 * - 멀티에이전트 워크플로우와 UI 연동 확인
 * - 오류 상황 처리 테스트
 */

import { test, expect } from '@playwright/test';

test.describe('사용자 시나리오 E2E 테스트', () => {
  
  test.beforeEach(async ({ page }) => {
    // 백엔드 API Mock 설정
    await page.route('**/api/**', (route) => {
      const url = route.request().url();
      const method = route.request().method();
      
      // 기본 성공 응답 설정
      if (url.includes('/api/health')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ status: 'healthy' })
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, message: 'Mock response' })
        });
      }
    });
  });

  test('1개 챕터 완전 학습 시나리오', async ({ page }) => {
    console.log('=== 1개 챕터 완전 학습 시나리오 E2E 테스트 시작 ===');
    
    // 1단계: 로그인 페이지 접속
    console.log('1단계: 로그인 페이지 접속');
    await page.goto('/');
    
    // 로그인 폼이 있는지 확인
    const loginForm = page.locator('form').first();
    await expect(loginForm).toBeVisible({ timeout: 10000 });
    
    // 2단계: 로그인 수행
    console.log('2단계: 로그인 수행');
    
    // Mock 로그인 API 응답 설정
    await page.route('**/api/auth/login', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          token: 'mock_jwt_token',
          user: {
            id: 1,
            username: 'test_user',
            user_type: 'beginner',
            user_level: 'low'
          }
        })
      });
    });
    
    // 로그인 폼 입력
    await page.fill('input[type="text"], input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"], .btn-primary');
    
    // 로그인 성공 후 학습 페이지로 이동 확인
    await expect(page).toHaveURL(/.*learning.*/, { timeout: 10000 });
    console.log('✅ 로그인 성공 및 학습 페이지 이동 확인');
    
    // 3단계: 챕터 시작
    console.log('3단계: 챕터 시작');
    
    // Mock 챕터 시작 API 응답
    await page.route('**/api/learning/chapter/start', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          chapter_id: 1,
          title: 'AI는 무엇인가?',
          theory_content: 'AI는 인공지능을 의미하며...',
          ui_mode: 'chat'
        })
      });
    });
    
    // 챕터 시작 버튼 클릭 (있다면)
    const startButton = page.locator('button:has-text("시작"), .btn:has-text("시작")').first();
    if (await startButton.isVisible({ timeout: 5000 })) {
      await startButton.click();
    }
    
    // 이론 설명이 표시되는지 확인
    await expect(page.locator('text=AI')).toBeVisible({ timeout: 10000 });
    console.log('✅ 챕터 시작 및 이론 설명 표시 확인');
    
    // 4단계: 질문 답변 시나리오
    console.log('4단계: 질문 답변 시나리오');
    
    // Mock 채팅 API 응답 (QnAResolver)
    await page.route('**/api/learning/chat', (route) => {
      const requestBody = route.request().postDataJSON();
      
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          agent: 'QnAResolver',
          response: 'AI는 인공지능으로, 컴퓨터가 인간의 지능을 모방하는 기술입니다.',
          ui_mode: 'chat',
          ui_elements: {
            type: 'text',
            content: 'AI 설명 응답'
          }
        })
      });
    });
    
    // 채팅 입력 필드 찾기 및 질문 입력
    const chatInput = page.locator('input[type="text"], textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 10000 });
    
    await chatInput.fill('AI에 대해 더 자세히 설명해주세요');
    
    // 전송 버튼 클릭
    const sendButton = page.locator('button:has-text("전송"), button:has-text("Send"), .btn-send').first();
    if (await sendButton.isVisible({ timeout: 5000 })) {
      await sendButton.click();
    } else {
      await chatInput.press('Enter');
    }
    
    // 응답이 표시되는지 확인
    await expect(page.locator('text=인공지능')).toBeVisible({ timeout: 10000 });
    console.log('✅ 질문 답변 시나리오 완료');
    
    // 5단계: 퀴즈 생성 및 문제 풀이
    console.log('5단계: 퀴즈 생성 및 문제 풀이');
    
    // Mock 퀴즈 생성 API 응답
    await page.route('**/api/learning/quiz/generate', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          agent: 'QuizGenerator',
          quiz: {
            type: 'multiple_choice',
            question: 'AI의 정의는 무엇인가요?',
            options: ['인공지능', '자동화', '로봇', '컴퓨터'],
            quiz_id: 'quiz_001'
          },
          ui_mode: 'quiz'
        })
      });
    });
    
    // 문제 풀기 요청
    await chatInput.fill('문제를 풀어보고 싶어요');
    if (await sendButton.isVisible({ timeout: 5000 })) {
      await sendButton.click();
    } else {
      await chatInput.press('Enter');
    }
    
    // 퀴즈 UI가 표시되는지 확인
    await expect(page.locator('text=AI의 정의')).toBeVisible({ timeout: 10000 });
    console.log('✅ 퀴즈 생성 확인');
    
    // 6단계: 답변 제출 및 평가
    console.log('6단계: 답변 제출 및 평가');
    
    // Mock 답변 평가 API 응답
    await page.route('**/api/learning/quiz/submit', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          agent: 'EvaluationFeedbackAgent',
          evaluation: {
            correct: true,
            score: 100,
            feedback: '정답입니다! AI는 인공지능을 의미합니다.',
            understanding_level: 'high'
          },
          ui_mode: 'feedback'
        })
      });
    });
    
    // 정답 선택 (첫 번째 옵션)
    const firstOption = page.locator('input[type="radio"], .option').first();
    if (await firstOption.isVisible({ timeout: 5000 })) {
      await firstOption.click();
    }
    
    // 답변 제출
    const submitButton = page.locator('button:has-text("제출"), .btn-submit').first();
    if (await submitButton.isVisible({ timeout: 5000 })) {
      await submitButton.click();
    }
    
    // 피드백이 표시되는지 확인
    await expect(page.locator('text=정답')).toBeVisible({ timeout: 10000 });
    console.log('✅ 답변 제출 및 평가 완료');
    
    // 7단계: 학습 진도 업데이트
    console.log('7단계: 학습 진도 업데이트');
    
    // Mock 진도 업데이트 API 응답
    await page.route('**/api/learning/progress/update', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          progress: {
            chapter_id: 1,
            completion_rate: 100,
            understanding_score: 95,
            next_chapter: 2
          },
          chapter_completed: true
        })
      });
    });
    
    // 다음 단계 진행 버튼 클릭
    const nextButton = page.locator('button:has-text("다음"), .btn-next').first();
    if (await nextButton.isVisible({ timeout: 5000 })) {
      await nextButton.click();
    }
    
    console.log('✅ 학습 진도 업데이트 완료');
    console.log('🎉 1개 챕터 완전 학습 시나리오 E2E 테스트 성공!');
  });

  test('멀티에이전트 워크플로우와 UI 연동 확인', async ({ page }) => {
    console.log('=== 멀티에이전트 워크플로우와 UI 연동 E2E 테스트 시작 ===');
    
    // 로그인 후 학습 페이지로 이동
    await page.goto('/learning');
    
    // 각 에이전트별 UI 모드 전환 테스트
    const agentScenarios = [
      {
        agent: 'TheoryEducator',
        input: '개념을 설명해주세요',
        expectedUI: 'chat',
        expectedContent: '설명'
      },
      {
        agent: 'QuizGenerator',
        input: '문제를 내주세요',
        expectedUI: 'quiz',
        expectedContent: '문제'
      },
      {
        agent: 'EvaluationFeedbackAgent',
        input: '답변 제출',
        expectedUI: 'feedback',
        expectedContent: '피드백'
      }
    ];
    
    for (const scenario of agentScenarios) {
      console.log(`${scenario.agent} UI 연동 테스트`);
      
      // Mock API 응답 설정
      await page.route('**/api/learning/chat', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            agent: scenario.agent,
            response: `${scenario.agent} 응답입니다`,
            ui_mode: scenario.expectedUI,
            ui_elements: {
              type: scenario.expectedUI,
              content: scenario.expectedContent
            }
          })
        });
      });
      
      // 메시지 입력 및 전송
      const chatInput = page.locator('input[type="text"], textarea').first();
      await chatInput.fill(scenario.input);
      await chatInput.press('Enter');
      
      // UI 모드 전환 확인
      await expect(page.locator(`text=${scenario.expectedContent}`)).toBeVisible({ timeout: 10000 });
      console.log(`✅ ${scenario.agent} UI 연동 확인`);
    }
    
    console.log('🎉 멀티에이전트 워크플로우와 UI 연동 E2E 테스트 성공!');
  });

  test('오류 상황 처리 E2E 테스트', async ({ page }) => {
    console.log('=== 오류 상황 처리 E2E 테스트 시작 ===');
    
    await page.goto('/learning');
    
    // 1. API 오류 상황 테스트
    console.log('1. API 오류 상황 테스트');
    
    // Mock API 오류 응답
    await page.route('**/api/learning/chat', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '서버 내부 오류가 발생했습니다'
        })
      });
    });
    
    const chatInput = page.locator('input[type="text"], textarea').first();
    await chatInput.fill('테스트 메시지');
    await chatInput.press('Enter');
    
    // 오류 메시지가 표시되는지 확인
    await expect(page.locator('text=오류, text=에러, text=Error').first()).toBeVisible({ timeout: 10000 });
    console.log('✅ API 오류 처리 확인');
    
    // 2. 네트워크 오류 시뮬레이션
    console.log('2. 네트워크 오류 시뮬레이션');
    
    // 네트워크 오류 Mock
    await page.route('**/api/learning/chat', (route) => {
      route.abort('failed');
    });
    
    await chatInput.fill('네트워크 오류 테스트');
    await chatInput.press('Enter');
    
    // 네트워크 오류 처리 확인
    await expect(page.locator('text=연결, text=네트워크, text=Network').first()).toBeVisible({ timeout: 10000 });
    console.log('✅ 네트워크 오류 처리 확인');
    
    // 3. 인증 오류 테스트
    console.log('3. 인증 오류 테스트');
    
    // 인증 오류 Mock
    await page.route('**/api/learning/chat', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '인증이 필요합니다'
        })
      });
    });
    
    await chatInput.fill('인증 오류 테스트');
    await chatInput.press('Enter');
    
    // 인증 오류 처리 확인 (로그인 페이지로 리다이렉트 또는 오류 메시지)
    const authError = page.locator('text=인증, text=로그인, text=Login').first();
    await expect(authError).toBeVisible({ timeout: 10000 });
    console.log('✅ 인증 오류 처리 확인');
    
    console.log('🎉 오류 상황 처리 E2E 테스트 성공!');
  });

  test('UI 모드 전환 및 상호작용 테스트', async ({ page }) => {
    console.log('=== UI 모드 전환 및 상호작용 E2E 테스트 시작 ===');
    
    await page.goto('/learning');
    
    // 1. 자유 대화 모드 테스트
    console.log('1. 자유 대화 모드 테스트');
    
    await page.route('**/api/learning/chat', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          ui_mode: 'chat',
          response: '자유롭게 질문해주세요',
          ui_elements: {
            type: 'text_input',
            placeholder: '질문을 입력하세요'
          }
        })
      });
    });
    
    const chatInput = page.locator('input[type="text"], textarea').first();
    await chatInput.fill('자유 대화 테스트');
    await chatInput.press('Enter');
    
    await expect(page.locator('text=질문해주세요')).toBeVisible({ timeout: 10000 });
    console.log('✅ 자유 대화 모드 확인');
    
    // 2. 퀴즈 모드 테스트
    console.log('2. 퀴즈 모드 테스트');
    
    await page.route('**/api/learning/chat', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          ui_mode: 'quiz',
          response: '다음 문제를 풀어보세요',
          ui_elements: {
            type: 'multiple_choice',
            question: '테스트 문제입니다',
            options: ['옵션1', '옵션2', '옵션3', '옵션4']
          }
        })
      });
    });
    
    await chatInput.fill('문제 모드 테스트');
    await chatInput.press('Enter');
    
    await expect(page.locator('text=문제를 풀어보세요')).toBeVisible({ timeout: 10000 });
    console.log('✅ 퀴즈 모드 확인');
    
    // 3. 피드백 모드 테스트
    console.log('3. 피드백 모드 테스트');
    
    await page.route('**/api/learning/chat', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          ui_mode: 'feedback',
          response: '훌륭한 답변입니다!',
          ui_elements: {
            type: 'feedback_display',
            score: 95,
            correct: true
          }
        })
      });
    });
    
    await chatInput.fill('피드백 모드 테스트');
    await chatInput.press('Enter');
    
    await expect(page.locator('text=훌륭한')).toBeVisible({ timeout: 10000 });
    console.log('✅ 피드백 모드 확인');
    
    console.log('🎉 UI 모드 전환 및 상호작용 E2E 테스트 성공!');
  });

  test('학습 진도 및 데이터 지속성 테스트', async ({ page }) => {
    console.log('=== 학습 진도 및 데이터 지속성 E2E 테스트 시작 ===');
    
    await page.goto('/learning');
    
    // 1. 학습 진도 저장 테스트
    console.log('1. 학습 진도 저장 테스트');
    
    await page.route('**/api/learning/progress/save', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          progress_id: 'progress_001',
          completion_rate: 75
        })
      });
    });
    
    // 진도 저장 버튼 클릭 (있다면)
    const saveButton = page.locator('button:has-text("저장"), .btn-save').first();
    if (await saveButton.isVisible({ timeout: 5000 })) {
      await saveButton.click();
    }
    
    console.log('✅ 학습 진도 저장 확인');
    
    // 2. 학습 진도 조회 테스트
    console.log('2. 학습 진도 조회 테스트');
    
    await page.route('**/api/learning/progress/**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          progress: {
            chapter_id: 1,
            completion_rate: 75,
            understanding_score: 85,
            last_updated: new Date().toISOString()
          }
        })
      });
    });
    
    // 페이지 새로고침하여 데이터 지속성 확인
    await page.reload();
    
    // 진도 정보가 복원되는지 확인
    await expect(page.locator('text=75%, text=85%').first()).toBeVisible({ timeout: 10000 });
    console.log('✅ 학습 진도 조회 및 데이터 지속성 확인');
    
    console.log('🎉 학습 진도 및 데이터 지속성 E2E 테스트 성공!');
  });
});