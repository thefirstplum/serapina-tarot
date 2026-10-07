<template>
  <div class="mypage-main">
      <div class="mypage-container">
        <!-- 헤더 -->
        <div class="mypage-header">
          <v-btn icon variant="text" @click="$router.back()">
            <v-icon color="white">mdi-arrow-left</v-icon>
          </v-btn>
          <h1 class="mypage-title">마이페이지</h1>
          <v-btn icon variant="text" @click="logout">
            <v-icon color="white" size="small">mdi-logout</v-icon>
          </v-btn>
        </div>

        <!-- 프로필 섹션 -->
        <div class="profile-section">
          <v-avatar size="64">
            <v-img v-if="authStore.user?.profile_image" :src="authStore.user.profile_image" />
            <v-icon v-else size="64" color="purple-lighten-2">mdi-account-circle</v-icon>
          </v-avatar>
          <h2 class="profile-name">{{ authStore.user?.nickname || '세라피나 유저' }}</h2>
          <p class="profile-email">{{ authStore.user?.email }}</p>
        </div>

        <!-- 포인트 카드 -->
        <div class="point-card" @click="$router.push('/points')">
          <div class="point-info">
            <span class="point-label">보유 포인트</span>
            <span class="point-value">
              <v-icon size="small" color="amber">mdi-star-circle</v-icon>
              {{ authStore.pointBalance }}P
            </span>
          </div>
          <v-btn size="small" color="amber" variant="flat" rounded="lg">
            충전하기
          </v-btn>
        </div>

        <!-- 포인트 사용 내역 -->
        <div class="section">
          <h3 class="section-title">포인트 내역</h3>
          <div v-if="pointHistory.length === 0" class="empty-state">
            아직 포인트 내역이 없어요
          </div>
          <div v-else class="history-list">
            <div v-for="item in pointHistory" :key="item.id" class="history-item">
              <div class="history-info">
                <span class="history-type" :class="item.usage_type === 'charge' ? 'charge' : 'usage'">
                  {{ getUsageLabel(item.usage_type) }}
                </span>
                <span class="history-desc">{{ item.description }}</span>
              </div>
              <div class="history-amount" :class="item.usage_type === 'charge' ? 'positive' : 'negative'">
                {{ item.usage_type === 'charge' ? '+' : '-' }}{{ item.amount }}P
              </div>
            </div>
          </div>
        </div>

        <!-- 리딩 히스토리 -->
        <div class="section">
          <h3 class="section-title">리딩 기록</h3>
          <div v-if="readings.length === 0" class="empty-state">
            아직 리딩 기록이 없어요
          </div>
          <div v-else class="reading-list">
            <div v-for="reading in readings" :key="reading.id" class="reading-item">
              <div class="reading-info">
                <span class="reading-question">{{ reading.question }}</span>
                <span class="reading-date">{{ formatDate(reading.timestamp) }}</span>
              </div>
              <v-btn
                icon
                variant="text"
                size="small"
                @click="toggleFavorite(reading.id)"
              >
                <v-icon :color="reading.is_favorite ? 'amber' : 'grey'">
                  {{ reading.is_favorite ? 'mdi-star' : 'mdi-star-outline' }}
                </v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { usePointStore } from '@/stores/pointStore'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const pointStore = usePointStore()

const pointHistory = ref<any[]>([])
const readings = ref<any[]>([])

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.replace('/login')
    return
  }

  // 병렬로 데이터 로드
  await Promise.allSettled([
    loadPointHistory(),
    loadReadings(),
  ])
})

async function loadPointHistory() {
  await pointStore.fetchHistory()
  pointHistory.value = pointStore.history
}

async function loadReadings() {
  try {
    const res = await axios.get('/api/user/readings', { params: { limit: 20 } })
    readings.value = res.data.readings
  } catch {
    // 리딩 로드 실패
  }
}

function getUsageLabel(type: string): string {
  const labels: Record<string, string> = {
    charge: '충전',
    extra_reading: '추가 리딩',
    premium_reading: '프리미엄',
    extra_question: '추가 질문',
    special_spread: '특별 스프레드',
  }
  return labels[type] || type
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function toggleFavorite(readingId: number) {
  try {
    await axios.post(`/api/user/readings/${readingId}/favorite`)
    const reading = readings.value.find((r) => r.id === readingId)
    if (reading) reading.is_favorite = !reading.is_favorite
  } catch {
    // 즐겨찾기 실패
  }
}

function logout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.mypage-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
}

.mypage-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 16px;
  padding-bottom: 40px;
}

.mypage-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0 20px;
}

.mypage-title {
  flex: 1;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
}

.profile-section {
  text-align: center;
  margin-bottom: 24px;
}

.profile-name {
  color: var(--text-primary);
  font-size: 20px;
  margin-top: 12px;
}

.profile-email {
  color: var(--text-secondary);
  font-size: 13px;
}

.point-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  cursor: pointer;
}

.point-label {
  display: block;
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 4px;
}

.point-value {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-yellow);
  font-size: 24px;
  font-weight: 700;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  padding: 24px;
}

.history-list,
.reading-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item,
.reading-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 12px 16px;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-type {
  font-size: 12px;
  font-weight: 600;
}

.history-type.charge { color: #4caf50; }
.history-type.usage { color: var(--accent-yellow); }

.history-desc {
  color: var(--text-secondary);
  font-size: 12px;
}

.history-amount {
  font-weight: 700;
  font-size: 14px;
}

.history-amount.positive { color: #4caf50; }
.history-amount.negative { color: var(--accent-yellow); }

.reading-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.reading-question {
  color: var(--text-primary);
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reading-date {
  color: var(--text-secondary);
  font-size: 12px;
}
</style>
