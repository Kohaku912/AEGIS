import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: true,
    timeout: 120_000
  },
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "on-first-retry"
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1366, height: 768 } } }
  ]
});
