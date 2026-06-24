/**
 * 事件埋点追踪系统
 * 支持20种核心事件 + 异常上报
 * 开发环境console.log + 生产环境批量上报
 */

import { api } from '@/api/request'

// 核心事件类型
export type TrackEvent =
  | 'page_view_landing'
  | 'page_view_quiz'
  | 'page_view_loading'
  | 'page_view_result'
  | 'click_start_test'
  | 'quiz_answer'
  | 'quiz_prev'
  | 'quiz_next'
  | 'quiz_skip'
  | 'quiz_submit'
  | 'result_view'
  | 'result_generate_poster'
  | 'result_save_poster'
  | 'result_share'
  | 'result_unlock_report'
  | 'audio_toggle'
  | 'app_error'
  | 'api_error'
  | 'quiz_timeout'
  | 'quiz_resume'

interface TrackData {
  event: TrackEvent
  timestamp: number
  userId?: string
  properties?: Record<string, any>
}

// 事件缓冲区（批量上报）
let eventBuffer: TrackData[] = []
const BUFFER_SIZE = 10
const FLUSH_INTERVAL = 30000 // 30秒

let flushTimer: ReturnType<typeof setInterval> | null = null

/** 初始化埋点系统 */
export function useEventTracker() {
  // 获取用户ID
  function getUserId(): string {
    try {
      const userInfo = uni.getStorageSync('user_info')
      if (userInfo) {
        const info = JSON.parse(userInfo)
        return info.id || info.openid || 'anonymous'
      }
    } catch (e) { /* ignore */ }
    return 'anonymous'
  }

  /** 记录事件 */
  function track(event: TrackEvent, properties?: Record<string, any>) {
    const data: TrackData = {
      event,
      timestamp: Date.now(),
      userId: getUserId(),
      properties,
    }

    // 开发环境打印日志
    const isDev = import.meta.env.DEV
    if (isDev) {
      console.log(`[Track] ${event}`, properties || '')
    }

    eventBuffer.push(data)

    // 缓冲区满则立即上报
    if (eventBuffer.length >= BUFFER_SIZE) {
      flush()
    }
  }

  /** 上报事件缓冲 */
  async function flush() {
    if (eventBuffer.length === 0) return

    const events = [...eventBuffer]
    eventBuffer = []

    try {
      // 埋点上报使用 silent 模式，失败时静默不弹 toast
      await api.post('/events/batch', { events }, false)
    } catch (e) {
      // 上报失败，放回缓冲区
      eventBuffer.unshift(...events)
      // 限制缓冲区大小防止内存泄漏
      if (eventBuffer.length > 100) {
        eventBuffer = eventBuffer.slice(-50)
      }
    }
  }

  /** 启动定时上报 */
  function startAutoFlush() {
    if (flushTimer) return
    flushTimer = setInterval(flush, FLUSH_INTERVAL)
  }

  /** 停止定时上报 */
  function stopAutoFlush() {
    if (flushTimer) {
      clearInterval(flushTimer)
      flushTimer = null
    }
  }

  /** 记录页面访问 */
  function trackPageView(page: 'landing' | 'quiz' | 'loading' | 'result') {
    track(`page_view_${page}` as TrackEvent)
  }

  /** 记录答题行为 */
  function trackQuizAnswer(questionIndex: number, score: number) {
    track('quiz_answer', { questionIndex, score })
  }

  /** 记录答题导航 */
  function trackQuizNav(direction: 'prev' | 'next' | 'skip') {
    track(`quiz_${direction}` as TrackEvent)
  }

  /** 记录异常 */
  function trackError(errorType: 'app_error' | 'api_error' | 'quiz_timeout', detail?: string) {
    track(errorType, { detail, timestamp: new Date().toISOString() })
  }

  return {
    track,
    flush,
    startAutoFlush,
    stopAutoFlush,
    trackPageView,
    trackQuizAnswer,
    trackQuizNav,
    trackError,
  }
}
