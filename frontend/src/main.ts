// frontend/src/main.ts
// Vue 3 애플리케이션 진입점

// 스타일 임포트
import '@/styles/main.scss'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/authStore'

const app = createApp(App)

// Pinia 설정
app.use(createPinia())

// 인증 상태 초기화
const authStore = useAuthStore()
authStore.initializeAuth()

// 라우터 설정
app.use(router)

app.mount('#app')
