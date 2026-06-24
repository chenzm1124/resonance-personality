<template>
  <view class="privacy-page">
    <view class="privacy-header">
      <text class="privacy-title">隐私政策</text>
      <text class="privacy-date">最后更新：2026年6月16日</text>
    </view>

    <view class="privacy-content">
      <view class="section">
        <text class="section-title">一、我们收集的信息</text>
        <view class="section-body">
          <text class="body-text">1. 微信登录信息：OpenID、昵称、头像，仅用于身份识别和结果页展示。</text>
          <text class="body-text">2. 答题数据：63道情境题评分、答题时长、人格计算结果，用于生成人格图谱。</text>
          <text class="body-text">3. 行为日志：操作事件统计，用于产品优化，不含个人敏感信息。</text>
          <text class="body-text">4. 偏好设置：音乐/动画偏好，仅本地存储。</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">二、信息使用目的</text>
        <view class="section-body">
          <text class="body-text">• 提供人格测试核心功能</text>
          <text class="body-text">• 生成个性化人格图谱与海报</text>
          <text class="body-text">• 改善产品体验与服务品质</text>
          <text class="body-text">• 保障系统安全与防欺诈</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">三、信息存储与保护</text>
        <view class="section-body">
          <text class="body-text">• 答题数据与计算结果存储在加密数据库中</text>
          <text class="body-text">• 不会向任何第三方出售或共享您的个人信息</text>
          <text class="body-text">• 您可随时删除自己的测试记录</text>
          <text class="body-text">• 账户注销后30天内自动清除所有数据</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">四、您的权利</text>
        <view class="section-body">
          <text class="body-text">• 查询权：查看自己的测试记录和结果</text>
          <text class="body-text">• 删除权：删除测试记录和个人数据</text>
          <text class="body-text">• 撤回授权：可在微信设置中取消授权</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">五、未成年人保护</text>
        <view class="section-body">
          <text class="body-text">本小程序适合所有年龄段用户使用。未满14周岁的未成年人建议在监护人指导下使用。</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">六、联系我们</text>
        <view class="section-body">
          <text class="body-text">如有隐私相关问题，请通过小程序内反馈功能联系我们。</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
.privacy-page {
  min-height: 100vh;
  background: $white-soft;
  padding: $spacing-lg;
}

.privacy-header {
  text-align: center;
  padding: $spacing-xl 0;
}

.privacy-title {
  display: block;
  font-size: $font-size-xxl;
  color: $text-primary;
  font-weight: bold;
  margin-bottom: $spacing-sm;
}

.privacy-date {
  display: block;
  font-size: $font-size-xs;
  color: $text-light;
}

.section {
  margin-bottom: $spacing-xl;
}

.section-title {
  display: block;
  font-size: $font-size-base;
  color: $text-primary;
  font-weight: bold;
  margin-bottom: $spacing-md;
}

.section-body {
  padding-left: $spacing-md;
}

.body-text {
  display: block;
  font-size: $font-size-sm;
  color: $text-light;
  line-height: 2;
}
</style>
