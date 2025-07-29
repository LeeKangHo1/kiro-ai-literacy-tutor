<!-- frontend/src/components/QuizComponent.vue -->
<!-- 퀴즈 컴포넌트 -->

<template>
  <div class="quiz-component">
    <div class="card">
      <div class="card-body">
        <!-- 퀴즈 제목 -->
        <h6 class="card-title mb-3">
          <i class="bi bi-question-circle me-2"></i>
          {{ quizData.title || '문제' }}
        </h6>

        <!-- 퀴즈 질문 -->
        <div class="quiz-question mb-4">
          {{ quizData.question }}
        </div>

        <!-- 객관식 문제 -->
        <div v-if="quizData.type === 'multiple_choice'" class="quiz-options">
          <div
            v-for="(option, index) in quizData.options"
            :key="index"
            class="form-check mb-2"
          >
            <input
              :id="`option-${index}`"
              v-model="selectedAnswer"
              class="form-check-input"
              type="radio"
              :value="typeof option === 'string' ? option : option.value"
              :disabled="isSubmitted"
            />
            <label :for="`option-${index}`" class="form-check-label">
              {{ typeof option === 'string' ? option : option.text }}
            </label>
          </div>
        </div>

        <!-- 주관식/프롬프트 작성 문제 -->
        <div v-else-if="quizData.type === 'text_input'" class="quiz-input">
          <textarea
            v-model="textAnswer"
            class="form-control"
            rows="4"
            :placeholder="quizData.placeholder || '답변을 입력하세요...'"
            :disabled="isSubmitted"
          ></textarea>
          <div class="form-text">
            {{ textAnswer.length }}/{{ maxLength }} 글자
          </div>
        </div>

        <!-- 프롬프트 실습 문제 -->
        <div v-else-if="quizData.type === 'prompt_practice'" class="prompt-practice">
          <div class="mb-3">
            <label class="form-label fw-bold">프롬프트 작성:</label>
            <textarea
              v-model="promptAnswer"
              class="form-control"
              rows="3"
              placeholder="ChatGPT에게 보낼 프롬프트를 작성하세요..."
              :disabled="isSubmitted"
            ></textarea>
          </div>
          
          <!-- 실행 결과 표시 -->
          <div v-if="promptResult" class="prompt-result mt-3">
            <div class="card bg-light">
              <div class="card-header">
                <small class="text-muted">ChatGPT 응답:</small>
              </div>
              <div class="card-body">
                <p class="card-text">{{ promptResult }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 힌트 표시 -->
        <div v-if="showHint && quizData.hint" class="alert alert-info mt-3">
          <i class="bi bi-lightbulb me-2"></i>
          <strong>힌트:</strong> {{ quizData.hint }}
        </div>

        <!-- 버튼 영역 -->
        <div class="quiz-actions mt-4">
          <div class="d-flex gap-2 flex-wrap">
            <!-- 힌트 버튼 -->
            <button
              v-if="quizData.hint && !showHint && !isSubmitted"
              class="btn btn-outline-info btn-sm"
              @click="toggleHint"
            >
              <i class="bi bi-lightbulb"></i>
              힌트 보기
            </button>

            <!-- 프롬프트 테스트 버튼 -->
            <button
              v-if="quizData.type === 'prompt_practice' && promptAnswer.trim() && !isSubmitted"
              class="btn btn-outline-secondary btn-sm"
              @click="testPrompt"
              :disabled="isTestingPrompt"
            >
              <i v-if="isTestingPrompt" class="bi bi-arrow-clockwise spin"></i>
              <i v-else class="bi bi-play"></i>
              {{ isTestingPrompt ? '테스트 중...' : '프롬프트 테스트' }}
            </button>

            <!-- 답변 제출 버튼 -->
            <button
              class="btn btn-primary btn-sm"
              @click="submitAnswer"
              :disabled="!canSubmit || isSubmitted"
            >
              <i class="bi bi-check-lg"></i>
              {{ isSubmitted ? '제출 완료' : '답변 제출' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Props 정의
interface QuizData {
  type: 'multiple_choice' | 'text_input' | 'prompt_practice'
  title?: string
  question: string
  options?: Array<{ text: string; value: string } | string>
  placeholder?: string
  hint?: string
}

const props = defineProps<{
  quizData: QuizData
}>()

// Emits 정의
const emit = defineEmits<{
  answerSubmitted: [answer: any]
}>()

// 반응형 데이터
const selectedAnswer = ref('')
const textAnswer = ref('')
const promptAnswer = ref('')
const promptResult = ref('')
const showHint = ref(false)
const isSubmitted = ref(false)
const isTestingPrompt = ref(false)
const maxLength = 500

// 계산된 속성
const canSubmit = computed(() => {
  switch (props.quizData.type) {
    case 'multiple_choice':
      return selectedAnswer.value !== ''
    case 'text_input':
      return textAnswer.value.trim() !== ''
    case 'prompt_practice':
      return promptAnswer.value.trim() !== ''
    default:
      return false
  }
})

// 힌트 토글
const toggleHint = () => {
  showHint.value = !showHint.value
}

// 프롬프트 테스트 (실제로는 백엔드 API 호출)
const testPrompt = async () => {
  if (!promptAnswer.value.trim()) return
  
  isTestingPrompt.value = true
  
  try {
    // 실제 구현에서는 백엔드 API 호출
    // const response = await apiClient.post('/learning/test-prompt', { prompt: promptAnswer.value })
    
    // 임시 응답 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 실제 ChatGPT API 응답을 시뮬레이션
    const sampleResponses = [
      "안녕하세요! 도움이 필요하시면 언제든 말씀해 주세요.",
      "네, 이해했습니다. 더 구체적인 질문이 있으시면 알려주세요.",
      "좋은 질문이네요! 이에 대해 자세히 설명드리겠습니다.",
      "물론입니다. 이 주제에 대해 더 자세히 알아보겠습니다."
    ]
    
    promptResult.value = sampleResponses[Math.floor(Math.random() * sampleResponses.length)]
  } catch (error) {
    console.error('프롬프트 테스트 오류:', error)
    promptResult.value = "프롬프트 테스트 중 오류가 발생했습니다. 다시 시도해 주세요."
  } finally {
    isTestingPrompt.value = false
  }
}

// 답변 제출
const submitAnswer = () => {
  if (!canSubmit.value || isSubmitted.value) return
  
  let answer: any
  
  switch (props.quizData.type) {
    case 'multiple_choice':
      answer = {
        type: 'multiple_choice',
        selected: selectedAnswer.value,
        used_hint: showHint.value
      }
      break
    case 'text_input':
      answer = {
        type: 'text_input',
        text: textAnswer.value,
        used_hint: showHint.value
      }
      break
    case 'prompt_practice':
      answer = {
        type: 'prompt_practice',
        prompt: promptAnswer.value,
        result: promptResult.value,
        used_hint: showHint.value
      }
      break
  }
  
  isSubmitted.value = true
  emit('answerSubmitted', answer)
}
</script>

<style scoped>
.quiz-component {
  max-width: 100%;
}

.card {
  border: 1px solid #dee2e6;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.quiz-question {
  font-size: 1.1rem;
  line-height: 1.5;
  color: #333;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.form-check-input:checked {
  background-color: #007bff;
  border-color: #007bff;
}

.form-check-label {
  cursor: pointer;
  line-height: 1.4;
}

.prompt-result .card {
  border: none;
  background-color: #f8f9fa;
}

.prompt-result .card-header {
  background-color: transparent;
  border-bottom: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
}

.quiz-actions {
  border-top: 1px solid #f0f0f0;
  padding-top: 1rem;
}

.btn-sm {
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 반응형 디자인 */
@media (max-width: 576px) {
  .quiz-actions .d-flex {
    flex-direction: column;
  }
  
  .quiz-actions .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
</style>