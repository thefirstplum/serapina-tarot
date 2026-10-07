import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'
import { trackPageView } from '../utils/analytics'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    // 브라우저 뒤로가기/앞으로가기 시 이전 스크롤 위치로
    if (savedPosition) {
      return savedPosition
    }
    // 페이지 이동 시 항상 최상단으로
    return { top: 0, behavior: 'smooth' }
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/chat',
      redirect: '/reading'
    },
    {
      path: '/reading',
      name: 'reading',
      component: () => import('../views/TarotReadingView.vue')
    },
    {
      path: '/cards',
      name: 'cards',
      component: () => import('../views/CardsView.vue')
    },
    {
      path: '/cards/major-arcana',
      name: 'major-arcana',
      component: () => import('../views/MajorArcanaView.vue')
    },
    {
      path: '/cards/minor-arcana',
      name: 'minor-arcana',
      component: () => import('../views/MinorArcanaView.vue')
    },
    {
      path: '/cards/:id',
      name: 'card-detail',
      component: () => import('../views/CardDetailView.vue')
    },
    {
      path: '/cards/suit/:suit',
      name: 'cards-suit',
      component: () => import('../views/CardsSuitView.vue')
    },
    {
      path: '/guides',
      name: 'guides',
      component: () => import('../views/GuidesView.vue')
    },
    {
      path: '/guides/love',
      name: 'guide-love',
      component: () => import('../views/GuideLoveView.vue')
    },
    {
      path: '/guides/career',
      name: 'guide-career',
      component: () => import('../views/GuideCareerView.vue')
    },
    {
      path: '/guides/study',
      name: 'guide-study',
      component: () => import('../views/GuideStudyView.vue')
    },
    {
      path: '/guides/money',
      name: 'guide-money',
      component: () => import('../views/GuideMoneyView.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/ContactView.vue')
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyView.vue')
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue')
    },
    {
      path: '/blog',
      name: 'blog',
      component: () => import('../views/BlogView.vue')
    },
    {
      path: '/blog/:id',
      name: 'blog-post',
      component: () => import('../views/BlogPostView.vue')
    },
    {
      path: '/today',
      name: 'today',
      component: () => import('../views/TodayView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue')
    },
    {
      path: '/today/:mbti',
      name: 'today-mbti',
      component: () => import('../views/TodayView.vue')
    },
    // 로그인·결제 관련 라우트 (현재 비활성)
    // {
    //   path: '/login',
    //   name: 'login',
    //   component: () => import('../views/LoginView.vue')
    // },
    // {
    //   path: '/auth/kakao/callback',
    //   name: 'auth-callback',
    //   component: () => import('../views/AuthCallbackView.vue')
    // },
    // {
    //   path: '/points',
    //   name: 'point-charge',
    //   component: () => import('../views/PointChargeView.vue')
    // },
    // {
    //   path: '/payments/success',
    //   name: 'payment-success',
    //   component: () => import('../views/PaymentSuccessView.vue')
    // },
    // {
    //   path: '/payments/fail',
    //   name: 'payment-fail',
    //   component: () => import('../views/PaymentFailView.vue')
    // },
    // {
    //   path: '/mypage',
    //   name: 'mypage',
    //   component: () => import('../views/MyPageView.vue')
    // },
    // {
    //   path: '/subscription',
    //   name: 'subscription',
    //   component: () => import('../views/SubscriptionView.vue')
    // },
    // {
    //   path: '/saved-readings',
    //   name: 'saved-readings',
    //   component: () => import('../views/SavedReadingsView.vue')
    // }
  ]
})

// 페이지 이동시 자동으로 Google Analytics 페이지뷰 추적
router.afterEach((to) => {
  trackPageView(to.path)
})

export default router