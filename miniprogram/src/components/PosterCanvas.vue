<template>
  <view class="poster-overlay" v-if="visible" @tap.stop>
    <view class="poster-container">
      <canvas
        canvas-id="posterCanvas"
        id="posterCanvas"
        class="poster-canvas"
        :style="{ width: '600rpx', height: '900rpx' }"
      ></canvas>
      <view class="poster-actions">
        <view class="btn-save" @tap="saveToAlbum">
          <text>保存到相册</text>
        </view>
        <view class="btn-share" @tap="shareToFriend">
          <text>转发给好友</text>
        </view>
        <view class="btn-close" @tap="close">
          <text>关闭</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { PERSONALITY_NAMES, PERSONALITY_COLORS } from '@/composables/usePersonalityCalc'
import personalitiesData from '@/data/personalities.json'

const props = defineProps<{
  visible: boolean
  result: {
    nineScores: number[]
    masterPersonality: number
    subPersonalities: number[]
  } | null
  userName: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const posterGenerated = ref(false)
const posterTempPath = ref('')

watch(() => props.visible, (val) => {
  if (val && props.result) {
    nextTick(() => {
      setTimeout(() => generatePoster(), 300)
    })
  }
})

function generatePoster() {
  if (!props.result) return

  const ctx = uni.createCanvasContext('posterCanvas')
  const W = 600
  const H = 900

  // 1. 背景 — 深蓝渐变
  const bgGrad = ctx.createLinearGradient(0, 0, 0, H)
  bgGrad.addColorStop(0, '#0D2137')
  bgGrad.addColorStop(0.5, '#1A5276')
  bgGrad.addColorStop(1, '#2980B9')
  ctx.setFillStyle(bgGrad as any)
  ctx.fillRect(0, 0, W, H)

  // 2. 顶部品牌名
  ctx.setFillStyle('#FFFFFF')
  ctx.setFontSize(16)
  ctx.setTextAlign('center')
  ctx.fillText('共鸣人格IP打造系统', W / 2, 40)

  // 3. 用户名 + 标题
  ctx.setFillStyle('#F1C40F')
  ctx.setFontSize(22)
  ctx.fillText(`${props.userName}的九色人格图谱`, W / 2, 80)

  // 4. 九色能量柱缩略图
  const barAreaX = 60
  const barAreaY = 110
  const barWidth = 40
  const barGap = 12
  const maxBarH = 200

  for (let i = 0; i < 9; i++) {
    const score = props.result.nineScores[i]
    const barH = (score / 10) * maxBarH
    const x = barAreaX + i * (barWidth + barGap)
    const y = barAreaY + maxBarH - barH

    // 柱体
    ctx.setFillStyle(PERSONALITY_COLORS[i])
    ctx.fillRect(x, y, barWidth, barH)

    // 主人格金色光晕
    if (i === props.result.masterPersonality) {
      ctx.setStrokeStyle('#F1C40F')
      ctx.setLineWidth(2)
      ctx.strokeRect(x - 2, y - 2, barWidth + 4, barH + 4)
    }

    // 人格名
    ctx.setFillStyle('#FFFFFF')
    ctx.setFontSize(10)
    ctx.setTextAlign('center')
    ctx.fillText(PERSONALITY_NAMES[i], x + barWidth / 2, barAreaY + maxBarH + 18)

    // 分数
    ctx.setFillStyle('#FCF3CF')
    ctx.setFontSize(9)
    ctx.fillText(String(score), x + barWidth / 2, y - 6)
  }

  // 5. 主人格信息区
  const masterInfo = personalitiesData[props.result.masterPersonality]
  const infoY = 380

  // 守护神兽占位区（圆形）
  ctx.setFillStyle('rgba(255,255,255,0.1)')
  ctx.beginPath()
  ctx.arc(W / 2, infoY + 60, 60, 0, Math.PI * 2)
  ctx.fill()

  ctx.setFillStyle('#FFFFFF')
  ctx.setFontSize(14)
  ctx.setTextAlign('center')
  ctx.fillText(masterInfo.guardian, W / 2, infoY + 65)

  // 主人格名称
  ctx.setFillStyle('#F1C40F')
  ctx.setFontSize(24)
  ctx.fillText(`主人格：${masterInfo.name}`, W / 2, infoY + 150)

  // IP类型
  ctx.setFillStyle('#FCF3CF')
  ctx.setFontSize(14)
  ctx.fillText(masterInfo.ipType, W / 2, infoY + 175)

  // IP特性标签
  const tags = masterInfo.keywords.slice(0, 4)
  const tagY = infoY + 205
  const tagTotalW = tags.length * 80
  const tagStartX = (W - tagTotalW) / 2

  for (let i = 0; i < tags.length; i++) {
    const tx = tagStartX + i * 80
    // 标签背景
    ctx.setFillStyle('rgba(241, 196, 15, 0.2)')
    roundRect(ctx, tx, tagY - 12, 70, 24, 12)
    ctx.fill()
    // 标签文字
    ctx.setFillStyle('#F1C40F')
    ctx.setFontSize(11)
    ctx.setTextAlign('center')
    ctx.fillText(tags[i], tx + 35, tagY + 4)
  }

  // 金句
  ctx.setFillStyle('rgba(255,255,255,0.8)')
  ctx.setFontSize(13)
  ctx.setTextAlign('center')
  ctx.fillText(`"${masterInfo.quote}"`, W / 2, infoY + 250)

  // 6. 辅人格信息
  const subY = infoY + 290
  ctx.setFillStyle('#FFFFFF')
  ctx.setFontSize(13)
  ctx.fillText('辅人格', W / 2, subY)

  for (let i = 0; i < 2; i++) {
    const subIdx = props.result.subPersonalities[i]
    const subInfo = personalitiesData[subIdx]
    const sx = W / 2 - 120 + i * 240

    ctx.setFillStyle(PERSONALITY_COLORS[subIdx])
    ctx.beginPath()
    ctx.arc(sx, subY + 35, 20, 0, Math.PI * 2)
    ctx.fill()

    ctx.setFillStyle('#FFFFFF')
    ctx.setFontSize(11)
    ctx.fillText(subInfo.name, sx, subY + 70)
    ctx.setFillStyle('#FCF3CF')
    ctx.setFontSize(9)
    ctx.fillText(subInfo.guardian, sx, subY + 85)
  }

  // 7. 底部品牌 + 小程序码占位
  ctx.setFillStyle('rgba(255,255,255,0.4)')
  ctx.setFontSize(10)
  ctx.setTextAlign('center')
  ctx.fillText('扫码测你的九色人格', W / 2, H - 40)

  // 小程序码占位方块
  ctx.setFillStyle('rgba(255,255,255,0.2)')
  ctx.fillRect(W / 2 - 30, H - 110, 60, 60)
  ctx.setFillStyle('#FFFFFF')
  ctx.setFontSize(8)
  ctx.fillText('小程序码', W / 2, H - 76)

  // 绘制完成
  ctx.draw(false, () => {
    setTimeout(() => {
      uni.canvasToTempFilePath({
        canvasId: 'posterCanvas',
        quality: 1,
        success: (res) => {
          posterTempPath.value = res.tempFilePath
          posterGenerated.value = true
        },
        fail: (err) => {
          console.error('海报生成失败', err)
          uni.showToast({ title: '海报生成失败', icon: 'none' })
        },
      })
    }, 500)
  })
}

/** 辅助：圆角矩形路径 */
function roundRect(ctx: any, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

function saveToAlbum() {
  if (!posterGenerated.value || !posterTempPath.value) {
    // 降级为文字版分享
    fallbackShare()
    return
  }

  uni.saveImageToPhotosAlbum({
    filePath: posterTempPath.value,
    success: () => {
      uni.showToast({ title: '已保存到相册', icon: 'success' })
    },
    fail: (err) => {
      if (err.errMsg?.includes('auth deny') || err.errMsg?.includes('authorize')) {
        uni.showModal({
          title: '提示',
          content: '需要相册权限才能保存海报，去开启？',
          success: (res) => {
            if (res.confirm) {
              uni.openSetting()
            }
          },
        })
      } else {
        fallbackShare()
      }
    },
  })
}

function shareToFriend() {
  // 微信小程序转发
  uni.showShareMenu({
    withShareTicket: true,
    success: () => {
      uni.showToast({ title: '点击右上角分享', icon: 'none' })
    },
  })
}

function fallbackShare() {
  if (!props.result) return
  const master = PERSONALITY_NAMES[props.result.masterPersonality]
  const sub1 = PERSONALITY_NAMES[props.result.subPersonalities[0]]
  const sub2 = PERSONALITY_NAMES[props.result.subPersonalities[1]]
  const text = `【共鸣人格IP打造系统】我的主人格是「${master}」，辅人格是「${sub1}」和「${sub2}」。快来测测你的九色人格！`

  uni.setClipboardData({
    data: text,
    success: () => {
      uni.showToast({ title: '分享文案已复制', icon: 'none' })
    },
  })
}

function close() {
  emit('close')
}
</script>

<style lang="scss" scoped>
.poster-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.poster-canvas {
  border-radius: $radius-lg;
  margin-bottom: $spacing-lg;
}

.poster-actions {
  display: flex;
  gap: $spacing-md;
}

.btn-save {
  background: linear-gradient(135deg, $gold-bright, $gold-deep);
  padding: $spacing-sm $spacing-xl;
  border-radius: $radius-full;
}

.btn-save text {
  color: $ocean-deep;
  font-size: $font-size-sm;
  font-weight: bold;
}

.btn-share {
  background: rgba(255, 255, 255, 0.2);
  padding: $spacing-sm $spacing-xl;
  border-radius: $radius-full;
}

.btn-share text {
  color: $text-white;
  font-size: $font-size-sm;
}

.btn-close {
  background: rgba(255, 255, 255, 0.1);
  padding: $spacing-sm $spacing-xl;
  border-radius: $radius-full;
}

.btn-close text {
  color: rgba(255, 255, 255, 0.6);
  font-size: $font-size-sm;
}
</style>
