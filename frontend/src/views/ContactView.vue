<template>
  <div class="app-main">
    <div class="page-layout">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <v-btn icon variant="flat" to="/" class="back-button">
            <v-icon size="28">mdi-arrow-left</v-icon>
          </v-btn>
          <div class="header-text">
            <h1 class="page-title">문의하기</h1>
            <p class="page-subtitle">운영자에게 바로 전달돼요. 답장은 24시간 안에 드려요</p>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="page-content">
        <div class="content-container">
          <!-- 문의 폼 -->
          <div class="info-card">
            <h2 class="section-title">문의 보내기</h2>
            <p class="section-text">
              버그 신고·제안·협업·기타 무엇이든 환영이에요. 입력하신 이메일로 답장드릴게요.
            </p>

            <form @submit.prevent="submitContact" class="contact-form">
              <div class="form-row">
                <label for="contact-name">이름 또는 닉네임</label>
                <input
                  id="contact-name"
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="OO"
                  class="form-input"
                  :disabled="submitting"
                />
              </div>

              <div class="form-row">
                <label for="contact-email">이메일 (답장받을 주소)</label>
                <input
                  id="contact-email"
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="hello@example.com"
                  class="form-input"
                  :disabled="submitting"
                />
              </div>

              <div class="form-row">
                <label for="contact-category">분류</label>
                <select id="contact-category" v-model="form.category" class="form-input" :disabled="submitting">
                  <option value="bug">버그 신고</option>
                  <option value="feature">기능 제안</option>
                  <option value="content">콘텐츠·해석 관련</option>
                  <option value="business">제휴·협업</option>
                  <option value="other">기타</option>
                </select>
              </div>

              <div class="form-row">
                <label for="contact-message">내용</label>
                <textarea
                  id="contact-message"
                  v-model="form.message"
                  required
                  placeholder="자유롭게 적어줘"
                  rows="6"
                  class="form-input form-textarea"
                  :disabled="submitting"
                ></textarea>
              </div>

              <button type="submit" class="contact-submit-btn" :disabled="submitting || !canSubmit">
                {{ submitting ? '보내는 중...' : '문의 보내기' }}
              </button>

              <p v-if="successMsg" class="form-success">{{ successMsg }}</p>
              <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>
            </form>
          </div>

          <!-- FAQ 짧게 -->
          <div class="info-card">
            <h2 class="section-title">자주 묻는 질문</h2>
            <h3 class="subsection-title">Q. 회원가입 안 해도 되나요?</h3>
            <p class="section-text">네, 회원가입 없이 바로 타로 카드 뽑을 수 있어요.</p>

            <h3 class="subsection-title">Q. 매일 몇 번 무료인가요?</h3>
            <p class="section-text">기본 무료 리딩 + 광고 보고 추가 리딩 가능해요.</p>

            <h3 class="subsection-title">Q. 해석이 마음에 안 들어요</h3>
            <p class="section-text">
              MBTI를 알려주거나 질문을 더 구체적으로 적으면 해석이 정확해져요.
              그래도 이상하다면 문의 폼으로 보내줘 — 직접 봐줄게.
            </p>

            <h3 class="subsection-title">Q. 광고를 더 안 보고 싶어요</h3>
            <p class="section-text">
              곧 구독·포인트 제도 도입할 예정이야. 정식 출시 전이라 양해 부탁해.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { useSeoMeta } from '@/composables/useSeoMeta'

useSeoMeta(
  '문의하기 — 세라피나',
  '세라피나 운영팀에게 직접 문의·제안·버그 신고하세요. 24시간 안에 답장드려요.',
  '세라피나 문의, 타로 문의, 버그 신고'
)

const form = ref({
  name: '',
  email: '',
  category: 'bug',
  message: '',
})

const submitting = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const canSubmit = computed(() => {
  return form.value.name.trim() && form.value.email.trim() && form.value.message.trim()
})

async function submitContact() {
  if (!canSubmit.value || submitting.value) return
  submitting.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const sessionId = (typeof window !== 'undefined' && localStorage.getItem('tarot_session_id')) || 'anonymous'
    await axios.post('/api/submit-contact', {
      session_id: sessionId,
      type: form.value.category,
      name: form.value.name,
      email: form.value.email,
      message: form.value.message,
    })
    successMsg.value = '문의 보냈어요! 24시간 안에 답장드릴게요 ✨'
    form.value = { name: '', email: '', category: 'bug', message: '' }
  } catch (err: any) {
    if (err?.response?.status === 429) {
      errorMsg.value = '잠시 후 다시 보내줘 (너무 자주 보냈어)'
    } else {
      errorMsg.value = '전송에 실패했어. 잠시 후 다시 시도해줘.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.contact-email-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--accent-yellow);
  border: 2px solid var(--text-primary);
  border-radius: 14px;
  margin-top: 14px;
  box-shadow: 3px 3px 0 var(--text-primary);
  flex-wrap: wrap;
}

.contact-email-label {
  font-weight: 800;
  color: var(--text-primary);
  font-size: 0.92rem;
}

.contact-email-link {
  color: var(--primary-color);
  font-weight: 800;
  font-size: 1rem;
  text-decoration: none;
  letter-spacing: -0.01em;
}

.contact-email-link:hover {
  text-decoration: underline;
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 6px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row label {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary);
}

.form-input {
  padding: 11px 14px;
  border: 2px solid var(--text-primary);
  border-radius: 10px;
  font-size: 0.95rem;
  background: var(--card-bg);
  color: var(--text-primary);
  font-family: inherit;
  outline: none;
  transition: box-shadow 0.15s;
}

.form-input:focus {
  box-shadow: 2.5px 2.5px 0 var(--primary-color);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}

.contact-submit-btn {
  background: var(--primary-color);
  color: var(--text-primary);
  border: 2px solid var(--text-primary);
  border-radius: 12px;
  padding: 12px 18px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 3.5px 3.5px 0 var(--text-primary);
  transition: all 0.15s;
  letter-spacing: -0.01em;
  margin-top: 4px;
}

.contact-submit-btn:hover:not(:disabled) {
  transform: translate(-1.5px, -1.5px);
  box-shadow: 5px 5px 0 var(--text-primary);
}

.contact-submit-btn:active {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0 var(--text-primary);
}

.contact-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-success {
  background: var(--accent-green);
  border: 1.5px solid var(--text-primary);
  border-radius: 10px;
  padding: 10px 14px;
  margin: 6px 0 0;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.form-error {
  background: rgba(251, 113, 133, 0.18);
  border: 1.5px solid var(--text-primary);
  border-radius: 10px;
  padding: 10px 14px;
  margin: 6px 0 0;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.subsection-title {
  margin-top: 18px;
}
</style>
