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
              <h1 class="page-title">{{ t('cards.majorArcana.title') }}</h1>
              <p class="page-subtitle">{{ t('cards.majorArcana.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <!-- Description -->
            <div class="intro-section">
              <p class="intro-text">
                {{ t('cards.majorArcana.introText') }}
              </p>
            </div>

            <!-- Cards Grid -->
            <div class="cards-grid">
              <div
                v-for="card in majorArcanaCards"
                :key="card.id"
                class="tarot-card"
                @click="$router.push({ name: 'card-detail', params: { id: card.id } })"
              >
                <div class="card-image-wrap">
                  <img
                    v-if="cardImages[card.id]"
                    :src="cardImages[card.id]"
                    :alt="card.name"
                    class="card-image"
                  />
                  <div v-else class="card-image-placeholder">
                    <span class="card-number-badge">{{ card.number }}</span>
                  </div>
                </div>
                <div class="card-info">
                  <div class="card-number-label">{{ card.number }}</div>
                  <h3 class="card-name">{{ card.name }}</h3>
                  <p class="card-keywords">{{ card.keywords }}</p>
                </div>
              </div>
            </div>

            <!-- CTA -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ t('cards.majorArcana.ctaTitle') }}</h3>
                <p>{{ t('cards.majorArcana.ctaDescription') }}</p>
                <v-btn
                  size="large"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'major_arcana')"
                >
                  {{ t('cards.majorArcana.ctaButton') }}
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
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useI18n } from 'vue-i18n'
import { trackCtaClick } from '@/utils/analytics'

const { t } = useI18n()
import AdBanner from '@/components/AdBanner.vue'

const imageModules = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>
const cardImages: Record<string, string> = {}
for (const [path, url] of Object.entries(imageModules)) {
  const filename = path.split('/').pop()?.replace('.jpg', '') || ''
  cardImages[filename] = url
}

useSeoMeta(
  t('cards.majorArcana.title') + ' | ' + t('app.name'),
  t('cards.majorArcana.introText'),
  t('cards.majorArcana.title') + ', ' + t('app.name')
)

const majorArcanaCards = [
  { id: 'maj00', number: 0, name: '바보', keywords: '새로운 시작, 순수함, 모험' },
  { id: 'maj01', number: 1, name: '마법사', keywords: '의지, 창조력, 현실화' },
  { id: 'maj02', number: 2, name: '여사제', keywords: '직관, 내적 지혜, 신비' },
  { id: 'maj03', number: 3, name: '여황제', keywords: '창조, 양육, 풍요' },
  { id: 'maj04', number: 4, name: '황제', keywords: '권위, 안정, 리더십' },
  { id: 'maj05', number: 5, name: '교황', keywords: '전통, 가르침, 영적 지혜' },
  { id: 'maj06', number: 6, name: '연인', keywords: '사랑, 선택, 조화' },
  { id: 'maj07', number: 7, name: '전차', keywords: '승리, 의지력, 성취' },
  { id: 'maj08', number: 8, name: '힘', keywords: '내적 힘, 용기, 인내' },
  { id: 'maj09', number: 9, name: '은둔자', keywords: '성찰, 내적 탐구, 고독' },
  { id: 'maj10', number: 10, name: '운명의 바퀴', keywords: '변화, 순환, 운명' },
  { id: 'maj11', number: 11, name: '정의', keywords: '공정, 균형, 진실' },
  { id: 'maj12', number: 12, name: '매달린 사람', keywords: '희생, 깨달음, 새로운 관점' },
  { id: 'maj13', number: 13, name: '죽음', keywords: '변화, 재생, 끝과 시작' },
  { id: 'maj14', number: 14, name: '절제', keywords: '균형, 조화, 절제' },
  { id: 'maj15', number: 15, name: '악마', keywords: '유혹, 속박, 물질적 집착' },
  { id: 'maj16', number: 16, name: '탑', keywords: '갑작스런 변화, 깨달음, 파괴' },
  { id: 'maj17', number: 17, name: '별', keywords: '희망, 영감, 치유' },
  { id: 'maj18', number: 18, name: '달', keywords: '환상, 불안, 무의식' },
  { id: 'maj19', number: 19, name: '태양', keywords: '성공, 기쁨, 활력' },
  { id: 'maj20', number: 20, name: '심판', keywords: '재생, 구원, 각성' },
  { id: 'maj21', number: 21, name: '세계', keywords: '완성, 성취, 통합' }
]
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Intro */
.intro-section {
  padding: 0 0.5rem 1.5rem 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.intro-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0;
}

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

.card-number-badge {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  opacity: 0.5;
}

.card-info {
  padding: 0.75rem;
}

.card-number-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.2rem;
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
