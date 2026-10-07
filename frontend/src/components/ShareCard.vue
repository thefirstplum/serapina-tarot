<template>
  <v-dialog v-model="dialogModel" max-width="400px" class="share-dialog">
    <v-card class="share-card">
      <div class="share-header">
        <h2>{{ t('share.title') }}</h2>
        <v-btn icon variant="text" @click="closeDialog" size="small">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-card-text class="share-body">
        <!-- 미리보기 카드 -->
        <div ref="cardRef" class="preview-card">
          <div class="preview-brand">
            <img src="/icons/symbol-64.png" class="brand-icon" alt="세라피나" width="28" height="28" />
            <span class="brand-name">{{ t('share.brandName') }}</span>
          </div>
          <div class="preview-cards">
            <span v-for="card in cardNames" :key="card" class="card-tag">{{ card }}</span>
          </div>
          <p class="preview-reading">{{ truncatedReading }}</p>
          <div class="preview-footer">
            <span class="preview-url">serapina.kr</span>
            <span class="preview-date">{{ today }}</span>
          </div>
        </div>

        <!-- 공유 버튼들 -->
        <div class="share-actions">
          <v-btn
            v-if="canNativeShare"
            color="primary"
            variant="flat"
            block
            rounded="lg"
            @click="nativeShare"
          >
            <v-icon start>mdi-share-variant</v-icon>
            {{ t('share.nativeShareButton') }}
          </v-btn>
          <v-btn
            variant="outlined"
            block
            rounded="lg"
            @click="copyToClipboard"
          >
            <v-icon start>mdi-content-copy</v-icon>
            {{ t('share.copyButton') }}
          </v-btn>
          <v-btn
            variant="outlined"
            block
            rounded="lg"
            color="amber"
            @click="downloadImage"
          >
            <v-icon start>mdi-download</v-icon>
            {{ t('share.downloadButton') }}
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import html2canvas from 'html2canvas'
import { trackShareClicked, trackShareCompleted } from '@/utils/analytics'

const { t } = useI18n()

interface Props {
  modelValue: boolean
  reading: string
  cards: string[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const cardRef = ref<HTMLDivElement>()

const dialogModel = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const today = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })

const cardNames = computed(() => props.cards.slice(0, 5))

const cleanReading = computed(() => {
  let text = props.reading || ''
  // 마크다운 태그 제거
  text = text.replace(/#{1,3}\s*/g, '')           // ### ## #
  text = text.replace(/\*\*(.*?)\*\*/g, '$1')     // **bold**
  text = text.replace(/\*(.*?)\*/g, '$1')          // *italic*
  text = text.replace(/^[-*]{3,}\s*$/gm, '')       // --- ***
  text = text.replace(/<\/?strong>/g, '')           // <strong> tags
  text = text.replace(/<br\s*\/?>/g, '\n')          // <br> 줄바꿈
  text = text.trim()
  return text
})

const truncatedReading = computed(() => {
  const text = cleanReading.value
  if (!text) return ''
  // 첫 200자까지, 문장 단위로 자르기
  if (text.length <= 200) return text
  const cut = text.slice(0, 200)
  const lastPeriod = Math.max(cut.lastIndexOf('.'), cut.lastIndexOf('!'), cut.lastIndexOf('?'), cut.lastIndexOf('~'))
  if (lastPeriod > 100) return cut.slice(0, lastPeriod + 1)
  return cut + '...'
})

const canNativeShare = computed(() => !!navigator.share)

const shareText = computed(() => {
  return t('share.shareText', {
    cards: props.cards.join(', '),
    reading: cleanReading.value.slice(0, 300)
  })
})

function closeDialog() {
  dialogModel.value = false
}

async function nativeShare() {
  trackShareClicked('native')
  try {
    const previewEl = document.querySelector('.preview-card') as HTMLElement
    let files: File[] = []
    if (previewEl) {
      try {
        const canvas = await html2canvas(previewEl, { scale: 2, backgroundColor: 'var(--bg-primary)', useCORS: true })
        const blob = await new Promise<Blob>((resolve) => canvas.toBlob((b) => resolve(b!), 'image/png'))
        files = [new File([blob], 'serapina-tarot.png', { type: 'image/png' })]
      } catch { /* ignore, share without image */ }
    }
    await navigator.share({
      title: t('share.shareTitle'),
      text: shareText.value,
      url: 'https://serapina.kr',
      ...(files.length && navigator.canShare?.({ files }) ? { files } : {}),
    })
    trackShareCompleted('native')
  } catch {
    // user cancelled or not supported
  }
}

async function copyToClipboard() {
  trackShareClicked('copy')
  try {
    await navigator.clipboard.writeText(shareText.value)
    trackShareCompleted('copy')
    alert(t('share.copiedMessage'))
  } catch {
    const ta = document.createElement('textarea')
    ta.value = shareText.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    alert(t('share.copiedMessage'))
  }
}

async function downloadImage() {
  trackShareClicked('download')
  try {
    const previewEl = document.querySelector('.preview-card') as HTMLElement
    if (!previewEl) return
    const canvas = await html2canvas(previewEl, {
      scale: 2,
      backgroundColor: 'var(--bg-primary)',
      useCORS: true,
    })
    const link = document.createElement('a')
    link.download = 'serapina-tarot-reading.png'
    link.href = canvas.toDataURL('image/png')
    link.click()
    trackShareCompleted('download')
  } catch {
    // fallback to text copy
    await copyToClipboard()
  }
}
</script>

<style scoped>
.share-card {
  border-radius: 20px !important;
  background: var(--card-bg, var(--bg-primary)) !important;
  overflow: hidden;
}

.share-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--card-bg);
}

.share-header h2 {
  color: var(--text-primary, var(--text-primary));
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
}

.share-body {
  padding: 16px 20px !important;
}

.preview-card {
  background: linear-gradient(135deg, #2a1b4e 0%, var(--bg-primary) 50%, #162040 100%);
  border-radius: 16px;
  padding: 24px 20px;
  margin-bottom: 16px;
  border: 1px solid var(--border-color);
}

.preview-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.brand-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 6px;
  vertical-align: middle;
}

.brand-name {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.preview-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}

.card-tag {
  background: rgba(255, 193, 7, 0.15);
  color: var(--accent-yellow);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 8px;
}

.preview-reading {
  color: var(--text-primary);
  font-size: 0.85rem;
  line-height: 1.6;
  margin-bottom: 14px;
}

.preview-footer {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--card-bg);
  padding-top: 10px;
}

.preview-url {
  color: rgba(156, 89, 182, 0.8);
  font-size: 0.75rem;
  font-weight: 600;
}

.preview-date {
  color: var(--border-color);
  font-size: 0.7rem;
}

.share-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
