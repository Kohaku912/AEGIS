"""Startup assertion for the egress gate.

Phase 1-6 of the goal-change plan: *"validate at startup that the egress gate is
enabled and external LLM is disabled; refuse to start otherwise."*

**Re-scoped 2026-09-30** (canonical: ``docs/GOAL-CHANGE.md``). That plan predates the
re-scope, where the constraint became *permission*-gated: outbound connections are
allowed and user information may be sent externally **with the user's permission**.
"external LLM is disabled" is therefore **no longer a requirement**, and asserting it
would make a permitted configuration unable to start. The assertion covers two classes
of failure that still hold:

1. **Incoherent permission configuration** — an opening that does not describe what it
   permits (the master switch on with an empty allowlist; a dead allowlist entry). See
   :meth:`~aegis_ai.egress.gate.EgressGate.status`.
2. **Ineffective configuration** — a profile that resolves to a destination the gate
   will deny, so it silently degrades to Mock instead of running. This is the same
   "declared but not effective" class as the retired TLS and ``requires_approval`` bugs,
   and it is reported as **readiness**, never as a violation.

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
    """Return a readiness string when the LLM config does not suit its declared mode.

    **Re-scoped 2026-09-30.** This used to return a violation whenever ``mode`` was not
    ``local``, which made a *permitted* cloud configuration unready by definition. The
    constraint no longer forbids external use — it forbids **unpermitted** use — so what
    remains here is genuine readiness: in ``local`` mode the ``local_*`` profiles (and a
    local vision profile) must exist, because otherwise the layers resolve to a cloud
    destination the gate will deny and silently degrade to Mock. In ``cloud`` mode there
    is nothing to require; which destinations are reachable is reported separately by
    :func:`verify_egress_configuration`.
    """
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
    if mode not in ("local", "cloud"):
        return f"llm.yaml mode is '{mode}' (must be 'local' or 'cloud')"

    # In cloud mode the ``local_*`` profiles are not required: the layer profiles
    # resolve to their declared cloud providers, and whether each destination is
    # permitted is the gate's decision at request time. Which of them are actually
    # reachable is reported separately by ``verify_egress_configuration``.
    if mode == "cloud":
        return None

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
                "LLM configuration is not ready for its declared mode: %s. "
                "AEGIS will not transmit to an unpermitted destination, but the affected "
                "profiles will degrade to Mock until this is fixed.",
                readiness,
            )

    # Which declared destinations the permission check will actually let through. A
    # profile whose destination is external and *not* permitted is not a violation — the
    # gate denies it, which is the correct outcome — but it is silently ineffective, so
    # report it rather than leaving it to be discovered from a Mock response.
    reachable = _destination_reachability(gate, llm_config_path)
    if reachable is not None:
        status.summary["reachable_destinations"] = reachable
        blocked = sorted(host for host, ok in reachable.items() if not ok)
        if blocked:
            logger.warning(
                "External destinations are declared but not permitted, so those profiles "
                "will degrade to Mock: %s. Permit them via privacy.egress_allowed_hosts "
                "(or a recorded user grant) if that is intended.",
                blocked,
            )

    if status.ok:
        logger.info(
            "Egress permission configuration verified: %d permitted destination(s) %s",
            len(status.summary.get("allowed_hosts", [])),
            status.summary.get("allowed_hosts", []),
        )
        return status

    message = "Egress permission configuration is incoherent: " + "; ".join(status.violations)
    if effective_mode == "fail":
        logger.error("%s — refusing to start", message)
        raise EgressConfigurationError(message)

    logger.warning("%s — continuing because AEGIS_EGRESS_STRICT=%s", message, effective_mode)
    return status


def _destination_reachability(gate: EgressGate, llm_config_path: str | Path | None) -> dict[str, bool] | None:
    """Map every *external* destination declared in ``llm.yaml`` to whether it is permitted.

    Local destinations are omitted — they never need permission. Returns ``None`` when the
    config is absent or unreadable, so a missing file degrades to "no report" rather than
    a fabricated one.
    """
    if llm_config_path is None:
        return None
    path = Path(llm_config_path)
    if not path.exists():
        return None
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None

    from aegis_ai.egress.gate import _extract_host, is_local_destination

    permitted = gate.allowed_hosts
    out: dict[str, bool] = {}
    for profile in (data.get("profiles", {}) or {}).values():
        base_url = str((profile or {}).get("base_url", "") or "")
        if not base_url or is_local_destination(base_url):
            continue
        host = _extract_host(base_url)
        out[host or base_url] = host in permitted
    return out
