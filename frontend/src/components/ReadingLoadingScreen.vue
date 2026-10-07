<template>
  <div class="loading-screen">
    <!-- Cards Reveal -->
    <div class="cards-reveal">
      <div
        v-for="(card, index) in cards"
        :key="index"
        class="card-flip-container"
        :class="{ 'flipped': flippedCards[index] }"
        :style="{ animationDelay: `${index * 0.8}s` }"
      >
        <div class="card-position-tag">{{ cardPositions[index] }}</div>
        <div class="card-flipper">
          <div class="card-front">
            <div class="card-back-design">
              <img src="/icons/symbol-128.png" class="card-back-symbol" alt="" width="48" height="48" />
            </div>
          </div>
          <div class="card-back-face">
            <img
              :src="getCardImageUrl(card.id)"
              :alt="card.name"
              class="card-revealed-img"
              :class="{ 'reversed-img': card.reversed }"
            />
          </div>
        </div>
        <div class="card-name-tag" :class="{ 'visible': flippedCards[index] }">
          {{ card.name }}
          <span v-if="card.reversed" class="reversed-badge">{{ t('loadingScreen.reversedBadge') }}</span>
        </div>
      </div>
    </div>

    <!-- Loading Message + Progress -->
    <div class="loading-area">
      <div class="loading-sparkles">
        <span class="sparkle" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.3}s` }">✦</span>
      </div>
      <p class="loading-message">{{ currentMessage }}</p>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
      </div>
    </div>

    <!-- MBTI × 타로 상식 카드 (지루함 해소) -->
    <div class="knowledge-card" :class="{ 'visible': showKnowledge }">
      <div class="knowledge-header">
        <span class="knowledge-icon">{{ currentKnowledge.icon }}</span>
        <span class="knowledge-label">{{ currentKnowledge.label }}</span>
      </div>
      <p class="knowledge-text">{{ currentKnowledge.text }}</p>
    </div>

    <!-- 로딩 중 광고는 산만해서 넣지 않음 -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'

interface CardInfo {
  id: string
  name: string
  reversed: boolean
}

const props = defineProps<{
  cards: CardInfo[]
  cardPositions: string[]
  spreadType: string
  isReady: boolean
  userMbti?: string
}>()

const emit = defineEmits(['transition-complete'])

const { t } = useI18n()
const authStore = useAuthStore()
const isPremium = computed(() => authStore.isPremium)

const flippedCards = ref<boolean[]>([])
const currentMessageIndex = ref(0)
const progressPercent = ref(0)
const knowledgeIndex = ref(0)
const showKnowledge = ref(false)

const messages = computed(() => [
  t('loadingScreen.messages.reading'),
  t('loadingScreen.messages.energy'),
  t('loadingScreen.messages.starlight'),
  t('loadingScreen.messages.insight'),
  t('loadingScreen.messages.preparing'),
])

const currentMessage = computed(() => messages.value[currentMessageIndex.value])
const progressWidth = computed(() => `${progressPercent.value}%`)

// MBTI × 타로 콘텐츠 (한 문장에 한 의미)
const MBTI_TAROT_KNOWLEDGE: { mbti?: string; icon: string; label: string; text: string }[] = [
  { mbti: 'INFP', icon: '💧', label: 'INFP × 컵', text: 'INFP에게 컵 카드는 가장 잘 맞는 슈트야. 감정 신호를 남보다 빨리 잡아내거든.' },
  { mbti: 'INFJ', icon: '🌙', label: 'INFJ × 달', text: 'INFJ는 달 카드를 자주 마주칠 거야. 안 보이는 걸 알아채는 직관이 강하니까.' },
  { mbti: 'INTP', icon: '⚔️', label: 'INTP × 검', text: 'INTP에게 검 카드는 익숙한 도구야. 다만 그 칼이 자기를 향할 때가 있어.' },
  { mbti: 'INTJ', icon: '🔮', label: 'INTJ × 마법사', text: 'INTJ에게 마법사 카드는 자기 거울이야. 머릿속 그림을 현실로 만드는 능력이 강하거든.' },
  { mbti: 'ISFP', icon: '🌿', label: 'ISFP × 펜타클', text: 'ISFP는 펜타클 카드와 잘 맞아. 순간의 결과 감각을 진심으로 느끼는 사람이니까.' },
  { mbti: 'ISFJ', icon: '🏛️', label: 'ISFJ × 황제', text: 'ISFJ에게 황제 카드는 보호의 의미야. 묵묵히 곁에서 지켜주는 사람이라서 그래.' },
  { mbti: 'ISTP', icon: '🏇', label: 'ISTP × 전차', text: 'ISTP는 전차 카드와 잘 어울려. 말없이 정확하게 움직이는 사람이거든.' },
  { mbti: 'ISTJ', icon: '💎', label: 'ISTJ × 펜타클', text: 'ISTJ는 펜타클의 견실함을 닮았어. 화려하진 않지만 무너지지 않는 사람이지.' },
  { mbti: 'ENFP', icon: '🔥', label: 'ENFP × 완드', text: 'ENFP는 완드 카드와 통해. 시작을 두려워하지 않는 에너지를 가졌거든.' },
  { mbti: 'ENFJ', icon: '☀️', label: 'ENFJ × 태양', text: 'ENFJ는 태양 카드처럼 주변을 밝게 만들어. 그 빛, 자기 자신한테도 비춰줘.' },
  { mbti: 'ENTP', icon: '✨', label: 'ENTP × 마법사', text: 'ENTP에게 마법사 카드는 자연스러워. 도구를 새 방식으로 조합하는 데 강하니까.' },
  { mbti: 'ENTJ', icon: '👑', label: 'ENTJ × 황제', text: 'ENTJ는 황제 카드가 잘 맞아. 결단과 비전을 갖춘 사람이거든.' },
  { mbti: 'ESFP', icon: '🎉', label: 'ESFP × 완드', text: 'ESFP는 완드 카드와 통해. 지금 이 순간을 사는 활기가 강하니까.' },
  { mbti: 'ESFJ', icon: '🤝', label: 'ESFJ × 연인', text: 'ESFJ는 연인 카드와 잘 어울려. 관계 속 균형을 만드는 능력이 강하거든.' },
  { mbti: 'ESTP', icon: '⚡', label: 'ESTP × 전차', text: 'ESTP는 전차 카드처럼 망설임이 없어. 생각보다 행동이 빠른 사람이거든.' },
  { mbti: 'ESTJ', icon: '🏛️', label: 'ESTJ × 황제', text: 'ESTJ에게 황제는 자기 거울이야. 질서와 체계로 세상을 단단히 세우는 사람이니까.' },
  { icon: '🌟', label: '타로 상식', text: '메이저 아르카나는 총 22장이야. 바보부터 세계까지 인생의 큰 흐름을 그려.' },
  { icon: '💞', label: '타로 상식', text: '역방향 카드는 나쁜 게 아니야. 다른 시각으로 보라는 신호일 뿐이야.' },
  { icon: '🎴', label: '타로 상식', text: '타로 슈트는 4개야. 컵·완드·검·펜타클이 마음·열정·생각·현실을 의미해.' },
  { icon: '🌙', label: '타로 상식', text: '달 카드는 막막함의 카드야. 답이 안 보일 땐 무리하지 말고 천천히 가.' },
  { icon: '☀️', label: '타로 상식', text: '태양 카드는 가장 좋은 카드 중 하나야. 망설일 거 없이 빛으로 나가도 돼.' },
  { icon: '🔮', label: '타로 상식', text: '여사제는 직관의 카드야. 머리로 따지지 말고 마음이 먼저 안 답을 따라가.' },
]

const currentKnowledge = computed(() => {
  return MBTI_TAROT_KNOWLEDGE[knowledgeIndex.value % MBTI_TAROT_KNOWLEDGE.length]
})

// Pre-load card images
const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

const getCardImageUrl = (cardId: string) => {
  const baseId = cardId.replace('_r', '')
  const imagePath = `../assets/cards/${baseId}.jpg`
  return cardImages[imagePath] || cardImages['../assets/cards/maj00.jpg'] || ''
}

let messageInterval: ReturnType<typeof setInterval> | null = null
let progressInterval: ReturnType<typeof setInterval> | null = null
let knowledgeInterval: ReturnType<typeof setInterval> | null = null
let flipTimeouts: ReturnType<typeof setTimeout>[] = []

const pickStartingKnowledge = () => {
  // 사용자 MBTI가 있으면 본인 콘텐츠부터
  if (props.userMbti) {
    const idx = MBTI_TAROT_KNOWLEDGE.findIndex(k => k.mbti === props.userMbti)
    if (idx >= 0) return idx
  }
  return Math.floor(Math.random() * MBTI_TAROT_KNOWLEDGE.length)
}

onMounted(() => {
  // Initialize flipped state
  flippedCards.value = props.cards.map(() => false)

  // Flip cards one by one
  props.cards.forEach((_, index) => {
    const timeout = setTimeout(() => {
      flippedCards.value[index] = true
      flippedCards.value = [...flippedCards.value]
    }, 800 + index * 1000)
    flipTimeouts.push(timeout)
  })

  // Rotate loading messages
  messageInterval = setInterval(() => {
    currentMessageIndex.value = (currentMessageIndex.value + 1) % messages.value.length
  }, 3000)

  // Progress bar
  progressInterval = setInterval(() => {
    if (props.isReady) {
      progressPercent.value = 100
    } else if (progressPercent.value < 85) {
      progressPercent.value += Math.random() * 3 + 0.5
    }
  }, 500)

  // MBTI × 타로 상식: 카드 뒤집기 끝난 후(약 3초) 등장, 5초마다 회전
  knowledgeIndex.value = pickStartingKnowledge()
  setTimeout(() => { showKnowledge.value = true }, 3000)
  knowledgeInterval = setInterval(() => {
    showKnowledge.value = false
    setTimeout(() => {
      knowledgeIndex.value = (knowledgeIndex.value + 1) % MBTI_TAROT_KNOWLEDGE.length
      showKnowledge.value = true
    }, 300)
  }, 5000)
})

onUnmounted(() => {
  if (messageInterval) clearInterval(messageInterval)
  if (progressInterval) clearInterval(progressInterval)
  if (knowledgeInterval) clearInterval(knowledgeInterval)
  flipTimeouts.forEach(t => clearTimeout(t))
})

// Watch for isReady to trigger transition
const checkReady = setInterval(() => {
  if (props.isReady && progressPercent.value >= 100) {
    clearInterval(checkReady)
    setTimeout(() => {
      emit('transition-complete')
    }, 600)
  }
}, 200)

onUnmounted(() => {
  clearInterval(checkReady)
})
</script>

<style scoped>
.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 16px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Cards Reveal */
.cards-reveal {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.card-flip-container {
  perspective: 1000px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-position-tag {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  background: var(--card-bg);
  padding: 4px 14px;
  border-radius: 12px;
  margin-bottom: 10px;
  border: 1px solid var(--text-primary);
  opacity: 0;
  animation: fadeInTag 0.5s ease forwards;
  animation-delay: inherit;
}

@keyframes fadeInTag {
  to { opacity: 1; }
}

.card-flipper {
  position: relative;
  width: 110px;
  height: 189px;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.card-flip-container.flipped .card-flipper {
  transform: rotateY(180deg);
}

.card-front,
.card-back-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 0;
  overflow: hidden;
}

.card-front {
  z-index: 2;
}

.card-back-face {
  transform: rotateY(180deg);
}

.card-back-design {
  width: 100%;
  height: 100%;
  background: var(--secondary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--text-primary);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}
.card-back-design::before {
  content: '';
  position: absolute;
  inset: 4px;
  border: 1px solid rgba(26, 26, 46, 0.25);
  border-radius: 5px;
  pointer-events: none;
}

.card-back-symbol {
  width: 48px;
  height: 48px;
  object-fit: contain;
  opacity: 0.95;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.15));
  border-radius: 8px;
}

.card-revealed-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 0;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.reversed-img {
  transform: rotate(180deg);
}

.card-name-tag {
  margin-top: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary, #1A1A1A);
  opacity: 0;
  transition: opacity 0.5s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.card-name-tag.visible {
  opacity: 1;
}

.reversed-badge {
  font-size: 0.65rem;
  color: var(--primary-color);
  background: rgba(244, 63, 94, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
}

/* Loading Area */
.loading-area {
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.loading-sparkles {
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.sparkle {
  color: var(--primary-color);
  font-size: 1rem;
  animation: sparkleFloat 2s ease-in-out infinite;
}

@keyframes sparkleFloat {
  0%, 100% { opacity: 0.3; transform: translateY(0) scale(0.8); }
  50% { opacity: 1; transform: translateY(-6px) scale(1.2); }
}

.loading-message {
  font-size: 1rem;
  color: var(--text-secondary, #6B6B6B);
  margin-bottom: 20px;
  transition: opacity 0.3s ease;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--card-bg);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-color));
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* MBTI × 타로 상식 카드 */
.knowledge-card {
  margin-top: 32px;
  max-width: 420px;
  width: 100%;
  padding: 18px 20px;
  background: var(--card-bg, #fff);
  border-radius: 16px;
  border: 1px solid var(--border-color, rgba(0,0,0,0.06));
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.knowledge-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.knowledge-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.knowledge-icon {
  font-size: 1.2rem;
}

.knowledge-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--primary-color);
  letter-spacing: 0.02em;
}

.knowledge-text {
  font-size: 0.92rem;
  line-height: 1.55;
  color: var(--text-primary, #2a2a2a);
  margin: 0;
}

/* 로딩 중 광고 */
.loading-ad-area {
  margin-top: 32px;
  width: 100%;
  max-width: 400px;
  display: flex;
  justify-content: center;
  opacity: 0;
  animation: fadeInAd 1s ease 3s forwards;
}

@keyframes fadeInAd {
  to { opacity: 1; }
}

/* Mobile */
@media (max-width: 600px) {
  .cards-reveal {
    gap: 12px;
  }

  .card-flipper {
    width: 85px;
    height: 146px;
  }

  .card-position-tag {
    font-size: 0.65rem;
    padding: 3px 10px;
  }

  .card-name-tag {
    font-size: 0.75rem;
  }

  .knowledge-card {
    padding: 14px 16px;
  }

  .knowledge-text {
    font-size: 0.85rem;
  }
}
</style>
