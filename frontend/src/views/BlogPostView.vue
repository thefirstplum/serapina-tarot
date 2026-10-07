<template>
  <div class="app-main">
      <div class="page-layout" v-if="post && !loading">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              to="/blog"
              icon
              variant="text"
              class="back-button"
            >
              <v-icon color="white">mdi-arrow-left</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ post.title }}</h1>
              <p class="page-subtitle">{{ post.category }} · {{ readingTime }}분 읽기 · 👁️ {{ post.view_count }}{{ t('blog.post.viewCount') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <div class="content-layout">
              <!-- Main Content -->
              <div class="main-content">
                <!-- 추천 MBTI 뱃지 (본문 앞) -->
                <div v-if="post && (post as any).recommended_mbti && (post as any).recommended_mbti.length > 0" class="mbti-recommend-box">
                  <span class="mbti-recommend-label">💎 이 글, 특히 도움돼</span>
                  <div class="mbti-chip-row">
                    <span v-for="m in (post as any).recommended_mbti" :key="m" class="mbti-chip">{{ m }}</span>
                  </div>
                </div>

                <!-- Situation Section -->
                <div class="info-card" v-if="parsedContent.situation">
                  <h2 class="section-title">{{ t('blog.post.situationTitle') }}</h2>
                  <p class="section-text">{{ parsedContent.situation }}</p>
                </div>

                <!-- Empathy CTA (between situation and interpretations) -->
                <div class="empathy-cta" v-if="parsedContent.situation">
                  <p class="empathy-text">혹시 너도 비슷한 고민이야?</p>
                  <v-btn variant="flat" color="white" rounded="pill" size="small" :to="{ name: 'reading' }" class="empathy-btn" @click="onCtaClick('empathy_cta', 'blog_mid')">
                    나도 {{ post.category }} 고민 물어보기 →
                  </v-btn>
                </div>

                <!-- Cards Section -->
                <div class="info-card" v-if="parsedContent.cards && parsedContent.cards.length > 0">
                  <h2 class="section-title">{{ t('blog.post.cardsTitle') }}</h2>
                  <div class="cards-grid">
                    <div
                      v-for="(card, index) in parsedContent.cards"
                      :key="index"
                      class="card-item"
                    >
                      <div class="card-label">{{ t('blog.post.cardLabels')[index] }}</div>
                      <div class="card-name">{{ card }}</div>
                    </div>
                  </div>
                </div>

                <!-- Interpretations Section -->
                <div class="info-card" v-if="parsedContent.interpretations && parsedContent.interpretations.length > 0">
                  <h2 class="section-title">{{ t('blog.post.interpretationTitle') }}</h2>
                  <div
                    v-for="(interp, index) in parsedContent.interpretations"
                    :key="index"
                    class="interpretation-item"
                  >
                    <div v-html="interp"></div>
                  </div>
                </div>

                <!-- 인아티클 광고: 해석 뒤, advice 앞 (CTR 제일 높은 자리) -->
                <AdSenseBlock slot="6300968433" format="fluid" layout="in-article" />

                <!-- Advisor Profile (above advice) -->
                <div class="advisor-profile" v-if="parsedContent.advice">
                  <img src="/icons/symbol-64.png" class="advisor-avatar" alt="세라피나" width="36" height="36" style="object-fit: contain; border-radius: 50%;" />
                  <div class="advisor-info">
                    <span class="advisor-name">세라피나</span>
                    <span class="advisor-title">타로 AI 마스터</span>
                  </div>
                </div>

                <!-- Advice Section -->
                <div class="info-card" v-if="parsedContent.advice">
                  <h2 class="section-title">{{ t('blog.post.adviceTitle') }}</h2>
                  <div class="advice-content">
                    <div v-html="parsedContent.advice"></div>
                  </div>
                </div>

                <!-- Inline CTA (after interpretation) -->
                <div class="inline-cta-card">
                  <p class="inline-cta-text">{{ t('blog.post.inlineCtaText') }}</p>
                  <v-btn
                    color="var(--primary-color)"
                    variant="flat"
                    rounded="pill"
                    size="large"
                    :to="{ name: 'reading' }"
                    class="inline-cta-btn"
                    @click="onCtaClick('inline_cta', 'blog_bottom')"
                  >
                    <v-icon start>mdi-cards-playing-outline</v-icon>
                    {{ t('blog.post.inlineCtaButton') }}
                  </v-btn>
                </div>

                <!-- Share Buttons -->
                <div class="share-bar">
                  <span class="share-bar-label">{{ t('blog.post.shareTitle') }}</span>
                  <div class="share-bar-buttons">
                    <v-btn variant="outlined" rounded="pill" size="small" @click="sharePost">
                      <v-icon start size="16">mdi-share-variant</v-icon>
                      {{ t('blog.post.shareButton') }}
                    </v-btn>
                    <v-btn variant="outlined" rounded="pill" size="small" @click="copyPostLink">
                      <v-icon start size="16">mdi-link-variant</v-icon>
                      {{ t('blog.post.copyLinkButton') }}
                    </v-btn>
                  </div>
                </div>

                <!-- Fallback: Show raw content if parsing failed -->
                <div class="info-card" v-if="!isParsed">
                  <div class="post-content" v-html="post.content"></div>
                </div>
              </div>

              <!-- Sidebar -->
              <div class="sidebar">
                <div class="sidebar-card">
                  <h3 class="sidebar-title">{{ t('blog.post.categoryTitle') }}</h3>
                  <div class="keywords-grid">
                    <span class="keyword-chip">{{ post.category }}</span>
                  </div>
                </div>

                <div class="sidebar-card" v-if="post.tags && post.tags.length > 0">
                  <h3 class="sidebar-title">{{ t('blog.post.tagsTitle') }}</h3>
                  <div class="keywords-grid">
                    <span v-for="tag in post.tags" :key="tag" class="keyword-chip">{{ tag }}</span>
                  </div>
                </div>

                <div class="sidebar-card" v-if="post.cards && post.cards.length > 0">
                  <h3 class="sidebar-title">{{ t('blog.post.relatedCardsTitle') }}</h3>
                  <div class="keywords-grid">
                    <span v-for="card in post.cards" :key="card" class="keyword-chip">{{ card }}</span>
                  </div>
                </div>

                <div class="sidebar-card cta">
                  <h3 class="sidebar-title">{{ t('blog.post.ctaSidebarTitle') }}</h3>
                  <p class="sidebar-text">{{ t('blog.post.ctaSidebarText') }}</p>
                  <v-btn
                    block
                    color="white"
                    variant="elevated"
                    :to="{ name: 'reading' }"
                    class="sidebar-button"
                    @click="onCtaClick('sidebar_cta', 'blog_sidebar')"
                  >
                    {{ t('blog.post.startNowButton') }}
                  </v-btn>
                </div>
              </div>
            </div>

            <!-- Related Posts Section -->
            <div class="related-posts" v-if="relatedPosts.length > 0">
              <h3 class="related-title">이 이야기도 읽어봐</h3>
              <div class="related-grid">
                <router-link v-for="rp in relatedPosts" :key="rp.id" :to="`/blog/${rp.id}`" class="related-post-card">
                  <span class="related-emoji">{{ rp.emoji }}</span>
                  <div class="related-post-info">
                    <span class="related-post-title">{{ rp.title }}</span>
                    <span class="related-post-category">{{ rp.category }}</span>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- AdSense 광고: 본문 끝, CTA 앞 -->
            <AdSenseBlock slot="1696071761" />

            <!-- CTA Section -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ t('blog.post.ctaMainTitle') }}</h3>
                <p>{{ t('blog.post.ctaMainText') }}</p>
                <v-btn
                  size="large"
                  color="white"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="onCtaClick('bottom_cta', 'blog_footer')"
                >
                  {{ t('blog.post.startReadingButton') }}
                </v-btn>
              </div>
            </div>

            <!-- 하단 광고 -->
            <div style="margin-top: 16px;">
              <AdSenseBlock slot="1696071761" />
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-else-if="loading" class="page-layout">
        <div class="page-content">
          <div class="content-container" style="text-align: center; padding: 4rem 2rem;">
            <v-progress-circular
              indeterminate
              color="white"
              size="64"
            ></v-progress-circular>
            <p style="color: var(--text-primary); margin-top: 1rem; font-size: 1.1rem;">{{ t('blog.post.loading') }}</p>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else class="page-layout">
        <div class="page-content">
          <div class="content-container not-found">
            <div class="not-found-icon">😢</div>
            <h2 class="section-title">{{ t('blog.post.notFoundTitle') }}</h2>
            <p class="section-text">{{ error }}</p>
            <v-btn
              to="/blog"
              size="large"
              class="cta-button"
            >
              {{ t('blog.post.backButton') }}
            </v-btn>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useSeoMeta } from '@/composables/useSeoMeta'
import AdSenseBlock from '@/components/AdSenseBlock.vue'
import { trackShareClicked, trackShareCompleted, trackCtaClick, trackReadingStarted } from '@/utils/analytics'

interface CardInterpretation {
  card: string
  meaning: string
}

interface BlogPost {
  id: number
  title: string
  content: string
  category: string
  excerpt: string
  cards: string[]
  tags: string[]
  gradient: string
  emoji: string
  published_at: string
  view_count: number
  situation?: string
  interpretations?: CardInterpretation[]
  advice?: string
}

interface ParsedContent {
  situation?: string
  cards?: string[]
  interpretations?: string[]
  advice?: string
}

const route = useRoute()
const post = ref<BlogPost | null>(null)
const loading = ref(true)
const error = ref('')
const relatedPosts = ref<any[]>([])

const readingTime = computed(() => {
  if (!post.value) return 0
  const text = (post.value.situation || '') +
    (post.value.interpretations?.map((i: any) => i.meaning).join('') || '') +
    (post.value.advice || '')
  return Math.max(1, Math.ceil(text.length / 300))
})

const parsedContent = computed<ParsedContent>(() => {
  if (!post.value?.content) return {}

  const content = post.value.content
  const parsed: ParsedContent = {}

  if (post.value?.situation) {
    parsed.situation = post.value.situation
  }

  if (post.value?.cards && Array.isArray(post.value.cards) && post.value.cards.length > 0) {
    parsed.cards = post.value.cards
  }

  if (post.value?.interpretations && post.value.interpretations.length > 0) {
    parsed.interpretations = post.value.interpretations.map(interp => {
      return `<h3>${interp.card}</h3><p>${interp.meaning}</p>`
    })
  }

  if (post.value?.advice) {
    parsed.advice = post.value.advice
  }

  return parsed
})

const isParsed = computed(() => {
  return !!(parsedContent.value.situation || parsedContent.value.cards || parsedContent.value.interpretations || parsedContent.value.advice)
})

const fetchRelatedPosts = async () => {
  if (!post.value) return
  try {
    const res = await axios.get('/api/blog')
    relatedPosts.value = res.data.posts
      .filter((p: any) => p.id !== post.value!.id && p.category === post.value!.category)
      .slice(0, 3)
    // 같은 카테고리가 3개 미만이면 다른 카테고리에서 채움
    if (relatedPosts.value.length < 3) {
      const others = res.data.posts
        .filter((p: any) => p.id !== post.value!.id && p.category !== post.value!.category)
        .slice(0, 3 - relatedPosts.value.length)
      relatedPosts.value.push(...others)
    }
  } catch { /* silent */ }
}

const addJsonLd = () => {
  if (!post.value) return
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': post.value.title,
    'description': post.value.excerpt,
    'author': { '@type': 'Person', 'name': '세라피나', 'url': 'https://serapina.kr' },
    'publisher': { '@type': 'Organization', 'name': '세라피나 타로', 'url': 'https://serapina.kr' },
    'datePublished': post.value.published_at,
    'articleSection': post.value.category
  }
  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(jsonLd)
  document.head.appendChild(script)
}

onMounted(async () => {
  try {
    const postId = route.params.id
    const response = await axios.get(`/api/blog/${postId}`)
    post.value = response.data

    // SEO 메타
    if (post.value) {
      const categoryKeywords: { [key: string]: string } = {
        '연애': '연애운 타로, 사랑운 타로, 짝사랑 타로, 이별 타로, 복연 타로',
        '우정': '우정운 타로, 친구 관계 타로, 화해 타로',
        '진로': '진로운 타로, 진학 타로, 적성 타로, 직업 타로',
        '가족': '가족운 타로, 부모님 타로, 가족 갈등 타로',
        '학업': '학업운 타로, 시험운 타로, 성적 타로, 입시 타로, 수험생 타로',
        '학교': '학교생활 타로, 전학 타로, 동아리 타로',
        '자기계발': '자기계발 타로, 다이어트 타로, 목표 달성 타로'
      }

      const categoryKeyword = categoryKeywords[post.value.category] || '타로'
      const keywords = [
        ...post.value.tags,
        `${post.value.category} 타로`,
        categoryKeyword,
        '타로 해석',
        '타로 사례',
        '타로 상담',
        '세라피나 타로',
        '무료 타로'
      ].join(', ')

      useSeoMeta(
        `${post.value.title} | 세라피나 타로`,
        `${post.value.excerpt} [${post.value.category}] ${post.value.cards.join(', ')} 타로 카드 해석 사례`,
        keywords
      )

      addJsonLd()

      fetchRelatedPosts()
    }
  } catch (err: any) {
    console.error('Failed to fetch blog post:', err)
    error.value = err.response?.data?.detail || t('blog.post.loadError')
  } finally {
    loading.value = false
  }
})

const onCtaClick = (ctaName: string, location: string) => {
  trackCtaClick(ctaName, location)
  trackReadingStarted(`blog_${ctaName}`)
}

const sharePost = async () => {
  if (!post.value) return
  trackShareClicked('blog_post')
  const shareText = `${post.value.title}\n${post.value.excerpt}\n\nhttps://serapina.kr/blog/${post.value.id}`
  if (navigator.share) {
    try {
      await navigator.share({ title: post.value.title, text: shareText })
      trackShareCompleted('native')
    } catch { /* cancelled */ }
  } else {
    await copyPostLink()
  }
}

const copyPostLink = async () => {
  if (!post.value) return
  trackShareClicked('copy_link')
  try {
    await navigator.clipboard.writeText(`https://serapina.kr/blog/${post.value.id}`)
    alert(t('blog.post.linkCopied'))
    trackShareCompleted('copy')
  } catch { /* fallback */ }
}
</script>

<style scoped>
@import '@/assets/guide-pages.css';

.not-found {
  text-align: center;
  padding: 4rem 2rem;
}

.not-found-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
}

/* Section Divider */
.section-divider {
  position: relative;
  padding-bottom: 2.5rem;
  margin-bottom: 2rem;
}

.section-divider::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 1px;
  background: var(--border-color);
}

.section-divider:last-child {
  padding-bottom: 0;
  margin-bottom: 0;
}

.section-divider:last-child::after {
  display: none;
}

/* Cards Grid */
.cards-grid {
  display: flex !important;
  flex-direction: row !important;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 1rem;
  flex-wrap: nowrap !important;
}

.card-item {
  flex: 1 1 0 !important;
  min-width: 0;
  background: var(--button-hover-bg);
  padding: 0.75rem 0.5rem;
  border-radius: 10px;
  text-align: center;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.card-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px var(--shadow-purple);
}

.card-label {
  font-size: 0.65rem;
  margin-bottom: 0.3rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--primary-color);
}

.card-name {
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
  line-height: 1.3;
  color: var(--text-primary);
}

.card-position {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Interpretation Items */
.interpretation-item {
  background: var(--card-bg);
  padding: 1.25rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  line-height: 1.7;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.interpretation-item:last-child {
  margin-bottom: 0;
}

/* Advice Content */
.advice-content {
  background: var(--card-bg);
  padding: 1.25rem;
  border-radius: 12px;
  line-height: 1.7;
  color: var(--text-primary);
  font-size: 0.95rem;
  white-space: pre-wrap;
  border: 1px solid var(--border-color);
}

.advice-content :deep(p) {
  margin-bottom: 1.25rem;
  font-size: 0.95rem;
  line-height: 1.7;
}

.advice-content :deep(strong) {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  display: inline-block;
  margin-top: 1.25rem;
  margin-bottom: 0.6rem;
}

.advice-content :deep(ul),
.advice-content :deep(ol) {
  margin: 0.75rem 0 1.25rem 1.25rem;
  font-size: 0.95rem;
}

.advice-content :deep(li) {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

/* Remove italic from all text */
.interpretation-item :deep(em),
.interpretation-item :deep(i),
.advice-content :deep(em),
.advice-content :deep(i),
.post-content :deep(em),
.post-content :deep(i) {
  font-style: normal !important;
}

/* Post Content (Fallback) */
.post-content :deep(section) {
  position: relative;
  padding-bottom: 2.5rem;
  margin-bottom: 2rem;
}

.post-content :deep(section)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 1px;
  background: var(--border-color);
}

.post-content :deep(section:last-child) {
  padding-bottom: 0;
  margin-bottom: 0;
}

.post-content :deep(section:last-child)::after {
  display: none;
}

.post-content :deep(h2) {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 2rem 0 1rem;
  color: var(--text-primary);
}

.post-content :deep(h3) {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 1.5rem 0 0.75rem;
  color: var(--text-primary);
}

.post-content :deep(p) {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.post-content :deep(ul),
.post-content :deep(ol) {
  margin: 1rem 0 1.5rem 1.5rem;
  color: var(--text-primary);
}

.post-content :deep(li) {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.post-content :deep(strong) {
  font-weight: 700;
  color: var(--text-primary);
}

.post-content :deep(blockquote) {
  padding: 1rem 1.25rem;
  margin: 1.5rem 0;
  border-left: 3px solid var(--primary-color);
  background: var(--button-hover-bg);
  border-radius: 0 12px 12px 0;
  font-style: normal;
  color: var(--text-primary);
  line-height: 1.9;
  font-size: 0.95rem;
}

.post-content :deep(blockquote p) {
  margin-bottom: 1rem;
  font-size: 0.95rem;
  line-height: 1.9;
}

.post-content :deep(blockquote strong) {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  display: inline-block;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.post-content :deep(blockquote ul),
.post-content :deep(blockquote ol) {
  margin: 1rem 0 1.5rem 1.5rem;
  font-size: 0.95rem;
}

.post-content :deep(blockquote li) {
  margin-bottom: 0.75rem;
  line-height: 1.8;
}

/* Inline CTA - 보라 그라데이션 */
.inline-cta-card {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  text-align: center;
  border: none;
  box-shadow: 0 4px 20px rgba(91, 33, 182, 0.15);
}

.inline-cta-text {
  font-size: 0.95rem;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.inline-cta-btn {
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  background: #FFFFFF !important;
  color: var(--primary-color) !important;
}

/* Share Bar */
.share-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0;
  margin-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.share-bar-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary, #1A1A1A);
}

.share-bar-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Related Posts */
.related-posts {
  margin: 2rem 0;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.related-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.related-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.related-post-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  text-decoration: none;
  transition: all 0.2s;
}

.related-post-card:hover {
  border-color: var(--border-color);
  background: var(--card-bg);
}

.related-emoji {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.related-post-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.related-post-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.related-post-category {
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: 500;
}

/* Advisor Profile */
.advisor-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  margin-bottom: 0.5rem;
}

.advisor-avatar {
  font-size: 2rem;
}

.advisor-info {
  display: flex;
  flex-direction: column;
}

.advisor-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.advisor-title {
  font-size: 0.75rem;
  color: var(--primary-color);
  font-weight: 500;
}

/* Empathy CTA - 보라 그라데이션 */
.empathy-cta {
  text-align: center;
  padding: 1.5rem;
  margin: 1.5rem 0;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(91, 33, 182, 0.15);
}

.empathy-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.empathy-btn {
  color: var(--primary-color) !important;
  font-weight: 600;
}

@media (max-width: 768px) {
  .cards-grid {
    flex-direction: column;
    gap: 0.75rem;
  }

  .card-item {
    padding: 0.75rem 0.5rem;
  }

  .share-bar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
