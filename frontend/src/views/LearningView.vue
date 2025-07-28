<!-- frontend/src/views/LearningView.vue -->
<!-- 메인 학습 페이지 -->

<template>
  <div class="learning-container">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <!-- 사이드바 (선택사항) -->
        <div class="col-md-3 col-lg-2 sidebar d-none d-md-block">
          <div class="sidebar-content p-3">
            <h5 class="mb-3">학습 진도</h5>
            <div class="chapter-list">
              <div
                v-for="chapter in chapters"
                :key="chapter.id"
                class="chapter-item"
                :class="{ active: chapter.id === learningStore.currentChapter }"
                @click="selectChapter(chapter.id)"
              >
                <span class="chapter-number">{{ chapter.id }}</span>
                <span class="chapter-title">{{ chapter.title }}</span>
              </div>
            </div>
            
            <!-- 사용자 정보 -->
            <div class="user-info mt-4 pt-3 border-top">
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-person-circle me-2"></i>
                <span class="fw-bold">{{ authStore.user?.username }}</span>
              </div>
              <div class="user-type">
                <span class="badge bg-secondary">
                  {{ authStore.userType === 'beginner' ? 'AI 입문자' : '실무 응용형' }}
                </span>
              </div>
              <button class="btn btn-outline-danger btn-sm mt-2 w-100" @click="handleLogout">
                로그아웃
              </button>
            </div>
          </div>
        </div>

        <!-- 메인 학습 영역 -->
        <div class="col-md-9 col-lg-10 main-content">
          <div class="learning-header p-3 border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h4 class="mb-0">
                챕터 {{ learningStore.currentChapter }}: {{ getCurrentChapterTitle() }}
              </h4>
              <div class="learning-controls">
                <button
                  class="btn btn-outline-primary btn-sm me-2"
                  @click="clearChat"
                >
                  대화 초기화
                </button>
                <span class="badge bg-info">
                  {{ learningStore.uiMode === 'chat' ? '자유 대화' : '퀴즈 모드' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 채팅/퀴즈 통합 인터페이스 -->
          <ChatInterface />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useLearningStore } from '@/stores/learningStore'
import ChatInterface from '@/components/ChatInterface.vue'

// 라우터 및 스토어
const router = useRouter()
const authStore = useAuthStore()
const learningStore = useLearningStore()

// 챕터 목록 (임시 데이터)
const chapters = ref([
  { id: 1, title: 'AI는 무엇인가?' },
  { id: 2, title: 'LLM이란 무엇인가?' },
  { id: 3, title: '프롬프트란 무엇인가?' },
  { id: 4, title: 'ChatGPT로 할 수 있는 것들' },
  { id: 5, title: 'AI 시대의 문해력' }
])

// 현재 챕터 제목 가져오기
const getCurrentChapterTitle = (): string => {
  const chapter = chapters.value.find(c => c.id === learningStore.currentChapter)
  return chapter?.title || '알 수 없는 챕터'
}

// 챕터 선택
const selectChapter = (chapterId: number) => {
  learningStore.setCurrentChapter(chapterId)
  learningStore.clearMessages()
}

// 대화 초기화
const clearChat = () => {
  learningStore.clearMessages()
}

// 로그아웃 처리
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 컴포넌트 마운트 시 초기화
onMounted(() => {
  // 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // 학습 세션 초기화
  learningStore.initializeLearningSession()
})
</script>

<style scoped>
.learning-container {
  height: 100vh;
  background-color: #f8f9fa;
}

.sidebar {
  background-color: white;
  border-right: 1px solid #dee2e6;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-content {
  position: sticky;
  top: 0;
}

.chapter-list {
  max-height: 400px;
  overflow-y: auto;
}

.chapter-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.chapter-item:hover {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.chapter-item.active {
  background-color: #e3f2fd;
  border-color: #2196f3;
  color: #1976d2;
}

.chapter-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #6c757d;
  color: white;
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 600;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.chapter-item.active .chapter-number {
  background-color: #2196f3;
}

.chapter-title {
  font-size: 0.9rem;
  line-height: 1.4;
}

.main-content {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.learning-header {
  background-color: white;
  flex-shrink: 0;
}

.user-info {
  font-size: 0.875rem;
}

.user-type .badge {
  font-size: 0.75rem;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .learning-container {
    height: 100vh;
  }
  
  .main-content {
    padding: 0;
  }
  
  .learning-header {
    padding: 1rem !important;
  }
  
  .learning-header h4 {
    font-size: 1.1rem;
  }
  
  .learning-controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>