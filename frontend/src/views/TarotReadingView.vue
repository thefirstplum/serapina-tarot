<template>
  <div class="reading-main">
      <div class="reading-container">
        <!-- Header -->
        <header class="reading-header">
          <div class="header-left" @click="goToHome" style="cursor: pointer;">
            <div class="logo-area">
              <img src="/icons/symbol-64.png" class="logo-icon" alt="세라피나" width="32" height="32" style="object-fit: contain; vertical-align: middle;" />
              <div>
                <h1 class="app-title">{{ t('readingView.appTitle') }}</h1>
                <p class="app-subtitle">{{ t('readingView.appSubtitle') }}</p>
              </div>
            </div>
          </div>
          <div class="header-actions">
            <v-btn icon variant="text" @click="goToHome" :title="t('readingView.homeButton')" class="header-btn">
              <v-icon>mdi-home</v-icon>
            </v-btn>
          </div>
        </header>

        <!-- Step Indicator -->
        <div class="step-indicator" v-show="currentStep !== 'cards'">
          <div class="step" :class="{ active: currentStep === 'question', completed: stepCompleted('question') }">
            <span class="step-num">1</span>
            <span class="step-label">{{ t('readingView.steps.question') }}</span>
          </div>
          <div class="step-line" :class="{ active: stepCompleted('question') }"></div>
          <div class="step" :class="{ active: currentStep === 'cards', completed: stepCompleted('cards') }">
            <span class="step-num">2</span>
            <span class="step-label">{{ t('readingView.steps.cards') }}</span>
          </div>
          <div class="step-line" :class="{ active: stepCompleted('cards') }"></div>
          <div class="step" :class="{ active: currentStep === 'interpreting', completed: stepCompleted('interpreting') }">
            <span class="step-num">3</span>
            <span class="step-label">{{ t('readingView.steps.interpreting') }}</span>
          </div>
          <div class="step-line" :class="{ active: stepCompleted('interpreting') }"></div>
          <div class="step" :class="{ active: currentStep === 'result' }">
            <span class="step-num">4</span>
            <span class="step-label">{{ t('readingView.steps.result') }}</span>
          </div>
        </div>

        <!-- Step 1: Question Input -->
        <section v-if="currentStep === 'question'" class="step-section question-section">
          <div class="question-card">
            <div class="question-header">
              <div class="crystal-ball">
                <img src="/icons/symbol-128.png" alt="" width="56" height="56" style="object-fit: contain;" />
              </div>
              <h2 class="section-title">{{ t('readingView.questionHeader') }}</h2>
              <p class="section-subtitle">{{ t('readingView.questionSubheader') }}</p>
            </div>

            <!-- Category Pills -->
            <div class="category-pills">
              <button
                v-for="cat in categories"
                :key="cat.key"
                class="cat-pill"
                :class="{ active: selectedCategory === cat.key }"
                @click="selectCategory(cat.key)"
              >
                <span class="cat-emoji">{{ cat.emoji }}</span>
                <span class="cat-name">{{ cat.name }}</span>
              </button>
            </div>

            <!-- MBTI 셀렉터 (선택, 입력 시 해석에 반영) -->
            <div class="mbti-row">
              <span class="mbti-label"><img src="/icons/symbol-48.png" alt="" width="18" height="18" style="object-fit: contain; vertical-align: -3px; margin-right: 4px;" />내 MBTI</span>
              <v-select
                v-model="userMbti"
                :items="mbtiOptions"
                placeholder="선택"
                density="compact"
                variant="outlined"
                hide-details
                clearable
                @update:model-value="onMbtiChange"
                class="mbti-select"
              ></v-select>
            </div>

            <div class="input-wrapper">
              <v-textarea
                v-model="question"
                :placeholder="placeholderText"
                rows="3"
                variant="outlined"
                class="question-input"
                hide-details
                auto-grow
                @keydown.enter.exact.prevent="submitQuestion"
              />
            </div>

            <v-btn
              color="primary"
              size="large"
              :disabled="!question.trim()"
              :loading="isLoadingSpread"
              @click="submitQuestion"
              class="submit-btn"
            >
              <v-icon start>mdi-cards-playing-outline</v-icon>
              {{ t('readingView.drawCardsButton') }}
              <v-icon end>mdi-arrow-right</v-icon>
            </v-btn>
          </div>

          <!-- Example Questions -->
          <div class="example-questions">
            <p class="examples-title">
              <v-icon size="small" class="mr-1">mdi-lightbulb-outline</v-icon>
              {{ t('readingView.examplesTitle') }}
            </p>
            <div class="examples-grid">
              <div
                v-for="example in filteredExamples"
                :key="example.text"
                class="example-item"
                @click="selectExample(example.text)"
              >
                <span class="example-emoji">{{ example.emoji }}</span>
                <span class="example-text">{{ example.text }}</span>
              </div>
            </div>
          </div>

          <!-- 질문 입력 하단 광고 -->
          <div v-if="!isPremium" class="reading-ad-slot">
            <AdSenseBlock slot="1696071761" />
          </div>
        </section>

        <!-- MBTI 미니 박스 (카드 단계 직전, 여기서 변경 가능) -->
        <section v-if="currentStep === 'cards'" class="mbti-mini-section">
          <div v-if="userMbti && !mbtiEditing" class="mbti-mini-chip">
            <div class="mini-chip-label">
              <span class="mini-chip-emoji">🧬</span>
              <span><strong>{{ userMbti }}</strong> 성향을 해석에 반영하고 있어</span>
            </div>
            <button class="mini-chip-change" @click="mbtiEditing = true">✏️ 변경</button>
          </div>
          <div v-else class="mbti-mini-select">
            <div class="mini-select-title">🧬 MBTI 알려주면 해석에 너의 성향이 반영돼</div>
            <v-select
              v-model="userMbti"
              :items="mbtiOptions"
              density="compact"
              hide-details
              variant="outlined"
              placeholder="MBTI 선택 (선택 사항)"
              class="mini-select"
              @update:modelValue="mbtiEditing = false"
            />
            <button v-if="userMbti" class="mini-skip" @click="mbtiEditing = false">접기</button>
          </div>
        </section>

        <!-- Step 2: Card Selection (CardPicker) -->
        <CardPicker
          v-if="currentStep === 'cards'"
          :question="question"
          :spread-type="spreadType"
          :card-count="cardCount"
          :card-positions="cardPositions"
          @cards-selected="onCardsSelected"
          @cards-cancelled="resetToQuestion"
        />

        <!-- Step 3: Interpreting (Loading Screen) -->
        <section v-if="currentStep === 'interpreting'" class="step-section">
          <div v-if="queueWaiting > 0" class="queue-screen">
            <div class="queue-spinner"></div>
            <h3 class="queue-title">세라피나가 다른 친구의 고민을 듣고 있어</h3>
            <p class="queue-desc">잠깐만 기다려줄래? 보통 1~2분이면 네 차례가 와 🌙</p>
            <p v-if="queueWaiting > 1" class="queue-count">지금 {{ queueWaiting }}명이 기다리고 있어</p>
          </div>
          <ReadingLoadingScreen
            v-else
            :cards="selectedCards"
            :card-positions="cardPositions"
            :spread-type="spreadType"
            :is-ready="interpretationReady"
            :user-mbti="userMbti || undefined"
            @transition-complete="showResult"
          />
        </section>

        <!-- Step 4: Result -->
        <section v-if="currentStep === 'result'" class="step-section result-section">
          <!-- Compact Header: 스프레드 + 질문 한 줄 -->
          <div class="result-header">
            <span class="result-spread"><img src="/icons/symbol-48.png" alt="" width="18" height="18" style="object-fit: contain; vertical-align: -3px; margin-right: 4px;" />{{ spreadType }}</span>
            <span class="result-dot">·</span>
            <span class="result-question">"{{ question }}"</span>
          </div>

          <!-- Cards Display -->
          <div class="cards-showcase">
            <div class="cards-row">
              <div
                v-for="(card, index) in selectedCards"
                :key="index"
                class="card-showcase-item"
                :style="{ animationDelay: `${index * 0.15}s` }"
              >
                <div class="card-position-label">{{ cardPositions[index] }}</div>
                <div class="card-frame" :class="{ 'reversed-frame': card.reversed }">
                  <img
                    :src="getCardImageUrl(card.id)"
                    :alt="card.name"
                    class="card-img"
                    :class="{ 'reversed-img': card.reversed }"
                  />
                </div>
                <div class="card-name-label">
                  {{ card.name }}
                  <span v-if="card.reversed" class="reversed-tag">{{ t('readingView.reversedTag') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Interpretation -->
          <div class="interpretation-card">
            <div class="interpretation-header">
              <div class="seraphina-avatar">
                <span>✨</span>
              </div>
              <div class="interpretation-title-area">
                <h3 class="interpretation-title">{{ t('readingView.interpretationTitle') }}</h3>
                <p class="interpretation-subtitle">{{ t('readingView.interpretationSubtitle') }}</p>
              </div>
            </div>

            <div class="interpretation-body">
              <div class="interpretation-content" v-html="formattedInterpretation"></div>
            </div>
          </div>

          <!-- 결과 이어보기 (답변 목록 위, 버튼 아래) -->
          <div class="follow-up-section">
            <h3 class="follow-up-title">💬 결과, 더 알아볼래?</h3>

            <!-- 펼쳐진 답변들 -->
            <div v-if="followUps.length" class="follow-up-answers">
              <div v-for="(fu, i) in followUps" :key="`fu${i}`" class="follow-up-item">
                <button
                  class="follow-up-q"
                  @click="expandedFollowUp = expandedFollowUp === i ? -1 : i"
                >
                  <span class="fu-toggle">{{ expandedFollowUp === i ? '▼' : '▶' }}</span>
                  <span class="fu-q-text">{{ fu.q }}</span>
                </button>
                <div v-if="expandedFollowUp === i" class="follow-up-a">
                  <FollowupLoadingCard v-if="!fu.a" :user-mbti="userMbti || undefined" />
                  <template v-else>{{ fu.a }}</template>
                </div>
              </div>
            </div>

            <!-- 액션 버튼 -->
            <template v-if="followUpRemaining > 0">
              <div class="follow-up-buttons">
                <button
                  class="follow-up-btn deepen"
                  :disabled="followUpLoading"
                  @click="deepenReading"
                >
                  <span class="follow-up-btn-icon">🔍</span>
                  <span class="follow-up-btn-text">더 깊게 풀어줘</span>
                </button>
                <button
                  class="follow-up-btn ask"
                  :disabled="followUpLoading"
                  @click="showFollowUpInput = !showFollowUpInput"
                >
                  <span class="follow-up-btn-icon">💬</span>
                  <span class="follow-up-btn-text">더 물어보기</span>
                </button>
              </div>
              <div v-if="showFollowUpInput" class="follow-up-input-row">
                <input
                  v-model="followUpInput"
                  class="follow-up-input"
                  :placeholder="followUpLoading ? '세라피나가 생각 중...' : '더 궁금한 걸 물어봐'"
                  :disabled="followUpLoading"
                  @keyup.enter="askFollowUp"
                />
                <button
                  class="follow-up-send"
                  :disabled="followUpLoading || !followUpInput.trim()"
                  @click="askFollowUp"
                >→</button>
              </div>
              <p class="follow-up-count">
                <template v-if="adsWatchedCount === 0">무료 {{ followUpRemaining }}번 남음</template>
                <template v-else>광고 보상 {{ followUpRemaining }}번 남음 ({{ adsWatchedCount }}/{{ MAX_ADS }})</template>
              </p>
            </template>
            <template v-else>
              <button v-if="adsWatchedCount < MAX_ADS" class="follow-up-ad-btn" @click="showAdUnlockDialog = true">
                💫 더 깊은 풀이 보기 ({{ adsWatchedCount }}/{{ MAX_ADS }})
              </button>
            </template>
          </div>

          <!-- 카테고리 매칭 링크프라이스 광고 -->
          <LinkpriceAdBlock
            v-if="interpretationReady && question"
            :category="adCategory"
            :sensitive="adSensitive"
          />

          <!-- 프리미엄 넛지 (숨김) -->
          <!-- <div v-if="!isPremium" class="premium-nudge">
            <div class="nudge-content" @click="goToSubscription">
              <span class="nudge-icon">👑</span>
              <span class="nudge-text">{{ t('readingView.premiumNudge') }}</span>
              <v-icon size="small">mdi-chevron-right</v-icon>
            </div>
          </div> -->

          <!-- Action Buttons -->
          <div class="result-actions">
            <v-btn
              color="primary"
              size="large"
              block
              @click="resetToQuestion"
              class="action-btn primary-action"
            >
              <v-icon start>mdi-cards-playing-outline</v-icon>
              {{ t('readingView.anotherQuestion') }}
            </v-btn>
            <div class="sub-actions">
              <v-btn
                variant="outlined"
                size="large"
                @click="openShareCard"
                class="action-btn share-action"
              >
                <v-icon start>mdi-share-variant</v-icon>
                {{ t('readingView.shareResult') }}
              </v-btn>
              <v-btn
                variant="text"
                size="large"
                @click="goToHome"
                class="action-btn secondary-action"
              >
                <v-icon start>mdi-home</v-icon>
                {{ t('readingView.homeButton') }}
              </v-btn>
            </div>
          </div>

          <!-- Saved confirmation (숨김) -->
          <!-- <div v-if="isSaved" class="saved-link">
            <router-link to="/saved-readings">{{ t('readingView.viewSavedReadings') }}</router-link>
          </div> -->

          <!-- 광고 (결과 + follow-up 다음) -->
          <div v-if="!isPremium" class="reading-ad-slot">
            <AdSenseBlock slot="1696071761" />
          </div>

        </section>

        <!-- 이어보기 unlock: 10초 카운트다운 + 링크프라이스 카드 -->
        <AdUnlockDialog
          v-model="showAdUnlockDialog"
          :category="adCategory"
          :user-mbti="userMbti || ''"
          :countdown-seconds="10"
          @unlock="onRewardedAdComplete"
        />

        <!-- 이전 보상형 광고 다이얼로그 (현재 v-if=false) -->
        <RewardedAdDialog
          v-if="false"
          v-model="showRewardedDialog"
          :session-id="sessionId"
          @rewarded="onRewardedAdComplete"
          @use-points="goToPoints"
        />

        <!-- 공유 카드 -->
        <ShareCard
          v-model="showShareCard"
          :reading="interpretation"
          :cards="selectedCards.map(c => c.name)"
        />

        <!-- 프리미엄 모달 -->
        <AdModal
          v-model="showAdModal"
          @ad-clicked="onAdClicked"
        />
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import CardPicker from '@/components/CardPicker.vue'
import ReadingLoadingScreen from '@/components/ReadingLoadingScreen.vue'
import AdSenseBlock from '@/components/AdSenseBlock.vue'
import LinkpriceAdBlock from '@/components/LinkpriceAdBlock.vue'
import FollowupLoadingCard from '@/components/FollowupLoadingCard.vue'
import AdModal from '@/components/AdModal.vue'
import RewardedAdDialog from '@/components/RewardedAdDialog.vue'
import AdUnlockDialog from '@/components/AdUnlockDialog.vue'
import ShareCard from '@/components/ShareCard.vue'
import { useAuthStore } from '@/stores/authStore'
import { cardDatabase } from '@/data/cardDatabase'
import { trackReadingStarted, trackReadingCompleted, trackShareClicked, trackDailyLimitReached, trackSubscriptionViewed, trackRewardedAdWatched } from '@/utils/analytics'
import { useCrisisDetection } from '@/composables/useCrisisDetection'
import { matchAdCategory, isSensitiveQuestion } from '@/utils/categoryMatcher'

const { checkText: checkCrisisText } = useCrisisDetection()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const isPremium = computed(() => authStore.isPremium)

// Dialogs
const showRewardedDialog = ref(false)
const showAdUnlockDialog = ref(false)
const showShareCard = ref(false)
const showAdModal = ref(false)
let readingCount = 0

// State
const currentStep = ref<'question' | 'cards' | 'interpreting' | 'result'>('question')
const question = ref('')
const selectedCards = ref<Array<{ id: string; name: string; reversed: boolean }>>([])
const interpretation = ref('')
const interpretationReady = ref(false)
const queueWaiting = ref(0)  // 0이면 대기 없음, 양수면 앞에 대기 중인 인원
const isLoadingSpread = ref(false)
const sessionId = ref(localStorage.getItem('tarot_session_id') || '')
const selectedCategory = ref('')
const currentReadingId = ref<number | null>(null)
const isSaved = ref(false)

// 결과 이어보기. 무료 횟수 없이 광고 1회 시청당 1번
const followUpRemaining = ref(0)
const adsWatchedCount = ref(0)
const MAX_ADS = 1

// 질문 기반 광고 카테고리
const adCategory = computed(() => matchAdCategory(question.value))
const adSensitive = computed(() => isSensitiveQuestion(question.value))

const followUpInput = ref('')
const followUps = ref<Array<{ q: string; a: string }>>([])
const followUpLoading = ref(false)
const showFollowUpInput = ref(false)
const expandedFollowUp = ref(-1)  // -1이면 모두 접힘

// Spread info
const spreadType = ref('과거-현재-미래')
const cardCount = ref(3)
const cardPositions = ref(['과거', '현재', '미래'])

// Categories
const categories = [
  { key: '연애', emoji: '💕', name: '연애' },
  { key: '진로', emoji: '🧭', name: '진로' },
  { key: '재물', emoji: '💰', name: '재물' },
  { key: '학업', emoji: '📚', name: '학업' },
  { key: '건강', emoji: '💪', name: '건강' },
  { key: '기타', emoji: '✨', name: '기타' },
]

// Example questions
const exampleQuestions = [
  { emoji: '💕', text: '좋아하는 사람이 날 어떻게 생각할까?', category: '연애' },
  { emoji: '💌', text: '썸남한테 먼저 연락해도 될까?', category: '연애' },
  { emoji: '💔', text: '전 애인이 자꾸 생각나', category: '연애' },
  { emoji: '📚', text: '이번 시험 결과가 어떻게 나올까?', category: '학업' },
  { emoji: '🤝', text: '친구랑 멀어진 것 같아 어떡하지?', category: '기타' },
  { emoji: '🧭', text: '지금 하는 일이 맞는 방향일까?', category: '진로' },
  { emoji: '💰', text: '올해 재물운은 어떨까?', category: '재물' },
  { emoji: '💪', text: '건강이 걱정돼', category: '건강' },
]

const filteredExamples = computed(() => {
  if (!selectedCategory.value) return exampleQuestions.slice(0, 6)
  return exampleQuestions.filter(e => e.category === selectedCategory.value).slice(0, 6)
})

const placeholderText = computed(() => t('readingView.questionPlaceholder'))

const formattedInterpretation = computed(() => {
  return interpretation.value
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
})

const stepCompleted = (step: string) => {
  const order = ['question', 'cards', 'interpreting', 'result']
  const currentIndex = order.indexOf(currentStep.value)
  const stepIndex = order.indexOf(step)
  return stepIndex < currentIndex
}

const goToHome = () => {
  router.push('/')
}

const selectCategory = (key: string) => {
  selectedCategory.value = selectedCategory.value === key ? '' : key
}

const selectExample = (text: string) => {
  question.value = text
}

const submitQuestion = async () => {
  if (!question.value.trim()) return

  // CardDetail에서 카드를 가지고 들어온 경우 스프레드/카드 뽑기 생략
  if (selectedCards.value.length > 0) {
    currentStep.value = 'interpreting'
    interpretationReady.value = false
    trackReadingStarted('card_detail_with_question')
    await getInterpretation()
    return
  }

  isLoadingSpread.value = true

  try {
    const response = await axios.post('/api/select_spread', {
      question: question.value
    })
    spreadType.value = response.data.spreadType
    cardCount.value = response.data.cardCount
    cardPositions.value = response.data.cardPositions
  } catch (error) {
    spreadType.value = '과거-현재-미래'
    cardCount.value = 3
    cardPositions.value = ['과거', '현재', '미래']
  } finally {
    isLoadingSpread.value = false
  }

  currentStep.value = 'cards'
  trackReadingStarted('reading_page')
}

const onCardsSelected = async (cardKeys: string[]) => {
  selectedCards.value = cardKeys.map(key => {
    const isReversed = key.endsWith('_r')
    const baseKey = key.replace('_r', '')
    const cardInfo = cardDatabase[baseKey]

    return {
      id: key,
      name: cardInfo?.name?.replace(/^\d+\.\s*/, '').split(' (')[0] || baseKey,
      reversed: isReversed
    }
  })

  currentStep.value = 'interpreting'
  interpretationReady.value = false

  await getInterpretation()
}

const showResult = () => {
  currentStep.value = 'result'
  trackReadingCompleted(spreadType.value, cardCount.value)
  maybeShowAd()
}

const getInterpretation = async () => {
  interpretation.value = ''
  queueWaiting.value = 0

  try {
    // 자살/자해 키워드 감지 시 안내 배너
    checkCrisisText(question.value)

    const cardIds = selectedCards.value.map(card => card.id)

    const response = await fetch('/api/interpret', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: question.value,
        cards: cardIds,
        session_id: sessionId.value,
        conversation_history: [],
        // chatStore를 안 거치는 직접 fetch라 MBTI를 여기서 넣어줘야 함
        context_info: {
          mbti: (typeof window !== 'undefined' && localStorage.getItem('serapina_mbti')) || undefined,
        },
        spread_info: {
          spreadType: spreadType.value,
          cardCount: cardCount.value,
          cardPositions: cardPositions.value
        }
      })
    })

    if (!response.ok) throw new Error('Interpretation failed')

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    while (reader) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue

          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'queue') {
              // 동시 처리 대기 중
              queueWaiting.value = parsed.waiting || 1
              continue
            }
            if (parsed.content) {
              queueWaiting.value = 0
              interpretation.value += parsed.content
            }
            if (parsed.session_id) {
              sessionId.value = parsed.session_id
              localStorage.setItem('tarot_session_id', parsed.session_id)
            }
            if (parsed.reading_id) {
              currentReadingId.value = parsed.reading_id
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } catch (error) {
    console.error('Interpretation error:', error)
    interpretation.value = t('readingView.errors.interpretFailed')
  } finally {
    interpretationReady.value = true
  }
}

const requestPremiumReading = async () => {
  // premium 플래그로 interpret 재호출
  const cardIds = selectedCards.value.map(card => card.id)

  interpretation.value = ''
  queueWaiting.value = 0
  currentStep.value = 'interpreting'
  interpretationReady.value = false

  try {
    const response = await fetch('/api/interpret', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: question.value,
        cards: cardIds,
        session_id: sessionId.value,
        conversation_history: [],
        context_info: {
          mbti: (typeof window !== 'undefined' && localStorage.getItem('serapina_mbti')) || undefined,
        },
        spread_info: {
          spreadType: spreadType.value,
          cardCount: cardCount.value,
          cardPositions: cardPositions.value
        },
        reading_type: 'premium',
        use_points: true
      })
    })

    if (!response.ok) throw new Error('Premium interpretation failed')

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    while (reader) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue

          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'queue') {
              queueWaiting.value = parsed.waiting || 1
              continue
            }
            if (parsed.content) {
              queueWaiting.value = 0
              interpretation.value += parsed.content
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } catch (error) {
    console.error('Premium interpretation error:', error)
    interpretation.value = t('readingView.errors.premiumFailed')
  } finally {
    interpretationReady.value = true
  }
}

// Pre-load all card images
const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

const getCardImageUrl = (cardId: string) => {
  const baseId = cardId.replace('_r', '')
  const imagePath = `../assets/cards/${baseId}.jpg`
  return cardImages[imagePath] || cardImages['../assets/cards/maj00.jpg'] || ''
}

// 광고/공유/구독
const openShareCard = () => {
  trackShareClicked('share_card')
  showShareCard.value = true
}

const goToSubscription = () => {
  trackSubscriptionViewed('reading_page')
  if (authStore.isLoggedIn) {
    router.push('/subscription')
  } else {
    router.push({ path: '/login', query: { redirect: '/subscription' } })
  }
}

const goToPoints = () => {
  router.push('/points')
}

const onRewardedAdComplete = () => {
  trackRewardedAdWatched()
  followUpRemaining.value += 1
  adsWatchedCount.value += 1
}

// LLM에는 questionForAI, 화면에는 labelForUI를 씀
const runFollowUp = async (questionForAI: string, labelForUI: string) => {
  if (followUpRemaining.value <= 0 || followUpLoading.value) return
  followUpLoading.value = true
  followUps.value.push({ q: labelForUI, a: '' })
  const idx = followUps.value.length - 1
  expandedFollowUp.value = idx  // 이전 항목은 자동으로 접힘
  try {
    const response = await fetch('/api/interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: questionForAI,
        // 기존 카드를 같이 보내야 다른 카드로 해석하지 않음
        cards: selectedCards.value.map(c => c.id),
        session_id: sessionId.value,
        context_info: {
          mbti: (typeof window !== 'undefined' && localStorage.getItem('serapina_mbti')) || undefined,
          // 방금 push했으므로 length가 현재 회차. 백엔드에서 회차별로 깊이 조절
          followup_depth: followUps.value.length,
        },
        conversation_history: [
          { role: 'user', content: question.value },
          { role: 'assistant', content: interpretation.value },
          // 중복 답변 방지용. 방금 push한 빈 항목은 제외
          ...followUps.value.slice(0, -1).flatMap(fu => [
            { role: 'user', content: fu.q },
            { role: 'assistant', content: fu.a }
          ])
        ]
      })
    })
    if (!response.ok) throw new Error('follow-up failed')
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let text = ''
    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      for (const line of decoder.decode(value).split('\n')) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6)
        if (data === '[DONE]') continue
        try {
          const parsed = JSON.parse(data)
          if (parsed.content) {
            text += parsed.content
            // 모델이 가끔 마크다운 강조를 섞어서 제거
            followUps.value[idx].a = text.replace(/\*\*/g, '').replace(/__/g, '')
          }
        } catch {
          // skip invalid JSON
        }
      }
    }
    followUpRemaining.value--
  } catch {
    followUps.value[idx].a = '앗, 잠깐 문제가 생겼어. 다시 시도해 줄래?'
  } finally {
    followUpLoading.value = false
  }
}

// 더 물어보기: 사용자가 직접 입력한 질문
const askFollowUp = () => {
  const q = followUpInput.value.trim()
  if (!q) return
  followUpInput.value = ''
  showFollowUpInput.value = false
  runFollowUp(q, q)
}

// 더 깊게: 방금 리딩 심화
const deepenReading = () => {
  runFollowUp('방금 본 타로 리딩을 좀 더 깊고 자세하게 풀어줘.', '🔍 더 깊은 해석')
}

const onAdClicked = () => {
  // AdModal 클릭 추적
}

const maybeShowAd = () => {
  // 구독 유도 AdModal은 로그인 UI 숨김으로 비활성화
  if (readingCount >= 3) {
    trackDailyLimitReached()
  }
  readingCount++
}

const saveReading = async () => {
  if (!authStore.isLoggedIn) {
    router.push({ path: '/login', query: { redirect: '/reading' } })
    return
  }
  if (!currentReadingId.value) return
  try {
    await axios.post('/api/save-reading', {
      reading_id: currentReadingId.value,
      session_id: sessionId.value
    })
    isSaved.value = true
  } catch {
    // ignore
  }
}

const resetToQuestion = () => {
  question.value = ''
  selectedCards.value = []
  interpretation.value = ''
  interpretationReady.value = false
  selectedCategory.value = ''
  currentReadingId.value = null
  isSaved.value = false
  currentStep.value = 'question'

  // 이전 이어보기 답변이 남아 있던 문제 때문에 같이 초기화
  followUps.value = []
  followUpRemaining.value = 0
  adsWatchedCount.value = 0
  followUpInput.value = ''
  showFollowUpInput.value = false
  expandedFollowUp.value = -1
  followUpLoading.value = false

  // submitQuestion에서 다시 정하지만 기본값으로 되돌려 둠
  spreadType.value = '과거-현재-미래'
  cardCount.value = 3
  cardPositions.value = ['과거', '현재', '미래']

  queueWaiting.value = 0
}

onMounted(() => {
  if (!sessionId.value) {
    sessionId.value = crypto.randomUUID()
    localStorage.setItem('tarot_session_id', sessionId.value)
  }

  // Check for daily fortune mode
  const queryDaily = route.query.daily as string
  if (queryDaily === 'true') {
    question.value = '오늘 하루 어떤 일이 있을까? 오늘의 운세를 알려줘'
    spreadType.value = '오늘의 운세'
    cardCount.value = 1
    cardPositions.value = ['오늘']
    currentStep.value = 'cards'
    return
  }

  // Check for query parameters
  const queryQuestion = route.query.q as string
  if (queryQuestion) {
    question.value = queryQuestion
  }

  const queryCategory = route.query.category as string
  if (queryCategory) {
    selectedCategory.value = queryCategory
  }

  // CardDetail에서 카드를 가지고 들어온 경우. 새로 뽑지 않고 그 카드로 해석
  const queryCard = route.query.card as string
  if (queryCard) {
    const baseKey = queryCard.replace('_r', '')
    const cardInfo = cardDatabase[baseKey]
    if (cardInfo) {
      const isReversed = queryCard.endsWith('_r')
      selectedCards.value = [{
        id: queryCard,
        name: cardInfo.name?.replace(/^\d+\.\s*/, '').split(' (')[0] || baseKey,
        reversed: isReversed,
      }]
      spreadType.value = '단일 카드 의미'
      cardCount.value = 1
      cardPositions.value = ['이 카드의 의미']

      // 질문도 있으면 바로 해석
      if (queryQuestion) {
        currentStep.value = 'interpreting'
        interpretationReady.value = false
        getInterpretation()
      } else {
        // 질문 입력 후 submitQuestion에서 카드 단계 없이 바로 해석
        currentStep.value = 'question'
      }
    }
  }
})

// MBTI 셀렉터 (선택, localStorage 저장)
const mbtiEditing = ref(false)
const userMbti = ref<string | null>(
  (typeof window !== 'undefined' && localStorage.getItem('serapina_mbti')) || null
)
const mbtiOptions = [
  'INFP', 'INFJ', 'INTP', 'INTJ',
  'ENFP', 'ENFJ', 'ENTP', 'ENTJ',
  'ISFP', 'ISFJ', 'ISTP', 'ISTJ',
  'ESFP', 'ESFJ', 'ESTP', 'ESTJ',
]
const onMbtiChange = (val: string | null) => {
  if (val) localStorage.setItem('serapina_mbti', val)
  else localStorage.removeItem('serapina_mbti')
}
</script>

<style scoped>
/* 동시 처리 대기 화면 */
.queue-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 64px 24px;
  gap: 6px;
}
.queue-spinner {
  width: 44px;
  height: 44px;
  border: 3px solid var(--shadow-purple);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: queue-spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes queue-spin {
  to { transform: rotate(360deg); }
}
.queue-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  color: #1e1b4b;
}
.queue-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}
.queue-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 8px 0 0;
}

/* 다크 미스티컬 테마 배경 */
.reading-main {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 50%, var(--bg-secondary) 100%);
  position: relative;
  color: var(--text-primary);
}

/* 배경 오브 효과 */
.reading-main::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 30%, var(--shadow-purple) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, var(--button-hover-bg) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.reading-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* 헤더 (글라스모피즘) */
.reading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 8px var(--border-color));
}

.app-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
  text-shadow: 0 0 20px var(--border-color);
}

.app-subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 2px 0 0 0;
}

.header-btn {
  color: var(--text-secondary) !important;
}

.header-btn:hover {
  color: var(--primary-color) !important;
  background: var(--button-hover-bg) !important;
}

/* 스텝 인디케이터 */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  padding: 0 20px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  opacity: 0.4;
  transition: all 0.3s;
}

.step.active, .step.completed {
  opacity: 1;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.step.active .step-num {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  color: var(--text-primary);
  border: none;
  box-shadow: 0 0 16px var(--border-color);
}

.step.completed .step-num {
  background: #10b981;
  color: var(--text-primary);
  border: none;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.step-label {
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.step-line {
  width: 28px;
  height: 2px;
  background: var(--border-color);
  margin: 0 6px;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.step-line.active {
  background: linear-gradient(90deg, #10b981, var(--primary-color));
  box-shadow: 0 0 8px var(--border-color);
}

/* Step Sections */
.step-section {
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 질문 섹션 */
.question-card {
  background: var(--card-bg);
  border-radius: 24px;
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 32px 24px;
  text-align: center;
}

.question-header {
  margin-bottom: 24px;
}

.crystal-ball {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--button-hover-bg) 0%, var(--shadow-purple) 100%);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  box-shadow: 0 0 30px var(--shadow-purple), inset 0 0 20px var(--button-hover-bg);
  animation: crystalPulse 3s ease-in-out infinite;
}

@keyframes crystalPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 30px var(--shadow-purple), inset 0 0 20px var(--button-hover-bg); }
  50% { transform: scale(1.05); box-shadow: 0 0 40px var(--shadow-purple), inset 0 0 25px var(--button-hover-bg); }
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.section-subtitle {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0;
}

/* 카테고리 알약 버튼 */
.category-pills {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.cat-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.85rem;
  font-weight: 500;
  color: rgba(232, 223, 245, 0.8);
}

.cat-pill:hover {
  background: var(--button-hover-bg);
  border-color: var(--border-color);
}

.cat-pill.active {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  border-color: transparent;
  color: var(--text-primary);
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.3);
}

.cat-emoji {
  font-size: 1rem;
}

.input-wrapper {
  margin-bottom: 20px;
}

/* 질문 입력 필드 */
.question-input :deep(.v-field) {
  border-radius: 16px;
  font-size: 1rem;
  background: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
  transition: all 0.3s ease;
}

.question-input :deep(.v-field__overlay) {
  background: transparent !important;
  opacity: 0 !important;
}

.question-input :deep(.v-field__input) {
  padding: 12px 16px !important;
  min-height: 48px;
  font-size: 0.95rem;
  color: var(--text-primary) !important;
}

.question-input :deep(.v-field__input::placeholder) {
  color: var(--text-muted);
}

.question-input :deep(.v-field--focused) {
  box-shadow: 0 0 0 2px var(--border-color), 0 0 20px var(--shadow-purple) !important;
  border-color: var(--border-color) !important;
}

.submit-btn {
  width: 100%;
  height: 56px !important;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 16px;
  text-transform: none;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%) !important;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.35), 0 0 40px rgba(139, 92, 246, 0.15);
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.5), 0 0 50px rgba(139, 92, 246, 0.2);
}

.submit-btn:disabled {
  opacity: 0.35;
}

/* 예시 질문 */
.example-questions {
  margin-top: 20px;
  padding: 24px;
  background: var(--card-bg);
  border: 1px solid var(--card-bg);
  border-radius: 20px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.examples-title {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 16px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.example-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: var(--card-bg);
  border: 1px solid var(--card-bg);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.example-item:hover {
  background: var(--button-hover-bg);
  border-color: var(--border-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--shadow-purple);
}

.example-emoji {
  font-size: 1.2rem;
}

.example-text {
  font-size: 0.85rem;
  color: rgba(232, 223, 245, 0.85);
  flex: 1;
}

/* Result Section */
.result-section {
  animation: fadeInUp 0.6s ease;
}

/* 스프레드 헤더 */
.spread-header {
  text-align: center;
  margin-bottom: 24px;
}

.spread-icon {
  font-size: 3rem;
  margin-bottom: 8px;
  filter: drop-shadow(0 0 12px var(--border-color));
}

.spread-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  text-shadow: 0 0 20px var(--border-color);
}

.spread-subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}

/* 질문 리캡 카드 */
.question-recap-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 28px;
  text-align: center;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.question-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.question-content {
  font-size: 1.1rem;
  color: var(--text-primary);
  line-height: 1.6;
}

.quote-mark {
  color: var(--primary-color);
  font-size: 1.3rem;
  font-weight: 700;
  text-shadow: 0 0 10px var(--border-color);
}

/* Cards Showcase */
.cards-showcase {
  margin-bottom: 28px;
}

.cards-showcase .cards-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.card-showcase-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: cardReveal 0.6s ease forwards;
  opacity: 0;
}

@keyframes cardReveal {
  from { opacity: 0; transform: translateY(20px) scale(0.9); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 카드 포지션 라벨 */
.card-position-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  background: var(--button-hover-bg);
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  border: 1px solid var(--border-color);
}

/* 카드 프레임 */
.card-frame {
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 0 20px var(--button-hover-bg);
  transition: all 0.3s ease;
  display: inline-block;
  border: 1px solid var(--button-hover-bg);
}

.card-frame:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35), 0 0 30px var(--border-color);
}

.reversed-frame {
  box-shadow: 0 8px 24px rgba(244, 63, 94, 0.2), 0 0 20px rgba(244, 63, 94, 0.1);
  border-color: rgba(244, 63, 94, 0.3);
}

.card-img {
  width: 100px;
  display: block;
  border-radius: 0;
}

.reversed-img {
  transform: rotate(180deg);
}

.card-name-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.reversed-tag {
  font-size: 0.65rem;
  color: #fb7185;
  background: rgba(244, 63, 94, 0.15);
  padding: 2px 8px;
  border-radius: 8px;
  border: 1px solid rgba(244, 63, 94, 0.2);
}

/* 해석 카드 */
.interpretation-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 24px;
}

.interpretation-header {
  background: linear-gradient(135deg, var(--shadow-purple) 0%, rgba(109, 40, 217, 0.5) 100%);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--button-hover-bg);
}

.seraphina-avatar {
  width: 50px;
  height: 50px;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 0 16px var(--button-hover-bg);
}

.interpretation-title-area {
  flex: 1;
}

.interpretation-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.interpretation-subtitle {
  font-size: 0.8rem;
  color: var(--text-primary);
  margin: 2px 0 0 0;
}

.interpretation-body {
  padding: 24px;
}

/* 해석 본문 */
.interpretation-content {
  font-size: 1rem;
  line-height: 1.9;
  color: rgba(232, 223, 245, 0.9);
}

.interpretation-content :deep(strong) {
  color: var(--primary-color);
  font-weight: 600;
}

.interpretation-content :deep(p) {
  margin-bottom: 16px;
}

.interpretation-content :deep(p:last-child) {
  margin-bottom: 0;
}

/* 컴팩트 결과 헤더 */
.result-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 24px;
  padding: 14px 18px;
  background: rgba(139, 92, 246, 0.08);
  border-left: 3px solid var(--primary-color);
  border-radius: 8px;
  flex-wrap: wrap;
}
.result-spread {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-color);
  white-space: nowrap;
}
.result-dot {
  color: var(--border-color);
}
.result-question {
  font-size: 14px;
  color: var(--text-primary);
  font-style: italic;
  flex: 1;
  min-width: 0;
  word-break: keep-all;
}

.follow-up-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
.follow-up-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0 0 14px;
}
.follow-up-item {
  margin-bottom: 14px;
}
.follow-up-q {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #e8e8e8;
  background: rgba(139, 92, 246, 0.15);
  border: none;
  border-radius: 12px;
  padding: 10px 14px;
  margin-bottom: 6px;
  cursor: pointer;
}
.fu-toggle {
  color: var(--primary-color);
  font-size: 11px;
  flex-shrink: 0;
}
.fu-q-text {
  flex: 1;
}
.follow-up-a {
  font-size: 14px;
  line-height: 1.7;
  color: #d0d0d0;
  white-space: pre-wrap;
  padding: 4px 6px 10px;
}
.fu-loading {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-size: 13px;
}
.fu-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: fu-spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes fu-spin {
  to { transform: rotate(360deg); }
}
.follow-up-buttons {
  display: flex;
  gap: 8px;
}
.follow-up-btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--button-hover-bg);
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.follow-up-btn:hover:not(:disabled) {
  background: var(--button-hover-bg);
}
.follow-up-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.follow-up-input-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.follow-up-input {
  flex: 1;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
}
.follow-up-input:focus {
  outline: none;
  border-color: var(--primary-color);
}
.follow-up-input:disabled {
  opacity: 0.6;
}
.follow-up-send {
  width: 48px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color));
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
}
.follow-up-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.follow-up-count {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 8px 0 0;
  text-align: center;
}
.follow-up-ad-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--button-hover-bg);
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sub-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  height: 52px !important;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 16px;
  text-transform: none;
  padding: 0 28px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

/* 액션 버튼 */
.premium-action {
  border-color: var(--border-color) !important;
  color: var(--primary-color) !important;
}

.premium-action:hover {
  background: var(--button-hover-bg) !important;
}

.primary-action {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%) !important;
  color: var(--text-primary) !important;
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.35);
}

.primary-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(139, 92, 246, 0.5);
}

.secondary-action {
  border-color: var(--border-color) !important;
  color: var(--text-secondary) !important;
}

.secondary-action:hover {
  background: var(--card-bg) !important;
}

/* 광고 슬롯 */
.reading-ad-slot {
  margin: 16px 0;
  display: flex;
  justify-content: center;
}

/* 프리미엄 넛지 */
.premium-nudge {
  margin: 16px 0;
}

.nudge-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--card-bg);
  border: 1px solid var(--button-hover-bg);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.nudge-content:hover {
  background: var(--button-hover-bg);
  border-color: var(--border-color);
}

.nudge-icon {
  font-size: 1.2rem;
}

.nudge-text {
  flex: 1;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

.save-action {
  border-color: var(--border-color) !important;
  color: var(--primary-color) !important;
}

.save-action:disabled {
  border-color: var(--button-hover-bg) !important;
  color: var(--border-color) !important;
  opacity: 0.8;
}

.saved-link {
  text-align: center;
  margin-top: 8px;
}

.saved-link a {
  color: var(--primary-color);
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
}

.saved-link a:hover {
  text-decoration: underline;
  color: var(--primary-color);
}

.share-action {
  border-color: var(--border-color) !important;
  color: var(--primary-color) !important;
}

/* 모바일 반응형 */
@media (max-width: 600px) {
  .reading-container {
    padding: 12px;
  }

  .question-card {
    padding: 20px 16px;
    border-radius: 20px;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .crystal-ball {
    width: 64px;
    height: 64px;
    font-size: 2rem;
  }

  .category-pills {
    gap: 6px;
  }

  .cat-pill {
    padding: 6px 12px;
    font-size: 0.8rem;
  }

  .input-wrapper {
    margin-bottom: 16px;
  }

  .question-input :deep(.v-field__input) {
    padding: 10px 14px !important;
    min-height: 44px;
    font-size: 0.9rem;
  }

  .submit-btn {
    height: 48px !important;
    font-size: 1rem;
    border-radius: 14px;
  }

  .examples-grid {
    grid-template-columns: 1fr;
  }

  .spread-title {
    font-size: 1.3rem;
  }

  .spread-icon {
    font-size: 2.5rem;
  }

  .question-recap-card {
    padding: 16px;
    margin-bottom: 20px;
  }

  .question-content {
    font-size: 1rem;
  }

  .cards-showcase .cards-row {
    gap: 12px;
  }

  .card-showcase-item {
    max-width: 100px;
  }

  .card-img {
    width: 80px;
  }

  .card-position-label {
    font-size: 0.65rem;
    padding: 3px 10px;
  }

  .card-name-label {
    font-size: 0.75rem;
  }

  .interpretation-card {
    border-radius: 20px;
  }

  .interpretation-header {
    padding: 16px 20px;
  }

  .seraphina-avatar {
    width: 42px;
    height: 42px;
    font-size: 1.2rem;
  }

  .interpretation-title {
    font-size: 1rem;
  }

  .interpretation-body {
    padding: 20px;
  }

  .interpretation-content {
    font-size: 0.95rem;
    line-height: 1.8;
  }

  .step-indicator {
    padding: 0 10px;
  }

  .step-line {
    width: 16px;
  }

  .step-label {
    font-size: 0.6rem;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions > .action-btn {
    width: 100%;
  }

  .action-btn.save-action,
  .action-btn.share-action,
  .action-btn.secondary-action {
    background: var(--card-bg) !important;
  }
}

/* D 톤 오버라이드 (LandingView와 통일) */

/* 메인 배경 */
.reading-main, .reading-container {
  background: var(--bg-primary) !important;
}
.reading-header {
  background: rgba(254, 248, 231, 0.92) !important;
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  border-bottom: 1.5px solid var(--text-primary) !important;
  color: var(--text-primary) !important;
}
.reading-header :deep(*) { color: var(--text-primary) !important; }

/* Question Section */
.question-section { background: var(--bg-primary) !important; }
.question-card {
  background: var(--card-bg) !important;
  border: 2px solid var(--text-primary) !important;
  border-radius: 20px !important;
  box-shadow: 5px 5px 0 var(--primary-color) !important;
}
.section-title { color: var(--text-primary) !important; }
.section-subtitle { color: var(--text-secondary) !important; }

/* Category Pills */
.cat-pill {
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
}
.cat-pill.active {
  background: var(--secondary-color) !important;
  color: var(--text-primary) !important;
  box-shadow: 3px 3px 0 var(--text-primary) !important;
}
.cat-pill:hover { background: var(--button-hover-bg) !important; }
.cat-name { color: var(--text-primary) !important; }

/* Question Input */
.question-input :deep(.v-field) {
  background: var(--bg-secondary) !important;
  border-radius: 16px !important;
}
.question-input :deep(.v-field__outline) { color: var(--text-primary) !important; }
.question-input :deep(.v-field__input),
.question-input :deep(textarea) {
  color: var(--text-primary) !important;
}
.question-input :deep(textarea::placeholder) {
  color: var(--text-muted) !important;
  opacity: 1;
}

/* Submit Button */
.submit-btn {
  background: var(--primary-color) !important;
  color: white !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 4px 4px 0 var(--text-primary) !important;
  font-weight: 700 !important;
}
.submit-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 6px 6px 0 var(--text-primary) !important;
}

/* Example Questions */
.examples-title { color: var(--text-secondary) !important; }
.example-item {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
}
.example-item:hover { border-color: var(--primary-color) !important; }
.example-text { color: var(--text-primary) !important; }

/* Result Section */
.result-section { background: var(--bg-primary) !important; }
.result-header { background: transparent !important; }
.result-spread, .result-question, .result-dot { color: var(--text-primary) !important; }

/* Interpretation Card */
.interpretation-card {
  background: var(--card-bg) !important;
  border: 2px solid var(--text-primary) !important;
  border-radius: 20px !important;
  box-shadow: 6px 6px 0 var(--secondary-color) !important;
}
.interpretation-title { color: var(--text-primary) !important; }
.interpretation-subtitle { color: var(--text-secondary) !important; }
.interpretation-content,
.interpretation-content :deep(p),
.interpretation-content :deep(span),
.interpretation-content :deep(div),
.interpretation-content :deep(li) {
  color: var(--text-primary) !important;
}
.interpretation-content :deep(strong) { color: var(--primary-color) !important; }

/* Result Actions */
.action-btn {
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
}
.action-btn:hover { background: var(--button-hover-bg) !important; }

/* Follow-up Section */
.follow-up-section {
  background: var(--bg-secondary) !important;
  border-top: 1px solid var(--border-color) !important;
}
.follow-up-title { color: var(--text-primary) !important; }
.follow-up-item {
  background: var(--card-bg) !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 12px !important;
}
.follow-up-q, .fu-q-text, .fu-toggle { color: var(--text-primary) !important; }
.follow-up-a, .fu-loading { color: var(--text-primary) !important; }
.follow-up-btn {
  background: var(--primary-color) !important;
  color: white !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 3px 3px 0 var(--text-primary) !important;
  font-weight: 700 !important;
}
.follow-up-btn:hover {
  transform: translateY(-2px);
  box-shadow: 5px 5px 0 var(--text-primary) !important;
}
.follow-up-input {
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
}
.follow-up-input::placeholder { color: var(--text-muted) !important; }
.follow-up-send {
  background: var(--primary-color) !important;
  color: white !important;
  border: 1.5px solid var(--text-primary) !important;
}
.follow-up-count { color: var(--text-secondary) !important; }
.follow-up-ad-btn {
  background: var(--accent-yellow) !important;
  color: var(--text-primary) !important;
  border: 2px solid var(--text-primary) !important;
  font-weight: 700 !important;
}

/* Queue Screen */
.queue-screen { background: var(--bg-primary) !important; }
.queue-title, .queue-text { color: var(--text-primary) !important; }

/* MBTI 셀렉터 */
.mbti-row {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(196, 181, 253, 0.2);
  border-radius: 14px;
  margin-bottom: 14px;
  border: 1.5px solid var(--text-primary);
}
.mbti-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.mbti-select {
  flex: 1;
  max-width: 180px;
  font-size: 0.9rem;
}
.mbti-select :deep(.v-field) {
  background: var(--card-bg) !important;
  border-radius: 999px !important;
}
.mbti-select :deep(.v-field__outline) { color: var(--text-primary) !important; }
.mbti-select :deep(.v-field__input) {
  min-height: 36px;
  padding: 4px 14px !important;
  color: var(--text-primary) !important;
  font-weight: 600;
}
.mbti-select :deep(.v-field__input input) { color: var(--text-primary) !important; }
.mbti-select :deep(.v-field__input input::placeholder) {
  color: var(--text-muted) !important;
  opacity: 1;
}
.mbti-select :deep(.v-field__append-inner .v-icon) {
  color: var(--primary-color) !important;
}

/* Interpreting, Result D 톤 */

/* Queue 대기 화면 */
.queue-desc { color: var(--text-secondary) !important; }
.queue-count { color: var(--text-muted) !important; }
.queue-spinner {
  border-color: var(--secondary-color) !important;
  border-top-color: var(--primary-color) !important;
}

/* Cards Showcase */
.cards-showcase, .cards-row, .card-showcase-item {
  background: transparent !important;
}

/* 카드 프레임: Memphis 보더 + 그림자 */
.card-frame {
  border: 2px solid var(--text-primary) !important;
  border-radius: 12px !important;
  box-shadow: 4px 4px 0 var(--secondary-color) !important;
  background: var(--card-bg) !important;
  padding: 6px !important;
}
.card-frame.reversed-frame {
  box-shadow: 4px 4px 0 var(--primary-color) !important;
}
.card-img { border-radius: 6px !important; }

/* 카드 라벨 (포지션, 이름, 역방향 태그) */
.card-position-label {
  background: var(--button-hover-bg) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--text-primary) !important;
  border-radius: 999px !important;
  padding: 4px 12px !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
}
.card-name-label {
  color: var(--text-primary) !important;
  font-weight: 700 !important;
}
.reversed-tag {
  background: var(--primary-color) !important;
  color: white !important;
  border: 1px solid var(--text-primary) !important;
  border-radius: 999px !important;
  padding: 2px 8px !important;
  font-size: 0.7em !important;
  margin-left: 6px !important;
  font-weight: 700 !important;
}

/* Seraphina 아바타 (Interpretation 헤더) */
.seraphina-avatar {
  background: var(--secondary-color) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 2px 2px 0 var(--text-primary) !important;
}
.seraphina-avatar span { color: var(--text-primary) !important; }
.interpretation-header {
  background: transparent !important;
}

/* Sub Actions (공유, 홈 버튼) */
.sub-actions { background: transparent !important; }
.action-btn.primary-action {
  background: var(--primary-color) !important;
  color: white !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 4px 4px 0 var(--text-primary) !important;
  font-weight: 700 !important;
}
.action-btn.primary-action:hover {
  transform: translateY(-2px);
  box-shadow: 6px 6px 0 var(--text-primary) !important;
}
.action-btn.share-action {
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
}
.action-btn.secondary-action {
  color: var(--text-secondary) !important;
}

/* Follow-up Section D 톤 */
.follow-up-section {
  background: var(--bg-secondary) !important;
  border: 2px solid var(--text-primary) !important;
  border-radius: 16px !important;
  padding: 22px 20px !important;
  margin-top: 22px !important;
  margin-bottom: 36px !important;
  box-shadow: 5px 5px 0 var(--primary-color) !important;
}
.result-actions { margin-top: 8px !important; }
.follow-up-title {
  color: var(--text-primary) !important;
  font-size: 1.1rem !important;
  font-weight: 800 !important;
  margin: 0 0 16px 0 !important;
  letter-spacing: -0.015em !important;
}

/* 액션 버튼 2개 (2열 그리드) */
.follow-up-buttons {
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 10px !important;
  margin-bottom: 4px !important;
}
.follow-up-btn {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 3px 3px 0 var(--text-primary) !important;
  border-radius: 14px !important;
  padding: 14px 10px !important;
  font-weight: 700 !important;
  cursor: pointer;
  transition: 0.15s ease;
}
.follow-up-btn:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  box-shadow: 5px 5px 0 var(--text-primary) !important;
}
.follow-up-btn.deepen { background: var(--secondary-color) !important; }
.follow-up-btn.ask { background: var(--primary-color) !important; color: white !important; }
.follow-up-btn-icon { font-size: 1.4rem !important; }
.follow-up-btn-text { font-size: 0.9rem !important; font-weight: 700 !important; }
.follow-up-btn:disabled {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: 1px 1px 0 var(--text-primary) !important;
}

/* 입력 행 */
.follow-up-input-row {
  display: flex !important;
  gap: 8px !important;
  margin-top: 12px !important;
}
.follow-up-input {
  flex: 1 !important;
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 999px !important;
  padding: 10px 16px !important;
  font-size: 0.95rem !important;
  outline: none !important;
}
.follow-up-input::placeholder {
  color: var(--text-muted) !important;
  font-style: italic !important;
}
.follow-up-send {
  background: var(--primary-color) !important;
  color: white !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 999px !important;
  width: 44px !important;
  height: 44px !important;
  font-size: 1.2rem !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
}
.follow-up-send:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

/* 카운트 */
.follow-up-count {
  color: var(--text-secondary) !important;
  font-size: 0.8rem !important;
  text-align: center !important;
  margin: 10px 0 0 0 !important;
}

/* 광고 보고 더 보기 버튼 */
.follow-up-ad-btn {
  background: var(--accent-yellow) !important;
  color: var(--text-primary) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 3px 3px 0 var(--text-primary) !important;
  border-radius: 12px !important;
  padding: 12px 16px !important;
  font-weight: 700 !important;
  width: 100% !important;
  cursor: pointer !important;
}

/* 펼쳐진 답변들 (액션 버튼 위) */
.follow-up-answers {
  margin-bottom: 18px !important;
  padding-bottom: 18px !important;
  border-bottom: 1.5px dashed var(--text-primary) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
}
.follow-up-item {
  background: var(--card-bg) !important;
  border: 1.5px solid var(--text-primary) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}
.follow-up-q {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  width: 100% !important;
  background: transparent !important;
  border: none !important;
  color: var(--text-primary) !important;
  padding: 12px 14px !important;
  text-align: left !important;
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
}
.fu-toggle { color: var(--primary-color) !important; font-weight: 700 !important; }
.fu-q-text { color: var(--text-primary) !important; }
.follow-up-a {
  padding: 0 14px 14px 14px !important;
  color: var(--text-primary) !important;
  font-size: 0.95rem !important;
  line-height: 1.65 !important;
  white-space: pre-wrap !important;
}
.fu-loading {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  color: var(--text-secondary) !important;
  font-style: italic !important;
}

/* 모바일 */
@media (max-width: 480px) {
  .follow-up-section { padding: 18px 16px !important; }
  .follow-up-btn { padding: 12px 8px !important; }
  .follow-up-btn-text { font-size: 0.85rem !important; }
}

/* MBTI 미니 박스 (카드 단계 상단) */
.mbti-mini-section {
  max-width: 720px;
  margin: 0 auto 20px;
  padding: 0 16px;
}

.mbti-mini-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: var(--secondary-color);
  border: 2px solid var(--text-primary);
  border-radius: 14px;
  box-shadow: 3px 3px 0 var(--text-primary);
  flex-wrap: wrap;
}

.mini-chip-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-size: 0.92rem;
  font-weight: 600;
}

.mini-chip-label strong {
  color: var(--primary-color);
  font-weight: 800;
  font-size: 1rem;
  letter-spacing: 0.02em;
}

.mini-chip-emoji {
  font-size: 1.1rem;
}

.mini-chip-change {
  background: var(--card-bg);
  border: 1.5px solid var(--text-primary);
  border-radius: 10px;
  padding: 6px 12px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s;
}

.mini-chip-change:hover {
  transform: translateY(-1px);
  box-shadow: 2px 2px 0 var(--text-primary);
}

.mbti-mini-select {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 18px;
  background: var(--accent-yellow);
  border: 2px solid var(--text-primary);
  border-radius: 14px;
  box-shadow: 4px 4px 0 var(--text-primary);
}

.mini-select-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text-primary);
}

.mini-select :deep(.v-field) {
  background: var(--card-bg) !important;
  border-radius: 10px !important;
}

.mini-select :deep(.v-field__outline) {
  --v-field-border-width: 1.5px;
  --v-field-border-opacity: 1;
  color: var(--text-primary) !important;
}

.mini-skip {
  align-self: flex-end;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .mbti-mini-chip {
    padding: 10px 14px;
  }
  .mini-chip-label {
    font-size: 0.85rem;
  }
  .mini-chip-change {
    font-size: 0.75rem;
    padding: 5px 10px;
  }
}

</style>
