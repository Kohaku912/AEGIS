import sys, py_compile
sys.path.insert(0, "/app/src")
for f in ["/app/src/aegis_ai/llm/providers/openai_provider.py",
          "/app/src/aegis_ai/llm/router.py",
          "/app/src/aegis_ai/llm/gateway.py",
          "/app/src/aegis_ai/autonomous/autonomous_loop.py"]:
    py_compile.compile(f, doraise=True)
print("compile OK")

from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.router import accepts_kwarg
from aegis_ai.llm.providers.openai_provider import OpenAIProvider
print("imports OK")

p = OpenAIProvider(model="deepseek-v4-flash", api_key="x", base_url="https://api.deepseek.com")
print("low   ->", p._reasoning_extra_body("low"))
print("high  ->", p._reasoning_extra_body("high"))
p2 = OpenAIProvider(model="gpt-4o", api_key="x", base_url="https://api.openai.com/v1")
print("openai low ->", p2._reasoning_extra_body("low"))
print("accepts reasoning_level:", accepts_kwarg(p.generate_with_tools, "reasoning_level"))
print("accepts profile (gateway):", accepts_kwarg(LLMGateway.generate_with_tools, "profile"))
