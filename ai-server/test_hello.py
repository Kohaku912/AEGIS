import sys, os, tempfile, shutil
sys.path.insert(0, 'src')
os.environ['LLM_API_KEY'] = 'sk-b7634b706d714a11944a498f1a520f52'
os.environ['LLM_BASE_URL'] = 'https://api.deepseek.com'
os.environ['LLM_MODEL_NAME'] = 'deepseek-chat'
from aegis_ai.llm.factory import create_llm_provider
from aegis_ai.self_development.controller import SelfDevelopmentController

sandbox = tempfile.mkdtemp()
deploy = tempfile.mkdtemp()
llm = create_llm_provider()
ctrl = SelfDevelopmentController(llm_provider=llm, sandbox_dir=sandbox, deploy_dir=deploy)

print('=== STEP 1: Create HelloWorld app ===')
task = ctrl.create_app('Create a Python app that prints HelloWorld')
print(f'Task ID: {task.task_id}')
print(f'Status: {task.status}')
print(f'Capability ID: {task.capability_id}')
print(f'Test passed: {task.test_result.get("passed")}')
print(f'Script:')
print(task.script_content[:500])
print()

if task.status == 'deployed':
    print('=== STEP 2: Execute the deployed app ===')
    result = ctrl.execute_app(task.task_id)
    print(f'Return code: {result.get("returncode")}')
    print(f'Stdout: {result.get("stdout", "").strip()}')
    print(f'Success: {result.get("success")}')
else:
    print(f'Deploy failed: {task.error}')

shutil.rmtree(sandbox, ignore_errors=True)
shutil.rmtree(deploy, ignore_errors=True)
