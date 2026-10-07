<template>
  <div class="charge-main">
      <div class="charge-container">
        <!-- 헤더 -->
        <div class="charge-header">
          <v-btn icon variant="text" @click="$router.back()">
            <v-icon color="white">mdi-arrow-left</v-icon>
          </v-btn>
          <h1 class="charge-title">포인트 충전</h1>
          <div class="current-balance">
            <v-icon size="small" color="amber">mdi-star-circle</v-icon>
            <span>{{ authStore.pointBalance }}P</span>
          </div>
        </div>

        <!-- 상품 목록 -->
        <div class="products-grid">
          <div
            v-for="product in pointStore.products"
            :key="product.code"
            class="product-card"
            :class="{ popular: product.is_popular, selected: selectedProduct === product.code }"
            @click="selectedProduct = product.code"
          >
            <div v-if="product.is_popular" class="popular-badge">인기</div>
            <div class="product-points">
              <v-icon size="small" color="amber">mdi-star-circle</v-icon>
              {{ product.points }}P
              <span v-if="product.bonus_points" class="bonus">+{{ product.bonus_points }}</span>
            </div>
            <div class="product-price">{{ product.price.toLocaleString() }}원</div>
            <div v-if="product.description" class="product-desc">{{ product.description }}</div>
          </div>
        </div>

        <!-- 기능별 비용 안내 -->
        <div class="costs-section">
          <h3 class="section-title">포인트 사용처</h3>
          <div class="cost-list">
            <div class="cost-item">
              <span>추가 리딩 (광고 없이 바로)</span>
              <span class="cost-value">20P</span>
            </div>
            <div class="cost-item">
              <span>프리미엄 리딩 (상세 해석)</span>
              <span class="cost-value">30P</span>
            </div>
            <div class="cost-item">
              <span>추가 질문 (대화 제한 초과)</span>
              <span class="cost-value">10P</span>
            </div>
            <div class="cost-item">
              <span>특별 스프레드</span>
              <span class="cost-value">50P</span>
            </div>
          </div>
        </div>

        <!-- 결제 버튼 -->
        <div class="charge-actions">
          <v-btn
            color="amber"
            variant="flat"
            size="large"
            rounded="lg"
            block
            :disabled="!selectedProduct || isLoading"
            :loading="isLoading"
            @click="startPayment"
          >
            {{ selectedProductInfo ? `${selectedProductInfo.price.toLocaleString()}원 결제하기` : '상품을 선택해주세요' }}
          </v-btn>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePointStore } from '@/stores/pointStore'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const pointStore = usePointStore()

const selectedProduct = ref('')
const isLoading = ref(false)

const selectedProductInfo = computed(() =>
  pointStore.products.find((p) => p.code === selectedProduct.value),
)

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.replace('/login')
    return
  }
  await pointStore.fetchProducts()
  // 인기 상품 자동 선택
  const popular = pointStore.products.find((p) => p.is_popular)
  if (popular) selectedProduct.value = popular.code
})

async function startPayment() {
  if (!selectedProduct.value) return
  isLoading.value = true

  try {
    // 1. 서버에서 주문 생성
    const res = await axios.post('/api/payments/order', {
      product_code: selectedProduct.value,
    })
    const { order_id, amount, product_name } = res.data

    // 2. 토스 결제 SDK 호출
    const clientKey = import.meta.env.VITE_TOSS_CLIENT_KEY
    if (!clientKey) {
      alert('결제 시스템 설정이 필요해요')
      isLoading.value = false
      return
    }

    // @ts-ignore - 토스 SDK는 CDN으로 로드
    const tossPayments = await loadTossPayments(clientKey)
    const payment = tossPayments.payment({ customerKey: `USER_${authStore.user?.id}` })

    await payment.requestPayment({
      method: 'CARD',
      amount: {
        currency: 'KRW',
        value: amount,
      },
      orderId: order_id,
      orderName: product_name,
      successUrl: `${window.location.origin}/payments/success`,
      failUrl: `${window.location.origin}/payments/fail`,
    })
  } catch (err: any) {
    if (err?.code === 'USER_CANCEL') {
      // 유저가 취소
    } else {
      console.error('결제 오류:', err)
      alert('결제 중 오류가 발생했어요')
    }
  } finally {
    isLoading.value = false
  }
}

// 토스 SDK 동적 로드
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
.charge-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
}

.charge-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 16px;
}

.charge-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0 20px;
}

.charge-title {
  flex: 1;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
}

.current-balance {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-yellow);
  font-weight: 700;
  font-size: 16px;
}

.products-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.product-card {
  position: relative;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.product-card:hover {
  background: var(--card-bg);
}

.product-card.selected {
  border-color: var(--accent-yellow);
  background: rgba(255, 193, 7, 0.1);
}

.product-card.popular {
  border-color: rgba(255, 193, 7, 0.5);
}

.popular-badge {
  position: absolute;
  top: -8px;
  right: 12px;
  background: var(--accent-yellow);
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
}

.product-points {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 22px;
  font-weight: 700;
  color: var(--accent-yellow);
  margin-bottom: 4px;
}

.bonus {
  font-size: 14px;
  color: #4caf50;
  font-weight: 600;
}

.product-price {
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 4px;
}

.product-desc {
  color: var(--text-secondary);
  font-size: 11px;
}

.costs-section {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.section-title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.cost-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary);
}

.cost-value {
  color: var(--accent-yellow);
  font-weight: 600;
}

.charge-actions {
  position: sticky;
  bottom: 16px;
  padding: 8px 0;
}
</style>
