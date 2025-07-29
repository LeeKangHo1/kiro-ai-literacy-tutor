// frontend/src/components/__tests__/ChatInterface.spec.ts
/**
 * ChatInterface 컴포넌트 단위 테스트
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ChatInterface from '../ChatInterface.vue'
import { useLearningStore } from '../../stores/learningStore'
import { useAuthStore } from '../../stores/authStore'

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

describe('ChatInterface', () => {
  let wrapper: VueWrapper
  let learningStore: any
  let authStore: any

  beforeEach(() => {
    setActivePinia(createPinia())
    learningStore = useLearningStore()
    authStore = useAuthStore()
    
    // Mock 사용자 인증 상태
    authStore.user = {
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
      user_type: 'beginner',
      user_level: 'low'
    }
    authStore.token = 'mock-jwt-token'
    authStore.isAuthenticated = true

    wrapper = mount(ChatInterface, {
      global: {
        plugins: [createPinia()]
      }
    })
  })

  it('컴포넌트가 정상적으로 렌더링된다', () => {
    expect(wrapper.find('.chat-interface').exists()).toBe(true)
    expect(wrapper.find('.messages-container').exists()).toBe(true)
    expect(wrapper.find('.input-area').exists()).toBe(true)
  })

  it('메시지 입력 필드가 정상적으로 작동한다', async () => {
    const messageInput = wrapper.find('input.message-input')
    expect(messageInput.exists()).toBe(true)

    // 메시지 입력
    await messageInput.setValue('테스트 메시지')
    expect((messageInput.element as HTMLInputElement).value).toBe('테스트 메시지')
  })

  it('메시지 전송 버튼이 정상적으로 작동한다', async () => {
    const messageInput = wrapper.find('input.message-input')
    const sendButton = wrapper.find('button.send-button')
    
    expect(sendButton.exists()).toBe(true)
    expect(sendButton.attributes('disabled')).toBeDefined() // 빈 메시지일 때 비활성화

    // 메시지 입력 후 버튼 활성화 확인
    await messageInput.setValue('테스트 메시지')
    expect(sendButton.attributes('disabled')).toBeUndefined()
  })

  it('Enter 키로 메시지를 전송할 수 있다', async () => {
    const messageInput = wrapper.find('input.message-input')
    const sendMessageSpy = vi.spyOn(wrapper.vm, 'sendMessage')

    await messageInput.setValue('테스트 메시지')
    await messageInput.trigger('keyup.enter')

    expect(sendMessageSpy).toHaveBeenCalled()
  })

  it('메시지 히스토리가 정상적으로 표시된다', async () => {
    // Mock 메시지 데이터 설정
    learningStore.messages = [
      {
        id: 1,
        type: 'user',
        content: '안녕하세요',
        timestamp: new Date()
      },
      {
        id: 2,
        type: 'system',
        content: '안녕하세요! 무엇을 도와드릴까요?',
        timestamp: new Date()
      }
    ]

    await wrapper.vm.$nextTick()

    const messages = wrapper.findAll('.message')
    expect(messages).toHaveLength(2)
    expect(messages[0].classes()).toContain('user')
    expect(messages[1].classes()).toContain('system')
  })

  it('채팅 모드에서 자유로운 입력이 가능하다', async () => {
    learningStore.uiMode = 'chat'
    await wrapper.vm.$nextTick()

    const messageInput = wrapper.find('input.message-input')
    expect(messageInput.exists()).toBe(true)
    expect(messageInput.attributes('placeholder')).toContain('메시지를 입력하세요')
  })

  it('퀴즈 모드에서 객관식 선택지가 표시된다', async () => {
    learningStore.uiMode = 'quiz'
    learningStore.currentQuiz = {
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

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.quiz-interface').exists()).toBe(true)
    expect(wrapper.find('.quiz-question').text()).toBe('AI의 정의는 무엇인가요?')
    
    const options = wrapper.findAll('.quiz-option')
    expect(options).toHaveLength(4)
    expect(options[0].text()).toContain('인공지능(Artificial Intelligence)')
  })

  it('퀴즈 선택지를 클릭할 수 있다', async () => {
    learningStore.uiMode = 'quiz'
    learningStore.currentQuiz = {
      quiz_type: 'multiple_choice',
      question: '테스트 질문',
      options: ['옵션1', '옵션2', '옵션3', '옵션4'],
      correct_answer: 0
    }

    await wrapper.vm.$nextTick()

    const firstOption = wrapper.find('.quiz-option:first-child')
    await firstOption.trigger('click')

    expect(wrapper.vm.selectedOption).toBe(0)
    expect(firstOption.classes()).toContain('selected')
  })

  it('퀴즈 답변을 제출할 수 있다', async () => {
    learningStore.uiMode = 'quiz'
    learningStore.currentQuiz = {
      quiz_type: 'multiple_choice',
      question: '테스트 질문',
      options: ['옵션1', '옵션2'],
      correct_answer: 0
    }

    await wrapper.vm.$nextTick()

    // 선택지 선택
    const firstOption = wrapper.find('.quiz-option:first-child')
    await firstOption.trigger('click')

    // 답변 제출
    const submitButton = wrapper.find('button.submit-answer')
    expect(submitButton.exists()).toBe(true)
    expect(submitButton.attributes('disabled')).toBeUndefined()

    const submitAnswerSpy = vi.spyOn(wrapper.vm, 'submitAnswer')
    await submitButton.trigger('click')

    expect(submitAnswerSpy).toHaveBeenCalled()
  })

  it('피드백 모드에서 결과가 표시된다', async () => {
    learningStore.uiMode = 'feedback'
    learningStore.currentFeedback = {
      is_correct: true,
      score: 100,
      feedback: '정답입니다!',
      explanation: '완벽한 답변입니다.'
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.feedback-interface').exists()).toBe(true)
    expect(wrapper.find('.feedback-message').text()).toBe('정답입니다!')
    expect(wrapper.find('.feedback-score').text()).toContain('100')
    expect(wrapper.find('.feedback-explanation').text()).toBe('완벽한 답변입니다.')
  })

  it('로딩 상태가 정상적으로 표시된다', async () => {
    learningStore.isLoading = true
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.loading-indicator').exists()).toBe(true)
    expect(wrapper.find('button.send-button').attributes('disabled')).toBeDefined()
  })

  it('오류 상태가 정상적으로 표시된다', async () => {
    learningStore.error = '서버 오류가 발생했습니다.'
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toContain('서버 오류가 발생했습니다.')
  })

  it('메시지 전송 시 스토어 액션이 호출된다', async () => {
    const sendMessageSpy = vi.spyOn(learningStore, 'sendMessage')
    
    const messageInput = wrapper.find('input.message-input')
    const sendButton = wrapper.find('button.send-button')

    await messageInput.setValue('테스트 메시지')
    await sendButton.trigger('click')

    expect(sendMessageSpy).toHaveBeenCalledWith('테스트 메시지', 1) // chapter_id = 1
  })

  it('스크롤이 자동으로 최하단으로 이동한다', async () => {
    const scrollToBottomSpy = vi.spyOn(wrapper.vm, 'scrollToBottom')
    
    // 새 메시지 추가
    learningStore.messages.push({
      id: 3,
      type: 'system',
      content: '새로운 메시지',
      timestamp: new Date()
    })

    await wrapper.vm.$nextTick()
    expect(scrollToBottomSpy).toHaveBeenCalled()
  })

  it('컴포넌트 언마운트 시 정리 작업이 수행된다', () => {
    const clearErrorSpy = vi.spyOn(learningStore, 'clearError')
    
    wrapper.unmount()
    expect(clearErrorSpy).toHaveBeenCalled()
  })

  it('반응형 디자인이 적용된다', async () => {
    // 모바일 뷰포트 시뮬레이션
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    await wrapper.vm.$nextTick()
    
    expect(wrapper.find('.chat-interface').classes()).toContain('mobile')
  })

  it('접근성 속성이 올바르게 설정된다', () => {
    const messageInput = wrapper.find('input.message-input')
    const sendButton = wrapper.find('button.send-button')
    const messagesContainer = wrapper.find('.messages-container')

    expect(messageInput.attributes('aria-label')).toBeDefined()
    expect(sendButton.attributes('aria-label')).toBeDefined()
    expect(messagesContainer.attributes('role')).toBe('log')
    expect(messagesContainer.attributes('aria-live')).toBe('polite')
  })
})