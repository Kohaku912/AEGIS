"""LLM Config Routes — Flask routes for LLM configuration management.

Provides:
- GET  /dashboard/llm-config     → LLM Config UI page
- GET  /api/llm/profiles         → List LLM profiles
- GET  /api/llm/prompts          → List all prompts
- GET  /api/llm/prompts/<id>     → Get a single prompt
- PUT  /api/llm/prompts/<id>     → Update a prompt (editable only)
- POST /api/llm/prompts/<id>/rollback → Rollback prompt to version
- POST /api/llm/regression-test  → Run prompt regression test
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, jsonify, render_template, request

logger = logging.getLogger("aegis_ai.web.llm_config")

llm_config_bp = Blueprint(
    "llm_config",
    __name__,
    template_folder="templates",
)

_prompt_registry = None
_settings_resolver = None


def init_llm_config(prompt_registry: Any, settings_resolver: Any) -> None:
    global _prompt_registry, _settings_resolver
    _prompt_registry = prompt_registry
    _settings_resolver = settings_resolver


@llm_config_bp.route("/dashboard/llm-config")
def llm_config_page():
    return render_template("dashboard/llm_config.html")


@llm_config_bp.route("/api/llm/profiles", methods=["GET"])
def get_profiles():
    if not _settings_resolver:
        return jsonify({"error": "Settings resolver not available"}), 500
    try:
        profiles = {}
        for name in ["chat_balanced", "tool_planning", "json_generation",
                      "long_answer", "vision_observation", "self_development"]:
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
            enriched.append({
                **meta,
                "editable": prompt.get("editable", True),
                "protected": prompt.get("protected", False),
            })
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
        return jsonify({
            "prompt_id": prompt_id,
            "template": prompt["template"],
            "version": prompt.get("version", "unknown"),
            "editable": prompt.get("editable", True),
            "protected": prompt.get("protected", False),
            "hash": meta["hash"],
        })
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
            return jsonify({
                "success": True,
                "old_template": old_template,
                "new_template": new_template,
            })
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
        target_template = data.get("template")
        if not target_template:
            return jsonify({"error": "Missing 'template' field for rollback"}), 400

        success = _prompt_registry.update_prompt(prompt_id, target_template)
        if success:
            return jsonify({"success": True, "prompt_id": prompt_id})
        return jsonify({"error": "Failed to rollback prompt"}), 500
    except KeyError:
        return jsonify({"error": f"Prompt '{prompt_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@llm_config_bp.route("/api/llm/regression-test", methods=["POST"])
def run_regression_test():
    if not _prompt_registry:
        return jsonify({"error": "Prompt registry not available"}), 500

    dangerous_patterns = [
        "ignore previous",
        "ignore all",
        "bypass safety",
        "disable safety",
        "override policy",
        "delete all",
        "rm -rf",
        "DROP TABLE",
    ]
    results = []
    try:
        prompts = _prompt_registry.list_prompts()
        for meta in prompts:
            pid = meta["prompt_id"]
            prompt = _prompt_registry.get(pid)
            template = prompt.get("template", "")
            found = [p for p in dangerous_patterns if p.lower() in template.lower()]
            results.append({
                "prompt_id": pid,
                "safe": len(found) == 0,
                "dangerous_patterns_found": found,
            })
        all_safe = all(r["safe"] for r in results)
        return jsonify({"all_safe": all_safe, "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
