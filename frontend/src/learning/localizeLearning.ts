import englishTranslations from '../i18n/learning.en.json'
import japaneseTranslations from '../i18n/learning.ja.json'
import { getLanguage, type Language } from '../i18n'

const translations: Record<Exclude<Language, 'zh-CN'>, Record<string, string>> = {
  en: englishTranslations,
  ja: japaneseTranslations,
}

const codeLikeKeys = new Set([
  'code',
  'command',
  'datasetPath',
  'file',
  'path',
  'scriptPath',
  'snippet',
  'url',
])

const caches: Record<Exclude<Language, 'zh-CN'>, WeakMap<object, unknown>> = {
  en: new WeakMap(),
  ja: new WeakMap(),
}

export function localizeLearningText(source: string, language = getLanguage()): string {
  if (language === 'zh-CN') return source
  return translations[language][source] ?? source
}

export function localizeLearning<T>(value: T, language = getLanguage(), key = ''): T {
  if (language === 'zh-CN' || value === null || value === undefined) return value
  if (typeof value === 'string') {
    return (codeLikeKeys.has(key) ? value : localizeLearningText(value, language)) as T
  }
  if (typeof value !== 'object') return value

  const cache = caches[language]
  const cached = cache.get(value)
  if (cached) return cached as T

  if (Array.isArray(value)) {
    const localized: unknown[] = []
    cache.set(value, localized)
    value.forEach((item) => localized.push(localizeLearning(item, language, key)))
    return localized as T
  }

  const localized: Record<string, unknown> = {}
  cache.set(value, localized)
  Object.entries(value as Record<string, unknown>).forEach(([entryKey, entryValue]) => {
    localized[entryKey] = localizeLearning(entryValue, language, entryKey)
  })
  return localized as T
}
