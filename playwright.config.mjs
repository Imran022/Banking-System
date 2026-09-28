import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: { baseURL: process.env.CAPITOL_LEDGER_URL || 'http://127.0.0.1:4173', browserName: 'chromium', headless: true },
  webServer: process.env.CAPITOL_LEDGER_URL ? undefined : { command: 'node tests/preview-server.mjs', url: 'http://127.0.0.1:4173', reuseExistingServer: true, timeout: 15000 }
});
