import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem('ai-quant-theme', 'light'))
})

test('desktop typography remains readable across learning and dense research pages', async ({ page }) => {
  await page.goto('learn/market-basics')

  await expectFontSizeAtLeast(page.locator('.sidebar nav a').first(), 15)
  await expectFontSizeAtLeast(page.locator('.textbook-section p').first(), 14)
  await expectFontSizeAtLeast(page.locator('.guide-terms p').first(), 11)

  await navigateClientSide(page, 'strategy')
  await expectFontSizeAtLeast(page.locator('.field > span').first(), 12)
  await expectFontSizeAtLeast(page.locator('.workflow-button small').first(), 11)

  await navigateClientSide(page, 'tasks')
  await expectFontSizeAtLeast(page.locator('th').first(), 11)
  const firstCell = page.locator('td').first()
  if (await firstCell.count()) {
    await expectFontSizeAtLeast(firstCell, 13)
  }
  await expectNoDocumentOverflow(page)
  await page.screenshot({ path: '../output/playwright/readable-desktop-tasks.png', fullPage: true })
})

test.describe('mobile readability', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('learning, strategy and tasks fit a phone without shrinking the text', async ({ page }) => {
    await page.goto('learn/market-basics')

    await expectFontSizeAtLeast(page.locator('.textbook-section p').first(), 14)
    await expectFontSizeAtLeast(page.locator('.chapter-hero p').first(), 14)
    await expectNoDocumentOverflow(page)
    await page.screenshot({ path: '../output/playwright/readable-mobile-learning.png', fullPage: false })

    await navigateClientSide(page, 'strategy')
    await expectFontSizeAtLeast(page.locator('.field > span').first(), 12)
    await expectNoDocumentOverflow(page)
    await page.screenshot({ path: '../output/playwright/readable-mobile-strategy.png', fullPage: false })

    await navigateClientSide(page, 'tasks')
    await expectFontSizeAtLeast(page.locator('th').first(), 11)
    await expectNoDocumentOverflow(page)
    await page.screenshot({ path: '../output/playwright/readable-mobile-tasks.png', fullPage: false })
  })
})

async function navigateClientSide(
  page: import('@playwright/test').Page,
  route: string,
): Promise<void> {
  await page.evaluate((nextRoute) => {
    window.history.pushState({}, '', `/quant/${nextRoute}`)
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, route)
  await expect(page.locator('.page-header')).toBeVisible()
}

async function expectFontSizeAtLeast(
  locator: import('@playwright/test').Locator,
  minimum: number,
): Promise<void> {
  const size = await locator.evaluate((element) => Number.parseFloat(getComputedStyle(element).fontSize))
  expect(size).toBeGreaterThanOrEqual(minimum)
}

async function expectNoDocumentOverflow(page: import('@playwright/test').Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }))
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth + 1)
}
