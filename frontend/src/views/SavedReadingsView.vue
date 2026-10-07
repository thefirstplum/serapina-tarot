<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              to="/"
              icon
              variant="flat"
              class="back-button"
            >
              <v-icon color="var(--primary-color)">mdi-home</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('savedReadings.title') }}</h1>
              <p class="page-subtitle">{{ t('savedReadings.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Filter Tabs -->
        <div class="filter-bar">
          <div class="filter-container">
            <button
              class="filter-chip"
              :class="{ active: activeFilter === 'all' }"
              @click="activeFilter = 'all'"
            >
              {{ t('savedReadings.filterAll') }}
            </button>
            <button
              class="filter-chip"
              :class="{ active: activeFilter === 'favorites' }"
              @click="activeFilter = 'favorites'"
            >
              {{ t('savedReadings.filterFavorites') }}
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <!-- Loading -->
            <div v-if="loading" class="loading-state">
              <v-progress-circular indeterminate color="var(--primary-color)" />
              <p>{{ t('common.loading') }}</p>
            </div>

            <!-- Reading Cards List -->
            <div v-else-if="filteredReadings.length > 0" class="readings-grid">
              <div
                v-for="reading in filteredReadings"
                :key="reading.id"
                class="reading-card"
                @click="openDetail(reading)"
              >
                <div class="reading-card-top">
                  <span class="reading-date">{{ formatDate(reading.timestamp) }}</span>
                  <button
                    class="favorite-btn"
                    @click.stop="toggleFavorite(reading)"
                  >
                    <v-icon :color="reading.is_favorite ? '#F59E0B' : '#CCC'" size="20">
                      {{ reading.is_favorite ? 'mdi-star' : 'mdi-star-outline' }}
                    </v-icon>
                  </button>
                </div>
                <p class="reading-question">{{ reading.question }}</p>
                <div class="reading-cards-chips" v-if="reading.cards && reading.cards.length > 0">
                  <span
                    v-for="(card, idx) in reading.cards.slice(0, 5)"
                    :key="idx"
                    class="card-chip"
                  >
                    {{ typeof card === 'string' ? card : card }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="empty-state">
              <img src="/icons/symbol-128.png" class="empty-icon" alt="" width="56" height="56" />
              <h3>{{ t('savedReadings.emptyTitle') }}</h3>
              <p>{{ t('savedReadings.emptyDesc') }}</p>
              <v-btn
                color="var(--primary-color)"
                size="large"
                variant="elevated"
                @click="$router.push('/reading')"
                class="cta-button"
              >
                {{ t('savedReadings.startReading') }}
              </v-btn>
            </div>
          </div>
        </div>

        <!-- Detail Modal -->
        <v-dialog v-model="showDetail" max-width="600" scrollable>
          <v-card v-if="detailReading" class="detail-card">
            <v-card-title class="detail-header">
              <span>{{ t('savedReadings.detailTitle') }}</span>
              <div class="detail-header-actions">
                <v-btn icon variant="text" size="small" @click="toggleFavorite(detailReading)">
                  <v-icon :color="detailReading.is_favorite ? '#F59E0B' : '#CCC'">
                    {{ detailReading.is_favorite ? 'mdi-star' : 'mdi-star-outline' }}
                  </v-icon>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="showDetail = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
            </v-card-title>
            <v-card-text class="detail-body">
              <!-- Loading detail -->
              <div v-if="detailLoading" class="detail-loading">
                <v-progress-circular indeterminate color="var(--primary-color)" size="32" />
              </div>
              <template v-else>
                <!-- Question -->
                <div class="detail-question">
                  <span class="quote-mark">"</span>
                  {{ detailReading.question }}
                  <span class="quote-mark">"</span>
                </div>

                <!-- Cards -->
                <div class="detail-cards" v-if="detailReading.cards && detailReading.cards.length > 0">
                  <div class="detail-cards-row">
                    <div
                      v-for="(card, idx) in detailReading.cards"
                      :key="idx"
                      class="detail-card-item"
                    >
                      <div class="detail-card-frame" :class="{ 'reversed-frame': isReversed(card) }">
                        <img
                          :src="getCardImageUrl(card)"
                          :alt="getCardDisplayName(card)"
                          class="detail-card-img"
                          :class="{ 'reversed-img': isReversed(card) }"
                        />
                      </div>
                      <span class="detail-card-name">
                        {{ getCardDisplayName(card) }}
                        <span v-if="isReversed(card)" class="reversed-tag">{{ t('readingView.reversedTag') }}</span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- AI Response -->
                <div class="detail-interpretation" v-if="detailReading.ai_response">
                  <h4 class="detail-section-title">
                    <span class="section-icon">✨</span>
                    {{ t('readingView.interpretationTitle') }}
                  </h4>
                  <div class="detail-response" v-html="formatResponse(detailReading.ai_response)"></div>
                </div>

                <!-- Date -->
                <div class="detail-date">
                  {{ formatDate(detailReading.timestamp) }}
                </div>
              </template>
            </v-card-text>
          </v-card>
        </v-dialog>

        <!-- Ad Banner -->
        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import AdSenseBlock from '@/components/AdSenseBlock.vue'
import { cardDatabase } from '@/data/cardDatabase'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

interface Reading {
  id: number
  question: string
  cards: any[]
  reading_type: string
  timestamp: string
  is_favorite: boolean
  is_saved: boolean
  ai_response?: string
}

const loading = ref(true)
const readings = ref<Reading[]>([])
const activeFilter = ref('all')
const showDetail = ref(false)
const detailReading = ref<Reading | null>(null)
const detailLoading = ref(false)

const filteredReadings = computed(() => {
  if (activeFilter.value === 'favorites') {
    return readings.value.filter(r => r.is_favorite)
  }
  return readings.value
})

const fetchReadings = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/user/readings', {
      params: { saved_only: true, limit: 50 }
    })
    readings.value = res.data.readings
  } catch {
    readings.value = []
  } finally {
    loading.value = false
  }
}

const openDetail = async (reading: Reading) => {
  detailReading.value = { ...reading }
  showDetail.value = true
  detailLoading.value = true

  try {
    const res = await axios.get(`/api/user/readings/${reading.id}`)
    detailReading.value = res.data
  } catch {
    // keep summary data
  } finally {
    detailLoading.value = false
  }
}

const toggleFavorite = async (reading: Reading) => {
  try {
    const res = await axios.post(`/api/user/readings/${reading.id}/favorite`)
    reading.is_favorite = res.data.is_favorite
    // Update in list too
    const found = readings.value.find(r => r.id === reading.id)
    if (found) found.is_favorite = res.data.is_favorite
  } catch {
    // ignore
  }
}

const isReversed = (card: any): boolean => {
  if (typeof card === 'string') return card.endsWith('_r')
  return false
}

const getCardBaseId = (card: any): string => {
  if (typeof card === 'string') return card.replace('_r', '')
  return ''
}

const cardImages = import.meta.glob('../assets/cards/*.jpg', { eager: true, import: 'default' }) as Record<string, string>

const getCardImageUrl = (card: any): string => {
  const baseId = getCardBaseId(card)
  if (!baseId) return ''
  const imagePath = `../assets/cards/${baseId}.jpg`
  return cardImages[imagePath] || ''
}

const getCardDisplayName = (card: any): string => {
  const baseId = getCardBaseId(card)
  if (!baseId) return String(card)
  const info = cardDatabase[baseId]
  return info?.name?.replace(/^\d+\.\s*/, '').split(' (')[0] || baseId
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

const formatResponse = (text: string) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.replace({ path: '/login', query: { redirect: '/saved-readings' } })
    return
  }
  await fetchReadings()
})
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Filter Bar */
.filter-bar {
  background: #FFFFFF;
  border-bottom: 1px solid #EAEAEA;
  padding: 0.75rem 1rem;
}

.filter-container {
  display: flex;
  gap: 0.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-chip {
  flex-shrink: 0;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #EAEAEA;
  background: #FFFFFF;
  color: #6B6B6B;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  border-color: #E9D5FF;
  color: var(--primary-color);
}

.filter-chip.active {
  background: var(--primary-color);
  color: var(--text-primary);
  border-color: var(--primary-color);
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: #6B6B6B;
}

/* Readings Grid */
.readings-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reading-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid #EAEAEA;
}

.reading-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: #E9D5FF;
}

.reading-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.reading-date {
  font-size: 0.8rem;
  color: #999;
}

.favorite-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.reading-question {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1A1A;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.reading-cards-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.card-chip {
  font-size: 0.75rem;
  color: var(--primary-color);
  background: #F5F3FF;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-weight: 500;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 1rem;
  gap: 0.75rem;
}

.empty-icon {
  width: 56px;
  height: 56px;
  object-fit: contain;
  display: block;
  margin: 0 auto 0.5rem;
}

.empty-state h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1A1A1A;
}

.empty-state p {
  color: #6B6B6B;
  font-size: 0.9rem;
}

.cta-button {
  margin-top: 1rem;
  border-radius: 12px;
  text-transform: none;
  font-weight: 600;
}

/* Detail Modal */
.detail-card {
  border-radius: 20px !important;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  font-size: 1.1rem;
  font-weight: 700;
  border-bottom: 1px solid #F0F0F0;
}

.detail-header-actions {
  display: flex;
  gap: 0.25rem;
}

.detail-body {
  padding: 1.25rem;
}

.detail-loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.detail-question {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1A1A1A;
  line-height: 1.6;
  margin-bottom: 1.25rem;
  padding: 1rem;
  background: #FAFAF8;
  border-radius: 12px;
}

.quote-mark {
  color: var(--primary-color);
  font-size: 1.3em;
  font-weight: 800;
}

/* Detail Cards */
.detail-cards {
  margin-bottom: 1.25rem;
}

.detail-cards-row {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding: 0.5rem 0;
  -webkit-overflow-scrolling: touch;
}

.detail-card-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}

.detail-card-frame {
  width: 70px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reversed-frame {
  border: 2px solid #E91E63;
}

.detail-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reversed-img {
  transform: rotate(180deg);
}

.detail-card-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #333;
  text-align: center;
  max-width: 80px;
}

.reversed-tag {
  display: inline-block;
  font-size: 0.65rem;
  color: #E91E63;
  font-weight: 600;
}

/* Interpretation */
.detail-interpretation {
  margin-bottom: 1rem;
}

.detail-section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 0.75rem;
}

.section-icon {
  font-size: 1.1rem;
}

.detail-response {
  font-size: 0.9rem;
  line-height: 1.8;
  color: #333;
}

.detail-date {
  font-size: 0.8rem;
  color: #999;
  text-align: right;
  margin-top: 1rem;
}
</style>
