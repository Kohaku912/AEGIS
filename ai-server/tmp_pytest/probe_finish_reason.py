import json, sys, os, glob
sys.path.insert(0, "/app/src")
from openai import OpenAI
import yaml

paths = glob.glob("/app/config/llm.yaml") + glob.glob("/app/**/llm.yaml", recursive=True)
print("llm.yaml:", paths[:3])
cfg = yaml.safe_load(open(paths[0]).read()) if paths else {}
print("mode:", cfg.get("mode"))
prof = (cfg.get("profiles") or {}).get("decision") or (cfg.get("profiles") or {}).get("tool_planning") or {}
print("decision profile:", json.dumps(prof, ensure_ascii=False))

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")
model = prof.get("model") or "deepseek-v4-flash"
print("base_url:", base_url, "key_set:", bool(api_key), "model:", model)
client = OpenAI(api_key=api_key, base_url=base_url)

tools = [{
  "type": "function",
  "function": {
    "name": "pc_server__system__get_os_info",
    "description": "Get OS information from the PC.",
    "parameters": {"type": "object", "properties": {}, "required": []},
  },
}]

for mt in (600, 2500):
    r = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are AEGIS's initiative evaluator. Select a tool only when acting now is justified. When non-action is more appropriate, return a concise reason."},
            {"role": "user", "content": "Low desires: growth:gap=1.0\nSelect up to 3 capabilities to advance an explicit outcome. It is valid to select no capability."},
        ],
        tools=tools,
        tool_choice="auto",
        max_tokens=mt,
        temperature=0.3,
    )
    ch = r.choices[0]
    print("--- max_tokens=", mt)
    print("  finish_reason:", ch.finish_reason)
    print("  content:", json.dumps((ch.message.content or "")[:400], ensure_ascii=False))
    print("  tool_calls:", ch.message.tool_calls)
    rc = getattr(ch.message, "reasoning_content", None)
    print("  reasoning_content_len:", len(rc) if rc else 0)
    print("  usage:", r.usage)
