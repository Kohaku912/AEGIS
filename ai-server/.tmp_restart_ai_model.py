import os
import sys
import threading
import time

ROOT = r'c:\Users\kohak\programs\AEGIS\ai-server'
sys.path.insert(0, os.path.join(ROOT, 'src'))
os.environ['OPENAI_API_KEY'] = os.environ.get('DEEPSEEK_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

from aegis_ai.config import get_config
from aegis_ai.grpc_server import serve
from aegis_ai.web.dashboard_routes import DashboardApp

DashboardApp._start_autonomous_loop = lambda self: None
cfg = get_config()
threading.Thread(target=lambda: serve(cfg), daemon=True).start()
threading.Thread(target=lambda: DashboardApp().run(host='0.0.0.0', port=8090, debug=False), daemon=True).start()

while True:
    time.sleep(60)
