<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              icon
              variant="flat"
              :to="backLink"
              class="back-button"
            >
              <v-icon size="28">mdi-arrow-left</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ card?.name || t('cards.detail.noCard') }}</h1>
              <p class="page-subtitle">{{ card?.subtitle || '' }}</p>
            </div>
            <v-btn
              v-if="card"
              icon
              variant="text"
              @click="shareCard"
              class="share-btn-header"
            >
              <v-icon>mdi-share-variant</v-icon>
            </v-btn>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content" v-if="card">
          <div class="content-container">

            <!-- Card Image Hero -->
            <div class="card-hero">
              <div class="card-image-wrapper">
                <img
                  :src="cardImageUrl"
                  :alt="card.name"
                  class="card-image"
                />
              </div>
              <div class="card-hero-info">
                <div class="meta-pills">
                  <span class="meta-pill">{{ card.category }}</span>
                  <span v-if="card.suit" class="meta-pill">{{ card.suit }}</span>
                  <span v-if="card.element" class="meta-pill accent">{{ card.element }}</span>
                </div>
                <p class="card-subtitle-hero">{{ card.subtitle }}</p>
              </div>
            </div>

            <!-- Card Description -->
            <div class="info-section">
              <h2 class="section-title">{{ t('cards.detail.descriptionTitle') }}</h2>
              <p class="section-text">{{ card.description }}</p>
            </div>

            <!-- Upright Meaning -->
            <div class="info-section">
              <div class="meaning-header upright">
                <v-icon size="20" color="var(--primary-color)">mdi-arrow-up-bold-circle</v-icon>
                <h2 class="section-title">{{ t('cards.detail.uprightTitle') }}</h2>
              </div>
              <p class="section-text">{{ card.uprightMeaning }}</p>
              <div class="keywords-grid">
                <span
                  v-for="keyword in card.uprightKeywords"
                  :key="keyword"
                  class="keyword-chip upright-chip"
                >
                  {{ keyword }}
                </span>
              </div>
            </div>

            <!-- Reversed Meaning -->
            <div class="info-section">
              <div class="meaning-header reversed">
                <v-icon size="20" color="#E11D48">mdi-arrow-down-bold-circle</v-icon>
                <h2 class="section-title">{{ t('cards.detail.reversedTitle') }}</h2>
              </div>
              <p class="section-text">{{ card.reversedMeaning }}</p>
              <div class="keywords-grid">
                <span
                  v-for="keyword in card.reversedKeywords"
                  :key="keyword"
                  class="keyword-chip reversed-chip"
                >
                  {{ keyword }}
                </span>
              </div>
            </div>

            <!-- Inline CTA (맥락형 퀵 질문 칩) -->
            <div class="inline-cta">
              <p class="inline-cta-question">{{ cardKoreanName }} 카드가 궁금하다면?</p>
              <p class="inline-cta-subtext">세라피나가 너의 상황에 맞게 해석해줄게</p>
              <div class="quick-question-chips">
                <v-btn
                  v-for="q in quickQuestions"
                  :key="q"
                  variant="outlined"
                  color="var(--primary-color)"
                  rounded="pill"
                  size="small"
                  class="quick-q-chip"
                  :to="{ name: 'reading', query: { q, card: card?.id } }"
                  @click="trackCtaClick('quick_question', 'card_detail')"
                >
                  {{ q }}
                </v-btn>
              </div>
              <v-btn
                color="var(--primary-color)"
                variant="flat"
                rounded="pill"
                size="large"
                :to="{ name: 'reading', query: { card: card?.id } }"
                class="inline-cta-btn"
                style="margin-top: 1rem;"
                @click="trackCtaClick('inline_cta', 'card_detail'); trackReadingStarted('card_detail_inline')"
              >
                <v-icon start>mdi-cards-playing-outline</v-icon>
                무료로 리딩 받기
              </v-btn>
            </div>

            <!-- Related Cards -->
            <div class="related-section" v-if="relatedCards.length > 0">
              <h2 class="section-title">{{ t('cards.detail.relatedTitle') }}</h2>
              <div class="related-grid">
                <router-link
                  v-for="rc in relatedCards"
                  :key="rc.id"
                  :to="`/cards/${rc.id}`"
                  class="related-card"
                >
                  <img :src="getCardImage(rc.id)" :alt="rc.name" class="related-card-img" />
                  <span class="related-card-name">{{ rc.name.split(' (')[0] }}</span>
                </router-link>
              </div>
            </div>

            <!-- Share Section -->
            <div class="share-section">
              <p class="share-label">{{ t('cards.detail.shareLabel') }}</p>
              <div class="share-buttons">
                <v-btn variant="outlined" rounded="pill" size="small" @click="shareCard">
                  <v-icon start size="16">mdi-share-variant</v-icon>
                  {{ t('cards.detail.shareButton') }}
                </v-btn>
                <v-btn variant="outlined" rounded="pill" size="small" @click="copyLink">
                  <v-icon start size="16">mdi-link-variant</v-icon>
                  {{ t('cards.detail.copyLinkButton') }}
                </v-btn>
              </div>
            </div>

            <!-- Related Guides -->
            <div class="related-guides">
              <h2 class="section-heading">관련 타로 가이드</h2>
              <div class="guide-link-grid">
                <router-link to="/guides/love" class="guide-link-card" @click="trackCtaClick('guide_link', 'card_detail')">💕 연애운 가이드</router-link>
                <router-link to="/guides/career" class="guide-link-card" @click="trackCtaClick('guide_link', 'card_detail')">💼 직업운 가이드</router-link>
                <router-link to="/guides/money" class="guide-link-card" @click="trackCtaClick('guide_link', 'card_detail')">💰 금전운 가이드</router-link>
                <router-link to="/guides/study" class="guide-link-card" @click="trackCtaClick('guide_link', 'card_detail')">📚 학업운 가이드</router-link>
              </div>
            </div>

            <!-- Bottom CTA -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" />
                <h3>{{ t('cards.detail.ctaTitle', { cardName: card.name }) }}</h3>
                <p>{{ t('cards.detail.ctaDescription', { cardName: card.name }) }}</p>
                <v-btn
                  size="large"
                  color="var(--primary-color)"
                  variant="flat"
                  rounded="pill"
                  :to="{ name: 'reading', query: { card: card?.id } }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'card_detail'); trackReadingStarted('card_detail_bottom')"
                >
                  {{ t('cards.detail.ctaButton') }}
                  <v-icon end>mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </div>
          </div>

          <div style="margin-top: 16px;">
            <AdSenseBlock slot="1696071761" />
          </div>
        </div>

        <!-- Not Found -->
        <div class="page-content" v-else>
          <div class="content-container">
            <div class="not-found">
              <div class="not-found-icon">🔍</div>
              <h2>{{ t('cards.detail.notFoundTitle') }}</h2>
              <v-btn
                size="large"
                color="var(--primary-color)"
                variant="flat"
                rounded="pill"
                :to="{ name: 'cards' }"
                class="mt-6"
              >
                {{ t('cards.detail.backButton') }}
              </v-btn>
            </div>
          </div>
        </div>
      </div>

      <!-- Snackbar (alert 대체) -->
      <v-snackbar v-model="snackbar" :timeout="2000" color="var(--primary-color)" rounded="pill">
        {{ snackbarText }}
      </v-snackbar>
    </div>

    <!-- 스크롤 기반 모바일 플로팅 CTA -->
    <Teleport to="body">
      <Transition name="slide-up">
        <div v-if="showFloatingCta" class="floating-cta">
          <v-btn
            color="var(--primary-color)"
            variant="flat"
            rounded="pill"
            block
            size="large"
            :to="{ name: 'reading', query: { q: cardKoreanName + ' 카드가 내 상황에서 의미하는 게 뭐야?', card: card?.id } }"
            class="floating-cta-btn"
            @click="trackCtaClick('floating_cta', 'card_detail'); trackReadingStarted('card_detail_floating')"
          >
            이 카드로 무료 리딩 받기
            <v-icon end>mdi-arrow-right</v-icon>
          </v-btn>
        </div>
      </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { cardDatabase } from '@/data/cardDatabase'
import AdSenseBlock from '@/components/AdSenseBlock.vue'
import { trackCtaClick, trackReadingStarted, trackShareClicked, trackShareCompleted } from '@/utils/analytics'

const { t } = useI18n()
const route = useRoute()
const cardId = computed(() => route.params.id as string)
const card = computed(() => cardDatabase[cardId.value])

const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

const cardImageUrl = computed(() => {
  const imagePath = `../assets/cards/${cardId.value}.jpg`
  return cardImages[imagePath] || cardImages['../assets/cards/maj00.jpg'] || ''
})

const getCardImage = (id: string) => {
  const imagePath = `../assets/cards/${id}.jpg`
  return cardImages[imagePath] || ''
}

// 맥락형 퀵 질문
const cardKoreanName = computed(() => card.value?.name.split(' (')[0] || '')
const quickQuestions = computed(() => {
  const name = cardKoreanName.value
  return [
    `${name} 카드가 연애에서 의미하는 것은?`,
    `${name} 카드가 나왔는데 어떻게 해야 하나요?`,
    `오늘 ${name} 카드의 메시지가 궁금해요`,
  ]
})

// Snackbar (alert 대체)
const snackbar = ref(false)
const snackbarText = ref('')

// 스크롤 기반 플로팅 CTA
const showFloatingCta = ref(false)
const handleScroll = () => {
  showFloatingCta.value = window.scrollY > 400
}

const relatedCards = computed(() => {
  if (!card.value) return []
  const allCards = Object.entries(cardDatabase)
  let related: Array<{ id: string; name: string }> = []

  if (card.value.suit) {
    related = allCards
      .filter(([id, c]) => c.suit === card.value!.suit && id !== cardId.value)
      .slice(0, 4)
      .map(([id, c]) => ({ id, name: c.name }))
  } else {
    related = allCards
      .filter(([id, c]) => c.category === card.value!.category && id !== cardId.value)
      .slice(0, 4)
      .map(([id, c]) => ({ id, name: c.name }))
  }
  return related
})

const backLink = computed(() => {
  if (!card.value) return { name: 'cards' }
  return card.value.category === '메이저 아르카나'
    ? { name: 'major-arcana' }
    : { name: 'minor-arcana' }
})

const shareCard = async () => {
  if (!card.value) return
  trackShareClicked('card_detail')
  const shareText = `${card.value.name}\n${card.value.subtitle}\n\nhttps://serapina.kr/cards/${cardId.value}`
  if (navigator.share) {
    try {
      await navigator.share({ title: card.value.name, text: shareText })
      trackShareCompleted('native')
    } catch { /* cancelled */ }
  } else {
    await copyLink()
  }
}

const copyLink = async () => {
  trackShareClicked('copy_link')
  try {
    await navigator.clipboard.writeText(`https://serapina.kr/cards/${cardId.value}`)
    snackbarText.value = t('cards.detail.linkCopied')
    snackbar.value = true
    trackShareCompleted('copy')
  } catch { /* fallback */ }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  // JSON-LD 구조화 데이터
  if (card.value) {
    const jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'Article',
      'headline': `${card.value.name} 타로 카드 의미`,
      'description': card.value.description,
      'author': { '@type': 'Organization', 'name': '세라피나 타로' },
      'publisher': { '@type': 'Organization', 'name': '세라피나 타로', 'url': 'https://serapina.kr' }
    }
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.textContent = JSON.stringify(jsonLd)
    document.head.appendChild(script)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

useSeoMeta(
  card.value
    ? t('seo.cardDetail.titleTemplate', { cardName: card.value.name })
    : t('seo.cardDetail.fallbackTitle'),
  card.value
    ? t('seo.cardDetail.descriptionTemplate', {
        cardName: card.value.name,
        description: card.value.description
      })
    : t('seo.cardDetail.fallbackDescription'),
  card.value
    ? t('seo.cardDetail.keywordsTemplate', {
        cardName: card.value.name,
        category: card.value.category,
        keywords: card.value.uprightKeywords.join(', ')
      })
    : t('seo.cardDetail.fallbackKeywords')
)
</script>

<style scoped>
.app-main {
  height: auto;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  min-height: 100vh;
  padding: 0;
}

.page-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.page-header {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 1.25rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 700px;
  margin: 0 auto;
}

.back-button {
  background: var(--border-color) !important;
  color: var(--text-primary) !important;
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color) !important;
}

.back-button .v-icon {
  color: var(--primary-color) !important;
}

.header-text { flex: 1; min-width: 0; }

.page-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.page-subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0.2rem 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.share-btn-header {
  color: var(--text-primary) !important;
  flex-shrink: 0;
}

.share-btn-header:hover {
  color: var(--text-primary) !important;
  background: var(--border-color) !important;
}

.page-content {
  flex: 1;
  padding: 0 1rem 2rem;
  max-width: 700px;
  width: 100%;
  margin: 0 auto;
}

.content-container {
  margin: 0 auto;
}

/* Card Image Hero */
.card-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0 1.5rem;
}

.card-image-wrapper {
  width: 180px;
  height: 309px;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 12px 40px var(--shadow-purple), 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.card-image-wrapper:hover {
  transform: scale(1.03);
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-hero-info {
  text-align: center;
  margin-top: 1.25rem;
}

.meta-pills {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.meta-pill {
  background: var(--button-hover-bg);
  color: var(--primary-color);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.meta-pill.accent {
  background: rgba(234, 88, 12, 0.15);
  color: #fb923c;
  border-color: rgba(234, 88, 12, 0.3);
}

.card-subtitle-hero {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 400px;
  margin: 0 auto;
}

/* Info Sections */
.info-section {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.info-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.section-heading {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.section-text {
  font-size: 0.9rem;
  color: var(--text-primary);
  line-height: 1.8;
  margin: 0 0 1rem 0;
}

.meaning-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.meaning-header .section-title {
  margin: 0;
}

.keywords-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-chip {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.upright-chip {
  background: var(--button-hover-bg);
  color: var(--primary-color);
  border: 1px solid var(--border-color);
}

.reversed-chip {
  background: rgba(225, 29, 72, 0.15);
  color: #fb7185;
  border: 1px solid rgba(225, 29, 72, 0.3);
}

/* Inline CTA - 보라 그라데이션 */
.inline-cta {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  text-align: center;
  border: none;
  box-shadow: 0 4px 20px rgba(91, 33, 182, 0.15);
}

.inline-cta-question {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
  line-height: 1.5;
}

.inline-cta-subtext {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
  line-height: 1.5;
}

.inline-cta-btn {
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  background: #FFFFFF !important;
  color: var(--primary-color) !important;
}

/* Quick Question Chips */
.quick-question-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.quick-q-chip {
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Floating CTA */
.floating-cta {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px 20px;
  background: linear-gradient(transparent, rgba(13,10,26,0.95) 30%);
  z-index: 999;
}

.floating-cta-btn {
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  box-shadow: 0 4px 20px var(--shadow-purple) !important;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* Related Guides */
.related-guides {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.guide-link-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.guide-link-card {
  display: block;
  padding: 0.75rem;
  background: var(--button-hover-bg);
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--primary-color);
  text-decoration: none;
  text-align: center;
  transition: background 0.2s;
  border: 1px solid var(--button-hover-bg);
}

.guide-link-card:hover {
  background: var(--button-hover-bg);
}

/* Related Cards */
.related-section {
  padding: 1.5rem 0;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-top: 1rem;
}

.related-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  transition: transform 0.2s ease;
}

.related-card:hover {
  transform: translateY(-4px);
}

.related-card-img {
  width: 100%;
  aspect-ratio: 7/12;
  object-fit: contain;
  border-radius: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.related-card-name {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 0.4rem;
  text-align: center;
  line-height: 1.3;
}

/* Share Section */
.share-section {
  padding: 1.5rem 0;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.share-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 0.75rem 0;
}

.share-buttons {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
}

/* CTA Section */
.cta-section {
  margin-top: 1rem;
}

.cta-card {
  padding: 2.5rem 1.5rem;
  text-align: center;
  background: var(--card-bg);
  border-radius: 24px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.cta-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -30%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, var(--border-color) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.cta-icon {
  width: 56px;
  height: 56px;
  object-fit: contain;
  display: block;
  margin: 0 auto 0.75rem;
  animation: pulse 2s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.cta-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  position: relative;
  z-index: 1;
}

.cta-card p {
  font-size: 0.9rem;
  margin: 0 0 1.25rem 0;
  line-height: 1.6;
  color: var(--text-secondary);
  position: relative;
  z-index: 1;
}

.cta-button {
  font-size: 1rem;
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  background: var(--primary-color) !important;
  color: var(--text-primary) !important;
  box-shadow: 0 4px 20px var(--shadow-purple) !important;
  position: relative;
  z-index: 1;
}

/* Not Found */
.not-found {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.not-found-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.not-found h2 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

@media (max-width: 600px) {
  .card-image-wrapper {
    width: 150px;
    height: 257px;
  }

  .related-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
  }
}
</style>
