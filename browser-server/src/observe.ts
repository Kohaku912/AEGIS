/**
 * Observe operations — read-only browser capabilities.
 * All methods are LEVEL_0_READ: no side effects.
 *
 * Capabilities implemented:
 *   browser.get_screenshot, browser.get_dom_snapshot, browser.extract_page_text,
 *   browser.get_current_url, browser.get_page_title, browser.get_links,
 *   browser.get_network_log
 */

import { getPage, getContext } from "./browser_context.js";
import { logger } from "./logging.js";

// ═══════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════

export interface BrowserError {
  error: string;
  code: string;
  detail?: string;
}

export interface ScreenshotResult {
  imageBase64: string;
  width: number;
  height: number;
  format: "png" | "jpeg";
}

export interface DomSnapshotResult {
  html: string;
}

export interface PageTextResult {
  text: string;
  charCount: number;
  truncated: boolean;
}

export interface PageLinksResult {
  links: Array<{ href: string; text: string }>;
  count: number;
}

export interface NetworkEntry {
  url: string;
  method: string;
  statusCode: number;
  mimeType: string;
  sizeBytes: number;
  durationMs: number;
}

export interface NetworkLogResult {
  entries: NetworkEntry[];
  totalCount: number;
}

/** Structured error factory */
export function browserError(error: string, code = "UNKNOWN", detail?: string): BrowserError {
  return { error, code, detail };
}

// ═══════════════════════════════════════════════════════════════
// Screenshot
// ═══════════════════════════════════════════════════════════════

export async function getScreenshot(
  selector?: string,
  format: "png" | "jpeg" = "png",
  quality?: number,
  timeoutMs = 15000,
): Promise<ScreenshotResult | BrowserError> {
  try {
    const page = await getPage();

    const buffer = await (async () => {
      if (selector) {
        const element = page.locator(selector);
        return element.screenshot({ type: format, quality, timeout: timeoutMs });
      }
      return page.screenshot({ type: format, quality, fullPage: true, timeout: timeoutMs });
    })();

    const viewport = page.viewportSize();
    return {
      imageBase64: buffer.toString("base64"),
      width: viewport?.width ?? 0,
      height: viewport?.height ?? 0,
      format,
    };
  } catch (err) {
    logger.error("Screenshot failed", { error: String(err) });
    return browserError(String(err), "SCREENSHOT_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// DOM Snapshot
// ═══════════════════════════════════════════════════════════════

export async function getDomSnapshot(selector?: string): Promise<DomSnapshotResult | BrowserError> {
  try {
    const page = await getPage();
    const html = selector
      ? await page.locator(selector).innerHTML()
      : await page.content();
    return { html };
  } catch (err) {
    logger.error("DOM snapshot failed", { error: String(err) });
    return browserError(String(err), "DOM_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// Page Text Extraction
// ═══════════════════════════════════════════════════════════════

/** CSS selectors for elements to exclude from text extraction. */
const EXCLUDE_SELECTORS = [
  "script", "style", "noscript",
  "nav", "footer", "header",
  '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
];

export async function extractPageText(
  selector?: string,
  maxLength = 50000,
): Promise<PageTextResult | BrowserError> {
  try {
    const page = await getPage();

    // Clone the body to avoid mutating the live page
    const bodyText = await page.evaluate((excludeSelectors) => {
      const body = document.body.cloneNode(true) as HTMLElement;
      // Remove excluded elements
      for (const sel of excludeSelectors) {
        for (const el of body.querySelectorAll(sel)) {
          el.remove();
        }
      }
      return body.innerText || "";
    }, EXCLUDE_SELECTORS);

    let text = bodyText
      .replace(/\n{3,}/g, "\n\n")   // Collapse multiple blank lines
      .trim();

    if (selector) {
      // If a selector is specified, extract only from that element (already cleaned)
      const elText = await page.evaluate(
        (sel) => document.querySelector(sel)?.textContent || "",
        selector,
      );
      text = elText.replace(/\n{3,}/g, "\n\n").trim();
    }

    const truncated = text.length > maxLength;
    if (truncated) {
      text = text.slice(0, maxLength);
    }

    return { text, charCount: text.length, truncated };
  } catch (err) {
    logger.error("Text extraction failed", { error: String(err) });
    return browserError(String(err), "TEXT_EXTRACT_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// Current URL
// ═══════════════════════════════════════════════════════════════

export async function getCurrentUrl(): Promise<string | BrowserError> {
  try {
    const page = await getPage();
    return page.url();
  } catch (err) {
    logger.error("getCurrentUrl failed", { error: String(err) });
    return browserError(String(err), "URL_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// Page Title
// ═══════════════════════════════════════════════════════════════

export async function getPageTitle(): Promise<string | BrowserError> {
  try {
    const page = await getPage();
    return await page.title();
  } catch (err) {
    logger.error("getPageTitle failed", { error: String(err) });
    return browserError(String(err), "TITLE_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// Page Links
// ═══════════════════════════════════════════════════════════════

export async function getLinks(maxLinks = 200): Promise<PageLinksResult | BrowserError> {
  try {
    const page = await getPage();
    const links = await page.evaluate((max) => {
      const anchors = document.querySelectorAll("a[href]");
      const result: Array<{ href: string; text: string }> = [];
      for (let i = 0; i < Math.min(anchors.length, max); i++) {
        const a = anchors[i];
        const href = a.getAttribute("href") || "";
        const text = (a.textContent || "").trim().slice(0, 200);
        if (href && !href.startsWith("javascript:")) {
          result.push({ href, text });
        }
      }
      return result;
    }, maxLinks);

    return { links, count: links.length };
  } catch (err) {
    logger.error("getLinks failed", { error: String(err) });
    return browserError(String(err), "LINKS_ERROR");
  }
}

// ═══════════════════════════════════════════════════════════════
// Network Log — with sensitive header masking
// ═══════════════════════════════════════════════════════════════

/** Headers whose values must be masked in network logs. */
const SENSITIVE_HEADERS = new Set([
  "authorization", "cookie", "set-cookie",
  "x-api-key", "x-auth-token", "proxy-authorization",
  "access-token", "refresh-token",
]);

/** Accumulated network log (populated by setupNetworkLogging). */
let _networkLog: NetworkEntry[] = [];

/** Initialize network request/response logging on a new page. */
export function setupNetworkLogging(page: import("playwright").Page): void {
  _networkLog = [];

  page.on("request", (request) => {
    // Mask sensitive headers before logging
    const maskedHeaders: Record<string, string> = {};
    for (const [key, value] of Object.entries(request.headers())) {
      maskedHeaders[key] = SENSITIVE_HEADERS.has(key.toLowerCase())
        ? "[REDACTED]"
        : value;
    }

    _networkLog.push({
      url: request.url(),
      method: request.method(),
      statusCode: 0,
      mimeType: "",
      sizeBytes: 0,
      durationMs: 0,
    });
  });

  page.on("response", (response) => {
    // Find matching entry and update
    for (let i = _networkLog.length - 1; i >= 0; i--) {
      if (_networkLog[i].url === response.url() && _networkLog[i].statusCode === 0) {
        _networkLog[i] = {
          ..._networkLog[i],
          statusCode: response.status(),
          mimeType: response.headers()["content-type"] || "",
          sizeBytes: parseInt(response.headers()["content-length"] || "0", 10),
        };
        break;
      }
    }
  });
}

/** Get the accumulated network log. */
export function getNetworkLog(maxEntries = 50): NetworkLogResult {
  const entries = _networkLog.slice(-maxEntries);
  return { entries, totalCount: _networkLog.length };
}

/** Clear the network log. */
export function clearNetworkLog(): void {
  _networkLog = [];
}

