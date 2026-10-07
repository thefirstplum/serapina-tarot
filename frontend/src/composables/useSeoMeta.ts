import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

interface SeoMetaOptions {
  /** 페이지 URL의 path 부분만 (예: '/blog/love-tarot'). 미지정 시 현재 경로 사용 */
  pathOverride?: string
  /** OG 이미지 URL. 미지정 시 사이트 기본 이미지 */
  ogImage?: string
  /** Article schema 적용 시 추가 정보 */
  article?: {
    publishedTime?: string
    modifiedTime?: string
    author?: string
    section?: string
  }
}

const SITE_ORIGIN = 'https://serapina.kr'
const DEFAULT_OG_IMAGE = `${SITE_ORIGIN}/icons/icon-512x512.png`

function upsertMeta(selector: string, attrName: 'name' | 'property', attrValue: string, content: string) {
  let el = document.querySelector(selector) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attrName, attrValue)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertLink(rel: string, href: string) {
  let el = document.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

const ARTICLE_LD_ID = 'page-article-jsonld'

function setArticleJsonLd(data: object) {
  const existing = document.getElementById(ARTICLE_LD_ID)
  if (existing) existing.remove()
  const script = document.createElement('script')
  script.id = ARTICLE_LD_ID
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(data)
  document.head.appendChild(script)
}

function clearArticleJsonLd() {
  const existing = document.getElementById(ARTICLE_LD_ID)
  if (existing) existing.remove()
}

export function useSeoMeta(
  title: string,
  description?: string,
  keywords?: string,
  options: SeoMetaOptions = {}
) {
  const { locale } = useI18n()

  onMounted(() => {
    document.title = title
    document.documentElement.lang = locale.value

    const path = options.pathOverride ?? window.location.pathname
    const canonicalUrl = `${SITE_ORIGIN}${path}`
    const ogImageUrl = options.ogImage || DEFAULT_OG_IMAGE

    // Description + keywords
    if (description) {
      upsertMeta('meta[name="description"]', 'name', 'description', description)
      upsertMeta('meta[property="og:description"]', 'property', 'og:description', description)
      upsertMeta('meta[name="twitter:description"]', 'name', 'twitter:description', description)
    }
    if (keywords) {
      upsertMeta('meta[name="keywords"]', 'name', 'keywords', keywords)
    }

    // Title (OG·Twitter)
    upsertMeta('meta[property="og:title"]', 'property', 'og:title', title)
    upsertMeta('meta[name="twitter:title"]', 'name', 'twitter:title', title)

    // URL (canonical·og:url), SPA라 페이지마다 갱신
    upsertLink('canonical', canonicalUrl)
    upsertMeta('meta[property="og:url"]', 'property', 'og:url', canonicalUrl)

    // OG image
    upsertMeta('meta[property="og:image"]', 'property', 'og:image', ogImageUrl)
    upsertMeta('meta[name="twitter:image"]', 'name', 'twitter:image', ogImageUrl)

    // Locale
    const localeMap: { [key: string]: string } = {
      ko: 'ko_KR', en: 'en_US', ja: 'ja_JP', fr: 'fr_FR', de: 'de_DE'
    }
    upsertMeta('meta[property="og:locale"]', 'property', 'og:locale', localeMap[locale.value] || 'ko_KR')

    // Article schema (블로그 포스트 등)
    if (options.article) {
      setArticleJsonLd({
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: title,
        description: description || '',
        image: ogImageUrl,
        author: {
          '@type': 'Person',
          name: options.article.author || '세라피나'
        },
        publisher: {
          '@type': 'Organization',
          name: '세라피나 타로',
          logo: {
            '@type': 'ImageObject',
            url: `${SITE_ORIGIN}/icons/icon-512x512.png`
          }
        },
        datePublished: options.article.publishedTime,
        dateModified: options.article.modifiedTime || options.article.publishedTime,
        articleSection: options.article.section,
        mainEntityOfPage: {
          '@type': 'WebPage',
          '@id': canonicalUrl
        }
      })
    } else {
      // 일반 페이지에선 article schema 제거 (이전 페이지 잔존 방지)
      clearArticleJsonLd()
    }
  })

  onUnmounted(() => {
    clearArticleJsonLd()
  })
}
