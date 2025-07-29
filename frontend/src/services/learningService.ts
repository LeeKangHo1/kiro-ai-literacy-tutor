// frontend/src/services/learningService.ts
// 학습 관련 API 서비스

import apiClient, { type ChatMessage, type ChatResponse, type ApiResponse } from './apiClient'

export interface LearningProgress {
  chapters: Array<{
    chapter_id: number
    title: string
    progress: number
    completed: boolean
  }>
  overall_progress: number
  current_chapter: number
}

export interface ChapterInfo {
  id: number
  title: string
  description: string
  difficulty: 'low' | 'medium' | 'high'
  estimated_time: number
  prerequisites: number[]
  learning_objectives: string[]
}

export interface LearningStats {
  total_study_time: number
  completed_chapters: number
  quiz_accuracy: number
  streak_days: number
  last_activity: string
}

export interface QuizAnswer {
  question_id: string
  selected_option: number
  quiz_type: 'multiple_choice' | 'true_false' | 'short_answer'
}

class LearningService {
  /**
   * 채팅 메시지 전송
   */
  async sendMessage(messageData: ChatMessage, signal?: AbortSignal): Promise<ChatResponse> {
    const response = await apiClient.post<ApiResponse<ChatResponse>>(
      '/learning/chat', 
      messageData,
      { signal }
    )
    return response.data.data!
  }

  /**
   * 학습 진도 조회
   */
  async getProgress(): Promise<LearningProgress> {
    const response = await apiClient.get<ApiResponse<LearningProgress>>('/learning/progress')
    return response.data.data!
  }

  /**
   * 챕터 정보 조회
   */
  async getChapter(chapterId: number): Promise<ChapterInfo> {
    const response = await apiClient.get<ApiResponse<ChapterInfo>>(`/learning/chapter/${chapterId}`)
    return response.data.data!
  }

  /**
   * 학습 통계 조회
   */
  async getStats(): Promise<LearningStats> {
    const response = await apiClient.get<ApiResponse<LearningStats>>('/user/stats')
    return response.data.data!
  }

  /**
   * 퀴즈 답변 제출
   */
  async submitQuizAnswer(answer: QuizAnswer): Promise<ChatResponse> {
    const response = await apiClient.post<ApiResponse<ChatResponse>>('/learning/quiz/answer', answer)
    return response.data.data!
  }

  /**
   * 챕터 완료 처리
   */
  async completeChapter(chapterId: number): Promise<void> {
    await apiClient.post(`/learning/chapter/${chapterId}/complete`)
  }

  /**
   * 학습 세션 시작
   */
  async startLearningSession(chapterId: number): Promise<{ session_id: string }> {
    const response = await apiClient.post<ApiResponse<{ session_id: string }>>(
      '/learning/session/start',
      { chapter_id: chapterId }
    )
    return response.data.data!
  }

  /**
   * 학습 세션 종료
   */
  async endLearningSession(sessionId: string): Promise<void> {
    await apiClient.post('/learning/session/end', { session_id: sessionId })
  }

  /**
   * 북마크 추가/제거
   */
  async toggleBookmark(chapterId: number): Promise<{ bookmarked: boolean }> {
    const response = await apiClient.post<ApiResponse<{ bookmarked: boolean }>>(
      '/learning/bookmark/toggle',
      { chapter_id: chapterId }
    )
    return response.data.data!
  }

  /**
   * 북마크 목록 조회
   */
  async getBookmarks(): Promise<ChapterInfo[]> {
    const response = await apiClient.get<ApiResponse<ChapterInfo[]>>('/learning/bookmarks')
    return response.data.data!
  }

  /**
   * 학습 히스토리 조회
   */
  async getLearningHistory(limit: number = 10): Promise<Array<{
    id: string
    chapter_id: number
    chapter_title: string
    started_at: string
    completed_at?: string
    progress: number
  }>> {
    const response = await apiClient.get<ApiResponse<any[]>>(
      `/learning/history?limit=${limit}`
    )
    return response.data.data!
  }
}

export const learningService = new LearningService()
export default learningService