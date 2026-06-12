"""Debug LLM provider with detailed output."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY", "")
base_url = os.getenv("OPENAI_BASE_URL", "")

print("API Key:", api_key[:20] + "...")
print("Base URL:", base_url)

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "Say hello in one word."}
        ],
        max_tokens=10,
        temperature=0.1,
    )
    
    print("Response:", response)
    print("Content:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
