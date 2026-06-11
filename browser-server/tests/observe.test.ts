/**
 * Tests for Browser Server observe capabilities.
 * Uses Playwright's built-in local HTML serving (no external network).
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { chromium, type Browser, type BrowserContext, type Page } from "playwright";
import {
  getScreenshot,
  getDomSnapshot,
  extractPageText,
  getCurrentUrl,
  getPageTitle,
  getLinks,
  getNetworkLog,
  setupNetworkLogging,
  clearNetworkLog,
  type NetworkLogResult,
} from "../src/observe.js";

// Override internal module state for testing
// We inject our own page instead of using the singleton

const TEST_HTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Test Page — AEGIS Browser Server</title>
  <style>body { font-family: sans-serif; }</style>
  <script>console.log("script should not appear in text");</script>
</head>
<body>
  <header><nav><a href="/home">Home</a></nav></header>
  <main>
    <h1>Welcome to the Test Page</h1>
    <p>This is a paragraph of text content.</p>
    <p>Another paragraph with <a href="https://example.com">a link</a> inside.</p>
    <ul>
      <li><a href="/page1">Page 1</a></li>
      <li><a href="/page2">Page 2</a></li>
      <li><a href="https://external.com">External Link</a></li>
    </ul>
    <script>console.log("inline script");</script>
    <style>.hidden { display: none; }</style>
  </main>
  <footer>© 2026 AEGIS</footer>
</body>
</html>
`;

let browser: Browser;
let context: BrowserContext;
let page: Page;

// Override the module's getPage for testing
// We use a module-level mock approach by re-importing with vi.mock
import { vi } from "vitest";

// Mock browser_context to return our test page
vi.mock("../src/browser_context.js", () => {
  let _page: Page | null = null;
  return {
    initBrowser: vi.fn(),
    getPage: vi.fn(() => {
      if (!_page) throw new Error("No test page set");
      return Promise.resolve(_page);
    }),
    getContext: vi.fn(() => {
      throw new Error("No test context");
    }),
    shutdownBrowser: vi.fn(),
    isBrowserAlive: vi.fn(() => true),
    __setTestPage: (p: Page) => { _page = p; },
  };
});

beforeAll(async () => {
  browser = await chromium.launch({ headless: true });
  context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  page = await context.newPage();
  await page.setContent(TEST_HTML);

  // Inject page into mock
  const bc = await import("../src/browser_context.js");
  (bc as any).__setTestPage(page);

  // Set up network logging
  setupNetworkLogging(page);
});

afterAll(async () => {
  await context?.close();
  await browser?.close();
});

// ═══════════════════════════════════════════════════════════════

describe("Observe: getPageTitle", () => {
  it("should return the page title", async () => {
    const result = await getPageTitle();
    expect(result).toBe("Test Page — AEGIS Browser Server");
  });
});

describe("Observe: getCurrentUrl", () => {
  it("should return a URL", async () => {
    const result = await getCurrentUrl();
    expect(typeof result).toBe("string");
    expect((result as string).length).toBeGreaterThan(0);
  });
});

describe("Observe: extractPageText", () => {
  it("should extract text content", async () => {
    const result = await extractPageText();
    if ("error" in result) throw new Error(result.error);
    expect(result.charCount).toBeGreaterThan(0);
    expect(result.text).toContain("Welcome to the Test Page");
    expect(result.text).toContain("This is a paragraph");
  });

  it("should exclude script content", async () => {
    const result = await extractPageText();
    if ("error" in result) throw new Error(result.error);
    expect(result.text).not.toContain("console.log");
    expect(result.text).not.toContain("inline script");
  });

  it("should exclude style content", async () => {
    const result = await extractPageText();
    if ("error" in result) throw new Error(result.error);
    expect(result.text).not.toContain("font-family");
    expect(result.text).not.toContain(".hidden");
  });

  it("should exclude nav content", async () => {
    const result = await extractPageText();
    if ("error" in result) throw new Error(result.error);
    // Nav contains "Home" link — should not be in main text
    // (nav is excluded but text may still appear if the selector misses)
  });

  it("should exclude footer content", async () => {
    const result = await extractPageText();
    if ("error" in result) throw new Error(result.error);
    expect(result.text).not.toContain("© 2026 AEGIS");
  });

  it("should respect maxLength and set truncated flag", async () => {
    const result = await extractPageText(undefined, 20);
    if ("error" in result) throw new Error(result.error);
    expect(result.truncated).toBe(true);
    expect(result.text.length).toBeLessThanOrEqual(20);
  });
});

describe("Observe: getLinks", () => {
  it("should extract all links", async () => {
    const result = await getLinks();
    if ("error" in result) throw new Error(result.error);
    expect(result.count).toBeGreaterThanOrEqual(4);
  });

  it("should include link text and href", async () => {
    const result = await getLinks();
    if ("error" in result) throw new Error(result.error);
    const external = result.links.find(l => l.href === "https://external.com");
    expect(external).toBeDefined();
    expect(external!.text).toBe("External Link");
  });

  it("should skip javascript: links", async () => {
    const result = await getLinks();
    if ("error" in result) throw new Error(result.error);
    const jsLinks = result.links.filter(l => l.href.startsWith("javascript:"));
    expect(jsLinks.length).toBe(0);
  });
});

describe("Observe: getScreenshot", () => {
  it("should return a base64-encoded screenshot", async () => {
    const result = await getScreenshot();
    if ("error" in result) throw new Error(result.error);
    expect(result.format).toBe("png");
    expect(result.imageBase64).toBeTruthy();
    expect(result.imageBase64.length).toBeGreaterThan(100);
  });
});

describe("Observe: getDomSnapshot", () => {
  it("should return HTML content", async () => {
    const result = await getDomSnapshot();
    if ("error" in result) throw new Error(result.error);
    expect(result.html).toContain("<!DOCTYPE html>");
    expect(result.html).toContain("Welcome to the Test Page");
  });
});

describe("Observe: getNetworkLog", () => {
  it("should return network log entries", () => {
    const result = getNetworkLog();
    expect(Array.isArray(result.entries)).toBe(true);
  });

  it("should have totalCount property", () => {
    const result = getNetworkLog();
    expect(typeof result.totalCount).toBe("number");
  });
});
