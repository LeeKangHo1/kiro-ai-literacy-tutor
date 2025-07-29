<!-- frontend/src/views/LoginView.vue -->
<!-- 로그인 페이지 -->

<template>
  <div class="login-container">
    <div class="container-fluid h-100">
      <div class="row h-100 justify-content-center align-items-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow">
            <div class="card-body p-4">
              <!-- 로고 및 제목 -->
              <div class="text-center mb-4">
                <h2 class="card-title mb-2">AI 문해력 네비게이터</h2>
                <p class="text-muted">AI 학습 튜터에 오신 것을 환영합니다</p>
              </div>

              <!-- 로그인 폼 -->
              <form @submit.prevent="handleLogin">
                <!-- 사용자명 입력 -->
                <div class="mb-3">
                  <label for="username" class="form-label">사용자명</label>
                  <input
                    id="username"
                    v-model="loginForm.username"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.username }"
                    placeholder="사용자명을 입력하세요"
                    required
                  />
                  <div v-if="errors.username" class="invalid-feedback">
                    {{ errors.username }}
                  </div>
                </div>

                <!-- 비밀번호 입력 -->
                <div class="mb-3">
                  <label for="password" class="form-label">비밀번호</label>
                  <input
                    id="password"
                    v-model="loginForm.password"
                    type="password"
                    class="form-control"
                    :class="{ 'is-invalid': errors.password }"
                    placeholder="비밀번호를 입력하세요"
                    required
                  />
                  <div v-if="errors.password" class="invalid-feedback">
                    {{ errors.password }}
                  </div>
                </div>

                <!-- 에러 메시지 -->
                <div v-if="authStore.error" class="alert alert-danger" role="alert">
                  {{ authStore.error }}
                </div>

                <!-- 로그인 버튼 -->
                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  :disabled="authStore.isLoading"
                >
                  <span
                    v-if="authStore.isLoading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ authStore.isLoading ? '로그인 중...' : '로그인' }}
                </button>
              </form>

              <!-- 회원가입 링크 -->
              <div class="text-center mt-3">
                <p class="mb-0">
                  계정이 없으신가요?
                  <router-link to="/register" class="text-decoration-none">회원가입</router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { validateLoginForm, type LoginFormData } from '@/utils/authValidation'

// 라우터 및 스토어
const router = useRouter()
const authStore = useAuthStore()

// 폼 데이터
const loginForm = reactive<LoginFormData>({
  username: '',
  password: ''
})

// 폼 검증 에러
const errors = ref<{ username?: string; password?: string }>({})

// 폼 검증
const validateForm = (): boolean => {
  const validation = validateLoginForm(loginForm)
  
  if (!validation.isValid) {
    // 에러 메시지를 필드별로 분류
    errors.value = {}
    validation.errors.forEach(error => {
      if (error.includes('사용자명')) {
        errors.value.username = error
      } else if (error.includes('비밀번호')) {
        errors.value.password = error
      }
    })
    return false
  }
  
  errors.value = {}
  return true
}

// 로그인 처리
const handleLogin = async () => {
  if (!validateForm()) {
    return
  }
  
  authStore.clearError()
  
  try {
    const success = await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password
    })
    
    if (success) {
      // 로그인 성공 시 원래 가려던 페이지 또는 학습 페이지로 이동
      const redirectPath = (router.currentRoute.value.query.redirect as string) || '/learning'
      await router.push(redirectPath)
    }
  } catch (error) {
    console.error('로그인 처리 중 오류:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
  border: none;
  border-radius: 10px;
}

.card-title {
  color: #333;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-weight: 500;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.form-control {
  border-radius: 8px;
  border: 1px solid #ddd;
  padding: 12px;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}
</style>