<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              icon
              variant="flat"
              to="/"
              class="back-button"
            >
              <v-icon color="var(--primary-color)" size="28">mdi-home</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('cards.main.title') }}</h1>
              <p class="page-subtitle">{{ t('cards.main.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <!-- Main Categories -->
            <div class="category-grid">
              <div class="category-card" @click="$router.push({ name: 'major-arcana' })">
                <div class="category-icon">🌙</div>
                <div class="category-info">
                  <h2 class="category-title">{{ t('cards.main.majorTitle') }}</h2>
                  <p class="category-subtitle">{{ t('cards.main.majorSubtitle') }}</p>
                  <p class="category-desc">{{ t('cards.main.majorDescription') }}</p>
                </div>
                <div class="category-footer">
                  <span class="category-count">{{ t('cards.main.majorCardCount') }}</span>
                  <v-icon color="var(--primary-color)" size="20">mdi-arrow-right</v-icon>
                </div>
              </div>

              <div class="category-card" @click="$router.push({ name: 'minor-arcana' })">
                <div class="category-icon">⭐</div>
                <div class="category-info">
                  <h2 class="category-title">{{ t('cards.main.minorTitle') }}</h2>
                  <p class="category-subtitle">{{ t('cards.main.minorSubtitle') }}</p>
                  <p class="category-desc">{{ t('cards.main.minorDescription') }}</p>
                </div>
                <div class="category-footer">
                  <span class="category-count">{{ t('cards.main.minorCardCount') }}</span>
                  <v-icon color="var(--primary-color)" size="20">mdi-arrow-right</v-icon>
                </div>
              </div>
            </div>

            <!-- Suits Section -->
            <h2 class="suits-section-title">{{ t('cards.main.suitsSectionTitle') }}</h2>
            <div class="suit-grid">
              <div class="suit-card" @click="$router.push({ name: 'cards-suit', params: { suit: 'cups' } })">
                <div class="suit-icon">💖</div>
                <h3 class="suit-name">{{ t('cards.suits.cups.name') }}</h3>
                <p class="suit-theme">{{ t('cards.suits.cups.theme') }}</p>
                <p class="suit-desc">{{ t('cards.suits.cups.description') }}</p>
              </div>

              <div class="suit-card" @click="$router.push({ name: 'cards-suit', params: { suit: 'pentacles' } })">
                <div class="suit-icon">💰</div>
                <h3 class="suit-name">{{ t('cards.suits.pentacles.name') }}</h3>
                <p class="suit-theme">{{ t('cards.suits.pentacles.theme') }}</p>
                <p class="suit-desc">{{ t('cards.suits.pentacles.description') }}</p>
              </div>

              <div class="suit-card" @click="$router.push({ name: 'cards-suit', params: { suit: 'swords' } })">
                <div class="suit-icon">⚡</div>
                <h3 class="suit-name">{{ t('cards.suits.swords.name') }}</h3>
                <p class="suit-theme">{{ t('cards.suits.swords.theme') }}</p>
                <p class="suit-desc">{{ t('cards.suits.swords.description') }}</p>
              </div>

              <div class="suit-card" @click="$router.push({ name: 'cards-suit', params: { suit: 'wands' } })">
                <div class="suit-icon">✨</div>
                <h3 class="suit-name">{{ t('cards.suits.wands.name') }}</h3>
                <p class="suit-theme">{{ t('cards.suits.wands.theme') }}</p>
                <p class="suit-desc">{{ t('cards.suits.wands.description') }}</p>
              </div>
            </div>

            <!-- Call to Action -->
            <div class="cta-section">
              <div class="cta-card">
                <div class="cta-icon">💬</div>
                <h3>{{ t('cards.main.ctaTitle') }}</h3>
                <p>{{ t('cards.main.ctaDescription') }}</p>
                <v-btn
                  size="x-large"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'cards_main')"
                >
                  <v-icon start>mdi-cards-heart</v-icon>
                  {{ t('cards.main.ctaButton') }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- AdBanner Component -->
        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useI18n } from 'vue-i18n'
import { trackCtaClick } from '@/utils/analytics'

const { t } = useI18n()
import AdBanner from '@/components/AdBanner.vue'

useSeoMeta(
  t('seo.cards.title'),
  t('seo.cards.description'),
  t('seo.cards.keywords')
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Category Grid */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.category-card {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 1.75rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--shadow-purple);
  border-color: var(--border-color);
}

.category-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.category-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.category-subtitle {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-weight: 600;
  margin: 0 0 0.75rem 0;
}

.category-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.category-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.category-count {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--primary-color);
}

/* Suits Section */
.suits-section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin: 0 0 1.5rem 0;
}

.suit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.suit-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 1.2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
}

.suit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px var(--shadow-purple);
  border-color: var(--border-color);
}

.suit-icon {
  font-size: 2rem;
  margin-bottom: 0.4rem;
}

.suit-name {
  font-size: 1rem;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0.4rem 0;
}

.suit-theme {
  font-size: 0.8rem;
  color: var(--primary-color);
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.suit-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: 1fr;
  }

  .suit-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
