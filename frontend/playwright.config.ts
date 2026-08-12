import { defineConfig } from '@playwright/test'

const remoteUsername = process.env.PLAYWRIGHT_USERNAME
const remotePassword = process.env.PLAYWRIGHT_PASSWORD
const remoteBaseUrl = process.env.PLAYWRIGHT_BASE_URL

export default defineConfig({
  testDir: './e2e',
  outputDir: '../output/playwright/test-results',
  timeout: 45_000,
  expect: { timeout: 8_000 },
  use: {
    baseURL: remoteBaseUrl ?? 'http://127.0.0.1:5173/quant/',
    channel: 'chrome',
    httpCredentials: remoteUsername && remotePassword
      ? { username: remoteUsername, password: remotePassword }
      : undefined,
    viewport: { width: 1600, height: 1000 },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: remoteBaseUrl
    ? undefined
    : [
        {
          command: '..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
          cwd: '../backend',
          url: 'http://127.0.0.1:8000/api/health',
          reuseExistingServer: true,
          timeout: 60_000,
        },
        {
          command: 'npm run dev -- --host 127.0.0.1 --port 5173',
          cwd: '.',
          url: 'http://127.0.0.1:5173/quant/',
          reuseExistingServer: true,
          timeout: 60_000,
        },
      ],
  reporter: [['list']],
})
