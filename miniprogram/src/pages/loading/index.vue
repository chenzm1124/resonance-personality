<template>
  <view class="loading-page">
    <!-- 九色能量光柱揭示动画 -->
    <view class="energy-reveal">
      <view
        v-for="(score, idx) in nineScores"
        :key="idx"
        class="energy-pillar"
        :class="{ 'revealed': revealed[idx] }"
        :style="{
          backgroundColor: personalityColors[idx],
          animationDelay: idx * 0.3 + 's',
          height: revealed[idx] ? score * 15 + 30 + 'rpx' : '20rpx'
        }"
      ></view>
    </view>

    <!-- Loading文案 -->
    <view class="loading-content">
      <view class="loading-spinner">
        <view class="spinner-ring"></view>
        <view class="spinner-ring ring-2"></view>
      </view>
      <text class="loading-text">{{ currentText }}</text>
      <view class="loading-dots">
        <view class="dot dot-1"></view>
        <view class="dot dot-2"></view>
        <view class="dot dot-3"></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { calculatePersonality, PERSONALITY_COLORS } from '@/composables/usePersonalityCalc'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const { switchTo } = useAudioPlayer()
const personalityColors = PERSONALITY_COLORS as string[]

const loadingTexts = [
  '正在穿越七维情境海...',
  '正在唤醒您的九色人格能量...',
  '主人格与辅人格正在浮现...',
  '正在生成您的IP人格图谱...',
]

const currentText = ref(loadingTexts[0])
const textIndex = ref(0)
const nineScores = ref<number[]>(new Array(9).fill(5))
const revealed = ref<boolean[]>(new Array(9).fill(false))

onMounted(() => {
  // 前端计算人格
  const answersJson = uni.getStorageSync('quiz_final_answers')
  let result: any = null

  if (answersJson) {
    try {
      const answers: number[] = JSON.parse(answersJson)
      result = calculatePersonality(answers)
      nineScores.value = result.nineScores
    } catch (e) {
      console.error('人格计算失败', e)
    }
  }

  // 文案轮播
  const textTimer = setInterval(() => {
    textIndex.value = (textIndex.value + 1) % loadingTexts.length
    currentText.value = loadingTexts[textIndex.value]
  }, 1500)

  // 逐个揭示能量柱
  for (let i = 0; i < 9; i++) {
    setTimeout(() => {
      revealed.value[i] = true
    }, 800 + i * 300)
  }

  // 4.5秒后跳转结果页
  setTimeout(() => {
    clearInterval(textTimer)
    if (result) {
      uni.setStorageSync('personality_result', JSON.stringify(result))
    }
    switchTo('result')
    uni.redirectTo({ url: '/pages/result/index' })
  }, 4500)
})
</script>

<style lang="scss" scoped>
.loading-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #0D2137 0%, $ocean-deep 50%, #0D2137 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 能量柱揭示 */
.energy-reveal {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 16rpx;
  margin-bottom: 100rpx;
  height: 300rpx;
}

.energy-pillar {
  width: 40rpx;
  height: 20rpx;
  border-radius: $radius-sm $radius-sm 0 0;
  opacity: 0.3;
  transition: height 1s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              opacity 0.5s ease;
}

.energy-pillar.revealed {
  opacity: 0.9;
  box-shadow: 0 0 20rpx currentColor;
}

/* Loading内容 */
.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 120rpx;
  height: 120rpx;
  margin: 0 auto $spacing-xl;
  position: relative;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 4rpx solid transparent;
  border-top-color: $gold-bright;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
}

.ring-2 {
  width: 80%;
  height: 80%;
  top: 10%;
  left: 10%;
  border-top-color: $gold-soft;
  animation-direction: reverse;
  animation-duration: 0.8s;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  display: block;
  font-size: $font-size-lg;
  color: $gold-soft;
  animation: fadeInOut 1.5s ease infinite;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: $spacing-sm;
  margin-top: $spacing-lg;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: $gold-bright;
  animation: dotBounce 1.4s ease infinite;
}

.dot-2 { animation-delay: 0.2s; }
.dot-3 { animation-delay: 0.4s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
</style>
