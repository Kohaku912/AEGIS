"""OpenHands SDK adapter — Phase 2.

**import 境界の不変条件 (instruction.md §6, §35.4)**
- `from openhands.*` は **このファイルにだけ** 書く。
- バージョンアップ時に触るのも **このファイルだけ** に閉じる (DoD).
- 他の backend / core ファイルは `adapter.py` の関数だけ利用する。

提供する関数:
- `build_llm(llm_config)` → openhands.sdk.LLM
- `build_agent(llm_config, tool_names)` → openhands.sdk.Agent
- `build_workspace(workspace_spec, base_dir)` → openhands.sdk.Workspace
- `run_conversation(...)` → openhands Conversation を blocking 実行
- `collect_events(conversation)` → List[dict] (event を AEGIS 形に正規化)
- `is_openhands_available()` → bool (CI で optional dep を扱う)

adapter は OpenHands の型 (LLM / Agent / Conversation / Event) を **絶対に外に
漏らさない**。戻り値は必ず JSON-able な dict か AEGIS の dataclass にする。
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Callable

from aegis_ai.agents.backends.openhands.config import WorkspaceSpec
from aegis_ai.agents.runtime.models import AgentTask

logger = logging.getLogger("aegis_ai.agents.backends.openhands.adapter")
_ENV_LOADED = False


# ---------------------------------------------------------------------------
# Public surface — AEGIS core / backend から呼ばれる API
# ---------------------------------------------------------------------------


def is_openhands_available() -> bool:
    """`openhands.sdk` が import 可能か検査する.

    CI 環境や openhands-sdk 未インストール環境で backend を register しても
    落ちないようにするための guard.
    """
    try:
        from openhands.sdk import LLM  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def build_llm(llm_config: dict[str, Any]) -> Any:
    """AgentTask.metadata["llm"] → openhands.sdk.LLM.

    必要な key: model, api_key_env (env var name), base_url (optional).
    SecretStr は openhands 側で吸収される。
    """
    from openhands.sdk import LLM

    api_key_env = llm_config.get("api_key_env", "LLM_API_KEY")
    api_key = _resolve_api_key(str(api_key_env))
    if not api_key:
        raise RuntimeError(
            f"OpenHands backend: LLM api_key not set "
            f"(api_key_env={api_key_env!r}, LLM_API_KEY env)"
        )
    return LLM(
        model=_normalize_model_name(
            llm_config.get("model", os.environ.get("LLM_MODEL", "gpt-4o-mini")),
            llm_config.get("provider"),
        ),
        api_key=api_key,
        base_url=llm_config.get("base_url", os.environ.get("LLM_BASE_URL")),
        usage_id="agent",
    )


def build_agent(llm: Any, tool_names: list[str]) -> Any:
    """`openhands.sdk.Agent` を組み立てる.

    tool_names は OpenHands の tool registry に登録された name だけ許可する。
    現行 SDK では `openhands-tools` 側の import 時に registry 登録されるため、
    まず built-in tools を登録してから `Tool(name=...)` を組み立てる。
    """
    from openhands.sdk import Agent, Tool, list_registered_tools
    from openhands.tools import register_default_tools

    register_default_tools(enable_browser=False)
    registered = set(list_registered_tools())
    tools: list[Tool] = []
    for name in tool_names:
        tool_name = str(name or "")
        if not tool_name:
            continue
        if tool_name not in registered:
            _import_tool_module(tool_name)
            registered = set(list_registered_tools())
        if tool_name not in registered:
            logger.warning("OpenHands tool not found, skipping: %s", name)
            continue
        tools.append(Tool(name=tool_name))
    return Agent(llm=llm, tools=tools)


def build_workspace(workspace: WorkspaceSpec, base_dir: str) -> Any:
    """WorkspaceSpec → openhands.sdk.Workspace.

    Phase 2 の DoD では LocalWorkspace のみ対応。
    PERSISTENT mode は `path` を尊重。READ_ONLY の場合は
    OpenHands 側に read-only mount を伝える (将来拡張、ここでは path を返すだけ)。
    """
    from openhands.sdk import LocalWorkspace

    target = workspace.path or base_dir
    # Note: OpenHands 1.46 の LocalWorkspace は working_dir のみ。
    # mount_ro / protected_paths は Phase 6 で capability bridge 側に実装する。
    return LocalWorkspace(working_dir=target)


def run_conversation(
    *,
    agent: Any,
    workspace: Any,
    prompt: str,
    timeout_seconds: int,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    on_conversation_ready: Callable[[Any], None] | None = None,
    should_interrupt: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """`conversation.send_message` + `conversation.run()` を blocking で実行.

    戻り値: AEGIS 形に正規化した event 配列を含む dict.
    {"events": [...], "elapsed_ms": int, "raw_status": str}
    """
    from openhands.sdk import Conversation

    started = time.monotonic()
    conversation = Conversation(agent=agent, workspace=workspace)
    if on_conversation_ready is not None:
        try:
            on_conversation_ready(conversation)
        except Exception:  # noqa: BLE001
            logger.debug("on_conversation_ready callback raised", exc_info=True)
    conversation.send_message(prompt)

    interrupted = False
    failure: BaseException | None = None

    def _run_async() -> None:
        nonlocal failure
        try:
            asyncio.run(conversation.arun())
        except BaseException as exc:  # noqa: BLE001
            failure = exc

    worker = threading.Thread(target=_run_async, name="openhands-arun", daemon=True)
    worker.start()
    while worker.is_alive():
        worker.join(0.1)
        if interrupted or should_interrupt is None or not should_interrupt():
            continue
        try:
            conversation.interrupt()
            interrupted = True
        except Exception:  # noqa: BLE001
            logger.debug("conversation.interrupt() failed", exc_info=True)

    if failure is not None:
        raise failure

    elapsed_ms = int((time.monotonic() - started) * 1000)

    events = collect_events(conversation)
    if on_progress is not None:
        try:
            on_progress(
                {
                    "stage": "cancelled" if interrupted else "completed",
                    "elapsed_ms": elapsed_ms,
                    "event_count": len(events),
                    "cancelled": interrupted,
                }
            )
        except Exception:  # noqa: BLE001
            logger.debug("on_progress callback raised", exc_info=True)

    return {
        "events": events,
        "elapsed_ms": elapsed_ms,
        "raw_status": _safe_status(conversation),
        "cancelled": interrupted,
    }


# ---------------------------------------------------------------------------
# Helpers (internal)
# ---------------------------------------------------------------------------


def _load_project_env() -> None:
    """Load repo `.env` once so standalone agent-server processes see LLM keys."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        _ENV_LOADED = True
        return
    for env_path in _project_env_paths():
        if env_path.exists():
            load_dotenv(env_path, override=False)
            break
    _ENV_LOADED = True


def _project_env_paths() -> tuple[Path, ...]:
    return (
        Path(__file__).resolve().parents[6] / ".env",
        Path(__file__).resolve().parents[5] / ".env",
    )


def _read_project_env_value(name: str) -> str:
    try:
        from dotenv import dotenv_values
    except ImportError:
        return ""
    for env_path in _project_env_paths():
        if not env_path.exists():
            continue
        try:
            values = dotenv_values(env_path)
        except Exception:  # noqa: BLE001
            logger.debug("Failed to parse .env from %s", env_path, exc_info=True)
            continue
        value = values.get(name)
        if isinstance(value, str) and value:
            return value
    return ""


def _resolve_api_key(api_key_env: str) -> str:
    api_key = os.environ.get(api_key_env, "") or os.environ.get("LLM_API_KEY", "")
    if api_key:
        return api_key
    _load_project_env()
    api_key = os.environ.get(api_key_env, "") or os.environ.get("LLM_API_KEY", "")
    if api_key:
        return api_key
    if api_key_env != "LLM_API_KEY":
        api_key = _read_project_env_value(api_key_env)
        if api_key:
            return api_key
    return _read_project_env_value("LLM_API_KEY")


def _import_tool_module(name: str) -> None:
    """Best-effort import so packages that self-register on import become visible."""
    try:
        __import__(f"openhands.tools.{name}", fromlist=["__name__"])
    except Exception:  # noqa: BLE001
        logger.debug("OpenHands tool import failed for %s", name, exc_info=True)


def _normalize_model_name(model: Any, provider: Any) -> str:
    """Convert AEGIS profile metadata into the provider/model form LiteLLM expects."""
    model_name = str(model or os.environ.get("LLM_MODEL", "gpt-4o-mini"))
    if "/" in model_name:
        return model_name
    provider_name = str(provider or "").strip().lower()
    if provider_name in {"", "mock"}:
        return model_name
    # AEGIS routes most hosted models through the OpenAI-compatible provider.
    if provider_name in {"openai", "deepseek"}:
        return f"openai/{model_name}"
    return f"{provider_name}/{model_name}"


def _safe_status(conversation: Any) -> str:
    """Conversation の現在の status を取り出す (version 差分を吸収)."""
    state = getattr(conversation, "state", None)
    if state is None:
        return "unknown"
    exec_status = getattr(state, "execution_status", None)
    if exec_status is not None:
        return getattr(exec_status, "name", str(exec_status))
    return getattr(state, "status", "unknown")


def collect_events(conversation: Any) -> list[dict[str, Any]]:
    """OpenHands の Event 列を AEGIS の dict 形に正規化する.

    OpenHands 内部の型は外に出さない (instruction.md §6 ルール).
    """
    state = getattr(conversation, "state", None)
    raw_events = getattr(state, "events", []) if state is not None else []
    out: list[dict[str, Any]] = []
    for ev in raw_events:
        try:
            out.append(_normalize_event(ev))
        except Exception:  # noqa: BLE001
            logger.debug("event normalization failed", exc_info=True)
            out.append({"kind": "unknown", "error": "normalize_failed"})
    return out


def _normalize_event(ev: Any) -> dict[str, Any]:
    """1 個の Event を AEGIS 形に写像する.

    OpenHands 1.46 の Event 系:
    - MessageEvent (user/assistant)
    - ActionEvent (tool 呼び出し)
    - ObservationEvent (tool 結果)
    - SystemPromptEvent
    - PauseEvent / Condense… 等
    """
    # クラス名で分岐 (Pydantic discriminator を信用しない)
    cls_name = type(ev).__name__
    ts = getattr(ev, "timestamp", None)
    iso_ts = None
    if ts is not None:
        try:
            iso_ts = ts.isoformat()
        except Exception:  # noqa: BLE001
            iso_ts = str(ts)

    if cls_name == "MessageEvent":
        msg = getattr(ev, "message", None)
        role = getattr(msg, "role", "assistant") if msg is not None else "assistant"
        # 1.46 の message は list[Content] 形式
        text_chunks: list[str] = []
        if msg is not None:
            for c in getattr(msg, "content", []) or []:
                ctype = type(c).__name__
                if ctype == "TextContent":
                    text_chunks.append(getattr(c, "text", ""))
        return {
            "kind": "message",
            "role": role,
            "text": "\n".join(t for t in text_chunks if t),
            "timestamp": iso_ts,
        }

    if cls_name == "ActionEvent":
        return {
            "kind": "action",
            "tool": getattr(ev, "tool_name", None) or getattr(ev, "name", None),
            "args": _safe_getattr(ev, "action", "args"),
            "timestamp": iso_ts,
        }

    if cls_name == "ObservationEvent":
        return {
            "kind": "observation",
            "tool": _safe_getattr(ev, "observation", "tool_name"),
            "output": _safe_getattr(ev, "observation", "output"),
            "timestamp": iso_ts,
        }

    return {"kind": cls_name.lower(), "timestamp": iso_ts}


def _safe_getattr(obj: Any, *path: str) -> Any:
    cur: Any = obj
    for p in path:
        if cur is None:
            return None
        cur = getattr(cur, p, None)
    return cur


# ---------------------------------------------------------------------------
# AgentTask → SDK 入力変換 (Phase 3 との接続点)
# ---------------------------------------------------------------------------


def build_prompt_from_task(task: AgentTask) -> str:
    """`AgentTask.goal` (+ context) → OpenHands への自然言語 prompt.

    Phase 2 では goal だけ渡す。Phase 3 で context や tools をどう組み込むか
    詳細化する。
    """
    if not task.context:
        return task.goal
    lines = [task.goal, "", "Context:"]
    for key, value in task.context.items():
        if isinstance(value, str) and len(value) < 1000:
            lines.append(f"- {key}: {value}")
        else:
            lines.append(f"- {key}: <{type(value).__name__}, len={len(str(value))}>")
    return "\n".join(lines)
