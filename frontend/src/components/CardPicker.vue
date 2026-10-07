<template>
  <div class="card-picker-fullscreen">
    <div class="fullscreen-container">

      <!-- PHASE: SHUFFLING -->
      <div v-if="isShuffling" class="phase-shuffle">
        <div class="shuffle-scene">
          <div class="fan-cards">
            <div
              v-for="i in 7"
              :key="i"
              class="fan-card"
              :style="getFanStyle(i - 1, 7)"
            >
              <div class="card-back-design">
                <div class="card-back-pattern"></div>
                <div class="card-back-gem">✦</div>
              </div>
            </div>
          </div>
          <div class="shuffle-text">
            <div class="shuffle-main">{{ t('cardPicker.shuffling') }}</div>
            <div class="shuffle-sub">{{ t('cardPicker.shuffleWait') }}</div>
          </div>
          <div class="shuffle-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- PHASE: PICKING -->
      <div v-else class="phase-picking">
        <!-- Starfield background -->
        <div class="starfield" aria-hidden="true"></div>

        <!-- Top bar -->
        <div class="top-bar">
          <button class="close-btn" @click="handleCancel">
            <v-icon size="20">mdi-close</v-icon>
          </button>
          <div class="step-indicator">
            <span class="step-current">{{ Math.min(selectedCards.length + 1, props.cardCount) }}</span>
            <span class="step-sep">/</span>
            <span class="step-total">{{ props.cardCount }}</span>
            <span class="step-label">{{ currentPositionLabel }}</span>
          </div>
          <div style="width: 40px"></div>
        </div>

        <!-- Guide text -->
        <div class="guide-area">
          <p class="guide-text">{{ guideMessage }}</p>
        </div>

        <!-- Card Grid (4 rows, no scroll) -->
        <div class="grid-area">
          <div class="card-grid">
            <div
              v-for="(card, idx) in displayCards"
              :key="card.key"
              :ref="el => setCardRef(card.key, el as HTMLElement)"
              :class="['grid-card', {
                'card-selected': isCardSelected(card),
                'card-disabled': selectedCards.length >= props.cardCount && !isCardSelected(card),
                'card-flipping': flippingCard === card.key,
                'card-hidden': hiddenCards.has(card.key),
                'card-glow-strong': card.glowStrong,
              }]"
              :style="{
                '--rotate': card.rotate + 'deg',
                '--y-offset': card.yOffset + 'px',
                '--shimmer-delay': card.shimmerDelay + 's',
                '--border-color': card.borderColor,
              }"
              @pointerdown="onPointerDown($event, card)"
              @pointermove="onPointerMove($event, card)"
              @pointerup="onPointerUp($event, card)"
              @pointercancel="onPointerCancel(card)"
            >
              <div class="card-flipper" :class="{ flipped: flippingCard === card.key || isCardSelected(card) }">
                <!-- Back face -->
                <div class="card-face card-back">
                  <div class="card-back-design" :style="{ borderColor: 'var(--border-color)' }">
                    <div class="card-back-pattern"></div>
                    <div class="card-back-gem">{{ card.symbol }}</div>
                    <div class="shimmer-overlay"></div>
                  </div>
                </div>
                <!-- Front face -->
                <div class="card-face card-front">
                  <img
                    v-if="isCardSelected(card) || flippingCard === card.key"
                    :src="getCardImageUrl(card.key)"
                    :alt="getCardName(card.key)"
                    class="card-front-img"
                    :class="{ 'reversed-img': card.reversed }"
                  />
                </div>
              </div>
              <!-- Charge ring for long press -->
              <svg v-if="chargingCard === card.key" class="charge-ring" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="36" class="charge-circle" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Bottom slots + button -->
        <div class="bottom-area">
          <div class="slot-row" :class="slotRowClass">
            <div
              v-for="(pos, idx) in props.cardPositions.slice(0, props.cardCount)"
              :key="idx"
              :ref="el => setSlotRef(idx, el as HTMLElement)"
              :class="['slot-item', { filled: idx < selectedCards.length, current: idx === selectedCards.length }]"
              @click="idx < selectedCards.length ? removeCardByIndex(idx) : null"
            >
              <div class="slot-card" v-if="idx < selectedCards.length">
                <img
                  :src="getCardImageUrl(selectedCards[idx].key)"
                  :alt="getCardName(selectedCards[idx].key)"
                  class="slot-card-img"
                  :class="{ 'reversed-img': selectedCards[idx].reversed }"
                />
                <div class="slot-remove">×</div>
              </div>
              <div class="slot-empty" v-else>
                <div class="slot-dashed">
                  <span class="slot-plus">+</span>
                </div>
              </div>
              <span class="slot-label">{{ truncateLabel(pos) }}</span>
            </div>
          </div>

          <v-btn
            v-if="selectedCards.length === props.cardCount"
            color="primary"
            size="large"
            @click="handleConfirm"
            class="interpret-btn"
          >
            <v-icon start>mdi-star-four-points</v-icon>
            해석해줘! 🌟
          </v-btn>

          <v-btn
            variant="text"
            size="small"
            @click="reshuffleCards"
            class="reshuffle-btn"
          >
            <v-icon start size="16">mdi-shuffle-variant</v-icon>
            카드 다시 섞기
          </v-btn>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  question: string
  selectionMode?: 'mystical' | 'manual'
  cardCount?: number
  spreadType?: string
  cardPositions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  selectionMode: 'mystical',
  cardCount: 3,
  spreadType: '과거-현재-미래',
  cardPositions: () => ['과거', '현재', '미래']
})

interface CardObject {
  key: string
  reversed: boolean
  symbol: string
  borderColor: string
  rotate: number
  yOffset: number
  shimmerDelay: number
  glowStrong: boolean
}

const emit = defineEmits(['cards-selected', 'cards-cancelled'])

// State
const shuffledDeck = ref<CardObject[]>([])
const selectedCards = ref<CardObject[]>([])
const isShuffling = ref(true)
const flippingCard = ref<string | null>(null)
const hiddenCards = ref<Set<string>>(new Set())
const chargingCard = ref<string | null>(null)

// Refs for FLIP animation
const cardRefs = new Map<string, HTMLElement>()
const slotRefs = new Map<number, HTMLElement>()

const setCardRef = (key: string, el: HTMLElement | null) => {
  if (el) cardRefs.set(key, el)
}
const setSlotRef = (idx: number, el: HTMLElement | null) => {
  if (el) slotRefs.set(idx, el)
}

// Long press tracking
let pressTimer: ReturnType<typeof setTimeout> | null = null
let pressStartX = 0
let pressStartY = 0
let isLongPress = false

// Card images
const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

const getCardImageUrl = (cardKey: string) => {
  const baseId = cardKey.replace('_r', '')
  const imagePath = `../assets/cards/${baseId}.jpg`
  return cardImages[imagePath] || cardImages['../assets/cards/maj00.jpg'] || ''
}

// Data
const FULL_DECK = [
  'maj00', 'maj01', 'maj02', 'maj03', 'maj04', 'maj05', 'maj06', 'maj07',
  'maj08', 'maj09', 'maj10', 'maj11', 'maj12', 'maj13', 'maj14', 'maj15',
  'maj16', 'maj17', 'maj18', 'maj19', 'maj20', 'maj21',
  'cups01', 'cups02', 'cups03', 'cups04', 'cups05', 'cups06', 'cups07',
  'cups08', 'cups09', 'cups10', 'cups11', 'cups12', 'cups13', 'cups14',
  'pents01', 'pents02', 'pents03', 'pents04', 'pents05', 'pents06', 'pents07',
  'pents08', 'pents09', 'pents10', 'pents11', 'pents12', 'pents13', 'pents14',
  'swords01', 'swords02', 'swords03', 'swords04', 'swords05', 'swords06', 'swords07',
  'swords08', 'swords09', 'swords10', 'swords11', 'swords12', 'swords13', 'swords14',
  'wands01', 'wands02', 'wands03', 'wands04', 'wands05', 'wands06', 'wands07',
  'wands08', 'wands09', 'wands10', 'wands11', 'wands12', 'wands13', 'wands14'
]

const TAROT_DECK: Record<string, { name: string; symbol: string }> = {
  maj00: { name: '바보', symbol: '0' },
  maj01: { name: '마법사', symbol: 'I' },
  maj02: { name: '여사제', symbol: 'II' },
  maj03: { name: '여황제', symbol: 'III' },
  maj04: { name: '황제', symbol: 'IV' },
  maj05: { name: '교황', symbol: 'V' },
  maj06: { name: '연인', symbol: 'VI' },
  maj07: { name: '전차', symbol: 'VII' },
  maj08: { name: '힘', symbol: 'VIII' },
  maj09: { name: '은둔자', symbol: 'IX' },
  maj10: { name: '운명의 바퀴', symbol: 'X' },
  maj11: { name: '정의', symbol: 'XI' },
  maj12: { name: '매달린 사람', symbol: 'XII' },
  maj13: { name: '죽음', symbol: 'XIII' },
  maj14: { name: '절제', symbol: 'XIV' },
  maj15: { name: '악마', symbol: 'XV' },
  maj16: { name: '탑', symbol: 'XVI' },
  maj17: { name: '별', symbol: 'XVII' },
  maj18: { name: '달', symbol: 'XVIII' },
  maj19: { name: '태양', symbol: 'XIX' },
  maj20: { name: '심판', symbol: 'XX' },
  maj21: { name: '세계', symbol: 'XXI' },
  cups01: { name: '컵 에이스', symbol: 'A♥' },
  cups02: { name: '컵 2', symbol: '2♥' },
  cups03: { name: '컵 3', symbol: '3♥' },
  cups04: { name: '컵 4', symbol: '4♥' },
  cups05: { name: '컵 5', symbol: '5♥' },
  cups06: { name: '컵 6', symbol: '6♥' },
  cups07: { name: '컵 7', symbol: '7♥' },
  cups08: { name: '컵 8', symbol: '8♥' },
  cups09: { name: '컵 9', symbol: '9♥' },
  cups10: { name: '컵 10', symbol: '10♥' },
  cups11: { name: '컵 시종', symbol: 'P♥' },
  cups12: { name: '컵 기사', symbol: 'N♥' },
  cups13: { name: '컵 여왕', symbol: 'Q♥' },
  cups14: { name: '컵 왕', symbol: 'K♥' },
  pents01: { name: '펜타클 에이스', symbol: 'A♦' },
  pents02: { name: '펜타클 2', symbol: '2♦' },
  pents03: { name: '펜타클 3', symbol: '3♦' },
  pents04: { name: '펜타클 4', symbol: '4♦' },
  pents05: { name: '펜타클 5', symbol: '5♦' },
  pents06: { name: '펜타클 6', symbol: '6♦' },
  pents07: { name: '펜타클 7', symbol: '7♦' },
  pents08: { name: '펜타클 8', symbol: '8♦' },
  pents09: { name: '펜타클 9', symbol: '9♦' },
  pents10: { name: '펜타클 10', symbol: '10♦' },
  pents11: { name: '펜타클 시종', symbol: 'P♦' },
  pents12: { name: '펜타클 기사', symbol: 'N♦' },
  pents13: { name: '펜타클 여왕', symbol: 'Q♦' },
  pents14: { name: '펜타클 왕', symbol: 'K♦' },
  swords01: { name: '검 에이스', symbol: 'A♠' },
  swords02: { name: '검 2', symbol: '2♠' },
  swords03: { name: '검 3', symbol: '3♠' },
  swords04: { name: '검 4', symbol: '4♠' },
  swords05: { name: '검 5', symbol: '5♠' },
  swords06: { name: '검 6', symbol: '6♠' },
  swords07: { name: '검 7', symbol: '7♠' },
  swords08: { name: '검 8', symbol: '8♠' },
  swords09: { name: '검 9', symbol: '9♠' },
  swords10: { name: '검 10', symbol: '10♠' },
  swords11: { name: '검 시종', symbol: 'P♠' },
  swords12: { name: '검 기사', symbol: 'N♠' },
  swords13: { name: '검 여왕', symbol: 'Q♠' },
  swords14: { name: '검 왕', symbol: 'K♠' },
  wands01: { name: '지팡이 에이스', symbol: 'A♣' },
  wands02: { name: '지팡이 2', symbol: '2♣' },
  wands03: { name: '지팡이 3', symbol: '3♣' },
  wands04: { name: '지팡이 4', symbol: '4♣' },
  wands05: { name: '지팡이 5', symbol: '5♣' },
  wands06: { name: '지팡이 6', symbol: '6♣' },
  wands07: { name: '지팡이 7', symbol: '7♣' },
  wands08: { name: '지팡이 8', symbol: '8♣' },
  wands09: { name: '지팡이 9', symbol: '9♣' },
  wands10: { name: '지팡이 10', symbol: '10♣' },
  wands11: { name: '지팡이 시종', symbol: 'P♣' },
  wands12: { name: '지팡이 기사', symbol: 'N♣' },
  wands13: { name: '지팡이 여왕', symbol: 'Q♣' },
  wands14: { name: '지팡이 왕', symbol: 'K♣' },
}

const getCardName = (key: string): string => {
  const baseKey = key.replace('_r', '')
  const info = TAROT_DECK[baseKey]
  if (!info) return key
  return key.endsWith('_r') ? `${info.name} (역방향)` : info.name
}

// Visual variation data
const BACK_SYMBOLS = ['✦', '◈', '⟡', '✧', '⊕']
const BORDER_COLORS = [
  'var(--border-color)',  // 연보라
  'rgba(234, 179, 8, 0.45)',   // 금빛
  'rgba(192, 192, 220, 0.5)',  // 은빛
]

const DISPLAY_COUNT = 26

const displayCards = computed(() => shuffledDeck.value.slice(0, DISPLAY_COUNT))

const currentPositionLabel = computed(() => {
  const idx = selectedCards.value.length
  if (idx >= props.cardCount) return props.cardPositions[props.cardCount - 1] || ''
  return props.cardPositions[idx] || `${idx + 1}번째`
})

const guideMessage = computed(() => {
  const idx = selectedCards.value.length
  if (idx >= props.cardCount) return '모든 카드를 골랐어! ✨'
  if (idx === 0) return '마음이 끌리는 카드를 지그시 눌러서 뽑아봐 ✨'
  return '카드를 지그시 눌러 다음 카드도 골라봐 ✨'
})

const slotRowClass = computed(() => {
  if (props.cardCount <= 1) return 'slots-1'
  if (props.cardCount <= 3) return 'slots-3'
  if (props.cardCount <= 5) return 'slots-5'
  return 'slots-many'
})

const getFanStyle = (index: number, total: number) => {
  const maxAngle = 40
  const angleStep = total > 1 ? maxAngle / (total - 1) : 0
  const angle = -maxAngle / 2 + angleStep * index
  return {
    transform: `rotate(${angle}deg)`,
    transformOrigin: 'center 120%',
    animationDelay: `${index * 0.1}s`
  }
}

// Deck creation
const createFullDeck = (): CardObject[] => {
  const fullDeck: { key: string; reversed: boolean }[] = []

  FULL_DECK.forEach(cardKey => {
    fullDeck.push({ key: cardKey, reversed: false })
  })

  const reversedCount = Math.floor(FULL_DECK.length * 0.25)
  const shuffledForReversed = [...FULL_DECK].sort(() => Math.random() - 0.5)
  for (let i = 0; i < reversedCount; i++) {
    fullDeck.push({ key: `${shuffledForReversed[i]}_r`, reversed: true })
  }

  // Fisher-Yates shuffle
  for (let i = fullDeck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    const temp = fullDeck[i]
    fullDeck[i] = fullDeck[j]
    fullDeck[j] = temp
  }

  // 최대 4장만 강한 글로우
  const glowIndices = new Set<number>()
  while (glowIndices.size < Math.min(4, DISPLAY_COUNT)) {
    glowIndices.add(Math.floor(Math.random() * DISPLAY_COUNT))
  }

  return fullDeck.map((card, idx) => ({
    ...card,
    symbol: BACK_SYMBOLS[Math.floor(Math.random() * BACK_SYMBOLS.length)],
    borderColor: BORDER_COLORS[Math.floor(Math.random() * BORDER_COLORS.length)],
    rotate: (Math.random() - 0.5) * 4,       // -2 ~ +2deg
    yOffset: (Math.random() - 0.5) * 6,       // -3px ~ +3px
    shimmerDelay: Math.random() * 5,           // 0~5s
    glowStrong: glowIndices.has(idx),
  }))
}

// Card selection with FLIP animation
const selectCard = async (cardObj: CardObject) => {
  if (isCardSelected(cardObj)) {
    // Deselect
    const existingIndex = selectedCards.value.findIndex(c => c.key === cardObj.key)
    if (existingIndex > -1) {
      selectedCards.value.splice(existingIndex, 1)
      hiddenCards.value.delete(cardObj.key)
    }
    return
  }

  if (selectedCards.value.length >= props.cardCount) return

  // 뒤집기 먼저, 끝나면 슬롯으로 FLIP 이동
  flippingCard.value = cardObj.key

  setTimeout(async () => {
    const cardEl = cardRefs.get(cardObj.key)
    const slotIdx = selectedCards.value.length
    const slotEl = slotRefs.get(slotIdx)

    if (cardEl && slotEl) {
      const cardRect = cardEl.getBoundingClientRect()
      const slotRect = slotEl.getBoundingClientRect()

      // Create flying clone
      const clone = document.createElement('div')
      clone.className = 'flying-card'
      const imgUrl = getCardImageUrl(cardObj.key)
      clone.innerHTML = `<img src="${imgUrl}" style="width:100%;height:100%;object-fit:cover;border-radius:6px;${cardObj.reversed ? 'transform:rotate(180deg);' : ''}" />`
      clone.style.cssText = `
        position:fixed;
        left:${cardRect.left}px;
        top:${cardRect.top}px;
        width:${cardRect.width}px;
        height:${cardRect.height}px;
        z-index:9999;
        border-radius:6px;
        box-shadow:0 8px 32px rgba(139,92,246,0.5);
        transition:all 0.5s cubic-bezier(0.34,1.56,0.64,1);
        pointer-events:none;
      `
      document.body.appendChild(clone)

      // 시작 위치를 먼저 반영시키려고 강제 reflow
      clone.offsetHeight

      requestAnimationFrame(() => {
        clone.style.left = `${slotRect.left}px`
        clone.style.top = `${slotRect.top}px`
        clone.style.width = `${slotRect.width}px`
        clone.style.height = `${slotRect.height - 20}px` // account for label
      })

      // Hide original card, add to selected
      hiddenCards.value.add(cardObj.key)
      selectedCards.value.push(cardObj)

      // Remove clone after animation
      setTimeout(() => {
        clone.remove()
        flippingCard.value = null
      }, 550)
    } else {
      // Fallback: no animation
      selectedCards.value.push(cardObj)
      hiddenCards.value.add(cardObj.key)
      flippingCard.value = null
    }
  }, 800) // flip 애니메이션 시간
}

const removeCardByIndex = (index: number) => {
  const card = selectedCards.value[index]
  if (card) {
    hiddenCards.value.delete(card.key)
  }
  selectedCards.value.splice(index, 1)
}

const isCardSelected = (card: CardObject) => {
  return selectedCards.value.some(c => c.key === card.key)
}

const truncateLabel = (text: string) => {
  if (text.length > 5) return text.substring(0, 4) + '…'
  return text
}

// Pointer events (tap + long press)
const onPointerDown = (e: PointerEvent, card: CardObject) => {
  if (selectedCards.value.length >= props.cardCount && !isCardSelected(card)) return
  if (flippingCard.value) return

  pressStartX = e.clientX
  pressStartY = e.clientY
  isLongPress = false

  // Start long press timer
  pressTimer = setTimeout(() => {
    isLongPress = true
    chargingCard.value = card.key
    // charge 애니메이션 끝나면 자동 선택
    setTimeout(() => {
      if (chargingCard.value === card.key) {
        chargingCard.value = null
        selectCard(card)
      }
    }, 700)
  }, 700)
}

const onPointerMove = (e: PointerEvent, card: CardObject) => {
  const dx = e.clientX - pressStartX
  const dy = e.clientY - pressStartY
  if (Math.sqrt(dx * dx + dy * dy) > 5) {
    // Cancel long press on drag
    if (pressTimer) {
      clearTimeout(pressTimer)
      pressTimer = null
    }
    if (chargingCard.value === card.key) {
      chargingCard.value = null
    }
  }
}

const onPointerUp = (e: PointerEvent, card: CardObject) => {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }

  if (isLongPress) {
    isLongPress = false
    return // Already handled by long press
  }

  if (chargingCard.value === card.key) {
    chargingCard.value = null
    return
  }

  if (flippingCard.value) return

  selectCard(card)
}

const onPointerCancel = (card: CardObject) => {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
  if (chargingCard.value === card.key) {
    chargingCard.value = null
  }
  isLongPress = false
}

// Confirm
const handleConfirm = () => {
  if (selectedCards.value.length === props.cardCount) {
    const cardKeys = selectedCards.value.map(c => {
      if (c.key.endsWith('_r')) return c.key
      return c.reversed ? `${c.key}_r` : c.key
    })
    emit('cards-selected', cardKeys)
  }
}

const handleCancel = () => {
  emit('cards-cancelled')
}

// Reshuffle
const reshuffleCards = () => {
  // 이미 고른 카드는 슬롯에 두고 나머지만 다시 섞음
  isShuffling.value = true
  flippingCard.value = null
  chargingCard.value = null

  setTimeout(() => {
    // 같은 카드가 다시 나오지 않게 제외
    const pickedKeys = new Set(selectedCards.value.map(c => c.key))
    shuffledDeck.value = createFullDeck().filter(c => !pickedKeys.has(c.key))
    setTimeout(() => {
      isShuffling.value = false
    }, 1200)
  }, 200)
}

// Init
onMounted(() => {
  shuffledDeck.value = createFullDeck()
  setTimeout(() => {
    isShuffling.value = false
  }, 1200)
})
</script>

<style scoped>
/* 카드 피커 풀스크린 */
.card-picker-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 40%, var(--bg-secondary) 100%);
}

.fullscreen-container {
  width: 100vw;
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
}

/* Shuffle Phase */
.phase-shuffle {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shuffle-scene {
  text-align: center;
  padding: 40px 20px;
}

.fan-cards {
  position: relative;
  width: 200px;
  height: 160px;
  margin: 0 auto 32px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.fan-card {
  width: 56px;
  height: 84px;
  border-radius: 8px;
  position: absolute;
  bottom: 0;
  left: 50%;
  margin-left: -28px;
  animation: fanReveal 0.6s ease-out both;
}

@keyframes fanReveal {
  from { opacity: 0; transform: rotate(0deg) translateY(20px); }
  to { opacity: 1; }
}

.shuffle-text { margin-bottom: 24px; }
.shuffle-main { font-size: 1.1rem; font-weight: 600; color: #e8d5f5; margin-bottom: 8px; }
.shuffle-sub { font-size: 0.85rem; color: #a88bc4; }

.shuffle-dots { display: flex; justify-content: center; gap: 8px; }
.shuffle-dots span {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--primary-color);
  animation: dotPulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 8px var(--border-color);
}
.shuffle-dots span:nth-child(2) { animation-delay: 0.3s; }
.shuffle-dots span:nth-child(3) { animation-delay: 0.6s; }

@keyframes dotPulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* Picking Phase */
.phase-picking {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.5s ease;
  position: relative;
  overflow: hidden;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Starfield */
.starfield {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.starfield::before,
.starfield::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: white;
}

.starfield::before {
  box-shadow:
    12vw 8vh 0 0.5px var(--text-secondary),
    85vw 12vh 0 1px var(--text-secondary),
    45vw 5vh 0 0.5px var(--text-secondary),
    72vw 22vh 0 1px var(--border-color),
    28vw 18vh 0 0.5px var(--border-color),
    90vw 35vh 0 1px var(--text-muted),
    8vw 42vh 0 0.5px var(--text-secondary),
    55vw 38vh 0 1px var(--border-color),
    35vw 55vh 0 0.5px var(--border-color),
    78vw 48vh 0 1px var(--text-secondary),
    18vw 62vh 0 0.5px var(--text-secondary),
    62vw 58vh 0 1px var(--border-color),
    42vw 72vh 0 0.5px var(--text-secondary),
    88vw 68vh 0 1px var(--text-secondary),
    5vw 78vh 0 0.5px var(--border-color);
  animation: twinkle1 4s ease-in-out infinite;
}

.starfield::after {
  box-shadow:
    22vw 15vh 0 1px var(--border-color),
    68vw 8vh 0 0.5px var(--text-secondary),
    38vw 25vh 0 1px var(--text-muted),
    82vw 30vh 0 0.5px var(--border-color),
    15vw 35vh 0 1px var(--border-color),
    52vw 45vh 0 0.5px var(--text-secondary),
    75vw 55vh 0 1px var(--text-secondary),
    30vw 65vh 0 0.5px var(--border-color),
    92vw 72vh 0 1px var(--border-color),
    48vw 82vh 0 0.5px var(--text-secondary),
    10vw 88vh 0 1px var(--text-secondary),
    65vw 75vh 0 0.5px var(--text-secondary),
    25vw 92vh 0 1px var(--border-color),
    58vw 15vh 0 0.5px var(--border-color),
    95vw 45vh 0 1px var(--text-muted);
  animation: twinkle2 5s ease-in-out infinite 1s;
}

@keyframes twinkle1 {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes twinkle2 {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Top bar */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  padding-top: max(12px, env(safe-area-inset-top));
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

.close-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--text-primary);
  transition: all 0.2s;
}
.close-btn:hover { background: var(--border-color); color: var(--text-primary); }

.step-indicator {
  display: flex; align-items: center; gap: 4px;
  background: var(--border-color);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: 24px; padding: 8px 18px;
}
.step-current { font-size: 1.15rem; font-weight: 700; color: var(--primary-color); }
.step-sep { font-size: 0.85rem; color: var(--border-color); margin: 0 2px; }
.step-total { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); }
.step-label {
  font-size: 0.8rem; font-weight: 600; color: var(--primary-color);
  margin-left: 8px; padding-left: 8px;
  border-left: 1px solid var(--border-color);
}

/* Guide area */
.guide-area {
  text-align: center; padding: 4px 24px 8px;
  flex-shrink: 0; position: relative; z-index: 2;
}
.guide-text { font-size: 0.95rem; color: #d4bfea; font-weight: 500; margin: 0; }

/* Card Grid */
.grid-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  min-height: 0;
  position: relative;
  z-index: 2;
  touch-action: manipulation;
}

.card-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  max-width: 420px;
}

.grid-card {
  width: 50px;
  height: 75px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  transform: rotate(var(--rotate)) translateY(var(--y-offset));
  transition: transform 0.3s ease, opacity 0.3s ease;
  touch-action: manipulation;
  user-select: none;
  perspective: 600px;
}

/* 카드 호버 글로우 */
.grid-card:hover:not(.card-disabled):not(.card-hidden) {
  transform: rotate(var(--rotate)) translateY(calc(var(--y-offset) - 8px)) scale(1.08);
  z-index: 5;
  filter: drop-shadow(0 0 12px var(--border-color));
}

.grid-card.card-disabled {
  opacity: 0.25;
  pointer-events: none;
}

.grid-card.card-hidden {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.5);
}

.grid-card.card-glow-strong {
  animation: strongGlow 3s ease-in-out infinite;
}

@keyframes strongGlow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3) drop-shadow(0 0 8px var(--border-color)); }
}

/* Card flipper (3D) */
.card-flipper {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-flipper.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 8px;
  overflow: hidden;
}

.card-front {
  transform: rotateY(180deg);
}

.card-front-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.card-front-img.reversed-img {
  transform: rotate(180deg);
}

/* Card back design */
.card-back-design {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #3b2066 0%, #2a1650 50%, #4a2d7a 100%);
  border: 1.5px solid var(--border-color, var(--border-color));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.card-back-pattern {
  position: absolute;
  inset: 3px;
  border: 1px solid var(--button-hover-bg);
  border-radius: 5px;
}

.card-back-pattern::before {
  content: '';
  position: absolute;
  inset: 2px;
  border: 1px solid var(--button-hover-bg);
  border-radius: 3px;
}

.card-back-gem {
  font-size: 1rem;
  color: var(--text-secondary);
  z-index: 1;
  text-shadow: 0 0 8px var(--border-color);
}

.shimmer-overlay {
  position: absolute;
  top: -100%;
  left: -100%;
  width: 300%;
  height: 300%;
  background: linear-gradient(
    115deg,
    transparent 30%,
    var(--card-bg) 45%,
    rgba(255, 255, 255, 0.18) 50%,
    var(--card-bg) 55%,
    transparent 70%
  );
  animation: shimmer 4s ease-in-out infinite;
  animation-delay: var(--shimmer-delay, 0s);
  pointer-events: none;
}

@keyframes shimmer {
  0% { transform: translate(-30%, -30%) rotate(25deg); }
  100% { transform: translate(30%, 30%) rotate(25deg); }
}

/* Charge ring */
.charge-ring {
  position: absolute;
  inset: -8px;
  width: calc(100% + 16px);
  height: calc(100% + 16px);
  pointer-events: none;
  z-index: 10;
}

.charge-circle {
  fill: none;
  stroke: var(--primary-color);
  stroke-width: 3;
  stroke-dasharray: 226;
  stroke-dashoffset: 226;
  stroke-linecap: round;
  animation: chargeStroke 0.7s linear forwards;
  filter: drop-shadow(0 0 6px rgba(167,139,250,0.8));
}

@keyframes chargeStroke {
  to { stroke-dashoffset: 0; }
}

/* 하단 영역 */
.bottom-area {
  flex-shrink: 0;
  padding: 12px 20px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  background: rgba(13, 10, 26, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--button-hover-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.3);
}

.slot-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  width: 100%;
}

.slot-row.slots-1 .slot-item { width: 80px; }
.slot-row.slots-3 .slot-item { width: 68px; }
.slot-row.slots-5 .slot-item { width: 52px; }
.slot-row.slots-many .slot-item { width: 44px; }

.slot-row.slots-5,
.slot-row.slots-many { flex-wrap: wrap; }

.slot-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: default;
}

.slot-item.filled { cursor: pointer; }

.slot-item.current .slot-empty {
  border-color: var(--border-color);
  animation: slotPulse 1.5s ease-in-out infinite;
}

@keyframes slotPulse {
  0%, 100% { box-shadow: 0 0 0 rgba(167, 139, 250, 0); }
  50% { box-shadow: 0 0 12px var(--border-color); }
}

.slot-card {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 6px;
  position: relative;
  animation: slotFill 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
  border: 1.5px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

@keyframes slotFill {
  from { transform: scale(0) rotate(-10deg); }
  to { transform: scale(1) rotate(0); }
}

.slot-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 5px;
}

.slot-card-img.reversed-img {
  transform: rotate(180deg);
}

.slot-remove {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ef4444;
  color: var(--text-primary);
  font-size: 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.2s;
}

.slot-item.filled:hover .slot-remove { opacity: 1; }

.slot-empty {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slot-dashed {
  width: 100%;
  height: 100%;
  border-radius: 6px;
  border: 1.5px dashed var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--button-hover-bg);
}

.slot-plus { color: var(--border-color); font-size: 1.2rem; font-weight: 300; }

.slot-label {
  font-size: 0.65rem;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

/* Interpret button */
.interpret-btn {
  width: 100%;
  height: 52px !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  font-size: 1.05rem !important;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color), var(--primary-color)) !important;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
  animation: btnGlow 2s ease-in-out infinite;
  text-transform: none !important;
  letter-spacing: 0.5px !important;
}

@keyframes btnGlow {
  0%, 100% { box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4); }
  50% { box-shadow: 0 4px 28px rgba(139, 92, 246, 0.6); }
}

.reshuffle-btn {
  color: var(--text-secondary) !important;
  text-transform: none !important;
  font-size: 0.8rem !important;
  letter-spacing: 0 !important;
}
.reshuffle-btn:hover { color: var(--text-primary) !important; }

/* Responsive */
@media (max-width: 360px) {
  .grid-card {
    width: 44px;
    height: 66px;
  }
  .card-grid { gap: 4px; max-width: 350px; }
  .slot-row.slots-3 .slot-item { width: 58px; }
}

@media (min-width: 768px) {
  .grid-card {
    width: 58px;
    height: 87px;
  }
  .card-grid { gap: 8px; max-width: 500px; }
}

/* D 톤 오버라이드 (LandingView와 통일) */

/* 메인 배경 */
.card-picker-fullscreen {
  background: var(--bg-primary) !important;
}

/* 셔플 화면 */
.shuffle-scene { background: transparent !important; }
.shuffle-main { color: var(--text-primary) !important; font-weight: 700 !important; }
.shuffle-sub { color: var(--text-secondary) !important; }
.shuffle-dots span,
.shuffle-dots > * { background: var(--primary-color) !important; }

/* 카드 뒷면: 라벤더 단색 + 잉크 보더 + 옐로 gem */
.card-back-design {
  background: var(--secondary-color) !important;
  border: 2px solid var(--text-primary) !important;
  border-radius: 8px !important;
  position: relative !important;
  overflow: hidden !important;
}
.card-back-design::before {
  content: '' !important;
  position: absolute !important;
  inset: 4px !important;
  border: 1px solid rgba(26, 26, 46, 0.25) !important;
  border-radius: 5px !important;
  pointer-events: none !important;
}
.card-back-pattern {
  background: radial-gradient(circle at 50% 50%, rgba(254, 248, 231, 0.2) 0%, transparent 65%) !important;
}
.card-back-gem {
  color: var(--text-primary) !important;
  text-shadow: 0 0 6px rgba(254, 243, 199, 0.5) !important;
  font-size: 1.5em !important;
  opacity: 0.85 !important;
}

/* Step Indicator */
.step-indicator {
  background: var(--card-bg) !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 999px !important;
  padding: 8px 16px !important;
  box-shadow: 3px 3px 0 var(--secondary-color) !important;
}
.step-current {
  color: var(--primary-color) !important;
  font-weight: 800 !important;
  font-size: 1.2em !important;
}
.step-sep, .step-total { color: var(--text-secondary) !important; }
.step-label { color: var(--text-primary) !important; font-weight: 600 !important; }

/* Reshuffle 버튼 */
.reshuffle-btn {
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 999px !important;
  font-weight: 600 !important;
}
.reshuffle-btn:hover {
  background: var(--button-hover-bg) !important;
  color: var(--text-primary) !important;
  transform: translateY(-1px);
}

/* 카드 그리드 */
.card-grid { background: transparent !important; }
.grid-card { cursor: pointer; }
.grid-card:hover .card-back-design {
  box-shadow: 0 4px 16px rgba(251, 113, 133, 0.4) !important;
  transform: translateY(-2px);
}

/* 카드 앞면 (뒤집힌 후) */
.card-front {
  background: var(--card-bg) !important;
  border: 2px solid var(--text-primary) !important;
  border-radius: 8px !important;
}
.card-front-img {
  border-radius: 6px !important;
}

/* 선택된 카드 슬롯 */
.slot-row { background: transparent !important; }
.slot-item {
  background: var(--card-bg) !important;
  border: 2px dashed var(--text-primary) !important;
  border-radius: 8px !important;
}
.slot-item.filled {
  border-style: solid !important;
  box-shadow: 4px 4px 0 var(--primary-color) !important;
}

/* 텍스트 색 잉크로 통일 */
.card-picker-fullscreen :deep(p),
.card-picker-fullscreen :deep(span),
.card-picker-fullscreen :deep(h1),
.card-picker-fullscreen :deep(h2),
.card-picker-fullscreen :deep(h3),
.card-picker-fullscreen :deep(div):not(.card-back-design):not(.card-back-pattern) {
  color: inherit;
}

/* 그라데이션, glow 애니메이션 끔 */
.shimmer-overlay {
  display: none !important;
}
.grid-card.card-glow-strong {
  animation: none !important;
}
</style>
