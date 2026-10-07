<template>
  <!-- 카카오 애드핏 광고 블록 (AdSense에서 교체)
       기존 호출처의 slot, format, layout 인자는 받기만 하고 애드핏 unit으로 통일 -->
  <div class="adfit-block" :class="{ 'in-article': layout === 'in-article' }" v-if="enabled">
    <div class="ad-label">광고</div>
    <ins
      :key="`adfit-${adKey}`"
      class="kakao_ad_area"
      style="display:none;"
      :data-ad-unit="adUnit"
      :data-ad-width="adWidth"
      :data-ad-height="adHeight"
    ></ins>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'

interface Props {
  slot?: string                // 옛 AdSense 슬롯 호환 (무시)
  format?: string              // 'auto' | 'rectangle' | 'fluid' | 'in-article'
  responsive?: boolean         // 옛 AdSense 호환 (무시)
  adClient?: string            // 옛 AdSense 호환 (무시)
  layout?: string              // 'in-article'
  adUnit?: string              // 카카오 애드핏 unit ID (Override 가능)
  adWidth?: string
  adHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  slot: '',
  format: 'auto',
  responsive: true,
  adClient: '',
  layout: '',
  adUnit: 'DAN-RGx7AuIcnkcCVE57',  // 카카오 애드핏 unit
  adWidth: '320',
  adHeight: '100',
})

const adKey = ref(Date.now())

// adUnit 형식(DAN-XXX)이 맞을 때만 활성화
const enabled = computed(() => {
  return props.adUnit && /^DAN-/.test(props.adUnit)
})

// format에 따라 크기 자동 조정
const adWidth = computed(() => {
  if (props.format === 'rectangle') return '300'
  if (props.layout === 'in-article') return '320'
  return props.adWidth
})

const adHeight = computed(() => {
  if (props.format === 'rectangle') return '250'
  if (props.layout === 'in-article') return '100'
  return props.adHeight
})

const adUnit = computed(() => props.adUnit)

onMounted(() => {
  if (!enabled.value) return
  // 애드핏 스크립트는 index.html에서 이미 async 로드됨
  // 컴포넌트 마운트 시 추가 트리거 (SPA 라우팅 시 광고 다시 표시)
  try {
    const script = document.createElement('script')
    script.async = true
    script.src = 'https://t1.daumcdn.net/kas/static/ba.min.js'
    document.body.appendChild(script)
  } catch (e) {
    console.warn('[애드핏] 광고 트리거 실패:', e)
  }
})
</script>

<style scoped>
.adfit-block {
  margin: 24px auto;
  text-align: center;
  max-width: 720px;
  padding: 0 16px;
}

.ad-label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-weight: 600;
  opacity: 0.7;
}

.kakao_ad_area {
  width: 100% !important;
}
</style>
