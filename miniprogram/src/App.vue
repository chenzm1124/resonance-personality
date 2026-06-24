<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch — 共鸣人格IP打造系统')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* 全局基础样式 — 三色体系 */
page {
  background-color: #1A5276;
  font-family: 'Source Han Sans', 'Noto Sans CJK SC', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2C3E50;
  min-height: 100vh;
}

/* 全局工具类 */
.text-gold {
  color: #F1C40F;
}

.text-white {
  color: #FFFFFF;
}

.bg-ocean {
  background-color: #1A5276;
}

.bg-ocean-light {
  background-color: #2980B9;
}

.bg-gold {
  background-color: #F1C40F;
}
</style>
