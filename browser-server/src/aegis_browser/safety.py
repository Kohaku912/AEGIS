"""Safety level definitions for Browser Server capabilities.

All capabilities are registered with AEGIS Core's ToolBroker,
which enforces PolicyEngine checks before execution.

Dangerous operations (SNS, purchases, credential access, CAPTCHA bypass)
are structurally blocked — either declared as LEVEL_3_RESTRICTED or
excluded from registration entirely.
"""

from __future__ import annotations

from enum import IntEnum


class SafetyLevel(IntEnum):
    LEVEL_0_READ = 1
    LEVEL_1_SAFE_ACT = 2
    LEVEL_2_APPROVAL = 3
    LEVEL_3_RESTRICTED = 4


# ── Registered capabilities ──────────────────────────────────

CAPABILITIES = {
    "browser.open_page": {
        "name": "Open Web Page",
        "description": "Navigate browser to a URL. Returns page title and status.",
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": ["sends HTTP request", "executes page JavaScript"],
        "timeout_ms": 30000,
        "tags": ["browser", "navigation", "web"],
    },
    "browser.extract_page_text": {
        "name": "Extract Page Text",
        "description": "Extract main textual content from the current page. Excludes scripts, styles, nav, and footer.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 15000,
        "tags": ["browser", "extract", "text", "observe"],
    },
    "browser.get_screenshot": {
        "name": "Page Screenshot",
        "description": "Capture a screenshot of the current page.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 10000,
        "tags": ["browser", "screenshot", "observe"],
    },
    "browser.get_current_url": {
        "name": "Get Current URL",
        "description": "Return the current page URL.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 3000,
        "tags": ["browser", "url", "observe"],
    },
    "browser.get_page_title": {
        "name": "Get Page Title",
        "description": "Return the HTML title of the current page.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 3000,
        "tags": ["browser", "title", "observe"],
    },
    "browser.get_links": {
        "name": "Get Page Links",
        "description": "Extract all hyperlinks from the current page (href + text).",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 10000,
        "tags": ["browser", "links", "observe"],
    },
    "browser.run_task_readonly": {
        "name": "Run Read-Only Agent Task",
        "description": (
            "Run a browser-use Agent task restricted to read-only operations "
            "(navigation + text extraction)."
        ),
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": ["may navigate to external sites"],
        "timeout_ms": 120000,
        "tags": ["browser", "agent", "readonly", "research"],
    },
}

# ── Capabilities intentionally NOT implemented ───────────────

BLOCKED_CAPABILITIES = {
    "browser.post_sns": "SNS posting — LEVEL_3_RESTRICTED, not implemented",
    "browser.send_message": "DM/message sending — LEVEL_3_RESTRICTED, not implemented",
    "browser.purchase": "Purchase automation — LEVEL_3_RESTRICTED, not implemented",
    "browser.captcha_bypass": "CAPTCHA bypass — FORBIDDEN, not implemented",
    "browser.tos_bypass": "ToS bypass — FORBIDDEN, not implemented",
    "browser.credential_fill": "Credential autofill — LEVEL_3_RESTRICTED, not implemented",
}
