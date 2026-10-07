/**
 * 위기 신호 감지 composable
 * 사용자 입력·AI 응답에서 자살·자해 신호가 보이면 안내(1393, 1577-0199) 배너 노출.
 * 오탐 방지로 명시적 키워드만 봄 ("힘들다" 정도는 감지 안 함)
 */
import { ref, computed } from 'vue'

// 배너용 키워드는 명백한 표현만 (오탐 방지)
// 백엔드는 키워드 + LLM 분류를 같이 씀. 목록은 main.py _crisis_explicit 와 맞춤
const CRISIS_KEYWORDS = [
  '자살', '자해', '리스트컷',
  '죽고 싶', '죽고싶', '뒤지고 싶', '뒤지고싶',
  '살기 싫어', '살기싫어',
  '살고 싶지 않', '살고싶지 않', '살고 싶지않', '살고싶지않',
]

// 3인칭 표현은 본인 위기가 아니라서 배너 안 띄움
const THIRD_PERSON_MARKERS = [
  '친구가', '엄마가', '아빠가', '동생이', '오빠가', '언니가',
  '그 사람이', '그사람이', '그애가', '걔가', '그녀가',
  '선배가', '후배가', '동료가', '남친이', '여친이', '남편이', '아내가',
  '아들이', '딸이', '부모님이',
]

// 한 번 닫으면 24시간 노출 안 함
const STORAGE_KEY = 'crisis_banner_dismissed_at'
const DISMISS_DURATION_MS = 24 * 60 * 60 * 1000  // 24시간

// 전역 상태 (싱글톤)
const isVisible = ref(false)
const detectedText = ref('')


function isDismissedRecently(): boolean {
  if (typeof window === 'undefined') return false
  const dismissedAt = localStorage.getItem(STORAGE_KEY)
  if (!dismissedAt) return false
  const elapsed = Date.now() - parseInt(dismissedAt, 10)
  return elapsed < DISMISS_DURATION_MS
}


function detectCrisis(text: string): boolean {
  if (!text) return false
  const lower = text.toLowerCase()
  // 친구·가족 걱정 같은 3인칭 표현은 제외
  if (THIRD_PERSON_MARKERS.some(tp => lower.includes(tp))) return false
  return CRISIS_KEYWORDS.some(kw => lower.includes(kw))
}


export function useCrisisDetection() {
  /**
   * 사용자 입력 또는 AI 응답에서 위기 신호 감지.
   * 감지되면 배너 노출. 24시간 안에 닫았으면 다시 띄우지 않음.
   */
  function checkText(text: string) {
    if (!text) return
    if (isDismissedRecently()) return
    if (detectCrisis(text)) {
      isVisible.value = true
      detectedText.value = text.slice(0, 80)
    }
  }

  function dismiss() {
    isVisible.value = false
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, Date.now().toString())
    }
  }

  function reset() {
    isVisible.value = false
    detectedText.value = ''
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  return {
    isVisible: computed(() => isVisible.value),
    detectedText: computed(() => detectedText.value),
    checkText,
    dismiss,
    reset,
  }
}
