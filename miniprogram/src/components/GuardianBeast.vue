<template>
  <view class="beast-container">
    <view class="beast-image-wrapper">
      <!-- 守护神兽占位图（设计稿到位后替换为真实插画） -->
      <view class="beast-placeholder" :style="{ borderColor: personality.color }">
        <text class="beast-emoji">{{ beastEmojis[personality.index] || '🦁' }}</text>
        <text class="beast-name">{{ personality.guardian }}</text>
      </view>
      <!-- 呼吸感动效通过CSS实现 -->
    </view>
    <text class="beast-title">{{ personality.name }} · {{ personality.guardian }}</text>
    <text class="beast-type">{{ personality.ipType }}</text>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  personality: {
    index: number
    name: string
    guardian: string
    ipType: string
    color: string
  }
}>()

// 神兽emoji占位（设计稿到位后替换为真实插画）
const beastEmojis: Record<number, string> = {
  0: '🦁', // 红色雄狮
  1: '🦊', // 深蓝银狐
  2: '🦌', // 绿色灵鹿
  3: '🦄', // 橙色飞马
  4: '🕷️', // 黑色蜘蛛
  5: '🐕', // 白色小狗
  6: '🐑', // 灰色绵羊
  7: '🐍', // 紫色巨蟒
  8: '🐆', // 金色金钱豹
}
</script>

<style lang="scss" scoped>
.beast-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl 0;
}

.beast-image-wrapper {
  margin-bottom: $spacing-lg;
}

.beast-placeholder {
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  border: 4rpx solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  animation: breathe 4s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scale(1.02) translateY(-5px); }
}

.beast-emoji {
  font-size: 80rpx;
  margin-bottom: $spacing-xs;
}

.beast-name {
  font-size: $font-size-sm;
  color: $text-white;
}

.beast-title {
  font-size: $font-size-xl;
  color: $gold-bright;
  font-weight: bold;
  margin-bottom: $spacing-xs;
}

.beast-type {
  font-size: $font-size-sm;
  color: $gold-soft;
}
</style>
