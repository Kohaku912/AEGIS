"""Test desire update with simpler prompt."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()

# Simpler prompt
prompt = (
    "I helped a user with coding and they were satisfied. "
    "How would this affect these desires (0-10 scale)? "
    "Respond with JSON only.\n\n"
    "Desires: social_connectivity=7.0, personal_fulfillment=5.5, curiosity=5.0, "
    "safety=5.0, recognition=6.0, autonomy=5.0, creativity=5.0, purpose=5.0\n\n"
    'JSON format: {"desire_updates": {"desire_name": {"new_value": X, "reason": "..."}, ...}}'
)

result = llm.generate(
    prompt=prompt,
    system_prompt="Respond with ONLY valid JSON. No explanation.",
    max_tokens=300,
)

print("Success:", result.success)
print("Content:", result.content)
