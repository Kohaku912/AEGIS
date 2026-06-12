"""Test basic LLM functionality."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()

# Basic test
result = llm.generate(
    prompt="What is 2+2? Answer with just the number.",
    system_prompt="Answer concisely.",
    max_tokens=10,
)

print("Success:", result.success)
print("Content:", result.content)
