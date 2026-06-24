<template>
  <view class="audio-controller" @tap="handleToggle">
    <view class="audio-icon" :class="{ 'is-playing': isPlaying }">
      <text v-if="isPlaying">♪</text>
      <text v-else>♫</text>
    </view>
    <!-- 播放时显示波纹动画 -->
    <view v-if="isPlaying" class="audio-waves">
      <view class="wave wave-1"></view>
      <view class="wave wave-2"></view>
      <view class="wave wave-3"></view>
    </view>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  isPlaying: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
}>()

function handleToggle() {
  emit('toggle')
}
</script>

<style lang="scss" scoped>
.audio-controller {
  position: fixed;
  top: 180rpx;
  left: 30rpx;
  z-index: 100;
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.audio-icon {
  font-size: 28rpx;
  color: $text-white;
  opacity: 0.7;
}

.audio-icon.is-playing {
  color: $gold-bright;
  opacity: 1;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.audio-waves {
  position: absolute;
  bottom: -4rpx;
  display: flex;
  gap: 3rpx;
  align-items: flex-end;
}

.wave {
  width: 4rpx;
  background: $gold-bright;
  border-radius: 2rpx;
  animation: wave-bounce 1.2s ease-in-out infinite;
}

.wave-1 {
  height: 12rpx;
  animation-delay: 0s;
}

.wave-2 {
  height: 18rpx;
  animation-delay: 0.2s;
}

.wave-3 {
  height: 10rpx;
  animation-delay: 0.4s;
}

@keyframes wave-bounce {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1.2); }
}
</style>
