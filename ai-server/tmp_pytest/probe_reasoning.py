import json, os, yaml
from openai import OpenAI
cfg = yaml.safe_load(open("/app/config/llm.yaml").read())
prof = cfg["profiles"]["decision"]
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url=prof["base_url"])
model = prof["model"]

tools = [{"type":"function","function":{"name":"pc_server__system__get_os_info",
    "description":"Get OS information from the PC.","parameters":{"type":"object","properties":{},"required":[]}}}]
msgs = [{"role":"user","content":"Check the PC operating system version now. Use the available tool."}]

def probe(label, **extra):
    try:
        r = client.chat.completions.create(model=model, messages=msgs, tools=tools,
                                           tool_choice="auto", max_tokens=800, temperature=0.0, **extra)
        u = r.usage
        ch = r.choices[0]
        print(f"[{label}] OK finish={ch.finish_reason} reasoning_tokens={getattr(u.completion_tokens_details,'reasoning_tokens',None)} completion={u.completion_tokens} tool_calls={bool(ch.message.tool_calls)}")
    except Exception as e:
        print(f"[{label}] ERROR {type(e).__name__}: {str(e)[:220]}")

probe("baseline")
probe("reasoning_effort=low", reasoning_effort="low")
probe("reasoning_effort=minimal", reasoning_effort="minimal")
probe("extra_body thinking disabled", extra_body={"thinking": {"type": "disabled"}})
probe("extra_body enable_thinking=False", extra_body={"enable_thinking": False})
