"""Tests for Folder-Based Capability Registry and Executor."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from aegis_ai.folder_registry import (
    CapabilityManifest,
    ExecutorManifest,
    ExecutionResult,
    FolderCapabilityRegistry,
    ExecutorRegistry,
    _derive_ids,
    _validate,
)


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def caps_dir(tmpdir):
    base = Path(tmpdir) / "capabilities"
    builtin = base / "builtin" / "ai-server" / "agora"
    builtin.mkdir(parents=True)
    (builtin / "read_posts.json").write_text(json.dumps({
        "title": "Read Posts", "description": "Read AGORA posts",
        "server_id": "ai-server", "app_id": "agora", "action": "read_posts",
        "risk": {"level": "low"},
        "tags": ["builtin", "agora"],
    }))
    (builtin / "create_post.json").write_text(json.dumps({
        "title": "Create Post", "description": "Post to AGORA",
        "server_id": "ai-server", "app_id": "agora", "action": "create_post",
        "risk": {"level": "high", "requires_approval": True, "side_effects": ["external_send"]},
    }))

    gen = base / "generated" / "ai-server" / "my_app" / "run"
    gen.mkdir(parents=True)
    (gen.parent / "run.json").write_text(json.dumps({
        "title": "Run App", "description": "Run my app",
        "server_id": "ai-server", "app_id": "my_app", "action": "run",
        "risk": {"level": "low"},
    }))
    return str(base)


@pytest.fixture()
def apps_dir(tmpdir):
    base = Path(tmpdir) / "apps"
    gen = base / "generated" / "hello_app" / "executors"
    gen.mkdir(parents=True)
    (gen / "say_hello.json").write_text(json.dumps({
        "action": "say_hello",
        "type": "command",
        "command": "echo hello",
        "timeout_ms": 5000,
    }))
    (base / "generated" / "hello_app" / "src").mkdir(parents=True)
    return str(base)


class TestDeriveIds:
    def test_valid_path(self, caps_dir):
        path = os.path.join(caps_dir, "builtin", "ai-server", "agora", "read_posts.json")
        ids = _derive_ids(path, caps_dir)
        assert ids["origin"] == "builtin"
        assert ids["server_id"] == "ai-server"
        assert ids["app_id"] == "agora"
        assert ids["action"] == "read_posts"

    def test_invalid_path(self, caps_dir):
        path = os.path.join(caps_dir, "builtin", "too_short.json")
        assert _derive_ids(path, caps_dir) is None


class TestValidate:
    def test_valid(self):
        data = {"server_id": "ai-server", "app_id": "agora", "action": "read_posts"}
        ids = {"server_id": "ai-server", "app_id": "agora", "action": "read_posts"}
        assert _validate(data, ids) == ""

    def test_mismatch(self):
        data = {"server_id": "wrong", "app_id": "agora", "action": "read_posts"}
        ids = {"server_id": "ai-server", "app_id": "agora", "action": "read_posts"}
        assert _validate(data, ids) != ""


class TestFolderCapabilityRegistry:
    def test_load_builtin(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        assert reg.count() >= 2
        cap = reg.get("builtin.ai-server.agora.read_posts")
        assert cap is not None
        assert cap.title == "Read Posts"
        assert cap.origin == "builtin"

    def test_load_generated(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        cap = reg.get("generated.ai-server.my_app.run")
        assert cap is not None
        assert cap.origin == "generated"

    def test_short_name(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        cap = reg.get("agora.read_posts")
        assert cap is not None
        assert cap.capability_id == "builtin.ai-server.agora.read_posts"

    def test_list_by_origin(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        builtin = reg.list_all(origin="builtin")
        generated = reg.list_all(origin="generated")
        assert len(builtin) >= 2
        assert len(generated) >= 1

    def test_requires_approval(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        cap = reg.get("builtin.ai-server.agora.create_post")
        assert cap.requires_approval is True
        assert "external_send" in cap.side_effects

    def test_reload(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        old = reg.count()
        result = reg.reload()
        assert result["new"] == old

    def test_broken_json_skipped(self, caps_dir):
        broken = Path(caps_dir) / "builtin" / "ai-server" / "agora" / "broken.json"
        broken.write_text("not valid json{{{")
        reg = FolderCapabilityRegistry(caps_dir)
        assert len(reg.errors()) >= 1
        assert reg.count() >= 2

    def test_mismatch_id_skipped(self, caps_dir):
        bad = Path(caps_dir) / "builtin" / "ai-server" / "agora" / "bad.json"
        bad.write_text(json.dumps({"server_id": "wrong", "app_id": "agora", "action": "bad"}))
        reg = FolderCapabilityRegistry(caps_dir)
        assert len(reg.errors()) >= 1

    def test_no_registry_json_needed(self, caps_dir):
        assert not (Path(caps_dir) / "registry.json").exists()
        reg = FolderCapabilityRegistry(caps_dir)
        assert reg.count() >= 2


class TestExecutorRegistry:
    def test_load_executor(self, apps_dir):
        reg = ExecutorRegistry(apps_dir)
        assert reg.count() >= 1
        exec_m = reg.get("generated", "hello_app", "say_hello")
        assert exec_m is not None
        assert exec_m.command == "echo hello"

    def test_executor_not_found(self, apps_dir):
        reg = ExecutorRegistry(apps_dir)
        assert reg.get("generated", "hello_app", "nonexistent") is None

    def test_reload(self, apps_dir):
        reg = ExecutorRegistry(apps_dir)
        old = reg.count()
        result = reg.reload()
        assert result["new"] == old


class TestExecutorExecution:
    def test_execute_echo(self, caps_dir, apps_dir):
        cap_reg = FolderCapabilityRegistry(caps_dir)
        exec_reg = ExecutorRegistry(apps_dir)

        cap = cap_reg.get("builtin.ai-server.agora.read_posts")
        result = exec_reg.execute(cap, {"limit": 5})
        assert result.ok is False
        assert result.error["code"] == "EXECUTOR_NOT_FOUND"

    def test_execute_generated(self, caps_dir, apps_dir):
        cap_reg = FolderCapabilityRegistry(caps_dir)
        exec_reg = ExecutorRegistry(apps_dir)

        cap = cap_reg.get("generated.ai-server.my_app.run")
        result = exec_reg.execute(cap, {})
        assert result.ok is False
        assert result.error["code"] == "EXECUTOR_NOT_FOUND"


class TestCapabilityIdFormat:
    def test_full_id_format(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        cap = reg.get("builtin.ai-server.agora.read_posts")
        assert cap.capability_id == "builtin.ai-server.agora.read_posts"

    def test_short_name_format(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        cap = reg.get("builtin.ai-server.agora.read_posts")
        assert cap.short_name == "agora.read_posts"


class TestOriginGenerated:
    def test_generated_origin(self, caps_dir):
        reg = FolderCapabilityRegistry(caps_dir)
        gen_caps = reg.list_all(origin="generated")
        for cap in gen_caps:
            assert cap.origin == "generated"
            assert cap.capability_id.startswith("generated.")
