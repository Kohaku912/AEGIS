"""Test desire update with LLM."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.desire.desire_system import DesireSystem

llm = create_llm_provider()

# Test what LLM returns
prompt = (
    "Analyze how this action affects AEGIS's desires.\n\n"
    "Action: Helped user with coding task\n"
    "Observation: User was satisfied with the solution\n\n"
    "Current desire states:\n"
    "- social_connectivity: 7.0/10\n"
    "- personal_fulfillment: 5.5/10\n"
    "- curiosity: 5.0/10\n"
    "- safety: 5.0/10\n"
    "- recognition: 6.0/10\n"
    "- autonomy: 5.0/10\n"
    "- creativity: 5.0/10\n"
    "- purpose: 5.0/10\n\n"
    "For each desire, determine how the action would affect it (0-10 scale).\n"
    'Respond with JSON: {"desire_updates": {"social_connectivity": {"new_value": 7.0, "reason": "..."}, ...}}\n'
    "Only include desires that would actually change."
)

result = llm.generate(
    prompt=prompt,
    system_prompt="You are a desire evaluation system. Analyze how actions affect intrinsic motivations. Output only JSON.",
    max_tokens=1000,
)

print("Success:", result.success)
print("Content:")
print(result.content)
