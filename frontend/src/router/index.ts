// frontend/src/router/index.ts
// Vue Router 설정

import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import LearningView from '@/views/LearningView.vue'

// 라우트 메타 타입 확장
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresGuest?: boolean
    title?: string
  }
}

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
      meta: { 
        requiresGuest: true,
        title: '로그인 - AI 문해력 네비게이터'
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { 
        requiresGuest: true,
        title: '회원가입 - AI 문해력 네비게이터'
      }
    },
    {
      path: '/learning',
      name: 'learning',
      component: LearningView,
      meta: { 
        requiresAuth: true,
        title: '학습 - AI 문해력 네비게이터'
      }
    },
    // 404 페이지
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      redirect: '/learning'
    }
  ],
})

// 라우터 가드 설정
router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next) => {
  const authStore = useAuthStore()
  
  // 앱 시작 시 인증 상태 초기화 (한 번만 실행)
  if (!authStore.token && !authStore.user) {
    authStore.initializeAuth()
  }
  
  // 페이지 제목 설정
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 인증이 필요한 페이지
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      console.log('인증이 필요한 페이지 접근 시도, 로그인 페이지로 리다이렉트')
      // 원래 가려던 페이지를 쿼리 파라미터로 저장
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 토큰 만료 시간 확인
    const tokenExpiry = localStorage.getItem('token_expiry')
    if (tokenExpiry) {
      const expiryTime = new Date(tokenExpiry)
      const now = new Date()
      
      // 토큰이 5분 이내에 만료될 예정이면 경고
      const fiveMinutesFromNow = new Date(now.getTime() + 5 * 60 * 1000)
      if (expiryTime <= fiveMinutesFromNow) {
        console.warn('토큰이 곧 만료됩니다.')
      }
      
      // 토큰이 이미 만료된 경우
      if (now >= expiryTime) {
        console.log('토큰이 만료되어 로그아웃 처리')
        authStore.logout()
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  }
  
  // 게스트만 접근 가능한 페이지 (로그인 페이지)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('이미 로그인된 사용자, 학습 페이지로 리다이렉트')
    // 리다이렉트 쿼리가 있으면 해당 페이지로, 없으면 기본 학습 페이지로
    const redirectPath = (to.query.redirect as string) || '/learning'
    next(redirectPath)
    return
  }
  
  next()
})

// 라우터 에러 처리
router.onError((error) => {
  console.error('라우터 오류:', error)
})

export default router
