"""AEGIS Browser Server — Web automation via browser-use.

Capabilities:
- browser.open_page: Navigate to URL
- browser.extract_page_text: Extract text content
- browser.get_screenshot: Page screenshot
- browser.get_current_url: Current URL
- browser.get_page_title: Page title
- browser.get_links: Extract links
- browser.run_task_readonly: Read-only AI agent task

Architecture: The Browser Server is a gRPC capability server that registers
with AEGIS Core. It wraps browser-use for AI-driven browser automation
while enforcing AEGIS safety policies.

Safety: All capabilities go through AEGIS Core's PolicyEngine.
Dangerous operations (SNS, purchases, CAPTCHA bypass) are structurally blocked.
"""

from aegis_browser.config import Config  # noqa: F401
from aegis_browser.safety import BLOCKED_ACTIONS, SUPPORTED_OPERATIONS  # noqa: F401
