// frontend/src/stores/authStore.ts
// 인증 상태 관리 스토어

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { type LoginRequest, type LoginResponse, type ApiResponse } from '@/services/apiClient'

export const useAuthStore = defineStore('auth', () => {
  // 상태 정의
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<LoginResponse['user'] | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 계산된 속성
  const isAuthenticated = computed(() => !!token.value)
  const userType = computed(() => user.value?.user_type || null)
  const userLevel = computed(() => user.value?.user_level || null)

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
        
        return true
      } else {
        error.value = response.data.message || '로그인에 실패했습니다.'
        return false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || '로그인 중 오류가 발생했습니다.'
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
    error.value = null
  }

  // 토큰 검증 및 사용자 정보 복원
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user_data')
    
    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch (err) {
        // 저장된 데이터가 손상된 경우 초기화
        logout()
      }
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
    
    // 액션
    login,
    logout,
    initializeAuth,
    clearError
  }
})