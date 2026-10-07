<template>
  <div class="sub-main">
      <div class="sub-container">
        <!-- 헤더 -->
        <div class="sub-header">
          <v-btn icon variant="text" @click="$router.back()">
            <v-icon color="white">mdi-arrow-left</v-icon>
          </v-btn>
          <h1 class="sub-title">{{ t('subscription.title') }}</h1>
          <div style="width:40px"></div>
        </div>

        <!-- 현재 상태 -->
        <div v-if="authStore.isPremium" class="current-plan-badge">
          <v-icon color="amber" size="small">mdi-crown</v-icon>
          {{ t('subscription.currentBadge') }}
        </div>

        <!-- 혜택 안내 -->
        <div class="benefits-card">
          <h2 class="benefits-title">{{ t('subscription.benefitsTitle') }}</h2>
          <div class="benefit-row" v-for="b in benefits" :key="b.icon">
            <v-icon color="amber" size="small">{{ b.icon }}</v-icon>
            <span>{{ b.text }}</span>
          </div>
        </div>

        <!-- 플랜 선택 -->
        <div class="plans-grid">
          <div
            v-for="plan in plans"
            :key="plan.code"
            class="plan-card"
            :class="{ selected: selectedPlan === plan.code, recommended: plan.code === 'yearly' }"
            @click="selectedPlan = plan.code"
          >
            <div v-if="plan.code === 'yearly'" class="save-badge">{{ t('subscription.discountBadge') }}</div>
            <div class="plan-name">{{ plan.name }}</div>
            <div class="plan-price">
              <span v-if="plan.original_price" class="original-price">{{ plan.original_price.toLocaleString() }}원</span>
              <span class="current-price">{{ plan.price.toLocaleString() }}원</span>
            </div>
            <div class="plan-per">
              {{ plan.code === 'yearly' ? `월 ${Math.round(plan.price / 12).toLocaleString()}원` : t('subscription.monthlyPayment') }}
            </div>
          </div>
        </div>

        <!-- 결제 버튼 -->
        <div class="sub-actions">
          <v-btn
            color="amber"
            variant="flat"
            size="large"
            rounded="lg"
            block
            :disabled="!selectedPlan || isLoading"
            :loading="isLoading"
            @click="startPayment"
          >
            {{ selectedPlanInfo ? t('subscription.payButton', { price: selectedPlanInfo.price.toLocaleString() }) : t('subscription.selectPlan') }}
          </v-btn>
        </div>

        <!-- 안내 -->
        <div class="sub-notice">
          <p>{{ t('subscription.notice1') }}</p>
          <p>{{ t('subscription.notice2') }}</p>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { trackSubscriptionViewed, trackSubscriptionStarted } from '@/utils/analytics'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const plans = ref<any[]>([])
const selectedPlan = ref('')
const isLoading = ref(false)

const benefits = computed(() => [
  { icon: 'mdi-infinity', text: t('subscription.benefits.unlimited') },
  { icon: 'mdi-content-save-all', text: t('subscription.benefits.unlimitedHistory') },
  { icon: 'mdi-eye-off', text: t('subscription.benefits.noAds') },
  { icon: 'mdi-cards-playing-outline', text: t('subscription.benefits.premiumSpreads') },
])

const selectedPlanInfo = computed(() =>
  plans.value.find((p) => p.code === selectedPlan.value)
)

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.replace({ path: '/login', query: { redirect: '/subscription' } })
    return
  }
  trackSubscriptionViewed('subscription_page')
  try {
    const res = await axios.get('/subscription/plans')
    plans.value = res.data
    // 연간 플랜 자동 선택
    const yearly = plans.value.find((p) => p.code === 'yearly')
    if (yearly) selectedPlan.value = yearly.code
    else if (plans.value.length) selectedPlan.value = plans.value[0].code
  } catch {
    // 플랜 로드 실패
  }
})

async function startPayment() {
  if (!selectedPlan.value) return
  isLoading.value = true

  try {
    const res = await axios.post('/subscription/order', {
      plan_code: selectedPlan.value,
    })
    const { order_id, amount, product_name } = res.data
    trackSubscriptionStarted(selectedPlan.value, amount)

    const clientKey = import.meta.env.VITE_TOSS_CLIENT_KEY
    if (!clientKey) {
      alert(t('subscription.errors.systemSetup'))
      isLoading.value = false
      return
    }

    // @ts-ignore
    const tossPayments = await loadTossPayments(clientKey)
    const payment = tossPayments.payment({ customerKey: `USER_${authStore.user?.id}` })

    await payment.requestPayment({
      method: 'CARD',
      amount: { currency: 'KRW', value: amount },
      orderId: order_id,
      orderName: product_name,
      successUrl: `${window.location.origin}/payments/success?type=subscription`,
      failUrl: `${window.location.origin}/payments/fail`,
    })
  } catch (err: any) {
    if (err?.code !== 'USER_CANCEL') {
      console.error('결제 오류:', err)
      alert(t('subscription.errors.paymentFailed'))
    }
  } finally {
    isLoading.value = false
  }
}

function loadTossPayments(clientKey: string): Promise<any> {
  return new Promise((resolve, reject) => {
    if ((window as any).TossPayments) {
      resolve(new (window as any).TossPayments(clientKey))
      return
    }
    const script = document.createElement('script')
    script.src = 'https://js.tosspayments.com/v2/standard'
    script.onload = () => resolve(new (window as any).TossPayments(clientKey))
    script.onerror = reject
    document.head.appendChild(script)
  })
}
</script>

<style scoped>
.sub-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
}

.sub-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 16px;
}

.sub-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0 20px;
}

.sub-title {
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
  text-align: center;
}

.current-plan-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(255, 193, 7, 0.15);
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 16px;
  color: var(--accent-yellow);
  font-weight: 600;
  font-size: 14px;
}

.benefits-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}

.benefits-title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
}

.benefit-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 10px;
}

.benefit-row:last-child {
  margin-bottom: 0;
}

.plans-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.plan-card {
  position: relative;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.plan-card:hover {
  background: var(--card-bg);
}

.plan-card.selected {
  border-color: var(--accent-yellow);
  background: rgba(255, 193, 7, 0.1);
}

.plan-card.recommended {
  border-color: rgba(255, 193, 7, 0.5);
}

.save-badge {
  position: absolute;
  top: -8px;
  right: 12px;
  background: #ff5722;
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
}

.plan-name {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}

.plan-price {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-bottom: 4px;
}

.original-price {
  color: var(--text-secondary);
  font-size: 13px;
  text-decoration: line-through;
}

.current-price {
  color: var(--accent-yellow);
  font-size: 22px;
  font-weight: 700;
}

.plan-per {
  color: var(--text-secondary);
  font-size: 12px;
}

.sub-actions {
  position: sticky;
  bottom: 16px;
  padding: 8px 0;
}

.sub-notice {
  margin-top: 16px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: 12px;
}

.sub-notice p {
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.sub-notice p:last-child {
  margin-bottom: 0;
}
</style>
