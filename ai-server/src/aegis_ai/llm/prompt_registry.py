"""Prompt Registry — loads and manages prompt templates from YAML config."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class PromptRegistry:
    """Manages prompt templates loaded from a YAML configuration file.

    Supports hot reload, validation, and protected prompt enforcement.
    """

    def __init__(self, prompts_path: str) -> None:
        self._path = Path(prompts_path)
        self._history_path = self._path.with_suffix(".history.jsonl")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._prompts: dict[str, dict[str, Any]] = {}
        self._file_version: str = "1.0.0"
        self._mtime: float = 0.0
        self._load()

    def _validate_prompt(self, prompt_id: str, prompt: Any) -> bool:
        if not isinstance(prompt, dict):
            logger.error("Invalid prompt '%s': must be a dict", prompt_id)
            return False

        template = prompt.get("template")
        if not isinstance(template, str):
            logger.error("Invalid prompt '%s': missing or invalid 'template'", prompt_id)
            return False

        version = prompt.get("version")
        if not isinstance(version, str) or not version:
            logger.error("Invalid prompt '%s': missing or invalid 'version'", prompt_id)
            return False

        editable = prompt.get("editable", True)
        if not isinstance(editable, bool):
            logger.error("Invalid prompt '%s': 'editable' must be a bool", prompt_id)
            return False

        protected = prompt.get("protected", False)
        if not isinstance(protected, bool):
            logger.error("Invalid prompt '%s': 'protected' must be a bool", prompt_id)
            return False

        return True

    def _read_payload(self) -> tuple[str, dict[str, dict[str, Any]], float] | None:
        if not self._path.exists():
            logger.error("Prompts file not found: %s", self._path)
            return None

        data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.error("Invalid prompts file: root must be a dict")
            return None

        file_version = data.get("version")
        if not isinstance(file_version, str) or not file_version:
            logger.error("Invalid prompts file: missing or invalid 'version'")
            return None

        prompts = data.get("prompts")
        if not isinstance(prompts, dict):
            logger.error("Invalid prompts file: 'prompts' must be a dict")
            return None

        validated: dict[str, dict[str, Any]] = {}
        for prompt_id, prompt in prompts.items():
            if not self._validate_prompt(prompt_id, prompt):
                return None
            validated[prompt_id] = dict(prompt)

        return file_version, validated, self._path.stat().st_mtime

    def _load(self) -> bool:
        """Load prompts from YAML file. Returns True if successful."""
        try:
            payload = self._read_payload()
            if payload is None:
                return False

            file_version, prompts, mtime = payload
            with self._lock:
                self._file_version = file_version
                self._prompts = prompts
                self._mtime = mtime

            logger.info("Loaded %s prompts from %s", len(prompts), self._path)
            return True
        except Exception as e:
            logger.error("Failed to load prompts: %s", e)
            return False

    def get(self, prompt_id: str) -> dict[str, Any]:
        """Get prompt by ID. Returns dict with template, version, editable, protected."""
        with self._lock:
            if prompt_id not in self._prompts:
                raise KeyError(f"Prompt '{prompt_id}' not found")
            return dict(self._prompts[prompt_id])

    def render(self, prompt_id: str, **variables: str) -> str:
        """Render prompt template with variables using {{variable}} syntax."""
        prompt = self.get(prompt_id)
        template = prompt["template"]
        for key, value in variables.items():
            template = template.replace("{{" + key + "}}", str(value))
        return template

    def get_metadata(self, prompt_id: str) -> dict[str, Any]:
        """Get prompt metadata: prompt_id, version, hash."""
        prompt = self.get(prompt_id)
        template = prompt["template"]
        return {
            "prompt_id": prompt_id,
            "version": prompt.get("version", "unknown"),
            "hash": hashlib.sha256(template.encode("utf-8")).hexdigest()[:16],
        }

    def reload(self) -> bool:
        """Hot reload prompts from file. Returns True if successful."""
        try:
            current_mtime = self._path.stat().st_mtime
            with self._lock:
                previous_mtime = self._mtime
            if current_mtime <= previous_mtime:
                return True

            logger.info("Detected prompts file change, reloading...")
            if self._load():
                logger.info("Prompts reloaded successfully")
                return True

            logger.warning("Prompts reload failed, keeping previous config")
            return False
        except Exception as e:
            logger.error("Failed to reload prompts: %s", e)
            return False

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all prompts with metadata."""
        with self._lock:
            return [self.get_metadata(prompt_id) for prompt_id in self._prompts]

    def update_prompt(self, prompt_id: str, template: str) -> bool:
        """Update prompt template. Returns False if protected."""
        with self._lock:
            if prompt_id not in self._prompts:
                raise KeyError(f"Prompt '{prompt_id}' not found")

            prompt = self._prompts[prompt_id]
            if prompt.get("protected", False) or not prompt.get("editable", True):
                logger.warning("Cannot update protected prompt '%s'", prompt_id)
                return False

            original_template = prompt["template"]
            prompt["template"] = template

            data = {"version": self._file_version, "prompts": self._prompts}
            tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")

            try:
                tmp_path.write_text(
                    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                tmp_path.replace(self._path)
                self._mtime = self._path.stat().st_mtime
                self._append_revision(prompt_id, original_template, template, action="update")
                return True
            except Exception as e:
                prompt["template"] = original_template
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass
                logger.error("Failed to save prompts: %s", e)
                return False

    def validate_candidate(self, prompt_id: str, template: str) -> dict[str, Any]:
        """Validate a candidate template without changing the registry."""
        current = self.get(prompt_id)
        required = set(re.findall(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}", current["template"]))
        provided = set(re.findall(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}", template))
        missing = sorted(required - provided)
        errors: list[str] = []
        if not template.strip():
            errors.append("Template must not be empty.")
        if len(template) > 200_000:
            errors.append("Template exceeds the 200000 character management limit.")
        if template.count("{{") != template.count("}}"):
            errors.append("Template variable braces are unbalanced.")
        if missing:
            errors.append(f"Required variables removed: {', '.join(missing)}")
        return {
            "valid": not errors,
            "errors": errors,
            "required_variables": sorted(required),
            "candidate_variables": sorted(provided),
            "current_hash": self.get_metadata(prompt_id)["hash"],
            "candidate_hash": hashlib.sha256(template.encode("utf-8")).hexdigest()[:16],
        }

    def list_versions(self, prompt_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return persisted revisions for one prompt, newest first."""
        self.get(prompt_id)
        if not self._history_path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in self._history_path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("prompt_id") == prompt_id:
                records.append(record)
        return sorted(records, key=lambda item: int(item.get("created_at", 0)), reverse=True)[: max(1, limit)]

    def rollback_prompt(self, prompt_id: str, revision_id: str) -> bool:
        """Restore the template captured before a persisted revision."""
        revision = next(
            (item for item in self.list_versions(prompt_id, limit=500) if item["revision_id"] == revision_id), None
        )
        if revision is None:
            raise KeyError(f"Revision '{revision_id}' not found")
        return self.update_prompt(prompt_id, str(revision["before_template"]))

    def _append_revision(self, prompt_id: str, before_template: str, after_template: str, *, action: str) -> None:
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "revision_id": f"pr_{uuid.uuid4().hex[:12]}",
            "prompt_id": prompt_id,
            "action": action,
            "created_at": int(time.time() * 1000),
            "before_hash": hashlib.sha256(before_template.encode("utf-8")).hexdigest()[:16],
            "after_hash": hashlib.sha256(after_template.encode("utf-8")).hexdigest()[:16],
            "before_template": before_template,
        }
        with self._history_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")


__all__ = ["PromptRegistry"]
