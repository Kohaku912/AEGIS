"""Browser-Use Agent — executes browser tasks using browser-use.

This is the core of the Browser Server.
It receives BrowserTasks from AEGIS Core and executes them
using browser-use (LLM + Playwright).

Architecture:
- Receives natural language BrowserTask
- Creates safety boundary from task constraints
- Passes task to browser-use with safety instructions
- Monitors execution for safety violations
- Returns structured BrowserTaskResult
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

from aegis_browser.config import Config
from aegis_browser.safety_boundary import BrowserSafetyBoundary, SafetyCheckResult
from aegis_browser.session import BrowserSession as AegisBrowserSession
from aegis_browser.task_models import BrowserTask, BrowserTaskResult, TaskStatus
from aegis_browser.trace import BrowserTrace

logger = logging.getLogger("aegis_browser.browser_use_agent")

_models_patched = False


def _patch_browser_use_models():
    """Patch browser-use to normalize DeepSeek's simplified JSON format.

    DeepSeek returns {"click": 811} instead of {"click": {"index": 811}}.
    This normalizes the JSON before Pydantic validation.
    """
    global _models_patched
    if _models_patched:
        return

    import json as _json

    _ACTION_KEYS_TO_NORMALIZE = {
        "click", "input", "scroll", "upload_file",
        "get_dropdown_options", "select_dropdown_option",
        "find_elements", "find_text", "read_file",
        "write_file", "replace_file",
    }

    def _normalize_action(json_obj):
        if not isinstance(json_obj, dict):
            return json_obj
        new_action = {}
        for key, value in json_obj.items():
            if isinstance(value, (int, float)) and key in _ACTION_KEYS_TO_NORMALIZE:
                new_action[key] = {"index": int(value)}
            elif key == "wait" and isinstance(value, dict) and "ms" in value:
                new_action[key] = {"seconds": value["ms"] / 1000}
            elif key == "select_dropdown_option" and isinstance(value, dict):
                if "index" in value and isinstance(value["index"], (int, float)):
                    value["index"] = int(value["index"])
                new_action[key] = value
            else:
                new_action[key] = value
        return new_action

    def _normalize_json(json_str):
        try:
            clean = json_str.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()
            elif clean.startswith("\n"):
                clean = clean.strip()
                if clean.startswith("```"):
                    lines = clean.split("\n")
                    clean = "\n".join(lines[1:])
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    clean = clean.strip()

            data = _json.loads(clean)
        except _json.JSONDecodeError:
            return json_str

        if not isinstance(data, dict):
            return json_str

        if "action" in data:
            actions = data["action"]
            if isinstance(actions, list):
                data["action"] = [_normalize_action(a) for a in actions]
            return _json.dumps(data)

        normalized = {}
        for key, value in data.items():
            if key in _ACTION_KEYS_TO_NORMALIZE:
                if isinstance(value, (int, float)):
                    normalized[key] = {"index": int(value)}
                elif isinstance(value, dict):
                    normalized[key] = _normalize_action({key: value})[key]
                else:
                    normalized[key] = value
            else:
                normalized[key] = value
        return _json.dumps(normalized)

    from browser_use.llm.openai import chat as openai_chat

    original_model_validate_json = None
    try:
        from pydantic import BaseModel
        original_model_validate_json = BaseModel.model_validate_json.__func__ if hasattr(BaseModel.model_validate_json, '__func__') else None
    except Exception:
        pass

    def _patched_model_validate_json(cls, json_data, **kwargs):
        if isinstance(json_data, str):
            json_data = _normalize_json(json_data)
        if original_model_validate_json:
            return original_model_validate_json(cls, json_data, **kwargs)
        return cls.__pydantic_validator__.validate_json(json_data)

    from pydantic import BaseModel
    BaseModel.model_validate_json = classmethod(_patched_model_validate_json)

    original_ainvoke = openai_chat.ChatOpenAI.ainvoke

    async def patched_ainvoke(self, messages, output_format=None, **kwargs):
        result = await original_ainvoke(self, messages, output_format=output_format, **kwargs)

        if output_format is not None and hasattr(result, "completion"):
            completion = result.completion
            if isinstance(completion, str):
                normalized = _normalize_json(completion)
                if normalized != completion:
                    from browser_use.llm.views import ChatInvokeCompletion
                    try:
                        parsed = output_format.model_validate_json(normalized)
                        return ChatInvokeCompletion(
                            completion=parsed,
                            usage=getattr(result, "usage", None),
                            stop_reason=getattr(result, "stop_reason", None),
                        )
                    except Exception:
                        return result

        return result

    openai_chat.ChatOpenAI.ainvoke = patched_ainvoke
    _models_patched = True


class BrowserUseAgent:
    """Executes browser tasks using browser-use.

    Usage:
        agent = BrowserUseAgent(llm_client=llm)
        result = agent.run_task(task)
    """

    def __init__(
        self,
        llm_client: Any = None,
        session: AegisBrowserSession | None = None,
        trace_dir: str | None = None,
        config: Config | None = None,
    ) -> None:
        self._config = config or Config()
        self._llm = llm_client
        self._session = session or AegisBrowserSession(
            session_id=self._config.browser_profile_name,
            profile_dir=self._config.browser_profile_root,
            session_dir=self._config.browser_session_root,
        )
        self._session.ensure_dirs()
        self._session.load_state()
        self._trace_dir = trace_dir or self._config.browser_trace_root
        self._current_task: BrowserTask | None = None
        self._current_trace: BrowserTrace | None = None
        self._running = False

    def run_task(self, task: BrowserTask) -> BrowserTaskResult:
        """Run a browser task synchronously."""
        try:
            return asyncio.run(self._run_task_async(task))
        except Exception as e:
            return BrowserTaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def _run_task_async(self, task: BrowserTask) -> BrowserTaskResult:
        """Run a browser task asynchronously."""
        start = time.perf_counter()
        self._current_task = task
        self._running = True

        # Create trace
        trace = BrowserTrace(task_id=task.task_id, output_dir=self._trace_dir)
        self._current_trace = trace

        # Create safety boundary
        boundary = BrowserSafetyBoundary(task)

        result = BrowserTaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            trace_id=trace.task_id,
        )

        try:
            trace.record("start", f"Starting task: {task.natural_language_goal[:100]}")

            browser_result = await self._execute_with_browser_use(task, boundary, trace)

            result.result_text = browser_result.get("text", "")
            result.extracted_data = browser_result.get("data", {})
            result.actions_taken = boundary.get_actions_taken()

            if browser_result.get("needs_user_input"):
                result.status = TaskStatus.NEEDS_USER_INPUT
                result.needs_user_input_for = [browser_result.get("user_input_reason", "User intervention required")]
                trace.record("user_input_needed", browser_result.get("user_input_reason", ""))
            else:
                result.status = TaskStatus.COMPLETED

            result.duration_ms = (time.perf_counter() - start) * 1000

            trace.record("complete", f"Task completed in {result.duration_ms:.0f}ms")

        except SafetyStop as e:
            result.status = TaskStatus.STOPPED
            result.stopped_reason = str(e)
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("safety_stop", str(e))

        except ApprovalBoundary as e:
            result.status = TaskStatus.NEEDS_APPROVAL
            result.needs_approval_for = [str(e)]
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("approval_needed", str(e))

        except UserInputNeeded as e:
            result.status = TaskStatus.NEEDS_USER_INPUT
            result.needs_user_input_for = [str(e)]
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("user_input_needed", str(e))

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("error", str(e))

        finally:
            self._running = False
            # Save trace
            try:
                trace.save()
            except Exception:
                pass

        return result

    def _build_task_with_safety(self, task: BrowserTask) -> str:
        """Build full task description with safety instructions."""
        parts = [
            f"Task: {task.natural_language_goal}",
            "",
            "SAFETY RULES (MUST FOLLOW):",
        ]

        # Add forbidden actions
        if task.forbidden_actions:
            parts.append("\nFORBIDDEN (STOP IMMEDIATELY if encountered):")
            for action in task.forbidden_actions:
                parts.append(f"  - DO NOT {action.replace('_', ' ')}")

        # Add stop conditions
        if task.stop_conditions:
            parts.append("\nSTOP CONDITIONS (STOP if detected):")
            for condition in task.stop_conditions:
                parts.append(f"  - {condition.replace('_', ' ')}")

        # Add allowed actions
        if task.allowed_actions:
            parts.append("\nALLOWED ACTIONS:")
            for action in task.allowed_actions:
                parts.append(f"  - {action.replace('_', ' ')}")

        # Add target domains
        if task.target_domains:
            parts.append(f"\nTARGET DOMAINS: {', '.join(task.target_domains)}")

        # Add user context
        if task.user_context:
            parts.append(f"\nUSER CONTEXT: {task.user_context}")

        # Add privacy constraints
        if task.privacy_constraints:
            parts.append("\nPRIVACY CONSTRAINTS:")
            for constraint in task.privacy_constraints:
                parts.append(f"  - {constraint}")

        parts.append("\nIMPORTANT: If you encounter payment or identity verification, STOP and report what you found. CAPTCHA solving is allowed.")

        return "\n".join(parts)

    async def _execute_with_browser_use(
        self,
        task: BrowserTask,
        boundary: BrowserSafetyBoundary,
        trace: BrowserTrace,
    ) -> dict[str, Any]:
        """Execute task using browser-use."""
        from browser_use import Agent
        from browser_use.llm.openai.chat import ChatOpenAI

        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        config = {}
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)

        llm_config = config.get("llm", {})
        api_key = (
            os.environ.get("LLM_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
            or llm_config.get("api_key")
            or ""
        )
        base_url = (
            os.environ.get("LLM_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or llm_config.get("base_url")
            or "https://api.deepseek.com"
        )
        model = os.environ.get("LLM_MODEL") or llm_config.get("model", "deepseek-v4-flash")

        if not api_key:
            return {"text": "Error: No API key configured. Set OPENAI_API_KEY or edit browser-server/config.json", "data": {}}

        base_llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            dont_force_structured_output=True,
        )

        _patch_browser_use_models()

        llm = base_llm

        trace.record("browser_use_start", "Starting browser-use agent")

        from browser_use import BrowserProfile, BrowserSession

        profile = BrowserProfile(
            keep_alive=True,
            headless=self._config.browser_headless,
            channel=self._config.browser_channel,
            user_data_dir=str(self._session.profile_dir),
            traces_dir=self._trace_dir,
        )
        session = BrowserSession(
            id=self._session.session_id,
            browser_profile=profile,
        )

        full_task = self._build_task_with_safety(task)

        agent = Agent(
            task=full_task,
            llm=llm,
            max_actions_per_step=5,
            browser_session=session,
            use_vision=True,
            enable_planning=True,
        )
        result = await agent.run(max_steps=task.max_steps)

        trace.record("browser_use_complete", f"Result: {str(result)[:200]}")
        self._session.record_page_visit(task.natural_language_goal[:200])
        self._session.save_state()

        result_text = str(result)
        needs_user_input = False
        user_input_reason = ""
        completed_without_user_input = self._completed_without_user_input(result, result_text)

        verification_patterns = [
            "verify your identity",
            "verify your phone",
            "phone verification",
            "scan the qr code",
            "scan qr",
            "verification code",
            "enter the code",
            "two-factor",
            "2fa",
            "captcha",
            "prove you are human",
            "verify you are human",
        ]
        result_lower = result_text.lower()
        if not completed_without_user_input:
            for pattern in verification_patterns:
                if pattern in result_lower:
                    needs_user_input = True
                    user_input_reason = f"Verification required: {pattern}"
                    break

        return {
            "text": result_text,
            "data": {},
            "needs_user_input": needs_user_input,
            "user_input_reason": user_input_reason,
        }

    @staticmethod
    def _completed_without_user_input(result: Any, result_text: str = "") -> bool:
        """Return True when browser-use reports successful completion."""
        all_results = getattr(result, "all_results", None) or []
        if all_results:
            final = all_results[-1]
            if getattr(final, "success", None) is not True:
                return False
            judgement = getattr(final, "judgement", None)
            return getattr(judgement, "reached_captcha", False) is False
        return "success=True" in result_text and "reached_captcha=False" in result_text

    def stop(self) -> None:
        """Stop current task execution."""
        self._running = False
        if self._current_trace:
            self._current_trace.record("stopped", "Task stopped by user")

    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._running


# ── Custom exceptions ──────────────────────────────────────


class SafetyStop(Exception):
    """Raised when safety boundary detects a stop condition."""
    pass


class ApprovalBoundary(Exception):
    """Raised when an approval boundary is hit."""
    pass


class UserInputNeeded(Exception):
    """Raised when user input is needed (password, 2FA)."""
    pass
