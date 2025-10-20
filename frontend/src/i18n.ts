import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import es from './locales/es.json'

export type MessageSchema = typeof en

export type SupportedLocale = 'en' | 'es'

const messages: Record<SupportedLocale, MessageSchema> = {
  en,
  es
}

// Get user's preferred language from localStorage or browser
const getDefaultLocale = (): SupportedLocale => {
  const stored = localStorage.getItem('locale')
  if (stored && (stored === 'en' || stored === 'es')) {
    return stored
  }

  const browserLang = navigator.language.split('-')[0]
  if (browserLang === 'en' || browserLang === 'es') {
    return browserLang
  }

  return 'en'
}

const i18n = createI18n<[MessageSchema], SupportedLocale>({
  legacy: false, // Use Composition API mode
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages,
  globalInjection: true
})

export default i18n
