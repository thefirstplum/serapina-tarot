<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              icon
              variant="flat"
              :to="{ name: 'cards' }"
              class="back-button"
            >
              <v-icon color="var(--primary-color)" size="28">mdi-arrow-left</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ suitInfo?.name || t('cards.detail.noCard') }}</h1>
              <p class="page-subtitle">{{ suitInfo?.description || '' }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container" v-if="suitCards.length > 0">
            <!-- Cards Grid -->
            <div class="cards-grid">
              <div
                v-for="card in suitCards"
                :key="card.id"
                class="tarot-card"
                @click="goToCard(card.id)"
              >
                <div class="card-image-wrap">
                  <img
                    v-if="cardImages[card.id]"
                    :src="cardImages[card.id]"
                    :alt="card.name"
                    class="card-image"
                  />
                  <div v-else class="card-image-placeholder">
                    <span class="card-placeholder-icon">🃏</span>
                  </div>
                </div>
                <div class="card-info">
                  <h3 class="card-name">{{ card.name }}</h3>
                  <p class="card-keywords">
                    {{ card.uprightKeywords.slice(0, 3).join(', ') }}
                  </p>
                </div>
              </div>
            </div>

            <!-- CTA -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ suitInfo?.name }}{{ t('cards.suitDetail.ctaTitle') }}</h3>
                <p>{{ suitInfo?.name }}{{ t('cards.suitDetail.ctaDescription') }}</p>
                <v-btn
                  size="large"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'cards_suit')"
                >
                  {{ t('cards.suit.startReadingButton') }}
                </v-btn>
              </div>
            </div>
          </div>

          <!-- Not Found -->
          <div class="content-container" v-else>
            <div class="not-found">
              <div class="not-found-icon">🔍</div>
              <h2>{{ t('cards.suitDetail.notFound.title') }}</h2>
              <v-btn
                size="large"
                color="var(--primary-color)"
                variant="elevated"
                :to="{ name: 'cards' }"
                class="mt-6"
                style="color: var(--text-primary);"
              >
                {{ t('cards.suit.backButton') }}
              </v-btn>
            </div>
          </div>
        </div>

        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { trackCtaClick } from '@/utils/analytics'

const { t } = useI18n()
import { useRoute, useRouter } from 'vue-router'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { cardDatabase } from '@/data/cardDatabase'
import AdBanner from '@/components/AdBanner.vue'

const route = useRoute()
const router = useRouter()
const suit = computed(() => route.params.suit as string)

const imageModules = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>
const cardImages: Record<string, string> = {}
for (const [path, url] of Object.entries(imageModules)) {
  const filename = path.split('/').pop()?.replace('.jpg', '') || ''
  cardImages[filename] = url
}

const suitInfo = computed(() => {
  const suitMap: Record<string, { name: string; description: string; element: string }> = {
    cups: {
      name: '컵 (Cups)',
      description: '감정, 관계, 사랑, 직관을 상징하는 물의 원소',
      element: '물'
    },
    pentacles: {
      name: '펜타클 (Pentacles)',
      description: '물질, 재정, 현실, 건강을 상징하는 흙의 원소',
      element: '흙'
    },
    swords: {
      name: '검 (Swords)',
      description: '지성, 논리, 갈등, 진실을 상징하는 공기의 원소',
      element: '공기'
    },
    wands: {
      name: '지팡이 (Wands)',
      description: '열정, 창조, 행동, 영감을 상징하는 불의 원소',
      element: '불'
    }
  }
  return suitMap[suit.value]
})

const suitCards = computed(() => {
  if (!suitInfo.value) return []

  return Object.values(cardDatabase).filter((card) => {
    return card.suit === suitInfo.value.name
  })
})

const goToCard = (id: string) => {
  router.push({ name: 'card-detail', params: { id } })
}

useSeoMeta(
  suitInfo.value
    ? t('seo.cardsSuit.titleTemplate', { suitName: suitInfo.value.name })
    : t('seo.cardsSuit.fallbackTitle'),
  suitInfo.value
    ? t('seo.cardsSuit.descriptionTemplate', {
        suitName: suitInfo.value.name,
        description: suitInfo.value.description
      })
    : t('seo.cardsSuit.fallbackDescription'),
  suitInfo.value
    ? t('seo.cardsSuit.keywordsTemplate', {
        suitName: suitInfo.value.name,
        element: suitInfo.value.element
      })
    : t('seo.cardsSuit.fallbackKeywords')
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.tarot-card {
  background: var(--card-bg);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
}

.tarot-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--shadow-purple);
  border-color: var(--border-color);
}

.card-image-wrap {
  aspect-ratio: 7/12;
  overflow: hidden;
  background: var(--button-hover-bg);
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--button-hover-bg) 0%, var(--button-hover-bg) 100%);
}

.card-placeholder-icon {
  font-size: 2.5rem;
  opacity: 0.4;
}

.card-info {
  padding: 0.75rem;
}

.card-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.3rem 0;
}

.card-keywords {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

/* Not Found */
.not-found {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.not-found-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.not-found h2 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
