import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PersonalityResult } from '@/composables/usePersonalityCalc'

export const useResultStore = defineStore('result', () => {
  const result = ref<PersonalityResult | null>(null)
  const resultId = ref<number | null>(null)

  function setResult(r: PersonalityResult) {
    result.value = r
  }

  function setResultId(id: number) {
    resultId.value = id
  }

  function loadFromCache(): boolean {
    try {
      const cached = uni.getStorageSync('personality_result')
      if (cached) {
        result.value = JSON.parse(cached)
        return true
      }
    } catch (e) { /* ignore */ }
    return false
  }

  function clear() {
    result.value = null
    resultId.value = null
  }

  return { result, resultId, setResult, setResultId, loadFromCache, clear }
})
