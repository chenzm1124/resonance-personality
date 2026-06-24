<template>
  <view class="result-page">
    <!-- 用户信息区 -->
    <view class="result-header">
      <view class="user-avatar-wrapper">
        <image v-if="avatarUrl" :src="avatarUrl" class="user-avatar" mode="aspectFill" />
        <view v-else class="user-avatar-placeholder">
          <text>{{ userName.charAt(0) }}</text>
        </view>
      </view>
      <text class="result-title">{{ userName }}的九色人格图谱</text>
    </view>

    <!-- 九色能量柱 -->
    <view class="scores-section" v-if="result">
      <text class="section-title">人格能量分布</text>
      <view class="energy-bars">
        <view
          v-for="(score, idx) in result.nineScores"
          :key="idx"
          class="bar-item"
          :class="{ 'bar-master': idx === result.masterPersonality, 'bar-sub': (result.subPersonalities || []).includes(idx) }"
        >
          <view
            class="bar"
            :style="{
              height: (animatedHeights[idx] || 0) + 'rpx',
              backgroundColor: personalityColors[idx] || '#888'
            }"
          ></view>
          <text class="bar-label">{{ personalityNames[idx] || '' }}</text>
          <text class="bar-score">{{ typeof score === 'number' ? score.toFixed(1) : '?' }}</text>
        </view>
      </view>
    </view>

    <!-- 前三名人格摘要 -->
    <view class="top3-section" v-if="result">
      <text class="section-title">你的人格组合</text>
      <view class="top3-row">
        <view class="top3-item top3-master">
          <text class="top3-rank">主人格</text>
          <text class="top3-name" :style="{ color: personalityColors[result.masterPersonality] || '#F1C40F' }">
            {{ personalityNames[result.masterPersonality] || '' }}
          </text>
          <text class="top3-score">{{ masterScore }}</text>
        </view>
        <view v-for="(subIdx, i) in (result.subPersonalities || [])" :key="i" class="top3-item">
          <text class="top3-rank">辅人格{{ i + 1 }}</text>
          <text class="top3-name" :style="{ color: personalityColors[subIdx] || '#ccc' }">
            {{ personalityNames[subIdx] || '' }}
          </text>
          <text class="top3-score">{{ subScore(i) }}</text>
        </view>
      </view>
    </view>

    <!-- 守护神兽展示 -->
    <view class="beast-section" v-if="result && masterPersonalityData.name">
      <view class="beast-container">
        <view class="beast-placeholder" :style="{ borderColor: masterPersonalityData.color || '#F1C40F' }">
          <text class="beast-emoji">{{ beastEmojis[masterPersonalityData.index] || '🦁' }}</text>
          <text class="beast-name">{{ masterPersonalityData.guardian || '' }}</text>
        </view>
        <text class="beast-title">{{ masterPersonalityData.name || '' }} · {{ masterPersonalityData.guardian || '' }}</text>
        <text class="beast-type">{{ masterPersonalityData.ipType || '' }}</text>
      </view>
    </view>

    <!-- 人格卡片 -->
    <view class="cards-section" v-if="result">
      <text class="section-title">人格解读</text>
      <!-- 主人格卡片 -->
      <view class="personality-card is-master">
        <view class="card-header">
          <view class="card-badge badge-master"><text>主人格</text></view>
          <text class="card-name" :style="{ color: masterPersonalityData.color || '#F1C40F' }">{{ masterPersonalityData.name || '' }}</text>
        </view>
        <view class="card-tags" v-if="masterPersonalityData.keywords">
          <view v-for="(tag, i) in masterPersonalityData.keywords" :key="i" class="tag-item">
            <text>{{ tag }}</text>
          </view>
        </view>
        <view class="card-quote" v-if="masterPersonalityData.quote">
          <text>"{{ masterPersonalityData.quote }}"</text>
        </view>
      </view>
      <!-- 辅人格卡片 -->
      <view v-for="(subIdx, i) in (result.subPersonalities || [])" :key="i" class="personality-card">
        <view class="card-header">
          <view class="card-badge badge-sub"><text>辅人格</text></view>
          <text class="card-name" :style="{ color: personalityColors[subIdx] || '#ccc' }">{{ personalityNames[subIdx] || '' }}</text>
        </view>
        <view class="card-tags" v-if="subPersonalityData(i).keywords">
          <view v-for="(tag, j) in subPersonalityData(i).keywords" :key="j" class="tag-item">
            <text>{{ tag }}</text>
          </view>
        </view>
        <view class="card-quote" v-if="subPersonalityData(i).quote">
          <text>"{{ subPersonalityData(i).quote }}"</text>
        </view>
      </view>
    </view>

    <!-- 推荐博主板块 -->
    <view class="recommend-section" v-if="result">
      <text class="section-title">为你推荐的短视频博主</text>
      <!-- 加载状态 -->
      <view v-if="recommendLoading" class="recommend-loading">
        <view class="loading-dots">
          <view class="dot"></view>
          <view class="dot"></view>
          <view class="dot"></view>
        </view>
        <text class="loading-text">正在为你匹配最合适的博主...</text>
      </view>
      <!-- 错误状态 -->
      <view v-else-if="recommendError" class="recommend-error">
        <text class="error-text">加载失败，请稍后再试</text>
        <view class="btn-retry" @tap="loadRecommendations">
          <text>重新加载</text>
        </view>
      </view>
      <!-- 博主卡片列表 -->
      <view v-else-if="recommendData" class="creator-list">
        <view
          v-for="(creator, idx) in recommendData.creators"
          :key="idx"
          class="creator-card"
        >
          <!-- 博主头部 -->
          <view class="creator-header">
            <view class="creator-avatar-placeholder">
              <text>{{ creator.name.charAt(0) }}</text>
            </view>
            <view class="creator-info">
              <text class="creator-name">{{ creator.name }}</text>
              <view class="platform-tag">
                <text>{{ creator.platform }}</text>
              </view>
            </view>
            <text class="creator-followers">{{ creator.followers }}</text>
          </view>
          <!-- 风格标签 -->
          <view class="creator-tags">
            <view v-for="(tag, j) in creator.style_tags" :key="j" class="style-tag">
              <text>{{ tag }}</text>
            </view>
          </view>
          <!-- 推荐理由 -->
          <view class="creator-reason">
            <text>{{ creator.reason }}</text>
          </view>
          <!-- 拍摄方向 -->
          <view class="creator-direction" v-if="creator.shooting_direction">
            <text class="direction-label">推荐拍摄方向：</text>
            <text class="direction-text">{{ creator.shooting_direction }}</text>
          </view>
          <!-- 参考视频 -->
          <view class="creator-videos" v-if="creator.videos && creator.videos.length > 0">
            <text class="videos-title">参考视频</text>
            <view
              v-for="(video, k) in creator.videos"
              :key="k"
              class="video-item"
              @tap="copyVideoLink(video.url)"
            >
              <view class="video-icon">
                <text>▶</text>
              </view>
              <view class="video-info">
                <text class="video-title">{{ video.title }}</text>
                <text class="video-desc">{{ video.description }}</text>
              </view>
              <text class="video-copy">复制链接</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <view class="btn-poster" @tap="generatePoster">
        <text>生成专属海报</text>
      </view>
      <button class="btn-share" open-type="share">
        <text>分享给好友</text>
      </button>
      <view class="btn-report">
        <text>解锁完整IP人格报告</text>
        <text class="btn-report-sub">敬请期待</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { PERSONALITY_NAMES, PERSONALITY_COLORS } from '@/composables/usePersonalityCalc'
import personalitiesData from '@/data/personalities.json'
import { getCreatorRecommendations, type RecommendResponse } from '@/api/recommend'

// 模板可直接引用的变量
const personalityNames = PERSONALITY_NAMES as string[]
const personalityColors = PERSONALITY_COLORS as string[]

const result = ref<any>(null)
// 开发版固定用户昵称（正式版通过微信授权获取）
const userName = ref('星辰探索者')
const avatarUrl = ref('')
const animatedHeights = ref<number[]>(new Array(9).fill(0))
const masterPersonalityData = ref<any>({})

// 推荐博主状态
const recommendLoading = ref(false)
const recommendError = ref(false)
const recommendData = ref<RecommendResponse | null>(null)

const beastEmojis: Record<number, string> = {
  0: '🦁', 1: '🦊', 2: '🦌', 3: '🦄', 4: '🕷️',
  5: '🐕', 6: '🐑', 7: '🐍', 8: '🐆',
}

// 主人格分值
const masterScore = computed(() => {
  if (!result.value || !Array.isArray(result.value.nineScores)) return '?'
  const s = result.value.nineScores[result.value.masterPersonality]
  return typeof s === 'number' ? s.toFixed(1) : '?'
})

// 辅人格分值
function subScore(i: number | string): string {
  const idx = Number(i)
  if (!result.value || !Array.isArray(result.value.subPersonalities)) return '?'
  const pIdx = result.value.subPersonalities[idx]
  const s = result.value.nineScores?.[pIdx]
  return typeof s === 'number' ? s.toFixed(1) : '?'
}

// 辅人格数据
function subPersonalityData(i: number | string): any {
  const idx = Number(i)
  if (!result.value || !Array.isArray(result.value.subPersonalities)) return {}
  const pIdx = result.value.subPersonalities[idx]
  return personalitiesData[pIdx] || {}
}

onMounted(() => {
  const resultJson = uni.getStorageSync('personality_result')
  if (resultJson) {
    try {
      result.value = JSON.parse(resultJson)
      const masterIdx = typeof result.value.masterPersonality === 'number' ? result.value.masterPersonality : 0
      masterPersonalityData.value = personalitiesData[masterIdx] || {}
    } catch (e) {
      console.error('解析人格结果失败', e)
    }
  }

  const userInfo = uni.getStorageSync('user_info')
  if (userInfo) {
    try {
      const info = JSON.parse(userInfo)
      userName.value = info.nickname || '星辰探索者'
      avatarUrl.value = info.avatar_url || ''
    } catch (e) { /* ignore */ }
  }

  if (result.value && Array.isArray(result.value.nineScores)) {
    nextTick(() => {
      const scores = result.value.nineScores as number[]
      const masterIdx = typeof result.value.masterPersonality === 'number' ? result.value.masterPersonality : 0
      for (let i = 0; i < 9; i++) {
        if (i === masterIdx) continue
        const s = typeof scores[i] === 'number' ? scores[i] : 5
        setTimeout(() => { animatedHeights.value[i] = s * 30 }, i * 150)
      }
      const ms = typeof scores[masterIdx] === 'number' ? scores[masterIdx] : 5
      setTimeout(() => { animatedHeights.value[masterIdx] = ms * 30 }, 9 * 150 + 200)
    })
  }

  // 加载博主推荐
  loadRecommendations()
})

function generatePoster() {
  uni.showToast({ title: '海报生成功能开发中', icon: 'none' })
}

/** 加载博主推荐 */
async function loadRecommendations() {
  if (!result.value || !Array.isArray(result.value.nineScores)) return

  recommendLoading.value = true
  recommendError.value = false

  try {
    const data = await getCreatorRecommendations({
      nineScores: result.value.nineScores,
      masterPersonality: result.value.masterPersonality,
      subPersonalities: result.value.subPersonalities || [],
    })
    if (data && data.creators && data.creators.length > 0) {
      recommendData.value = data
    } else {
      // API 返回空数据，标记为错误
      recommendError.value = true
    }
  } catch (e) {
    console.error('博主推荐加载失败', e)
    recommendError.value = true
  } finally {
    recommendLoading.value = false
  }
}

/** 复制视频链接 */
function copyVideoLink(url: string) {
  uni.setClipboardData({
    data: url,
    success: () => {
      uni.showToast({ title: '链接已复制，请在抖音中打开', icon: 'none', duration: 2000 })
    },
    fail: () => {
      uni.showToast({ title: '复制失败', icon: 'none' })
    },
  })
}
</script>

<style lang="scss" scoped>
.result-page {
  min-height: 100vh;
  background: linear-gradient(180deg, $ocean-deep 0%, $ocean-mid 30%, $ocean-light 100%);
  padding: $spacing-lg;
  padding-top: 100rpx;
  padding-bottom: 80rpx;
}

.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: $spacing-xl;
}

.user-avatar-wrapper { margin-bottom: $spacing-md; }

.user-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  border: 3rpx solid $gold-bright;
}

.user-avatar-placeholder {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  border: 3rpx solid $gold-bright;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar-placeholder text {
  font-size: $font-size-xl;
  color: $gold-bright;
  font-weight: bold;
}

.result-title {
  font-size: $font-size-xl;
  color: $text-white;
  font-weight: bold;
}

.section-title {
  display: block;
  font-size: $font-size-lg;
  color: $gold-bright;
  text-align: center;
  margin-bottom: $spacing-lg;
  font-weight: bold;
}

.energy-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 400rpx;
  padding: $spacing-md;
  background: rgba(255, 255, 255, 0.08);
  border-radius: $radius-lg;
  margin-bottom: $spacing-xl;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar {
  width: 36rpx;
  border-radius: $radius-sm $radius-sm 0 0;
  transition: height 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  min-height: 10rpx;
}

.bar-master .bar { box-shadow: 0 0 16rpx rgba(241, 196, 15, 0.6); }
.bar-sub .bar { box-shadow: 0 0 10rpx rgba(255, 255, 255, 0.4); }

.bar-label {
  font-size: 20rpx;
  color: $text-white;
  margin-top: $spacing-xs;
  white-space: nowrap;
}

.bar-score {
  font-size: 18rpx;
  color: $gold-soft;
}

.beast-section { margin-bottom: $spacing-xl; }

/* 前三名人格摘要 */
.top3-section { margin-bottom: $spacing-xl; }

.top3-row {
  display: flex;
  justify-content: center;
  gap: $spacing-md;
}

.top3-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-lg $spacing-sm;
  background: rgba(255, 255, 255, 0.08);
  border-radius: $radius-lg;
}

.top3-master {
  background: rgba(241, 196, 15, 0.12);
  border: 2rpx solid rgba(241, 196, 15, 0.4);
  box-shadow: 0 0 20rpx rgba(241, 196, 15, 0.15);
}

.top3-rank {
  font-size: $font-size-xs;
  color: $gold-soft;
  margin-bottom: $spacing-xs;
}

.top3-name {
  font-size: $font-size-xl;
  font-weight: bold;
  margin-bottom: $spacing-xs;
}

.top3-score {
  font-size: $font-size-sm;
  color: $text-white;
}

.beast-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl 0;
}

.beast-placeholder {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  border: 4rpx solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  margin-bottom: $spacing-lg;
}

.beast-emoji { font-size: 70rpx; }
.beast-name { font-size: $font-size-sm; color: $text-white; }
.beast-title { font-size: $font-size-xl; color: $gold-bright; font-weight: bold; }
.beast-type { font-size: $font-size-sm; color: $gold-soft; }

.cards-section { margin-bottom: $spacing-xl; }

.personality-card {
  background: rgba(13, 33, 55, 0.7);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  border: 2rpx solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10rpx);
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

.card-badge { padding: 4rpx 16rpx; border-radius: $radius-full; }
.badge-master { background: linear-gradient(135deg, $gold-bright, $gold-deep); }
.badge-master text { color: $ocean-deep; font-size: $font-size-xs; font-weight: bold; }
.badge-sub { background: rgba(255, 255, 255, 0.3); }
.badge-sub text { color: $text-white; font-size: $font-size-xs; }

.card-name { font-size: $font-size-xl; font-weight: bold; text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.5); }

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.tag-item {
  background: rgba(241, 196, 15, 0.18);
  padding: 6rpx 20rpx;
  border-radius: $radius-full;
  border: 1rpx solid rgba(241, 196, 15, 0.25);
}

.tag-item text { font-size: $font-size-xs; color: $gold-bright; }

.card-quote {
  margin-top: $spacing-md;
}

.card-quote text {
  font-size: $font-size-sm;
  color: $gold-bright;
  font-style: italic;
  line-height: 1.8;
}

/* ===== 推荐博主板块 ===== */
.recommend-section { margin-bottom: $spacing-xl; }

.recommend-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl;
}

.loading-dots {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}

.loading-dots .dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: $gold-bright;
  animation: dotPulse 1.2s ease-in-out infinite;
}

.loading-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 100% { transform: scale(0.6); opacity: 0.4; }
  50% { transform: scale(1); opacity: 1; }
}

.loading-text { font-size: $font-size-sm; color: $gold-soft; }

.recommend-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xl;
}

.error-text { font-size: $font-size-sm; color: rgba(255,255,255,0.5); margin-bottom: $spacing-md; }

.btn-retry {
  background: rgba(255,255,255,0.15);
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-full;
}

.btn-retry text { font-size: $font-size-sm; color: $text-white; }

/* 博主卡片 */
.creator-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.creator-card {
  background: rgba(13, 33, 55, 0.75);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  border: 2rpx solid rgba(241, 196, 15, 0.2);
  backdrop-filter: blur(10rpx);
}

.creator-header {
  display: flex;
  align-items: center;
  margin-bottom: $spacing-md;
}

.creator-avatar-placeholder {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $gold-bright, $gold-deep);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.creator-avatar-placeholder text {
  font-size: $font-size-lg;
  color: $ocean-deep;
  font-weight: bold;
}

.creator-info { flex: 1; }

.creator-name {
  font-size: $font-size-lg;
  color: $text-white;
  font-weight: bold;
  display: block;
}

.platform-tag {
  display: inline-block;
  background: rgba(255, 59, 48, 0.2);
  padding: 2rpx 12rpx;
  border-radius: $radius-full;
  margin-top: 4rpx;
}

.platform-tag text { font-size: 20rpx; color: #FF6B6B; }

.creator-followers {
  font-size: $font-size-sm;
  color: $gold-soft;
  flex-shrink: 0;
}

.creator-tags {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}

.style-tag {
  background: rgba(100, 180, 255, 0.15);
  padding: 4rpx 16rpx;
  border-radius: $radius-full;
  border: 1rpx solid rgba(100, 180, 255, 0.3);
}

.style-tag text { font-size: $font-size-xs; color: #7FB8FF; }

.creator-reason {
  background: rgba(241, 196, 15, 0.08);
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-sm;
  margin-bottom: $spacing-md;
  border-left: 4rpx solid $gold-bright;
}

.creator-reason text { font-size: $font-size-sm; color: $gold-bright; line-height: 1.6; }

.creator-direction {
  margin-bottom: $spacing-md;
}

.direction-label { font-size: $font-size-xs; color: $gold-soft; }
.direction-text { font-size: $font-size-sm; color: $text-white; }

/* 参考视频 */
.creator-videos { margin-top: $spacing-sm; }

.videos-title {
  font-size: $font-size-xs;
  color: $gold-soft;
  display: block;
  margin-bottom: $spacing-xs;
}

.video-item {
  display: flex;
  align-items: center;
  padding: $spacing-sm;
  background: rgba(255, 255, 255, 0.05);
  border-radius: $radius-sm;
  margin-bottom: $spacing-xs;
}

.video-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(255, 59, 48, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-sm;
  flex-shrink: 0;
}

.video-icon text { font-size: 24rpx; color: #FF6B6B; }

.video-info { flex: 1; overflow: hidden; }

.video-title {
  font-size: $font-size-sm;
  color: $text-white;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-desc {
  font-size: 20rpx;
  color: rgba(255,255,255,0.4);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-copy {
  font-size: 20rpx;
  color: $gold-bright;
  flex-shrink: 0;
  padding: 4rpx 12rpx;
  border: 1rpx solid rgba(241, 196, 15, 0.3);
  border-radius: $radius-full;
  margin-left: $spacing-sm;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  padding-bottom: 60rpx;
}

.btn-poster {
  background: linear-gradient(135deg, $gold-bright, $gold-deep);
  padding: $spacing-md;
  border-radius: $radius-full;
  text-align: center;
  box-shadow: $shadow-gold;
}

.btn-poster text {
  color: $ocean-deep;
  font-size: $font-size-base;
  font-weight: bold;
}

.btn-share {
  background: rgba(255, 255, 255, 0.2) !important;
  padding: $spacing-md !important;
  border-radius: $radius-full !important;
  text-align: center;
  border: none;
  margin: 0;
  line-height: normal;
}

.btn-share text { color: $text-white; font-size: $font-size-base; }

.btn-report {
  background: rgba(255, 255, 255, 0.1);
  padding: $spacing-md;
  border-radius: $radius-full;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.btn-report text { color: rgba(255, 255, 255, 0.5); font-size: $font-size-base; }
.btn-report-sub { font-size: $font-size-xs !important; margin-top: 4rpx; }
</style>
