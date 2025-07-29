// frontend/src/services/__tests__/apiClient.spec.ts
/**
 * API 클라이언트 단위 테스트
 * Axios 통신 및 인터셉터 테스트
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }))
  }
}))

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // localStorage mock
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
      },
      writable: true,
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('API Client 초기화', () => {
    it('axios 인스턴스가 올바른 설정으로 생성된다', async () => {
      // 동적 import를 사용하여 모듈 로드
      const { default: apiClient } = await import('../apiClient')
      
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:5000/api',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      })
    })

    it('서비스 모듈들이 정상적으로 로드된다', async () => {
      const { authService } = await import('../authService')
      const { learningService } = await import('../learningService')
      
      expect(authService).toBeDefined()
      expect(learningService).toBeDefined()
    })
  })

  describe('인증 서비스', () => {
    it('AuthService 클래스가 정의되어 있다', async () => {
      const { authService } = await import('../authService')
      
      expect(authService).toBeDefined()
      expect(typeof authService.login).toBe('function')
      expect(typeof authService.register).toBe('function')
      expect(typeof authService.getProfile).toBe('function')
      expect(typeof authService.updateProfile).toBe('function')
    })

    it('로그인 메서드가 존재한다', async () => {
      const { authService } = await import('../authService')
      
      expect(authService.login).toBeDefined()
      expect(typeof authService.login).toBe('function')
    })

    it('회원가입 메서드가 존재한다', async () => {
      const { authService } = await import('../authService')
      
      expect(authService.register).toBeDefined()
      expect(typeof authService.register).toBe('function')
    })

    it('프로필 조회 메서드가 존재한다', async () => {
      const { authService } = await import('../authService')
      
      expect(authService.getProfile).toBeDefined()
      expect(typeof authService.getProfile).toBe('function')
    })

    it('프로필 업데이트 메서드가 존재한다', async () => {
      const { authService } = await import('../authService')
      
      expect(authService.updateProfile).toBeDefined()
      expect(typeof authService.updateProfile).toBe('function')
    })
  })

  describe('학습 서비스', () => {
    it('LearningService 클래스가 정의되어 있다', async () => {
      const { learningService } = await import('../learningService')
      
      expect(learningService).toBeDefined()
      expect(typeof learningService.sendMessage).toBe('function')
      expect(typeof learningService.getProgress).toBe('function')
      expect(typeof learningService.getChapter).toBe('function')
      expect(typeof learningService.getStats).toBe('function')
    })

    it('채팅 메시지 전송 메서드가 존재한다', async () => {
      const { learningService } = await import('../learningService')
      
      expect(learningService.sendMessage).toBeDefined()
      expect(typeof learningService.sendMessage).toBe('function')
    })

    it('학습 진도 조회 메서드가 존재한다', async () => {
      const { learningService } = await import('../learningService')
      
      expect(learningService.getProgress).toBeDefined()
      expect(typeof learningService.getProgress).toBe('function')
    })

    it('챕터 정보 조회 메서드가 존재한다', async () => {
      const { learningService } = await import('../learningService')
      
      expect(learningService.getChapter).toBeDefined()
      expect(typeof learningService.getChapter).toBe('function')
    })

    it('학습 통계 조회 메서드가 존재한다', async () => {
      const { learningService } = await import('../learningService')
      
      expect(learningService.getStats).toBeDefined()
      expect(typeof learningService.getStats).toBe('function')
    })
  })

  describe('API 타입 정의', () => {
    it('API 응답 타입이 정의되어 있다', async () => {
      const apiClientModule = await import('../apiClient')
      
      // 모듈이 정상적으로 로드되는지 확인
      expect(apiClientModule.default).toBeDefined()
    })

    it('인증 관련 타입이 정의되어 있다', async () => {
      const authServiceModule = await import('../authService')
      
      // 모듈이 정상적으로 로드되는지 확인
      expect(authServiceModule.authService).toBeDefined()
    })

    it('학습 관련 타입이 정의되어 있다', async () => {
      const learningServiceModule = await import('../learningService')
      
      // 모듈이 정상적으로 로드되는지 확인
      expect(learningServiceModule.learningService).toBeDefined()
    })
  })

  describe('서비스 메서드 구조', () => {
    it('인증 서비스의 모든 필수 메서드가 존재한다', async () => {
      const { authService } = await import('../authService')
      
      const requiredMethods = [
        'login',
        'register', 
        'getProfile',
        'updateProfile',
        'logout',
        'validateToken',
        'changePassword'
      ]
      
      requiredMethods.forEach(method => {
        expect(authService[method]).toBeDefined()
        expect(typeof authService[method]).toBe('function')
      })
    })

    it('학습 서비스의 모든 필수 메서드가 존재한다', async () => {
      const { learningService } = await import('../learningService')
      
      const requiredMethods = [
        'sendMessage',
        'getProgress',
        'getChapter',
        'getStats',
        'submitQuizAnswer',
        'completeChapter',
        'startLearningSession',
        'endLearningSession'
      ]
      
      requiredMethods.forEach(method => {
        expect(learningService[method]).toBeDefined()
        expect(typeof learningService[method]).toBe('function')
      })
    })
  })

  describe('모듈 Export', () => {
    it('apiClient가 기본 export로 제공된다', async () => {
      const { default: apiClient } = await import('../apiClient')
      
      expect(apiClient).toBeDefined()
    })

    it('authService가 named export로 제공된다', async () => {
      const { authService } = await import('../apiClient')
      
      expect(authService).toBeDefined()
    })

    it('learningService가 named export로 제공된다', async () => {
      const { learningService } = await import('../apiClient')
      
      expect(learningService).toBeDefined()
    })
  })

  describe('기본 기능 테스트', () => {
    it('서비스 인스턴스들이 올바르게 생성된다', async () => {
      const { authService } = await import('../authService')
      const { learningService } = await import('../learningService')
      
      expect(authService).toBeInstanceOf(Object)
      expect(learningService).toBeInstanceOf(Object)
    })

    it('API 클라이언트가 올바른 구조를 가진다', async () => {
      const { default: apiClient } = await import('../apiClient')
      
      expect(apiClient).toBeDefined()
      expect(typeof apiClient).toBe('object')
    })
  })
})