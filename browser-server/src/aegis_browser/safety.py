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
    # ── Existing capabilities ──
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

    # ── Permissive owner-assisted capabilities ──
    "browser.read_owned_account_page": {
        "name": "Read Owned Account Page",
        "description": "Read content from a user-owned account page (SNS, email, GitHub, blog dashboard).",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 30000,
        "tags": ["browser", "read", "owned", "account"],
    },
    "browser.read_messages": {
        "name": "Read Messages",
        "description": "Read DMs, emails, notifications from user-owned accounts.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 15000,
        "tags": ["browser", "read", "messages", "owned"],
    },
    "browser.summarize_messages": {
        "name": "Summarize Messages",
        "description": "Summarize DMs, emails, SNS notifications, comments.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 30000,
        "tags": ["browser", "summarize", "messages"],
    },
    "browser.draft_reply": {
        "name": "Draft Reply",
        "description": "Create a reply draft (not send). Returns draft text for user review.",
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 30000,
        "tags": ["browser", "draft", "reply"],
    },
    "browser.draft_post": {
        "name": "Draft Post",
        "description": "Create a blog/SNS post draft (not publish). Returns draft text.",
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 30000,
        "tags": ["browser", "draft", "post"],
    },
    "browser.check_signup_risk": {
        "name": "Check Signup Risk",
        "description": "Analyze a signup form for risk factors (payment, CAPTCHA, identity verification).",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 10000,
        "tags": ["browser", "risk", "signup", "check"],
    },
    "browser.fill_signup_form": {
        "name": "Fill Signup Form",
        "description": "Fill a low-risk signup form with user data.",
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": ["fills form fields"],
        "timeout_ms": 15000,
        "tags": ["browser", "signup", "form", "fill"],
    },
    "browser.submit_low_risk_signup": {
        "name": "Submit Low-Risk Signup",
        "description": "Submit a signup form that passed risk check (free, no payment, no CAPTCHA).",
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": ["creates account", "sends HTTP request"],
        "timeout_ms": 30000,
        "tags": ["browser", "signup", "submit", "low-risk"],
    },
    "browser.detect_payment_required": {
        "name": "Detect Payment Required",
        "description": "Check if a page requires payment information.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 5000,
        "tags": ["browser", "detect", "payment"],
    },
    "browser.detect_captcha": {
        "name": "Detect CAPTCHA",
        "description": "Check if a page contains CAPTCHA challenges.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 5000,
        "tags": ["browser", "detect", "captcha"],
    },
    "browser.detect_identity_verification": {
        "name": "Detect Identity Verification",
        "description": "Check if a page requires identity document verification.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 5000,
        "tags": ["browser", "detect", "identity"],
    },
    "browser.detect_external_publish_action": {
        "name": "Detect External Publish Action",
        "description": "Check if an action would publish/send content externally.",
        "safety_level": SafetyLevel.LEVEL_0_READ,
        "requires_approval": False,
        "side_effects": [],
        "timeout_ms": 5000,
        "tags": ["browser", "detect", "publish"],
    },

    # ── Approval-required capabilities ──
    "browser.publish_post": {
        "name": "Publish Post",
        "description": "Publish a blog post or SNS post. Requires approval.",
        "safety_level": SafetyLevel.LEVEL_2_APPROVAL,
        "requires_approval": True,
        "side_effects": ["publishes content externally"],
        "timeout_ms": 30000,
        "tags": ["browser", "publish", "post"],
    },
    "browser.send_message": {
        "name": "Send Message",
        "description": "Send a DM or message. Requires approval.",
        "safety_level": SafetyLevel.LEVEL_2_APPROVAL,
        "requires_approval": True,
        "side_effects": ["sends message externally"],
        "timeout_ms": 15000,
        "tags": ["browser", "send", "message"],
    },
    "browser.send_email": {
        "name": "Send Email",
        "description": "Send an email. Requires approval.",
        "safety_level": SafetyLevel.LEVEL_2_APPROVAL,
        "requires_approval": True,
        "side_effects": ["sends email"],
        "timeout_ms": 15000,
        "tags": ["browser", "send", "email"],
    },

    # ── Restricted capabilities ──
    "browser.purchase": {
        "name": "Purchase",
        "description": "Make a purchase or paid subscription. Restricted.",
        "safety_level": SafetyLevel.LEVEL_3_RESTRICTED,
        "requires_approval": True,
        "side_effects": ["spends money"],
        "timeout_ms": 30000,
        "tags": ["browser", "purchase", "restricted"],
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
