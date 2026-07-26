from __future__ import annotations

import json
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.capability_index import CapabilityIndex, CapabilityRetriever


def _write_capability(
    root: Path,
    server_id: str,
    app_id: str,
    action: str,
    *,
    title: str,
    description: str,
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
    input_schema: dict | None = None,
) -> None:
    path = root / "builtin" / server_id / app_id / f"{action}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "title": title,
                "description": description,
                "server_id": server_id,
                "app_id": app_id,
                "action": action,
                "operation_category": "test_fixture",
                "risk": {"level": "low", "requires_approval": False},
                "tags": tags or [],
                "aliases": aliases or [],
                "examples": [{"user": title, "arguments": {}}],
                "input_schema": input_schema or {"type": "object", "properties": {}},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _catalog_with_many_caps(tmp_path: Path, count: int = 200) -> CapabilityCatalog:
    caps_dir = tmp_path / "capabilities"
    _write_capability(
        caps_dir,
        "pc-server",
        "screenshot",
        "get_screenshot",
        title="Screenshot",
        description="Capture a screenshot of the desktop.",
        aliases=["画面を見る", "画面を見て", "スクショ", "現在の表示確認"],
        tags=["pc", "screenshot", "observe"],
    )
    _write_capability(
        caps_dir,
        "browser-server",
        "page",
        "browse",
        title="Browse with AI",
        description="Use AI agent to browse websites and perform multi-step tasks.",
        aliases=["ブラウザで開いて", "Webページを開く", "サイトを見て", "ページを操作"],
        tags=["browser", "web", "automation"],
        input_schema={
            "type": "object",
            "properties": {"task": {"type": "string"}},
            "required": ["task"],
        },
    )
    for i in range(count - 2):
        _write_capability(
            caps_dir,
            "ai-server",
            f"dummy{i}",
            "run",
            title=f"Dummy Capability {i}",
            description=f"Generic test capability number {i}.",
            tags=["dummy"],
            input_schema={
                "type": "object",
                "properties": {"value": {"type": "string"}},
            },
        )
    return CapabilityCatalog(str(caps_dir))


def test_retrieval_limits_full_schema_with_200_capabilities(tmp_path: Path) -> None:
    catalog = _catalog_with_many_caps(tmp_path, count=200)
    index = CapabilityIndex(catalog, enable_chroma=False)
    retriever = CapabilityRetriever(catalog, index)

    selection = retriever.select_for_request("何か調べて", {}, top_k_schema=8, top_k_summary=50)

    assert len(catalog.list_for_tools()) == 200
    assert len(selection.retrieved_schema_tools) == 8
    assert len(selection.tools) == 11  # ask_user + 2 meta tools + 8 retrieved schemas
    assert len(selection.lightweight_catalog) == 50
    assert all("input_schema" not in item for item in selection.lightweight_catalog)


def test_japanese_alias_finds_screenshot(tmp_path: Path) -> None:
    catalog = _catalog_with_many_caps(tmp_path)
    index = CapabilityIndex(catalog, enable_chroma=False)
    results = index.search("画面を見て", top_k=5)

    assert results[0].document.id == "pc-server.screenshot.get_screenshot"


def test_japanese_alias_finds_browser_browse(tmp_path: Path) -> None:
    catalog = _catalog_with_many_caps(tmp_path)
    index = CapabilityIndex(catalog, enable_chroma=False)
    results = index.search("ブラウザで開いて", top_k=5)

    assert results[0].document.id == "browser-server.page.browse"


def test_keyword_fallback_works_without_chroma(tmp_path: Path) -> None:
    catalog = _catalog_with_many_caps(tmp_path)
    index = CapabilityIndex(catalog, enable_chroma=False)
    results = index.search("スクショ", top_k=3)

    assert any(result.document.id == "pc-server.screenshot.get_screenshot" for result in results)


def test_chroma_query_uses_current_embedding_protocol(tmp_path: Path) -> None:
    catalog = _catalog_with_many_caps(tmp_path, count=12)
    index = CapabilityIndex(
        catalog,
        chroma_path=str(tmp_path / "chroma"),
        enable_chroma=True,
    )

    results = index.search("Capture a screenshot of the desktop", top_k=3)

    assert results
    assert any(result.vector_score > 0 for result in results)
