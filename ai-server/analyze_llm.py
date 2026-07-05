import json
import os
from openai import OpenAI

# Get the full autonomous_tool_call prompt for analysis
with open('/tmp/prompts_for_analysis.json', 'r', encoding='utf-8') as f:
    samples = json.load(f)

# Get the full prompt for autonomous_tool_call
autonomous_prompt = samples['autonomous_tool_call'][0]['prompt']

# Create analysis request
analysis_prompt = """You are an LLM token optimization analyst. Analyze the following prompt used in an autonomous AI assistant system and identify which information components are useful vs wasteful for the task.

PROMPT TO ANALYZE:
---
""" + autonomous_prompt + """
---

TASK: This prompt is used to select which tool/capability to execute next in an autonomous loop. The LLM needs to decide which action to take based on the current state.

ANALYZE EACH SECTION:
1. Current desire states - Is this information necessary for tool selection?
2. AFFECT STATE (Personality, Mood, Emotional state) - Is this needed for tool selection?
3. Experiential memory (recent executions) - Is this useful?
4. People section (AGORA posts) - Is this relevant?
5. Recent autonomous executions - Is this needed?
6. Action trace hints - Is this useful?
7. Available tools list - Is this necessary?

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

# Call DeepSeek
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
print(result)
