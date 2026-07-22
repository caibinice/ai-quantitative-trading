import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem('ai-quant-theme', 'light'))
})

test('light theme covers learning, strategy and walk-forward surfaces', async ({ page }) => {
  await page.goto('learn')
  await expect(page).toHaveTitle('学习学院 · AI 量化研究舱')
  await expect(page.locator('.market-status strong')).toHaveText('学习学院')
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  await expect(page.locator('.progress-ring > div')).toHaveCSS('background-color', 'rgb(255, 255, 255)')
  await page.screenshot({ path: '../output/playwright/light-learning.png', fullPage: true })

  await page.getByRole('link', { name: '策略实验室' }).click()
  await expect(page).toHaveTitle('策略实验室 · AI 量化研究舱')
  await expect(page.locator('.workflow-button.accent > span')).toHaveCSS('color', 'rgb(255, 255, 255)')
  await page.screenshot({ path: '../output/playwright/light-strategy.png', fullPage: true })

  await page.getByRole('link', { name: '样本外验证' }).click()
  await expect(page).toHaveTitle('样本外验证 · AI 量化研究舱')
  await expect(page.locator('.wf-layout')).toBeVisible()
  const firstRun = page.locator('.run-list button').first()
  if (await firstRun.count()) {
    await expect(firstRun).toHaveCSS('background-color', 'rgb(234, 247, 250)')
  }
  await page.screenshot({ path: '../output/playwright/light-walk-forward.png', fullPage: true })
})

test('all learning chapters expose three detailed lessons', async ({ page }) => {
  const chapterIds = [
    'market-basics',
    'quant-map',
    'project-tour',
    'python-bridge',
    'numpy-pandas',
    'market-data',
    'factor-backtest',
    'sentiment-llm',
    'walk-forward',
    'research-engineering',
    'capstone',
  ]

  for (const [chapterIndex, chapterId] of chapterIds.entries()) {
    if (chapterIndex === 0) {
      const response = await page.goto(`learn/${chapterId}`)
      expect(response?.status(), `chapter ${chapterId} should load`).toBe(200)
    } else {
      await page.evaluate((id) => {
        window.history.pushState({}, '', `/quant/learn/${id}`)
        window.dispatchEvent(new PopStateEvent('popstate'))
      }, chapterId)
    }
    await expect(page.locator('.concept-card')).toHaveCount(3)
    if (chapterId === 'market-basics') {
      await expect(page.locator('.kline-primer')).toBeVisible()
      await expect(page.locator('.textbook-section')).toHaveCount(4)
      await page.screenshot({ path: '../output/playwright/kline-textbook.png', fullPage: true })
    }
    await page.locator('.concept-card').first().click()
    await expect(page.locator('.concept-flow-node').first()).toBeVisible()
    expect(await page.locator('.concept-flow-node').count()).toBeGreaterThan(2)
    expect(await page.locator('.concept-prose > p').count()).toBeGreaterThanOrEqual(2)
    await expect(page.locator('.concept-list-card.pitfall > p')).toHaveCount(3)
    await page.waitForTimeout(200)
  }
  await page.screenshot({ path: '../output/playwright/learning-detail.png', fullPage: true })
})

test('learning sources download and automation settings are visible', async ({ page }) => {
  await page.goto('learn/quant-map')
  const downloadPromise = page.waitForEvent('download')
  await page.locator('.project-map a[download]').first().click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('README.md')

  await page.goto('sentiment')
  await expect(page.locator('.automation-panel')).toBeVisible()
  await expect(page.locator('.automation-model strong')).toHaveText('deepseek-v4-pro')
  const interval = Number(await page.locator('.automation-interval input').inputValue())
  expect(interval).toBeGreaterThanOrEqual(1)
  expect(interval).toBeLessThanOrEqual(48)
  await expect(page.locator('.automation-model small')).toContainText('备用 Key 就绪')
  await expect(page.locator('.sentiment-source-grid article')).toHaveCount(5)
  await expect(page.locator('.dedup-note')).toContainText('按相同标题合并为一个事件')
  const visibleTitles = (await page.locator('.news-copy h3').allTextContents())
    .map((title) => title.replace(/\s+/g, ' ').trim())
  expect(new Set(visibleTitles).size).toBe(visibleTitles.length)
  const positiveResult = page.locator('.sentiment-result.positive').first()
  if (await positiveResult.count()) {
    await expect(positiveResult).toHaveCSS('color', 'rgb(8, 127, 91)')
  }
  await page.screenshot({ path: '../output/playwright/sentiment-automation.png', fullPage: true })
})
