"""Self-Development Controller — LLM-driven app creation, testing, deployment, execution.

Full flow:
1. LLM receives goal (e.g., "Create HelloWorld app")
2. LLM generates Python script
3. Script is written to sandbox
4. Script is tested in sandbox
5. If tests pass, script is deployed to production
6. Script is registered as a capability
7. User can then execute the capability
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.self_development")


@dataclass
class DevTask:
    task_id: str = ""
    goal: str = ""
    status: str = "pending"
    script_path: str = ""
    script_content: str = ""
    test_result: dict[str, Any] = field(default_factory=dict)
    deploy_path: str = ""
    capability_id: str = ""
    execution_result: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: int = 0
    completed_at: int = 0


class SelfDevelopmentController:
    """LLM-driven self-development: create, test, deploy, execute apps."""

    def __init__(
        self,
        llm_provider: Any = None,
        sandbox_dir: str = "data/sandbox",
        deploy_dir: str = "data/apps",
        capabilities_dir: str = "capabilities",
        capability_registry: Any = None,
    ) -> None:
        self._llm = llm_provider
        self._sandbox_dir = Path(sandbox_dir)
        self._deploy_dir = Path(deploy_dir)
        self._capabilities_dir = Path(capabilities_dir)
        self._sandbox_dir.mkdir(parents=True, exist_ok=True)
        self._deploy_dir.mkdir(parents=True, exist_ok=True)
        self._capabilities_dir.mkdir(parents=True, exist_ok=True)
        self._registry = capability_registry
        self._tasks: dict[str, DevTask] = {}
        self._load()

    def _load(self) -> None:
        path = Path(self._deploy_dir) / "tasks.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for d in data:
                task = DevTask(
                    task_id=d.get("task_id", ""),
                    goal=d.get("goal", ""),
                    status=d.get("status", "pending"),
                    script_path=d.get("script_path", ""),
                    script_content=d.get("script_content", ""),
                    deploy_path=d.get("deploy_path", ""),
                    capability_id=d.get("capability_id", ""),
                    error=d.get("error", ""),
                    created_at=d.get("created_at", 0),
                    completed_at=d.get("completed_at", 0),
                )
                self._tasks[task.task_id] = task
        except Exception:
            pass

    def _save(self) -> None:
        path = Path(self._deploy_dir) / "tasks.json"
        data = []
        for task in self._tasks.values():
            data.append({
                "task_id": task.task_id,
                "goal": task.goal,
                "status": task.status,
                "script_path": task.script_path,
                "script_content": task.script_content,
                "deploy_path": task.deploy_path,
                "capability_id": task.capability_id,
                "error": task.error,
                "created_at": task.created_at,
                "completed_at": task.completed_at,
            })
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def create_app(self, goal: str) -> DevTask:
        task = DevTask(
            task_id=f"dev_{uuid.uuid4().hex[:8]}",
            goal=goal,
            created_at=int(time.time() * 1000),
        )

        if not self._llm:
            task.status = "failed"
            task.error = "No LLM provider"
            return task

        script = self._generate_script(goal)
        if not script:
            task.status = "failed"
            task.error = "LLM failed to generate script"
            return task

        task.script_content = script
        task.script_path = str(self._sandbox_dir / f"{task.task_id}.py")

        with open(task.script_path, "w", encoding="utf-8") as f:
            f.write(script)

        test_result = self._test_in_sandbox(task.script_path)
        task.test_result = test_result

        if test_result.get("passed"):
            deploy_result = self._deploy(task)
            if deploy_result.get("success"):
                task.deploy_path = deploy_result["path"]
                task.capability_id = self._register_capability(task)
                task.status = "deployed"
            else:
                task.status = "test_passed_deploy_failed"
                task.error = deploy_result.get("error", "")
        else:
            task.status = "test_failed"
            task.error = test_result.get("error", "")

        task.completed_at = int(time.time() * 1000)
        self._tasks[task.task_id] = task
        self._save()
        return task

    def execute_app(self, task_id: str) -> dict[str, Any]:
        task = self._tasks.get(task_id)
        if task is None:
            return {"error": f"Task '{task_id}' not found."}
        if task.status != "deployed":
            return {"error": f"Task not deployed (status={task.status})."}

        app_dir = self._deploy_dir / task_id
        script_path = app_dir / "src" / "main.py"
        if not script_path.exists():
            return {"error": f"Script not found: {script_path}"}

        try:
            result = subprocess.run(
                ["python", "src/main.py"],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=30,
                cwd=str(app_dir),
            )
            task.execution_result = {
                "returncode": result.returncode,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "success": result.returncode == 0,
            }
            return task.execution_result
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out."}
        except Exception as e:
            return {"error": str(e)}

    def execute_by_capability(self, capability_id: str) -> dict[str, Any]:
        for task in self._tasks.values():
            if task.capability_id == capability_id:
                return self.execute_app(task.task_id)
        return {"error": f"No task with capability '{capability_id}'."}

    def get_task(self, task_id: str) -> DevTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[DevTask]:
        return list(self._tasks.values())

    def _generate_script(self, goal: str) -> str:
        prompt = f"""You are AEGIS's self-development system. Write a Python script for this goal:

Goal: {goal}

Rules:
- Write ONLY the Python code, no explanation
- The script must be self-contained
- Use only standard library modules
- Print the result to stdout
- Include a main guard (if __name__ == "__main__")
- Keep it simple and safe

Respond with ONLY the Python code:"""

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are a Python code generator. Output only valid Python code. No markdown, no explanation.",
            max_tokens=1000,
        )

        if not result.success:
            return ""

        code = result.content.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def _test_in_sandbox(self, script_path: str) -> dict[str, Any]:
        try:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=30,
                cwd=str(self._sandbox_dir),
            )
            passed = result.returncode == 0
            return {
                "passed": passed,
                "returncode": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:1000],
                "error": "" if passed else result.stderr[:500],
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timed out."}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _deploy(self, task: DevTask) -> dict[str, Any]:
        app_dir = self._deploy_dir / task.task_id
        src_dir = app_dir / "src"
        exec_dir = app_dir / "executors"
        try:
            src_dir.mkdir(parents=True, exist_ok=True)
            exec_dir.mkdir(parents=True, exist_ok=True)

            script_path = src_dir / "main.py"
            script_path.write_text(task.script_content, encoding="utf-8")

            exec_manifest = {
                "action": "run",
                "type": "command",
                "command": "python src/main.py",
                "working_dir": ".",
                "timeout_ms": 30000,
                "stdin": "json",
                "stdout": "json",
            }
            (exec_dir / "run.json").write_text(
                json.dumps(exec_manifest, indent=2), encoding="utf-8",
            )

            app_manifest = {
                "app_id": task.task_id,
                "title": task.goal[:100],
                "description": f"Self-developed app: {task.goal}",
                "origin": "generated",
                "version": "1.0.0",
            }
            (app_dir / "app.json").write_text(
                json.dumps(app_manifest, indent=2, ensure_ascii=False), encoding="utf-8",
            )

            return {"success": True, "path": str(script_path), "app_dir": str(app_dir)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _register_capability(self, task: DevTask) -> str:
        cap_id = f"generated.ai-server.{task.task_id}.run"
        cap_dir = self._capabilities_dir / "generated" / "ai-server" / task.task_id
        cap_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "title": task.goal[:100],
            "description": f"Self-developed app: {task.goal}",
            "server_id": "ai-server",
            "app_id": task.task_id,
            "action": "run",
            "version": "1.0.0",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
            "risk": {
                "level": "low",
                "side_effects": [],
                "requires_approval": False,
            },
            "tags": ["generated", "self_development", task.task_id],
        }
        manifest_path = cap_dir / "run.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8",
        )

        if self._registry is not None:
            try:
                from aegis_ai.folder_registry import FolderCapabilityRegistry
                if isinstance(self._registry, FolderCapabilityRegistry):
                    self._registry.reload()
            except Exception:
                pass

        return cap_id
