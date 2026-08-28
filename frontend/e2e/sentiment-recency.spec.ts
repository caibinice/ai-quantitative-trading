import { expect, test } from '@playwright/test'
import { setUiLanguage } from './language-helper'

test('sentiment radar excludes stale positive news and reflects recent negatives', async ({ page, context, baseURL }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await setUiLanguage(context, baseURL, 'zh-CN')
  const now = Date.now()
  const event = (id: number, daysAgo: number, label: string, score: number) => ({
    id,
    symbol: '601799',
    kind: 'news',
    title: `事件 ${id}`,
    source: '测试源',
    source_url: '',
    published_at: new Date(now - daysAgo * 86_400_000).toISOString(),
    label,
    score,
    confidence: 1,
    summary: '',
    rationale: '',
    model: 'test-model',
  })
  await page.route(/\/api\/sentiment\/news(?:\?.*)?$/, (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify([
      event(1, 1, '利空', -0.8),
      event(2, 21, '利好', 1),
    ]),
  }))

  await page.goto('sentiment')
  const gauge = page.locator('.sentiment-gauge')
  await expect(gauge).toContainText('近 7 日股票池情绪')
  await expect(gauge).toContainText('有效样本 1')
  await expect(gauge).toHaveAttribute('aria-label', /近 7 日情绪分 -0\./)
  await expect(page.locator('.mood-cell.positive strong')).toHaveText('0')
  await expect(page.locator('.mood-cell.negative strong')).toHaveText('1')
  await page.screenshot({ path: '../output/playwright/sentiment-recency.png', fullPage: true })
})
