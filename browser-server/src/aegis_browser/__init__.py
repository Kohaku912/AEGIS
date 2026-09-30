"""AEGIS Browser Server — Web automation via browser-use.

Transport: the live server is **HTTP**, not gRPC. ``main.py`` runs a
``ThreadingHTTPServer`` (bound to ``AEGIS_GRPC_PORT``, default 50053 — the field
name is historical) exposing ``POST /execute``, ``POST /capability/<app>/<action>``,
``POST /browse``, ``POST /health``, ``GET /health`` and ``GET /capabilities``. The
protos under ``protos/aegis/`` exist for the shared contract only; no gRPC servicer
is registered here. Canonical capability IDs come from the AI Server's JSON
manifests (``ai-server/capabilities/builtin/browser-server/``), not from this module.

Operations the endpoint accepts (``safety.SUPPORTED_OPERATIONS``, short form
``<app>.<action>``):

- ``search.query``, ``page.read``, ``page.summarize``, ``page.navigate``
- ``feed.monitor``, ``session.open``, ``session.authenticated``
- ``element.click``, ``form.fill``, ``form.submit``
- ``file.download``, ``file.upload``, ``social.react``, ``social.post``
- ``account.create``

``/execute`` also accepts ``legacy.page.browse`` as a compatibility operation.
``/capability/...`` additionally requires ``viewer`` (``agent_private`` /
``shared``), a ``purpose`` (``research`` / ``monitor`` / ``automate`` /
``collaborative_review``) and both ``success_condition`` and ``stop_condition``.

Safety: the AI Server's PolicyEngine decides every capability before the request
reaches this endpoint, and ``safety.BLOCKED_ACTIONS`` refuses ``captcha_bypass``,
``bot_evasion``, ``credential_store_read``, ``purchase`` and ``contract_acceptance``
at the boundary. Egress is gated in ``browser_use_agent.py`` and
``safety_boundary.py`` through ``egress.py``, which enforces the single constraint —
user-information egress, **re-scoped 2026-09-30** to *unpermitted* disclosure (outbound
connections, and disclosure the user permits, are allowed). Because this server is
agent-private, user-visible pages must be routed to the PC or Android server.
"""

from aegis_browser.config import Config  # noqa: F401
from aegis_browser.safety import BLOCKED_ACTIONS, SUPPORTED_OPERATIONS  # noqa: F401
