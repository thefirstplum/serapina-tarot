/**
 * Google Analytics 설정 및 이벤트 추적
 */

// GA 초기화 (환경변수에서 GA ID가 있을 때만)
export const initGA = () => {
  const gaId = import.meta.env.VITE_GA_ID
  if (!gaId || gaId === 'G-XXXXXXXXXX') {
    console.log('GA disabled in development')
    return
  }

  // GA 스크립트가 이미 로드되어 있으면 설정
  if (window.gtag) {
    window.gtag('config', gaId)
  }
}

// 페이지뷰 추적
export const trackPageView = (pagePath: string) => {
  if (window.gtag) {
    window.gtag('event', 'page_view', {
      page_path: pagePath
    })
  }
}

// 이벤트 추적
export const trackEvent = (
  eventName: string,
  params?: Record<string, any>
) => {
  if (window.gtag) {
    window.gtag('event', eventName, params)
  }
}

// 타로 리딩 추적
export const trackTarotReading = (questionType: string) => {
  trackEvent('tarot_reading', {
    question_type: questionType,
    event_category: 'engagement'
  })
}

// 카드 선택 추적
export const trackCardSelection = (cardNames: string[]) => {
  trackEvent('card_selection', {
    cards: cardNames.join(', '),
    event_category: 'engagement'
  })
}

// 세션 시작 추적
export const trackSessionStart = () => {
  trackEvent('session_start', {
    event_category: 'engagement'
  })
}

// 새로운 대화 시작 추적
export const trackNewConversation = () => {
  trackEvent('new_conversation', {
    event_category: 'engagement'
  })
}

// 질문 입력 추적
export const trackQuestionSubmit = (questionLength: number) => {
  trackEvent('question_submit', {
    event_category: 'engagement',
    question_length: questionLength
  })
}

// 카드 선택 완료 추적 (개별 카드 포함)
export const trackCardsSelected = (cards: string[], questionType: string) => {
  trackEvent('cards_selected', {
    event_category: 'engagement',
    card_count: cards.length,
    cards: cards.join(', '),
    question_type: questionType
  })
}

// 타로 해석 완료 추적
export const trackInterpretationComplete = (responseLength: number, duration: number) => {
  trackEvent('interpretation_complete', {
    event_category: 'engagement',
    response_length: responseLength,
    duration_seconds: Math.round(duration / 1000)
  })
}

// 공유 버튼 클릭 추적
export const trackShare = (shareMethod?: string) => {
  trackEvent('share_reading', {
    event_category: 'social',
    share_method: shareMethod || 'unknown'
  })
}

// 타로 기록 보기 추적
export const trackViewHistory = () => {
  trackEvent('view_history', {
    event_category: 'engagement'
  })
}

// 정보 패널 열기 추적
export const trackInfoOpen = () => {
  trackEvent('info_open', {
    event_category: 'engagement'
  })
}

// 테마 변경 추적
export const trackThemeChange = (theme: string) => {
  trackEvent('theme_change', {
    event_category: 'customization',
    theme: theme
  })
}

// 광고 클릭 추적
export const trackAdClick = (adSlot: string) => {
  trackEvent('ad_click', {
    event_category: 'monetization',
    ad_slot: adSlot
  })
}

// 에러 추적
export const trackError = (errorType: string, errorMessage: string) => {
  trackEvent('error', {
    event_category: 'error',
    error_type: errorType,
    error_message: errorMessage
  })
}

// 사용자 인게이지먼트 추적 (스크롤 깊이)
export const trackScrollDepth = (depth: number) => {
  trackEvent('scroll_depth', {
    event_category: 'engagement',
    depth_percentage: depth
  })
}

// 세션 시간 추적
export const trackSessionDuration = (durationSeconds: number) => {
  trackEvent('session_duration', {
    event_category: 'engagement',
    duration_seconds: durationSeconds
  })
}

// 전환 퍼널 이벤트

// 리딩 시작 (질문 입력 단계 진입)
export const trackReadingStarted = (source: string) => {
  trackEvent('reading_started', {
    event_category: 'funnel',
    source, // 'landing_cta', 'landing_input', 'landing_category', 'nav'
  })
}

// 리딩 완료 (결과 화면 도달)
export const trackReadingCompleted = (spreadType: string, cardCount: number) => {
  trackEvent('reading_completed', {
    event_category: 'funnel',
    spread_type: spreadType,
    card_count: cardCount,
  })
}

// 공유 클릭 (방법별)
export const trackShareClicked = (method: string) => {
  trackEvent('share_clicked', {
    event_category: 'funnel',
    share_method: method, // 'native', 'copy', 'download'
  })
}

// 공유 완료
export const trackShareCompleted = (method: string) => {
  trackEvent('share_completed', {
    event_category: 'funnel',
    share_method: method,
  })
}

// 구독 페이지 조회
export const trackSubscriptionViewed = (source: string) => {
  trackEvent('subscription_viewed', {
    event_category: 'monetization',
    source, // 'ad_modal', 'rewarded_dialog', 'premium_nudge', 'nav'
  })
}

// 구독 결제 시작
export const trackSubscriptionStarted = (planCode: string, amount: number) => {
  trackEvent('subscription_started', {
    event_category: 'monetization',
    plan_code: planCode,
    amount,
  })
}

// 구독 결제 완료
export const trackSubscriptionCompleted = (planCode: string, amount: number) => {
  trackEvent('purchase', {
    event_category: 'monetization',
    plan_code: planCode,
    value: amount,
    currency: 'KRW',
  })
}

// 보상형 광고 시청
export const trackRewardedAdWatched = () => {
  trackEvent('rewarded_ad_watched', {
    event_category: 'monetization',
  })
}

// 일일 한도 도달
export const trackDailyLimitReached = () => {
  trackEvent('daily_limit_reached', {
    event_category: 'funnel',
  })
}

// CTA 클릭 추적
export const trackCtaClick = (ctaName: string, location: string) => {
  trackEvent('cta_click', {
    event_category: 'engagement',
    cta_name: ctaName,
    location,
  })
}

// 타입 선언은 env.d.ts에서 처리
