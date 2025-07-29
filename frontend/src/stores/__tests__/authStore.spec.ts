// frontend/src/stores/__tests__/authStore.spec.ts
/**
 * AuthStore 단위 테스트
 * JWT 인증 및 사용자 상태 관리 테스트
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../authStore'
import axios from 'axios'

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

const mockedAxios = vi.mocked(axios)

describe('AuthStore', () => {
  let authStore: ReturnType<typeof useAuthStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    authStore = useAuthStore()
    
    // localStorage mock
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('초기 상태', () => {
    it('초기 상태가 올바르게 설정된다', () => {
      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.isLoading).toBe(false)
      expect(authStore.error).toBeNull()
    })
  })

  describe('로그인 기능', () => {
    it('성공적인 로그인이 처리된다', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-jwt-token',
          user_info: {
            user_id: 1,
            username: 'testuser',
            email: 'test@example.com',
            user_type: 'beginner',
            user_level: 'low'
          }
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockResponse)

      const credentials = {
        username: 'testuser',
        password: 'testpassword123'
      }

      const result = await authStore.login(credentials)

      expect(result.success).toBe(true)
      expect(authStore.token).toBe('mock-jwt-token')
      expect(authStore.user).toEqual(mockResponse.data.user_info)
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.error).toBeNull()
      
      // localStorage에 토큰이 저장되었는지 확인
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'mock-jwt-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('user_info', JSON.stringify(mockResponse.data.user_info))
    })

    it('로그인 실패가 처리된다', async () => {
      const mockError = {
        response: {
          status: 401,
          data: {
            error: '잘못된 사용자명 또는 비밀번호입니다.'
          }
        }
      }

      mockedAxios.post.mockRejectedValueOnce(mockError)

      const credentials = {
        username: 'wronguser',
        password: 'wrongpassword'
      }

      const result = await authStore.login(credentials)

      expect(result.success).toBe(false)
      expect(result.error).toBe('잘못된 사용자명 또는 비밀번호입니다.')
      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.error).toBe('잘못된 사용자명 또는 비밀번호입니다.')
    })

    it('로그인 중 로딩 상태가 관리된다', async () => {
      let resolvePromise: (value: any) => void
      const mockPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })

      mockedAxios.post.mockReturnValueOnce(mockPromise)

      const loginPromise = authStore.login({
        username: 'testuser',
        password: 'testpassword123'
      })

      // 로딩 상태 확인
      expect(authStore.isLoading).toBe(true)

      // Promise 해결
      resolvePromise!({
        data: {
          access_token: 'token',
          user_info: { user_id: 1, username: 'testuser' }
        }
      })

      await loginPromise

      // 로딩 완료 확인
      expect(authStore.isLoading).toBe(false)
    })
  })

  describe('로그아웃 기능', () => {
    it('로그아웃이 정상적으로 처리된다', () => {
      // 로그인 상태 설정
      authStore.token = 'mock-token'
      authStore.user = { user_id: 1, username: 'testuser' }

      authStore.logout()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.error).toBeNull()
      
      // localStorage에서 데이터가 제거되었는지 확인
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user_info')
    })
  })

  describe('토큰 검증 기능', () => {
    it('유효한 토큰이 검증된다', () => {
      // Mock JWT 토큰 (실제로는 더 복잡한 구조)
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock-signature'
      
      authStore.token = mockToken
      
      const isValid = authStore.isTokenValid()
      expect(isValid).toBe(true)
    })

    it('만료된 토큰이 감지된다', () => {
      // 만료된 토큰 (exp가 과거)
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxfQ.mock-signature'
      
      authStore.token = expiredToken
      
      const isValid = authStore.isTokenValid()
      expect(isValid).toBe(false)
    })

    it('잘못된 형식의 토큰이 처리된다', () => {
      authStore.token = 'invalid-token'
      
      const isValid = authStore.isTokenValid()
      expect(isValid).toBe(false)
    })
  })

  describe('자동 로그인 기능', () => {
    it('저장된 토큰으로 자동 로그인이 수행된다', async () => {
      const mockToken = 'stored-token'
      const mockUser = {
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }

      // localStorage에서 데이터 반환 모킹
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'auth_token') return mockToken
        if (key === 'user_info') return JSON.stringify(mockUser)
        return null
      })

      // 사용자 정보 검증 API 모킹
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUser
      })

      const result = await authStore.initializeAuth()

      expect(result).toBe(true)
      expect(authStore.token).toBe(mockToken)
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('저장된 토큰이 없으면 자동 로그인이 실패한다', async () => {
      vi.mocked(localStorage.getItem).mockReturnValue(null)

      const result = await authStore.initializeAuth()

      expect(result).toBe(false)
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('저장된 토큰이 유효하지 않으면 자동 로그인이 실패한다', async () => {
      vi.mocked(localStorage.getItem).mockImplementation((key) => {
        if (key === 'auth_token') return 'invalid-token'
        return null
      })

      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 401 }
      })

      const result = await authStore.initializeAuth()

      expect(result).toBe(false)
      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('사용자 정보 업데이트', () => {
    it('사용자 정보가 업데이트된다', async () => {
      // 초기 사용자 설정
      authStore.user = {
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com',
        user_type: 'beginner',
        user_level: 'low'
      }

      const updatedInfo = {
        user_level: 'medium'
      }

      const mockResponse = {
        data: {
          ...authStore.user,
          ...updatedInfo
        }
      }

      mockedAxios.post.mockResolvedValueOnce(mockResponse)

      const result = await authStore.updateUserInfo(updatedInfo)

      expect(result.success).toBe(true)
      expect(authStore.user?.user_level).toBe('medium')
      
      // localStorage 업데이트 확인
      expect(localStorage.setItem).toHaveBeenCalledWith('user_info', JSON.stringify(mockResponse.data))
    })
  })

  describe('오류 처리', () => {
    it('네트워크 오류가 적절히 처리된다', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Network Error'))

      const result = await authStore.login({
        username: 'testuser',
        password: 'testpassword123'
      })

      expect(result.success).toBe(false)
      expect(result.error).toBe('네트워크 연결을 확인해주세요.')
      expect(authStore.error).toBe('네트워크 연결을 확인해주세요.')
    })

    it('서버 오류가 적절히 처리된다', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 500,
          data: {
            error: '서버 내부 오류'
          }
        }
      })

      const result = await authStore.login({
        username: 'testuser',
        password: 'testpassword123'
      })

      expect(result.success).toBe(false)
      expect(result.error).toBe('서버 내부 오류')
    })
  })

  describe('상태 초기화', () => {
    it('오류 상태가 초기화된다', () => {
      authStore.error = '테스트 오류'
      
      authStore.clearError()
      
      expect(authStore.error).toBeNull()
    })

    it('전체 상태가 초기화된다', () => {
      authStore.token = 'test-token'
      authStore.user = { user_id: 1, username: 'testuser' }
      authStore.error = '테스트 오류'
      
      authStore.reset()
      
      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.error).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Computed 속성', () => {
    it('isAuthenticated가 올바르게 계산된다', () => {
      expect(authStore.isAuthenticated).toBe(false)
      
      authStore.token = 'valid-token'
      authStore.user = { user_id: 1, username: 'testuser' }
      
      expect(authStore.isAuthenticated).toBe(true)
    })

    it('userDisplayName이 올바르게 계산된다', () => {
      expect(authStore.userDisplayName).toBe('')
      
      authStore.user = { user_id: 1, username: 'testuser', email: 'test@example.com' }
      
      expect(authStore.userDisplayName).toBe('testuser')
    })
  })
})