/**
 * Action operations — browser interaction capabilities.
 * LEVEL_1_SAFE_ACT or LEVEL_2_APPROVAL depending on the operation.
 * SNS posting, DM sending, purchases are explicitly NOT implemented.
 */

import { getPage } from "./browser_context.js";
import { logger } from "./logging.js";

export interface OpenPageResult {
  title: string;
  finalUrl: string;
  statusCode: number;
}

/** Navigate to a URL. LEVEL_1_SAFE_ACT. */
export async function openPage(
  url: string,
  waitUntil: "load" | "domcontentloaded" | "networkidle" = "networkidle",
  timeoutMs = 30000,
): Promise<OpenPageResult> {
  const page = await getPage();
  const response = await page.goto(url, { waitUntil, timeout: timeoutMs });

  return {
    title: await page.title(),
    finalUrl: page.url(),
    statusCode: response?.status() ?? 0,
  };
}

export interface ClickResult {
  navigatedUrl?: string;
}

/** Click on an element by CSS selector or coordinates. LEVEL_1_SAFE_ACT. */
export async function click(
  options: { selector?: string; x?: number; y?: number; button?: "left" | "right" | "middle"; doubleClick?: boolean },
): Promise<ClickResult> {
  const page = await getPage();
  let navigatedUrl: string | undefined;

  if (options.selector) {
    const navPromise = page.waitForNavigation({ timeout: 5000 }).catch(() => undefined);
    await page.locator(options.selector).click({
      button: options.button || "left",
      clickCount: options.doubleClick ? 2 : 1,
    });
    const nav = await navPromise;
    if (nav) navigatedUrl = nav.url();
  } else if (options.x !== undefined && options.y !== undefined) {
    await page.mouse.click(options.x, options.y, {
      button: options.button || "left",
      clickCount: options.doubleClick ? 2 : 1,
    });
  }

  return { navigatedUrl };
}

export interface FillFormResult {
  fieldsFilled: number;
  submitted: boolean;
}

/** Fill form fields. LEVEL_1_SAFE_ACT (LEVEL_2_APPROVAL for sensitive targets). */
export async function fillForm(
  fields: Array<{ selector: string; value: string; type?: string }>,
  submit = false,
): Promise<FillFormResult> {
  const page = await getPage();
  let filled = 0;

  for (const field of fields) {
    await page.locator(field.selector).fill(field.value);
    filled++;
  }

  if (submit) {
    // Submit the form — actual submission is a placeholder
    logger.warn("Form submit is a skeleton — not actually submitting to remote.");
  }

  return { fieldsFilled: filled, submitted: submit };
}

export interface DownloadResult {
  savedPath: string;
  sizeBytes: number;
}

/** Download a file from a URL. LEVEL_2_APPROVAL. */
export async function downloadFile(
  url: string,
  _savePath?: string,
): Promise<DownloadResult> {
  const page = await getPage();

  // Start download
  const [download] = await Promise.all([
    page.waitForEvent("download", { timeout: 30000 }),
    page.goto(url),
  ]);

  const path = _savePath || `/tmp/${download.suggestedFilename()}`;
  await download.saveAs(path);

  return {
    savedPath: path,
    sizeBytes: 0, // Playwright doesn't expose file size after save
  };
}

/**
 * NOT IMPLEMENTED — these are Level 3 restricted or explicitly forbidden.
 *
 * - postSns(): LEVEL_3_RESTRICTED
 * - sendDm(): LEVEL_3_RESTRICTED
 * - purchase(): LEVEL_3_RESTRICTED
 * - captchaBypass(): LEVEL_3_RESTRICTED + forbidden by PolicyEngine
 * - fillCredentials(): LEVEL_3_RESTRICTED
 */
