from aegis_ai.runtime import get_runtime
from tool_broker import ToolExecutionRequest, ExecutionSource

rt = get_runtime()
if hasattr(rt.task_manager, "sweep_stale_incidents"):
    print("sweep", rt.task_manager.sweep_stale_incidents())

for cap, args in [
    ("ai-server.search.web", {"query": "orange pi", "max_results": 1}),
    ("ai-server.commitment.list", {}),
]:
    req = ToolExecutionRequest(
        capability_id=cap,
        arguments=args,
        source=ExecutionSource.AUTONOMOUS,
        reason="verify",
    )
    res = rt.tool_broker.execute(req)
    out = res.output if isinstance(res.output, dict) else {"raw": str(res.output)}
    print(cap, "ok", res.success, "err", res.error)
    print("  result=", str(out.get("result"))[:160])
    print("  hint=", out.get("task_effect_hint"), "count=", out.get("count"))
