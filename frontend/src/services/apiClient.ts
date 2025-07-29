// frontend/src/services/apiClient.ts
// Axios API 클라이언트 설정

import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터 - JWT 토큰 자동 첨부
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // localStorage에서 직접 토큰을 가져와서 순환 참조 방지
    const token = localStorage.getItem('auth_token')
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 요청 로깅 (개발 환경에서만)
    if (import.meta.env.DEV) {
      console.log(`API 요청: ${config.method?.toUpperCase()} ${config.url}`)
    }
    
    return config
  },
  (error) => {
    console.error('API 요청 오류:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터 - 토큰 만료 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 401 오류 처리 (토큰 만료 또는 인증 실패)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // 로그인 요청이 아닌 경우에만 로그아웃 처리
      if (!originalRequest.url?.includes('/auth/login') && !originalRequest.url?.includes('/auth/register')) {
        console.log('토큰 만료 또는 인증 실패, 로그아웃 처리')
        
        // localStorage 정리
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
        
        // 현재 페이지를 리다이렉트 파라미터로 저장하여 로그인 페이지로 이동
        const currentPath = window.location.pathname + window.location.search
        const loginUrl = `/login?redirect=${encodeURIComponent(currentPath)}`
        
        // 로그인 페이지로 리다이렉트 (현재 페이지가 로그인 페이지가 아닌 경우)
        if (window.location.pathname !== '/login') {
          window.location.href = loginUrl
        }
      }
    }
    
    // 네트워크 오류 처리
    if (!error.response) {
      error.code = 'NETWORK_ERROR'
      error.message = '네트워크 연결을 확인해주세요.'
    }
    
    // 서버 오류 처리
    if (error.response?.status >= 500) {
      error.message = '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }
    
    return Promise.reject(error)
  }
)

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 인증 관련 API 타입
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  user_type: 'beginner' | 'business'
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    email: string
    user_type: 'beginner' | 'business'
    user_level: 'low' | 'medium' | 'high'
    created_at: string
    is_active: boolean
  }
}

// 학습 관련 API 타입
export interface ChatMessage {
  message: string
  context?: {
    current_chapter?: number
    loop_id?: string
    stage?: string
  }
}

export interface ChatResponse {
  response: string
  ui_mode: 'chat' | 'quiz' | 'restricted'
  ui_elements?: {
    type: string
    data: any
  } | null
  current_stage: string
  loop_id: string
}

// 진단 퀴즈 관련 타입
export interface DiagnosisRequest {
  answers: Record<string, any>
}

export interface DiagnosisResponse {
  user_type: 'beginner' | 'business'
  user_level: 'low' | 'medium' | 'high'
  recommended_chapters: number[]
}

// 서비스 인스턴스들을 export
export { authService } from './authService'
export { learningService } from './learningService'

export default apiClient