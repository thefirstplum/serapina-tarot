<template>
  <div class="app-main">
      <div class="page-layout">
        <!-- Header -->
        <div class="page-header">
          <div class="header-content">
            <v-btn
              icon
              variant="flat"
              :to="{ name: 'guides' }"
              class="back-button"
            >
              <v-icon color="var(--primary-color)" size="28">mdi-arrow-left</v-icon>
            </v-btn>
            <div class="header-text">
              <h1 class="page-title">{{ t('guides.study.detailPage.title') }}</h1>
              <p class="page-subtitle">{{ t('guides.study.detailPage.subtitle') }}</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="page-content">
          <div class="content-container">
            <div class="content-layout">
              <!-- Main Content -->
              <div class="main-content">
                <div class="info-card">
                  <h2 class="section-title">학업운세, 타로로 이렇게 봐!</h2>
                  <p class="section-text">
                    시험? 성적? 입시? 공부 고민이 있다면, 세라피나가 타로로 읽어줄게!
                  </p>
                  <p class="section-text">
                    같은 질문이라도 네 상황에 따라 카드 해석이 완전히 달라져. 그래서 AI가 맥락을 파악해서 너만을 위한 해석을 해주는 거야!
                  </p>
                </div>

                <div class="info-card">
                  <h2 class="section-title">시험운 & 성적 보는 법</h2>
                  <h3 class="subsection-title">🎯 이런 고민이라면 바로 물어봐!</h3>
                  <ul class="section-list clickable-list">
                    <li @click="startReading('다음 주 중간고사 잘 볼 수 있을까?')">
                      "다음 주 중간고사 잘 볼 수 있을까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('이번 학기 성적이 오를 수 있을까?')">
                      "이번 학기 성적 오를까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('수능 결과가 어떻게 나올까?')">
                      "수능 결과가 어떻게 나올까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('시험 준비를 어디에 집중해야 할까?')">
                      "시험 준비 어디에 집중해야 해?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                  </ul>

                  <div class="card-hint-box">
                    <p class="card-hint-text">
                      💡 같은 카드라도 네 상황에 따라 해석이 완전히 달라! 세라피나가 너의 맥락에 맞춰 정확하게 읽어줄게.
                    </p>
                  </div>
                </div>

                <!-- 인라인 CTA: 2번째 섹션 뒤에 삽입 -->
                <div class="inline-cta-card">
                  <p class="inline-cta-emoji">✨</p>
                  <p class="inline-cta-text">질문법은 충분히 알았지?<br/>이제 직접 물어볼 차례!</p>
                  <v-btn
                    color="var(--primary-color)"
                    variant="flat"
                    rounded="pill"
                    size="large"
                    :to="{ name: 'reading' }"
                    class="inline-cta-btn"
                    @click="trackCtaClick('inline_cta', 'guide_study')"
                  >
                    <v-icon start>mdi-cards-playing-outline</v-icon>
                    세라피나한테 물어보기
                  </v-btn>
                </div>

                <div class="info-card">
                  <h2 class="section-title">공부 집중력 & 학습법</h2>
                  <h3 class="subsection-title">🎯 이런 고민이라면 바로 물어봐!</h3>
                  <ul class="section-list clickable-list">
                    <li @click="startReading('요즘 공부에 집중이 안 돼... 어떻게 하면 돼?')">
                      "요즘 공부에 집중이 안 돼..."
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('이 과목 공부법 뭐가 좋을까?')">
                      "이 과목 공부법 뭐가 좋을까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('독서실 vs 도서관 vs 집, 어디서 공부하는 게 좋을까?')">
                      "독서실 vs 도서관 vs 집, 어디가 좋아?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('스터디 그룹을 만드는 게 좋을까?')">
                      "스터디 그룹 만들까 말까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                  </ul>

                  <div class="card-hint-box">
                    <p class="card-hint-text">
                      💡 공부는 자기에게 맞는 스타일을 찾는 게 제일 중요해! 세라피나가 너만의 학습법을 찾아줄게.
                    </p>
                  </div>
                </div>

                <div class="info-card">
                  <h2 class="section-title">입시 & 진로 선택</h2>
                  <h3 class="subsection-title">🎯 이런 고민이라면 바로 물어봐!</h3>
                  <ul class="section-list clickable-list">
                    <li @click="startReading('A대학 vs B대학, 어디로 가는 게 좋을까?')">
                      "A대학 vs B대학, 어디로 갈까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('이 학과가 나한테 맞을까?')">
                      "이 학과 나랑 맞을까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('수시 vs 정시, 뭐가 더 유리할까?')">
                      "수시 vs 정시, 뭐가 더 유리해?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                    <li @click="startReading('재수를 해야 할까 말아야 할까?')">
                      "재수할까 말까?"
                      <span class="try-badge">이 질문으로 리딩 →</span>
                    </li>
                  </ul>

                  <div class="alert-box warning">
                    <strong>참고:</strong> 진로는 신중하게! 타로는 가능성을 보여주지만, 최종 결정은 너의 꿈과 적성을 고려해야 해.
                  </div>
                </div>

                <div class="info-card">
                  <h2 class="section-title">상황별 이렇게 물어봐!</h2>

                  <div class="action-guide">
                    <h4 class="action-title">🌟 시험 불안할 때</h4>
                    <p class="action-text">→ "시험이 너무 불안한데 잘 볼 수 있을까?" 라고 물어봐!</p>
                    <v-btn variant="text" color="var(--primary-color)" size="small" @click="startReading('시험이 너무 불안한데 잘 볼 수 있을까?')">
                      바로 물어보기 →
                    </v-btn>
                  </div>

                  <div class="action-guide">
                    <h4 class="action-title">⏳ 슬럼프가 왔을 때</h4>
                    <p class="action-text">→ "공부 슬럼프에서 빠져나오려면 어떻게 해야 할까?" 라고 물어봐!</p>
                    <v-btn variant="text" color="var(--primary-color)" size="small" @click="startReading('공부 슬럼프에서 빠져나오려면 어떻게 해야 할까?')">
                      바로 물어보기 →
                    </v-btn>
                  </div>

                  <div class="action-guide">
                    <h4 class="action-title">💬 학원/과외 고민될 때</h4>
                    <p class="action-text">→ "이 학원 다니는 게 효과 있을까?" 라고 물어봐!</p>
                    <v-btn variant="text" color="var(--primary-color)" size="small" @click="startReading('이 학원 다니는 게 효과 있을까?')">
                      바로 물어보기 →
                    </v-btn>
                  </div>
                </div>
              </div>

              <!-- Sidebar -->
              <div class="sidebar">
                <div class="sidebar-card keywords">
                  <h3 class="sidebar-title">{{ t('guides.study.detailPage.keywordsTitle') }}</h3>
                  <div class="keywords-grid">
                    <span class="keyword-chip">시험</span>
                    <span class="keyword-chip">성적</span>
                    <span class="keyword-chip">수능</span>
                    <span class="keyword-chip">입시</span>
                    <span class="keyword-chip">공부법</span>
                    <span class="keyword-chip">집중력</span>
                    <span class="keyword-chip">진로</span>
                    <span class="keyword-chip">학원</span>
                    <span class="keyword-chip">과외</span>
                    <span class="keyword-chip">학교생활</span>
                  </div>
                </div>

                <div class="sidebar-card cta">
                  <h3 class="sidebar-title">{{ t('guides.study.detailPage.ctaTitle') }}</h3>
                  <p class="sidebar-text">{{ t('guides.study.detailPage.ctaText') }}</p>
                  <v-btn
                    block
                    color="white"
                    variant="elevated"
                    :to="{ name: 'reading' }"
                    class="sidebar-button"
                    @click="trackCtaClick('sidebar_cta', 'guide_study')"
                  >
                    {{ t('guides.common.startButton') }}
                  </v-btn>
                </div>

                <div class="sidebar-card faq">
                  <h3 class="sidebar-title">자주 묻는 질문</h3>
                  <div class="faq-item">
                    <h4 class="faq-question">Q. 같은 질문 계속 해도 돼?</h4>
                    <p class="faq-answer">1-2주 간격 두는 게 좋아. 상황 안 바뀌면 같은 답 나올 거야.</p>
                  </div>
                  <div class="faq-item">
                    <h4 class="faq-question">Q. 역방향은 나쁜 거야?</h4>
                    <p class="faq-answer">꼭 그렇진 않아. 에너지가 약하거나 다른 관점일 수 있어.</p>
                  </div>
                  <div class="faq-item">
                    <h4 class="faq-question">Q. 타로가 미래 정확히 예측해?</h4>
                    <p class="faq-answer">현재 흐름 보고 가능성 알려줘. 네 선택과 행동으로 미래는 바뀔 수 있어!</p>
                  </div>
                </div>

                <!-- 크로스 가이드 링크 -->
                <div class="sidebar-card">
                  <h3 class="sidebar-title">다른 고민도 있어?</h3>
                  <div class="cross-guide-links">
                    <router-link :to="{ name: 'guide-love' }" class="cross-guide-chip">💕 연애운 가이드</router-link>
                    <router-link :to="{ name: 'guide-career' }" class="cross-guide-chip">💼 직업운 가이드</router-link>
                    <router-link :to="{ name: 'guide-money' }" class="cross-guide-chip">💰 금전운 가이드</router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Blog Section -->
            <div class="blog-section" v-if="studyPosts.length > 0">
              <h2 class="blog-section-title">{{ t('guides.study.detailPage.blogTitle') }}</h2>
              <p class="blog-section-desc">{{ t('guides.study.detailPage.blogSubtitle') }}</p>
              <div class="blog-grid">
                <div
                  v-for="post in studyPosts"
                  :key="post.id"
                  class="blog-card"
                  @click="$router.push(`/blog/${post.id}`)"
                >
                  <div class="blog-emoji">{{ post.emoji }}</div>
                  <h3 class="blog-card-title">{{ post.title }}</h3>
                  <p class="blog-card-excerpt">{{ post.excerpt }}</p>
                  <div class="blog-card-link">{{ t('guides.common.readMore') }}</div>
                </div>
              </div>
            </div>

            <!-- CTA Section -->
            <div class="cta-section">
              <div class="cta-card">
                <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" style="object-fit: contain; display: block; margin: 0 auto 12px;" />
                <h3>{{ t('guides.study.detailPage.readingCta') }}</h3>
                <p>{{ t('guides.study.detailPage.readingCtaDesc') }}</p>
                <v-btn
                  size="large"
                  color="white"
                  variant="elevated"
                  :to="{ name: 'reading' }"
                  class="cta-button"
                  @click="trackCtaClick('bottom_cta', 'guide_study')"
                >
                  {{ t('guides.common.readingButton') }}
                </v-btn>
              </div>
            </div>
          </div>
        </div>

        <!-- 모바일 플로팅 CTA -->
        <Teleport to="body">
          <Transition name="slide-up">
            <div v-if="showFloatingCta" class="floating-cta">
              <v-btn
                color="var(--primary-color)"
                variant="flat"
                rounded="pill"
                block
                size="large"
                :to="{ name: 'reading' }"
                class="floating-cta-btn"
                @click="trackCtaClick('floating_cta', 'guide_study')"
              >
                <v-icon start>mdi-cards-playing-outline</v-icon>
                학업운 고민 바로 물어보기
              </v-btn>
            </div>
          </Transition>
        </Teleport>

        <!-- AdBanner Component -->
        <AdSenseBlock slot="1696071761" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
import AdBanner from '@/components/AdBanner.vue'
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { trackCtaClick, trackReadingStarted } from '@/utils/analytics'

const studyPosts = ref<any[]>([])
const showFloatingCta = ref(false)

const startReading = (question: string) => {
  trackReadingStarted('guide_study_question')
  router.push({ name: 'reading', query: { q: question } })
}

const handleScroll = () => {
  showFloatingCta.value = window.scrollY > 400 && window.innerWidth <= 960
}

const fetchStudyPosts = async () => {
  try {
    const response = await axios.get('/api/blog')
    studyPosts.value = response.data.posts
      .filter((post: any) => post.category === '학업')
      .slice(0, 2)
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
  }
}

onMounted(() => {
  fetchStudyPosts()
  window.addEventListener('scroll', handleScroll)

  // FAQ Schema JSON-LD
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': [
      {
        '@type': 'Question',
        'name': '타로로 학업운을 어떻게 보나요?',
        'acceptedAnswer': {
          '@type': 'Answer',
          'text': '시험, 성적, 입시, 공부법 등 구체적인 상황을 질문하면 타로 AI 상담사가 78장 카드 중 뽑힌 카드를 상황에 맞게 해석해줍니다.'
        }
      },
      {
        '@type': 'Question',
        'name': '같은 타로 질문을 계속 해도 되나요?',
        'acceptedAnswer': {
          '@type': 'Answer',
          'text': '1-2주 간격을 두는 것이 좋습니다. 상황이 바뀌지 않으면 비슷한 결과가 나올 수 있어요.'
        }
      },
      {
        '@type': 'Question',
        'name': '역방향 카드는 나쁜 의미인가요?',
        'acceptedAnswer': {
          '@type': 'Answer',
          'text': '꼭 그렇지 않습니다. 에너지가 약하거나 다른 관점을 제시하는 것일 수 있어요. AI가 상황에 맞게 정확히 해석해드립니다.'
        }
      }
    ]
  }
  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(jsonLd)
  document.head.appendChild(script)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

useSeoMeta(
  '학업운세 타로 가이드 - 시험, 성적, 입시, 공부법 | 세라피나 타로',
  '시험, 성적, 수능, 입시, 중간고사, 기말고사, 모의고사 등 학업과 관련된 타로 리딩 방법과 해석을 상세하게 안내합니다. 내신 관리, 수시 정시 선택, 재수 결정, 학원 선택, 공부 집중력, 진로 고민까지 다양한 학업 상황별 타로 해석법을 알려드립니다.',
  '학업운세, 타로, 시험, 시험운, 성적, 수능, 입시, 중간고사, 기말고사, 모의고사, 내신, 수시, 정시, 재수, 진로, 공부법, 집중력, 학원, 학업 타로, 성적 향상'
)
</script>

<style scoped>
@import '@/assets/guide-pages.css';

/* 클릭 가능한 질문 리스트 */
.clickable-list li {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 8px;
  padding: 0.6rem 1rem 0.6rem 1.2rem !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.clickable-list li:hover {
  background: var(--button-hover-bg);
  color: var(--primary-color);
}

.try-badge {
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--primary-color);
  opacity: 0;
  transition: opacity 0.2s;
  white-space: nowrap;
}

.clickable-list li:hover .try-badge {
  opacity: 1;
}

/* 카드 힌트 박스 */
.card-hint-box {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: var(--button-hover-bg);
  border-radius: 12px;
  border-left: 3px solid var(--primary-color);
}

.card-hint-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* 인라인 CTA - 보라 그라데이션 */
.inline-cta-card {
  text-align: center;
  padding: 2rem 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-color) 100%);
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(91, 33, 182, 0.15);
}

.inline-cta-emoji {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.inline-cta-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.inline-cta-btn {
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  background: #FFFFFF !important;
  color: var(--primary-color) !important;
}

/* 액션 가이드 개선 */
.action-guide {
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.action-guide:last-child {
  border-bottom: none;
}

.action-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.4rem 0;
}

.action-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 0.4rem 0;
  line-height: 1.5;
}

/* 크로스 가이드 링크 */
.cross-guide-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cross-guide-chip {
  display: block;
  padding: 0.6rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--primary-color);
  background: var(--button-hover-bg);
  text-decoration: none;
  transition: all 0.2s;
}

.cross-guide-chip:hover {
  background: var(--button-hover-bg);
}

/* 모바일 플로팅 CTA */
.floating-cta {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px 20px;
  background: linear-gradient(transparent, rgba(13,10,26,0.95) 30%);
  z-index: 999;
}

.floating-cta-btn {
  font-weight: 700;
  text-transform: none;
  letter-spacing: 0;
  box-shadow: 0 4px 20px var(--shadow-purple) !important;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (min-width: 961px) {
  .floating-cta {
    display: none;
  }
}
</style>
