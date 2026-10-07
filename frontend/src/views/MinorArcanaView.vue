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
              <h1 class="page-title">{{ t('cards.minorArcana.title') }}</h1>
              <p class="page-subtitle">{{ t('cards.minorArcana.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <!-- Description -->
            <div class="info-card">
              <p class="section-text">
                {{ t('cards.minorArcana.introText') }}
              </p>
            </div>

            <!-- Suit Cards Grid -->
            <div class="suits-grid">
              <div class="suit-card" @click="goToSuit('cups')">
                <div class="suit-icon">💖</div>
                <h3 class="suit-name">{{ t('cards.suits.cups.name') }}</h3>
                <p class="suit-element">{{ t('cards.suits.cups.element') }}</p>
                <p class="suit-description">{{ t('cards.minorArcana.cupsDesc') }}</p>
              </div>

              <div class="suit-card" @click="goToSuit('pentacles')">
                <div class="suit-icon">💰</div>
                <h3 class="suit-name">{{ t('cards.suits.pentacles.name') }}</h3>
                <p class="suit-element">{{ t('cards.suits.pentacles.element') }}</p>
                <p class="suit-description">{{ t('cards.minorArcana.pentaclesDesc') }}</p>
              </div>

              <div class="suit-card" @click="goToSuit('swords')">
                <div class="suit-icon">⚡</div>
                <h3 class="suit-name">{{ t('cards.suits.swords.name') }}</h3>
                <p class="suit-element">{{ t('cards.suits.swords.element') }}</p>
                <p class="suit-description">{{ t('cards.minorArcana.swordsDesc') }}</p>
              </div>

              <div class="suit-card" @click="goToSuit('wands')">
                <div class="suit-icon">✨</div>
                <h3 class="suit-name">{{ t('cards.suits.wands.name') }}</h3>
                <p class="suit-element">{{ t('cards.suits.wands.element') }}</p>
                <p class="suit-description">{{ t('cards.minorArcana.wandsDesc') }}</p>
              </div>
            </div>

            <!-- Card Structure -->
            <div class="structure-section">
              <h2 class="structure-heading">{{ t('cards.minorArcana.structureTitle') }}</h2>
              <div class="structure-content">
                <div class="structure-item">
                  <h3 class="structure-title">{{ t('cards.minorArcana.numberCardsTitle') }}</h3>
                  <p class="structure-text">{{ t('cards.minorArcana.numberCardsDesc') }}</p>
                  <ul class="structure-list">
                    <li><strong>{{ t('cards.minorArcana.numberCardsAce') }}</strong> {{ t('cards.minorArcana.numberCardsAceDesc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.numberCards24') }}</strong> {{ t('cards.minorArcana.numberCards24Desc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.numberCards57') }}</strong> {{ t('cards.minorArcana.numberCards57Desc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.numberCards810') }}</strong> {{ t('cards.minorArcana.numberCards810Desc') }}</li>
                  </ul>
                </div>

                <div class="structure-item">
                  <h3 class="structure-title">{{ t('cards.minorArcana.courtCardsTitle') }}</h3>
                  <p class="structure-text">{{ t('cards.minorArcana.courtCardsDesc') }}</p>
                  <ul class="structure-list">
                    <li><strong>{{ t('cards.minorArcana.courtCardsPage') }}</strong> {{ t('cards.minorArcana.courtCardsPageDesc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.courtCardsKnight') }}</strong> {{ t('cards.minorArcana.courtCardsKnightDesc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.courtCardsQueen') }}</strong> {{ t('cards.minorArcana.courtCardsQueenDesc') }}</li>
                    <li><strong>{{ t('cards.minorArcana.courtCardsKing') }}</strong> {{ t('cards.minorArcana.courtCardsKingDesc') }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- CTA -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ t('cards.minorArcana.ctaTitle') }}</h3>
                <p>{{ t('cards.minorArcana.ctaDescription') }}</p>
                <v-btn
                  size="large"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'minor_arcana')"
                >
                  {{ t('cards.minorArcana.ctaButton') }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { trackCtaClick } from '@/utils/analytics'

const { t } = useI18n()
import { useSeoMeta } from '@/composables/useSeoMeta'
import AdBanner from '@/components/AdBanner.vue'

const router = useRouter()

const goToSuit = (suit: string) => {
  router.push({ name: 'cards-suit', params: { suit } })
}

useSeoMeta(
  t('cards.minorArcana.title') + ' | ' + t('app.name'),
  t('cards.minorArcana.introText'),
  t('cards.minorArcana.title') + ', ' + t('app.name')
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Suits Grid */
.suits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.suit-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
}

.suit-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px var(--shadow-purple);
  border-color: var(--border-color);
}

.suit-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}

.suit-name {
  font-size: 1.3rem;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 0.4rem 0;
}

.suit-element {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-weight: 600;
  margin: 0 0 0.75rem 0;
}

.suit-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Structure Section */
.structure-section {
  margin-bottom: 2rem;
}

.structure-heading {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin: 0 0 1.5rem 0;
}

.structure-content {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.structure-item {
  padding: 1.5rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.structure-item:last-child {
  border-bottom: none;
}

.structure-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.structure-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0 0 0.75rem 0;
  line-height: 1.6;
}

.structure-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.structure-list li {
  font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 0.4rem 0 0.4rem 1.2rem;
  position: relative;
}

.structure-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-weight: bold;
}

.structure-list li strong {
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .suits-grid {
    grid-template-columns: 1fr;
  }
}
</style>
