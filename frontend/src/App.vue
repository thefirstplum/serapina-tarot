<template>
  <v-app>
    <v-main>
      <router-view />
      <!-- 공통 풋터 (AdSense 필수: About·Contact·Privacy·Terms 링크 + 면책) -->
      <AppFooter v-if="showFooter" />
    </v-main>
    <!-- PWA 설치 유도 배너 (모든 페이지 위 fixed) -->
    <PWAInstallBanner />
    <!-- 위기 신호 감지 시 안내 배너 (자살예방·정신건강위기) -->
    <CrisisInfoBanner />
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import PWAInstallBanner from '@/components/PWAInstallBanner.vue'
import AppFooter from '@/components/AppFooter.vue'
import CrisisInfoBanner from '@/components/CrisisInfoBanner.vue'

const route = useRoute()
// 카드 뽑기·로딩 중에는 풋터 숨김 (UX 방해)
const showFooter = computed(() => {
  return !['reading', 'chat'].includes(String(route.name))
})
</script>

<style>
body, #app {
  background-color: #F9F9F7;
}

.v-application {
  background: transparent !important;
}
</style>