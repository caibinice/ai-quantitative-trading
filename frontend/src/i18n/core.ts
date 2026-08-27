import englishMessages from './ui.en.json'
import japaneseMessages from './ui.ja.json'

export type Language = 'en' | 'zh-CN' | 'ja'

export const LANGUAGE_COOKIE = 'aq_language'

export const languageOptions: Array<{ value: Language; label: string }> = [
  { value: 'en', label: 'English' },
  { value: 'zh-CN', label: '简体中文' },
  { value: 'ja', label: '日本語' },
]

const messages: Record<Exclude<Language, 'zh-CN'>, Record<string, string>> = {
  en: englishMessages,
  ja: japaneseMessages,
}

function normalizeLanguage(value: string | null | undefined): Language | null {
  if (!value) return null
  const normalized = value.trim().toLowerCase()
  if (normalized === 'zh-cn' || normalized === 'zh' || normalized.startsWith('zh-')) return 'zh-CN'
  if (normalized === 'ja' || normalized.startsWith('ja-')) return 'ja'
  if (normalized === 'en' || normalized.startsWith('en-')) return 'en'
  return null
}

export function languageFromCookie(cookie: string): Language | null {
  const entry = cookie
    .split(';')
    .map((item) => item.trim())
    .find((item) => item.startsWith(`${LANGUAGE_COOKIE}=`))
  if (!entry) return null
  return normalizeLanguage(decodeURIComponent(entry.slice(LANGUAGE_COOKIE.length + 1)))
}

export function detectLanguage(
  cookie = typeof document === 'undefined' ? '' : document.cookie,
  browserLanguages = typeof navigator === 'undefined'
    ? []
    : (navigator.languages?.length ? navigator.languages : [navigator.language]),
): Language {
  const saved = languageFromCookie(cookie)
  if (saved) return saved
  for (const candidate of browserLanguages) {
    const language = normalizeLanguage(candidate)
    if (language) return language
  }
  return 'en'
}

let activeLanguage: Language = detectLanguage()

export function getLanguage(): Language {
  return activeLanguage
}

export function setActiveLanguage(language: Language): void {
  activeLanguage = language
}

export function localeForLanguage(language = activeLanguage): string {
  if (language === 'zh-CN') return 'zh-CN'
  if (language === 'ja') return 'ja-JP'
  return 'en-US'
}

export function tr(source: string, language = activeLanguage): string {
  if (!source || language === 'zh-CN') return source
  return messages[language][source] ?? source
}

export function localize(
  values: Record<Language, string>,
  variables: Record<string, string | number> = {},
  language = activeLanguage,
): string {
  return Object.entries(variables).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    values[language],
  )
}
