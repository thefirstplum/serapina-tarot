<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              to="/"
              icon
              variant="flat"
              class="back-button"
            >
              <v-icon color="var(--primary-color)">mdi-home</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('blog.list.title') }}</h1>
              <p class="page-subtitle">{{ t('blog.list.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Category Filter -->
        <div class="filter-bar" v-if="categories.length > 0">
          <div class="filter-container">
            <button
              v-for="cat in categories"
              :key="cat"
              class="filter-chip"
              :class="{ active: activeCategory === cat }"
              @click="activeCategory = cat"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <!-- Blog Posts Grid -->
        <div class="page-content">
          <div class="content-container">
            <div class="blog-grid" v-if="filteredPosts.length > 0">
              <div
                v-for="post in filteredPosts"
                :key="post.id"
                class="blog-card"
                @click="$router.push(`/blog/${post.id}`)"
              >
                <div class="blog-card-top">
                  <div class="blog-emoji">{{ post.emoji }}</div>
                  <span class="blog-category-badge">{{ post.category }}</span>
                </div>
                <h3 class="blog-card-title">{{ post.title }}</h3>
                <p class="blog-card-excerpt">{{ post.excerpt }}</p>
                <div class="blog-card-footer">
                  <span class="blog-card-date">{{ formatDate(post.published_at) }}</span>
                  <span class="blog-card-link">{{ t('blog.list.readMore') }}</span>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              <p>{{ t('blog.list.noPosts') || '아직 작성된 글이 없어.' }}</p>
            </div>

            <!-- CTA -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ t('blog.list.ctaTitle') || '타로로 궁금한 거 물어보기' }}</h3>
                <p>{{ t('blog.list.ctaDesc') || '블로그에서 본 내용 바탕으로 직접 타로 리딩 받아봐.' }}</p>
                <v-btn
                  size="large"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'blog_list')"
                >
                  {{ t('guides.common.readingButton') }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- 하단 광고 -->
        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { trackCtaClick } from '@/utils/analytics'
import AdSenseBlock from '@/components/AdSenseBlock.vue'

const { t } = useI18n()
import { useSeoMeta } from '@/composables/useSeoMeta'
import axios from 'axios'

interface BlogPost {
  id: number
  title: string
  excerpt: string
  emoji: string
  category: string
  published_at: string
}

const blogPosts = ref<BlogPost[]>([])
const activeCategory = ref('전체')

const categories = computed(() => {
  if (blogPosts.value.length === 0) return []
  const cats = [...new Set(blogPosts.value.map(p => p.category))]
  return ['전체', ...cats]
})

const filteredPosts = computed(() => {
  if (activeCategory.value === '전체') return blogPosts.value
  return blogPosts.value.filter(p => p.category === activeCategory.value)
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

const fetchBlogPosts = async () => {
  try {
    const response = await axios.get('/api/blog')
    blogPosts.value = response.data.posts
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
  }
}

onMounted(() => {
  fetchBlogPosts()
})

useSeoMeta(
  t('seo.blog.listTitle'),
  t('seo.blog.listDescription'),
  t('seo.blog.listKeywords')
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* Filter Bar */
.filter-bar {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  padding: 0.75rem 1rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.filter-bar::-webkit-scrollbar {
  display: none;
}

.filter-container {
  display: flex;
  gap: 0.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-chip {
  flex-shrink: 0;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  border-color: var(--border-color);
  color: var(--primary-color);
}

.filter-chip.active {
  background: var(--primary-color);
  color: var(--text-primary);
  border-color: var(--primary-color);
}

/* Blog Grid - override guide-pages defaults */
.blog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.blog-card {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 1.75rem 1.25rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.blog-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--shadow-purple);
  border-color: var(--border-color);
}

.blog-card-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.blog-emoji {
  font-size: 2rem;
}

.blog-category-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  background: var(--button-hover-bg);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
}

.blog-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.blog-card-excerpt {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.blog-card-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.blog-card-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary-color);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
  font-size: 1rem;
}

@media (max-width: 768px) {
  .blog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
