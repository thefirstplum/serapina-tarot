<template>
  <!-- 링크프라이스 카테고리별 제휴 광고
       질문 카테고리에 맞춰 노출하되 직설 매칭(연애 질문에 데이팅 광고)은 피하고
       셀프케어·돌봄 쪽 우선 -->
  <div class="linkprice-block" v-if="enabled">
    <!-- 광고 직전 위로 멘트 (친구 톤) -->
    <div class="comfort-line">{{ ad.comfort }}</div>

    <div class="ad-label">{{ ad.label }}</div>

    <!-- 머천트 카드 그리드 -->
    <div class="merchant-grid">
      <a
        v-for="m in ad.merchants"
        :key="m.id"
        :href="buildUrl(m.id)"
        target="_blank"
        rel="noopener sponsored"
        class="merchant-card"
        @click="trackClick(m)"
      >
        <span class="merchant-emoji">{{ m.emoji }}</span>
        <span class="merchant-name">{{ m.name }}</span>
        <span class="merchant-desc">{{ m.desc }}</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  category?: 'love' | 'family' | 'career' | 'money' | 'self' | 'daily'
  sensitive?: boolean   // 펫로스·위기 케이스는 광고 자제
}

const props = withDefaults(defineProps<Props>(), {
  category: 'daily',
  sensitive: false,
})

// 링크프라이스 어필리에이트 ID
const AFFILIATE_ID = 'A100704705'

// 링크 ID, 기본 0000 (머천트 기본 페이지 추적)
// 머천트별 캠페인 ID 따로 받으면 m별로 override 가능
const buildUrl = (merchantId: string, linkId: string = '0000') =>
  `https://click.linkprice.com/click.php?m=${merchantId}&a=${AFFILIATE_ID}&l=${linkId}`

const enabled = computed(() => !props.sensitive)

// 광고 클릭 트래킹 (구글 애널리틱스)
const trackClick = (m: { id: string; name: string }) => {
  if (typeof (window as any).gtag === 'function') {
    ;(window as any).gtag('event', 'linkprice_click', {
      merchant_id: m.id,
      merchant_name: m.name,
      category: props.category,
    })
  }
}

interface Merchant { id: string; name: string; emoji: string; desc: string }

// 카테고리별 멘트·머천트
const ADS: Record<string, {
  label: string
  comfort: string
  merchants: Merchant[]
}> = {
  // 짝사랑·이별·권태기: 셀프케어 위로
  love: {
    label: '💕 오늘의 너에게 작은 위로 한 스푼',
    comfort: '오늘 마음이 무거웠지. 너 자신한테 작은 선물 하나 어때?',
    merchants: [
      { id: 'clubclio',   name: '클리오',       emoji: '💄', desc: '오늘은 좀 예쁜 입술로' },
      { id: 'yes24',      name: 'YES24',        emoji: '📚', desc: '마음 풀어주는 책 한 권' },
      { id: 'cjbrand',    name: 'CJ더마켓',     emoji: '🍰', desc: '디저트로 위로받기' },
      { id: 'myrealtrip', name: '마이리얼트립', emoji: '✈️', desc: '주말에 짧게 떠나볼까' },
    ],
  },

  // 가족 갈등·소진: 거리두기, 자기 돌봄
  family: {
    label: '🌿 가족 안에서 지친 너에게 잠깐 쉼',
    comfort: '가족이라 더 깊이 상처받지. 오늘은 너부터 챙겨봐.',
    merchants: [
      { id: 'clubclio',   name: '클리오',       emoji: '🛁', desc: '오늘은 너 위해 작게라도' },
      { id: 'yes24',      name: 'YES24',        emoji: '📓', desc: '거리감 배우는 책 한 권' },
      { id: 'cjbrand',    name: 'CJ더마켓',     emoji: '🍵', desc: '달콤한 한 입으로 풀기' },
      { id: 'myrealtrip', name: '마이리얼트립', emoji: '✈️', desc: '잠깐 거리 두는 시간' },
    ],
  },

  // 이직·면접·창업: 새 출발 무드
  career: {
    label: '✨ 새 출발하는 너를 응원하는 작은 선물',
    comfort: '한 걸음 떼는 게 무겁지. 새 시작에 어울리는 거 하나 챙겨봐.',
    merchants: [
      { id: 'yes24',      name: 'YES24',        emoji: '📘', desc: '결심을 책으로 시작' },
      { id: 'myrealtrip', name: '마이리얼트립', emoji: '🌏', desc: '머리 식히는 짧은 여행' },
      { id: 'arket',      name: 'ARKET',        emoji: '👔', desc: '면접·새 출발 룩' },
      { id: 'udemy',      name: 'Udemy',        emoji: '💻', desc: '실력 한 단계 올리기' },
    ],
  },

  // 빚·저축·투자: 금융은 직접 매칭해도 괜찮음
  money: {
    label: '🌿 오늘 하루도 잘 챙기는 너에게',
    comfort: '돈 생각하느라 머리 무거웠지. 잠깐 너 자신도 챙겨봐.',
    merchants: [
      { id: 'mycredit1', name: 'NICE지키미', emoji: '🔐', desc: '무료 신용조회' },
      { id: 'allcredit', name: '올크레딧',   emoji: '💳', desc: '내 신용점수 확인' },
      { id: 'yes24',     name: 'YES24',      emoji: '📕', desc: '돈 공부 시작하기' },
      { id: 'gmarket',   name: 'G마켓',      emoji: '🛒', desc: '알뜰 쇼핑 한 번에' },
    ],
  },

  // 자존감·번아웃·외모: 셀프케어 (클릭률 제일 높음)
  self: {
    label: '🌷 오늘은 너를 위한 작은 선물 하나',
    comfort: '너 자신한테 너무 인색했지? 오늘은 너 위해 작게라도.',
    merchants: [
      { id: 'clubclio', name: '클리오',   emoji: '💅', desc: '오늘 너의 컬러' },
      { id: 'iherb',    name: '아이허브', emoji: '💊', desc: '몸부터 챙기기' },
      { id: 'yes24',    name: 'YES24',    emoji: '📓', desc: '나를 채우는 책' },
      { id: 'arket',    name: 'ARKET',    emoji: '🧥', desc: '나에게 선물하는 옷' },
    ],
  },

  // 가족·친구·일상: 돌봄 소비
  daily: {
    label: '🍀 소중한 사람들과 함께하는 하루',
    comfort: '주변 챙기느라 너도 고생 많았지. 작은 거 하나라도 편하게.',
    merchants: [
      { id: 'cjbrand',  name: 'CJ더마켓', emoji: '🍱', desc: '부모님 식사 챙기기' },
      { id: 'pulmuone', name: '풀무원',   emoji: '🥦', desc: '식탁 든든하게' },
      { id: 'soomgo',   name: '숨고',     emoji: '🔧', desc: '집 손볼 거 한 번에' },
      { id: 'iherb',    name: '아이허브', emoji: '💊', desc: '온 가족 영양제' },
    ],
  },
}

const ad = computed(() => ADS[props.category] || ADS.daily)
</script>

<style scoped>
.linkprice-block {
  margin: 32px auto 24px;
  max-width: 720px;
  padding: 20px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--card-bg, transparent);
  text-align: center;
}

.comfort-line {
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.5;
  font-weight: 500;
}

.ad-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
  font-weight: 600;
  opacity: 0.85;
}

.merchant-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

@media (max-width: 600px) {
  .merchant-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.merchant-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 14px 8px;
  border-radius: 10px;
  background: var(--card-bg-alt, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  cursor: pointer;
}

.merchant-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.merchant-emoji {
  font-size: 1.6rem;
  line-height: 1;
}

.merchant-name {
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 4px;
}

.merchant-desc {
  font-size: 0.7rem;
  color: var(--text-secondary);
  opacity: 0.8;
  line-height: 1.3;
}

/* repeat(2, 1fr) 위에서 600px 이하 처리 */
</style>
