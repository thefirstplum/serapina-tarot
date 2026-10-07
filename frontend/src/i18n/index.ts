import { createI18n } from 'vue-i18n'
import ko from './locales/ko.json'
import en from './locales/en.json'
import ja from './locales/ja.json'
import fr from './locales/fr.json'
import de from './locales/de.json'

export type MessageSchema = typeof ko
export type SupportedLocale = 'ko' | 'en' | 'ja' | 'fr' | 'de'

const i18n = createI18n<[MessageSchema], SupportedLocale>({
  legacy: false,
  locale: (localStorage.getItem('locale') as SupportedLocale) || 'ko',
  fallbackLocale: 'ko',
  messages: {
    ko,
    en,
    ja,
    fr,
    de
  }
})

export default i18n
