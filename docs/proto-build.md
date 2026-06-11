# Proto Build Guide

> **Status**: Verified (2026-06-11)  
> **Related**: [`proto-overview.md`](proto-overview.md), [`architecture.md`](architecture.md)

## Prerequisites

### Option A: `protoc` (standalone compiler)

Install from: https://github.com/protocolbuffers/protobuf/releases

```bash
# macOS
brew install protobuf

# Linux
apt-get install protobuf-compiler

# Windows
choco install protoc
# Or download from GitHub releases
```

### Option B: `grpc_tools` (Python package) — ✅ Verified

```bash
cd ai-server
pip install grpcio-tools
```

## Syntax Check (Lint)

```bash
# Using grpc_tools (Python)
cd AEGIS
python -m grpc_tools.protoc \
  -I protos \
  --python_out=/tmp/proto_out \
  protos/ellie/*.proto
```

Output: no output = all files valid ✅ (verified 2026-06-11)

## Code Generation (not yet needed)

When implementation begins, generate gRPC stubs:

### Python (AI Server, PC Server, Room Server)

```bash
python -m grpc_tools.protoc \
  -I protos \
  --python_out=ai-server/src/generated \
  --grpc_python_out=ai-server/src/generated \
  protos/ellie/*.proto
```

### Node.js (Browser Server)

```bash
npm install -g grpc-tools
grpc_tools_node_protoc \
  --js_out=import_style=commonjs,binary:browser-server/src/generated \
  --grpc_out=grpc_js:browser-server/src/generated \
  --proto_path=protos \
  protos/ellie/*.proto
```

### Kotlin (Android Server)

```gradle
// build.gradle.kts
plugins {
    id("com.google.protobuf") version "0.9.4"
}

protobuf {
    protoc { artifact = "com.google.protobuf:protoc:3.25.0" }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.plugins { create("grpc") {} }
        }
    }
}
```

## CI Integration (Planned)

```yaml
# .github/workflows/proto-lint.yml (planned)
- name: Check proto syntax
  run: |
    python -m grpc_tools.protoc -I protos --python_out=/tmp/proto_out protos/ellie/*.proto
```
