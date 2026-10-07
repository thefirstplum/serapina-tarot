<template>
  <div class="fail-main">
      <div class="fail-container">
        <v-icon size="64" color="error">mdi-close-circle</v-icon>
        <h2>결제 실패</h2>
        <p class="fail-message">{{ message }}</p>
        <p v-if="errorCode" class="fail-code">오류 코드: {{ errorCode }}</p>
        <div class="actions">
          <v-btn color="purple" variant="flat" rounded="lg" @click="$router.push('/points')">
            다시 시도하기
          </v-btn>
          <v-btn variant="outlined" color="white" rounded="lg" @click="$router.push('/chat')">
            돌아가기
          </v-btn>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const message = computed(() => (route.query.message as string) || '결제가 완료되지 않았어요')
const errorCode = computed(() => route.query.code as string)
</script>

<style scoped>
.fail-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fail-container {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.fail-container h2 {
  color: #ef9a9a;
  font-size: 24px;
}

.fail-message {
  color: var(--text-primary);
  font-size: 14px;
}

.fail-code {
  color: var(--text-secondary);
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
</style>
