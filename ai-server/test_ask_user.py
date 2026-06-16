import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.web.chat_tools import call_llm_with_tools, get_catalog
from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()
catalog = get_catalog()

system_prompt = """You are AEGIS, an autonomous AI assistant.

CRITICAL RULE: When the user asks a question that requires their input, choices, or confirmation, you MUST use the ask_user tool. Do NOT answer the question yourself.

Examples of when to use ask_user:
- User asks "what name should I use?" → use ask_user with options
- User asks "should I proceed?" → use ask_user with Yes/No options
- User asks "which option do you prefer?" → use ask_user with the options

Format: {"name": "ask_user", "arguments": {"question": "...", "options": ["option1", "option2"]}}"""

result = call_llm_with_tools(
    llm,
    'Googleアカウントを作りたいのですが、名前を教えてください。',
    system_prompt,
    catalog=catalog,
)

print('Response:', result['response'][:500])
print('Needs user input:', result.get('needs_user_input'))
print('Question:', result.get('question'))
print('Options:', result.get('options'))
