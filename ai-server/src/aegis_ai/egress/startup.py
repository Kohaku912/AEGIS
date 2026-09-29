"""Startup assertion for the egress gate.

Phase 1-6 of the goal-change plan: *"validate at startup that the egress gate is
enabled and external LLM is disabled; refuse to start otherwise."*

The assertion covers two classes of failure:

1. **Configuration drift** — a feature flag or allowlist has been opened.
2. **Ineffective configuration** — the LLM config points at a cloud provider, which
   means the local path is not actually usable and cloud is a functional prerequisite.
   This is the same "declared but not effective" class as the retired TLS and
   ``requires_approval`` bugs.

Environment:
    ``AEGIS_EGRESS_STRICT`` — ``fail`` (default in production) or ``warn``.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from aegis_ai.egress.gate import (
    EgressConfigurationError,
    EgressGate,
    EgressStatus,
    get_egress_gate,
)

logger = logging.getLogger("aegis_ai.egress.startup")


def _llm_config_violation(llm_config_path: str | Path | None) -> str | None:
    """Return a violation string when the LLM config is not local-only."""
    if llm_config_path is None:
        return None
    path = Path(llm_config_path)
    if not path.exists():
        return f"LLM config not found at {path}"

    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return f"LLM config at {path} could not be read: {exc}"

    mode = str(data.get("mode", "cloud")).strip().lower()
    if mode != "local":
        return f"llm.yaml mode is '{mode}' (must be 'local')"

    profiles = data.get("profiles", {}) or {}
    local_names = [name for name in profiles if str(name).startswith("local_")]
    if not local_names:
        return "llm.yaml defines no local_* profiles"

    # In local mode, vision_observation is remapped to local_vision. Check the
    # *resolved* profile, not the cloud definition it replaces.
    try:
        from aegis_ai.llm.settings_resolver import LLMSettingsResolver

        vision_name = LLMSettingsResolver._LOCAL_PROFILE_MAP.get("vision_observation", "vision_observation")
    except Exception:
        vision_name = "vision_observation"

    vision_profile = profiles.get(vision_name, {}) or {}
    if not vision_profile:
        return f"llm.yaml has no local vision profile ('{vision_name}')"

    vision_base_url = str(vision_profile.get("base_url", ""))
    if vision_base_url and "localhost" not in vision_base_url and "127.0.0.1" not in vision_base_url:
        return (
            f"llm.yaml vision profile '{vision_name}' is not local "
            f"(base_url={vision_base_url}); no local VLM is configured"
        )
    return None


def verify_egress_configuration(
    gate: EgressGate | None = None,
    *,
    llm_config_path: str | Path | None = None,
    settings_store: Any = None,
    mode: str | None = None,
    require_local_llm: bool = False,
) -> EgressStatus:
    """Verify that egress is structurally closed.

    Two classes of finding:

    - **Violations** (always fatal in ``fail`` mode): a feature flag or allowlist has
      been opened. These mean the constraint is *not* structurally enforced.
    - **Readiness warnings** (fatal only when ``require_local_llm=True``): the local LLM
      path is incomplete, so AEGIS would degrade to Mock rather than function. The
      constraint still holds — nothing is transmitted — but the system is not usable.

    Args:
        gate: The egress gate to inspect. Defaults to the process-wide gate.
        llm_config_path: Path to ``llm.yaml``. When given, local readiness is checked.
        settings_store: Unused placeholder for symmetry; the gate owns the store.
        mode: ``fail`` or ``warn``. Defaults to ``AEGIS_EGRESS_STRICT`` or ``fail``.
        require_local_llm: Escalate local-LLM readiness to a fatal violation.

    Returns:
        The :class:`EgressStatus`. Raises :class:`EgressConfigurationError` in
        ``fail`` mode when fatal findings are present.
    """
    del settings_store  # the gate already holds the settings store
    gate = gate or get_egress_gate()
    effective_mode = (mode or os.environ.get("AEGIS_EGRESS_STRICT", "fail")).strip().lower()

    status = gate.status()

    readiness = _llm_config_violation(llm_config_path)
    status.summary["local_llm_readiness"] = readiness or "ok"
    if readiness:
        if require_local_llm:
            status.violations.append(readiness)
            status.ok = False
        else:
            logger.warning(
                "Egress is closed, but the local LLM path is not ready: %s. "
                "AEGIS will not transmit, but it will degrade to Mock until this is fixed.",
                readiness,
            )

    if status.ok:
        logger.info("Egress configuration verified: local-only, deny-by-default")
        return status

    message = "Egress configuration is NOT closed: " + "; ".join(status.violations)
    if effective_mode == "fail":
        logger.error("%s — refusing to start", message)
        raise EgressConfigurationError(message)

    logger.warning("%s — continuing because AEGIS_EGRESS_STRICT=%s", message, effective_mode)
    return status
