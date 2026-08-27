import { expect, test } from '@playwright/test'
import { setUiLanguage } from './language-helper'

test.describe('automatic language selection', () => {
  test.describe('unsupported browser locale', () => {
    test.use({ locale: 'fr-FR' })

    test('falls back to English', async ({ page }) => {
      await page.goto('')
      await expect(page.locator('html')).toHaveAttribute('lang', 'en')
      await expect(page.locator('.market-status strong')).toHaveText('Research Overview')
      await expect(page).toHaveTitle('Research Overview · AI Quant Research Cockpit')
      await expect(page.locator('.language-switcher select')).toHaveValue('en')
    })
  })

  test.describe('Japanese browser locale', () => {
    test.use({ locale: 'ja-JP' })

    test('selects Japanese and localizes learning content', async ({ page }) => {
      await page.goto('learn/market-basics')
      await expect(page.locator('html')).toHaveAttribute('lang', 'ja')
      await expect(page.locator('.market-status strong')).toHaveText('ラーニングアカデミー')
      await expect(page.locator('.chapter-hero h1')).toHaveText('株式とローソク足の基礎')
      await expect(page.locator('.teaching-candle').first()).toContainText('陽線の実体')
      await expect(page.locator('.language-switcher select')).toHaveValue('ja')
    })
  })

  test.describe('Chinese browser locale', () => {
    test.use({ locale: 'zh-CN' })

    test('keeps the existing Simplified Chinese interface', async ({ page }) => {
      await page.goto('learn/market-basics')
      await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN')
      await expect(page.locator('.market-status strong')).toHaveText('学习学院')
      await expect(page.locator('.chapter-hero h1')).toHaveText('股票与 K 线零基础')
    })
  })
})

test('a manual selection is saved in a cookie and restored on reload', async ({ page, context }) => {
  await page.goto('')
  await expect(page.locator('.language-switcher select')).toHaveValue('en')

  await page.locator('.language-switcher select').selectOption('ja')
  await expect(page.locator('html')).toHaveAttribute('lang', 'ja')
  await expect(page.locator('.market-status strong')).toHaveText('研究概要')
  await expect.poll(async () => (await context.cookies()).find((cookie) => cookie.name === 'aq_language')?.value).toBe('ja')

  await page.reload()
  await expect(page.locator('.language-switcher select')).toHaveValue('ja')
  await expect(page).toHaveTitle('研究概要 · AIクオンツ・リサーチ・コックピット')
})

test.describe('saved language priority', () => {
  test.use({ locale: 'ja-JP' })

  test('the cookie overrides the browser locale', async ({ page, context, baseURL }) => {
    await setUiLanguage(context, baseURL, 'zh-CN')
    await page.goto('')
    await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN')
    await expect(page.locator('.market-status strong')).toHaveText('研究总览')
  })
})

test.describe('translated layouts', () => {
  for (const language of ['en', 'zh-CN', 'ja'] as const) {
    test(`${language} fits desktop and mobile widths`, async ({ browser, baseURL }) => {
      test.setTimeout(150_000)
      const root = baseURL ?? 'http://127.0.0.1:5173/quant/'
      for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
        const context = await browser.newContext({ viewport })
        await setUiLanguage(context, baseURL, language)
        const page = await context.newPage()
        for (const route of ['learn', 'learn/market-basics', 'market', 'strategy', 'tasks']) {
          await page.goto(new URL(route, root).toString())
          await expect(page.locator(route === 'learn/market-basics' ? '.chapter-page' : '.page-header')).toBeVisible()
          await expect(page.locator('.language-switcher select')).toBeVisible()
          const dimensions = await page.evaluate(() => ({
            clientWidth: document.documentElement.clientWidth,
            scrollWidth: document.documentElement.scrollWidth,
          }))
          expect(dimensions.scrollWidth, `${language} ${viewport.width}px ${route}`).toBeLessThanOrEqual(dimensions.clientWidth + 1)
          if (route === 'learn/market-basics') {
            await page.screenshot({ path: `../output/playwright/i18n-${language}-${viewport.width}.png`, fullPage: viewport.width > 400 })
          }
        }
        await context.close()
      }
    })
  }
})
