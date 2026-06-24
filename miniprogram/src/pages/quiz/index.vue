<template>
  <view class="quiz-page" :class="`dim-${dimensionIndex}`">
    <!-- 音频控制 -->
    <AudioController :isPlaying="isPlaying" @toggle="toggleAudio" />

    <!-- 顶部进度区 -->
    <view class="header">
      <view class="dimension-badge">
        <text class="dim-number">维度 {{ dimensionIndex + 1 }}/7</text>
        <text class="dim-name">{{ currentDimension }}</text>
      </view>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
      <text class="progress-text">{{ currentIndex + 1 }} / 63</text>
    </view>

    <!-- 题目区域 - 金色卷轴 -->
    <view class="scroll-container" v-if="currentQuestion" :class="{ 'fade-in': showQuestion }">
      <!-- 左卷轴头 -->
      <view class="scroll-end scroll-left"></view>

      <!-- 卷轴主体 -->
      <view class="scroll-body">
        <text class="question-text">{{ currentQuestion.text }}</text>

        <!-- 评分滑块 -->
        <view class="score-slider">
          <view class="score-labels">
            <text class="label-min">完全不是我</text>
            <text class="label-mid">不确定</text>
            <text class="label-max">这就是说我</text>
          </view>

          <!-- 自定义滑块 -->
          <view class="custom-slider" @tap="onTrackTap">
            <view class="slider-track" id="sliderTrack">
              <view class="slider-fill" :style="{ width: sliderPercent + '%' }"></view>
              <!-- 心形滑块 -->
              <view
                class="heart-thumb"
                :style="{ left: sliderPercent + '%' }"
                @touchstart.prevent="onTouchStart"
                @touchmove.prevent="onTouchMove"
                @touchend="onTouchEnd"
              >
                <view class="heart"></view>
              </view>
            </view>
          </view>

          <view class="score-display">
            <text class="score-value" :class="{ 'score-active': true }">
              {{ displayScore }}
            </text>
            <text class="score-hint">{{ scoreLabel }}</text>
          </view>
        </view>
      </view>

      <!-- 右卷轴头 -->
      <view class="scroll-end scroll-right"></view>
    </view>

    <!-- 导航按钮 -->
    <view class="nav-buttons">
      <view class="btn-prev" :class="{ disabled: currentIndex === 0 }" @tap="prevQuestion">
        <text>← 上一题</text>
      </view>
      <view class="btn-next highlight" @tap="nextQuestion">
        <text>{{ currentIndex === 62 ? '✨ 查看我的人格' : '下一题 →' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import questionsData from '@/data/questions.json'
import AudioController from '@/components/AudioController.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const { isPlaying, switchTo, togglePlay, startFpsCheck, stopFpsCheck } = useAudioPlayer()
const toggleAudio = togglePlay

const currentIndex = ref(0)
// 初始所有答案为 5（中间位置）
const answers = ref<number[]>(new Array(63).fill(5))
const startTime = ref(Date.now())
const showQuestion = ref(true)

// 每次进入测试题环节，清空旧答案重新开始
uni.removeStorageSync('quiz_answers')

const currentQuestion = computed(() => questionsData[currentIndex.value] || null)
const currentDimension = computed(() => currentQuestion.value?.dimension || '')
const currentScore = computed(() => {
  const v = answers.value[currentIndex.value]
  return typeof v === 'number' ? v : 5
})
const progressPercent = computed(() => ((currentIndex.value + 1) / 63) * 100)
const dimensionIndex = computed(() => {
  if (!currentQuestion.value) return 0
  return (currentQuestion.value as any).dimensionIndex ?? Math.floor(currentIndex.value / 9)
})

// 滑块百分比 (0-100)
const sliderPercent = computed(() => {
  const v = currentScore.value
  const s = typeof v === 'number' ? v : 5
  return (s / 10) * 100
})

// 显示的分值（保留1位小数）
const displayScore = computed(() => {
  const v = currentScore.value
  const s = typeof v === 'number' ? v : 5
  if (s === 0) return '0'
  if (s === 10) return '10'
  try { return s.toFixed(1) } catch { return String(s) }
})

// 分值对应文字描述
const scoreLabel = computed(() => {
  const v = currentScore.value
  const s = typeof v === 'number' ? v : 5
  if (s <= 0.3) return '完全不是我'
  if (s <= 1.5) return '几乎不是我'
  if (s <= 2.5) return '很少像我'
  if (s <= 3.5) return '不太像我'
  if (s <= 4.5) return '有点不像我'
  if (s <= 5.5) return '不确定'
  if (s <= 6.5) return '有点像我'
  if (s <= 7.5) return '比较像我'
  if (s <= 8.5) return '很像我'
  if (s <= 9.5) return '几乎就是我'
  return '这就是说我'
})

// 题目切换动画
watch(currentIndex, () => {
  showQuestion.value = false
  setTimeout(() => {
    showQuestion.value = true
  }, 50)
})

onShow(() => {
  switchTo('quiz')
  startFpsCheck()
})

// === 自定义滑块触摸处理 ===
const trackLeft = ref(0)
const trackWidth = ref(0)
const isDragging = ref(false)

function getTrackRect() {
  return new Promise<void>((resolve) => {
    uni.createSelectorQuery().select('#sliderTrack').boundingClientRect((rect: any) => {
      if (rect) {
        trackLeft.value = rect.left
        trackWidth.value = rect.width
      }
      resolve()
    }).exec()
  })
}

function calcScore(pageX: number): number {
  const x = pageX - trackLeft.value
  const pct = Math.max(0, Math.min(1, x / trackWidth.value))
  // 精确到0.1
  return Math.round(pct * 100) / 10
}

async function onTouchStart(e: any) {
  isDragging.value = true
  await getTrackRect()
  const touch = e.touches[0]
  const score = calcScore(touch.pageX)
  answers.value[currentIndex.value] = score
}

async function onTouchMove(e: any) {
  if (!isDragging.value) return
  if (trackWidth.value === 0) await getTrackRect()
  const touch = e.touches[0]
  const score = calcScore(touch.pageX)
  answers.value[currentIndex.value] = score
}

function onTouchEnd() {
  isDragging.value = false
  uni.setStorageSync('quiz_answers', JSON.stringify(answers.value))
}

async function onTrackTap(e: any) {
  await getTrackRect()
  const score = calcScore(e.detail.x ?? e.touches?.[0]?.pageX ?? 0)
  answers.value[currentIndex.value] = score
  uni.setStorageSync('quiz_answers', JSON.stringify(answers.value))
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function nextQuestion() {
  if (currentIndex.value < 62) {
    currentIndex.value++
  } else {
    submitQuiz()
  }
}

function submitQuiz() {
  const validAnswers = answers.value.map(a => a ?? 5)
  const duration = Math.floor((Date.now() - startTime.value) / 1000)
  uni.setStorageSync('quiz_final_answers', JSON.stringify(validAnswers))
  uni.setStorageSync('quiz_duration', String(duration))
  stopFpsCheck()
  uni.navigateTo({ url: '/pages/loading/index' })
}
</script>

<style lang="scss" scoped>
.quiz-page {
  min-height: 100vh;
  padding: $spacing-xl $spacing-lg;
  display: flex;
  flex-direction: column;
  transition: background 0.8s ease;
}

/* 7个维度不同背景渐变 */
.dim-0 { background: linear-gradient(180deg, #0D2137 0%, #1A3A5C 100%); }
.dim-1 { background: linear-gradient(180deg, #0D2137 0%, #1A2F5C 100%); }
.dim-2 { background: linear-gradient(180deg, #0D2137 0%, #1A4A3C 100%); }
.dim-3 { background: linear-gradient(180deg, #0D2137 0%, #3A2F1A 100%); }
.dim-4 { background: linear-gradient(180deg, #0D2137 0%, #1A1A2F 100%); }
.dim-5 { background: linear-gradient(180deg, #0D2137 0%, #2F2F3A 100%); }
.dim-6 { background: linear-gradient(180deg, #0D2137 0%, #2F2A1A 100%); }

/* 顶部 */
.header {
  margin-bottom: $spacing-xl;
  padding-top: 80rpx;
}

.dimension-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
}

.dim-number {
  font-size: $font-size-xs;
  color: rgba(255, 255, 255, 0.5);
}

.dim-name {
  font-size: $font-size-sm;
  color: $gold-bright;
  font-weight: bold;
}

.progress-bar {
  height: 12rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: $radius-full;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $gold-bright, $gold-deep);
  border-radius: $radius-full;
  transition: width $transition-base;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: $font-size-xs;
  color: $text-white;
  margin-top: $spacing-xs;
}

/* ===== 金色卷轴 ===== */
.scroll-container {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.scroll-container.fade-in {
  animation: fadeSlideIn 0.3s ease;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateX(30rpx); }
  to { opacity: 1; transform: translateX(0); }
}

/* 卷轴头 */
.scroll-end {
  width: 40rpx;
  flex-shrink: 0;
  background: linear-gradient(180deg, #D4A843 0%, #B8860B 30%, #8B6914 50%, #B8860B 70%, #D4A843 100%);
  border-radius: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.4);
  position: relative;
}

.scroll-end::before,
.scroll-end::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 40%, #E8C860, #B8860B 60%, #8B6914);
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.3);
}

.scroll-end::before { top: -16rpx; }
.scroll-end::after { bottom: -16rpx; }

/* 卷轴主体 */
.scroll-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl $spacing-lg;
  background: linear-gradient(180deg,
    rgba(184, 134, 11, 0.12) 0%,
    rgba(212, 168, 67, 0.08) 5%,
    rgba(212, 168, 67, 0.06) 50%,
    rgba(212, 168, 67, 0.08) 95%,
    rgba(184, 134, 11, 0.12) 100%
  );
  border-top: 3rpx solid rgba(212, 168, 67, 0.4);
  border-bottom: 3rpx solid rgba(212, 168, 67, 0.4);
  position: relative;
  overflow: hidden;
}

.scroll-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    90deg,
    transparent 0rpx,
    transparent 80rpx,
    rgba(212, 168, 67, 0.03) 80rpx,
    rgba(212, 168, 67, 0.03) 82rpx
  );
  pointer-events: none;
}

.question-text {
  font-size: $font-size-lg;
  color: #FFF8E1;
  text-align: center;
  line-height: 1.8;
  margin-bottom: $spacing-xl;
  max-width: 95%;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.3);
}

/* ===== 评分滑块 ===== */
.score-slider {
  width: 100%;
  padding: $spacing-md $spacing-sm;
}

.score-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: $spacing-md;
  padding: 0 8rpx;
}

.label-min, .label-mid, .label-max {
  font-size: 22rpx;
  color: rgba(255, 248, 225, 0.6);
}

/* 自定义滑块 */
.custom-slider {
  padding: 20rpx 0;
}

.slider-track {
  position: relative;
  height: 10rpx;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 5rpx;
}

.slider-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #E74C3C, #F39C12);
  border-radius: 5rpx;
  transition: width 0.05s linear;
}

/* 心形滑块 */
.heart-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 56rpx;
  height: 56rpx;
  z-index: 5;
  transition: left 0.05s linear;
}

.heart {
  width: 40rpx;
  height: 40rpx;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  background: linear-gradient(135deg, #FF4757, #E74C3C);
  border-radius: 50% 50% 0 0;
  box-shadow: 0 4rpx 12rpx rgba(231, 76, 60, 0.5);
}

.heart::before {
  content: '';
  position: absolute;
  top: -50%;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #FF6B7A, #FF4757);
  border-radius: 50%;
}

.heart::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #FF4757, #C0392B);
  border-radius: 50%;
}

/* 分值显示 */
.score-display {
  text-align: center;
  margin-top: $spacing-md;
}

.score-value {
  font-size: 72rpx;
  color: $gold-bright;
  font-weight: bold;
}

.score-hint {
  display: block;
  font-size: $font-size-sm;
  color: $gold-soft;
  margin-top: $spacing-xs;
}

/* 导航 */
.nav-buttons {
  display: flex;
  justify-content: space-between;
  padding: $spacing-lg 0;
  padding-bottom: 60rpx;
}

.btn-prev, .btn-next {
  padding: $spacing-md $spacing-xl;
  border-radius: $radius-full;
  text-align: center;
  transition: all 0.3s ease;
}

.btn-prev {
  background: rgba(255, 255, 255, 0.15);
}

.btn-prev text {
  color: $text-white;
  font-size: $font-size-sm;
}

.btn-prev.disabled {
  opacity: 0.3;
  pointer-events: none;
}

.btn-next {
  background: rgba(255, 255, 255, 0.15);
  opacity: 0.5;
}

.btn-next text {
  color: $text-white;
  font-size: $font-size-sm;
}

.btn-next.highlight {
  background: linear-gradient(135deg, $gold-bright, $gold-deep);
  opacity: 1;
  box-shadow: $shadow-gold;
}

.btn-next.highlight text {
  color: $ocean-deep;
  font-weight: bold;
}

.btn-next.disabled {
  pointer-events: none;
}
</style>
