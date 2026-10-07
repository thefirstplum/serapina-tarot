<template>
  <div class="landing-main">
      <!-- Hero Section with Gradient Background -->
      <section class="hero-section">
        <div class="hero-bg-elements">
          <div class="hero-orb orb-1"></div>
          <div class="hero-orb orb-2"></div>
          <div class="hero-orb orb-3"></div>
        </div>
        <!-- Star particles -->
        <div class="stars-container">
          <div v-for="n in 30" :key="'star-'+n" class="star" :style="starStyle(n)"></div>
        </div>

        <!-- Header (over hero) -->
        <header class="landing-header">
          <div class="header-content">
            <div class="header-left" @click="goToPage('/')" style="cursor: pointer;">
              <img src="/icons/symbol-64.png" class="header-logo" alt="세라피나" width="32" height="32" />
              <h1 class="app-title">{{ t('landing.header.appTitle') }}</h1>
            </div>
            <div class="header-actions">
              <v-btn icon variant="text" @click="goToPage('/cards')" :title="t('landing.header.cardsTitle')" class="header-icon-btn desktop-only">
                <v-icon>mdi-cards-outline</v-icon>
              </v-btn>
              <v-btn icon variant="text" @click="goToPage('/guides')" :title="t('landing.header.guidesTitle')" class="header-icon-btn desktop-only">
                <v-icon>mdi-book-open-variant</v-icon>
              </v-btn>
              <v-btn icon variant="text" @click="goToPage('/blog')" :title="t('landing.header.blogTitle')" class="header-icon-btn desktop-only">
                <v-icon>mdi-post-outline</v-icon>
              </v-btn>
              <v-btn icon variant="text" @click="mobileMenuOpen = !mobileMenuOpen" class="header-icon-btn mobile-only">
                <v-icon>{{ mobileMenuOpen ? 'mdi-close' : 'mdi-menu' }}</v-icon>
              </v-btn>
            </div>
            <!-- Mobile Menu -->
            <transition name="menu-slide">
              <div v-if="mobileMenuOpen" class="mobile-menu">
                <a class="mobile-menu-item" @click="goToPage('/cards'); mobileMenuOpen = false">
                  <v-icon size="20">mdi-cards-outline</v-icon>
                  {{ t('landing.header.cardsTitle') }}
                </a>
                <a class="mobile-menu-item" @click="goToPage('/guides'); mobileMenuOpen = false">
                  <v-icon size="20">mdi-book-open-variant</v-icon>
                  {{ t('landing.header.guidesTitle') }}
                </a>
                <a class="mobile-menu-item" @click="goToPage('/blog'); mobileMenuOpen = false">
                  <v-icon size="20">mdi-post-outline</v-icon>
                  {{ t('landing.header.blogTitle') }}
                </a>
                <a class="mobile-menu-item" @click="goToPage('/reading'); mobileMenuOpen = false">
                  <v-icon size="20">mdi-cards-playing-outline</v-icon>
                  {{ t('landing.hero.cta') }}
                </a>
              </div>
            </transition>
          </div>
        </header>

        <!-- Hero Content -->
        <div class="hero-content">
          <p class="hero-badge">{{ t('landing.hero.badge') }}</p>
          <h2 class="hero-title" v-html="t('landing.hero.title').replace(/\n/g, '<br>')"></h2>
          <p class="hero-desc" v-html="`${t('landing.hero.desc1')}<br>${t('landing.hero.desc2').replace(/\n/g, '<br>')}`"></p>

          <!-- Question Input (Glass Card) -->
          <div class="hero-input-card">
            <p class="input-card-label">{{ t('landing.hero.inputLabel') }}</p>
            <v-text-field
              v-model="questionInput"
              :placeholder="HERO_INPUT_PLACEHOLDER"
              variant="solo"
              density="comfortable"
              hide-details
              class="question-input"
              append-inner-icon="mdi-arrow-right-circle"
              @click:append-inner="startWithQuestion"
              @keyup.enter="startWithQuestion"
            ></v-text-field>
            <div class="quick-questions">
              <button
                v-for="(question, index) in QUICK_QUESTIONS"
                :key="index"
                class="quick-q-chip"
                @click="startWithQuickQuestion(question)"
              >
                {{ question }}
              </button>
            </div>
          </div>

          <!-- 질문 없이 바로 시작 -->
          <v-btn
            variant="text"
            size="small"
            rounded="pill"
            class="hero-cta-sub"
            @click="onHeroCtaClick"
          >
            <span>{{ t('landing.hero.cta') }}</span>
            <v-icon end size="16">mdi-arrow-right</v-icon>
          </v-btn>

          <!-- 메인 일러스트 -->
          <div class="hero-illustration">
            <img src="/landing-illustration.png" alt="세라피나 — 친구처럼 듣는 타로 AI" />
          </div>
        </div>

        <!-- Social Proof -->
        <div class="social-proof-bar">
          <div class="proof-item">
            <span class="proof-number">{{ t('landing.socialProof.readings') }}</span>
            <span class="proof-label">{{ t('landing.socialProof.readingsLabel') }}</span>
          </div>
          <div class="proof-divider"></div>
          <div class="proof-item">
            <span class="proof-number">{{ t('landing.socialProof.satisfaction') }}</span>
            <span class="proof-label">{{ t('landing.socialProof.satisfactionLabel') }}</span>
          </div>
          <div class="proof-divider"></div>
          <div class="proof-item">
            <span class="proof-number">{{ t('landing.socialProof.available') }}</span>
            <span class="proof-label">{{ t('landing.socialProof.availableLabel') }}</span>
          </div>
        </div>

        <!-- Category Pills (over hero bottom) -->
        <div class="category-bar">
          <div class="category-pill" v-for="cat in categories" :key="cat.key" @click="goToReading(cat.key)">
            <span class="cat-emoji">{{ cat.emoji }}</span>
            <span class="cat-label">{{ cat.label }}</span>
          </div>
        </div>

        <!-- Hero Wave Divider -->
        <div class="hero-wave">
          <svg viewBox="0 0 1440 120" preserveAspectRatio="none">
            <path d="M0,60 C360,120 720,0 1080,60 C1260,90 1380,80 1440,70 L1440,120 L0,120 Z" fill="var(--bg-secondary)"/>
          </svg>
        </div>
      </section>

      <!-- Today's Card Section - Dark Mystical -->
      <section class="today-section" ref="todaySectionRef">
        <div class="section-stars">
          <div v-for="n in 15" :key="'ts-'+n" class="mini-star" :style="miniStarStyle(n)"></div>
        </div>
        <div class="today-inner animate-on-scroll" @click="goToPage(`/cards/${todayCard.id}`)" style="cursor: pointer;">
          <div class="today-card-visual">
            <div class="card-glow"></div>
            <div class="card-sparkles">
              <div v-for="n in 6" :key="'sp-'+n" class="sparkle" :style="sparkleStyle(n)"></div>
            </div>
            <img
              :src="todayCard.imagePath"
              :alt="todayCard.name"
              class="today-card-img"
            />
          </div>
          <div class="today-card-info">
            <span class="today-label">{{ t('landing.todayCard.label') }}</span>
            <h3 class="today-name">{{ todayCard.name }}</h3>
            <p class="today-subtitle">{{ todayCard.subtitle }}</p>
            <p class="today-meaning">{{ todayCard.meaning }}</p>
            <div class="today-keywords">
              <span v-for="(kw, i) in todayCard.keywords" :key="i" class="kw-chip">{{ kw }}</span>
            </div>
            <div class="today-actions">
              <button class="daily-fortune-btn" @click.stop="startDailyFortune">
                ✨ 오늘의 운세 보기
              </button>
              <button class="share-btn" @click.stop="shareTodayCard">
                <v-icon size="16">mdi-share-variant</v-icon>
                {{ t('landing.todayCard.shareBtn') }}
              </button>
              <span class="today-detail-link">이 카드 알아보기 →</span>
            </div>
          </div>
        </div>
        <!-- Section divider -->
        <div class="mystical-divider">
          <span class="divider-star">✦</span>
          <div class="divider-line"></div>
          <span class="divider-star">✦</span>
        </div>
      </section>

      <!-- Chat Preview Section -->
      <section class="chat-preview-section">
        <div class="chat-preview-inner">
          <div class="chat-section-label">★ 매일 밤 오가는 대화</div>
          <h3 class="chat-section-title">
            이런 대화가<br>
            매일 밤 <span class="yellow-highlight">오가</span>
          </h3>
          <div class="chat-preview-box">
            <div class="chat-bubble chat-user">{{ randomScenario.userMsg }}</div>
            <div class="chat-bubble chat-bot">{{ randomScenario.botMsg1 }}</div>
            <div class="chat-bubble-card">
              <img :src="randomScenario.cardImg" :alt="randomScenario.cardName" class="chat-card-img" />
              <div class="chat-card-meta">
                <div class="chat-card-name">{{ randomScenario.cardName }}</div>
                <div class="chat-card-en">{{ randomScenario.cardSub }}</div>
              </div>
            </div>
            <div class="chat-bubble chat-bot" v-html="randomScenario.botMsg2"></div>
          </div>
        </div>
      </section>

      <!-- Popular Problems -->
      <section class="popular-section">
        <h3 class="sec-title animate-on-scroll">{{ t('landing.popular.title') }} <span class="title-accent">💫</span></h3>
        <div v-if="loadingPopular" class="loading-container">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
        <div v-else-if="popularPosts.length > 0" class="popular-grid">
          <div
            v-for="(post, idx) in visiblePopularPosts"
            :key="post.id"
            class="popular-card animate-on-scroll"
            :class="`popular-accent-${idx % 3}`"
            :style="{ transitionDelay: `${idx * 0.1}s` }"
            @click="goToPage(`/blog/${post.id}`)"
          >
            <div class="pop-emoji">{{ post.emoji }}</div>
            <span class="pop-category">{{ post.category }}</span>
            <h4 class="pop-title">{{ post.title }}</h4>
            <div class="pop-views">
              <v-icon size="14">mdi-eye</v-icon>
              {{ t('landing.popular.views', { count: post.view_count }) }}
            </div>
          </div>
        </div>
      </section>

      <!-- Mystical Divider -->
      <div class="section-break">
        <div class="break-ornament">
          <span class="ornament-dot"></span>
          <span class="ornament-line"></span>
          <span class="ornament-symbol">☽</span>
          <span class="ornament-line"></span>
          <span class="ornament-dot"></span>
        </div>
      </div>

      <!-- Topics with gradient cards -->
      <section class="topics-section">
        <h3 class="sec-title animate-on-scroll">{{ t('landing.topics.title') }}</h3>
        <div class="topics-grid">
          <div class="topic-card topic-love animate-on-scroll" style="transition-delay: 0s" @click="goToGuide('love')">
            <div class="topic-glow"></div>
            <span class="topic-icon">💝</span>
            <span class="topic-name">{{ t('landing.topics.love.name') }}</span>
            <span class="topic-desc">{{ t('landing.topics.love.desc') }}</span>
          </div>
          <div class="topic-card topic-career animate-on-scroll" style="transition-delay: 0.1s" @click="goToGuide('career')">
            <div class="topic-glow"></div>
            <span class="topic-icon">🎯</span>
            <span class="topic-name">{{ t('landing.topics.career.name') }}</span>
            <span class="topic-desc">{{ t('landing.topics.career.desc') }}</span>
          </div>
          <div class="topic-card topic-study animate-on-scroll" style="transition-delay: 0.2s" @click="goToGuide('study')">
            <div class="topic-glow"></div>
            <span class="topic-icon">✨</span>
            <span class="topic-name">{{ t('landing.topics.study.name') }}</span>
            <span class="topic-desc">{{ t('landing.topics.study.desc') }}</span>
          </div>
          <div class="topic-card topic-money animate-on-scroll" style="transition-delay: 0.3s" @click="goToGuide('money')">
            <div class="topic-glow"></div>
            <span class="topic-icon">🌟</span>
            <span class="topic-name">{{ t('landing.topics.money.name') }}</span>
            <span class="topic-desc">{{ t('landing.topics.money.desc') }}</span>
          </div>
        </div>
      </section>

      <!-- Instagram Section -->
      <section class="insta-section">
        <div class="insta-inner">
          <a href="https://instagram.com/serapina_tarot" target="_blank" rel="noopener" class="insta-card">
            <div class="insta-text">
              <h4>매일 밤, 네 MBTI에 한 장</h4>
              <p>오늘의 카드와 짧은 한 줄. 자기 전 5분만.</p>
            </div>
            <span class="insta-handle">@serapina_tarot →</span>
          </a>
        </div>
      </section>

      <!-- Mobile Floating CTA -->
      <transition name="slide-up">
        <div v-if="showFloatingCta" class="floating-cta">
          <v-btn
            color="primary"
            size="large"
            rounded="pill"
            block
            class="floating-cta-btn"
            @click="onFloatingCtaClick"
          >
            <v-icon start>mdi-cards-playing-outline</v-icon>
            {{ t('landing.hero.cta') }}
          </v-btn>
        </div>
      </transition>

      <footer class="landing-footer">
        <div class="footer-links">
          <a @click="goToPage('/privacy')">{{ t('landing.footer.privacy') }}</a>
          <span class="footer-dot">·</span>
          <a @click="goToPage('/terms')">{{ t('landing.footer.terms') }}</a>
        </div>
        <p class="footer-copy">{{ t('landing.footer.copyright') }}</p>
      </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted, ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { cardDatabase } from '@/data/cardDatabase'
import { trackReadingStarted, trackCtaClick } from '@/utils/analytics'

const router = useRouter()
const { t } = useI18n()

const windowWidth = ref(window.innerWidth)
const onResize = () => { windowWidth.value = window.innerWidth }

const gridCols = computed(() => {
  if (windowWidth.value <= 960) return 2
  return 3
})

const HERO_INPUT_PLACEHOLDER = computed(() => t('landing.hero.placeholder'))
const ALL_QUICK_QUESTIONS = [
  '좋아하는 사람이 날 어떻게 생각할까?',
  '썸남이 나한테 진심일까?',
  '이번 시험 잘 볼 수 있을까?',
  '친구랑 사이가 멀어진 것 같아',
  '내 진로가 맞는 방향일까?',
  '요즘 자꾸 우울해',
  '새로운 연애 언제쯤 시작될까?',
  '내 진로, 이대로 괜찮을까?',
  '가족관계가 힘들어',
  '재물운이 풀릴까?',
  '헤어진 사람이 자꾸 생각나',
  '내년 운세가 궁금해'
]

const getRandomQuestions = () => {
  const shuffled = [...ALL_QUICK_QUESTIONS].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, 3)
}

const QUICK_QUESTIONS = ref(getRandomQuestions())

const getCardImageUrl = (cardId: string) => {
  return new URL(`../assets/cards/${cardId}.jpg`, import.meta.url).href
}

const CHAT_SCENARIOS = [
  {
    userMsg: '남친이랑 또 싸웠어... 나만 잘못한 걸까 ㅠ',
    botMsg1: '음, 일단 카드 한 장 뽑아볼래?',
    cardId: 'maj18',
    cardName: '달',
    cardSub: '머릿속 복잡한 너에게',
    botMsg2: '달이네. 머릿속 복잡한 거 알아.<br>답 강제로 찾지 마. 흐릿한 채로 둬봐.'
  },
  {
    userMsg: '회사 그만두고 싶은데 진짜 그래도 될까?',
    botMsg1: '결정 무거운 거 알아. 카드부터 뽑자.',
    cardId: 'maj00',
    cardName: '바보',
    cardSub: '한 발 떼는 너에게',
    botMsg2: '바보네. 무모해 보여도 그게 너의 시작이야.<br>계획 없어도 괜찮아. 직감이 이미 알고 있잖아.'
  },
  {
    userMsg: '친구들 다 잘 사는데 나만 뒤처진 것 같아',
    botMsg1: '그 마음 알아. 같이 카드 펴보자.',
    cardId: 'maj09',
    cardName: '은둔자',
    cardSub: '지금 멈춰 있는 너에게',
    botMsg2: '은둔자야. 잠깐 멈춘 게 아니라 너만의 속도지.<br>남들 보지 마. 너의 걸음으로 가도 돼.'
  },
  {
    userMsg: '주식 -30% 손절해야 할까...',
    botMsg1: '잃은 거 떠올리는 거 힘들지. 카드 뽑자.',
    cardId: 'pents05',
    cardName: '펜타클 5',
    cardSub: '막막한 너에게',
    botMsg2: '잃은 것만 보고 있지?<br>도움 받는 거 약점 아니야. 그게 회복의 시작이야.'
  },
  {
    userMsg: '엄마랑 또 부딪혔어 너무 답답해',
    botMsg1: '또 그 패턴이네. 같이 들여다보자.',
    cardId: 'cups05',
    cardName: '컵 5',
    cardSub: '쏟긴 마음에',
    botMsg2: '쏟긴 컵만 보고 있지?<br>뒤에 두 개 아직 남아있어. 다 잃은 거 아니야.'
  },
  {
    userMsg: '좋아하는 사람한테 고백할까 말까',
    botMsg1: '머릿속 복잡한 거 알아. 카드 한 장 펴자.',
    cardId: 'cups02',
    cardName: '컵 2',
    cardSub: '마음 흔들리는 너에게',
    botMsg2: '컵 2야. 이미 마음은 답을 알고 있어.<br>거절이 무서워서 미루는 거잖아. 그것도 답이야.'
  },
  {
    userMsg: '잠이 안 와 매일 새벽까지 뒤척여',
    botMsg1: '계속 그러면 진짜 지치지. 카드부터 뽑자.',
    cardId: 'swords09',
    cardName: '검 9',
    cardSub: '잠 못 드는 너에게',
    botMsg2: '검 9야. 생각이 너를 찌르고 있는 거지.<br>다 너의 잘못 같지? 사실 그만큼 진심이라서 그래.'
  }
]

const pickRandomScenario = () => {
  const idx = Math.floor(Math.random() * CHAT_SCENARIOS.length)
  const s = CHAT_SCENARIOS[idx]
  return { ...s, cardImg: getCardImageUrl(s.cardId) }
}
const randomScenario = ref(pickRandomScenario())

const categories = computed(() => [
  { key: '연애', emoji: '💕', label: t('landing.categories.love') },
  { key: '진로', emoji: '🧭', label: t('landing.categories.career') },
  { key: '재물', emoji: '💰', label: t('landing.categories.money') },
  { key: '학업', emoji: '📚', label: t('landing.categories.study') },
  { key: '건강', emoji: '💪', label: t('landing.categories.health') },
  { key: '기타', emoji: '✨', label: t('landing.categories.other') },
])

const mobileMenuOpen = ref(false)
const showFloatingCta = ref(false)
const todaySectionRef = ref<HTMLElement | null>(null)

const onScroll = () => {
  showFloatingCta.value = window.scrollY > 600
}

const questionInput = ref('')
const popularPosts = ref<any[]>([])
const loadingPopular = ref(false)

// Star particle style generator
const starStyle = (n: number) => {
  const seed = n * 137.508
  const left = ((seed * 7) % 100)
  const top = ((seed * 13) % 100)
  const size = 1 + (n % 3)
  const delay = (n * 0.3) % 5
  const duration = 2 + (n % 3)
  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

const miniStarStyle = (n: number) => {
  const seed = n * 97.3
  const left = ((seed * 11) % 100)
  const top = ((seed * 17) % 100)
  const size = 1 + (n % 2)
  const delay = (n * 0.4) % 4
  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`
  }
}

const sparkleStyle = (n: number) => {
  const angle = (n / 6) * 360
  const distance = 60 + (n % 3) * 20
  const x = Math.cos(angle * Math.PI / 180) * distance
  const y = Math.sin(angle * Math.PI / 180) * distance
  const delay = n * 0.5
  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    animationDelay: `${delay}s`
  }
}

// Scroll-triggered animations
const setupScrollAnimations = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-visible')
        }
      })
    },
    { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
  )

  nextTick(() => {
    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
      observer.observe(el)
    })
  })
}


const todayCard = computed(() => {
  const today = new Date()
  const dateString = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`
  let hash = 0
  for (let i = 0; i < dateString.length; i++) {
    hash = ((hash << 5) - hash) + dateString.charCodeAt(i)
    hash = hash & hash
  }
  const cardIds = Object.keys(cardDatabase)
  const index = Math.abs(hash) % cardIds.length
  const cardId = cardIds[index]
  const card = cardDatabase[cardId]
  return {
    id: cardId,
    name: card.name,
    subtitle: card.subtitle,
    meaning: card.uprightMeaning.slice(0, 150) + '...',
    keywords: card.uprightKeywords.slice(0, 3),
    imagePath: getCardImageUrl(cardId)
  }
})

const startWithQuestion = () => {
  if (questionInput.value.trim()) {
    trackReadingStarted('landing_input')
    router.push({ path: '/reading', query: { q: questionInput.value.trim() } })
  }
}

const startWithQuickQuestion = (question: string) => {
  trackReadingStarted('landing_quick_question')
  router.push({ path: '/reading', query: { q: question } })
}

const goToReading = (category: string) => {
  trackReadingStarted('landing_category')
  router.push({ path: '/reading', query: { category } })
}

const shareTodayCard = () => {
  const shareText = `오늘의 타로 카드: ${todayCard.value.name}\n${todayCard.value.subtitle}\n\nhttps://serapina.kr`
  if (navigator.share) {
    navigator.share({ title: '오늘의 타로 카드', text: shareText }).catch(() => {})
  } else {
    navigator.clipboard.writeText(shareText).then(() => alert('링크 복사됐어!'))
  }
}

const visiblePopularPosts = computed(() => popularPosts.value.slice(0, gridCols.value))

const fetchPopularPosts = async () => {
  loadingPopular.value = true
  try {
    const response = await axios.get('/api/blog', { params: { sort: 'popular', limit: 6 } })
    popularPosts.value = response.data.posts
  } catch (error) {
    console.error('Failed to fetch popular posts:', error)
  } finally {
    loadingPopular.value = false
  }
}

onMounted(async () => {
  window.addEventListener('resize', onResize)
  window.addEventListener('scroll', onScroll, { passive: true })
  await fetchPopularPosts()
  setupScrollAnimations()
  const script = document.createElement('script')
  script.async = true
  script.src = '//t1.daumcdn.net/kas/static/ba.min.js'
  document.head.appendChild(script)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onScroll)
})

const startDailyFortune = () => {
  trackReadingStarted('landing_daily_fortune')
  router.push({ path: '/reading', query: { daily: 'true' } })
}

const goToGuide = (type: string) => router.push(`/guides/${type}`)
const onHeroCtaClick = () => {
  trackCtaClick('hero_cta', 'landing_hero')
  trackReadingStarted('landing_cta')
  router.push('/reading')
}

const onFloatingCtaClick = () => {
  trackCtaClick('floating_cta', 'landing_bottom')
  trackReadingStarted('landing_floating_cta')
  router.push('/reading')
}

const onFinalCtaClick = () => {
  trackCtaClick('final_cta', 'landing_final')
  trackReadingStarted('landing_final_cta')
  router.push('/reading')
}

const goToPage = (path: string) => router.push(path)
</script>

<style scoped>
/* Base */
.landing-main {
  background: var(--bg-secondary);
  min-height: 100vh;
  overflow-x: hidden;
}

/* Star Particles */
.stars-container,
.final-stars {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.5); }
}

.mini-star {
  position: absolute;
  background: var(--border-color);
  border-radius: 50%;
  animation: twinkle 4s ease-in-out infinite;
}

/* Hero Section */
.hero-section {
  position: relative;
  background: linear-gradient(160deg, #0f0a1e 0%, #2D1B69 25%, var(--primary-color) 50%, var(--primary-color) 75%, var(--primary-color) 100%);
  padding-bottom: 80px;
  overflow: hidden;
}

.hero-bg-elements {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #C084FC;
  top: -100px;
  right: -80px;
  animation: float-slow 8s ease-in-out infinite;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #F0ABFC;
  bottom: -60px;
  left: -60px;
  animation: float-slow 10s ease-in-out infinite reverse;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #818CF8;
  top: 40%;
  left: 50%;
  animation: float-slow 12s ease-in-out infinite;
}

@keyframes float-slow {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -30px) scale(1.1); }
}

/* Hero Wave Divider */
.hero-wave {
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  z-index: 2;
  line-height: 0;
}

.hero-wave svg {
  width: 100%;
  height: 80px;
  display: block;
}

/* Header */
.landing-header {
  position: relative;
  z-index: 10;
  padding: 16px 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-logo {
  width: 32px;
  height: 32px;
  display: inline-block;
  vertical-align: middle;
  object-fit: contain;
  border-radius: 8px;
}

.app-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.header-icon-btn {
  color: var(--text-primary) !important;
  border-radius: 12px !important;
}

.header-icon-btn:hover {
  color: var(--text-primary) !important;
  background: var(--border-color) !important;
}

.mobile-only {
  display: none !important;
}

/* Mobile Menu */
.mobile-menu {
  position: absolute;
  top: 100%;
  right: 16px;
  background: rgba(45, 27, 105, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 8px;
  min-width: 200px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  z-index: 50;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: 12px;
  transition: background 0.2s ease;
  text-decoration: none;
}

.mobile-menu-item:hover {
  background: var(--border-color);
}

.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.menu-slide-enter-from,
.menu-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Hero Content */
.hero-content {
  position: relative;
  z-index: 5;
  max-width: 700px;
  margin: 0 auto;
  padding: 48px 24px 40px;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  padding: 6px 16px;
  background: var(--border-color);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  letter-spacing: 0.3px;
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 8px var(--border-color); }
  50% { box-shadow: 0 0 20px var(--border-color); }
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 16px;
  line-height: 1.25;
  letter-spacing: -0.02em;
}

.hero-desc {
  font-size: 1.1rem;
  color: var(--text-primary);
  margin-bottom: 40px;
  line-height: 1.6;
}

/* 보조 CTA: 질문 없이 바로 시작 */
.hero-cta-sub {
  margin-top: 14px;
  color: var(--text-primary) !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em;
  transition: color 0.2s ease !important;
}

.hero-cta-sub:hover {
  color: var(--text-primary) !important;
}

.input-card-label {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 12px;
  text-align: center;
}

/* Glass Input Card */
.hero-input-card {
  margin-top: 20px;
  background: var(--border-color);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.question-input {
  border-radius: 16px !important;
}

.question-input :deep(.v-field) {
  background: var(--text-primary) !important;
  border-radius: 16px !important;
  box-shadow: none !important;
}

.question-input :deep(.v-field__overlay) {
  background: transparent !important;
  opacity: 0 !important;
}

.question-input :deep(.v-field__input) {
  padding: 12px 16px !important;
  min-height: 48px;
  font-size: 0.95rem;
  color: #1a1a1a !important;
  font-weight: 500;
}

.question-input :deep(.v-field__input::placeholder) {
  color: rgba(0, 0, 0, 0.4);
  font-weight: 400;
}

.question-input :deep(.v-field__append-inner) {
  padding-right: 8px;
  align-items: center;
}

.question-input :deep(.v-field__append-inner .v-icon) {
  color: var(--primary-color);
  font-size: 28px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.question-input :deep(.v-field__append-inner .v-icon:hover) {
  opacity: 1;
  transform: scale(1.1);
}

.quick-questions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

.quick-q-chip {
  padding: 8px 16px;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.quick-q-chip:hover {
  background: var(--border-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--border-color);
}

/* Social Proof Bar */
.social-proof-bar {
  position: relative;
  z-index: 5;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  padding: 20px 24px;
  margin: 0 auto 24px;
  max-width: 600px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.proof-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.proof-number {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.proof-label {
  font-size: 0.75rem;
  color: var(--text-primary);
  font-weight: 500;
}

.proof-divider {
  width: 1px;
  height: 32px;
  background: var(--border-color);
}

/* Category Bar */
.category-bar {
  position: relative;
  z-index: 5;
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 0 24px 0;
  flex-wrap: wrap;
  max-width: 700px;
  margin: 0 auto;
}

.category-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--border-color);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-pill:hover {
  background: var(--border-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--border-color);
}

.cat-emoji {
  font-size: 1rem;
}

.cat-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* Today's Card */
.today-section {
  position: relative;
  padding: 80px 24px 40px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.section-stars {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.today-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  gap: 48px;
  align-items: center;
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  padding: 48px;
  border: 1px solid var(--button-hover-bg);
  box-shadow: 0 8px 40px var(--shadow-purple);
  transition: all 0.4s ease;
}

.today-inner:hover {
  border-color: var(--border-color);
  box-shadow: 0 12px 60px var(--shadow-purple);
}

.today-card-visual {
  flex-shrink: 0;
  position: relative;
}

.card-glow {
  position: absolute;
  inset: -30px;
  background: radial-gradient(circle, var(--shadow-purple) 0%, var(--button-hover-bg) 50%, transparent 70%);
  border-radius: 24px;
  z-index: 0;
  animation: card-glow-pulse 4s ease-in-out infinite;
}

@keyframes card-glow-pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

.card-sparkles {
  position: absolute;
  inset: -40px;
  z-index: 2;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: sparkle-float 3s ease-in-out infinite;
}

@keyframes sparkle-float {
  0%, 100% { opacity: 0; transform: scale(0); }
  50% { opacity: 1; transform: scale(1); }
}

.today-card-img {
  position: relative;
  z-index: 1;
  width: 200px;
  border-radius: 16px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4), 0 0 30px var(--shadow-purple);
  transition: transform 0.4s ease;
}

.today-inner:hover .today-card-img {
  transform: scale(1.03) rotate(1deg);
}

.today-card-info {
  flex: 1;
}

.today-label {
  display: inline-block;
  padding: 4px 14px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color));
  color: var(--text-primary);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

.today-name {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.today-subtitle {
  font-size: 1rem;
  color: var(--primary-color);
  font-style: italic;
  margin: 0 0 16px;
  font-weight: 500;
}

.today-meaning {
  font-size: 0.95rem;
  color: var(--text-primary);
  line-height: 1.7;
  margin: 0 0 20px;
}

.today-keywords {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.kw-chip {
  padding: 6px 14px;
  background: var(--button-hover-bg);
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--primary-color);
  border: 1px solid var(--border-color);
}

.daily-fortune-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color));
  border: none;
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.4);
}

.daily-fortune-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(139, 92, 246, 0.5);
}

.share-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: var(--border-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn:hover {
  background: var(--button-hover-bg);
  border-color: var(--border-color);
}

.today-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.today-detail-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary-color);
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.today-inner:hover .today-detail-link {
  opacity: 1;
}

/* Mystical Divider between sections */
.mystical-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px 0 0;
}

.divider-star {
  color: var(--border-color);
  font-size: 0.8rem;
}

.divider-line {
  width: 60px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color), transparent);
}

/* Section Common */
.sec-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 40px;
  letter-spacing: -0.02em;
}

.title-accent {
  display: inline-block;
  animation: bounce-soft 2s ease-in-out infinite;
}

@keyframes bounce-soft {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.sec-desc {
  text-align: center;
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 40px;
}

/* Scroll Animations */
.animate-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.animate-on-scroll.animate-visible {
  opacity: 1;
  transform: translateY(0);
}

/* Popular Section */
.popular-section {
  padding: 80px 24px;
  background: var(--bg-secondary);
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.popular-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.popular-card {
  padding: 28px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  border: 1px solid transparent;
}

.popular-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.popular-accent-0 {
  background: linear-gradient(145deg, rgba(254, 202, 202, 0.1) 0%, rgba(252, 165, 165, 0.15) 100%);
  border-color: rgba(254, 202, 202, 0.2);
}

.popular-accent-1 {
  background: linear-gradient(145deg, var(--card-bg) 0%, var(--button-hover-bg) 100%);
  border-color: var(--border-color);
}

.popular-accent-2 {
  background: linear-gradient(145deg, rgba(134, 239, 172, 0.1) 0%, rgba(74, 222, 128, 0.15) 100%);
  border-color: rgba(134, 239, 172, 0.2);
}

.pop-emoji {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.pop-category {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--primary-color);
  background: var(--button-hover-bg);
  padding: 3px 10px;
  border-radius: 8px;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pop-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
  line-height: 1.4;
}

.pop-views {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

/* Section Break Ornament */
.section-break {
  padding: 20px 0;
  background: var(--bg-secondary);
}

.break-ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.ornament-dot {
  width: 4px;
  height: 4px;
  background: var(--border-color);
  border-radius: 50%;
}

.ornament-line {
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color), transparent);
}

.ornament-symbol {
  color: var(--border-color);
  font-size: 1.2rem;
}

/* Topics Section */
.topics-section {
  padding: 80px 24px;
  background: var(--bg-secondary);
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.topic-card {
  position: relative;
  padding: 32px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.topic-glow {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.topic-card:hover .topic-glow {
  opacity: 1;
}

.topic-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.topic-love {
  background: rgba(255, 100, 130, 0.08);
  border: 1px solid rgba(255, 100, 130, 0.2);
}

.topic-love .topic-glow {
  background: radial-gradient(circle at center, rgba(255, 100, 130, 0.15) 0%, transparent 70%);
}

.topic-career {
  background: var(--button-hover-bg);
  border: 1px solid var(--button-hover-bg);
}

.topic-career .topic-glow {
  background: radial-gradient(circle at center, var(--button-hover-bg) 0%, transparent 70%);
}

.topic-study {
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.topic-study .topic-glow {
  background: radial-gradient(circle at center, rgba(251, 191, 36, 0.15) 0%, transparent 70%);
}

.topic-money {
  background: rgba(74, 222, 128, 0.08);
  border: 1px solid rgba(74, 222, 128, 0.2);
}

.topic-money .topic-glow {
  background: radial-gradient(circle at center, rgba(74, 222, 128, 0.15) 0%, transparent 70%);
}

.topic-icon {
  font-size: 2.5rem;
}

.topic-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.topic-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Steps Section (How It Works) */
.steps-section {
  padding: 80px 24px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, #231544 100%);
  position: relative;
}

.sec-title-light {
  color: var(--text-primary);
}

.steps-timeline {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}

.step-item {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  position: relative;
  padding-bottom: 40px;
}

.step-item:last-child {
  padding-bottom: 0;
}

.step-item:last-child .step-connector {
  display: none;
}

.step-number {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color));
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px var(--shadow-purple);
  position: relative;
  z-index: 2;
}

.step-connector {
  position: absolute;
  left: 23px;
  top: 48px;
  width: 2px;
  bottom: 0;
  background: linear-gradient(180deg, var(--border-color) 0%, var(--button-hover-bg) 100%);
  z-index: 1;
}

.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-icon-wrap {
  margin-bottom: 8px;
}

.step-icon {
  font-size: 1.8rem;
}

.step-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.step-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

/* Final CTA Section */
.final-cta-section {
  position: relative;
  padding: 100px 24px;
  background: linear-gradient(160deg, #2D1B69 0%, var(--primary-color) 50%, var(--primary-color) 100%);
  text-align: center;
  overflow: hidden;
}

.final-cta-content {
  position: relative;
  z-index: 2;
}

.final-cta-icon {
  font-size: 3rem;
  margin-bottom: 24px;
  animation: float-slow 4s ease-in-out infinite;
}

.final-cta-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.final-cta-desc {
  font-size: 1.1rem;
  color: var(--text-primary);
  margin: 0 0 40px;
  line-height: 1.6;
}

.final-cta-btn {
  padding: 0 48px !important;
  height: 56px !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 0 60px var(--border-color) !important;
  transition: all 0.3s ease !important;
}

.final-cta-btn:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 80px var(--border-color) !important;
}

.final-cta-btn-text {
  color: var(--primary-color);
}

/* Footer */
.landing-footer {
  padding: 40px 24px 100px;
  text-align: center;
  border-top: 1px solid var(--button-hover-bg);
  background: var(--bg-secondary);
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.footer-links a {
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.3s ease;
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--primary-color);
}

.footer-dot {
  color: var(--border-color);
}

.footer-copy {
  font-size: 0.78rem;
  color: var(--border-color);
  margin: 0;
}

/* Floating CTA */
.floating-cta {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  background: rgba(26, 16, 51, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--button-hover-bg);
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
}

.floating-cta-btn {
  height: 52px !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.01em;
  text-transform: none !important;
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

/* Desktop: hide floating CTA */
@media (min-width: 960px) {
  .floating-cta {
    display: none;
  }
}

/* Responsive */
@media (max-width: 960px) {
  .hero-title {
    font-size: 2.4rem;
  }

  .today-inner {
    flex-direction: column;
    padding: 32px;
    text-align: center;
  }

  .today-card-info {
    text-align: center;
  }

  .today-keywords {
    justify-content: center;
  }

  .today-card-img {
    width: 180px;
  }

  .today-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .popular-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .step-item {
    gap: 16px;
  }
}

@media (max-width: 600px) {
  .hero-content {
    padding: 32px 16px 32px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-desc {
    font-size: 0.95rem;
    margin-bottom: 28px;
  }

  .hero-input-card {
    padding: 14px;
  }

  .quick-q-chip {
    font-size: 0.75rem;
    padding: 6px 12px;
  }

  .category-bar {
    gap: 8px;
  }

  .category-pill {
    padding: 8px 14px;
  }

  .cat-label {
    font-size: 0.8rem;
  }

  .header-icon-btn.desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: flex !important;
  }

  .social-proof-bar {
    gap: 16px;
    padding: 16px;
  }

  .proof-number {
    font-size: 1.1rem;
  }

  .proof-label {
    font-size: 0.68rem;
  }

  .hero-cta-btn {
    height: 48px !important;
    font-size: 1rem !important;
    padding: 0 32px !important;
  }

  .sec-title {
    font-size: 1.6rem;
    margin-bottom: 28px;
  }

  .popular-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .popular-card {
    padding: 20px;
  }

  .topics-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .today-inner {
    padding: 24px;
  }

  .today-card-img {
    width: 160px;
  }

  .today-name {
    font-size: 1.5rem;
  }

  .popular-section,
  .topics-section,
  .steps-section,
  .today-section {
    padding: 56px 16px;
  }

  .final-cta-section {
    padding: 72px 16px;
  }

  .final-cta-title {
    font-size: 1.8rem;
  }

  .step-number {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  .step-connector {
    left: 19px;
    top: 40px;
  }

  .today-actions {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
}
/* Chat Preview Section */
.chat-preview-section {
  padding: 80px 1.5rem;
  background: linear-gradient(180deg, #F4EBDC 0%, #E8DCC4 100%);
  position: relative;
}
.chat-preview-inner {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}
.chat-section-label {
  display: inline-block;
  background: #1A1A2E;
  color: #FEF8E7;
  padding: 6px 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-bottom: 24px;
  border-radius: 999px;
}
.chat-section-title {
  font-family: 'Pretendard', sans-serif;
  font-size: 36px;
  font-weight: 900;
  line-height: 1.2;
  letter-spacing: -0.035em;
  color: #1A1A2E;
  margin-bottom: 40px;
}
.yellow-highlight {
  background: #FEF3C7;
  padding: 0 10px;
  border-radius: 6px;
}
.chat-preview-box {
  background: white;
  border-radius: 24px;
  padding: 32px 28px 26px;
  box-shadow: 0 20px 40px rgba(26, 26, 46, 0.12);
  border: 2px solid #1A1A2E;
  text-align: left;
}
.chat-bubble {
  margin-bottom: 12px;
  max-width: 82%;
  padding: 12px 18px;
  border-radius: 20px;
  font-family: 'Pretendard', sans-serif;
  font-size: 15px;
  line-height: 1.5;
  letter-spacing: -0.015em;
  font-weight: 500;
}
.chat-user {
  background: #C4B5FD;
  color: #1A1A2E;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}
.chat-bot {
  background: #FEF8E7;
  color: #1A1A2E;
  border-bottom-left-radius: 4px;
}
.chat-bubble-card {
  display: flex;
  gap: 12px;
  align-items: center;
  margin: 10px 0 12px;
  padding: 12px;
  background: #FB7185;
  border-radius: 14px;
  max-width: 82%;
}
.chat-card-img {
  width: 56px;
  height: auto;
  border-radius: 6px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.chat-card-meta {
  display: flex;
  flex-direction: column;
}
.chat-card-name {
  font-family: 'Pretendard', sans-serif;
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 800;
  margin-bottom: 1px;
}
.chat-card-en {
  font-family: 'Space Grotesk', 'Pretendard', sans-serif;
  font-size: 11px;
  color: var(--text-primary);
  letter-spacing: 0.12em;
  font-weight: 600;
}
@media (max-width: 600px) {
  .chat-preview-section { padding: 60px 1rem; }
  .chat-section-title { font-size: 28px; }
  .chat-preview-box { padding: 26px 22px 22px; }
}

/* D 톤 오버라이드 */
/* 팔레트: 크림 #FEF8E7, 웜 베이지 #F4EBDC, 코랄 #FB7185, 라벤더 #C4B5FD, 민트 #6EE7B7, 잉크 #1A1A2E */

/* Hero 배경 (베이지) */
.hero-section {
  background: linear-gradient(180deg, #FEF8E7 0%, #F4EBDC 100%) !important;
}
.hero-section .hero-bg-elements .hero-orb {
  opacity: 0.18 !important;
}
.hero-section .stars-container { opacity: 0.25 !important; }

/* Hero 헤더 */
.landing-header { background: transparent !important; }
.app-title { color: #1A1A2E !important; }
.header-logo { filter: none !important; border-radius: 8px; }
.header-icon-btn { color: #1A1A2E !important; }

/* Hero 콘텐츠 */
.hero-badge {
  background: #1A1A2E !important;
  color: #FEF8E7 !important;
  letter-spacing: 0.18em !important;
}
.hero-title { color: #1A1A2E !important; }
.hero-desc { color: #2D2D4D !important; }

/* Hero 입력 카드 (Memphis 스타일) */
.hero-input-card {
  background: white !important;
  border: 2px solid #1A1A2E !important;
  box-shadow: 5px 5px 0 #FB7185 !important;
  border-radius: 20px !important;
}
.input-card-label { color: #2D2D4D !important; }
.question-input :deep(.v-field) { background: white !important; }
.quick-q-chip {
  background: #FEF3C7 !important;
  color: #1A1A2E !important;
  border: 1px solid #1A1A2E !important;
  font-weight: 600 !important;
}
.quick-q-chip:hover { background: #FB7185 !important; color: var(--text-primary) !important; }
.hero-cta-sub { color: #2D2D4D !important; }

/* Social Proof */
.social-proof-bar { background: rgba(255, 255, 255, 0.5) !important; border-color: #1A1A2E !important; }
.proof-number { color: #FB7185 !important; }
.proof-label { color: #2D2D4D !important; }

/* Category Pills */
.category-pill {
  background: white !important;
  border: 1.5px solid #1A1A2E !important;
  color: #1A1A2E !important;
}
.category-pill:hover { background: #C4B5FD !important; }
.cat-label { color: #1A1A2E !important; }

/* Hero Wave Divider */
.hero-wave svg path { fill: #F4EBDC !important; }

/* Topics 카드 (Memphis 보더 + 그림자) */
.topics-section { background: #F4EBDC !important; }
.topics-section .sec-title { color: #1A1A2E !important; }
.topic-card {
  border: 2px solid #1A1A2E !important;
  border-radius: 20px !important;
  transition: 0.2s !important;
}
.topic-card:hover {
  transform: translateY(-4px) !important;
  box-shadow: 6px 6px 0 #1A1A2E !important;
}
.topic-card.topic-love { background: rgba(251, 113, 133, 0.18) !important; }
.topic-card.topic-career { background: rgba(196, 181, 253, 0.18) !important; }
.topic-card.topic-study { background: rgba(110, 231, 183, 0.18) !important; }
.topic-card.topic-money { background: rgba(254, 243, 199, 0.6) !important; }
.topic-name { color: #1A1A2E !important; }
.topic-desc { color: #2D2D4D !important; }

/* Popular 카드 */
.popular-section { background: #FEF8E7 !important; }
.popular-section .sec-title { color: #1A1A2E !important; }
.popular-card {
  background: white !important;
  border: 2px solid #1A1A2E !important;
  border-radius: 16px !important;
  transition: 0.2s !important;
}
.popular-card:hover {
  transform: translateY(-3px) !important;
  box-shadow: 5px 5px 0 #FB7185 !important;
}
.pop-category { background: #C4B5FD !important; color: #1A1A2E !important; }
.pop-title { color: #1A1A2E !important; }
.pop-views { color: #2D2D4D !important; }

/* Mystical Divider */
.section-break .ornament-symbol { color: #FB7185 !important; }
.section-break .ornament-line { background: #1A1A2E !important; opacity: 0.3 !important; }
.section-break .ornament-dot { background: #FB7185 !important; }

/* Instagram Section */
.insta-section {
  padding: 80px 1.5rem;
  background: #6EE7B7;
  position: relative;
}
.insta-inner {
  max-width: 720px;
  margin: 0 auto;
}
.insta-card {
  background: #FEF8E7;
  border: 2px solid #1A1A2E;
  border-radius: 24px;
  padding: 32px 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  box-shadow: 6px 6px 0 #1A1A2E;
  text-decoration: none;
  color: inherit;
  transition: 0.2s;
}
.insta-card:hover {
  transform: translateY(-3px);
  box-shadow: 9px 9px 0 #1A1A2E;
}
.insta-text h4 {
  font-family: 'Pretendard', sans-serif;
  font-size: 24px;
  font-weight: 900;
  color: #1A1A2E;
  margin-bottom: 6px;
  letter-spacing: -0.025em;
}
.insta-text p {
  font-family: 'Pretendard', sans-serif;
  font-size: 14px;
  color: #2D2D4D;
  line-height: 1.6;
  font-weight: 500;
}
.insta-handle {
  font-family: 'Pretendard', sans-serif;
  font-size: 22px;
  font-weight: 800;
  color: #FB7185;
  white-space: nowrap;
  letter-spacing: -0.01em;
}
@media (max-width: 600px) {
  .insta-section { padding: 60px 1rem; }
  .insta-card { flex-direction: column; align-items: flex-start; padding: 24px 22px; gap: 12px; }
  .insta-handle { font-size: 18px; }
  .insta-text h4 { font-size: 20px; }
}

/* Footer */
.landing-footer {
  background: #1A1A2E !important;
  color: #FEF8E7 !important;
}
.landing-footer .footer-links a { color: #FEF8E7 !important; opacity: 0.85; }
.landing-footer .footer-dot { color: #FB7185 !important; }
.landing-footer .footer-copy { color: rgba(254, 248, 231, 0.6) !important; }

/* Mobile Floating CTA */
.floating-cta-btn {
  background: #1A1A2E !important;
  color: #FEF8E7 !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
  box-shadow: 0 8px 24px rgba(26, 26, 46, 0.3) !important;
}
.floating-cta-btn :deep(.v-icon) { color: #FB7185 !important; }

/* 가독성 보정 */

/* Hero 배경 데코는 베이지 위에서 튀어서 흐리게 */
.hero-section .hero-orb { opacity: 0.04 !important; }
.hero-section .stars-container { display: none !important; }
.hero-section .star { display: none !important; }

/* Topics 카드 배경 */
.topic-card.topic-love { background: rgba(251, 113, 133, 0.32) !important; }
.topic-card.topic-career { background: rgba(196, 181, 253, 0.4) !important; }
.topic-card.topic-study { background: rgba(110, 231, 183, 0.4) !important; }
.topic-card.topic-money { background: rgba(254, 220, 130, 0.7) !important; }
.topic-glow { display: none !important; }
.topic-icon { filter: none !important; }

/* Topics, Popular 카드 텍스트 */
.topic-name, .topic-desc, .pop-title, .pop-category, .pop-views {
  color: #1A1A2E !important;
}
.pop-views .v-icon { color: #2D2D4D !important; }
.pop-category { color: #1A1A2E !important; background: #FEF3C7 !important; border: 1px solid #1A1A2E !important; }

/* Today 섹션 끝 Mystical Divider */
.mystical-divider {
  background: transparent !important;
}
.mystical-divider .divider-star { color: #C4B5FD !important; opacity: 0.8 !important; }
.mystical-divider .divider-line { background: #C4B5FD !important; opacity: 0.4 !important; }

/* 섹션 사이 break ornament */
.section-break {
  background: #F4EBDC !important;
  padding: 20px 0 !important;
}

/* Quick Questions chips */
.quick-q-chip {
  font-size: 0.85rem !important;
  padding: 8px 14px !important;
}

/* Hero badge */
.hero-badge {
  display: inline-block !important;
  border-radius: 999px !important;
  font-size: 0.75rem !important;
  padding: 6px 14px !important;
}

/* Hero 입력카드 placeholder */
.question-input :deep(.v-field__input) { color: #1A1A2E !important; }
.question-input :deep(.v-field__input::placeholder) { color: #6B6B7B !important; }

/* Social proof divider */
.proof-divider { background: #1A1A2E !important; opacity: 0.2 !important; }

/* Today 섹션 (라벤더) */
.today-section {
  background: linear-gradient(180deg, #C4B5FD 0%, #A78BFA 100%) !important;
  padding: 80px 1.5rem 60px !important;
}
.today-section .section-stars { opacity: 0.35 !important; }
.today-section .mini-star { background: rgba(255, 255, 255, 0.7) !important; box-shadow: 0 0 6px rgba(255,255,255,0.5) !important; }
.today-section .card-glow { display: none !important; }
.today-section .card-sparkles { opacity: 0.5 !important; }
.today-section .sparkle { background: #FEF8E7 !important; }

.today-section .today-label {
  background: #FEF3C7 !important;
  color: #1A1A2E !important;
  padding: 6px 14px !important;
  border-radius: 999px !important;
  font-weight: 700 !important;
  letter-spacing: 0.15em !important;
  border: 1.5px solid #1A1A2E !important;
  display: inline-block !important;
}
.today-section .today-name { color: #1A1A2E !important; }
.today-section .today-subtitle { color: #2D2D4D !important; }
.today-section .today-meaning { color: #1A1A2E !important; opacity: 0.85 !important; }

.today-section .kw-chip {
  background: #FEF8E7 !important;
  color: #1A1A2E !important;
  border: 1.5px solid #1A1A2E !important;
  font-weight: 600 !important;
}
.today-section .today-detail-link {
  color: #1A1A2E !important;
  font-weight: 700 !important;
}
.today-section .share-btn {
  background: white !important;
  color: #1A1A2E !important;
  border: 1.5px solid #1A1A2E !important;
}
.today-section .daily-fortune-btn {
  background: #FB7185 !important;
  color: var(--text-primary) !important;
  border: 2px solid #1A1A2E !important;
  box-shadow: 4px 4px 0 #1A1A2E !important;
  font-weight: 700 !important;
}
.today-section .daily-fortune-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 6px 6px 0 #1A1A2E !important;
}
.today-card-img {
  border: 2px solid #1A1A2E !important;
  border-radius: 12px !important;
  box-shadow: 8px 8px 0 #1A1A2E !important;
}

/* Hero 입력카드 */
.hero-input-card {
  padding: 28px 24px !important;
}
.input-card-label {
  color: #1A1A2E !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  margin-bottom: 14px !important;
  letter-spacing: -0.015em !important;
}
.question-input :deep(.v-field) {
  background: #FEF8E7 !important;
  border: 1.5px solid #1A1A2E !important;
  border-radius: 999px !important;
  padding-right: 4px !important;
  box-shadow: none !important;
}
.question-input :deep(.v-field__input) {
  color: #1A1A2E !important;
  font-size: 1rem !important;
  padding: 12px 18px !important;
  min-height: 48px !important;
}
.question-input :deep(.v-field__input input) { color: #1A1A2E !important; }
.question-input :deep(.v-field__input input::placeholder) {
  color: #6B6B7B !important;
  font-style: italic !important;
  opacity: 1 !important;
}
.question-input :deep(.v-field__append-inner .v-icon) {
  color: #FB7185 !important;
  font-size: 28px !important;
}

/* Hero 메인 일러스트 */
.hero-illustration {
  margin: 32px auto 0;
  max-width: 460px;
  text-align: center;
}
.hero-illustration img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 20px;
  border: 2px solid #1A1A2E;
  box-shadow: 6px 6px 0 #FB7185;
}
@media (max-width: 600px) {
  .hero-illustration { max-width: 320px; margin-top: 24px; }
  .hero-illustration img { border-radius: 16px; box-shadow: 4px 4px 0 #FB7185; }
}

</style>
