"""Test autonomous execution with real LLM."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

os.environ["OPENAI_API_KEY"] = "sk-b7634b706d714a11944a498f1a520f52"
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.desire.desire_system import DesireSystem
from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

print("=== Creating Systems ===")
llm = create_llm_provider()
print("LLM Provider:", type(llm).__name__)

desire = DesireSystem(data_dir="data/desires", llm_provider=llm)
print("Desire System: OK")

print()
print("=== Initial Desire States ===")
for name, d in desire.get_all_desires().items():
    print(f"  {name}: {d.value:.1f}/10")

print()
print("=== Testing Autonomous Cycle ===")
loop = AutonomousLoop(
    llm_provider=llm,
    desire_system=desire,
    data_dir="data/autonomous",
    desire_threshold=6.0,  # Higher threshold to trigger tasks
)

# Get low desires
low = loop._get_low_desires()
print(f"Low desires (< 6.0): {len(low)}")
for d in low:
    print(f"  - {d['name']}: {d['value']:.1f}")

if low:
    print()
    print("=== Generating Tasks ===")
    tasks = loop._generate_tasks(low)
    print(f"Generated {len(tasks)} tasks:")
    for t in tasks:
        print(f"  - {t.get('desire')}: {t.get('action')}")

    print()
    print("=== Executing Tasks ===")
    results = loop._execute_tasks(tasks)
    print(f"Executed {len(results)} tasks:")
    for r in results:
        print(f"  - {r.get('desire')}: {'OK' if r.get('success') else 'FAILED'}")
        if r.get('result'):
            print(f"    Result: {r['result'][:100]}")

    print()
    print("=== Updated Desire States ===")
    for name, d in desire.get_all_desires().items():
        print(f"  {name}: {d.value:.1f}/10")
else:
    print("No low desires, testing manual trigger...")
    status = loop.trigger_now()
    print("Trigger result:", status)
