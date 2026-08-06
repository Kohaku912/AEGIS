from aegis_ai.desire.fulfillment import evaluate_task_result
r = evaluate_task_result("ai-server.agora.read_posts", True, {"posts": [1]}, "social")
print("structural", r.task_effect.value, r.pressure_reduction, r.details)
from aegis_ai.integrations.android.manager import AndroidServerManager
print("sweep", hasattr(AndroidServerManager, "sweep_stale_sessions"))
from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
print("release_doc", "LLM fulfillment" in (AutonomousLoop._release_cycle_pressure.__doc__ or ""))
