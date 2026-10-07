<template>
  <div class="callback-main">
      <div class="callback-container">
        <div v-if="isLoading" class="callback-loading">
          <v-progress-circular indeterminate color="purple-lighten-2" size="48" />
          <p class="callback-text">로그인 중이에요...</p>
        </div>
        <div v-else-if="error" class="callback-error">
          <v-icon size="48" color="error">mdi-alert-circle</v-icon>
          <p class="callback-text">{{ error }}</p>
          <v-btn color="purple" variant="flat" @click="$router.push('/login')">
            다시 시도하기
          </v-btn>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useChatStore } from '@/stores/chatStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const chatStore = useChatStore()

const isLoading = ref(true)
const error = ref('')

onMounted(async () => {
  const code = route.query.code as string
  if (!code) {
    error.value = '인증 코드가 없어요'
    isLoading.value = false
    return
  }

  const success = await authStore.handleKakaoCallback(code)
  if (success) {
    // 기존 세션 연결
    if (chatStore.sessionId) {
      await authStore.linkSession(chatStore.sessionId)
    }
    router.replace('/chat')
  } else {
    error.value = '로그인에 실패했어요. 다시 시도해주세요.'
    isLoading.value = false
  }
})
</script>

<style scoped>
.callback-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.callback-container {
  text-align: center;
  padding: 40px;
}

.callback-loading,
.callback-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.callback-text {
  color: var(--text-primary);
  font-size: 16px;
}
</style>
