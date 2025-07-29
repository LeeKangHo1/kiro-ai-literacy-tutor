<!-- frontend/src/components/TokenExpiryNotification.vue -->
<!-- 토큰 만료 알림 컴포넌트 -->

<template>
  <div
    v-if="showNotification"
    class="token-expiry-notification position-fixed top-0 end-0 m-3"
    style="z-index: 1050;"
  >
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>세션 만료 알림</strong>
      <br>
      <span v-if="timeRemaining > 1">
        {{ timeRemaining }}분 후 자동 로그아웃됩니다.
      </span>
      <span v-else>
        곧 자동 로그아웃됩니다.
      </span>
      
      <div class="mt-2">
        <button
          type="button"
          class="btn btn-sm btn-outline-warning me-2"
          @click="extendSession"
          :disabled="isExtending"
        >
          <span
            v-if="isExtending"
            class="spinner-border spinner-border-sm me-1"
            role="status"
            aria-hidden="true"
          ></span>
          세션 연장
        </button>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          @click="dismissNotification"
        >
          닫기
        </button>
      </div>
      
      <button
        type="button"
        class="btn-close"
        @click="dismissNotification"
        aria-label="Close"
      ></button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'

// 스토어
const authStore = useAuthStore()

// 상태
const showNotification = ref(false)
const isDismissed = ref(false)
const isExtending = ref(false)
let intervalId: number | null = null

// 계산된 속성
const timeRemaining = computed(() => authStore.tokenTimeRemaining)

// 알림 표시 조건 (5분 이하일 때)
const shouldShowNotification = computed(() => {
  return authStore.isAuthenticated && 
         timeRemaining.value <= 5 && 
         timeRemaining.value > 0 && 
         !isDismissed.value
})

// 세션 연장
const extendSession = async () => {
  isExtending.value = true
  
  try {
    const success = await authStore.validateToken()
    if (success) {
      // 토큰이 유효하면 새로운 만료 시간 설정
      const expiryTime = new Date()
      expiryTime.setHours(expiryTime.getHours() + 24)
      localStorage.setItem('token_expiry', expiryTime.toISOString())
      
      showNotification.value = false
      isDismissed.value = false
    }
  } catch (error) {
    console.error('세션 연장 실패:', error)
  } finally {
    isExtending.value = false
  }
}

// 알림 닫기
const dismissNotification = () => {
  showNotification.value = false
  isDismissed.value = true
  
  // 1분 후 다시 알림 표시 가능하도록 설정
  setTimeout(() => {
    isDismissed.value = false
  }, 60000)
}

// 알림 상태 업데이트
const updateNotificationState = () => {
  if (shouldShowNotification.value) {
    showNotification.value = true
  } else if (timeRemaining.value <= 0) {
    showNotification.value = false
    isDismissed.value = false
  }
}

// 컴포넌트 마운트
onMounted(() => {
  // 30초마다 토큰 상태 확인
  intervalId = window.setInterval(updateNotificationState, 30000)
  updateNotificationState()
})

// 컴포넌트 언마운트
onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>

<style scoped>
.token-expiry-notification {
  max-width: 350px;
}

.alert-warning {
  border-left: 4px solid #ffc107;
}

.btn-outline-warning:hover {
  color: #000;
  background-color: #ffc107;
  border-color: #ffc107;
}

.btn-outline-secondary:hover {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}
</style>