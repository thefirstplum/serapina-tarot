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
              <v-icon color="white" size="28">mdi-home</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('guides.main.title') }}</h1>
              <p class="page-subtitle">{{ t('guides.main.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <!-- Main Guide Cards -->
            <div class="guide-grid">
              <div class="guide-card love" @click="trackCtaClick('guide_love', 'guides_main'); $router.push({ name: 'guide-love' })">
                <div class="guide-icon">💕</div>
                <h2 class="guide-title">{{ t('guides.love.cardTitle') }}</h2>
                <p class="guide-subtitle">{{ t('guides.love.cardSubtitle') }}</p>
                <p class="guide-description">
                  {{ t('guides.love.description') }}
                </p>
                <ul class="guide-list">
                  <li v-for="(topic, index) in loveTopics" :key="index">{{ topic }}</li>
                </ul>
                <div class="guide-footer">
                  <span>{{ t('guides.main.viewMore') }}</span>
                  <v-icon>mdi-arrow-right</v-icon>
                </div>
              </div>

              <div class="guide-card career" @click="trackCtaClick('guide_career', 'guides_main'); $router.push({ name: 'guide-career' })">
                <div class="guide-icon">💼</div>
                <h2 class="guide-title">{{ t('guides.career.cardTitle') }}</h2>
                <p class="guide-subtitle">{{ t('guides.career.cardSubtitle') }}</p>
                <p class="guide-description">
                  {{ t('guides.career.description') }}
                </p>
                <ul class="guide-list">
                  <li v-for="(topic, index) in careerTopics" :key="index">{{ topic }}</li>
                </ul>
                <div class="guide-footer">
                  <span>{{ t('guides.main.viewMore') }}</span>
                  <v-icon>mdi-arrow-right</v-icon>
                </div>
              </div>

              <div class="guide-card study" @click="trackCtaClick('guide_study', 'guides_main'); $router.push({ name: 'guide-study' })">
                <div class="guide-icon">📚</div>
                <h2 class="guide-title">{{ t('guides.study.cardTitle') }}</h2>
                <p class="guide-subtitle">{{ t('guides.study.cardSubtitle') }}</p>
                <p class="guide-description">
                  {{ t('guides.study.description') }}
                </p>
                <ul class="guide-list">
                  <li v-for="(topic, index) in studyTopics" :key="index">{{ topic }}</li>
                </ul>
                <div class="guide-footer">
                  <span>{{ t('guides.main.viewMore') }}</span>
                  <v-icon>mdi-arrow-right</v-icon>
                </div>
              </div>

              <div class="guide-card money" @click="trackCtaClick('guide_money', 'guides_main'); $router.push({ name: 'guide-money' })">
                <div class="guide-icon">💰</div>
                <h2 class="guide-title">{{ t('guides.money.cardTitle') }}</h2>
                <p class="guide-subtitle">{{ t('guides.money.cardSubtitle') }}</p>
                <p class="guide-description">
                  {{ t('guides.money.description') }}
                </p>
                <ul class="guide-list">
                  <li v-for="(topic, index) in moneyTopics" :key="index">{{ topic }}</li>
                </ul>
                <div class="guide-footer">
                  <span>{{ t('guides.main.viewMore') }}</span>
                  <v-icon>mdi-arrow-right</v-icon>
                </div>
              </div>
            </div>

            <!-- Basic Guide Section -->
            <div class="section-title">{{ t('guides.basicTips.sectionTitle') }}</div>
            <div class="basic-grid">
              <div class="basic-info-box">
                <div class="basic-icon">{{ t('guides.basicTips.question.icon') }}</div>
                <h3>{{ t('guides.basicTips.question.title') }}</h3>
                <p class="basic-description">
                  {{ t('guides.basicTips.question.description') }}
                </p>
                <ul class="basic-list">
                  <li><strong>{{ t('guides.basicTips.question.badExample') }}</strong> {{ t('guides.basicTips.question.badExampleText') }}</li>
                  <li><strong>{{ t('guides.basicTips.question.goodExample') }}</strong> {{ t('guides.basicTips.question.goodExampleText') }}</li>
                  <li><strong>{{ t('guides.basicTips.question.tip') }}</strong> {{ t('guides.basicTips.question.tipText') }}</li>
                </ul>
              </div>

              <div class="basic-info-box">
                <div class="basic-icon">{{ t('guides.basicTips.interpretation.icon') }}</div>
                <h3>{{ t('guides.basicTips.interpretation.title') }}</h3>
                <p class="basic-description">
                  {{ t('guides.basicTips.interpretation.description') }}
                </p>
                <ul class="basic-list">
                  <li><strong>{{ t('guides.basicTips.interpretation.upright') }}</strong> {{ t('guides.basicTips.interpretation.uprightText') }}</li>
                  <li><strong>{{ t('guides.basicTips.interpretation.reversed') }}</strong> {{ t('guides.basicTips.interpretation.reversedText') }}</li>
                  <li><strong>{{ t('guides.basicTips.interpretation.tip') }}</strong> {{ t('guides.basicTips.interpretation.tipText') }}</li>
                </ul>
              </div>

              <div class="basic-info-box">
                <div class="basic-icon">{{ t('guides.basicTips.timing.icon') }}</div>
                <h3>{{ t('guides.basicTips.timing.title') }}</h3>
                <p class="basic-description">
                  {{ t('guides.basicTips.timing.description') }}
                </p>
                <ul class="basic-list">
                  <li><strong>{{ t('guides.basicTips.timing.good') }}</strong> {{ t('guides.basicTips.timing.goodText') }}</li>
                  <li><strong>{{ t('guides.basicTips.timing.bad') }}</strong> {{ t('guides.basicTips.timing.badText') }}</li>
                  <li><strong>{{ t('guides.basicTips.timing.tip') }}</strong> {{ t('guides.basicTips.timing.tipText') }}</li>
                </ul>
              </div>

              <div class="basic-info-box">
                <div class="basic-icon">{{ t('guides.basicTips.usage.icon') }}</div>
                <h3>{{ t('guides.basicTips.usage.title') }}</h3>
                <p class="basic-description">
                  {{ t('guides.basicTips.usage.description') }}
                </p>
                <ul class="basic-list">
                  <li><strong>{{ t('guides.basicTips.usage.daily') }}</strong> {{ t('guides.basicTips.usage.dailyText') }}</li>
                  <li><strong>{{ t('guides.basicTips.usage.weekly') }}</strong> {{ t('guides.basicTips.usage.weeklyText') }}</li>
                  <li><strong>{{ t('guides.basicTips.usage.choice') }}</strong> {{ t('guides.basicTips.usage.choiceText') }}</li>
                </ul>
              </div>
            </div>

            <!-- CTA Section -->
            <div class="cta-section">
              <div class="cta-card">
                <div class="cta-icon">{{ t('guides.cta.icon') }}</div>
                <h3>{{ t('guides.cta.title') }}</h3>
                <p>
                  {{ t('guides.cta.description') }}
                </p>
                <v-btn
                  size="large"
                  color="white"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'guides_main')"
                >
                  {{ t('guides.cta.button') }}
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
import { computed } from 'vue'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { trackCtaClick } from '@/utils/analytics'
import AdBanner from '@/components/AdBanner.vue'
import { useI18n } from 'vue-i18n'

const { t, tm } = useI18n()

// Use tm() for accessing arrays in i18n
const loveTopics = computed(() => tm('guides.topics.love') as string[])
const careerTopics = computed(() => tm('guides.topics.career') as string[])
const studyTopics = computed(() => tm('guides.topics.study') as string[])
const moneyTopics = computed(() => tm('guides.topics.money') as string[])

useSeoMeta(
  t('seo.guides.title'),
  t('seo.guides.description'),
  t('seo.guides.keywords')
)
</script>

<style scoped>
@import '@/assets/common-pages.css';

.app-main {
  height: auto;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  min-height: 100vh;
  padding: 0;
  position: relative;
  overflow-x: hidden;
}

.app-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, var(--shadow-purple) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, var(--button-hover-bg) 0%, transparent 50%);
  pointer-events: none;
}

.page-layout {
  display: flex;
  flex-direction: column;
  min-height: auto;

}

.page-header {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.back-button {
  background: var(--border-color) !important;
  border: 1px solid var(--border-color) !important;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary) !important;
  background: none !important;
  -webkit-background-clip: unset !important;
  -webkit-text-fill-color: var(--text-primary) !important;
  background-clip: unset !important;
  text-shadow: none;
}

.page-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary) !important;
  margin: 0.25rem 0 0 0;
  text-shadow: none;
}

.page-content {
  flex: 1;
  
  padding: 2rem 1rem 6rem;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.guide-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  color: var(--text-primary);
}

.guide-card:hover {
  transform: translateY(-4px);
  background: var(--card-bg);
  border-color: var(--border-color);
  box-shadow: 0 8px 24px var(--shadow-purple);
}

.guide-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.guide-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin: 0 0 0.3rem 0;
  color: var(--text-primary);
}

.guide-subtitle {
  font-size: 0.9rem;
  color: var(--primary-color);
  margin: 0 0 0.75rem 0;
}

.guide-description {
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0 0 0.75rem 0;
}

.guide-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem 0;
}

.guide-list li {
  font-size: 0.85rem;
  padding: 0.4rem 0;
  color: var(--text-secondary);
  position: relative;
  padding-left: 1.2rem;
}

.guide-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  font-weight: bold;
}

.guide-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  margin-top: 1rem;
  color: var(--primary-color);
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 1rem;
  text-align: center;
}

.basic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.basic-info-box {
  padding: 0 1rem 1.5rem 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.basic-info-box:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.basic-icon {
  font-size: 2rem;
  margin-bottom: 0.6rem;
  display: inline-block;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.basic-info-box h3 {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0 0 0.6rem 0;
}

.basic-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 0.8rem 0;
}

.basic-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.basic-list li {
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 0.4rem 0;
  position: relative;
  padding-left: 1.2rem;
  line-height: 1.5;
}

.basic-list li::before {
  content: "✨";
  position: absolute;
  left: 0;
  font-size: 1rem;
}

.cta-section {
  margin-top: 2rem;
}

.cta-card {
  padding: 2rem 1.5rem;
  text-align: center;
  color: var(--text-primary);
  background: var(--card-bg);
  border-radius: 24px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.cta-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.cta-card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
}

.cta-card p {
  font-size: 0.95rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
  color: var(--text-secondary);
}

.cta-button {
  font-size: 1rem;
  font-weight: 700;
  padding: 1rem 2rem !important;
  height: auto !important;
  background: var(--primary-color) !important;
  color: var(--text-primary) !important;
  border-radius: 16px !important;
  border: none !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px var(--shadow-purple) !important;
}

.cta-button:hover {
  background: var(--primary-color) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 28px var(--shadow-purple) !important;
}

@media (max-width: 768px) {
  .guide-grid {
    grid-template-columns: 1fr;
  }

  .basic-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-title {
    font-size: 1.2rem;
  }

  .cta-card h3 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .basic-grid {
    grid-template-columns: 1fr;
  }
}
</style>
