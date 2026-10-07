import './assets/main.css'
import './assets/detail-page.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import vuetify from './plugins/vuetify'

import i18n from './i18n'

import App from './App.vue'
import router from './router'
import { registerServiceWorker, installChunkErrorRecovery } from './utils/sw-register'
import { initGA } from './utils/analytics'

// Google Analytics 초기화
const gaId = import.meta.env.VITE_GA_ID
if (gaId && gaId !== 'G-XXXXXXXXXX') {
  // GA 스크립트 동적 로드
  const script1 = document.createElement('script')
  script1.async = true
  script1.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`
  document.head.appendChild(script1)

  // gtag 함수 초기화
  window.dataLayer = window.dataLayer || []
  window.gtag = function() {
    window.dataLayer?.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', gaId, {
    send_page_view: false // router에서 수동으로 페이지뷰 전송
  })

  console.log('Google Analytics initialized:', gaId)
}

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(vuetify)
app.use(i18n)

// 인증 상태 초기화 (토큰이 있으면 유저 정보 불러오기)
import { useAuthStore } from './stores/authStore'
const authStore = useAuthStore()
authStore.init()

app.mount('#app')

// 서비스 워커 등록 및 오프라인 지원 활성화
if (import.meta.env.PROD) {
  // 배포 후 옛 번들 때문에 나는 청크 404 복구
  installChunkErrorRecovery()
  registerServiceWorker().then((registration) => {
    if (registration) {
      console.log('오프라인 지원이 활성화되었습니다')
    }
  })
}
