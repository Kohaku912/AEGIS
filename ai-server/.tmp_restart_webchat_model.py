import os
import sys

ROOT = r'c:\Users\kohak\programs\AEGIS\ai-server'
sys.path.insert(0, os.path.join(ROOT, 'src'))
os.environ['OPENAI_API_KEY'] = os.environ.get('DEEPSEEK_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

from aegis_ai.interaction.channels.web import WebChatApp
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager
from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()
router = InteractionRouter(llm_provider=llm)
sessions = SessionManager()
app = WebChatApp(router=router, session_manager=sessions)
app.run(host='0.0.0.0', port=8091, debug=False)
