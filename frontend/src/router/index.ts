// frontend/src/router/index.ts
// Vue Router 설정

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '@/views/LoginView.vue'
import LearningView from '@/views/LearningView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/learning'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/learning',
      name: 'learning',
      component: LearningView,
      meta: { requiresAuth: true }
    },
    // 404 페이지
    {
      path: '/:pathMatch(.*)*',
      redirect: '/learning'
    }
  ],
})

// 라우터 가드 설정
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 인증이 필요한 페이지
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 게스트만 접근 가능한 페이지 (로그인 페이지)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/learning')
    return
  }
  
  next()
})

export default router
