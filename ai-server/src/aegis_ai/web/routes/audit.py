"""Read-only ledger of irreversible operations.

Phase 3 of the goal-change plan replaces the retired approval gate with
*post-hoc visibility*: the gate is gone, but what was done must be enumerable and
traceable afterwards. These endpoints are read-only by design — the ledger
observes, it does not decide.

Endpoints
---------
``GET /api/audit/irreversible``
    Inventory of capabilities at or above the reversibility threshold, plus
    tallies. Query params: ``threshold`` (``recoverable`` | ``difficult`` |
    ``irreversible``, default ``difficult``), ``include_unknown`` (default true).

``GET /api/audit/irreversible/occurrences``
    Audit entries for those capabilities — what actually ran. Query params:
    ``limit``, ``page``, plus the same ``threshold`` / ``include_unknown``.

UI is deliberately deferred to Phase 5; this is the data surface it will read.
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request


def _threshold_arg() -> str:
    from aegis_ai import irreversibility

    raw = (request.args.get("threshold") or irreversibility.DEFAULT_THRESHOLD).strip().lower()
    if raw not in irreversibility.SEVERITY:
        raise ValueError(f"threshold must be one of {sorted(irreversibility.SEVERITY)}")
    return raw


def _include_unknown_arg() -> bool:
    raw = (request.args.get("include_unknown") or "true").strip().lower()
    return raw not in {"0", "false", "no"}


def _int_arg(name: str, default: int, *, minimum: int = 1, maximum: int = 1000) -> int:
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    value = int(raw)
    return max(minimum, min(maximum, value))


def init_audit_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_audit", __name__)

    def _catalog():
        runtime = getattr(owner, "_runtime", None)
        broker = getattr(runtime, "tool_broker", None)
        return getattr(broker, "_catalog", None)

    @bp.route("/api/audit/irreversible")
    def irreversible_inventory():
        from aegis_ai import irreversibility

        try:
            catalog = _catalog()
            if catalog is None:
                return jsonify({"error": "capability catalog unavailable"}), 503
            ledger = irreversibility.summarize(
                catalog,
                threshold=_threshold_arg(),
                include_unknown=_include_unknown_arg(),
            )
            return jsonify(ledger)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard
            return jsonify({"error": str(exc)}), 500

    @bp.route("/api/audit/irreversible/occurrences")
    def irreversible_occurrences():
        from aegis_ai import irreversibility

        try:
            catalog = _catalog()
            if catalog is None:
                return jsonify({"error": "capability catalog unavailable"}), 503
            runtime = getattr(owner, "_runtime", None)
            audit_manager = getattr(runtime, "audit_manager", None) or getattr(
                runtime, "audit_log", None
            )
            result = irreversibility.occurrences(
                audit_manager,
                catalog,
                threshold=_threshold_arg(),
                include_unknown=_include_unknown_arg(),
                limit=_int_arg("limit", 200),
                page=_int_arg("page", 1),
            )
            return jsonify(result)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # noqa: BLE001 - surfaced to the dashboard
            return jsonify({"error": str(exc)}), 500

    owner.app.register_blueprint(bp)
