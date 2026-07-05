import json
import os
from openai import OpenAI

with open('/tmp/prompts_for_analysis.json', 'r', encoding='utf-8') as f:
    samples = json.load(f)

# Analyze follow_up prompt
follow_up_prompt = samples['follow_up'][0]['prompt']

analysis_prompt = """You are an LLM token optimization analyst. Analyze the following prompt used in an autonomous AI assistant system.

PROMPT TO ANALYZE:
---
""" + follow_up_prompt + """
---

TASK: This prompt is used to determine if follow-up actions are needed after executing tasks.

ANALYZE EACH SECTION:
1. Task results - Is this information necessary?
2. Rules section - Is this useful?
3. Available tools - Is this necessary?

For each section, provide:
- Token estimate (approximate)
- Usefulness rating (high/medium/low/unnecessary)
- Reasoning
- Recommendation (keep as-is, reduce, remove, or condense)

Return your analysis as JSON with this structure:
{
  "sections": [
    {
      "name": "section name",
      "token_estimate": N,
      "usefulness": "high|medium|low|unnecessary",
      "reasoning": "why",
      "recommendation": "keep|reduce|remove|condense",
      "suggestion": "specific suggestion"
    }
  ],
  "total_estimated_tokens": N,
  "potential_savings": N,
  "top_optimization_targets": ["target1", "target2"]
}"""

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY', ''),
    base_url='https://api.deepseek.com'
)

response = client.chat.completions.create(
    model='deepseek-chat',
    messages=[
        {'role': 'system', 'content': 'You are a token optimization analyst. Return valid JSON only.'},
        {'role': 'user', 'content': analysis_prompt}
    ],
    temperature=0.1,
    max_tokens=2000
)

result = response.choices[0].message.content
print("=== FOLLOW_UP ANALYSIS ===")
print(result)
