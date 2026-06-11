/**
 * Browser Context — manages Playwright browser instance lifecycle.
 *
 * Creates and manages a single browser instance with its context.
 * All observe and action operations use this shared context.
 * Graceful shutdown closes the browser and context cleanly.
 */

import { chromium, type Browser, type BrowserContext, type Page } from "playwright";
import type { BrowserServerConfig } from "./config.js";
import { logger } from "./logging.js";

let browser: Browser | null = null;
let context: BrowserContext | null = null;
let defaultPage: Page | null = null;

/** Initialize the Playwright browser and create a default context + page. */
export async function initBrowser(config: BrowserServerConfig): Promise<void> {
  if (browser) {
    logger.warn("Browser already initialized.");
    return;
  }

  logger.info(`Launching ${config.browserType} (headless: ${config.headless})...`);
  browser = await chromium.launch({ headless: config.headless });

  context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    userAgent: "AEGIS-BrowserServer/0.1.0",
  });

  defaultPage = await context.newPage();
  logger.info("Browser context ready.");
}

/** Get the default page. Creates one if needed. */
export async function getPage(): Promise<Page> {
  if (!context) {
    throw new Error("Browser context not initialized. Call initBrowser() first.");
  }
  if (!defaultPage || defaultPage.isClosed()) {
    defaultPage = await context.newPage();
  }
  return defaultPage;
}

/** Get the browser context. */
export function getContext(): BrowserContext {
  if (!context) {
    throw new Error("Browser context not initialized. Call initBrowser() first.");
  }
  return context;
}

/** Gracefully close the browser and release resources. */
export async function shutdownBrowser(): Promise<void> {
  logger.info("Shutting down browser...");
  if (context) {
    await context.close();
    context = null;
  }
  if (browser) {
    await browser.close();
    browser = null;
  }
  defaultPage = null;
  logger.info("Browser closed.");
}

/** Check if the browser is currently running. */
export function isBrowserAlive(): boolean {
  return browser !== null && browser.isConnected();
}
