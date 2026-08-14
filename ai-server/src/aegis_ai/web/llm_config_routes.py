"""LLM Config Routes — Flask routes for LLM configuration management.

Provides:
- GET  /api/llm/profiles         → List LLM profiles
- GET  /api/llm/prompts          → List all prompts
- GET  /api/llm/prompts/<id>     → Get a single prompt
- PUT  /api/llm/prompts/<id>     → Update a prompt (editable only)
- POST /api/llm/prompts/<id>/rollback → Rollback prompt to version
- POST /api/llm/regression-test  → Run prompt regression test
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger("aegis_ai.web.llm_config")

llm_config_bp = Blueprint("llm_config", __name__)

_prompt_registry = None
_settings_resolver = None
_audit_log = None


def init_llm_config(prompt_registry: Any, settings_resolver: Any, audit_log: Any = None) -> None:
    global _prompt_registry, _settings_resolver, _audit_log
    _prompt_registry = prompt_registry
    _settings_resolver = settings_resolver
    _audit_log = audit_log


@llm_config_bp.route("/api/llm/profiles", methods=["GET"])
def get_profiles():
    if not _settings_resolver:
        return jsonify({"error": "Settings resolver not available"}), 500
    try:
        profiles = {}
        for name in [
            "chat_balanced",
            "tool_planning",
            "json_generation",
            "long_answer",
            "vision_observation",
            "self_development",
        ]:
            try:
                s = _settings_resolver.resolve(profile_id=name)
                profiles[name] = {
                    "provider": s.provider,
                    "model": s.model,
                    "max_tokens": s.max_tokens,
                    "temperature": s.temperature,
                    "reasoning_level": s.reasoning_level,
                    "timeout_seconds": s.timeout_seconds,
                    "max_tool_rounds": s.max_tool_rounds,
                }
            except KeyError:
                pass
        return jsonify({"profiles": profiles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/prompts", methods=["GET"])
def get_prompts():
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500
    try:
        prompts = _prompt_registry.list_prompts()
        enriched = []
        for meta in prompts:
            prompt = _prompt_registry.get(meta["prompt_id"])
            enriched.append(
                {
                    **meta,
                    "editable": prompt.get("editable", True),
                    "protected": prompt.get("protected", False),
                }
            )
        return jsonify({"prompts": enriched})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/prompts/<prompt_id>", methods=["GET"])
def get_prompt(prompt_id: str):
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500
    try:
        prompt = _prompt_registry.get(prompt_id)
        meta = _prompt_registry.get_metadata(prompt_id)
        return jsonify(
            {
                "prompt_id": prompt_id,
                "template": prompt["template"],
                "version": prompt.get("version", "unknown"),
                "editable": prompt.get("editable", True),
                "protected": prompt.get("protected", False),
                "hash": meta["hash"],
            }
        )
    except KeyError:
        return jsonify({"error": f"Prompt '{prompt_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/prompts/<prompt_id>", methods=["PUT"])
def update_prompt(prompt_id: str):
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500
    try:
        prompt = _prompt_registry.get(prompt_id)
        if prompt.get("protected", False) or not prompt.get("editable", True):
            return jsonify({"error": f"Prompt '{prompt_id}' is not editable"}), 403

        data = request.get_json(silent=True) or {}
        new_template = data.get("template")
        if not new_template or not isinstance(new_template, str):
            return jsonify({"error": "Missing or invalid 'template' field"}), 400

        old_template = prompt["template"]
        success = _prompt_registry.update_prompt(prompt_id, new_template)
        if success:
            _audit_prompt_change("prompt.updated", prompt_id, old_template, new_template)
            return jsonify(
                {
                    "success": True,
                    "old_template": old_template,
                    "new_template": new_template,
                }
            )
        return jsonify({"error": "Failed to update prompt"}), 500
    except KeyError:
        return jsonify({"error": f"Prompt '{prompt_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/prompts/<prompt_id>/rollback", methods=["POST"])
def rollback_prompt(prompt_id: str):
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500
    try:
        prompt = _prompt_registry.get(prompt_id)
        if prompt.get("protected", False):
            return jsonify({"error": f"Prompt '{prompt_id}' is protected"}), 403

        data = request.get_json(silent=True) or {}
        revision_id = str(data.get("revision_id") or "")
        target_template = data.get("template")
        if not revision_id and not target_template:
            return jsonify({"error": "Missing revision_id for rollback"}), 400
        before = prompt["template"]
        success = (
            _prompt_registry.rollback_prompt(prompt_id, revision_id)
            if revision_id
            else _prompt_registry.update_prompt(prompt_id, str(target_template))
        )
        if success:
            after = _prompt_registry.get(prompt_id)["template"]
            _audit_prompt_change("prompt.rolled_back", prompt_id, before, after)
            return jsonify({"success": True, "prompt_id": prompt_id, "revision_id": revision_id})
        return jsonify({"error": "Failed to rollback prompt"}), 500
    except KeyError:
        return jsonify({"error": f"Prompt '{prompt_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/prompts/<prompt_id>/versions", methods=["GET"])
def prompt_versions(prompt_id: str):
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500
    try:
        return jsonify({"prompt_id": prompt_id, "versions": _prompt_registry.list_versions(prompt_id)})
    except KeyError:
        return jsonify({"error": f"Prompt '{prompt_id}' not found"}), 404


@llm_config_bp.route("/api/llm/regression-test", methods=["POST"])
def run_regression_test():
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500

    try:
        data = request.get_json(silent=True) or {}
        prompt_id = str(data.get("prompt_id") or "")
        template = data.get("template")
        if prompt_id and isinstance(template, str):
            result = _prompt_registry.validate_candidate(prompt_id, template)
            return jsonify({"all_valid": result["valid"], "candidate": result})
        results = [
            {
                "prompt_id": meta["prompt_id"],
                **_prompt_registry.validate_candidate(
                    meta["prompt_id"], _prompt_registry.get(meta["prompt_id"])["template"]
                ),
            }
            for meta in _prompt_registry.list_prompts()
        ]
        return jsonify({"all_valid": all(item["valid"] for item in results), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _audit_prompt_change(action: str, prompt_id: str, before: str, after: str) -> None:
    if _audit_log is None or not hasattr(_audit_log, "log_decision"):
        return
    _audit_log.log_decision(
        action,
        prompt_id,
        "ALLOW",
        actor="dashboard",
        reason="Fresh-authenticated prompt management action",
        detail={
            "before_hash": hashlib.sha256(before.encode("utf-8")).hexdigest()[:16],
            "after_hash": hashlib.sha256(after.encode("utf-8")).hexdigest()[:16],
        },
    )
