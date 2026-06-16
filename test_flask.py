"""Test Flask server."""
from flask import Flask
import threading
import time
import urllib.request

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>AEGIS Dashboard Test</h1>'

@app.route('/health')
def health():
    return {'status': 'ok'}

def run_server():
    app.run(host='0.0.0.0', port=8092, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test the server
    try:
        response = urllib.request.urlopen('http://0.0.0.0:8092/health', timeout=5)
        print(f'Status: {response.status}')
        print(f'Content: {response.read().decode()}')
    except Exception as e:
        print(f'Error: {e}')
    
    # Keep server running
    print('Server running on http://0.0.0.0:8092')
    print('Press Ctrl+C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping...')
