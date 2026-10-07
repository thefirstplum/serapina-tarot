// SEO 설정 (환경변수 기반)

export const SEO_CONFIG = {
  appUrl: import.meta.env.VITE_APP_URL || 'https://serapina.kr',
  appName: import.meta.env.VITE_APP_NAME || '세라피나 타로',
  gaId: import.meta.env.VITE_GA_ID || '',
  
  // 구조화된 데이터용
  structuredData: {
    webApplication: {
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      name: '세라피나 타로',
      applicationCategory: 'LifestyleApplication',
      operatingSystem: 'All',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'KRW'
      },
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.8',
        ratingCount: '1250'
      }
    }
  }
}

export const getFullUrl = (path: string = '') => {
  const baseUrl = SEO_CONFIG.appUrl.replace(/\/$/, '')
  const cleanPath = path.replace(/^\//, '')
  return cleanPath ? `${baseUrl}/${cleanPath}` : baseUrl
}
