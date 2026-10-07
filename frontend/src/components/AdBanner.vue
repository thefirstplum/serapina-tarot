<template>
  <div class="ad-banner-container" v-if="isVisible">
    <div :id="adSlotId" class="ad-slot">
      <!-- 광고가 차단되지 않았을 때만 광고 표시 -->
      <template v-if="!adBlocked">
        <!-- 샘플 광고 (디버깅용) -->
        <div v-if="showSampleAd" class="sample-ad">
          <div class="sample-ad-content">
            <span class="sample-ad-label">광고</span>
            <span class="sample-ad-text">🎯 애드핏 광고 영역 (샘플)</span>
          </div>
        </div>

        <!-- 카카오 애드핏 광고 -->
        <ins v-else
             :key="`adfit-${adKey}`"
             class="kakao_ad_area"
             style="display:none;width:100%;"
             :data-ad-unit="adfitUnit"
             :data-ad-width="adfitWidth"
             :data-ad-height="adfitHeight"></ins>
      </template>

      <!-- 광고 차단 시 대체 콘텐츠 -->
      <div v-else class="fallback-content">
        <!-- 자체 프로모션 -->
        <div v-if="fallbackType === 'promotion'" class="promo-content">
          <div class="promo-icon">✨</div>
          <div class="promo-text">
            <div class="promo-title">세라피나 타로, 친구에게도 공유해봐</div>
            <div class="promo-subtitle">친구들이랑 같이 타로의 지혜를 나눠봐</div>
          </div>
          <button @click="shareApp" class="share-btn">
            <span class="share-icon">📤</span>
          </button>
        </div>

        <!-- 타로 팁 -->
        <div v-else class="tarot-tip">
          <img src="/icons/symbol-64.png" class="tip-icon" alt="타로" width="32" height="32" />
          <div class="tip-content">
            <div class="tip-label">오늘의 타로 카드</div>
            <div class="tip-card">{{ dailyCard.name }}</div>
            <div class="tip-meaning">{{ dailyCard.meaning }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

interface Props {
  adSlotId: string
  adFormat?: 'banner' | 'rectangle' | 'responsive'
  modelValue?: boolean
  showSampleAd?: boolean  // true면 샘플 광고 표시
  adfitUnit?: string
  adfitWidth?: string
  adfitHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  adFormat: 'banner',
  modelValue: true,
  showSampleAd: false,
  adfitUnit: 'DAN-RGx7AuIcnkcCVE57',
  adfitWidth: '320',
  adfitHeight: '50',
})

// 프로덕션 환경인지 확인
const isProduction = window.location.hostname === 'serapina.kr' ||
                     window.location.hostname === 'www.serapina.kr'

// 샘플 광고 표시 여부 (props가 명시적으로 설정되지 않았으면 개발 환경에서 샘플 표시)
const showSampleAd = computed(() => {
  // props에서 명시적으로 설정된 경우 그 값 사용
  if (props.showSampleAd !== undefined) {
    return props.showSampleAd
  }
  // 아니면 개발 환경에서만 샘플 표시
  return !isProduction
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'ad-loaded': []
  'ad-failed': []
}>()

const isVisible = ref(props.modelValue)
const adKey = ref(Date.now())
// 개발 환경에서는 기본적으로 대체 콘텐츠 표시 (실제 광고가 로드되면 false로 변경)
const adBlocked = ref(!isProduction)
const fallbackType = ref<'promotion' | 'tip'>('promotion')

// 타이머 ID 저장
let checkTimeout1: number | null = null
let checkTimeout2: number | null = null
let rotationInterval: number | null = null

// 타로 카드 데이터 (간단한 버전)
const tarotCards = [
  { name: '바보', meaning: '새로운 시작을 의미합니다' },
  { name: '마법사', meaning: '의지와 창조력을 상징합니다' },
  { name: '여사제', meaning: '내적 지혜와 직감을 나타냅니다' },
  { name: '여황제', meaning: '창조와 양육을 의미합니다' },
  { name: '황제', meaning: '리더십과 질서를 상징합니다' },
  { name: '교황', meaning: '전통과 가르침을 나타냅니다' },
  { name: '연인', meaning: '사랑과 선택의 갈림길을 의미합니다' },
  { name: '전차', meaning: '의지력과 성취를 상징합니다' },
  { name: '힘', meaning: '내적 힘과 용기를 나타냅니다' },
  { name: '은둔자', meaning: '성찰과 내적 탐구를 의미합니다' },
  { name: '운명의 바퀴', meaning: '변화와 순환을 상징합니다' },
  { name: '정의', meaning: '균형과 공정함을 나타냅니다' },
  { name: '매달린 사람', meaning: '희생과 깨달음을 의미합니다' },
  { name: '죽음', meaning: '변화와 재생을 상징합니다' },
  { name: '절제', meaning: '균형과 절제를 나타냅니다' },
  { name: '악마', meaning: '유혹과 속박을 의미합니다' },
  { name: '탑', meaning: '갑작스런 변화와 깨달음을 상징합니다' },
  { name: '별', meaning: '희망과 영감을 나타냅니다' },
  { name: '달', meaning: '환상과 불안을 의미합니다' },
  { name: '태양', meaning: '성공과 기쁨을 상징합니다' },
  { name: '심판', meaning: '재생과 구원을 나타냅니다' },
  { name: '세계', meaning: '성취와 완성을 의미합니다' }
]

// 오늘의 카드 선택 (날짜 기반)
const dailyCard = computed(() => {
  const today = new Date()
  const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / 86400000)
  return tarotCards[dayOfYear % tarotCards.length]
})

// 앱 공유 함수
const shareApp = async () => {
  const shareData = {
    title: '세라피나 타로',
    text: '타로 AI 상담으로 네 고민, 같이 풀어보자',
    url: window.location.origin
  }

  try {
    if (navigator.share) {
      await navigator.share(shareData)
    } else {
      // 공유 API 미지원 시 클립보드 복사
      await navigator.clipboard.writeText(window.location.origin)
      alert('링크 복사됐어!')
    }
  } catch (err) {
    console.warn('공유 실패:', err)
  }
}

watch(() => props.modelValue, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    // 광고가 다시 표시될 때 새로운 키로 강제 리렌더링
    adKey.value = Date.now()
  }
})

onMounted(() => {
  loadAd()

  // 광고 차단 감지 (3초 후, 광고 로드 충분한 시간)
  checkTimeout1 = window.setTimeout(() => {
    if (isVisible.value) checkAdBlock()
  }, 3000)

  // 추가 체크 (5초 후, 재확인)
  checkTimeout2 = window.setTimeout(() => {
    if (isVisible.value) checkAdBlock()
  }, 5000)

  // 대체 콘텐츠 타입 교체 (10초마다)
  rotationInterval = window.setInterval(() => {
    if (isVisible.value && adBlocked.value) {
      fallbackType.value = fallbackType.value === 'promotion' ? 'tip' : 'promotion'
    }
  }, 10000)
})

const checkAdBlock = () => {
  const adSlot = document.getElementById(props.adSlotId)
  if (!adSlot) {
    console.warn('광고 슬롯을 찾을 수 없습니다')
    return
  }

  // 카카오 애드핏 광고 로드 확인
  const kakaoAd = adSlot.querySelector('.kakao_ad_area')
  const adDisplay = kakaoAd ? window.getComputedStyle(kakaoAd).display : 'none'
  if (kakaoAd && adDisplay !== 'none' && kakaoAd.clientHeight > 0) {
    adBlocked.value = false
  } else {
    adBlocked.value = true
  }
}

const loadAd = () => {
  // 카카오 애드핏 스크립트가 이미 로드되어 있는지 확인
  const existingScript = document.querySelector('script[src*="ba.min.js"]')

  if (existingScript) {
    // 스크립트가 이미 있으면 스크립트를 다시 추가하여 강제 재실행
    // DOM 요소를 제거하지 않고 새 스크립트만 추가
    setTimeout(() => {
      const adElement = document.querySelector(`#${props.adSlotId} .kakao_ad_area`)
      if (adElement) {
        const display = window.getComputedStyle(adElement).display
        if (display === 'none') {
          // 기존 스크립트는 그대로 두고 새 스크립트 추가 (중복 실행으로 강제 렌더링)
          const newScript = document.createElement('script')
          newScript.async = true
          newScript.type = 'text/javascript'
          newScript.charset = 'utf-8'
          newScript.src = 'https://t1.daumcdn.net/kas/static/ba.min.js'
          document.body.appendChild(newScript)
        }
      } else {
        console.warn('광고 엘리먼트를 찾을 수 없음')
      }
      emit('ad-loaded')
    }, 100)
    return
  }

  // 스크립트가 없으면 새로 로드
  const script = document.createElement('script')
  script.async = true
  script.type = 'text/javascript'
  script.charset = 'utf-8'
  script.src = 'https://t1.daumcdn.net/kas/static/ba.min.js'
  script.onload = () => {
    emit('ad-loaded')
  }
  script.onerror = () => {
    console.error('애드핏 광고 로드 실패')
    adBlocked.value = true
    emit('ad-failed')
  }
  // body 태그 하단에 추가 (공식 권장)
  document.body.appendChild(script)
}

onUnmounted(() => {
  // 모든 타이머 정리
  if (checkTimeout1) window.clearTimeout(checkTimeout1)
  if (checkTimeout2) window.clearTimeout(checkTimeout2)
  if (rotationInterval) window.clearInterval(rotationInterval)

  const adSlot = document.getElementById(props.adSlotId)
  if (adSlot) {
    adSlot.innerHTML = ''
  }
})
</script>

<style scoped>
.ad-banner-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  margin: 0;
  position: relative;
  background: transparent;
}

.ad-banner-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    var(--border-color) 20%,
    var(--border-color) 80%,
    transparent
  );
  opacity: 0.3;
}

.ad-slot {
  width: 100%;
  max-width: 100%;
  min-height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

@media (min-width: 768px) {
  .ad-slot {
    max-width: 728px;
    min-height: 90px;
  }
}

/* 샘플 광고 스타일 */
.sample-ad {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.sample-ad-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sample-ad-label {
  background: var(--border-color);
  color: var(--text-primary);
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.sample-ad-text {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 600;
}

@media (min-width: 768px) {
  .sample-ad {
    height: 90px;
  }

  .sample-ad-text {
    font-size: 1.1rem;
  }
}

/* 광고 차단 시 대체 콘텐츠 스타일 */
.fallback-content {
  width: 100%;
  height: 50px;
  display: flex;
  align-items: center;
}

/* 자체 프로모션 스타일 */
.promo-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  background: transparent;
  width: 100%;
  height: 100%;
}

.promo-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.promo-text {
  flex: 1;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.promo-title {
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.promo-subtitle {
  font-size: 0.7rem;
  opacity: 0.85;
  line-height: 1.3;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.share-btn {
  background: transparent;
  border: none;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.share-btn:hover {
  transform: translateY(-1px) scale(1.1);
}

.share-icon {
  font-size: 1rem;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

/* 타로 팁 스타일 */
.tarot-tip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  background: transparent;
  width: 100%;
  height: 100%;
}

.tip-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
  flex-shrink: 0;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.tip-content {
  flex: 1;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.tip-label {
  font-size: 0.65rem;
  opacity: 0.85;
  font-weight: 500;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.tip-card {
  font-size: 0.9rem;
  font-weight: 700;
  line-height: 1.2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.tip-meaning {
  font-size: 0.7rem;
  opacity: 0.85;
  line-height: 1.3;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

@media (min-width: 768px) {
  .fallback-content {
    height: 90px;
  }

  .promo-content,
  .tarot-tip {
    gap: 16px;
    padding: 0 20px;
  }

  .promo-icon,
  .tip-icon {
    font-size: 2rem;
  }

  .promo-title {
    font-size: 0.95rem;
  }

  .promo-subtitle {
    font-size: 0.75rem;
  }

  .tip-label {
    font-size: 0.7rem;
  }

  .tip-card {
    font-size: 1rem;
  }

  .tip-meaning {
    font-size: 0.8rem;
  }

  .share-btn {
    width: 40px;
    height: 40px;
  }

  .share-icon {
    font-size: 1.2rem;
  }
}
</style>
