// frontend/src/stores/authStore.ts
// 인증 상태 관리 스토어

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { type LoginRequest, type LoginResponse, type RegisterRequest, type ApiResponse } from '@/services/apiClient'
import { isTokenExpired, getTokenTimeRemaining } from '@/utils/authValidation'

export const useAuthStore = defineStore('auth', () => {
  // 상태 정의
  const token = ref<string | null>(null)
  const user = ref<LoginResponse['user'] | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 계산된 속성
  const isAuthenticated = computed(() => {
    if (!token.value || !user.value) {
      return false
    }
    
    // 토큰 만료 확인
    const tokenExpiry = localStorage.getItem('token_expiry')
    if (isTokenExpired(tokenExpiry)) {
      return false
    }
    
    return true
  })
  const userType = computed(() => user.value?.user_type || null)
  const userLevel = computed(() => user.value?.user_level || null)
  const tokenTimeRemaining = computed(() => {
    const tokenExpiry = localStorage.getItem('token_expiry')
    return getTokenTimeRemaining(tokenExpiry)
  })

  // 로그인 액션
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<ApiResponse<LoginResponse>>('/auth/login', credentials)
      
      if (response.data.success && response.data.data) {
        const { token: authToken, user: userData } = response.data.data
        
        // 토큰과 사용자 정보 저장
        token.value = authToken
        user.value = userData
        localStorage.setItem('auth_token', authToken)
        localStorage.setItem('user_data', JSON.stringify(userData))
        
        // 토큰 만료 시간 설정 (24시간 후)
        const expiryTime = new Date()
        expiryTime.setHours(expiryTime.getHours() + 24)
        localStorage.setItem('token_expiry', expiryTime.toISOString())
        
        return true
      } else {
        error.value = response.data.message || '로그인에 실패했습니다.'
        return false
      }
    } catch (err: any) {
      console.error('로그인 오류:', err)
      if (err.response?.status === 401) {
        error.value = '사용자명 또는 비밀번호가 올바르지 않습니다.'
      } else if (err.response?.status === 500) {
        error.value = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        error.value = '네트워크 연결을 확인해주세요.'
      } else {
        error.value = err.response?.data?.message || '로그인 중 오류가 발생했습니다.'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 로그아웃 액션
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('token_expiry')
    error.value = null
  }

  // 토큰 검증 및 사용자 정보 복원
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user_data')
    const tokenExpiry = localStorage.getItem('token_expiry')
    
    if (savedToken && savedUser) {
      try {
        // 토큰 만료 시간 확인
        if (tokenExpiry) {
          const expiryTime = new Date(tokenExpiry)
          const now = new Date()
          
          if (now >= expiryTime) {
            console.log('토큰이 만료되었습니다.')
            logout()
            return
          }
        }
        
        const userData = JSON.parse(savedUser)
        // 기본적인 데이터 검증
        if (userData && userData.id && userData.username) {
          token.value = savedToken
          user.value = userData
        } else {
          // 데이터가 유효하지 않은 경우 초기화
          logout()
        }
      } catch (err) {
        console.error('저장된 인증 데이터 복원 실패:', err)
        // 저장된 데이터가 손상된 경우 초기화
        logout()
      }
    }
  }

  // 토큰 유효성 검증 (서버 호출)
  const validateToken = async (): Promise<boolean> => {
    if (!token.value) {
      return false
    }

    try {
      const response = await apiClient.get<ApiResponse<LoginResponse['user']>>('/auth/validate')
      
      if (response.data.success && response.data.data) {
        user.value = response.data.data
        return true
      } else {
        logout()
        return false
      }
    } catch (err) {
      console.error('토큰 검증 실패:', err)
      logout()
      return false
    }
  }

  // 회원가입 액션
  const register = async (userData: RegisterRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<ApiResponse<LoginResponse>>('/auth/register', userData)
      
      if (response.data.success && response.data.data) {
        const { token: authToken, user: newUser } = response.data.data
        
        // 회원가입 성공 시 자동 로그인
        token.value = authToken
        user.value = newUser
        localStorage.setItem('auth_token', authToken)
        localStorage.setItem('user_data', JSON.stringify(newUser))
        
        // 토큰 만료 시간 설정 (24시간 후)
        const expiryTime = new Date()
        expiryTime.setHours(expiryTime.getHours() + 24)
        localStorage.setItem('token_expiry', expiryTime.toISOString())
        
        return true
      } else {
        error.value = response.data.message || '회원가입에 실패했습니다.'
        return false
      }
    } catch (err: any) {
      console.error('회원가입 오류:', err)
      if (err.response?.status === 409) {
        error.value = '이미 존재하는 사용자명 또는 이메일입니다.'
      } else if (err.response?.status === 400) {
        error.value = '입력 정보를 확인해주세요.'
      } else if (err.response?.status === 500) {
        error.value = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      } else if (err.code === 'NETWORK_ERROR' || !err.response) {
        error.value = '네트워크 연결을 확인해주세요.'
      } else {
        error.value = err.response?.data?.message || '회원가입 중 오류가 발생했습니다.'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 에러 초기화
  const clearError = () => {
    error.value = null
  }

  return {
    // 상태
    token,
    user,
    isLoading,
    error,
    
    // 계산된 속성
    isAuthenticated,
    userType,
    userLevel,
    tokenTimeRemaining,
    
    // 액션
    login,
    register,
    logout,
    initializeAuth,
    validateToken,
    clearError
  }
})