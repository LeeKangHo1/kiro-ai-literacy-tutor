<!-- frontend/src/components/ButtonGroup.vue -->
<!-- 버튼 그룹 컴포넌트 -->

<template>
  <div class="button-group">
    <div class="d-flex flex-wrap gap-2">
      <button
        v-for="(button, index) in buttons"
        :key="index"
        class="btn"
        :class="getButtonClass(button)"
        :disabled="button.disabled"
        @click="handleButtonClick(button)"
      >
        <i v-if="button.icon" :class="button.icon" class="me-2"></i>
        {{ button.text }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props 정의
interface Button {
  text: string
  value?: string
  type?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark'
  size?: 'sm' | 'lg'
  icon?: string
  disabled?: boolean
}

const props = defineProps<{
  buttons: Button[]
}>()

// Emits 정의
const emit = defineEmits<{
  buttonClicked: [button: Button]
}>()

// 버튼 클래스 계산
const getButtonClass = (button: Button): string => {
  const type = button.type || 'outline-primary'
  const size = button.size ? `btn-${button.size}` : ''
  
  return `btn-${type} ${size}`.trim()
}

// 버튼 클릭 처리
const handleButtonClick = (button: Button) => {
  if (button.disabled) return
  emit('buttonClicked', button)
}
</script>

<style scoped>
.button-group {
  margin: 0.5rem 0;
}

.btn {
  transition: all 0.2s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 반응형 디자인 */
@media (max-width: 576px) {
  .button-group .d-flex {
    flex-direction: column;
  }
  
  .button-group .btn {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
</style>