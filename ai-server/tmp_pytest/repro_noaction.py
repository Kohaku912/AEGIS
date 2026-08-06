import json, sys, types
sys.path.insert(0, "/app/src")
from aegis_ai.runtime import get_runtime

rt = get_runtime()
loop = getattr(rt, "autonomous_loop", None) or getattr(rt, "_autonomous_loop", None)
print("loop:", type(loop).__name__)

prov = loop._llm
orig = prov.generate_with_tools
captured = {}

def wrapped(prompt, tools, system_prompt="", max_tokens=1000, temperature=0.3, context_meta=None):
    captured["prompt"] = prompt
    captured["system"] = system_prompt
    captured["tools"] = [t.get("function", {}).get("name") for t in tools]
    captured["max_tokens"] = max_tokens
    r = orig(prompt=prompt, tools=tools, system_prompt=system_prompt,
             max_tokens=max_tokens, temperature=temperature, context_meta=context_meta)
    captured["resp_content"] = getattr(r, "content", None)
    captured["resp_tool_calls"] = getattr(r, "tool_calls", None)
    captured["resp_success"] = getattr(r, "success", None)
    captured["resp_out_tokens"] = getattr(r, "output_tokens", None)
    return r

prov.generate_with_tools = wrapped
low = loop._get_low_desires()
print("low_desires:", json.dumps(low, ensure_ascii=False)[:400])
if not low:
    low = [{"name":"growth","value":0.0,"expected":1.0,"pressure":6.0,"gap":1.0}]
tasks = loop._generate_tasks(low)
print("tasks:", len(tasks))
print("=== TOOLS OFFERED (%d) ===" % len(captured.get("tools") or []))
print(captured.get("tools"))
print("max_tokens:", captured.get("max_tokens"))
print("=== SYSTEM ===")
print(captured.get("system"))
print("=== PROMPT (%d chars) ===" % len(captured.get("prompt") or ""))
print((captured.get("prompt") or "")[:6000])
print("=== RESPONSE ===")
print("success:", captured.get("resp_success"), "out_tokens:", captured.get("resp_out_tokens"))
print("tool_calls:", captured.get("resp_tool_calls"))
print("content:", json.dumps(captured.get("resp_content"), ensure_ascii=False)[:2000])
