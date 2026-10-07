// Service Worker 등록 (자동 업데이트 모드)
let refreshing = false
let recovering = false

/**
 * 청크 로드 실패 복구.
 *
 * 배포로 청크 해시가 바뀌면 옛 번들을 들고 있는 브라우저가 이미 없는 파일을 요청해 404를 받고,
 * 동적 import가 실패해 페이지가 안 넘어간다. 이때 캐시와 서비스워커를 비우고 한 번 새로고침한다.
 * 새로고침이 반복되지 않게 세션당 1회만.
 */
function isChunkLoadError(msg: string): boolean {
  return (
    msg.includes('Failed to fetch dynamically imported module') ||
    msg.includes('Importing a module script failed') ||
    msg.includes('error loading dynamically imported module')
  )
}

async function recoverFromStaleBundle() {
  if (recovering) return
  if (sessionStorage.getItem('sw-chunk-recovered') === '1') {
    console.error('[SW] 청크 복구를 이미 시도했습니다. 수동 새로고침이 필요합니다.')
    return
  }
  recovering = true
  sessionStorage.setItem('sw-chunk-recovered', '1')
  console.warn('[SW] 옛 번들 감지, 캐시를 비우고 새로고침합니다')
  try {
    const keys = await caches.keys()
    await Promise.all(keys.map((k) => caches.delete(k)))
    const regs = await navigator.serviceWorker.getRegistrations()
    await Promise.all(regs.map((r) => r.unregister()))
  } catch (e) {
    console.error('[SW] 캐시 정리 실패:', e)
  }
  location.reload()
}

export function installChunkErrorRecovery() {
  if (!('serviceWorker' in navigator)) return

  window.addEventListener('error', (e) => {
    const msg = (e as ErrorEvent)?.message || ''
    if (isChunkLoadError(msg)) void recoverFromStaleBundle()
  })

  window.addEventListener('unhandledrejection', (e) => {
    const msg = String((e as PromiseRejectionEvent)?.reason?.message || e?.reason || '')
    if (isChunkLoadError(msg)) void recoverFromStaleBundle()
  })
}

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.log('Service Worker not supported')
    return null
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
      updateViaCache: 'none'
    })

    console.log('[SW] 등록 완료:', registration.scope)

    // 새 SW 발견 시 자동 활성화 (배포 직후 바로 반영되게)
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing
      if (!newWorker) return
      console.log('[SW] 새 버전 감지, 자동 적용')
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // sw.js install 시 self.skipWaiting() 자동 호출하지만 안전하게 명시 전송
          newWorker.postMessage({ type: 'SKIP_WAITING' })
          // 알림 이벤트 (선택적 토스트 UI용)
          showUpdateAvailableNotification(registration)
        }
      })
    })

    // SW 교체 완료 시 한 번만 자동 새로고침
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (refreshing) return
      refreshing = true
      console.log('[SW] 새 버전 활성화, 새로고침')
      // 진행 중 fetch 정리 시간 800ms
      setTimeout(() => window.location.reload(), 800)
    })

    // 탭 복귀 시 업데이트 확인
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        registration.update().catch(() => {})
      }
    })

    // 주기적으로 업데이트 확인 (5분마다)
    setInterval(() => {
      registration.update().catch(() => {})
    }, 5 * 60 * 1000)

    // SW 메시지 리스너
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'OFFLINE_FALLBACK') {
        console.log('[SW] 오프라인 폴백 활성화')
      }
    })

    return registration
  } catch (error) {
    console.error('[SW] 등록 실패:', error)
    return null
  }
}

function showUpdateAvailableNotification(registration: ServiceWorkerRegistration) {
  // Create a simple notification for app updates
  const updateAvailable = new CustomEvent('sw-update-available', {
    detail: { registration }
  })
  window.dispatchEvent(updateAvailable)
}

export async function updateServiceWorker(registration: ServiceWorkerRegistration): Promise<void> {
  if (!registration.waiting) return

  // Send message to service worker to skip waiting
  registration.waiting.postMessage({ type: 'SKIP_WAITING' })

  // Reload the page after the new service worker takes control
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload()
  })
}

// Check if app is running from home screen (PWA mode)
export function isRunningAsPWA(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.matchMedia('(display-mode: fullscreen)').matches ||
         // @ts-ignore - for iOS Safari
         (window.navigator.standalone === true)
}

// Show install prompt for PWA
export function showInstallPrompt(): Promise<boolean> {
  return new Promise((resolve) => {
    let deferredPrompt: any = null

    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      deferredPrompt = e
      
      // Show custom install button or prompt
      const installEvent = new CustomEvent('pwa-install-available', {
        detail: { 
          prompt: () => {
            if (deferredPrompt) {
              deferredPrompt.prompt()
              deferredPrompt.userChoice.then((choiceResult: any) => {
                resolve(choiceResult.outcome === 'accepted')
                deferredPrompt = null
              })
            }
          }
        }
      })
      window.dispatchEvent(installEvent)
    })

    // Handle iOS Safari install prompt
    if ('standalone' in navigator && !window.matchMedia('(display-mode: standalone)').matches) {
      const iosInstallEvent = new CustomEvent('pwa-ios-install-available')
      window.dispatchEvent(iosInstallEvent)
    }
  })
}

// Cache management utilities
export async function clearAppCache(): Promise<void> {
  if ('caches' in window) {
    const cacheNames = await caches.keys()
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    )
    console.log('App cache cleared')
  }
}

export async function getCacheSize(): Promise<string> {
  if ('caches' in window && 'storage' in navigator && 'estimate' in navigator.storage) {
    try {
      const estimate = await navigator.storage.estimate()
      const usedMB = ((estimate.usage || 0) / 1024 / 1024).toFixed(2)
      return `${usedMB} MB`
    } catch {
      return 'Unknown'
    }
  }
  return 'Not available'
}