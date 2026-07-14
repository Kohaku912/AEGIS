from __future__ import annotations

from pathlib import Path


def test_aegis_local_is_gitignored():
    repo_root = Path(__file__).resolve().parents[2]
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert ".aegis-local/" in gitignore
