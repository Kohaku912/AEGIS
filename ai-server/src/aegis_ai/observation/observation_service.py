"""Multimodal Observation Service — gathers and compares observations from PC/Browser/Android."""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from typing import Any

from aegis_ai.observation.observation_types import (
    ElementKind,
    ObservationDiff,
    ObservationPurpose,
    ObservationRequest,
    ObservationResult,
    ObservationStatus,
    ObservationTarget,
)

logger = logging.getLogger("aegis_ai.observation.observation_service")

_SENSITIVE_KEYWORDS = {
    "password", "token", "secret", "api_key", "credential",
    "cookie", "session", "auth", "bearer", "credit_card",
}


def _mask_sensitive_text(text: str) -> tuple[str, list[str]]:
    redactions: list[str] = []
    masked = text
    for kw in _SENSITIVE_KEYWORDS:
        if kw.lower() in masked.lower():
            redactions.append(kw)
    import re as _re
    _pat1 = r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+"
    masked = _re.sub(_pat1, r"\1=***MASKED***", masked, flags=_re.IGNORECASE)
    masked = _re.sub(r"Bearer\s+\S+", "Bearer ***MASKED***", masked, flags=_re.IGNORECASE)
    masked = _re.sub(r"sk-[a-zA-Z0-9]{20,}", "sk-***MASKED***", masked)
    return masked, redactions


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class MultimodalObservationService:
    """Gathers and compares observations from external devices.

    Parameters
    ----------
    browser_client:
        Client for browser-server (optional).
    pc_client:
        Client for pc-server (optional).
    android_client:
        Client for android-server (optional).
    audit_log:
        Optional audit log for recording observations.
    """

    def __init__(
        self,
        browser_client: Any = None,
        pc_client: Any = None,
        android_client: Any = None,
        audit_log: Any = None,
    ) -> None:
        self._browser = browser_client
        self._pc = pc_client
        self._android = android_client
        self._audit = audit_log

    def observe(
        self,
        request: ObservationRequest,
    ) -> ObservationResult:
        """Execute an observation based on target."""
        if not request.observation_id:
            request.observation_id = f"obs_{uuid.uuid4().hex[:10]}"
        if not request.created_at:
            request.created_at = int(time.time() * 1000)

        try:
            if request.target == ObservationTarget.BROWSER:
                return self._observe_browser(request)
            elif request.target == ObservationTarget.PC:
                return self._observe_pc(request)
            elif request.target == ObservationTarget.ANDROID:
                return self._observe_android(request)
            else:
                return self._observe_unavailable(request)
        except Exception as exc:
            logger.error("Observation error: %s", exc)
            return ObservationResult(
                observation_id=request.observation_id,
                target=request.target,
                status=ObservationStatus.FAILED,
                created_at=int(time.time() * 1000),
            )

    def observe_all(
        self,
        purpose: ObservationPurpose = ObservationPurpose.PERIODIC_STATE,
    ) -> list[ObservationResult]:
        """Observe all available targets and return a list of results."""
        results: list[ObservationResult] = []
        targets: list[tuple[ObservationTarget, Any]] = [
            (ObservationTarget.PC, self._pc),
            (ObservationTarget.BROWSER, self._browser),
            (ObservationTarget.ANDROID, self._android),
        ]
        for target, client in targets:
            if client is not None:
                request = ObservationRequest(target=target, purpose=purpose)
                results.append(self.observe(request))
        return results

    def summarize(self, result: ObservationResult) -> str:
        """Create a short text summary of an observation."""
        return result.to_context_string()

    def diff(self, before: ObservationResult, after: ObservationResult) -> ObservationDiff:
        """Compare two observations and detect changes."""
        diff = ObservationDiff(
            before_observation_id=before.observation_id,
            after_observation_id=after.observation_id,
        )

        if before.current_url != after.current_url:
            diff.url_changed = True
            diff.changed = True

        if before.active_window != after.active_window:
            diff.active_window_changed = True
            diff.changed = True

        if before.visible_text_summary != after.visible_text_summary:
            diff.visible_text_changed = True
            diff.changed = True

        if before.dom_summary != after.dom_summary:
            diff.dom_changed = True
            diff.changed = True

        if before.ui_tree != after.ui_tree:
            diff.ui_tree_changed = True
            diff.changed = True

        before_ids = {e.element_id for e in before.detected_elements}
        after_ids = {e.element_id for e in after.detected_elements}
        new_ids = after_ids - before_ids
        removed_ids = before_ids - after_ids

        diff.new_elements = [e for e in after.detected_elements if e.element_id in new_ids]
        diff.removed_elements = [e for e in before.detected_elements if e.element_id in removed_ids]

        for elem in after.detected_elements:
            if elem.kind == ElementKind.ERROR_MESSAGE:
                old_texts = {e.text for e in before.detected_elements if e.kind == ElementKind.ERROR_MESSAGE}
                if elem.text not in old_texts:
                    diff.new_error_messages.append(elem.text[:200])
            if elem.kind == ElementKind.SUCCESS_MESSAGE:
                old_texts = {e.text for e in before.detected_elements if e.kind == ElementKind.SUCCESS_MESSAGE}
                if elem.text not in old_texts:
                    diff.new_success_messages.append(elem.text[:200])

        if diff.new_elements:
            diff.changed = True
        if diff.new_error_messages or diff.new_success_messages:
            diff.changed = True

        change_parts = []
        if diff.url_changed:
            change_parts.append(f"url: {before.current_url[:50]} → {after.current_url[:50]}")
        if diff.active_window_changed:
            change_parts.append("window changed")
        if diff.new_error_messages:
            change_parts.append(f"new errors: {len(diff.new_error_messages)}")
        if diff.new_success_messages:
            change_parts.append(f"new success: {len(diff.new_success_messages)}")
        if diff.new_elements:
            change_parts.append(f"new elements: {len(diff.new_elements)}")
        diff.state_change_summary = "; ".join(change_parts) if change_parts else "no changes"
        diff.confidence = 0.8 if diff.changed else 0.9

        return diff

    def redact_sensitive(self, result: ObservationResult) -> ObservationResult:
        """Redact sensitive information from an observation."""
        redactions: list[str] = []

        masked_text, red = _mask_sensitive_text(result.visible_text_summary)
        result.visible_text_summary = masked_text
        redactions.extend(red)

        masked_dom, red = _mask_sensitive_text(result.dom_summary)
        result.dom_summary = masked_dom
        redactions.extend(red)

        masked_tree, red = _mask_sensitive_text(result.ui_tree)
        result.ui_tree = masked_tree
        redactions.extend(red)

        for elem in result.detected_elements:
            if elem.sensitive:
                redactions.append(f"element:{elem.element_id}")

        result.redactions = list(set(redactions))
        if redactions:
            result.sensitivity_flags.append("contains_sensitive_data")
        return result

    def build_multimodal_context(
        self,
        result: ObservationResult,
        max_chars: int = 1000,
    ) -> str:
        """Build a text context string for LLM consumption."""
        parts: list[str] = []
        parts.append(f"Target: {result.target.value}")
        parts.append(f"Status: {result.status.value}")

        if result.active_window:
            parts.append(f"Active window: {result.active_window}")
        if result.current_url:
            parts.append(f"URL: {result.current_url[:100]}")
        if result.page_title:
            parts.append(f"Title: {result.page_title[:100]}")
        if result.active_app:
            parts.append(f"App: {result.active_app}")

        if result.visible_text_summary:
            parts.append(f"Visible text: {result.visible_text_summary[:300]}")

        buttons = [e for e in result.detected_elements if e.kind == ElementKind.BUTTON and e.clickable]
        if buttons:
            parts.append(f"Buttons: {[e.label for e in buttons[:8]]}")

        inputs = [e for e in result.detected_elements if e.kind == ElementKind.INPUT and e.editable]
        if inputs:
            parts.append(f"Inputs: {[e.label for e in inputs[:5]]}")

        errors = [e for e in result.detected_elements if e.kind == ElementKind.ERROR_MESSAGE]
        if errors:
            parts.append(f"Errors: {[e.text[:50] for e in errors[:3]]}")

        successes = [e for e in result.detected_elements if e.kind == ElementKind.SUCCESS_MESSAGE]
        if successes:
            parts.append(f"Success: {[e.text[:50] for e in successes[:3]]}")

        text = "\n".join(parts)
        return text[:max_chars] + "..." if len(text) > max_chars else text

    def _observe_browser(self, request: ObservationRequest) -> ObservationResult:
        if self._browser is None:
            return self._observe_unavailable(request)

        now = int(time.time() * 1000)
        result = ObservationResult(
            observation_id=request.observation_id,
            target=ObservationTarget.BROWSER,
            created_at=now,
        )

        try:
            if hasattr(self._browser, "get_current_url"):
                result.current_url = str(self._browser.get_current_url() or "")
            if hasattr(self._browser, "get_page_title"):
                result.page_title = str(self._browser.get_page_title() or "")
            if hasattr(self._browser, "get_page_text"):
                result.visible_text_summary = str(self._browser.get_page_text() or "")[:1000]
            if hasattr(self._browser, "get_dom_summary"):
                result.dom_summary = str(self._browser.get_dom_summary() or "")[:1000]
            result.status = ObservationStatus.SUCCESS
        except Exception as exc:
            logger.warning("Browser observation partial: %s", exc)
            result.status = ObservationStatus.PARTIAL

        return self.redact_sensitive(result)

    def _observe_pc(self, request: ObservationRequest) -> ObservationResult:
        if self._pc is None:
            return self._observe_unavailable(request)

        now = int(time.time() * 1000)
        result = ObservationResult(
            observation_id=request.observation_id,
            target=ObservationTarget.PC,
            created_at=now,
        )

        try:
            if hasattr(self._pc, "get_active_window"):
                result.active_window = str(self._pc.get_active_window() or "")
            if hasattr(self._pc, "get_active_app"):
                result.active_app = str(self._pc.get_active_app() or "")
            if hasattr(self._pc, "get_screen_text"):
                result.visible_text_summary = str(self._pc.get_screen_text() or "")[:1000]
            result.status = ObservationStatus.SUCCESS
        except Exception as exc:
            logger.warning("PC observation partial: %s", exc)
            result.status = ObservationStatus.PARTIAL

        return self.redact_sensitive(result)

    def _observe_android(self, request: ObservationRequest) -> ObservationResult:
        if self._android is None:
            return self._observe_unavailable(request)

        now = int(time.time() * 1000)
        result = ObservationResult(
            observation_id=request.observation_id,
            target=ObservationTarget.ANDROID,
            created_at=now,
        )

        try:
            if hasattr(self._android, "get_current_app"):
                result.active_app = str(self._android.get_current_app() or "")
            if hasattr(self._android, "get_ui_tree"):
                result.ui_tree = str(self._android.get_ui_tree() or "")[:1000]
            if hasattr(self._android, "get_screen_text"):
                result.visible_text_summary = str(self._android.get_screen_text() or "")[:1000]
            result.status = ObservationStatus.SUCCESS
        except Exception as exc:
            logger.warning("Android observation partial: %s", exc)
            result.status = ObservationStatus.PARTIAL

        return self.redact_sensitive(result)

    def _observe_unavailable(self, request: ObservationRequest) -> ObservationResult:
        return ObservationResult(
            observation_id=request.observation_id,
            target=request.target,
            status=ObservationStatus.UNAVAILABLE,
            created_at=int(time.time() * 1000),
        )
