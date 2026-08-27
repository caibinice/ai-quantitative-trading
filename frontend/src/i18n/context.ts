import { createContext, useContext } from 'react'
import type { Language } from './core'
import { tr } from './core'

export interface I18nContextValue {
  language: Language
  setLanguage: (language: Language) => void
  tr: typeof tr
}

export const I18nContext = createContext<I18nContextValue | null>(null)

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext)
  if (!context) throw new Error('useI18n must be used within I18nProvider')
  return context
}
