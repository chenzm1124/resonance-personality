import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useQuizStore = defineStore('quiz', () => {
  // 状态
  const currentIndex = ref(0)
  const answers = ref<(number | null)[]>(new Array(63).fill(null))
  const startTime = ref(Date.now())
  const isCompleted = ref(false)

  // 计算属性
  const currentScore = computed(() => answers.value[currentIndex.value])
  const answeredCount = computed(() => answers.value.filter(a => a !== null).length)
  const progressPercent = computed(() => ((currentIndex.value + 1) / 63) * 100)
  const isLastQuestion = computed(() => currentIndex.value === 62)
  const isFirstQuestion = computed(() => currentIndex.value === 0)

  // 方法
  function setScore(score: number) {
    answers.value[currentIndex.value] = score
    saveToCache()
  }

  function goNext() {
    if (currentScore.value === null) return false
    if (currentIndex.value < 62) {
      currentIndex.value++
      return true
    }
    return false
  }

  function goPrev() {
    if (currentIndex.value > 0) {
      currentIndex.value--
      return true
    }
    return false
  }

  function reset() {
    currentIndex.value = 0
    answers.value = new Array(63).fill(null)
    startTime.value = Date.now()
    isCompleted.value = false
    uni.removeStorageSync('quiz_answers')
    uni.removeStorageSync('quiz_final_answers')
  }

  function saveToCache() {
    try {
      uni.setStorageSync('quiz_answers', JSON.stringify(answers.value))
    } catch (e) {
      console.warn('本地缓存写入失败', e)
    }
  }

  function loadFromCache(): boolean {
    try {
      const cached = uni.getStorageSync('quiz_answers')
      if (cached) {
        const parsed = JSON.parse(cached)
        if (Array.isArray(parsed) && parsed.length === 63) {
          answers.value = parsed
          currentIndex.value = Math.min(parsed.filter((a: any) => a !== null).length, 62)
          return true
        }
      }
    } catch (e) { /* ignore */ }
    return false
  }

  function finalize(): { answers: number[]; duration: number } {
    isCompleted.value = true
    const validAnswers = answers.value.map(a => a ?? 0)
    const duration = Math.floor((Date.now() - startTime.value) / 1000)
    uni.setStorageSync('quiz_final_answers', JSON.stringify(validAnswers))
    uni.setStorageSync('quiz_duration', String(duration))
    return { answers: validAnswers, duration }
  }

  return {
    currentIndex,
    answers,
    startTime,
    isCompleted,
    currentScore,
    answeredCount,
    progressPercent,
    isLastQuestion,
    isFirstQuestion,
    setScore,
    goNext,
    goPrev,
    reset,
    loadFromCache,
    finalize,
  }
})
