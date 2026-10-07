<template>
  <div class="followup-loading">
    <!-- 상단: 회전 메시지 + 스피너 -->
    <div class="loading-header">
      <div class="loading-sparkles">
        <span class="sparkle" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.25}s` }">✦</span>
      </div>
      <p class="loading-message">{{ currentMessage }}</p>
    </div>

    <!-- 진행 점 -->
    <div class="progress-dots">
      <span class="dot" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.2}s` }"></span>
    </div>

    <!-- MBTI × 타로 상식 카드 -->
    <div class="knowledge-card" :class="{ 'visible': showKnowledge }">
      <div class="knowledge-header">
        <span class="knowledge-icon">{{ currentKnowledge.icon }}</span>
        <span class="knowledge-label">{{ currentKnowledge.label }}</span>
      </div>
      <p class="knowledge-text">{{ currentKnowledge.text }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  userMbti?: string
}>()

const messages = [
  '더 깊은 결을 들여다보는 중…',
  '카드 사이의 이야기를 잇는 중…',
  '네 마음에 맞춰 풀어내는 중…',
  '진짜 신호와 잡음을 가르는 중…',
  '이번엔 더 자세히 정리하는 중…',
]
const currentMessageIndex = ref(0)
const currentMessage = computed(() => messages[currentMessageIndex.value])

const MBTI_TAROT_KNOWLEDGE: { mbti?: string; icon: string; label: string; text: string }[] = [
  { mbti: 'INFP', icon: '💧', label: 'INFP × 컵', text: 'INFP에게 컵 카드는 가장 잘 맞는 슈트야. 감정 신호를 남보다 빨리 잡아내거든.' },
  { mbti: 'INFJ', icon: '🌙', label: 'INFJ × 달', text: 'INFJ는 달 카드를 자주 마주칠 거야. 안 보이는 걸 알아채는 직관이 강하니까.' },
  { mbti: 'INTP', icon: '⚔️', label: 'INTP × 검', text: 'INTP에게 검 카드는 익숙한 도구야. 다만 그 칼이 자기를 향할 때가 있어.' },
  { mbti: 'INTJ', icon: '🔮', label: 'INTJ × 마법사', text: 'INTJ에게 마법사 카드는 자기 거울이야. 머릿속 그림을 현실로 만드는 능력이 강하거든.' },
  { mbti: 'ISFP', icon: '🌿', label: 'ISFP × 펜타클', text: 'ISFP는 펜타클 카드와 잘 맞아. 순간의 결과 감각을 진심으로 느끼는 사람이니까.' },
  { mbti: 'ISFJ', icon: '🏛️', label: 'ISFJ × 황제', text: 'ISFJ에게 황제 카드는 보호의 의미야. 묵묵히 곁에서 지켜주는 사람이라서 그래.' },
  { mbti: 'ISTP', icon: '🏇', label: 'ISTP × 전차', text: 'ISTP는 전차 카드와 잘 어울려. 말없이 정확하게 움직이는 사람이거든.' },
  { mbti: 'ISTJ', icon: '💎', label: 'ISTJ × 펜타클', text: 'ISTJ는 펜타클의 견실함을 닮았어. 화려하진 않지만 무너지지 않는 사람이지.' },
  { mbti: 'ENFP', icon: '🔥', label: 'ENFP × 완드', text: 'ENFP는 완드 카드와 통해. 시작을 두려워하지 않는 에너지를 가졌거든.' },
  { mbti: 'ENFJ', icon: '☀️', label: 'ENFJ × 태양', text: 'ENFJ는 태양 카드처럼 주변을 밝게 만들어. 그 빛, 자기 자신한테도 비춰줘.' },
  { mbti: 'ENTP', icon: '✨', label: 'ENTP × 마법사', text: 'ENTP에게 마법사 카드는 자연스러워. 도구를 새 방식으로 조합하는 데 강하니까.' },
  { mbti: 'ENTJ', icon: '👑', label: 'ENTJ × 황제', text: 'ENTJ는 황제 카드가 잘 맞아. 결단과 비전을 갖춘 사람이거든.' },
  { mbti: 'ESFP', icon: '🎉', label: 'ESFP × 완드', text: 'ESFP는 완드 카드와 통해. 지금 이 순간을 사는 활기가 강하니까.' },
  { mbti: 'ESFJ', icon: '🤝', label: 'ESFJ × 연인', text: 'ESFJ는 연인 카드와 잘 어울려. 관계 속 균형을 만드는 능력이 강하거든.' },
  { mbti: 'ESTP', icon: '⚡', label: 'ESTP × 전차', text: 'ESTP는 전차 카드처럼 망설임이 없어. 생각보다 행동이 빠른 사람이거든.' },
  { mbti: 'ESTJ', icon: '🏛️', label: 'ESTJ × 황제', text: 'ESTJ에게 황제는 자기 거울이야. 질서와 체계로 세상을 단단히 세우는 사람이니까.' },
  { icon: '🌟', label: '타로 상식', text: '메이저 아르카나는 총 22장이야. 바보부터 세계까지 인생의 큰 흐름을 그려.' },
  { icon: '💞', label: '타로 상식', text: '역방향 카드는 나쁜 게 아니야. 다른 시각으로 보라는 신호일 뿐이야.' },
  { icon: '🎴', label: '타로 상식', text: '타로 슈트는 4개야. 컵·완드·검·펜타클이 마음·열정·생각·현실을 의미해.' },
  { icon: '🌙', label: '타로 상식', text: '달 카드는 막막함의 카드야. 답이 안 보일 땐 무리하지 말고 천천히 가.' },
  { icon: '☀️', label: '타로 상식', text: '태양 카드는 가장 좋은 카드 중 하나야. 망설일 거 없이 빛으로 나가도 돼.' },
  { icon: '🔮', label: '타로 상식', text: '여사제는 직관의 카드야. 머리로 따지지 말고 마음이 먼저 안 답을 따라가.' },
]

const knowledgeIndex = ref(0)
const showKnowledge = ref(false)
const currentKnowledge = computed(() => MBTI_TAROT_KNOWLEDGE[knowledgeIndex.value % MBTI_TAROT_KNOWLEDGE.length])

const pickStartingKnowledge = () => {
  if (props.userMbti) {
    const idx = MBTI_TAROT_KNOWLEDGE.findIndex(k => k.mbti === props.userMbti)
    if (idx >= 0) return idx
  }
  return Math.floor(Math.random() * MBTI_TAROT_KNOWLEDGE.length)
}

let messageInterval: ReturnType<typeof setInterval> | null = null
let knowledgeInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  // 메시지 회전 (3초마다)
  messageInterval = setInterval(() => {
    currentMessageIndex.value = (currentMessageIndex.value + 1) % messages.length
  }, 3000)

  // 타로 상식 카드: 1.2초 후 등장, 5초마다 회전
  knowledgeIndex.value = pickStartingKnowledge()
  setTimeout(() => { showKnowledge.value = true }, 800)
  knowledgeInterval = setInterval(() => {
    showKnowledge.value = false
    setTimeout(() => {
      knowledgeIndex.value = (knowledgeIndex.value + 1) % MBTI_TAROT_KNOWLEDGE.length
      showKnowledge.value = true
    }, 250)
  }, 5000)
})

onUnmounted(() => {
  if (messageInterval) clearInterval(messageInterval)
  if (knowledgeInterval) clearInterval(knowledgeInterval)
})
</script>

<style scoped>
.followup-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 16px;
  background: linear-gradient(180deg, rgba(244, 63, 94, 0.04), transparent);
  border-radius: 16px;
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.loading-sparkles {
  display: flex;
  gap: 6px;
}

.sparkle {
  color: var(--primary-color);
  font-size: 0.85rem;
  animation: sparkleFloat 1.8s ease-in-out infinite;
}

@keyframes sparkleFloat {
  0%, 100% { opacity: 0.3; transform: translateY(0) scale(0.8); }
  50% { opacity: 1; transform: translateY(-4px) scale(1.15); }
}

.loading-message {
  font-size: 0.95rem;
  color: var(--text-secondary, #6B6B6B);
  margin: 0;
  text-align: center;
  transition: opacity 0.3s ease;
}

.progress-dots {
  display: flex;
  gap: 5px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-color);
  opacity: 0.4;
  animation: dotPulse 1.4s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.1); }
}

.knowledge-card {
  width: 100%;
  max-width: 380px;
  margin-top: 4px;
  padding: 14px 16px;
  background: var(--card-bg, #fff);
  border-radius: 12px;
  border: 1px solid var(--border-color, rgba(0,0,0,0.06));
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  opacity: 0;
  transform: translateY(6px);
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.knowledge-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.knowledge-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.knowledge-icon {
  font-size: 1rem;
}

.knowledge-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--primary-color);
  letter-spacing: 0.02em;
}

.knowledge-text {
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--text-primary, #2a2a2a);
  margin: 0;
}

@media (max-width: 600px) {
  .followup-loading {
    padding: 16px 12px;
  }
  .knowledge-text {
    font-size: 0.8rem;
  }
}
</style>
