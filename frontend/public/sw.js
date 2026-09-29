// Service Worker for Offline Support (Performance Optimized)
// Version: 1.0.3 (auto-generated from package.json)
const APP_VERSION = '1.0.3';
const BUILD_TIMESTAMP = '1788322321298'; // Replaced at build time
const CACHE_VERSION = `${APP_VERSION}-${BUILD_TIMESTAMP}`;
const CACHE_NAME = `tarot-seraphina-v${CACHE_VERSION}`;
const STATIC_CACHE = `tarot-static-v${CACHE_VERSION}`;
const DYNAMIC_CACHE = `tarot-dynamic-v${CACHE_VERSION}`;

// Files to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  // Core app files will be added by Vite build process
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
  
  // Take control immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE;
            })
            .map((cacheName) => {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }

  // Skip 카카오 애드핏 스크립트 (항상 네트워크에서 가져오기)
  if (url.hostname === 't1.daumcdn.net' || url.pathname.includes('ba.min.js')) {
    return;
  }

  // Skip Google AdSense 스크립트 (항상 네트워크에서 가져오기)
  if (url.hostname === 'pagead2.googlesyndication.com' || url.hostname === 'adservice.google.com') {
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // HTML(내비게이션)은 네트워크 우선.
  // 예전에는 index.html까지 캐시 우선이라 배포 후 재방문자가 옛 index.html을 받았고,
  // 거기 적힌 옛 해시 청크(TarotReadingView.<옛해시>.js)가 404가 나서 화면이 안 넘어갔다.
  // HTML은 항상 새로 받고 네트워크가 안 될 때만 캐시를 쓴다.
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(request).then((c) => c || caches.match('/index.html')))
    );
    return;
  }

  // Handle static assets
  // 현재 버전 캐시에서만 찾는다. 인자 없는 caches.match()는 이 오리진의 캐시를
  // 전부 뒤지기 때문에 옛 배포본이 계속 살아남는다.
  event.respondWith(
    Promise.all([caches.open(STATIC_CACHE), caches.open(DYNAMIC_CACHE)])
      .then(([staticCache, dynamicCache]) =>
        staticCache.match(request).then((hit) => hit || dynamicCache.match(request))
      )
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        // Try to fetch from network
        return fetch(request)
          .then((networkResponse) => {
            // Cache successful responses
            if (networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(DYNAMIC_CACHE)
                .then((cache) => {
                  cache.put(request, responseClone);
                });
            }
            
            return networkResponse;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (request.destination === 'document') {
              return caches.match('/index.html');
            }
            
            // Return offline response for other requests
            return new Response(
              JSON.stringify({
                error: 'Offline',
                message: '인터넷 연결을 확인해주세요'
              }),
              {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
      })
  );
});

// Handle API requests with offline fallback
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful interpretations for offline access
    if (networkResponse.status === 200 && url.pathname === '/api/interpret') {
      const responseClone = networkResponse.clone();
      const cache = await caches.open(DYNAMIC_CACHE);
      await cache.put(request, responseClone);
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('[SW] Network failed, trying offline mode');
    
    // For tarot interpretations, provide basic offline response
    if (url.pathname === '/api/interpret') {
      return handleOfflineInterpretation(request);
    }
    
    // For other API requests, return cached response if available
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline error
    return new Response(
      JSON.stringify({
        error: 'Offline',
        message: '현재 오프라인 상태입니다. 인터넷 연결을 확인해주세요.'
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Basic offline tarot interpretation
async function handleOfflineInterpretation(request) {
  try {
    const body = await request.clone().json();
    const cards = body.cards || [];
    
    // Basic offline interpretation using stored card meanings
    const offlineInterpretation = generateOfflineInterpretation(cards, body.question);
    
    // Return as server-sent events format for compatibility
    const responseText = `data: ${JSON.stringify({
      content: offlineInterpretation,
      session_id: 'offline-' + Date.now(),
      offline: true
    })}\n\ndata: ${JSON.stringify({ done: true })}\n\n`;
    
    return new Response(responseText, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    });
    
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Offline parsing failed',
        message: '오프라인 해석을 생성할 수 없습니다.'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Generate basic offline interpretation
function generateOfflineInterpretation(cards, question) {
  const offlineCardMeanings = {
    // Major Arcana - basic meanings
    'maj00': '새로운 시작과 무한한 가능성',
    'maj01': '의지력과 창조적 에너지', 
    'maj02': '직감과 내면의 지혜',
    'maj03': '풍요로움과 모성적 사랑',
    'maj04': '안정감과 권위적 힘',
    'maj05': '전통과 영적 지도',
    'maj06': '사랑과 선택의 기로',
    'maj07': '의지력과 승리',
    'maj08': '내면의 힘과 용기',
    'maj09': '성찰과 내적 탐구',
    'maj10': '운명적 변화와 순환',
    'maj11': '균형과 공정함',
    'maj12': '희생과 새로운 관점',
    'maj13': '변화와 재생',
    'maj14': '조화와 중용',
    'maj15': '유혹과 속박',
    'maj16': '급격한 변화와 해방',
    'maj17': '희망과 영감',
    'maj18': '환상과 불안',
    'maj19': '성공과 기쁨',
    'maj20': '각성과 새로운 인식',
    'maj21': '완성과 성취'
  };
  
  if (!cards.length) {
    return `🔮 **오프라인 모드**\n\n안녕하세요! 지금은 인터넷 연결이 없어서 세라피나와 직접 대화할 수는 없지만, 기본적인 안내를 드릴 수 있어요.\n\n"${question}"\n\n오프라인 상태에서는 카드 해석을 제공할 수 없지만, 잠시 마음을 가다듬고 자신의 내면에 집중해보세요. 때로는 외부의 조언보다 자신만의 직감이 더 정확할 때도 있거든요.\n\n인터넷이 연결되면 다시 세라피나와 대화해보세요! 💫`;
  }
  
  let interpretation = `🔮 **오프라인 타로 해석**\n\n안녕하세요! 현재 오프라인 상태라서 세라피나와 직접 대화할 수는 없지만, 선택하신 카드들의 기본적인 의미를 알려드릴게요.\n\n`;
  
  cards.forEach((card, index) => {
    const isReversed = card.endsWith('_r');
    const baseCard = card.replace('_r', '');
    const meaning = offlineCardMeanings[baseCard] || '새로운 인사이트';
    const position = ['첫 번째', '두 번째', '세 번째', '네 번째', '다섯 번째'][index] || `${index + 1}번째`;
    
    interpretation += `**${position} 카드**: ${meaning}`;
    if (isReversed) {
      interpretation += ' (역방향 - 내면의 성찰이 필요)';
    }
    interpretation += '\n\n';
  });
  
  interpretation += `이는 기본적인 해석이며, 인터넷이 연결되면 세라피나가 더 자세하고 개인적인 해석을 해드릴 수 있어요. \n\n지금은 이 메시지를 참고하여 스스로 생각해보는 시간을 가져보세요. 💫`;
  
  return interpretation;
}

// Listen for messages from main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLIENT_OFFLINE') {
    console.log('[SW] Client went offline');
  }
  
  if (event.data && event.data.type === 'CLIENT_ONLINE') {
    console.log('[SW] Client came online');
  }
});

// Handle background sync for queued actions (if supported)
if ('sync' in self.registration) {
  self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'background-sync-tarot') {
      event.waitUntil(syncTarotData());
    }
  });
}

// Sync queued tarot readings when back online
async function syncTarotData() {
  try {
    // This would sync any queued feedback or readings
    console.log('[SW] Syncing tarot data in background');
    
    // Get queued data from IndexedDB or localStorage
    // This is a placeholder for actual sync logic
    
    return Promise.resolve();
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
    throw error;
  }
}