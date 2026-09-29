<template>
  <!-- 1단계 풀이 전 광고 unlock
       10초 카운트다운 + 링크프라이스 카드 4개, 카드 클릭 시 바로 진행 -->
  <v-dialog v-model="dialogModel" max-width="520px" persistent>
    <v-card class="unlock-card">
      <!-- 헤더: MBTI 맞춤 풀이 준비 -->
      <div class="unlock-header">
        <div class="unlock-title">
          <span class="sparkle">💫</span>
          {{ mbtiHeadline }}
        </div>
        <div class="unlock-sub">
          {{ countdown > 0 ? `${countdown}초 후 자동으로 시작돼` : '풀이를 시작할게...' }}
        </div>
      </div>

      <!-- 광고 카드 4개 (클릭하면 카운트다운 스킵 + 즉시 1단계 시작) -->
      <div class="merchant-grid">
        <a
          v-for="m in merchants"
          :key="m.id"
          :href="buildUrl(m.id)"
          target="_blank"
          rel="noopener sponsored"
          class="merchant-card"
          @click="handleCardClick(m)"
        >
          <span class="merchant-emoji">{{ m.emoji }}</span>
          <span class="merchant-name">{{ m.name }}</span>
          <span class="merchant-desc">{{ m.desc }}</span>
        </a>
      </div>

      <div class="sponsor-label">sponsored · 클릭하면 풀이가 바로 시작돼</div>

      <!-- 건너뛰기 버튼 (작게) -->
      <div class="unlock-footer">
        <button class="skip-btn" @click="handleSkip">건너뛰기</button>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'

interface Merchant { id: string; name: string; emoji: string; desc: string }

interface Props {
  modelValue: boolean
  category?: 'love' | 'family' | 'career' | 'money' | 'self' | 'daily'
  userMbti?: string
  countdownSeconds?: number
}

const props = withDefaults(defineProps<Props>(), {
  category: 'daily',
  userMbti: '',
  countdownSeconds: 10,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'unlock': []  // 1단계 시작 신호 (부모가 받아서 진행)
  'ad-click': [merchant: Merchant]
}>()

const dialogModel = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const AFFILIATE_ID = 'A100704705'
const buildUrl = (merchantId: string, linkId = '0000') =>
  `https://click.linkprice.com/click.php?m=${merchantId}&a=${AFFILIATE_ID}&l=${linkId}`

// 카운트다운
const countdown = ref(props.countdownSeconds)
const progressPercent = computed(() => {
  return ((props.countdownSeconds - countdown.value) / props.countdownSeconds) * 100
})

let timer: number | null = null

const startCountdown = () => {
  countdown.value = props.countdownSeconds
  if (timer) clearInterval(timer)
  timer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      stopCountdown()
      triggerUnlock()
    }
  }, 1000)

  // GA 이벤트
  if (typeof (window as any).gtag === 'function') {
    ;(window as any).gtag('event', 'ad_countdown_start', { category: props.category })
  }
}

const stopCountdown = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const triggerUnlock = () => {
  stopCountdown()
  dialogModel.value = false
  emit('unlock')
}

const handleCardClick = (m: Merchant) => {
  // 광고 클릭 시 카운트다운 스킵하고 1단계 바로 시작
  emit('ad-click', m)
  if (typeof (window as any).gtag === 'function') {
    ;(window as any).gtag('event', 'ad_card_click', {
      merchant_id: m.id, merchant_name: m.name, category: props.category,
    })
  }
  // 새 탭에서 광고 확인할 여유를 주려고 약간 늦게 unlock
  setTimeout(() => triggerUnlock(), 500)
}

const handleSkip = () => {
  // 강제감 줄이려고 건너뛰기 허용
  if (typeof (window as any).gtag === 'function') {
    ;(window as any).gtag('event', 'ad_countdown_skip', { category: props.category })
  }
  triggerUnlock()
}

// 모달 열릴 때 카운트다운 시작
watch(() => props.modelValue, (open) => {
  if (open) {
    startCountdown()
  } else {
    stopCountdown()
  }
})

onUnmounted(() => {
  stopCountdown()
})

// MBTI 헤드라인
const mbtiHeadline = computed(() => {
  if (props.userMbti) {
    return `${props.userMbti}에 맞춘 풀이를 준비 중이에요`
  }
  return '너에게 맞춘 풀이를 준비 중이에요'
})

// 카테고리별 머천트 (4개)
const MERCHANTS_BY_CATEGORY: Record<string, Merchant[]> = {
  love: [
    { id: 'clubclio',   name: '클리오',       emoji: '💄', desc: '오늘은 좀 예쁜 입술로' },
    { id: 'yes24',      name: 'YES24',        emoji: '📚', desc: '마음 풀어주는 책' },
    { id: 'cjbrand',    name: 'CJ더마켓',     emoji: '🍰', desc: '디저트로 위로받기' },
    { id: 'myrealtrip', name: '마이리얼트립', emoji: '✈️', desc: '주말에 짧게 떠나볼까' },
  ],
  family: [
    { id: 'clubclio',   name: '클리오',       emoji: '🛁', desc: '오늘은 너 위해 작게라도' },
    { id: 'yes24',      name: 'YES24',        emoji: '📓', desc: '거리감 배우는 책 한 권' },
    { id: 'cjbrand',    name: 'CJ더마켓',     emoji: '🍵', desc: '달콤한 한 입으로 풀기' },
    { id: 'myrealtrip', name: '마이리얼트립', emoji: '✈️', desc: '잠깐 거리 두는 시간' },
  ],
  career: [
    { id: 'yes24',      name: 'YES24',        emoji: '📘', desc: '결심을 책으로 시작' },
    { id: 'myrealtrip', name: '마이리얼트립', emoji: '🌏', desc: '머리 식히는 짧은 여행' },
    { id: 'arket',      name: 'ARKET',        emoji: '👔', desc: '면접·새 출발 룩' },
    { id: 'udemy',      name: 'Udemy',        emoji: '💻', desc: '실력 한 단계 올리기' },
  ],
  money: [
    { id: 'mycredit1', name: 'NICE지키미', emoji: '🔐', desc: '무료 신용조회' },
    { id: 'allcredit', name: '올크레딧',   emoji: '💳', desc: '내 신용점수 확인' },
    { id: 'yes24',     name: 'YES24',      emoji: '📕', desc: '돈 공부 시작' },
    { id: 'gmarket',   name: 'G마켓',      emoji: '🛒', desc: '알뜰 쇼핑' },
  ],
  self: [
    { id: 'clubclio', name: '클리오',   emoji: '💅', desc: '오늘 너의 컬러' },
    { id: 'iherb',    name: '아이허브', emoji: '💊', desc: '몸부터 챙기기' },
    { id: 'yes24',    name: 'YES24',    emoji: '📓', desc: '나를 채우는 책' },
    { id: 'arket',    name: 'ARKET',    emoji: '🧥', desc: '나에게 선물하는 옷' },
  ],
  daily: [
    { id: 'cjbrand',  name: 'CJ더마켓', emoji: '🍱', desc: '부모님 식사 챙기기' },
    { id: 'pulmuone', name: '풀무원',   emoji: '🥦', desc: '식탁 든든하게' },
    { id: 'soomgo',   name: '숨고',     emoji: '🔧', desc: '집 손볼 거 한 번에' },
    { id: 'iherb',    name: '아이허브', emoji: '💊', desc: '온 가족 영양제' },
  ],
}

const merchants = computed(() => MERCHANTS_BY_CATEGORY[props.category] || MERCHANTS_BY_CATEGORY.daily)
</script>

<style scoped>
.unlock-card {
  padding: 24px 20px 20px;
  border-radius: 16px;
}

.unlock-header {
  text-align: center;
  margin-bottom: 20px;
}

.unlock-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 6px;
}

.sparkle {
  font-size: 1.3rem;
}

.unlock-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
  opacity: 0.85;
}

.merchant-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}

.merchant-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 14px 8px;
  border-radius: 10px;
  background: var(--card-bg-alt, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.merchant-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.merchant-emoji {
  font-size: 1.5rem;
}

.merchant-name {
  font-size: 0.82rem;
  font-weight: 600;
}

.merchant-desc {
  font-size: 0.68rem;
  color: var(--text-secondary);
  opacity: 0.8;
  text-align: center;
  line-height: 1.3;
}

.sponsor-label {
  text-align: center;
  font-size: 0.7rem;
  color: var(--text-secondary);
  opacity: 0.6;
  margin-bottom: 12px;
}

.unlock-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skip-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.78rem;
  opacity: 0.6;
  cursor: pointer;
  align-self: flex-end;
  padding: 4px 8px;
}

.skip-btn:hover {
  opacity: 1;
  text-decoration: underline;
}

.progress-bar {
  width: 100%;
  height: 3px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffd700, #ff8c00);
  transition: width 1s linear;
}
</style>
