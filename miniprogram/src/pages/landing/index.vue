<template>
  <view class="landing-page">
    <!-- 音频控制 -->
    <AudioController :isPlaying="isPlaying" @toggle="toggleAudio" />

    <!-- 封面层 -->
    <view class="cover-layer" :class="{ 'cover-leaving': isLeaving }">
      <!-- 全屏背景图 -->
      <image class="bg-image" src="/static/images/cover-bg-new.jpg" mode="widthFix" />

      <!-- 底部暗色渐变 -->
      <view class="bottom-gradient"></view>

      <!-- 中上方标题（行楷字体图片） - 已隐藏，标题已包含在新封面图中 -->
      <!-- <image class="title-image" src="/static/images/cover-title.png" mode="widthFix" /> -->

      <!-- 开始探索 -->
      <view class="start-area" @tap="handleStart">
        <text class="start-text">开始探索</text>
        <view class="glow-triangle"></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api } from '@/api/request'
import AudioController from '@/components/AudioController.vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const { isPlaying, switchTo, togglePlay } = useAudioPlayer()
const toggleAudio = togglePlay
const isLeaving = ref(false)

onShow(() => {
  switchTo('landing')
})

function handleStart() {
  if (isLeaving.value) return
  isLeaving.value = true

  const doNavigate = () => {
    setTimeout(() => {
      uni.navigateTo({ url: '/pages/quiz/index' })
    }, 900)
  }

  api.post('/auth/login', { code: 'mock_test_user' }).then((res) => {
    if (res.data?.token) {
      uni.setStorageSync('auth_token', res.data.token)
      uni.setStorageSync('user_info', JSON.stringify(res.data.user))
    }
    doNavigate()
  }).catch(() => {
    doNavigate()
  })
}
</script>

<style lang="scss" scoped>
.landing-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: #050520;
}

/* ===== 封面层 ===== */
.cover-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  transform: translateY(0);
  transition: transform 0.9s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.9s ease;
}

.cover-layer.cover-leaving {
  transform: translateY(-100%);
  opacity: 0;
}

/* ===== 背景图 ===== */
.bg-image {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 750rpx;
  z-index: 0;
}

/* 底部暗色渐变 - 加高加深，让开始探索区域纯净 */
.bottom-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 55%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(5, 5, 32, 0.4) 30%,
    rgba(5, 5, 32, 0.85) 70%,
    rgba(5, 5, 32, 1) 100%
  );
  pointer-events: none;
  z-index: 1;
}

/* ===== 中上方标题图片（已隐藏） ===== */
/* .title-image {
  position: absolute;
  top: 22%;
  left: 50%;
  transform: translateX(-50%);
  width: 600rpx;
  z-index: 2;
} */

/* ===== 开始探索 ===== */
.start-area {
  position: absolute;
  bottom: 60rpx;
  left: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 3;
}

.start-text {
  font-size: 52rpx;
  font-weight: 600;
  letter-spacing: 16rpx;
  color: #f6c453;
  font-family: "STKaiti", "KaiTi", "Kaiti SC", "STSong", "SimSun", "Noto Serif SC", serif;
  text-shadow:
    0 0 12rpx rgba(255, 215, 100, 0.8),
    0 0 24rpx rgba(255, 200, 80, 0.55),
    0 0 40rpx rgba(255, 180, 60, 0.3),
    0 2rpx 4rpx rgba(0, 0, 0, 0.6);
  animation: text-glow 2.5s ease-in-out infinite;
}

@keyframes text-glow {
  0%, 100% {
    text-shadow:
      0 0 8rpx rgba(255, 215, 100, 0.55),
      0 0 16rpx rgba(255, 200, 80, 0.35),
      0 0 28rpx rgba(255, 180, 60, 0.18),
      0 2rpx 4rpx rgba(0, 0, 0, 0.6);
  }
  50% {
    text-shadow:
      0 0 18rpx rgba(255, 220, 120, 1),
      0 0 36rpx rgba(255, 205, 90, 0.75),
      0 0 60rpx rgba(255, 185, 70, 0.45),
      0 0 90rpx rgba(255, 170, 50, 0.18),
      0 2rpx 4rpx rgba(0, 0, 0, 0.6);
  }
}

/* ===== 荧光三角 ===== */
.glow-triangle {
  margin-top: 20rpx;
  width: 0;
  height: 0;
  border-left: 16rpx solid transparent;
  border-right: 16rpx solid transparent;
  border-top: 20rpx solid rgba(255, 210, 100, 0.85);
  animation: triangle-float 2.5s ease-in-out infinite, triangle-glow 2.5s ease-in-out infinite;
}

@keyframes triangle-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(14rpx); }
}

@keyframes triangle-glow {
  0%, 100% {
    border-top-color: rgba(255, 200, 80, 0.55);
    filter: drop-shadow(0 0 6rpx rgba(255, 195, 80, 0.5));
  }
  50% {
    border-top-color: rgba(255, 225, 130, 1);
    filter: drop-shadow(0 0 16rpx rgba(255, 205, 90, 0.95)) drop-shadow(0 0 28rpx rgba(255, 180, 60, 0.5));
  }
}
</style>
