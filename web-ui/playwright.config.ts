import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.AEGIS_E2E_BASE_URL || "http://127.0.0.1:5173";
const useRemote = Boolean(process.env.AEGIS_E2E_BASE_URL);

export default defineConfig({
  testDir: "./tests",
  webServer: useRemote ? undefined : {
    command: "npm run dev",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: true,
    timeout: 120_000
  },
  use: {
    baseURL,
    trace: "on-first-retry"
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1366, height: 768 } } },
    { name: "android-mobile", use: { ...devices["Pixel 7"] } },
  ]
});
