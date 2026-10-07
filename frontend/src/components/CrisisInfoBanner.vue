<template>
  <Transition name="crisis-banner">
    <div v-if="isVisible" class="crisis-banner" role="alert">
      <div class="crisis-inner">
        <div class="crisis-icon-area">
          <span class="crisis-icon">🤍</span>
        </div>
        <div class="crisis-content">
          <p class="crisis-title">혼자 끙끙대지 마. 들어줄 사람이 더 있어.</p>
          <p class="crisis-desc">
            지금 마음이 너무 무거우면 아래 번호로 한번 연락해봐.
            전문가가 진짜 잘 들어줄 거야.
          </p>
          <div class="crisis-hotlines">
            <a href="tel:1393" class="crisis-hotline">
              <span class="hotline-num">📞 1393</span>
              <span class="hotline-label">자살예방상담</span>
            </a>
            <a href="tel:1577-0199" class="crisis-hotline">
              <span class="hotline-num">📞 1577-0199</span>
              <span class="hotline-label">정신건강위기상담</span>
            </a>
          </div>
        </div>
        <button class="crisis-dismiss" @click="dismiss" aria-label="안내 닫기">
          ✕
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useCrisisDetection } from '@/composables/useCrisisDetection'

const { isVisible, dismiss } = useCrisisDetection()
</script>

<style scoped>
.crisis-banner {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  width: 92%;
  max-width: 520px;
  background: linear-gradient(180deg, #fff, #fff5f5);
  border: 2px solid #f43f5e;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(244, 63, 94, 0.2),
              0 2px 8px rgba(0, 0, 0, 0.1);
}

.crisis-inner {
  display: flex;
  gap: 12px;
  padding: 16px 14px 16px 18px;
  align-items: flex-start;
}

.crisis-icon-area {
  flex-shrink: 0;
  padding-top: 2px;
}

.crisis-icon {
  font-size: 1.6rem;
}

.crisis-content {
  flex: 1;
  min-width: 0;
}

.crisis-title {
  font-size: 0.98rem;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.crisis-desc {
  font-size: 0.85rem;
  color: #4b5563;
  margin: 0 0 12px 0;
  line-height: 1.55;
}

.crisis-hotlines {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.crisis-hotline {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #fff;
  border: 1.5px solid #f43f5e;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.15s;
  color: inherit;
}

.crisis-hotline:hover {
  background: #fff5f5;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(244, 63, 94, 0.15);
}

.hotline-num {
  font-size: 0.95rem;
  font-weight: 800;
  color: #f43f5e;
}

.hotline-label {
  font-size: 0.78rem;
  color: #6b7280;
}

.crisis-dismiss {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.15s;
}

.crisis-dismiss:hover {
  background: #f3f4f6;
  color: #374151;
}

/* 다크 모드 */
:global(.dark-theme) .crisis-banner {
  background: linear-gradient(180deg, #1e293b, #2a1f24);
  border-color: #f43f5e;
}

:global(.dark-theme) .crisis-title {
  color: #f3f4f6;
}

:global(.dark-theme) .crisis-desc {
  color: #d1d5db;
}

:global(.dark-theme) .crisis-hotline {
  background: #0f172a;
}

:global(.dark-theme) .crisis-hotline:hover {
  background: #1a1a2e;
}

/* Transition */
.crisis-banner-enter-active,
.crisis-banner-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.crisis-banner-enter-from,
.crisis-banner-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}

@media (max-width: 600px) {
  .crisis-banner {
    bottom: 12px;
    width: 94%;
  }

  .crisis-title {
    font-size: 0.92rem;
  }

  .crisis-desc {
    font-size: 0.8rem;
  }
}
</style>
