import { expect, test } from '@playwright/test'
import { setUiLanguage } from './language-helper'

const phoneViewports = [
  { name: 'compact Android', width: 360, height: 800 },
  { name: 'iPhone Pro', width: 393, height: 852 },
  { name: 'iPhone Pro Max', width: 430, height: 932 },
  { name: 'classic iPhone Pro', width: 375, height: 812 },
  { name: 'iQOO class Android', width: 412, height: 915 },
]

for (const language of ['en', 'zh-CN', 'ja'] as const) {
  test(`${language} mobile header stays aligned on mainstream phone widths`, async ({ browser, baseURL }) => {
    test.setTimeout(120_000)
    const root = baseURL ?? 'http://127.0.0.1:5173/quant/'
    for (const viewport of phoneViewports) {
      const context = await browser.newContext({ viewport })
      await setUiLanguage(context, baseURL, language)
      const page = await context.newPage()
      await page.goto(root)
      await expect(page.locator('.topbar')).toBeVisible()

      const layout = await page.locator('.topbar').evaluate((topbar) => {
        const box = (selector: string) => {
          const rect = topbar.querySelector(selector)!.getBoundingClientRect()
          return { left: rect.left, right: rect.right, centerY: rect.top + rect.height / 2 }
        }
        const rootElement = document.documentElement
        return {
          menu: box('.menu-trigger'),
          title: box('.market-status'),
          actions: box('.topbar-actions'),
          clientWidth: rootElement.clientWidth,
          scrollWidth: rootElement.scrollWidth,
          selectAppearance: getComputedStyle(topbar.querySelector('.language-switcher select')!).appearance,
        }
      })

      expect(layout.menu.right, `${language} ${viewport.name}: menu/title overlap`).toBeLessThanOrEqual(layout.title.left + 1)
      expect(layout.title.right, `${language} ${viewport.name}: title/actions overlap`).toBeLessThanOrEqual(layout.actions.left + 1)
      expect(Math.abs(layout.menu.centerY - layout.title.centerY), `${language} ${viewport.name}: title vertical alignment`).toBeLessThanOrEqual(1)
      expect(Math.abs(layout.actions.centerY - layout.title.centerY), `${language} ${viewport.name}: actions vertical alignment`).toBeLessThanOrEqual(1)
      expect(layout.scrollWidth, `${language} ${viewport.name}: horizontal overflow`).toBeLessThanOrEqual(layout.clientWidth + 1)
      expect(layout.selectAppearance).toBe('none')
      if (language === 'zh-CN') {
        await page.screenshot({ path: `../output/playwright/mobile-header-${viewport.width}.png` })
      }
      await context.close()
    }
  })
}
