from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_generated_design_tokens_exist_and_pass_contrast() -> None:
    report_path = ROOT / "design-tokens" / "contrast-report.json"
    web_tokens = ROOT / "web-ui" / "src" / "styles" / "tokens.css"
    android_tokens = (
        ROOT
        / "android-server"
        / "app"
        / "src"
        / "main"
        / "java"
        / "com"
        / "aegis"
        / "android"
        / "ui"
        / "designsystem"
        / "GeneratedTokens.kt"
    )

    assert web_tokens.exists()
    assert android_tokens.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["all_aa_body"] is True
    assert all(pair["ratio"] >= 4.5 for pair in report["pairs"])
