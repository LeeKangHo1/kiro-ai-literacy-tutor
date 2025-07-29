// frontend/src/services/authService.ts
// 인증 관련 API 서비스

import apiClient, { type LoginRequest, type RegisterRequest, type LoginResponse, type ApiResponse } from './apiClient'

export interface UserProfile {
  id: number
  username: string
  email: string
  user_type: 'beginner' | 'business'
  user_level: 'low' | 'medium' | 'high'
  created_at: string
  is_active: boolean
}

export interface UpdateProfileRequest {
  username?: string
  email?: string
  user_type?: 'beginner' | 'business'
}

class AuthService {
  /**
   * 사용자 로그인
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>('/auth/login', credentials)
    return response.data.data!
  }

  /**
   * 사용자 회원가입
   */
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>('/auth/register', userData)
    return response.data.data!
  }

  /**
   * 사용자 프로필 조회
   */
  async getProfile(): Promise<UserProfile | null> {
    try {
      const response = await apiClient.get<ApiResponse<UserProfile>>('/user/profile')
      return response.data.data || null
    } catch (error) {
      console.error('프로필 조회 실패:', error)
      return null
    }
  }

  /**
   * 사용자 프로필 업데이트
   */
  async updateProfile(updateData: UpdateProfileRequest): Promise<UserProfile> {
    const response = await apiClient.put<ApiResponse<UserProfile>>('/user/profile', updateData)
    return response.data.data!
  }

  /**
   * 로그아웃
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('로그아웃 API 호출 실패:', error)
    } finally {
      // 로컬 스토리지 정리
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
    }
  }

  /**
   * 토큰 유효성 검증
   */
  async validateToken(): Promise<boolean> {
    try {
      const response = await apiClient.get('/auth/validate')
      return response.status === 200
    } catch (error) {
      return false
    }
  }

  /**
   * 비밀번호 변경
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  }
}

export const authService = new AuthService()
export default authService