import type { BrowserContext } from '@playwright/test'

export async function setUiLanguage(
  context: BrowserContext,
  baseURL: string | undefined,
  language: 'en' | 'zh-CN' | 'ja',
): Promise<void> {
  const origin = new URL(baseURL ?? 'http://127.0.0.1:5173/quant/').origin
  await context.addCookies([{ name: 'aq_language', value: language, url: origin }])
}
