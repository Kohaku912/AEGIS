"""Tests for Real LLM and Memory integration."""

from __future__ import annotations

import os
import tempfile

from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.memory.factory import (
    create_episodic_memory,
    create_procedural_memory,
    create_reflection_log,
    create_semantic_memory,
)
from aegis_ai.memory.semantic import Fact


class TestLLMFactory:
    """LLM provider factory tests."""

    def test_create_mock_provider(self):
        """Creates mock provider when no API key."""
        provider = create_llm_provider(provider_name="mock")
        assert provider is not None

    def test_mock_provider_responds(self):
        """Mock provider generates responses."""
        provider = create_llm_provider(provider_name="mock")
        response = provider.generate(prompt="Hello")
        assert response.success is True
        assert len(response.content) > 0

    def test_create_with_env_key(self):
        """Creates provider with env API key."""
        old_key = os.environ.get("OPENAI_API_KEY")
        try:
            os.environ["OPENAI_API_KEY"] = "test-key"
            provider = create_llm_provider(provider_name="openai", api_key="test-key")
            assert provider is not None
        finally:
            if old_key:
                os.environ["OPENAI_API_KEY"] = old_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)


class TestMemoryFactory:
    """Memory factory tests."""

    def test_create_semantic_jsonl(self):
        """Creates JSONL semantic memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = create_semantic_memory(
                path=f"{tmpdir}/semantic.jsonl",
                use_chroma=False,
            )
            assert mem is not None

    def test_create_episodic(self):
        """Creates episodic memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = create_episodic_memory(path=f"{tmpdir}/episodic.jsonl")
            assert mem is not None

    def test_create_procedural(self):
        """Creates procedural memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = create_procedural_memory(path=f"{tmpdir}/procedural.jsonl")
            assert mem is not None

    def test_create_reflection(self):
        """Creates reflection log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = create_reflection_log(path=f"{tmpdir}/reflection.jsonl")
            assert mem is not None

    def test_semantic_add_and_search(self):
        """Semantic memory can add and search facts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = create_semantic_memory(
                path=f"{tmpdir}/semantic.jsonl",
                use_chroma=False,
            )
            mem.add(Fact(content="User prefers dark mode", category="preference"))
            results = mem.search("dark mode")
            assert len(results) >= 1

    def test_chroma_fallback(self):
        """Falls back to JSONL when Chroma unavailable."""
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            mem = create_semantic_memory(
                path=f"{tmpdir}/semantic.jsonl",
                use_chroma=True,
                chroma_path=f"{tmpdir}/chroma",
            )
            # Should still work (either Chroma or JSONL)
            mem.add(Fact(content="Test fact", category="general"))
            results = mem.search("test")
            assert len(results) >= 1
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
