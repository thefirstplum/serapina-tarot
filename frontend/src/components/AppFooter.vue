<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <img src="/icons/symbol-64.png" alt="세라피나" class="footer-logo" />
        <div>
          <div class="footer-brand-name">세라피나</div>
          <div class="footer-brand-tagline">MBTI × 타로 — 너에게 딱 맞는 카드 해석</div>
        </div>
      </div>

      <nav class="footer-nav" aria-label="사이트 내비게이션">
        <router-link to="/about">소개</router-link>
        <router-link to="/contact">문의</router-link>
        <router-link to="/blog">블로그</router-link>
        <router-link to="/guides">가이드</router-link>
        <router-link to="/cards">카드 도감</router-link>
        <router-link to="/privacy">개인정보 처리방침</router-link>
        <router-link to="/terms">이용약관</router-link>
      </nav>

      <div class="footer-meta">
        <p class="footer-disclaimer">
          ※ 세라피나의 타로 해석은 <strong>엔터테인먼트·자기 성찰</strong>을 위한 콘텐츠예요.
          의학·법률·재무 결정의 근거로 삼지 말아주세요.
        </p>
        <p class="footer-copy">© 2026 세라피나 (Serapina). All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-footer {
  background: var(--bg-secondary);
  border-top: 2px solid var(--text-primary);
  padding: 32px 20px 28px;
  margin-top: 60px;
}

.footer-container {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1.5px solid var(--text-primary);
  background: var(--card-bg);
  box-shadow: 2.5px 2.5px 0 var(--text-primary);
}

.footer-brand-name {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: -0.015em;
}

.footer-brand-tagline {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 2px;
}

.footer-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  padding: 16px 0;
  border-top: 1.5px dashed rgba(26, 26, 46, 0.2);
  border-bottom: 1.5px dashed rgba(26, 26, 46, 0.2);
}

.footer-nav a {
  color: var(--text-primary);
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.15s;
  letter-spacing: -0.01em;
}

.footer-nav a:hover {
  background: var(--accent-yellow);
  color: var(--primary-color);
}

.footer-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-disclaimer {
  color: var(--text-primary);
  font-size: 0.82rem;
  line-height: 1.55;
  font-weight: 500;
  opacity: 0.85;
  margin: 0;
}

.footer-disclaimer strong {
  color: var(--primary-color);
  font-weight: 800;
}

.footer-copy {
  color: var(--text-secondary);
  font-size: 0.78rem;
  margin: 0;
  font-weight: 600;
}

@media (max-width: 600px) {
  .app-footer {
    padding: 28px 16px 22px;
    margin-top: 40px;
  }
  .footer-nav {
    gap: 4px 12px;
  }
  .footer-nav a {
    font-size: 0.82rem;
  }
}
</style>
