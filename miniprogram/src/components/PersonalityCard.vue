<template>
  <view class="personality-card" :class="{ 'is-master': isMaster }">
    <view class="card-header">
      <view class="card-badge" :class="{ 'badge-master': isMaster, 'badge-sub': !isMaster }">
        <text>{{ isMaster ? '主人格' : '辅人格' }}</text>
      </view>
      <text class="card-name" :style="{ color: personality.color }">{{ personality.name }}</text>
      <text class="card-guardian">{{ personality.guardian }}</text>
    </view>

    <!-- IP特性标签 -->
    <view class="card-tags">
      <view
        v-for="(tag, idx) in personality.keywords"
        :key="idx"
        class="tag-item"
      >
        <text>{{ tag }}</text>
      </view>
    </view>

    <!-- 折叠面板 -->
    <view class="card-expand" @tap="expanded = !expanded">
      <text>{{ expanded ? '收起详情' : '展开详情' }}</text>
      <text class="expand-arrow">{{ expanded ? '▲' : '▼' }}</text>
    </view>

    <view class="card-detail" v-show="expanded">
      <!-- IP气质描述 -->
      <view class="detail-section">
        <text class="detail-label">IP气质</text>
        <text class="detail-text">"{{ personality.quote }}"</text>
      </view>

      <!-- 拍摄方向建议 -->
      <view class="detail-section">
        <text class="detail-label">推荐拍摄方向</text>
        <view class="direction-list">
          <view v-for="(dir, idx) in personality.shootDirections" :key="idx" class="direction-item">
            <text class="dir-icon">🎬</text>
            <text class="dir-text">{{ dir }}</text>
          </view>
        </view>
      </view>

      <!-- 不要拍什么 -->
      <view class="detail-section">
        <text class="detail-label">避免方向</text>
        <view class="avoid-list">
          <text class="avoid-text">{{ personality.avoidDirections.join('、') }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  personality: {
    name: string
    guardian: string
    color: string
    keywords: string[]
    quote: string
    shootDirections: string[]
    avoidDirections: string[]
  }
  isMaster: boolean
}>()

const expanded = ref(false)
</script>

<style lang="scss" scoped>
.personality-card {
  background: $white-alpha;
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  border: 2rpx solid transparent;
  transition: border-color $transition-base;
}

.personality-card.is-master {
  border-color: $gold-bright;
  box-shadow: $shadow-gold;
}

.card-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.card-badge {
  padding: 4rpx 16rpx;
  border-radius: $radius-full;
}

.badge-master {
  background: linear-gradient(135deg, $gold-bright, $gold-deep);
}

.badge-master text {
  color: $ocean-deep;
  font-size: $font-size-xs;
  font-weight: bold;
}

.badge-sub {
  background: rgba(255, 255, 255, 0.3);
}

.badge-sub text {
  color: $text-white;
  font-size: $font-size-xs;
}

.card-name {
  font-size: $font-size-xl;
  font-weight: bold;
}

.card-guardian {
  font-size: $font-size-sm;
  color: $gold-soft;
  margin-left: auto;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}

.tag-item {
  background: rgba(241, 196, 15, 0.15);
  padding: 4rpx 16rpx;
  border-radius: $radius-full;
}

.tag-item text {
  font-size: $font-size-xs;
  color: $gold-bright;
}

.card-expand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  padding: $spacing-sm 0;
}

.card-expand text {
  font-size: $font-size-sm;
  color: rgba(255, 255, 255, 0.6);
}

.expand-arrow {
  font-size: $font-size-xs;
}

.card-detail {
  border-top: 1rpx solid rgba(255, 255, 255, 0.1);
  padding-top: $spacing-md;
}

.detail-section {
  margin-bottom: $spacing-lg;
}

.detail-label {
  display: block;
  font-size: $font-size-sm;
  color: $gold-bright;
  margin-bottom: $spacing-sm;
  font-weight: bold;
}

.detail-text {
  font-size: $font-size-base;
  color: $text-white;
  line-height: 1.8;
  font-style: italic;
}

.direction-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.direction-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.dir-icon {
  font-size: $font-size-sm;
}

.dir-text {
  font-size: $font-size-sm;
  color: $text-white;
}

.avoid-list {
  padding-left: $spacing-md;
}

.avoid-text {
  font-size: $font-size-sm;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
}
</style>
