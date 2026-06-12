"""Debug LLM provider."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY", "NOT SET")[:20] + "...")
print("OPENAI_BASE_URL:", os.getenv("OPENAI_BASE_URL", "NOT SET"))

from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()
print("Provider type:", type(llm).__name__)
print("Model:", llm._model if hasattr(llm, '_model') else 'unknown')

# Test with very simple prompt
result = llm.generate(
    prompt="Say hello in one word.",
    system_prompt="",
    max_tokens=10,
    temperature=0.1,
)

print("Success:", result.success)
print("Content:", repr(result.content))
print("Error:", result.error if hasattr(result, 'error') else 'none')
