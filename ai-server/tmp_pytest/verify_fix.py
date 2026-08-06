import sys, types
sys.path.insert(0, "/app/src")
import py_compile
for f in ["/app/src/aegis_ai/llm/providers/openai_provider.py",
          "/app/src/aegis_ai/llm/router.py",
          "/app/src/aegis_ai/autonomous/autonomous_loop.py"]:
    py_compile.compile(f, doraise=True)
print("compile OK")

from aegis_ai.llm.providers.openai_provider import LLMResponse as PR
from aegis_ai.llm.router import LLMResponse as RR
print("provider finish_reason field:", PR().finish_reason == "")
print("router finish_reason field:", RR().finish_reason == "")

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

class FakeDesire:
    def __init__(self): self.calls = []
    def release_cycle_pressure(self, *, effectiveness=1.0): self.calls.append(effectiveness)

loop = AutonomousLoop.__new__(AutonomousLoop)
loop._desire = FakeDesire()

# no tasks -> no release
loop._release_cycle_pressure([], [])
print("no tasks -> calls:", loop._desire.calls)

# tasks all failed -> partial
loop._desire.calls.clear()
loop._release_cycle_pressure([{"action": "x"}], [{"success": False}])
print("failed -> calls:", loop._desire.calls)

# tasks with success -> full
loop._desire.calls.clear()
loop._release_cycle_pressure([{"action": "x"}], [{"success": True}])
print("success -> calls:", loop._desire.calls)
