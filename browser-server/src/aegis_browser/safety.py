"""Safety level definitions for Browser Server capabilities.

The Browser Server uses browser-use for all web automation.
A single capability (browser-server.page.browse) handles all browser tasks
through natural language instructions to the browser-use Agent.

Safety: browser-use Agent has built-in safety rules (no CAPTCHA bypass,
no purchases, no credential filling).
"""

from __future__ import annotations

from enum import IntEnum


class SafetyLevel(IntEnum):
    LEVEL_0_READ = 1
    LEVEL_1_SAFE_ACT = 2
    LEVEL_2_APPROVAL = 3
    LEVEL_3_RESTRICTED = 4


CAPABILITIES = {
    "browser-server.page.browse": {
        "name": "Browse with AI",
        "description": (
            "Execute browser tasks using AI agent (browser-use). "
            "Navigate pages, extract information, fill forms, and interact "
            "with web content using natural language instructions."
        ),
        "safety_level": SafetyLevel.LEVEL_1_SAFE_ACT,
        "requires_approval": False,
        "side_effects": ["sends HTTP request", "executes page JavaScript"],
        "timeout_ms": 120000,
        "tags": ["browser", "web", "ai", "automation"],
    },
}

BLOCKED_CAPABILITIES = {
    "browser.tos_bypass": "ToS bypass — FORBIDDEN",
    "browser.credential_fill": "Credential autofill — RESTRICTED",
    "browser.purchase": "Purchase automation — RESTRICTED",
}
