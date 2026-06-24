/**
 * 背景音乐与氛围控制系统
 * 三段音乐: 引导段 / 答题段 / 结果段
 * 支持播放/暂停、跨页面无缝切换、偏好缓存、低帧率降级
 *
 * 实现：使用模块级单例 audioContext，所有页面共享同一个音频实例，
 *      切换 stage 时先 stop 当前曲目再 play 新曲目，避免重叠。
 */

import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settingsStore'

// 音乐资源URL
const AUDIO_SOURCES = {
  landing: {
    url: '',  // landing 阶段不播放背景音乐
    loop: true,
    label: '引导段',
  },
  quiz: {
    url: '/static/audio/quiz.mp3',
    loop: true,
    label: '答题段',
  },
  result: {
    url: '/static/audio/result.mp3',
    loop: false,
    label: '结果段',
  },
}

type AudioStage = keyof typeof AUDIO_SOURCES

// ============ 模块级单例状态 ============
let sharedAudioContext: UniApp.InnerAudioContext | null = null
let sharedFpsCheckTimer: ReturnType<typeof setInterval> | null = null
let initListenersAttached = false

// 全局响应式状态（所有页面共享）
const currentStage = ref<AudioStage | null>(null)
const isPlaying = ref(false)
const isLoaded = ref(false)

/** 初始化共享音频上下文 */
function initAudio() {
  if (sharedAudioContext) return

  sharedAudioContext = uni.createInnerAudioContext()
  sharedAudioContext.obeyMuteSwitch = false // 不受静音开关影响

  sharedAudioContext.onPlay(() => {
    isPlaying.value = true
  })

  sharedAudioContext.onPause(() => {
    isPlaying.value = false
  })

  sharedAudioContext.onStop(() => {
    isPlaying.value = false
    isLoaded.value = false
  })

  sharedAudioContext.onEnded(() => {
    isPlaying.value = false
  })

  sharedAudioContext.onError((err) => {
    console.warn('音频播放错误，静默处理:', err)
    isPlaying.value = false
  })

  sharedAudioContext.onCanplay(() => {
    isLoaded.value = true
  })

  initListenersAttached = true
}

/** 切换到指定阶段的音乐 */
function switchTo(stage: AudioStage) {
  const settingsStore = useSettingsStore()
  settingsStore.loadPreferences()

  currentStage.value = stage

  if (!settingsStore.musicEnabled) {
    // 用户关闭了音乐，停止当前播放
    if (sharedAudioContext) {
      try { sharedAudioContext.stop() } catch (e) { /* ignore */ }
    }
    return
  }

  // 如果已经在播放同一阶段，不重复操作
  if (sharedAudioContext && sharedAudioContext.src === AUDIO_SOURCES[stage].url && isPlaying.value) {
    return
  }

  const source = AUDIO_SOURCES[stage]

  // 如果该阶段没有配置音频，停止当前播放并返回（不报错）
  if (!source.url) {
    if (sharedAudioContext) {
      try { sharedAudioContext.stop() } catch (e) { /* ignore */ }
    }
    isPlaying.value = false
    return
  }

  initAudio()
  if (!sharedAudioContext) return

  // 先停止当前播放（关键：避免两个阶段音乐重叠）
  try {
    sharedAudioContext.stop()
  } catch (e) { /* ignore */ }

  // 设置新曲目并播放
  sharedAudioContext.src = source.url
  sharedAudioContext.loop = source.loop

  try {
    sharedAudioContext.play()
  } catch (e) {
    console.warn('音频播放失败:', e)
  }
}

/** 切换播放/暂停 */
function togglePlay() {
  const settingsStore = useSettingsStore()
  settingsStore.loadPreferences()

  if (!sharedAudioContext) {
    initAudio()
  }

  settingsStore.toggleMusic()

  if (!settingsStore.musicEnabled) {
    // 关闭音乐
    if (sharedAudioContext) {
      try { sharedAudioContext.stop() } catch (e) { /* ignore */ }
    }
    isPlaying.value = false
    return
  }

  // 开启音乐
  if (!currentStage.value) {
    currentStage.value = 'landing'
  }
  switchTo(currentStage.value)
}

/** 停止播放 */
function stop() {
  if (sharedAudioContext) {
    try { sharedAudioContext.stop() } catch (e) { /* ignore */ }
  }
  isPlaying.value = false
  currentStage.value = null
}

/** 开始帧率检测（答题页使用） */
function startFpsCheck() {
  if (sharedFpsCheckTimer) return
  let lastTime = Date.now()
  let frameCount = 0

  sharedFpsCheckTimer = setInterval(() => {
    frameCount++
    const now = Date.now()
    const elapsed = now - lastTime

    if (elapsed >= 1000) {
      const fps = (frameCount / elapsed) * 1000
      if (fps < 20) {
        console.warn(`低帧率检测: ${fps.toFixed(1)}fps，建议关闭动画`)
      }
      frameCount = 0
      lastTime = now
    }
  }, 1000)
}

/** 停止帧率检测 */
function stopFpsCheck() {
  if (sharedFpsCheckTimer) {
    clearInterval(sharedFpsCheckTimer)
    sharedFpsCheckTimer = null
  }
}

/** 销毁（仅在 App.onHide / 退出时调用，正常情况不要调用）*/
function destroy() {
  stopFpsCheck()
  if (sharedAudioContext) {
    try { sharedAudioContext.destroy() } catch (e) { /* ignore */ }
    sharedAudioContext = null
  }
  isPlaying.value = false
  isLoaded.value = false
  currentStage.value = null
  initListenersAttached = false
}

export function useAudioPlayer() {
  return {
    currentStage,
    isPlaying,
    isLoaded,
    switchTo,
    togglePlay,
    stop,
    startFpsCheck,
    stopFpsCheck,
    destroy,
  }
}
