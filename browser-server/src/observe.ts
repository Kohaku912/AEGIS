/**
 * Observe operations — read-only browser capabilities.
 * All methods are LEVEL_0_READ: no side effects.
 */

import { getPage } from "./browser_context.js";
import { logger } from "./logging.js";

export interface ScreenshotResult {
  imageBase64: string;
  width: number;
  height: number;
  format: "png" | "jpeg";
}

/** Capture a screenshot of the current page or a specific element. */
export async function getScreenshot(
  selector?: string,
  format: "png" | "jpeg" = "png",
  quality?: number,
): Promise<ScreenshotResult> {
  const page = await getPage();

  if (selector) {
    const element = page.locator(selector);
    const buffer = await element.screenshot({ type: format, quality });
    return {
      imageBase64: buffer.toString("base64"),
      width: 0,
      height: 0,
      format,
    };
  }

  const buffer = await page.screenshot({ type: format, quality, fullPage: true });
  const viewport = page.viewportSize();
  return {
    imageBase64: buffer.toString("base64"),
    width: viewport?.width ?? 0,
    height: viewport?.height ?? 0,
    format,
  };
}

export interface DomSnapshotResult {
  html: string;
}

/** Get the full DOM HTML of the current page or a specific element. */
export async function getDomSnapshot(selector?: string): Promise<DomSnapshotResult> {
  const page = await getPage();
  if (selector) {
    const html = await page.locator(selector).innerHTML();
    return { html };
  }
  const html = await page.content();
  return { html };
}

export interface PageTextResult {
  text: string;
  charCount: number;
  truncated: boolean;
}

/** Extract the main text content from the current page. */
export async function extractPageText(
  selector?: string,
  maxLength = 50000,
): Promise<PageTextResult> {
  const page = await getPage();
  let text: string;

  if (selector) {
    text = (await page.locator(selector).innerText()) || "";
  } else {
    text = (await page.innerText("body")) || "";
  }

  const truncated = text.length > maxLength;
  if (truncated) {
    text = text.slice(0, maxLength);
  }

  return { text, charCount: text.length, truncated };
}

export interface NetworkEntry {
  url: string;
  method: string;
  statusCode: number;
  mimeType: string;
  sizeBytes: number;
  durationMs: number;
}

/** Get the network request log for the current page. */
export async function getNetworkLog(maxEntries = 50): Promise<NetworkEntry[]> {
  // Playwright doesn't directly expose network log after the fact without setting up listeners.
  // This is a skeleton — in production, we'd set up route interception at page creation time.
  logger.debug("Network log retrieval is a skeleton — returning empty list.");
  return [];
}
