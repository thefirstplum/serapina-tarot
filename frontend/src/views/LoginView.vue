<template>
  <div class="login-main">
      <div class="login-container">
        <div class="login-card">
          <div class="login-header">
            <img src="/icons/symbol-128.png" class="login-icon" alt="세라피나" width="72" height="72" />
            <h1 class="login-title">세라피나 타로</h1>
            <p class="login-subtitle">로그인하면 리딩 기록도 저장하고,<br>포인트로 프리미엄 서비스도 이용할 수 있어!</p>
          </div>

          <!-- 이메일/패스워드 폼 -->
          <div class="email-form">
            <input
              v-model="email"
              type="email"
              class="email-input"
              placeholder="이메일"
              @keyup.enter="passwordInput?.focus()"
            />
            <input
              ref="passwordInput"
              v-model="password"
              type="password"
              class="email-input"
              :placeholder="isRegisterMode ? '비밀번호 (6자 이상)' : '비밀번호'"
              @keyup.enter="isRegisterMode ? register() : login()"
            />
            <input
              v-if="isRegisterMode"
              v-model="nickname"
              type="text"
              class="email-input"
              placeholder="닉네임 (선택)"
              @keyup.enter="register()"
            />

            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

            <button
              class="email-login-btn"
              @click="isRegisterMode ? register() : login()"
              :disabled="isLoading"
            >
              {{ isLoading ? '처리 중...' : (isRegisterMode ? '회원가입' : '로그인') }}
            </button>

            <button class="toggle-mode-btn" @click="toggleMode">
              {{ isRegisterMode ? '이미 계정이 있어요? 로그인' : '계정이 없어요? 회원가입' }}
            </button>
          </div>

          <div class="divider">
            <span class="divider-line"></span>
            <span class="divider-text">또는</span>
            <span class="divider-line"></span>
          </div>

          <div class="login-actions">
            <button class="kakao-login-btn" @click="loginWithKakao" :disabled="isLoading">
              <svg class="kakao-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#3C1E1E" d="M12 3C6.48 3 2 6.36 2 10.44c0 2.61 1.74 4.9 4.36 6.2l-1.1 4.07c-.1.36.3.64.61.44l4.84-3.2c.42.04.85.06 1.29.06 5.52 0 10-3.36 10-7.57C22 6.36 17.52 3 12 3z"/>
              </svg>
              <span>카카오로 시작하기</span>
            </button>

            <button class="guest-btn" @click="continueAsGuest">
              로그인 없이 계속하기
            </button>
          </div>

          <p class="login-note">
            로그인 없이도 바로 무료 상담이 가능해요!
          </p>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoading = ref(false)
const isRegisterMode = ref(false)
const email = ref('')
const password = ref('')
const nickname = ref('')
const errorMessage = ref('')
const passwordInput = ref<HTMLInputElement | null>(null)

function toggleMode() {
  isRegisterMode.value = !isRegisterMode.value
  errorMessage.value = ''
}

function getRedirectPath() {
  return (route.query.redirect as string) || '/reading'
}

async function login() {
  errorMessage.value = ''
  if (!email.value || !password.value) {
    errorMessage.value = '이메일과 비밀번호를 입력해주세요'
    return
  }
  isLoading.value = true
  const result = await authStore.emailLogin(email.value, password.value)
  isLoading.value = false

  if (result.success) {
    router.push(getRedirectPath())
  } else {
    errorMessage.value = result.error || '로그인에 실패했어요'
  }
}

async function register() {
  errorMessage.value = ''
  if (!email.value || !password.value) {
    errorMessage.value = '이메일과 비밀번호를 입력해주세요'
    return
  }
  if (password.value.length < 6) {
    errorMessage.value = '비밀번호는 6자 이상이어야 해요'
    return
  }
  isLoading.value = true
  const result = await authStore.emailRegister(email.value, password.value, nickname.value)
  isLoading.value = false

  if (result.success) {
    router.push(getRedirectPath())
  } else {
    errorMessage.value = result.error || '회원가입에 실패했어요'
  }
}

async function loginWithKakao() {
  isLoading.value = true
  try {
    const url = await authStore.getKakaoLoginUrl()
    if (url) {
      window.location.href = url
    }
  } finally {
    isLoading.value = false
  }
}

function continueAsGuest() {
  router.push(getRedirectPath())
}
</script>

<style scoped>
.login-main {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 50%, #0f3460 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 40px 28px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.login-icon {
  width: 72px;
  height: 72px;
  object-fit: contain;
  display: block;
  margin: 0 auto 16px;
}

.login-title {
  color: var(--text-primary);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 28px;
}

/* Email Form */
.email-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.email-input {
  width: 100%;
  padding: 13px 16px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.email-input::placeholder {
  color: var(--text-secondary);
}

.email-input:focus {
  border-color: var(--primary-color);
}

.error-message {
  color: #F87171;
  font-size: 13px;
  text-align: left;
  margin: 0;
}

.email-login-btn {
  width: 100%;
  padding: 14px;
  background: var(--primary-color);
  color: var(--text-primary);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.email-login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--shadow-purple);
}

.email-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-mode-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  padding: 4px;
}

.toggle-mode-btn:hover {
  color: var(--text-primary);
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.divider-text {
  color: var(--text-secondary);
  font-size: 13px;
}

/* Login Actions */
.login-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.kakao-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: #FEE500;
  color: #3C1E1E;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.kakao-login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(254, 229, 0, 0.3);
}

.kakao-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.guest-btn {
  width: 100%;
  padding: 14px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.guest-btn:hover {
  background: var(--card-bg);
}

.login-note {
  color: var(--text-secondary);
  font-size: 12px;
}
</style>
