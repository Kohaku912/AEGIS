"""Dashboard LLM usage page route."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, render_template


def init_llm_usage_page_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_llm_usage_page", __name__)

    @bp.route("/dashboard/llm-usage")
    def dashboard_llm_usage():
        return render_template("dashboard/llm_usage.html")

    owner.app.register_blueprint(bp)
