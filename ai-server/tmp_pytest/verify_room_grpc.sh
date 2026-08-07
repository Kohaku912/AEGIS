#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 python -c "import grpc,os,json; from generated.aegis import common_pb2, room_server_pb2_grpc; from aegis_ai.runtime import get_runtime; host=os.getenv('ROOM_SERVER_HOST'); port=int(os.getenv('ROOM_SERVER_PORT','50055')); ch=grpc.insecure_channel(f'{host}:{port}'); r=room_server_pb2_grpc.RoomServerStub(ch).HealthCheck(common_pb2.HealthCheckRequest(server_id='ai-verify'), timeout=5); print('grpc', r.status.code, r.status.message, r.version); sm=get_runtime().status_manager; print('before', json.dumps(sm.get_snapshot().get('room-server',{}),ensure_ascii=False)[:500]);
getattr(sm, 'check_once', lambda: None)();
print('methods', [m for m in dir(sm) if 'check' in m.lower()][:20])"
