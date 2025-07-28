<!-- frontend/src/components/ChatInterface.vue -->
<!-- 통합 채팅/퀴즈 인터페이스 -->

<template>
  <div class="chat-interface">
    <!-- 메시지 표시 영역 -->
    <div ref="messagesContainer" class="messages-container">
      <div class="messages-content p-3">
        <!-- 메시지가 없을 때 -->
        <div v-if="learningStore.messages.length === 0" class="empty-state text-center py-5">
          <div class="empty-icon mb-3">
            <i class="bi bi-chat-dots" style="font-size: 3rem; color: #6c757d;"></i>
          </div>
          <h5 class="text-muted">학습을 시작해보세요!</h5>
          <p class="text-muted">
            질문을 하거나 "시작"이라고 입력하여 학습을 시작할 수 있습니다.
          </p>
        </div>

        <!-- 메시지 목록 -->
        <div
          v-for="message in learningStore.messages"
          :key="message.id"
          class="message-wrapper"
          :class="message.type"
        >
          <div class="message-bubble">
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>

          <!-- UI 요소 (퀴즈, 버튼 등) -->
          <div v-if="message.ui_elements" class="ui-elements mt-3">
            <QuizComponent
              v-if="message.ui_elements.type === 'quiz'"
              :quiz-data="message.ui_elements.data"
              @answer-submitted="handleQuizAnswer"
            />
            <ButtonGroup
              v-else-if="message.ui_elements.type === 'buttons'"
              :buttons="message.ui_elements.data"
              @button-clicked="handleButtonClick"
            />
          </div>
        </div>

        <!-- 로딩 인디케이터 -->
        <div v-if="learningStore.isLoading" class="message-wrapper system">
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 입력 영역 -->
    <div class="input-area">
      <div class="input-container p-3">
        <!-- 에러 메시지 -->
        <div v-if="learningStore.error" class="alert alert-danger alert-sm mb-2" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ learningStore.error }}
          <button
            type="button"
            class="btn-close btn-close-sm"
            @click="learningStore.clearError"
          ></button>
        </div>

        <!-- 입력 폼 -->
        <form @submit.prevent="sendMessage" class="input-form">
          <div class="input-group">
            <input
              v-model="messageInput"
              type="text"
              class="form-control"
              placeholder="메시지를 입력하세요..."
              :disabled="learningStore.isLoading"
              maxlength="500"
            />
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!messageInput.trim() || learningStore.isLoading"
            >
              <i v-if="learningStore.isLoading" class="bi bi-arrow-clockwise spin"></i>
              <i v-else class="bi bi-send"></i>
            </button>
          </div>
        </form>

        <!-- 입력 도움말 -->
        <div class="input-help mt-2">
          <small class="text-muted">
            <i class="bi bi-info-circle me-1"></i>
            팁: "문제 내줘", "힌트", "다음 단계" 등으로 학습을 진행할 수 있습니다.
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useLearningStore } from '@/stores/learningStore'
import QuizComponent from './QuizComponent.vue'
import ButtonGroup from './ButtonGroup.vue'

// 스토어
const learningStore = useLearningStore()

// 반응형 데이터
const messageInput = ref('')
const messagesContainer = ref<HTMLElement>()

// 메시지 전송
const sendMessage = async () => {
  const content = messageInput.value.trim()
  if (!content) return

  const success = await learningStore.sendMessage(content)
  if (success) {
    messageInput.value = ''
    scrollToBottom()
  }
}

// 퀴즈 답변 처리
const handleQuizAnswer = async (answer: any) => {
  const answerText = typeof answer === 'string' ? answer : JSON.stringify(answer)
  await learningStore.sendMessage(`답변: ${answerText}`)
  scrollToBottom()
}

// 버튼 클릭 처리
const handleButtonClick = async (buttonData: any) => {
  await learningStore.sendMessage(buttonData.text || buttonData.value)
  scrollToBottom()
}

// 시간 포맷팅
const formatTime = (timestamp: Date): string => {
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp)
}

// 스크롤을 맨 아래로
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 메시지 변경 감지하여 자동 스크롤
watch(
  () => learningStore.messages.length,
  () => {
    scrollToBottom()
  }
)
</script>

<style scoped>
.chat-interface {
  height: calc(100vh - 80px); /* 헤더 높이 제외 */
  display: flex;
  flex-direction: column;
  background-color: white;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  background-color: #f8f9fa;
}

.messages-content {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.message-wrapper {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.message-wrapper.user {
  align-items: flex-end;
}

.message-wrapper.system {
  align-items: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
}

.message-wrapper.user .message-bubble {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-wrapper.system .message-bubble {
  background-color: white;
  color: #333;
  border: 1px solid #dee2e6;
  border-bottom-left-radius: 4px;
}

.message-content {
  line-height: 1.4;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.ui-elements {
  max-width: 70%;
}

.message-wrapper.system .ui-elements {
  align-self: flex-start;
}

/* 타이핑 인디케이터 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6c757d;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 입력 영역 */
.input-area {
  background-color: white;
  border-top: 1px solid #dee2e6;
  flex-shrink: 0;
}

.input-form {
  margin: 0;
}

.input-group .form-control {
  border-right: none;
  border-radius: 25px 0 0 25px;
  padding: 0.75rem 1rem;
}

.input-group .btn {
  border-radius: 0 25px 25px 0;
  padding: 0.75rem 1rem;
  min-width: 50px;
}

.input-help {
  font-size: 0.8rem;
}

.alert-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.btn-close-sm {
  font-size: 0.75rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .chat-interface {
    height: calc(100vh - 60px);
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .ui-elements {
    max-width: 85%;
  }
  
  .input-container {
    padding: 1rem !important;
  }
}
</style>