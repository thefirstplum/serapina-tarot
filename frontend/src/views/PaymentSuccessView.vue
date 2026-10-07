<template>
  <div class="success-main">
      <div class="success-container">
        <div v-if="isLoading" class="loading-state">
          <v-progress-circular indeterminate color="amber" size="48" />
          <p>결제를 확인하고 있어요...</p>
        </div>
        <div v-else-if="isSuccess" class="success-state">
          <v-icon size="64" color="success">mdi-check-circle</v-icon>
          <h2>충전 완료!</h2>
          <p class="points-granted">
            <v-icon size="small" color="amber">mdi-star-circle</v-icon>
            {{ pointsGranted }}P 충전 완료
          </p>
          <p class="new-balance">현재 잔액: {{ newBalance }}P</p>
          <div class="actions">
            <v-btn color="purple" variant="flat" rounded="lg" @click="$router.push('/chat')">
              타로 보러 가기
            </v-btn>
            <v-btn variant="outlined" color="white" rounded="lg" @click="$router.push('/mypage')">
              마이페이지
            </v-btn>
          </div>
        </div>
        <div v-else class="error-state">
          <v-icon size="64" color="error">mdi-alert-circle</v-icon>
          <h2>결제 확인 실패</h2>
          <p>{{ errorMessage }}</p>
          <v-btn color="purple" variant="flat" rounded="lg" @click="$router.push('/points')">
            다시 시도하기
          </v-btn>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()

const isLoading = ref(true)
const isSuccess = ref(false)
const pointsGranted = ref(0)
const newBalance = ref(0)
const errorMessage = ref('')

onMounted(async () => {
  const paymentKey = route.query.paymentKey as string
  const orderId = route.query.orderId as string
  const amount = Number(route.query.amount)

  if (!paymentKey || !orderId || !amount) {
    errorMessage.value = '결제 정보가 올바르지 않아요'
    isLoading.value = false
    return
  }

  try {
    const res = await axios.post('/api/payments/confirm', {
      payment_key: paymentKey,
      order_id: orderId,
      amount: amount,
    })

    isSuccess.value = true
    pointsGranted.value = res.data.points_granted
    newBalance.value = res.data.balance

    authStore.updatePointBalance(res.data.balance)
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.detail || '결제 확인에 실패했어요'
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.success-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-container {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-primary);
}

.loading-state,
.success-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.success-state h2 {
  color: var(--text-primary);
  font-size: 24px;
}

.points-granted {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-yellow);
}

.new-balance {
  color: var(--text-secondary);
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.error-state h2 {
  color: #ef9a9a;
}

.error-state p {
  color: var(--text-secondary);
}
</style>
