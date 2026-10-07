<template>
  <v-dialog v-model="dialogModel" max-width="400px" persistent class="rewarded-dialog">
    <v-card class="rewarded-card">
      <div class="rewarded-header">
        <h2>{{ t('rewardedAd.title') }}</h2>
        <p>{{ t('rewardedAd.subtitle') }}</p>
      </div>

      <v-card-text class="rewarded-body">
        <!-- 보상형 광고 -->
        <div
          v-if="!adWatchedToday"
          class="option-card highlight"
          @click="watchRewardedAd"
        >
          <div class="option-icon">🎬</div>
          <div class="option-info">
            <div class="option-title">{{ t('rewardedAd.watchAdTitle') }}</div>
            <div class="option-desc">{{ t('rewardedAd.watchAdDesc') }}</div>
          </div>
          <v-icon color="amber">mdi-chevron-right</v-icon>
        </div>
        <div v-else class="option-card disabled">
          <div class="option-icon">🎬</div>
          <div class="option-info">
            <div class="option-title">{{ t('rewardedAd.alreadyWatched') }}</div>
            <div class="option-desc">{{ t('rewardedAd.comeTomorrow') }}</div>
          </div>
          <v-icon color="grey">mdi-check</v-icon>
        </div>

        <!-- 포인트 사용 - 숨김 처리 -->
        <!-- <div class="option-card" @click="usePoints">
          <div class="option-icon">💎</div>
          <div class="option-info">
            <div class="option-title">{{ t('rewardedAd.pointsTitle') }}</div>
            <div class="option-desc">{{ t('rewardedAd.pointsBalance', { balance: authStore.pointBalance }) }}</div>
          </div>
          <v-icon>mdi-chevron-right</v-icon>
        </div> -->

        <!-- 구독 - 숨김 처리 -->
        <!-- <div class="option-card premium" @click="goSubscription">
          <div class="option-icon">👑</div>
          <div class="option-info">
            <div class="option-title">{{ t('rewardedAd.subscriptionTitle') }}</div>
            <div class="option-desc">{{ t('rewardedAd.subscriptionDesc') }}</div>
          </div>
          <v-icon color="amber">mdi-chevron-right</v-icon>
        </div> -->

        <!-- 내일 다시 -->
        <div class="option-card" @click="closeDialog">
          <div class="option-icon">🌙</div>
          <div class="option-info">
            <div class="option-title">{{ t('rewardedAd.tomorrowTitle') }}</div>
            <div class="option-desc">{{ t('rewardedAd.freeReadingsInfo') }}</div>
          </div>
          <v-icon>mdi-chevron-right</v-icon>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { trackRewardedAdWatched, trackSubscriptionViewed } from '@/utils/analytics'

const { t } = useI18n()

interface Props {
  modelValue: boolean
  sessionId: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'rewarded': []
  'use-points': []
}>()

const router = useRouter()
const authStore = useAuthStore()
// 일일 cap은 부모(TarotReadingView)에서 관리, 여기선 제한 안 함
const adWatchedToday = ref(false)

const dialogModel = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

onMounted(() => {
  adWatchedToday.value = false
})

async function watchRewardedAd() {
  const confirmed = confirm(t('rewardedAd.confirmMessage'))
  if (!confirmed) return

  // 백엔드 기록 시도. 실패해도 보상은 진행 (광고는 아직 가짜 단계)
  try {
    await axios.post('/api/rewarded-ad/complete', {
      session_id: props.sessionId,
    })
  } catch (err: any) {
    if (err?.response?.status === 429) {
      // 진짜 이미 본 케이스만 차단
      adWatchedToday.value = true
      alert(t('rewardedAd.alreadyWatchedAlert'))
      closeDialog()
      return
    }
    // 그 외 오류(DB·인증·네트워크)는 사용자에게 안 보여주고 보상 진행
    console.warn('Rewarded ad backend tracking failed (보상은 진행):', err?.message)
  }

  trackRewardedAdWatched()
  emit('rewarded')
  closeDialog()
}

function usePoints() {
  emit('use-points')
  closeDialog()
}

function goSubscription() {
  trackSubscriptionViewed('rewarded_dialog')
  closeDialog()
  if (authStore.isLoggedIn) {
    router.push('/subscription')
  } else {
    router.push({ path: '/login', query: { redirect: '/subscription' } })
  }
}

function closeDialog() {
  dialogModel.value = false
}
</script>

<style scoped>
/* LandingView와 같은 톤 (Memphis 보더 + 그림자) */
.rewarded-card {
  border-radius: 20px !important;
  background: var(--card-bg) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 6px 6px 0 var(--primary-color) !important;
  overflow: hidden;
}

.rewarded-header {
  background: var(--secondary-color);
  border-bottom: 2px solid var(--text-primary);
  padding: 24px;
  text-align: center;
}

.rewarded-header h2 {
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 800;
  margin: 0 0 6px;
  letter-spacing: -0.015em;
}

.rewarded-header p {
  color: var(--text-primary);
  font-size: 0.88rem;
  margin: 0;
  opacity: 0.85;
  font-weight: 500;
}

.rewarded-body {
  padding: 18px !important;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--card-bg);
}

.option-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--bg-secondary);
  border: 1.5px solid var(--text-primary);
  cursor: pointer;
  transition: all 0.15s;
}

.option-card:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 3px 3px 0 var(--text-primary);
}

.option-card.highlight {
  border: 2px solid var(--text-primary);
  background: var(--accent-yellow);
  box-shadow: 3px 3px 0 var(--text-primary);
}
.option-card.highlight:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 5px 5px 0 var(--text-primary);
}

.option-card.premium {
  border: 2px solid var(--text-primary);
  background: var(--secondary-color);
}

.option-card.disabled {
  opacity: 0.5;
  cursor: default;
  pointer-events: none;
}

.option-icon {
  font-size: 1.7rem;
  flex-shrink: 0;
}

.option-info {
  flex: 1;
}

.option-title {
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 700;
}

.option-desc {
  color: var(--text-secondary);
  font-size: 0.78rem;
  margin-top: 3px;
  font-weight: 500;
}
</style>
