/**
 * Safety level definitions for Browser Server capabilities.
 * These mirror the proto SafetyLevel enum in protos/aegis/common.proto.
 *
 * LEVEL_0_READ      = 1 — Observe only, no side effects
 * LEVEL_1_SAFE_ACT  = 2 — Non-destructive, reversible
 * LEVEL_2_APPROVAL  = 3 — Requires user approval
 * LEVEL_3_RESTRICTED = 4 — May be prohibited entirely
 */

export enum SafetyLevel {
  LEVEL_0_READ = 1,
  LEVEL_1_SAFE_ACT = 2,
  LEVEL_2_APPROVAL = 3,
  LEVEL_3_RESTRICTED = 4,
}

export interface CapabilityDefinition {
  id: string;
  name: string;
  description: string;
  safetyLevel: SafetyLevel;
  requiresApproval: boolean;
  sideEffects: string[];
  tags: string[];
  timeoutMs: number;
  version: string;
}

/** All capabilities that the Browser Server registers with AEGIS Core. */
export const BROWSER_CAPABILITIES: CapabilityDefinition[] = [
  {
    id: "browser.open_page",
    name: "Open Web Page",
    description: "Navigate the browser to a specified URL and wait for page load.",
    safetyLevel: SafetyLevel.LEVEL_1_SAFE_ACT,
    requiresApproval: false,
    sideEffects: ["sends HTTP request", "executes page JavaScript"],
    tags: ["navigation", "browser", "web", "risk:safe_action"],
    timeoutMs: 30000,
    version: "0.1.0",
  },
  {
    id: "browser.get_dom_snapshot",
    name: "Get DOM Snapshot",
    description: "Capture the current page's DOM as HTML text.",
    safetyLevel: SafetyLevel.LEVEL_0_READ,
    requiresApproval: false,
    sideEffects: [],
    tags: ["dom", "html", "observe", "risk:read_only"],
    timeoutMs: 10000,
    version: "0.1.0",
  },
  {
    id: "browser.get_screenshot",
    name: "Get Screenshot",
    description: "Capture a screenshot of the current page or a specific element.",
    safetyLevel: SafetyLevel.LEVEL_0_READ,
    requiresApproval: false,
    sideEffects: [],
    tags: ["screenshot", "observe", "risk:read_only"],
    timeoutMs: 15000,
    version: "0.1.0",
  },
  {
    id: "browser.extract_page_text",
    name: "Extract Page Text",
    description: "Extract the main textual content from the current page for LLM processing.",
    safetyLevel: SafetyLevel.LEVEL_0_READ,
    requiresApproval: false,
    sideEffects: [],
    tags: ["extract", "text", "observe", "llm", "risk:read_only"],
    timeoutMs: 15000,
    version: "0.1.0",
  },
  {
    id: "browser.click",
    name: "Click Element",
    description: "Click on a DOM element identified by CSS selector or coordinates.",
    safetyLevel: SafetyLevel.LEVEL_1_SAFE_ACT,
    requiresApproval: false,
    sideEffects: ["may trigger navigation", "may modify page state"],
    tags: ["click", "interaction", "risk:safe_action"],
    timeoutMs: 10000,
    version: "0.1.0",
  },
  {
    id: "browser.fill_form",
    name: "Fill Form",
    description: "Fill form fields on the current page. Requires approval for sensitive targets.",
    safetyLevel: SafetyLevel.LEVEL_1_SAFE_ACT,
    requiresApproval: false,
    sideEffects: ["modifies form state", "may submit data"],
    tags: ["form", "input", "interaction", "risk:safe_action"],
    timeoutMs: 15000,
    version: "0.1.0",
  },
  {
    id: "browser.download_file",
    name: "Download File",
    description: "Download a file from a URL to the server. Requires approval.",
    safetyLevel: SafetyLevel.LEVEL_2_APPROVAL,
    requiresApproval: true,
    sideEffects: ["writes to filesystem", "consumes disk space"],
    tags: ["download", "file", "risk:approval_required"],
    timeoutMs: 60000,
    version: "0.1.0",
  },
];

/**
 * Capabilities that are explicitly NOT implemented:
 * - browser.post_sns (LEVEL_3_RESTRICTED — SNS posting is forbidden)
 * - browser.send_dm (LEVEL_3_RESTRICTED — DM sending is forbidden)
 * - browser.purchase (LEVEL_3_RESTRICTED — purchases are forbidden)
 * - browser.captcha_bypass (LEVEL_3_RESTRICTED — forbidden by PolicyEngine)
 * - browser.fill_credentials (LEVEL_3_RESTRICTED — password automation forbidden)
 */
