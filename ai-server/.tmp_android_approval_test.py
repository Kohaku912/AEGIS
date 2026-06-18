import grpc
from generated.aegis import ai_server_pb2_grpc, common_pb2
channel = grpc.insecure_channel('127.0.0.1:50061')
stub = ai_server_pb2_grpc.AIServerStub(channel)
req = common_pb2.ToolInvocationRequest(
    capability_id='android-server.screen.get_ui_tree',
    invocation_id='adb-approval-ui-tree',
    caller='adb-approval-test',
    params_json='{}',
)
try:
    res = stub.InvokeTool(req, timeout=120)
    print('STATUS', res.status.code, res.status.message)
    print('ERROR', res.error)
    print('OUTPUT', res.output_json[:2000])
except Exception as exc:
    print('EXC', repr(exc))
