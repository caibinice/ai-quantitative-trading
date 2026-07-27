import { expect, test } from '@playwright/test'

test('market page displays the persisted Tushare source', async ({ page }) => {
  await page.route('**/api/stocks**', (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify([
      { symbol: '600519', name: '贵州茅台', market: 'A', industry: '白酒' },
    ]),
  }))
  await page.route('**/api/market/600519/prices**', (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify([
      {
        date: '2026-07-23',
        open: 1410,
        high: 1430,
        low: 1400,
        close: 1420,
        volume: 100,
        amount: 142000,
        turnover_rate: 0.2,
        adjustment: 'qfq',
        source: 'tushare-pro',
      },
      {
        date: '2026-07-24',
        open: 1420,
        high: 1440,
        low: 1410,
        close: 1430,
        volume: 120,
        amount: 171600,
        turnover_rate: 0.25,
        adjustment: 'qfq',
        source: 'tushare-pro',
      },
    ]),
  }))
  await page.route('**/api/market/600519/financials**', (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify([
      {
        report_date: '2026-03-31',
        report_period: '一季报',
        metric_name: '净资产收益率',
        metric_value: 8.2,
        yoy: null,
        source: 'tushare-pro',
      },
    ]),
  }))

  await page.goto('market')

  await expect(page.getByText('Tushare Pro · 前复权')).toBeVisible()
  await expect(page.getByText('Tushare Pro · 报告期 2026-03-31')).toBeVisible()
})

test('live deployment exposes a synced Tushare symbol', async ({ page }) => {
  const symbol = process.env.PLAYWRIGHT_LIVE_TUSHARE_SYMBOL
  test.skip(!symbol, 'Set PLAYWRIGHT_LIVE_TUSHARE_SYMBOL for a deployed-data smoke test.')

  await page.goto('market')
  await page.locator('.market-toolbar select').selectOption(symbol)

  await expect(page.getByText('Tushare Pro · 前复权')).toBeVisible()
  await expect(page.locator('.financial-panel .source-chip')).toContainText('Tushare Pro')
})
