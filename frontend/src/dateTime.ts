import { localeForLanguage, type Language } from './i18n'

const BEIJING_TIME_ZONE = 'Asia/Shanghai'

function parseApiDateTime(value: string): Date {
  // Old internal timestamps were naive UTC. New API responses always include
  // either Z or an explicit offset; this fallback keeps cached responses safe.
  const hasZone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
  return new Date(hasZone ? value : `${value}Z`)
}

export function formatBeijingDateTime(value: string | null | undefined, language?: Language): string {
  if (!value) return '—'
  return parseApiDateTime(value).toLocaleString(localeForLanguage(language), {
    timeZone: BEIJING_TIME_ZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

export function formatBeijingDate(value: string, language?: Language): string {
  return parseApiDateTime(value).toLocaleDateString(localeForLanguage(language), {
    timeZone: BEIJING_TIME_ZONE,
    month: '2-digit',
    day: '2-digit',
  })
}

export function formatBeijingTime(value: string, language?: Language): string {
  return parseApiDateTime(value).toLocaleTimeString(localeForLanguage(language), {
    timeZone: BEIJING_TIME_ZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

export function beijingDateInput(offsetDays = 0): string {
  const value = new Date(Date.now() + offsetDays * 86_400_000)
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: BEIJING_TIME_ZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(value)
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((part) => part.type === type)?.value ?? ''
  return `${get('year')}-${get('month')}-${get('day')}`
}
