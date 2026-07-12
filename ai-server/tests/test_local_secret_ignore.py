from __future__ import annotations

from pathlib import Path


def test_aegis_local_is_gitignored():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert ".aegis-local/" in gitignore
