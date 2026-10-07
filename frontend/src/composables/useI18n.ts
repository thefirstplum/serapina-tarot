import { useI18n as useVueI18n } from 'vue-i18n'

export function useI18n() {
  const { t, locale } = useVueI18n()

  return {
    t,
    locale,
    isKorean: () => locale.value === 'ko',
    isEnglish: () => locale.value === 'en'
  }
}
