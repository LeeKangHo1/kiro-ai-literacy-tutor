// frontend/src/stores/learningStore.ts
// 학습 상태 관리 스토어

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { type ChatMessage, type ChatResponse, type ApiResponse } from '@/services/apiClient'

// 메시지 타입 정의
export interface Message {
  id: string
  type: 'user' | 'system'
  content: string
  timestamp: Date
  ui_elements?: {
    type: string
    data: any
  }
}

// UI 모드 타입 정의
export type UIMode = 'chat' | 'quiz' | 'restricted'

export const useLearningStore = defineStore('learning', () => {
  // 상태 정의
  const messages = ref<Message[]>([])
  const currentChapter = ref<number>(1)
  const uiMode = ref<UIMode>('chat')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 계산된 속성
  const lastMessage = computed(() => {
    return messages.value.length > 0 ? messages.value[messages.value.length - 1] : null
  })

  const isQuizMode = computed(() => uiMode.value === 'quiz')
  const isChatMode = computed(() => uiMode.value === 'chat')

  // 메시지 ID 생성 헬퍼
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // 사용자 메시지 추가
  const addUserMessage = (content: string) => {
    const message: Message = {
      id: generateMessageId(),
      type: 'user',
      content,
      timestamp: new Date()
    }
    messages.value.push(message)
  }

  // 시스템 메시지 추가
  const addSystemMessage = (content: string, ui_elements?: any) => {
    const message: Message = {
      id: generateMessageId(),
      type: 'system',
      content,
      timestamp: new Date(),
      ui_elements
    }
    messages.value.push(message)
  }

  // 채팅 메시지 전송
  const sendMessage = async (content: string): Promise<boolean> => {
    if (!content.trim()) return false

    isLoading.value = true
    error.value = null

    // 사용자 메시지 추가
    addUserMessage(content)

    try {
      const chatMessage: ChatMessage = {
        message: content,
        context: {
          current_chapter: currentChapter.value,
          stage: 'chat'
        }
      }

      const response = await apiClient.post<ApiResponse<ChatResponse>>('/learning/chat/message', chatMessage)
      
      if (response.data.success && response.data.data) {
        const { response: systemResponse, ui_mode, ui_elements } = response.data.data
        
        // 시스템 응답 추가
        addSystemMessage(systemResponse, ui_elements)
        
        // UI 모드 업데이트
        uiMode.value = ui_mode
        
        return true
      } else {
        error.value = response.data.message || '메시지 전송에 실패했습니다.'
        return false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || '메시지 전송 중 오류가 발생했습니다.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 챕터 변경
  const setCurrentChapter = (chapterId: number) => {
    currentChapter.value = chapterId
  }

  // UI 모드 변경
  const setUIMode = (mode: UIMode) => {
    uiMode.value = mode
  }

  // 대화 히스토리 초기화
  const clearMessages = () => {
    messages.value = []
  }

  // 에러 초기화
  const clearError = () => {
    error.value = null
  }

  // 학습 세션 초기화
  const initializeLearningSession = () => {
    clearMessages()
    setCurrentChapter(1)
    setUIMode('chat')
    clearError()
    
    // 환영 메시지 추가
    addSystemMessage(
      '안녕하세요! AI 활용 맞춤형 학습 튜터에 오신 것을 환영합니다.\n\n' +
      '학습을 시작하려면 "시작"이라고 입력하거나, 궁금한 것이 있으면 언제든 질문해 주세요!'
    )
  }

  // 대화 기록 저장 (로컬 스토리지)
  const saveMessagesToLocal = () => {
    try {
      const data = {
        messages: messages.value,
        currentChapter: currentChapter.value,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem(`learning_session_${currentChapter.value}`, JSON.stringify(data))
    } catch (error) {
      console.warn('대화 기록 저장 실패:', error)
    }
  }

  // 대화 기록 복원 (로컬 스토리지)
  const loadMessagesFromLocal = (chapterId: number) => {
    try {
      const saved = localStorage.getItem(`learning_session_${chapterId}`)
      if (saved) {
        const data = JSON.parse(saved)
        // 1시간 이내의 데이터만 복원
        const savedTime = new Date(data.timestamp)
        const now = new Date()
        const hoursDiff = (now.getTime() - savedTime.getTime()) / (1000 * 60 * 60)
        
        if (hoursDiff < 1) {
          messages.value = data.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
          return true
        }
      }
    } catch (error) {
      console.warn('대화 기록 복원 실패:', error)
    }
    return false
  }

  return {
    // 상태
    messages,
    currentChapter,
    uiMode,
    isLoading,
    error,
    
    // 계산된 속성
    lastMessage,
    isQuizMode,
    isChatMode,
    
    // 액션
    addUserMessage,
    addSystemMessage,
    sendMessage,
    setCurrentChapter,
    setUIMode,
    clearMessages,
    clearError,
    initializeLearningSession,
    saveMessagesToLocal,
    loadMessagesFromLocal
  }
})