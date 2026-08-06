import json, sys, os, glob, yaml
sys.path.insert(0, "/app/src")
from openai import OpenAI

cfg = yaml.safe_load(open("/app/config/llm.yaml").read())
prof = cfg["profiles"]["decision"]
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url=prof["base_url"])
model = prof["model"]

tools = []
for i in range(12):
    tools.append({"type":"function","function":{
        "name": f"pc_server__system__cap_{i}",
        "description": "Capability " + ("detail " * 20),
        "parameters": {"type":"object","properties":{"target":{"type":"string","description":"target " * 10}},"required":[]}}})

filler = "\n".join(f"- context line {i}: " + ("observation detail " * 12) for i in range(180))
prompt = f"""Low desires: user_support:gap=1.0, social:gap=1.0, growth:gap=1.0

Recent: {filler}

Select up to 3 capabilities to advance an explicit outcome.
It is valid to select no capability when action is unnecessary or cannot advance a verified outcome.
Choose an action only if its expected value exceeds risk, interruption, repetition, cost, and uncertainty."""

for mt in (600, 2048):
    r = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":"You are AEGIS's initiative evaluator. Select a tool only when acting now is justified. When non-action is more appropriate, return a concise reason."},
            {"role":"user","content":prompt},
        ],
        tools=tools, tool_choice="auto", max_tokens=mt, temperature=0.0,
    )
    ch = r.choices[0]
    u = r.usage
    print("--- max_tokens=", mt, "prompt_tokens=", u.prompt_tokens, "completion=", u.completion_tokens,
          "reasoning=", getattr(u.completion_tokens_details, "reasoning_tokens", None))
    print("  finish_reason:", ch.finish_reason)
    print("  content_len:", len(ch.message.content or ""), "| preview:", json.dumps((ch.message.content or "")[:200], ensure_ascii=False))
    print("  tool_calls:", ch.message.tool_calls)
