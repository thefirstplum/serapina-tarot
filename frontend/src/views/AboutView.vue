<template>
  <div class="app-main">
    <div class="page-layout">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <v-btn icon variant="flat" to="/" class="back-button">
            <v-icon size="28">mdi-arrow-left</v-icon>
          </v-btn>
          <div class="header-text">
            <h1 class="page-title">세라피나 소개</h1>
            <p class="page-subtitle">MBTI × 타로로 매일 너만의 답 찾기</p>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="page-content">
        <div class="content-container">
          <!-- 페르소나 소개 -->
          <div class="info-card persona-card">
            <h2 class="section-title">세라피나는 누구야?</h2>
            <p class="persona-tagline">"혼자 끙끙대지 마. 들어줄게."</p>
            <p class="section-text">
              마음 따뜻한 친구. 판단하지 않고 깊이 듣는 사람이야.
              너랑 비슷한 또래라 그 떨림·답답함·외로움 다 알아.
              밤에 깨어있는 친구처럼, 잠 안 오는 시간에 곁에 있어줄게.
            </p>
            <ul class="persona-list">
              <li>판단하지 않음 — "그럴 수도 있지" 먼저</li>
              <li>답 강요 X — 같이 헤매주는 자세</li>
              <li>조곤조곤 차분 — 흥분하지 않는 친구</li>
              <li>깊이 듣는 사람 — 표면 말고 그 뒤 마음</li>
              <li>밤에 깨어있는 친구 — 외로운 시간에 곁</li>
            </ul>
          </div>

          <!-- Mission -->
          <div class="info-card">
            <h2 class="section-title">세라피나가 만들어진 이유</h2>
            <p class="section-text">
              매일 밤 고민 한 줄, 두 줄 — 누구한테 말하기엔 사소하지만 나한테는 큰 일.
              그런 순간 옆에서 카드 한 장 뽑아보며 같이 고민할 친구가 필요했어.
            </p>
            <p class="section-text">
              그래서 만들었어. 가벼운 호기심으로 시작해도,
              깊은 고민으로 와도 — 받는 답이 너한테 딱 맞도록.
            </p>
          </div>

          <!-- 차별점 -->
          <div class="info-card">
            <h2 class="section-title">우리만의 차별점</h2>
            <h3 class="subsection-title">💎 MBTI × 타로 — 똑같은 카드, 다른 해석</h3>
            <p class="section-text">
              16가지 MBTI 유형마다 같은 카드를 다르게 받아들여.
              INFP한테 달 카드는 내면을 깊게 들여다보라는 신호고,
              ENTJ한테는 전략적으로 모호함을 관리하라는 신호야.
            </p>
            <p class="section-text">
              세라피나는 너의 성향까지 고려해서 — 너만의 답을 찾아줘.
              일반 타로 사이트는 못 하는 일이지.
            </p>

            <h3 class="subsection-title">💬 친구 톤 — 어렵지 않게</h3>
            <p class="section-text">
              "별 카드는 희망을 상징합니다" 같은 형식적인 말투 X.
              "별 카드 나왔다는 건 — 지금 네가 보고 있는 그 가능성, 진짜야"
              친구가 카페에서 해주는 톤으로 풀어줄게.
            </p>

            <h3 class="subsection-title">🌙 매일 무료로 시작</h3>
            <p class="section-text">
              회원가입 없이도 바로 카드 뽑을 수 있어.
              매일 무료 리딩 + 광고 보고 추가 리딩 — 부담 없이 와.
            </p>
          </div>

          <!-- 사용법 -->
          <div class="info-card">
            <h2 class="section-title">이렇게 써봐</h2>
            <ol class="section-list">
              <li>홈에서 "오늘의 운세" 또는 "타로 시작하기" 누르기</li>
              <li>네 MBTI 선택 (선택 사항 — 알려주면 해석 더 정확해져)</li>
              <li>고민·질문 입력 ("○○이랑 어떻게 될까?")</li>
              <li>카드 3장 뽑기 (과거·현재·미래)</li>
              <li>세라피나의 해석 받기 + "더 깊게" 추가 질문 가능</li>
            </ol>
          </div>

          <!-- 면책 -->
          <div class="info-card" style="background: var(--accent-yellow);">
            <h2 class="section-title">알아두세요</h2>
            <p class="section-text">
              세라피나의 타로 해석은 <strong>엔터테인먼트와 자기 성찰</strong>을 위한
              콘텐츠예요. 의학·법률·재무·중요한 인생 결정의 근거로는 삼지 말아주세요.
              어디까지나 너 마음을 정리하는 데 도움이 되는 도구예요.
            </p>
            <p class="section-text">
              심각한 고민이 있다면 <strong>전문 상담 기관</strong>을 찾아주세요.
              청소년상담 1388, 자살예방상담 1393, 정신건강위기상담 1577-0199.
            </p>
          </div>

          <!-- CTA -->
          <div class="cta-section">
            <div class="cta-card">
              <img src="/icons/symbol-128.png" class="cta-icon" alt="" width="56" height="56" />
              <h3>지금 카드 한 장 뽑아볼까?</h3>
              <p>고민 한 줄이면 충분해 — 세라피나가 같이 들여다봐줄게</p>
              <v-btn size="large" :to="{ name: 'reading' }">타로 시작하기</v-btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSeoMeta } from '@/composables/useSeoMeta'

useSeoMeta(
  '세라피나 소개 — MBTI × 타로 AI 상담사',
  'MBTI 16가지 유형마다 다른 타로 해석. 친구 톤 + 매일 무료 + 회원가입 없이 시작. 세라피나가 만들어진 이유와 차별점을 소개합니다.',
  '세라피나 소개, MBTI 타로, 타로 AI, 타로 해석, 무료 타로'
)
</script>

<style scoped>
.subsection-title {
  margin-top: 18px;
}

.persona-card {
  border: 1px solid var(--primary-color);
  background: linear-gradient(180deg, rgba(244, 63, 94, 0.04), transparent);
}

.persona-tagline {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--primary-color);
  text-align: center;
  margin: 8px 0 16px 0;
  font-style: italic;
}

.persona-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0 0;
}

.persona-list li {
  padding: 6px 0 6px 18px;
  font-size: 0.9rem;
  color: var(--text-primary);
  position: relative;
  line-height: 1.55;
}

.persona-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-weight: 700;
}
</style>
