import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  detectLanguage,
  LANGUAGE_COOKIE,
  setActiveLanguage,
  tr,
  type Language,
} from '../i18n/core'
import { I18nContext, type I18nContextValue } from '../i18n/context'

function persistLanguage(language: Language) {
  const secure = location.protocol === 'https:' ? '; Secure' : ''
  document.cookie = `${LANGUAGE_COOKIE}=${encodeURIComponent(language)}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, updateLanguage] = useState<Language>(detectLanguage)
  setActiveLanguage(language)

  useEffect(() => {
    document.documentElement.lang = language
  }, [language])

  const value = useMemo<I18nContextValue>(() => ({
    language,
    setLanguage: (nextLanguage) => {
      setActiveLanguage(nextLanguage)
      persistLanguage(nextLanguage)
      updateLanguage(nextLanguage)
    },
    tr,
  }), [language])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}
