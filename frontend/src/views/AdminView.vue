<template>
  <div class="admin-page">
    <header class="admin-header">
      <div class="header-content">
        <div class="header-left">
          <span class="brand">🔮 세라피나 어드민</span>
        </div>
        <div class="header-right">
          <span class="today-tag">{{ todayStr }}</span>
          <button class="refresh-btn" @click="refreshAll">
            <v-icon size="18">mdi-refresh</v-icon> 새로고침
          </button>
        </div>
      </div>
      <div class="tab-bar">
        <button
          v-for="t in TABS"
          :key="t.key"
          class="tab-btn"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.icon }} {{ t.label }}
        </button>
      </div>
    </header>

    <main class="admin-main">
      <!-- 대시보드 -->
      <section v-if="activeTab === 'dashboard'" class="tab-content">
        <div v-if="loading.dashboard" class="loading-state">로딩 중…</div>
        <div v-else-if="dashboard">
          <!-- 지표 카드 -->
          <div class="metric-grid">
            <div class="metric-card">
              <p class="metric-label">오늘 세션</p>
              <p class="metric-value">{{ dashboard.stats?.sessions_today ?? 0 }}</p>
              <p class="metric-sub">7일 합계: {{ dashboard.stats?.sessions_week ?? 0 }}</p>
            </div>
            <div class="metric-card">
              <p class="metric-label">오늘 리딩</p>
              <p class="metric-value">{{ dashboard.stats?.readings_today ?? 0 }}</p>
              <p class="metric-sub">7일 합계: {{ dashboard.stats?.readings_week ?? 0 }}</p>
            </div>
            <div class="metric-card">
              <p class="metric-label">블로그 노출</p>
              <p class="metric-value">{{ dashboard.stats?.blog_published ?? 0 }}<span class="metric-suffix">/ {{ dashboard.stats?.blog_total ?? 0 }}</span></p>
              <p class="metric-sub">AdSense 통과용 30+</p>
            </div>
            <div class="metric-card">
              <p class="metric-label">인스타 콘텐츠 재고</p>
              <p class="metric-value">{{ dashboard.instagram?.future_days ?? 0 }}<span class="metric-suffix">일</span></p>
              <p class="metric-sub">~{{ dashboard.instagram?.last_date || '—' }}</p>
            </div>
            <div class="metric-card" :class="{ warn: dashboard.system?.token_days_left !== null && dashboard.system?.token_days_left < 10 }">
              <p class="metric-label">인스타 토큰</p>
              <p class="metric-value">
                <template v-if="dashboard.system?.token_days_left !== null">
                  D-{{ dashboard.system?.token_days_left }}
                </template>
                <template v-else>—</template>
              </p>
              <p class="metric-sub">만료: {{ dashboard.system?.token_expires || '미설정' }}</p>
            </div>
          </div>

          <!-- 7일 리딩 추이 -->
          <div class="card-block">
            <h3>📊 최근 7일 리딩 추이</h3>
            <div class="bar-chart">
              <div v-for="d in dashboard.stats?.daily_readings || []" :key="d.day" class="bar-item">
                <div class="bar" :style="{ height: barHeight(d.count) + 'px' }">
                  <span class="bar-value">{{ d.count }}</span>
                </div>
                <p class="bar-label">{{ formatDay(d.day) }}</p>
              </div>
              <p v-if="!(dashboard.stats?.daily_readings || []).length" class="empty-text">데이터 없음</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 인스타 -->
      <section v-if="activeTab === 'instagram'" class="tab-content">
        <div v-if="loading.instagram" class="loading-state">로딩 중…</div>
        <div v-else-if="instagram">
          <p class="section-info">
            예정 콘텐츠 <strong>{{ instagram.total_future }}일</strong>치
            <button class="btn-mini" @click="restockNow" :disabled="restocking">
              {{ restocking ? '생성 중…' : '+ 다음 6일치 생성' }}
            </button>
          </p>
          <div class="insta-day-list">
            <div v-for="d in instagram.days" :key="d.date" class="insta-day-block">
              <h4 class="insta-day-title">
                <span>{{ d.date }}</span>
                <span class="insta-day-tag">{{ d.items?.length || 0 }} 게시물</span>
              </h4>
              <div v-if="d.items" class="insta-items">
                <div v-for="item in d.items" :key="item.mbti" class="insta-item">
                  <div class="insta-item-head">
                    <span class="mbti-pill">{{ item.mbti }}</span>
                    <span class="card-name-pill">{{ item.card_name }}</span>
                  </div>
                  <p class="insta-cover">{{ item.slides?.cover }}</p>
                </div>
              </div>
              <p v-else class="error-text">{{ d.error }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 블로그 -->
      <section v-if="activeTab === 'blog'" class="tab-content">
        <div v-if="loading.blog" class="loading-state">로딩 중…</div>
        <div v-else>
          <p class="section-info">
            전체 {{ blogPosts.length }}개 / 노출 {{ blogPublishedCount }}개
            <span class="info-sub">·  AdSense 통과 위해 30+ 권장</span>
          </p>
          <div class="blog-list">
            <div v-for="p in blogPosts" :key="p.id" class="blog-row">
              <div class="blog-row-main">
                <span class="blog-id">#{{ p.id }}</span>
                <span class="blog-cat">{{ p.category }}</span>
                <span class="blog-title">{{ p.title }}</span>
              </div>
              <div class="blog-row-right">
                <span class="blog-views">👁 {{ p.view_count }}</span>
                <label class="switch">
                  <input type="checkbox" :checked="p.published" @change="togglePost(p)" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 세션, 위기 -->
      <section v-if="activeTab === 'sessions'" class="tab-content">
        <div v-if="loading.sessions" class="loading-state">로딩 중…</div>
        <div v-else>
          <p class="section-info">
            최근 {{ sessions.length }}개 리딩
            <span v-if="crisisCount > 0" class="crisis-banner">⚠️ 위기 키워드 {{ crisisCount }}건 감지</span>
          </p>
          <div class="session-list">
            <div v-for="s in sessions" :key="s.id" class="session-row" :class="{ crisis: s.crisis }">
              <div class="session-head" @click="toggleExpand(s.id)" style="cursor: pointer;">
                <span class="session-id">#{{ s.id }}</span>
                <span class="session-time">{{ formatTime(s.timestamp) }}</span>
                <span class="session-type">{{ s.reading_type || 'basic' }}</span>
                <span v-if="s.crisis" class="crisis-tag">🚨 위기 키워드</span>
                <span class="expand-toggle">{{ expanded.has(s.id) ? '▼' : '▶' }}</span>
              </div>
              <div class="session-body">
                <p class="session-q-label">📝 질문</p>
                <p class="session-q" :class="{ collapsed: !expanded.has(s.id) }">{{ s.question || '(빈 질문)' }}</p>
                <template v-if="expanded.has(s.id)">
                  <p class="session-cards-label">🎴 뽑은 카드</p>
                  <p class="session-cards">{{ s.cards || '(없음)' }}</p>
                  <p class="session-a-label">💬 응답</p>
                  <p class="session-a">{{ s.response || '(응답 없음)' }}</p>
                </template>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const TABS = [
  { key: 'dashboard', label: '대시보드', icon: '📊' },
  { key: 'instagram', label: '인스타',   icon: '📷' },
  { key: 'blog',      label: '블로그',   icon: '📝' },
  { key: 'sessions',  label: '세션·위기', icon: '💬' },
]

const activeTab = ref('dashboard')
const dashboard = ref<any>(null)
const instagram = ref<any>(null)
const blogPosts = ref<any[]>([])
const sessions = ref<any[]>([])
const restocking = ref(false)
const expanded = ref<Set<number>>(new Set())

function toggleExpand(id: number) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
  expanded.value = new Set(expanded.value)
}

const loading = ref({
  dashboard: false,
  instagram: false,
  blog: false,
  sessions: false,
})

const todayStr = new Date().toISOString().slice(0, 10)

async function fetchJson(url: string) {
  const res = await fetch(url, { credentials: 'include' })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()
}

async function loadDashboard() {
  loading.value.dashboard = true
  try { dashboard.value = await fetchJson('/api/admin/dashboard') }
  catch (e) { console.error(e) }
  finally { loading.value.dashboard = false }
}

async function loadInstagram() {
  loading.value.instagram = true
  try { instagram.value = await fetchJson('/api/admin/instagram?limit=14') }
  catch (e) { console.error(e) }
  finally { loading.value.instagram = false }
}

async function loadBlog() {
  loading.value.blog = true
  try {
    const r = await fetchJson('/api/admin/blog')
    blogPosts.value = r.posts || []
  } catch (e) { console.error(e) }
  finally { loading.value.blog = false }
}

async function loadSessions() {
  loading.value.sessions = true
  try {
    const r = await fetchJson('/api/admin/sessions?limit=50')
    sessions.value = r.readings || []
  } catch (e) { console.error(e) }
  finally { loading.value.sessions = false }
}

async function togglePost(p: any) {
  const next = !p.published
  try {
    await fetch(`/api/admin/blog/${p.id}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ published: next }),
    })
    p.published = next
  } catch (e) {
    alert('실패: ' + e)
  }
}

async function restockNow() {
  restocking.value = true
  alert('재고 생성은 launchd가 매주 일요일 10:00에 자동 실행해요.\n수동으로 즉시 실행하려면 터미널에서:\nbash scripts/auto/restock_instagram.sh')
  restocking.value = false
}

const blogPublishedCount = computed(() => blogPosts.value.filter(p => p.published).length)
const crisisCount = computed(() => sessions.value.filter(s => s.crisis).length)

function barHeight(count: number) {
  const max = Math.max(...(dashboard.value?.stats?.daily_readings?.map((d: any) => d.count) || [1]))
  if (max === 0) return 6
  return Math.max(6, Math.round((count / max) * 120))
}

function formatDay(s: string) {
  return s.slice(5)  // YYYY-MM-DD에서 MM-DD만
}

function formatTime(s: string) {
  if (!s) return '—'
  return s.replace('T', ' ').slice(0, 16)
}

function refreshAll() {
  loadDashboard()
  loadInstagram()
  loadBlog()
  loadSessions()
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #0f0d0b;
  color: #ede4d3;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
}

.admin-header {
  background: #1a1612;
  border-bottom: 1px solid #2a2520;
  position: sticky; top: 0; z-index: 10;
}
.header-content {
  display: flex; align-items: center; justify-content: space-between;
  max-width: 1280px; margin: 0 auto;
  padding: 14px 24px;
}
.brand {
  font-size: 18px; font-weight: 700;
  color: #c9a86a;
  letter-spacing: 0.5px;
}
.header-right { display: flex; align-items: center; gap: 14px; }
.today-tag {
  font-size: 12px; color: #8a8070;
  padding: 4px 12px;
  background: #2a2520; border-radius: 999px;
}
.refresh-btn {
  background: transparent;
  border: 1px solid #2a2520;
  color: #c9a86a;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  display: flex; align-items: center; gap: 4px;
  font-family: inherit;
}
.refresh-btn:hover { background: #2a2520; }

.tab-bar {
  display: flex; gap: 2px;
  max-width: 1280px; margin: 0 auto;
  padding: 0 24px;
  border-top: 1px solid #2a2520;
  overflow-x: auto;
}
.tab-btn {
  background: transparent; border: none;
  color: #8a8070;
  padding: 14px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
  white-space: nowrap;
  font-family: inherit;
}
.tab-btn:hover { color: #ede4d3; }
.tab-btn.active {
  color: #c9a86a;
  border-bottom-color: #c9a86a;
}

.admin-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}
.tab-content { animation: fadeIn 0.25s ease; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Loading / Empty */
.loading-state {
  text-align: center; padding: 60px 0;
  color: #8a8070; font-size: 14px;
}
.empty-text {
  text-align: center; padding: 40px 0;
  color: #6a5e50; font-size: 13px;
}
.error-text {
  color: #ff6a6a; font-size: 13px;
}

/* 메트릭 카드 */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}
.metric-card {
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 14px;
  padding: 20px;
}
.metric-card.warn {
  border-color: #ff6a6a;
  background: rgba(255,106,106,0.05);
}
.metric-label {
  font-size: 12px;
  color: #8a8070;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #c9a86a;
  letter-spacing: -1px;
  line-height: 1;
}
.metric-suffix {
  font-size: 16px;
  color: #8a8070;
  font-weight: 400;
  margin-left: 4px;
}
.metric-sub {
  font-size: 11px;
  color: #6a5e50;
  margin-top: 6px;
}

/* 카드 블록 */
.card-block {
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 20px;
}
.card-block h3 {
  font-size: 15px;
  color: #ede4d3;
  margin: 0 0 16px;
  font-weight: 600;
}

/* 막대 그래프 */
.bar-chart {
  display: flex; align-items: flex-end;
  gap: 16px;
  height: 160px;
  padding: 10px 4px;
  border-bottom: 1px solid #2a2520;
}
.bar-item {
  flex: 1;
  display: flex; flex-direction: column;
  align-items: center;
  min-width: 28px;
}
.bar {
  width: 100%;
  max-width: 40px;
  background: linear-gradient(180deg, #c9a86a 0%, #8a6a4a 100%);
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: all 0.3s ease;
}
.bar-value {
  position: absolute;
  top: -22px; left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: #c9a86a;
  font-weight: 600;
}
.bar-label {
  font-size: 11px;
  color: #8a8070;
  margin-top: 8px;
}

/* 섹션 인포 */
.section-info {
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 18px;
  font-size: 14px;
  color: #ede4d3;
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.section-info strong { color: #c9a86a; }
.info-sub { color: #8a8070; font-size: 12px; }
.btn-mini {
  background: #c9a86a;
  color: #0f0d0b;
  border: none;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  margin-left: auto;
  font-family: inherit;
}
.btn-mini:hover { background: #d4b67e; }
.btn-mini:disabled { opacity: 0.5; cursor: not-allowed; }

/* 인스타 */
.insta-day-list { display: flex; flex-direction: column; gap: 16px; }
.insta-day-block {
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 12px;
  padding: 16px;
}
.insta-day-title {
  display: flex; align-items: center; justify-content: space-between;
  margin: 0 0 12px;
  font-size: 14px;
  color: #c9a86a;
  font-weight: 600;
}
.insta-day-tag {
  font-size: 11px;
  color: #8a8070;
  font-weight: 400;
  background: #0f0d0b;
  padding: 2px 8px;
  border-radius: 999px;
}
.insta-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.insta-item {
  background: #0f0d0b;
  border: 1px solid #2a2520;
  border-radius: 10px;
  padding: 12px;
}
.insta-item-head {
  display: flex; gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.mbti-pill {
  background: #c9a86a;
  color: #0f0d0b;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  letter-spacing: 0.5px;
}
.card-name-pill {
  background: #2a2520;
  color: #ede4d3;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}
.insta-cover {
  font-size: 13px;
  line-height: 1.5;
  color: #ede4d3;
  margin: 0;
}

/* 블로그 */
.blog-list { display: flex; flex-direction: column; gap: 4px; }
.blog-row {
  display: flex; align-items: center; justify-content: space-between;
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 8px;
  padding: 12px 16px;
  transition: background 0.15s ease;
}
.blog-row:hover { background: #2a2520; }
.blog-row-main {
  display: flex; align-items: center; gap: 12px;
  flex: 1; min-width: 0;
}
.blog-id {
  font-size: 11px; color: #6a5e50;
  font-family: monospace;
  min-width: 32px;
}
.blog-cat {
  background: #2a2520;
  color: #c9a86a;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  min-width: 60px;
  text-align: center;
}
.blog-title {
  font-size: 14px;
  color: #ede4d3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.blog-row-right {
  display: flex; align-items: center; gap: 16px;
}
.blog-views {
  font-size: 12px;
  color: #8a8070;
}

/* 토글 스위치 */
.switch {
  position: relative;
  display: inline-block;
  width: 40px; height: 22px;
}
.switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; inset: 0;
  background: #2a2520;
  border-radius: 999px;
  cursor: pointer;
  transition: 0.2s;
}
.slider::before {
  position: absolute;
  content: "";
  height: 16px; width: 16px;
  left: 3px; top: 3px;
  background: #ede4d3;
  border-radius: 50%;
  transition: 0.2s;
}
.switch input:checked + .slider { background: #c9a86a; }
.switch input:checked + .slider::before { transform: translateX(18px); background: #0f0d0b; }

/* 세션 */
.session-list { display: flex; flex-direction: column; gap: 8px; }
.session-row {
  background: #1a1612;
  border: 1px solid #2a2520;
  border-radius: 10px;
  padding: 14px 16px;
}
.session-row.crisis {
  border-color: #ff6a6a;
  background: rgba(255,106,106,0.05);
}
.session-head {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.session-id { font-family: monospace; color: #6a5e50; font-size: 11px; }
.session-time { font-size: 12px; color: #8a8070; }
.session-type {
  background: #2a2520;
  color: #c9a86a;
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 10px;
}
.crisis-tag {
  background: #ff6a6a;
  color: #0f0d0b;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}
.session-body { margin-top: 8px; }
.session-q-label, .session-cards-label, .session-a-label {
  font-size: 11px;
  color: #8a8070;
  letter-spacing: 0.5px;
  margin: 12px 0 4px;
}
.session-q, .session-a, .session-cards {
  font-size: 13px;
  line-height: 1.6;
  color: #ede4d3;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.session-q {
  color: #c9a86a;
  background: rgba(201,168,106,0.05);
  padding: 8px 10px;
  border-radius: 6px;
  border-left: 2px solid #c9a86a;
}
.session-q.collapsed {
  max-height: 3.6em;
  overflow: hidden;
  position: relative;
}
.session-q.collapsed::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 1.6em;
  background: linear-gradient(180deg, transparent, rgba(201,168,106,0.05));
}
.session-cards {
  color: #b8a890;
  font-style: italic;
}
.session-a {
  background: #0f0d0b;
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 2px solid #2a2520;
}
.expand-toggle {
  margin-left: auto;
  color: #8a8070;
  font-size: 11px;
}
.crisis-banner {
  background: rgba(255,106,106,0.15);
  border: 1px solid #ff6a6a;
  color: #ff6a6a;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 6px;
  margin-left: auto;
  font-size: 12px;
}

/* Mobile */
@media (max-width: 700px) {
  .header-content { padding: 12px 16px; }
  .tab-bar { padding: 0 16px; }
  .tab-btn { padding: 12px 14px; font-size: 13px; }
  .admin-main { padding: 16px; }
  .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .metric-card { padding: 14px; }
  .metric-value { font-size: 24px; }
  .blog-row-main { flex-direction: column; align-items: flex-start; gap: 4px; }
  .blog-row-right { gap: 10px; }
}
</style>
