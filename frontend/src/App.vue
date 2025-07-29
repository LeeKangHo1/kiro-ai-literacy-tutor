<!-- frontend/src/App.vue -->
<!-- 메인 애플리케이션 컴포넌트 -->

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import TokenExpiryNotification from '@/components/TokenExpiryNotification.vue'

// 스토어
const authStore = useAuthStore()

// 앱 초기화
onMounted(() => {
  // 저장된 인증 정보 복원
  authStore.initializeAuth()
})
</script>

<template>
  <div id="app">
    <RouterView />
    <!-- 토큰 만료 알림 -->
    <TokenExpiryNotification />
  </div>
</template>

<style>
/* 전역 스타일 리셋 */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* Bootstrap Icons 지원 */
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css');
</style>
