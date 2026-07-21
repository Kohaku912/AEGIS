"""Browser runtime safety boundaries.

Capability risk and approval metadata live only in the AI Server JSON
manifests.  This module describes the operations implemented by this process
and the actions that the browser runtime will never perform.
"""

from __future__ import annotations

SUPPORTED_OPERATIONS = frozenset(
    {
        "search.query",
        "page.read",
        "page.summarize",
        "page.navigate",
        "feed.monitor",
        "session.open",
        "session.authenticated",
        "element.click",
        "form.fill",
        "form.submit",
        "file.download",
        "file.upload",
        "social.react",
        "social.post",
        "account.create",
    }
)

# These are runtime boundaries, not user-intent classifiers. The AI Server
# PolicyEngine still makes every capability decision before this endpoint.
BLOCKED_ACTIONS = frozenset(
    {
        "captcha_bypass",
        "bot_evasion",
        "credential_store_read",
        "purchase",
        "contract_acceptance",
    }
)
