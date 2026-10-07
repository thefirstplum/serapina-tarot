<template>
  <Transition name="slide-up">
    <div v-if="show" class="pwa-install-banner" role="region" aria-label="앱 설치 안내">
      <button class="banner-close" @click="dismiss" aria-label="닫기">
        <v-icon size="20">mdi-close</v-icon>
      </button>

      <img src="/icons/icon-192x192.png" alt="" class="banner-icon" width="56" height="56" />

      <div class="banner-text">
        <div class="banner-title">{{ title }}</div>
        <div class="banner-desc">{{ desc }}</div>
      </div>

      <button v-if="!isIOS" class="banner-cta" @click="install">
        홈 화면에 추가
      </button>
      <button v-else class="banner-cta" @click="showIOSGuide = true">
        방법 보기
      </button>
    </div>
  </Transition>

  <!-- iOS 안내 모달 -->
  <Transition name="fade">
    <div v-if="showIOSGuide" class="ios-modal-backdrop" @click="showIOSGuide = false">
      <div class="ios-modal" @click.stop>
        <div class="ios-modal-header">
          <h3>홈 화면에 추가하는 법</h3>
          <button class="modal-close" @click="showIOSGuide = false" aria-label="닫기">
            <v-icon>mdi-close</v-icon>
          </button>
        </div>
        <ol class="ios-steps">
          <li>
            <span class="step-num">1</span>
            <span>아래 <strong>공유 버튼</strong> <v-icon size="18" style="vertical-align: -3px;">mdi-export-variant</v-icon> 누르기</span>
          </li>
          <li>
            <span class="step-num">2</span>
            <span>"<strong>홈 화면에 추가</strong>" 선택</span>
          </li>
          <li>
            <span class="step-num">3</span>
            <span>오른쪽 위 "<strong>추가</strong>" 탭</span>
          </li>
        </ol>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const show = ref(false)
const showIOSGuide = ref(false)
const isIOS = ref(false)
const deferredPrompt = ref<any>(null)

const title = '앱처럼 빠르게 쓰기'
const desc = '홈 화면에 추가하면 오프라인도 OK ✨'

const STORAGE_KEY = 'pwa_install_dismissed_at'
const DISMISS_DAYS = 7
const SHOW_DELAY = 3000 // 첫 등장 3초 후

// 현재 PWA로 실행 중인지
function isRunningStandalone(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         // @ts-ignore - iOS Safari
         window.navigator.standalone === true
}

// 최근 dismiss 후 충분히 지났는지
function shouldShow(): boolean {
  const dismissed = localStorage.getItem(STORAGE_KEY)
  if (!dismissed) return true
  const lastTime = parseInt(dismissed, 10)
  if (isNaN(lastTime)) return true
  const daysSince = (Date.now() - lastTime) / (1000 * 60 * 60 * 24)
  return daysSince >= DISMISS_DAYS
}

// 안드로이드/데스크탑: beforeinstallprompt
function onBeforeInstallPrompt(e: Event) {
  e.preventDefault()
  deferredPrompt.value = e
  if (!isRunningStandalone() && shouldShow()) {
    setTimeout(() => { show.value = true }, SHOW_DELAY)
  }
}

// 설치 완료 시 배너 바로 숨김
function onAppInstalled() {
  show.value = false
  showIOSGuide.value = false
  deferredPrompt.value = null
}

function dismiss() {
  show.value = false
  localStorage.setItem(STORAGE_KEY, String(Date.now()))
}

async function install() {
  if (!deferredPrompt.value) return
  deferredPrompt.value.prompt()
  const choice = await deferredPrompt.value.userChoice
  if (choice.outcome === 'accepted') {
    show.value = false
  } else {
    dismiss() // 거부 시 7일 후 재시도
  }
  deferredPrompt.value = null
}

onMounted(() => {
  // 이미 PWA로 실행 중이면 표시 안 함
  if (isRunningStandalone()) {
    return
  }

  // iOS 감지 (beforeinstallprompt 미지원)
  const ua = navigator.userAgent.toLowerCase()
  isIOS.value = /iphone|ipad|ipod/.test(ua) && !/(crios|fxios)/.test(ua)

  window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
  window.addEventListener('appinstalled', onAppInstalled)

  // iOS는 beforeinstallprompt가 없어서 직접 띄움 (dismiss 조건 통과 시)
  if (isIOS.value && shouldShow()) {
    setTimeout(() => { show.value = true }, SHOW_DELAY)
  }
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
  window.removeEventListener('appinstalled', onAppInstalled)
})
</script>

<style scoped>
/* 하단 고정 배너 */
.pwa-install-banner {
  position: fixed;
  bottom: 16px;
  left: 16px;
  right: 16px;
  z-index: 9000;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px 14px 16px;
  background: var(--accent-yellow);
  border: 2px solid var(--text-primary);
  border-radius: 18px;
  box-shadow: 5px 5px 0 var(--primary-color);
  max-width: 520px;
  margin: 0 auto;
}

.banner-icon {
  flex-shrink: 0;
  border-radius: 12px;
  border: 1.5px solid var(--text-primary);
  background: var(--card-bg);
  object-fit: contain;
}

.banner-text {
  flex: 1;
  min-width: 0;
}

.banner-title {
  color: var(--text-primary);
  font-size: 0.98rem;
  font-weight: 800;
  letter-spacing: -0.015em;
  line-height: 1.3;
}

.banner-desc {
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 500;
  opacity: 0.85;
  margin-top: 2px;
}

.banner-cta {
  background: var(--primary-color);
  color: var(--text-primary);
  border: 2px solid var(--text-primary);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 0.85rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 2.5px 2.5px 0 var(--text-primary);
  transition: all 0.15s;
  flex-shrink: 0;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.banner-cta:hover {
  transform: translate(-1px, -1px);
  box-shadow: 3.5px 3.5px 0 var(--text-primary);
}

.banner-cta:active {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0 var(--text-primary);
}

.banner-close {
  position: absolute;
  top: 6px;
  right: 6px;
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-primary);
  opacity: 0.6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-close:hover {
  opacity: 1;
  background: rgba(26, 26, 46, 0.06);
}

/* iOS 안내 모달 */
.ios-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(26, 26, 46, 0.5);
  z-index: 9100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.ios-modal {
  background: var(--card-bg);
  border: 2px solid var(--text-primary);
  border-radius: 20px;
  padding: 24px 24px 28px;
  max-width: 380px;
  width: 100%;
  box-shadow: 6px 6px 0 var(--primary-color);
}

.ios-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.ios-modal-header h3 {
  color: var(--text-primary);
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.015em;
}

.modal-close {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-primary);
  opacity: 0.7;
  border-radius: 50%;
}
.modal-close:hover { opacity: 1; }

.ios-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ios-steps li {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.5;
}

.step-num {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  background: var(--accent-yellow);
  border: 2px solid var(--text-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  box-shadow: 2px 2px 0 var(--text-primary);
}

/* 슬라이드 업 애니메이션 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(120%);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 모바일 */
@media (max-width: 480px) {
  .pwa-install-banner {
    bottom: 12px;
    left: 10px;
    right: 10px;
    padding: 12px 12px;
    gap: 10px;
  }
  .banner-icon {
    width: 48px !important;
    height: 48px !important;
  }
  .banner-title { font-size: 0.92rem; }
  .banner-desc { font-size: 0.76rem; }
  .banner-cta {
    padding: 9px 11px;
    font-size: 0.8rem;
  }
}
</style>
