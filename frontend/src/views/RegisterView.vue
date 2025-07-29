<!-- frontend/src/views/RegisterView.vue -->
<!-- 회원가입 페이지 -->

<template>
  <div class="register-container">
    <div class="container-fluid h-100">
      <div class="row h-100 justify-content-center align-items-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-body p-4">
              <!-- 로고 및 제목 -->
              <div class="text-center mb-4">
                <h2 class="card-title mb-2">회원가입</h2>
                <p class="text-muted">AI 학습 튜터에 가입하여 시작하세요</p>
              </div>

              <!-- 회원가입 폼 -->
              <form @submit.prevent="handleRegister">
                <!-- 사용자명 입력 -->
                <div class="mb-3">
                  <label for="username" class="form-label">사용자명</label>
                  <input
                    id="username"
                    v-model="registerForm.username"
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

                <!-- 이메일 입력 -->
                <div class="mb-3">
                  <label for="email" class="form-label">이메일</label>
                  <input
                    id="email"
                    v-model="registerForm.email"
                    type="email"
                    class="form-control"
                    :class="{ 'is-invalid': errors.email }"
                    placeholder="이메일을 입력하세요"
                    required
                  />
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <!-- 비밀번호 입력 -->
                <div class="mb-3">
                  <label for="password" class="form-label">비밀번호</label>
                  <input
                    id="password"
                    v-model="registerForm.password"
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

                <!-- 비밀번호 확인 -->
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">비밀번호 확인</label>
                  <input
                    id="confirmPassword"
                    v-model="confirmPassword"
                    type="password"
                    class="form-control"
                    :class="{ 'is-invalid': errors.confirmPassword }"
                    placeholder="비밀번호를 다시 입력하세요"
                    required
                  />
                  <div v-if="errors.confirmPassword" class="invalid-feedback">
                    {{ errors.confirmPassword }}
                  </div>
                </div>

                <!-- 사용자 유형 선택 -->
                <div class="mb-3">
                  <label class="form-label">사용자 유형</label>
                  <div class="row">
                    <div class="col-6">
                      <div class="form-check">
                        <input
                          id="beginner"
                          v-model="registerForm.user_type"
                          class="form-check-input"
                          type="radio"
                          value="beginner"
                        />
                        <label class="form-check-label" for="beginner">
                          <strong>AI 입문자</strong><br>
                          <small class="text-muted">AI를 처음 배우는 분</small>
                        </label>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="form-check">
                        <input
                          id="business"
                          v-model="registerForm.user_type"
                          class="form-check-input"
                          type="radio"
                          value="business"
                        />
                        <label class="form-check-label" for="business">
                          <strong>실무 응용형</strong><br>
                          <small class="text-muted">업무에 AI를 활용하고 싶은 분</small>
                        </label>
                      </div>
                    </div>
                  </div>
                  <div v-if="errors.user_type" class="text-danger small mt-1">
                    {{ errors.user_type }}
                  </div>
                </div>

                <!-- 에러 메시지 -->
                <div v-if="authStore.error" class="alert alert-danger" role="alert">
                  {{ authStore.error }}
                </div>

                <!-- 회원가입 버튼 -->
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
                  {{ authStore.isLoading ? '가입 중...' : '회원가입' }}
                </button>
              </form>

              <!-- 로그인 링크 -->
              <div class="text-center mt-3">
                <p class="mb-0">
                  이미 계정이 있으신가요?
                  <router-link to="/login" class="text-decoration-none">로그인</router-link>
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
import type { RegisterRequest } from '@/services/apiClient'

// 라우터 및 스토어
const router = useRouter()
const authStore = useAuthStore()

// 폼 데이터
const registerForm = reactive<RegisterRequest>({
  username: '',
  email: '',
  password: '',
  user_type: 'beginner'
})

const confirmPassword = ref('')

// 폼 검증 에러
const errors = ref<{
  username?: string
  email?: string
  password?: string
  confirmPassword?: string
  user_type?: string
}>({})

// 폼 검증
const validateForm = (): boolean => {
  errors.value = {}
  
  if (!registerForm.username.trim()) {
    errors.value.username = '사용자명을 입력해주세요.'
  } else if (registerForm.username.length < 3) {
    errors.value.username = '사용자명은 3자 이상이어야 합니다.'
  }
  
  if (!registerForm.email.trim()) {
    errors.value.email = '이메일을 입력해주세요.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
    errors.value.email = '올바른 이메일 형식을 입력해주세요.'
  }
  
  if (!registerForm.password.trim()) {
    errors.value.password = '비밀번호를 입력해주세요.'
  } else if (registerForm.password.length < 6) {
    errors.value.password = '비밀번호는 6자 이상이어야 합니다.'
  }
  
  if (!confirmPassword.value.trim()) {
    errors.value.confirmPassword = '비밀번호 확인을 입력해주세요.'
  } else if (registerForm.password !== confirmPassword.value) {
    errors.value.confirmPassword = '비밀번호가 일치하지 않습니다.'
  }
  
  if (!registerForm.user_type) {
    errors.value.user_type = '사용자 유형을 선택해주세요.'
  }
  
  return Object.keys(errors.value).length === 0
}

// 회원가입 처리
const handleRegister = async () => {
  if (!validateForm()) {
    return
  }
  
  authStore.clearError()
  
  try {
    const success = await authStore.register({
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password,
      user_type: registerForm.user_type
    })
    
    if (success) {
      // 회원가입 성공 시 학습 페이지로 이동
      await router.push('/learning')
    }
  } catch (error) {
    console.error('회원가입 처리 중 오류:', error)
  }
}
</script>

<style scoped>
.register-container {
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

.form-check-input:checked {
  background-color: #667eea;
  border-color: #667eea;
}

.form-check-label {
  cursor: pointer;
}
</style>