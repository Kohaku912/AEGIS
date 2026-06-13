import sys, os, json, shutil, tempfile
sys.path.insert(0, 'src')
os.environ['LLM_API_KEY'] = 'sk-b7634b706d714a11944a498f1a520f52'
os.environ['LLM_BASE_URL'] = 'https://api.deepseek.com'
os.environ['LLM_MODEL_NAME'] = 'deepseek-chat'

from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.self_development.controller import SelfDevelopmentController
from aegis_ai.folder_registry import FolderCapabilityRegistry

sandbox = tempfile.mkdtemp()
deploy = tempfile.mkdtemp()
caps_dir = 'capabilities'
llm = create_llm_provider()
ctrl = SelfDevelopmentController(
    llm_provider=llm, sandbox_dir=sandbox,
    deploy_dir=deploy, capabilities_dir=caps_dir,
)

print('=== STEP 1: LLM creates app ===')
task = ctrl.create_app('Create a Python app that prints GoodMorning')
print(f'Task: {task.task_id}, Status: {task.status}')
print(f'Capability: {task.capability_id}')

print()
print('=== STEP 2: Check capability manifest ===')
manifest_path = os.path.join(caps_dir, 'generated', 'ai-server', task.task_id, 'run.json')
if os.path.exists(manifest_path):
    data = json.loads(open(manifest_path).read())
    print(f'Manifest exists: {manifest_path}')
    print(f'  title: {data.get("title")}')
    print(f'  server_id: {data.get("server_id")}')
    print(f'  app_id: {data.get("app_id")}')
    print(f'  action: {data.get("action")}')
else:
    print('Manifest NOT found!')

print()
print('=== STEP 3: FolderRegistry discovers it ===')
reg = FolderCapabilityRegistry(caps_dir)
cap = reg.get(task.capability_id)
if cap:
    print(f'Discovered: {cap.capability_id}')
    print(f'  title: {cap.title}')
    print(f'  origin: {cap.origin}')
    print(f'  risk: {cap.risk_level}')
else:
    print('NOT discovered by registry!')

print()
print('=== STEP 4: Execute the app ===')
result = ctrl.execute_app(task.task_id)
print(f'Success: {result.get("success")}')
print(f'Output: {result.get("stdout", "").strip()}')

print()
print('=== STEP 5: Check executor manifest ===')
exec_path = os.path.join(deploy, task.task_id, 'executors', 'run.json')
if os.path.exists(exec_path):
    data = json.loads(open(exec_path).read())
    print(f'Executor exists: {exec_path}')
    print(f'  command: {data.get("command")}')
else:
    print('Executor NOT found!')

shutil.rmtree(sandbox, ignore_errors=True)
shutil.rmtree(deploy, ignore_errors=True)
shutil.rmtree(os.path.join(caps_dir, 'generated', 'ai-server', task.task_id), ignore_errors=True)
