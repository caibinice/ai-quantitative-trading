import { defineConfig } from '@playwright/test'

const remoteUsername = process.env.PLAYWRIGHT_USERNAME
const remotePassword = process.env.PLAYWRIGHT_PASSWORD

export default defineConfig({
  testDir: './e2e',
  outputDir: '../output/playwright/test-results',
  timeout: 45_000,
  expect: { timeout: 8_000 },
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:5173/quant/',
    channel: 'chrome',
    httpCredentials: remoteUsername && remotePassword
      ? { username: remoteUsername, password: remotePassword }
      : undefined,
    viewport: { width: 1600, height: 1000 },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  reporter: [['list']],
})
