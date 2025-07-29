// frontend/src/utils/authValidation.ts
// 인증 관련 유효성 검사 유틸리티

export interface ValidationResult {
  isValid: boolean
  errors: string[]
}

export interface LoginFormData {
  username: string
  password: string
}

export interface RegisterFormData {
  username: string
  email: string
  password: string
  confirmPassword: string
  user_type: 'beginner' | 'business'
}

/**
 * 로그인 폼 유효성 검사
 */
export const validateLoginForm = (data: LoginFormData): ValidationResult => {
  const errors: string[] = []

  // 사용자명 검증
  if (!data.username || data.username.trim().length === 0) {
    errors.push('사용자명을 입력해주세요.')
  } else if (data.username.trim().length < 3) {
    errors.push('사용자명은 3자 이상이어야 합니다.')
  } else if (data.username.trim().length > 50) {
    errors.push('사용자명은 50자 이하여야 합니다.')
  }

  // 비밀번호 검증
  if (!data.password || data.password.length === 0) {
    errors.push('비밀번호를 입력해주세요.')
  } else if (data.password.length < 6) {
    errors.push('비밀번호는 6자 이상이어야 합니다.')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * 회원가입 폼 유효성 검사
 */
export const validateRegisterForm = (data: RegisterFormData): ValidationResult => {
  const errors: string[] = []

  // 사용자명 검증
  if (!data.username || data.username.trim().length === 0) {
    errors.push('사용자명을 입력해주세요.')
  } else if (data.username.trim().length < 3) {
    errors.push('사용자명은 3자 이상이어야 합니다.')
  } else if (data.username.trim().length > 50) {
    errors.push('사용자명은 50자 이하여야 합니다.')
  } else if (!/^[a-zA-Z0-9_]+$/.test(data.username.trim())) {
    errors.push('사용자명은 영문, 숫자, 밑줄(_)만 사용할 수 있습니다.')
  }

  // 이메일 검증
  if (!data.email || data.email.trim().length === 0) {
    errors.push('이메일을 입력해주세요.')
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email.trim())) {
    errors.push('올바른 이메일 형식을 입력해주세요.')
  } else if (data.email.trim().length > 100) {
    errors.push('이메일은 100자 이하여야 합니다.')
  }

  // 비밀번호 검증
  if (!data.password || data.password.length === 0) {
    errors.push('비밀번호를 입력해주세요.')
  } else if (data.password.length < 8) {
    errors.push('비밀번호는 8자 이상이어야 합니다.')
  } else if (data.password.length > 128) {
    errors.push('비밀번호는 128자 이하여야 합니다.')
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.push('비밀번호는 대문자, 소문자, 숫자를 각각 하나 이상 포함해야 합니다.')
  }

  // 비밀번호 확인 검증
  if (!data.confirmPassword || data.confirmPassword.length === 0) {
    errors.push('비밀번호 확인을 입력해주세요.')
  } else if (data.password !== data.confirmPassword) {
    errors.push('비밀번호가 일치하지 않습니다.')
  }

  // 사용자 유형 검증
  if (!data.user_type || !['beginner', 'business'].includes(data.user_type)) {
    errors.push('사용자 유형을 선택해주세요.')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * 토큰 만료 시간 확인
 */
export const isTokenExpired = (tokenExpiry: string | null): boolean => {
  if (!tokenExpiry) {
    return true
  }

  try {
    const expiryTime = new Date(tokenExpiry)
    const now = new Date()
    return now >= expiryTime
  } catch (error) {
    console.error('토큰 만료 시간 파싱 오류:', error)
    return true
  }
}

/**
 * 토큰 만료까지 남은 시간 (분 단위)
 */
export const getTokenTimeRemaining = (tokenExpiry: string | null): number => {
  if (!tokenExpiry) {
    return 0
  }

  try {
    const expiryTime = new Date(tokenExpiry)
    const now = new Date()
    const diffMs = expiryTime.getTime() - now.getTime()
    return Math.max(0, Math.floor(diffMs / (1000 * 60))) // 분 단위
  } catch (error) {
    console.error('토큰 시간 계산 오류:', error)
    return 0
  }
}