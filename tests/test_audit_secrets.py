from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "audit-secrets.py"
    spec = importlib.util.spec_from_file_location("audit_secrets", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


def test_local_secret_patterns_are_loaded_without_hardcoding_values() -> None:
    module = _load_module()
    patterns = module._patterns_from_local_notes(
        "- Linux SSH/sudo password candidates: `alpha-secret`\n"
        "- Host: `192.0.2.1`\n"
        "- Wi-Fi passphrase: `beta-secret`\n"
    )

    assert {name for name, _ in patterns} == {"known_local_secret"}
    assert any(pattern.search("alpha-secret") for _, pattern in patterns)
    assert any(pattern.search("beta-secret") for _, pattern in patterns)
    assert not any(pattern.search("192.0.2.1") for _, pattern in patterns)


def test_secret_auditor_does_not_embed_local_passwords() -> None:
    source = (Path(__file__).resolve().parents[1] / "scripts" / "audit-secrets.py").read_text(
        encoding="utf-8"
    )
    notes = Path(__file__).resolve().parents[1] / ".aegis-local" / "infra_access.md"
    for _, pattern in _load_module()._patterns_from_local_notes(notes.read_text(encoding="utf-8")):
        assert pattern.pattern not in source
