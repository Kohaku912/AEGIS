"""LLM Usage API routes — Flask Blueprint."""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.observability.llm_usage.routes")

llm_usage_bp = Blueprint("llm_usage", __name__)

_service = None


def init_llm_usage_routes(app: Any, service: Any) -> None:
    """Register the LLM Usage blueprint."""
    global _service
    _service = service
    app.register_blueprint(llm_usage_bp)


def _svc():
    return _service


def _common_filters() -> dict[str, Any]:
    return {
        "period": request.args.get("period", "24h"),
        "caller": request.args.get("caller", ""),
        "profile": request.args.get("profile", ""),
        "prompt_id": request.args.get("prompt_id", ""),
        "model": request.args.get("model", ""),
        "errors_only": request.args.get("errors_only", "").lower() in ("1", "true"),
        "min_tokens": int(request.args.get("min_tokens", 0)),
    }


# ── Endpoints ─────────────────────────────────────────────────


@llm_usage_bp.route("/api/llm-usage/summary")
def api_summary():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_summary(**_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/timeseries")
def api_timeseries():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        bucket = request.args.get("bucket", "1h")
        return jsonify(svc.get_timeseries(bucket=bucket, **_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/breakdown/callers")
def api_breakdown_callers():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_breakdown("caller", **_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/breakdown/profiles")
def api_breakdown_profiles():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_breakdown("profile", **_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/breakdown/prompts")
def api_breakdown_prompts():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_prompts(**_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/breakdown/models")
def api_breakdown_models():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_breakdown("model", **_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/traces")
def api_traces():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        limit = int(request.args.get("limit", 200))
        return jsonify(svc.get_traces(limit=limit, **_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_usage_bp.route("/api/llm-usage/waste-candidates")
def api_waste_candidates():
    try:
        svc = _svc()
        if svc is None:
            return jsonify({"error": "LLMUsageService unavailable"}), 503
        return jsonify(svc.get_waste_candidates(**_common_filters()))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
