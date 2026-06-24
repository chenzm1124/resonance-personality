import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const musicEnabled = ref(true)  // 默认开启背景音乐（音频文件已就绪）
  const animationEnabled = ref(true)

  function loadPreferences() {
    const music = uni.getStorageSync('pref_music')
    const animation = uni.getStorageSync('pref_animation')
    if (music !== '') musicEnabled.value = music === 'true'
    if (animation !== '') animationEnabled.value = animation === 'true'
  }

  function toggleMusic() {
    musicEnabled.value = !musicEnabled.value
    uni.setStorageSync('pref_music', String(musicEnabled.value))
  }

  function toggleAnimation() {
    animationEnabled.value = !animationEnabled.value
    uni.setStorageSync('pref_animation', String(animationEnabled.value))
  }

  return { musicEnabled, animationEnabled, loadPreferences, toggleMusic, toggleAnimation }
})
