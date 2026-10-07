<template>
  <div class="today-page">
    <!-- 배경 -->
    <div class="bg-elements">
      <div class="bg-orb orb-1"></div>
      <div class="bg-orb orb-2"></div>
      <div class="bg-orb orb-3"></div>
    </div>
    <div class="stars-container">
      <div v-for="n in 40" :key="'star-'+n" class="star" :style="starStyle(n)"></div>
    </div>

    <!-- Header -->
    <header class="today-header">
      <div class="header-content">
        <div class="header-left" @click="goToPage('/')">
          <img src="/icons/symbol-64.png" class="header-logo" alt="세라피나" />
          <h1 class="app-title">세라피나</h1>
        </div>
        <div class="header-actions">
          <v-btn icon variant="text" @click="goToPage('/reading')" class="header-icon-btn">
            <v-icon>mdi-cards-playing-outline</v-icon>
          </v-btn>
        </div>
      </div>
    </header>

    <main class="today-main">
      <!-- 1. MBTI 선택 -->
      <section v-if="stage === 'select'" class="stage stage-select">
        <p class="section-badge">{{ todayLabel }} · 오늘의 카드</p>
        <h2 class="section-title">
          어디 보자,<br>
          <span class="title-gold">너의 카드</span> 한 장 뽑아줄게
        </h2>
        <p class="section-desc">MBTI 알려주면 너에게 딱 맞는 카드로 골라줄게</p>

        <!-- 카드 뒷면 -->
        <div class="card-back-wrap" @click="scrollToMbti">
          <div class="card-back">
            <div class="card-back-border">
              <div class="card-back-pattern">
                <div class="card-back-symbol">
                  <img src="/icons/symbol-128.png" alt="세라피나" />
                </div>
                <div class="card-back-stars">
                  <span class="cb-star cb-star-1">✦</span>
                  <span class="cb-star cb-star-2">✧</span>
                  <span class="cb-star cb-star-3">✦</span>
                  <span class="cb-star cb-star-4">✧</span>
                </div>
              </div>
            </div>
          </div>
          <p class="card-back-hint">↓ 너의 MBTI 선택</p>
        </div>

        <!-- MBTI 선택 글래스 카드 -->
        <div ref="mbtiBox" class="mbti-glass-card">
          <p class="mbti-label">너의 MBTI는?</p>
          <div class="mbti-grid">
            <button
              v-for="mbti in MBTI_LIST"
              :key="mbti"
              class="mbti-btn"
              :class="{ 'mbti-btn-saved': mbti === savedMbti }"
              @click="pickMbti(mbti)"
            >
              {{ mbti }}
            </button>
          </div>
          <p class="mbti-hint">
            MBTI 모르면? <a href="https://www.16personalities.com/ko" target="_blank" rel="noopener">5분만에 알아보기 →</a>
          </p>
        </div>
      </section>

      <!-- 2. 카드 뽑는 중 -->
      <section v-else-if="stage === 'drawing'" class="stage stage-drawing">
        <p class="drawing-text">너의 카드를 꺼내는 중…</p>
        <div class="card-flipper">
          <div class="card-flip-inner" :class="{ flipped: cardFlipped }">
            <div class="card-flip-front">
              <div class="card-back">
                <div class="card-back-border">
                  <div class="card-back-pattern">
                    <div class="card-back-symbol">
                      <img src="/icons/symbol-128.png" alt="세라피나" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-flip-back">
              <img v-if="cardImageUrl" :src="cardImageUrl" :alt="todayData?.card_name" />
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 결과 (슬라이드) -->
      <section v-else-if="stage === 'result' && todayData" class="stage stage-result">
        <div class="result-top-bar">
          <button class="back-btn" @click="resetMbti">
            <v-icon size="16">mdi-arrow-left</v-icon>
            <span>다른 MBTI</span>
          </button>
          <span class="result-mbti-tag">{{ selectedMbti }} · {{ todayData.trait }}</span>
        </div>

        <!-- 카드 이미지 -->
        <div class="result-card-image-wrap">
          <img :src="cardImageUrl" :alt="todayData.card_name" class="result-card-image" />
          <p class="result-card-name">{{ todayData.card_name }}</p>
        </div>

        <!-- 슬라이드 -->
        <div class="slides-container"
             @touchstart="onTouchStart"
             @touchmove="onTouchMove"
             @touchend="onTouchEnd">
          <transition :name="slideDirection" mode="out-in">
            <div :key="slideIndex" class="slide-content">
              <p class="slide-label">{{ SLIDE_META[slideIndex].label }}</p>
              <p class="slide-text" :class="{ 'slide-cover': slideIndex === 0, 'slide-closing': slideIndex === 3 }">
                {{ slideTexts[slideIndex] }}
              </p>
            </div>
          </transition>
        </div>

        <!-- 슬라이드 컨트롤 -->
        <div class="slide-controls">
          <button class="slide-arrow" :disabled="slideIndex === 0" @click="prevSlide">
            <v-icon>mdi-chevron-left</v-icon>
          </button>
          <div class="slide-dots">
            <span
              v-for="(_, i) in SLIDE_META"
              :key="i"
              class="slide-dot"
              :class="{ active: i === slideIndex }"
              @click="goToSlide(i)"
            ></span>
          </div>
          <button class="slide-arrow" :disabled="slideIndex === 3" @click="nextSlide">
            <v-icon>mdi-chevron-right</v-icon>
          </button>
        </div>

        <!-- CTA -->
        <div class="cta-block">
          <v-btn
            color="#c9a86a"
            size="large"
            rounded="pill"
            class="cta-btn"
            block
            @click="goToPage('/reading')"
          >
            <v-icon start>mdi-cards-playing-outline</v-icon>
            내 사연으로 더 깊이 보기
          </v-btn>
          <p class="cta-sub">진짜 궁금한 거 한 줄 적어봐, 끝까지 들어줄게</p>
        </div>
      </section>

      <!-- 4. 콘텐츠 없음 -->
      <section v-else-if="stage === 'result' && !todayData" class="stage stage-empty">
        <div class="result-top-bar">
          <button class="back-btn" @click="resetMbti">
            <v-icon size="16">mdi-arrow-left</v-icon>
            <span>다른 MBTI</span>
          </button>
          <span class="result-mbti-tag">{{ selectedMbti }}</span>
        </div>

        <div class="empty-content">
          <p class="empty-emoji">🌙</p>
          <h3 class="empty-title">오늘은 다른 친구들 차례야</h3>
          <p class="empty-desc">
            {{ selectedMbti }} 차례도 곧 와.<br>
            오늘은 이 친구들 카드 한번 볼래?
          </p>
          <div class="empty-todays-list">
            <button
              v-for="m in todayMbtis"
              :key="m"
              class="empty-mbti-chip"
              @click="pickMbti(m)"
            >
              {{ m }} →
            </button>
          </div>

          <div class="empty-or">또는</div>

          <v-btn
            color="#c9a86a"
            size="large"
            rounded="pill"
            class="cta-btn"
            block
            @click="goToPage('/reading')"
          >
            <v-icon start>mdi-cards-playing-outline</v-icon>
            내 사연으로 카드 받기
          </v-btn>
        </div>
      </section>
    </main>

    <footer class="today-footer">
      <p>© 세라피나 · 타로 AI · 매일 너의 카드 한 장</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const MBTI_LIST = [
  'ENFP', 'ENFJ', 'ENTP', 'ENTJ',
  'ESFP', 'ESFJ', 'ESTP', 'ESTJ',
  'INFP', 'INFJ', 'INTP', 'INTJ',
  'ISFP', 'ISFJ', 'ISTP', 'ISTJ'
]

const SLIDE_META = [
  { label: '오늘의 한마디', key: 'cover' },
  { label: '진단',         key: 'diagnosis' },
  { label: '오늘 하루',     key: 'action' },
  { label: '마음 한 줄',    key: 'closing' },
]

interface TodayItem {
  date: string
  cycle_day: number
  mbti: string
  trait: string
  card_id: string
  card_name: string
  slides: {
    cover: string
    diagnosis: string
    action: string
    closing: string
  }
}

type Stage = 'select' | 'drawing' | 'result'

const stage = ref<Stage>('select')
const selectedMbti = ref<string>('')
const savedMbti = ref<string>('')
const allTodayData = ref<TodayItem[]>([])
const slideIndex = ref(0)
const slideDirection = ref<'slide-left' | 'slide-right'>('slide-left')
const cardFlipped = ref(false)
const mbtiBox = ref<HTMLElement | null>(null)

const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

function getKSTDate(): string {
  const now = new Date()
  const kst = new Date(now.getTime() + (9 * 60 + now.getTimezoneOffset()) * 60000)
  return kst.toISOString().slice(0, 10)
}

const todayDateStr = getKSTDate()

const todayLabel = computed(() => {
  const [, m, d] = todayDateStr.split('-')
  return `${parseInt(m)}월 ${parseInt(d)}일`
})

const todayData = computed(() => {
  return allTodayData.value.find(item => item.mbti === selectedMbti.value) || null
})

const todayMbtis = computed(() => allTodayData.value.map(item => item.mbti))

const slideTexts = computed(() => {
  if (!todayData.value) return ['', '', '', '']
  const s = todayData.value.slides
  return [s.cover, s.diagnosis, s.action, s.closing]
})

const cardImageUrl = computed(() => {
  if (!todayData.value) return ''
  const path = `../assets/cards/${todayData.value.card_id}.jpg`
  return cardImages[path] || cardImages['../assets/cards/maj00.jpg'] || ''
})

async function loadTodayData() {
  try {
    const res = await fetch(`/today-data/${todayDateStr}.json?v=${Date.now()}`)
    if (res.ok) {
      allTodayData.value = await res.json()
    } else {
      allTodayData.value = []
    }
  } catch (e) {
    console.error('오늘 콘텐츠 로딩 실패', e)
    allTodayData.value = []
  }
}

async function enterMbti(mbti: string) {
  selectedMbti.value = mbti
  localStorage.setItem('serapina_mbti', mbti)
  await loadTodayData()

  // 오늘 콘텐츠가 없으면 뽑기 연출 없이 빈 결과 화면
  if (!todayData.value) {
    stage.value = 'result'
    slideIndex.value = 0
    return
  }

  stage.value = 'drawing'
  cardFlipped.value = false
  await nextTick()
  setTimeout(() => { cardFlipped.value = true }, 400)
  setTimeout(() => {
    stage.value = 'result'
    slideIndex.value = 0
    slideDirection.value = 'slide-left'
  }, 1800)
}

async function pickMbti(mbti: string) {
  if (route.params.mbti !== mbti) {
    router.replace(`/today/${mbti}`)
  }
  await enterMbti(mbti)
}

function resetMbti() {
  stage.value = 'select'
  selectedMbti.value = ''
  router.replace('/today')
}

function nextSlide() {
  if (slideIndex.value < 3) {
    slideDirection.value = 'slide-left'
    slideIndex.value++
  }
}

function prevSlide() {
  if (slideIndex.value > 0) {
    slideDirection.value = 'slide-right'
    slideIndex.value--
  }
}

function goToSlide(i: number) {
  slideDirection.value = i > slideIndex.value ? 'slide-left' : 'slide-right'
  slideIndex.value = i
}

// 스와이프
let touchStartX = 0
let touchEndX = 0
function onTouchStart(e: TouchEvent) { touchStartX = e.changedTouches[0].screenX }
function onTouchMove(e: TouchEvent) { touchEndX = e.changedTouches[0].screenX }
function onTouchEnd() {
  if (touchEndX === 0) return
  const diff = touchStartX - touchEndX
  if (Math.abs(diff) < 50) { touchEndX = 0; return }
  if (diff > 0) nextSlide()
  else prevSlide()
  touchEndX = 0
}

function scrollToMbti() {
  mbtiBox.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function goToPage(path: string) { router.push(path) }

function starStyle(_n: number) {
  return {
    top: Math.random() * 100 + '%',
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 4 + 's',
    animationDuration: 2 + Math.random() * 3 + 's',
  }
}

watch(() => route.params.mbti, async (newMbti) => {
  const val = (newMbti as string)?.toUpperCase()
  if (val && MBTI_LIST.includes(val) && val !== selectedMbti.value) {
    await enterMbti(val)
  } else if (!newMbti) {
    stage.value = 'select'
  }
})

onMounted(async () => {
  const saved = localStorage.getItem('serapina_mbti')
  if (saved && MBTI_LIST.includes(saved)) savedMbti.value = saved

  const urlMbti = (route.params.mbti as string)?.toUpperCase()
  if (urlMbti && MBTI_LIST.includes(urlMbti)) {
    await enterMbti(urlMbti)
  }
})
</script>

<style scoped>
.today-page {
  min-height: 100vh;
  background:
    radial-gradient(ellipse at top, rgba(138, 44, 58, 0.18) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(201, 168, 106, 0.10) 0%, transparent 50%),
    linear-gradient(180deg, #15110e 0%, #1f1813 60%, #1a1410 100%);
  color: #ede4d3;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* 배경 */
.bg-elements {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
}
.bg-orb {
  position: absolute; border-radius: 50%;
  filter: blur(90px); opacity: 0.35;
}
.orb-1 {
  width: 380px; height: 380px;
  background: radial-gradient(circle, #c9a86a, transparent 70%);
  top: -120px; right: -80px;
}
.orb-2 {
  width: 320px; height: 320px;
  background: radial-gradient(circle, #8a2c3a, transparent 70%);
  top: 40%; left: -100px;
}
.orb-3 {
  width: 280px; height: 280px;
  background: radial-gradient(circle, #6a4a8a, transparent 70%);
  bottom: -80px; right: -50px;
}

.stars-container {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
}
.star {
  position: absolute; width: 2px; height: 2px;
  background: #f5e9cf; border-radius: 50%;
  opacity: 0; animation: twinkle 3s ease-in-out infinite;
  box-shadow: 0 0 4px #f5e9cf;
}
@keyframes twinkle {
  0%, 100% { opacity: 0; transform: scale(0.5); }
  50%      { opacity: 0.9; transform: scale(1); }
}

/* Header */
.today-header {
  position: relative; z-index: 10;
  padding: 14px 20px;
}
.header-content {
  max-width: 720px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
}
.header-left { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.header-logo { width: 28px; height: 28px; }
.app-title {
  font-size: 18px; font-weight: 600; color: #ede4d3; margin: 0;
  font-family: 'Cormorant Garamond', 'Noto Serif KR', serif;
  letter-spacing: 1px;
}
.header-icon-btn { color: #c9a86a !important; }

/* Main */
.today-main {
  position: relative; z-index: 1;
  max-width: 480px; margin: 0 auto;
  padding: 20px 20px 60px;
}
.stage { animation: fadeInUp 0.5s ease; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 1. 선택 화면 */
.stage-select { text-align: center; }
.section-badge {
  display: inline-block;
  font-size: 12px; color: #c9a86a; letter-spacing: 2px;
  padding: 6px 18px; margin-bottom: 24px;
  border: 1px solid rgba(201,168,106,0.35);
  border-radius: 999px;
  background: rgba(201,168,106,0.06);
  text-transform: uppercase;
}
.section-title {
  font-family: 'Noto Serif KR', serif;
  font-size: 32px; font-weight: 500; line-height: 1.45;
  margin: 0 0 14px;
  color: #ede4d3;
  letter-spacing: -0.5px;
}
.title-gold {
  color: #c9a86a;
  font-weight: 600;
  text-shadow: 0 0 20px rgba(201,168,106,0.4);
}
.section-desc {
  font-size: 14px; line-height: 1.7;
  color: #b8a890; margin-bottom: 36px;
}

/* 카드 뒷면 */
.card-back-wrap { margin-bottom: 44px; cursor: pointer; }
.card-back {
  width: 200px; height: 320px; margin: 0 auto;
  position: relative;
  border-radius: 14px;
  background:
    radial-gradient(circle at center, #3a2540 0%, #1f1428 60%, #15101a 100%);
  box-shadow:
    0 20px 60px rgba(0,0,0,0.5),
    0 0 0 1px rgba(201,168,106,0.25),
    inset 0 0 30px rgba(0,0,0,0.4);
  transition: transform 0.3s ease;
}
.card-back-wrap:hover .card-back { transform: translateY(-4px); }

.card-back-border {
  position: absolute; inset: 10px;
  border: 1px solid rgba(201,168,106,0.5);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.card-back-pattern {
  position: relative;
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
}
.card-back-symbol {
  width: 60%; height: 60%;
  display: flex; align-items: center; justify-content: center;
  opacity: 0.85;
  filter: drop-shadow(0 0 18px rgba(201,168,106,0.5));
}
.card-back-symbol img {
  width: 100%; height: 100%; object-fit: contain;
  filter: brightness(1.1) saturate(0.8);
}
.card-back-stars { position: absolute; inset: 0; pointer-events: none; }
.cb-star {
  position: absolute;
  color: #c9a86a;
  text-shadow: 0 0 8px rgba(201,168,106,0.6);
  font-size: 18px;
  animation: cbStarPulse 2.5s ease-in-out infinite;
}
.cb-star-1 { top: 12px; left: 12px; }
.cb-star-2 { top: 12px; right: 12px; animation-delay: 0.5s; font-size: 14px; }
.cb-star-3 { bottom: 12px; right: 12px; animation-delay: 1s; }
.cb-star-4 { bottom: 12px; left: 12px; animation-delay: 1.5s; font-size: 14px; }
@keyframes cbStarPulse {
  0%, 100% { opacity: 0.4; }
  50%      { opacity: 1; }
}

.card-back-hint {
  margin-top: 18px;
  font-size: 13px;
  color: #c9a86a;
  letter-spacing: 1px;
  animation: bounce 2s ease-in-out infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); opacity: 0.7; }
  50%      { transform: translateY(6px); opacity: 1; }
}

/* MBTI 글래스 카드 */
.mbti-glass-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(201,168,106,0.18);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 22px;
  padding: 28px 20px;
  box-shadow: 0 16px 60px rgba(0,0,0,0.3);
}
.mbti-label {
  font-family: 'Noto Serif KR', serif;
  font-size: 18px; font-weight: 500;
  color: #ede4d3;
  margin-bottom: 20px;
  letter-spacing: -0.3px;
}
.mbti-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.mbti-btn {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  color: #ede4d3;
  padding: 16px 4px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}
.mbti-btn:hover {
  background: rgba(201,168,106,0.13);
  border-color: rgba(201,168,106,0.6);
  color: #f5e9cf;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(201,168,106,0.15);
}
.mbti-btn-saved {
  background: rgba(201,168,106,0.18);
  border-color: rgba(201,168,106,0.6);
  color: #f5e9cf;
}
.mbti-btn-saved::before {
  content: '★ ';
  font-size: 10px;
  color: #c9a86a;
}
.mbti-hint {
  margin-top: 20px;
  font-size: 12px;
  color: #8a8070;
}
.mbti-hint a {
  color: #c9a86a;
  text-decoration: none;
  border-bottom: 1px dashed rgba(201,168,106,0.4);
}
.mbti-hint a:hover { color: #f5e9cf; }

/* 2. 카드 뽑는 중 */
.stage-drawing { text-align: center; padding-top: 30px; }
.drawing-text {
  font-family: 'Noto Serif KR', serif;
  font-size: 18px;
  color: #c9a86a;
  margin-bottom: 36px;
  letter-spacing: 0.5px;
  animation: fadeBlink 2s ease-in-out infinite;
}
@keyframes fadeBlink {
  0%, 100% { opacity: 0.6; }
  50%      { opacity: 1; }
}
.card-flipper {
  perspective: 1200px;
  width: 220px; height: 350px;
  margin: 0 auto;
}
.card-flip-inner {
  position: relative; width: 100%; height: 100%;
  transform-style: preserve-3d;
  transition: transform 1.1s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.card-flip-inner.flipped { transform: rotateY(180deg); }
.card-flip-front, .card-flip-back {
  position: absolute; inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 14px;
}
.card-flip-front .card-back { width: 100%; height: 100%; }
.card-flip-back {
  transform: rotateY(180deg);
  background: #1a1410;
  box-shadow: 0 24px 70px rgba(0,0,0,0.6);
}
.card-flip-back img {
  width: 100%; height: 100%;
  object-fit: cover;
  border-radius: 14px;
}

/* 3. 결과 */
.stage-result { padding-bottom: 20px; }
.result-top-bar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 24px;
}
.back-btn {
  background: transparent; border: none;
  color: #b8a890;
  display: flex; align-items: center; gap: 4px;
  cursor: pointer; font-size: 13px; font-family: inherit;
  padding: 6px 8px;
}
.back-btn:hover { color: #ede4d3; }
.result-mbti-tag {
  font-size: 12px; color: #c9a86a; letter-spacing: 1px;
  padding: 4px 12px;
  background: rgba(201,168,106,0.1);
  border: 1px solid rgba(201,168,106,0.3);
  border-radius: 999px;
}

.result-card-image-wrap {
  text-align: center;
  margin-bottom: 32px;
}
.result-card-image {
  width: 240px; max-width: 70%;
  border-radius: 14px;
  box-shadow:
    0 24px 70px rgba(0,0,0,0.6),
    0 0 0 1px rgba(201,168,106,0.25);
  animation: cardEnter 0.6s ease;
}
@keyframes cardEnter {
  from { opacity: 0; transform: translateY(20px) rotateY(-15deg); }
  to   { opacity: 1; transform: translateY(0) rotateY(0); }
}
.result-card-name {
  margin-top: 14px;
  font-family: 'Noto Serif KR', serif;
  font-size: 15px;
  color: #c9a86a;
  letter-spacing: 1px;
}

/* 슬라이드 */
.slides-container {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(201,168,106,0.15);
  border-radius: 18px;
  padding: 32px 26px;
  min-height: 200px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  touch-action: pan-y;
}
.slide-content {
  width: 100%;
  text-align: center;
}
.slide-label {
  font-size: 11px;
  color: #c9a86a;
  letter-spacing: 2.5px;
  margin-bottom: 14px;
  text-transform: uppercase;
}
.slide-text {
  font-family: 'Noto Serif KR', serif;
  font-size: 16px;
  line-height: 1.85;
  color: #ede4d3;
  white-space: pre-line;
  margin: 0;
  letter-spacing: -0.2px;
}
.slide-cover {
  font-size: 22px;
  font-weight: 500;
  color: #f5e9cf;
}
.slide-closing {
  color: #c9a86a;
  font-style: italic;
}

/* 슬라이드 트랜지션 */
.slide-left-enter-active, .slide-left-leave-active,
.slide-right-enter-active, .slide-right-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1);
}
.slide-left-enter-from { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to   { opacity: 0; transform: translateX(-40px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-40px); }
.slide-right-leave-to   { opacity: 0; transform: translateX(40px); }

/* 슬라이드 컨트롤 */
.slide-controls {
  display: flex; align-items: center; justify-content: space-between;
  margin: 20px 0 28px;
}
.slide-arrow {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9a86a;
  width: 40px; height: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.slide-arrow:hover:not(:disabled) {
  background: rgba(201,168,106,0.13);
  border-color: rgba(201,168,106,0.4);
}
.slide-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.slide-dots { display: flex; gap: 10px; }
.slide-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(255,255,255,0.15);
  cursor: pointer;
  transition: all 0.2s ease;
}
.slide-dot.active {
  background: #c9a86a;
  width: 26px;
  border-radius: 4px;
  box-shadow: 0 0 8px rgba(201,168,106,0.5);
}

/* CTA */
.cta-block { text-align: center; margin-top: 12px; }
.cta-btn {
  font-weight: 600 !important;
  letter-spacing: 0.3px;
  color: #1a1410 !important;
  box-shadow: 0 8px 24px rgba(201,168,106,0.3) !important;
}
.cta-sub {
  margin-top: 14px;
  font-size: 12px;
  color: #8a8070;
}

/* 4. Empty */
.stage-empty .empty-content {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(201,168,106,0.15);
  border-radius: 22px;
  padding: 44px 26px;
  text-align: center;
  backdrop-filter: blur(12px);
}
.empty-emoji { font-size: 52px; margin-bottom: 4px; }
.empty-title {
  font-family: 'Noto Serif KR', serif;
  font-size: 22px;
  font-weight: 500;
  color: #ede4d3;
  margin: 14px 0 14px;
}
.empty-desc {
  font-size: 14px; line-height: 1.7;
  color: #b8a890;
  margin-bottom: 28px;
}
.empty-todays-list {
  display: flex; flex-wrap: wrap; gap: 10px;
  justify-content: center;
  margin-bottom: 24px;
}
.empty-mbti-chip {
  background: rgba(201,168,106,0.1);
  border: 1px solid rgba(201,168,106,0.35);
  color: #c9a86a;
  padding: 10px 18px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}
.empty-mbti-chip:hover {
  background: rgba(201,168,106,0.2);
  color: #f5e9cf;
  transform: translateY(-1px);
}
.empty-or {
  font-size: 12px;
  color: #8a8070;
  margin: 18px 0 18px;
  letter-spacing: 2px;
  position: relative;
}
.empty-or::before, .empty-or::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 60px; height: 1px;
  background: rgba(138,128,112,0.3);
}
.empty-or::before { right: calc(50% + 30px); }
.empty-or::after  { left: calc(50% + 30px); }

/* Footer */
.today-footer {
  text-align: center;
  padding: 28px 20px 36px;
  color: #6a5e50;
  font-size: 11px;
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}

/* Mobile */
@media (max-width: 480px) {
  .section-title { font-size: 26px; }
  .card-back { width: 170px; height: 272px; }
  .mbti-grid { grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .mbti-btn { padding: 14px 2px; font-size: 13px; }
  .result-card-image { width: 200px; }
  .slide-cover { font-size: 19px; }
  .slide-text { font-size: 15px; }
  .slides-container { padding: 28px 22px; min-height: 180px; }
  .card-flipper { width: 200px; height: 320px; }
}

@media (max-width: 360px) {
  .mbti-btn { padding: 12px 2px; font-size: 12px; letter-spacing: 0.3px; }
  .mbti-grid { gap: 6px; }
}
</style>
