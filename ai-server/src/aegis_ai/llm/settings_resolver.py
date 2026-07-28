"""LLM Settings Resolver — loads and validates LLM profiles from YAML config."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class LLMSettings:
    """Resolved LLM configuration for a single call."""

    provider: str = "openai"
    model: str = "deepseek-v4-flash"
    api_key_env: str = ""
    base_url: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    reasoning_level: str = "medium"
    timeout_seconds: int = 30
    max_tool_rounds: int = 5


class LLMSettingsResolver:
    """Resolves LLM settings from YAML profiles with safety validation."""

    def __init__(self, llm_path: str, policy_engine: Any = None) -> None:
        self._path = Path(llm_path)
        self._policy = policy_engine
        self._lock = threading.Lock()
        self._profiles: dict[str, dict[str, Any]] = {}
        self._safety: dict[str, Any] = {}
        self._mode: str = "cloud"
        self._mtime: float = 0.0
        self._load()

    def _load(self) -> bool:
        """Load profiles from YAML file. Returns True if successful."""
        try:
            data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                logger.error("Invalid LLM config file")
                return False

            profiles = data.get("profiles", {})
            safety = data.get("safety", {})

            if not isinstance(profiles, dict):
                logger.error("Invalid LLM config: 'profiles' must be a dict")
                return False
            if not isinstance(safety, dict):
                logger.error("Invalid LLM config: 'safety' must be a dict")
                return False

            with self._lock:
                self._profiles = profiles
                self._safety = safety
                self._mode = data.get("mode", "cloud")
                self._mtime = self._path.stat().st_mtime

            logger.info("Loaded %d LLM profiles from %s (mode=%s)", len(profiles), self._path, self._mode)
            return True
        except FileNotFoundError:
            logger.error("LLM config file not found: %s", self._path)
            return False
        except Exception as exc:
            logger.error("Failed to load LLM config: %s", exc)
            return False

    # Profile name mapping: cloud profile → local profile
    _LOCAL_PROFILE_MAP: dict[str, str] = {
        "chat_balanced": "local_chat",
        "tool_planning": "local_tool_planning",
        "json_generation": "local_json_generation",
        "decision": "local_decision",
        "long_answer": "local_long_answer",
        "self_development": "local_chat",
        "task_analysis": "local_tool_planning",
    }

    def resolve(self, call_type: str = None, profile_id: str = None) -> LLMSettings:
        """Resolve LLM settings by call_type or profile_id."""
        del call_type

        with self._lock:
            mode = self._mode
            if profile_id:
                # In local mode, remap cloud profile names to local profiles
                if mode == "local" and profile_id in self._LOCAL_PROFILE_MAP:
                    local_name = self._LOCAL_PROFILE_MAP[profile_id]
                    if local_name in self._profiles:
                        profile_id = local_name
                if profile_id not in self._profiles:
                    raise KeyError(f"Profile '{profile_id}' not found")
                profile = dict(self._profiles[profile_id])
            else:
                default = "local_chat" if mode == "local" else "chat_balanced"
                profile = dict(self._profiles.get(default, {}))

        settings = LLMSettings(
            provider=profile.get("provider", "openai"),
            model=profile.get("model", "deepseek-v4-flash"),
            api_key_env=profile.get("api_key_env", ""),
            base_url=profile.get("base_url", ""),
            max_tokens=int(profile.get("max_tokens", 4096)),
            temperature=float(profile.get("temperature", 0.7)),
            reasoning_level=profile.get("reasoning_level", "medium"),
            timeout_seconds=int(profile.get("timeout_seconds", 30)),
            max_tool_rounds=int(profile.get("max_tool_rounds", 5)),
        )

        if not self.validate(settings):
            raise ValueError(f"Resolved LLM settings failed validation for profile {profile_id or 'chat_balanced'}")

        return settings

    def validate(self, settings: LLMSettings) -> bool:
        """Validate LLM settings against safety constraints."""
        with self._lock:
            upper = self._safety.get("max_tokens_upper_bound", 128000)
            min_temp = self._safety.get("min_temperature", 0.0)
            max_temp = self._safety.get("max_temperature", 2.0)
            allowed = list(self._safety.get("allowed_models", []))

        if settings.max_tokens < 1 or settings.max_tokens > upper:
            logger.warning("Invalid max_tokens: %s (range: 1-%s)", settings.max_tokens, upper)
            return False

        if settings.temperature < min_temp or settings.temperature > max_temp:
            logger.warning(
                "Invalid temperature: %s (range: %s-%s)",
                settings.temperature,
                min_temp,
                max_temp,
            )
            return False

        if allowed and settings.model not in allowed:
            logger.warning("Model '%s' not in allowed list: %s", settings.model, allowed)
            return False

        return True

    def get_allowed_models(self) -> list[str]:
        """Get list of allowed models."""
        with self._lock:
            return list(self._safety.get("allowed_models", []))

    def get_max_tokens_upper_bound(self) -> int:
        """Get max_tokens upper bound."""
        with self._lock:
            return int(self._safety.get("max_tokens_upper_bound", 128000))

    def reload(self) -> bool:
        """Hot reload profiles from file. Returns True if successful."""
        try:
            current_mtime = self._path.stat().st_mtime
            if current_mtime <= self._mtime:
                return True

            logger.info("Detected LLM config file change, reloading...")
            if self._load():
                logger.info("LLM config reloaded successfully")
                return True

            logger.warning("LLM config reload failed, keeping previous config")
            return False
        except Exception as exc:
            logger.error("Failed to reload LLM config: %s", exc)
            return False
