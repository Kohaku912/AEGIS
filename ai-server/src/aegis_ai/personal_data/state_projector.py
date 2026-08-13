"""Project latest user/device/room state from PDC events."""

from __future__ import annotations

from typing import Any

from aegis_ai.personal_data.ingest import location_from_payload, new_id
from aegis_ai.personal_data.models import Location, StateSnapshot


def project_state(event: dict[str, Any], *, previous: dict[str, Any] | None = None) -> StateSnapshot:
    payload = dict(event.get("payload") or {})
    prev_payload = dict((previous or {}).get("payload") or {})
    merged = {**prev_payload, **{k: v for k, v in payload.items() if v not in (None, "", [], {})}}
    device = str(event.get("source_device") or "pc")
    title = str(
        merged.get("app_name")
        or merged.get("window_title")
        or merged.get("package_name")
        or event.get("title")
        or "state"
    )
    loc = event.get("location")
    if isinstance(loc, Location):
        location = loc
    elif isinstance(loc, dict):
        location = Location.model_validate(loc)
    else:
        location = location_from_payload(merged)
    return StateSnapshot(
        id=new_id("st"),
        timestamp_ms=int(event.get("timestamp_ms") or 0),
        source_device=device,
        source_sensor=str(event.get("source_sensor") or "os"),
        event_type="state.snapshot",
        epistemics="generated",
        payload=merged,
        title=title,
        entity_ids=list(event.get("entity_ids") or []),
        evidence_ids=list(event.get("evidence_ids") or []),
        location=location,
        retention_class="forever_metadata",
        subject="user",
    )
