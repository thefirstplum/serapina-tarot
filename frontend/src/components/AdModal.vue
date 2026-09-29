<template>
  <v-dialog
    v-model="dialogModel"
    max-width="520px"
    persistent
    class="ad-dialog"
  >
    <v-card class="ad-card">
      <div class="ad-header">
        <div class="header-content">
          <h2 class="header-title">{{ t('ad.specialOfferTitle') }}</h2>
          <p class="header-subtitle">{{ t('ad.specialOfferSubtitle') }}</p>
        </div>
        <v-btn
          icon
          variant="text"
          @click="closeAd"
          class="close-button"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-card-text class="ad-content">
        <div class="ad-body">
          <div class="ad-image">
            🎁
          </div>

          <h3 class="ad-title">{{ t('ad.premiumTitle') }}</h3>

          <p class="ad-description" v-html="t('ad.premiumDescription')"></p>

          <div class="benefits-list">
            <div class="benefit-item">
              <v-icon color="primary">mdi-check-circle</v-icon>
              <span>{{ t('ad.benefits.unlimited') }}</span>
            </div>
            <div class="benefit-item">
              <v-icon color="primary">mdi-check-circle</v-icon>
              <span>{{ t('ad.benefits.unlimitedHistory') }}</span>
            </div>
            <div class="benefit-item">
              <v-icon color="primary">mdi-check-circle</v-icon>
              <span>{{ t('ad.benefits.noAds') }}</span>
            </div>
            <div class="benefit-item">
              <v-icon color="primary">mdi-check-circle</v-icon>
              <span>{{ t('ad.benefits.premiumSpreads') }}</span>
            </div>
          </div>

          <div class="price-section">
            <div class="price-tag">
              <span class="original-price">{{ t('ad.originalPrice') }}</span>
              <span class="discount-price">{{ t('ad.discountedPrice') }}</span>
            </div>
            <p class="discount-label">{{ t('ad.discountLabel') }}</p>
          </div>
        </div>
      </v-card-text>

      <v-card-actions class="ad-actions">
        <v-btn
          variant="text"
          @click="closeAd"
          class="later-btn"
        >
          {{ t('ad.laterButton') }}
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          @click="goToPremium"
          class="premium-btn"
        >
          {{ t('ad.signUpButton') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'

const { t } = useI18n()

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'ad-clicked': []
}>()

const router = useRouter()
const authStore = useAuthStore()

const dialogModel = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const closeAd = () => {
  dialogModel.value = false

  try {
    localStorage.setItem('tarot_last_ad_closed', Date.now().toString())
  } catch (error) {
    // 저장 실패 무시
  }
}

const goToPremium = () => {
  emit('ad-clicked')

  try {
    localStorage.setItem('tarot_ad_clicked', Date.now().toString())
  } catch (error) {
    // 저장 실패 무시
  }

  closeAd()

  if (authStore.isLoggedIn) {
    router.push('/subscription')
  } else {
    router.push({ path: '/login', query: { redirect: '/subscription' } })
  }
}
</script>

<style scoped>
.ad-card {
  border-radius: 20px !important;
  background: var(--card-bg) !important;
  overflow: hidden;
}

.ad-header {
  background: var(--gradient-primary);
  color: rgb(var(--v-theme-on-primary));
  padding: 24px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
}

.header-content {
  flex: 1;
}

.header-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: rgb(var(--v-theme-on-primary));
}

.header-subtitle {
  font-size: 0.95rem;
  margin: 0;
  opacity: 0.95;
  color: rgb(var(--v-theme-on-primary));
}

.close-button {
  color: rgb(var(--v-theme-on-primary)) !important;
  opacity: 0.9;
}

.close-button:hover {
  opacity: 1;
  background: var(--border-color) !important;
}

.ad-content {
  padding: 32px 24px;
}

.ad-body {
  text-align: center;
}

.ad-image {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce-in 0.6s ease-out;
}

.ad-title {
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.ad-description {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 24px;
}

.benefits-list {
  text-align: left;
  max-width: 320px;
  margin: 0 auto 24px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  color: var(--text-primary);
  font-weight: 500;
}

.benefit-item:last-child {
  margin-bottom: 0;
}

.price-section {
  margin-top: 24px;
  padding: 20px;
  background: var(--gradient-primary);
  border-radius: 12px;
}

.price-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.original-price {
  color: var(--text-primary);
  font-size: 1rem;
  text-decoration: line-through;
}

.discount-price {
  color: var(--text-primary);
  font-size: 1.8rem;
  font-weight: 700;
}

.discount-label {
  color: var(--text-primary);
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
}

.ad-actions {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.later-btn {
  font-weight: 500;
  color: var(--text-secondary) !important;
}

.premium-btn {
  font-weight: 600;
  padding: 0 28px;
  height: 44px;
}

@keyframes bounce-in {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Mobile optimizations */
@media (max-width: 600px) {
  .ad-header {
    padding: 20px;
  }

  .header-title {
    font-size: 1.25rem;
  }

  .header-subtitle {
    font-size: 0.9rem;
  }

  .ad-content {
    padding: 24px 20px;
  }

  .ad-title {
    font-size: 1.3rem;
  }

  .ad-description {
    font-size: 0.95rem;
  }

  .benefits-list {
    padding: 16px;
  }

  .discount-price {
    font-size: 1.5rem;
  }

  .ad-actions {
    padding: 16px 20px 20px;
    flex-direction: column;
    gap: 10px;
  }

  .later-btn,
  .premium-btn {
    width: 100%;
  }

  .premium-btn {
    order: 1;
  }

  .later-btn {
    order: 2;
  }
}
</style>
