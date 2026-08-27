import { expect, test } from '@playwright/test'
import { setUiLanguage } from './language-helper'

test.beforeEach(async ({ page, context, baseURL }) => {
  await setUiLanguage(context, baseURL, 'zh-CN')
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
  test.setTimeout(120_000)
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

  for (const chapterId of chapterIds) {
    await test.step(`chapter ${chapterId}`, async () => {
      const response = await page.goto(`learn/${chapterId}`)
      expect(response?.status(), `chapter ${chapterId} should load`).toBe(200)
      await expect(page.locator('.concept-card')).toHaveCount(3)
      if (chapterId === 'market-basics') {
        await expect(page.locator('.kline-primer')).toBeVisible()
        await expect(page.locator('.textbook-section')).toHaveCount(4)
        await page.screenshot({ path: '../output/playwright/kline-textbook.png', fullPage: true })
      }
      for (let conceptIndex = 0; conceptIndex < 3; conceptIndex += 1) {
        const detailResponse = await page.goto(`learn/${chapterId}/concepts/${conceptIndex}`)
        expect(detailResponse?.status()).toBe(200)
        await expect(page.locator('.concept-flow-node').first()).toBeVisible()
        expect(await page.locator('.concept-flow-node').count()).toBeGreaterThan(2)
        expect(await page.locator('.concept-prose > p').count()).toBeGreaterThanOrEqual(2)
        await expect(page.locator('.beginner-compass')).toBeVisible()
        await expect(page.locator('.pitfall-detail')).toHaveCount(3)
        expect(await page.locator('.guided-lab-step').count()).toBeGreaterThanOrEqual(4)
        expect(await page.locator('.code-walkthrough article').count()).toBeGreaterThanOrEqual(3)
        expect(await page.locator('.public-reading-grid a').count()).toBeGreaterThanOrEqual(2)
        await expect(page.locator('.lab-downloads a').first()).toHaveAttribute('href', /learning\/files\/learning\/datasets/)
      }
    })
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
  await expect(page.locator('.automation-panel')).toHaveCount(0)
  await expect(page.locator('.sentiment-source-grid article')).toHaveCount(5)
  await expect(page.locator('.dedup-note')).toContainText('按相同标题合并为一个事件')
  const visibleTitles = (await page.locator('.news-copy h3').allTextContents())
    .map((title) => title.replace(/\s+/g, ' ').trim())
  expect(new Set(visibleTitles).size).toBe(visibleTitles.length)
  const positiveResult = page.locator('.sentiment-result.positive').first()
  if (await positiveResult.count()) {
    await expect(positiveResult).toHaveCSS('color', 'rgb(8, 127, 91)')
  }

  await page.goto('tasks')
  await expect(page.locator('.automation-panel')).toBeVisible()
  await expect(page.locator('.automation-model strong')).toHaveText('deepseek-v4-flash')
  const interval = Number(await page.locator('.automation-interval input').inputValue())
  expect(interval).toBeGreaterThanOrEqual(1)
  expect(interval).toBeLessThanOrEqual(48)
  await expect(page.locator('.automation-model small')).toContainText('备用 Key 就绪')
  await expect(page.getByRole('button', { name: '立即执行全流程' })).toBeVisible()
  await expect(page.locator('.quick-task-note')).toContainText('彼此不会自动串联')
  await page.screenshot({ path: '../output/playwright/tasks-automation.png', fullPage: true })
})
