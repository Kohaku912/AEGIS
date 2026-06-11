# Proto Build Guide

> **Status**: ✅ Verified (2026-06-11)
> **Related**: [`proto-overview.md`](proto-overview.md), [`architecture.md`](architecture.md)

## Quick Start

```bash
# Windows (PowerShell)
.\scripts\generate_protos.ps1 -Language python

# Linux / macOS
./scripts/generate_protos.sh python
```

---

## Decision: Git Tracking Policy

**Generated code IS committed to Git.**

| Reason | Explanation |
|--------|-------------|
| Reproducibility | CI can verify generation is deterministic |
| No protoc required | Contributors can use the repo without installing protoc |
| Code review | Generated changes are visible in PR diffs |
| Consistency | Everyone uses the same generated code |

> **Rule**: Generated code in `*/src/generated/` is committed.  
> **Do NOT edit generated files manually.** Always regenerate from `.proto` files.

---

## Build System: buf + protoc

We use two tools:
- **buf** (v2) — proto lint, format, breaking change detection
- **grpc_tools.protoc** — Python code generation (gRPC + protobuf)
- **protoc** (standalone) — Node.js, Kotlin code generation (documented below)

### Configuration Files

| File | Purpose |
|------|---------|
| `buf.yaml` | Lint rules, module definition, breaking change config |
| `scripts/generate_protos.ps1` | Windows generation script |
| `scripts/generate_protos.sh` | Linux/macOS generation script |

---

## Step 1: Install Prerequisites

### buf (lint + breaking check)

```bash
# Via npm (cross-platform)
npm install -g @bufbuild/buf

# Or direct download: https://buf.build/docs/installation
```

### grpc_tools (Python code generation)

```bash
cd ai-server
pip install grpcio-tools
```

---

## Step 2: Lint Proto Files

```bash
cd AEGIS
buf lint
```

✅ Verified: 0 errors (2026-06-11)

---

## Step 3: Generate Code

### Python (AI Server, PC Server, Room Server)

```bash
# Windows
.\scripts\generate_protos.ps1 -Language python

# Linux/macOS
./scripts/generate_protos.sh python
```

Output: `ai-server/src/generated/ellie/*_pb2.py`, `*_pb2_grpc.py`, `*_pb2.pyi`

**What is generated:**

| Pattern | Description |
|---------|-------------|
| `*_pb2.py` | Protobuf message classes |
| `*_pb2_grpc.py` | gRPC service stubs (client + server) |
| `*_pb2.pyi` | Type hints for IDE support |

**Import example:**

```python
from generated.ellie import common_pb2
from generated.ellie import ai_server_pb2, ai_server_pb2_grpc

# Use proto enums
level = common_pb2.SafetyLevel.LEVEL_0_READ
server_type = common_pb2.ServerType.SERVER_TYPE_PC

# Create messages
cap = common_pb2.Capability(
    id="pc.screenshot",
    name="Screenshot",
    safety_level=common_pb2.LEVEL_0_READ,
)
```

---

### Node.js / TypeScript (Browser Server)

**Prerequisites:**

```bash
npm install -g grpc-tools grpc_tools_node_protoc_plugin
# Or locally:
cd browser-server
npm install --save-dev grpc-tools grpc_tools_node_protoc_plugin @grpc/grpc-js google-protobuf
```

**Generation command:**

```bash
# Using protoc directly
protoc \
  -I protos \
  --js_out=import_style=commonjs,binary:browser-server/src/generated \
  --grpc_out=grpc_js:browser-server/src/generated \
  protos/ellie/*.proto

# Or using grpc_tools_node_protoc
grpc_tools_node_protoc \
  --js_out=import_style=commonjs,binary:browser-server/src/generated \
  --grpc_out=grpc_js:browser-server/src/generated \
  --proto_path=protos \
  protos/ellie/*.proto
```

**Import example (TypeScript):**

```typescript
import { SafetyLevel, Capability } from './generated/ellie/common_pb';
import { BrowserServerClient } from './generated/ellie/browser_server_grpc_pb';
```

---

### Kotlin / Android (Android Server)

**Prerequisites:** Android project with Gradle + protobuf plugin.

**`build.gradle.kts` (app-level):**

```kotlin
plugins {
    id("com.google.protobuf") version "0.9.4"
}

dependencies {
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("io.grpc:grpc-protobuf:1.60.0")
    implementation("com.google.protobuf:protobuf-kotlin:3.25.0")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.0"
    }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0:jdk8@jar"
        }
        create("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.plugins {
                create("grpc") {
                    option("lite")
                }
                create("grpckt") {
                    option("lite")
                }
            }
        }
    }
}
```

**Source directory:** Symlink or copy `protos/` into `android-server/src/main/proto/`.

---

## Step 4: Verify

```bash
# buf lint
cd AEGIS && buf lint
# Expected: no output (clean)

# Python
cd AEGIS/ai-server
python -c "
from generated.ellie import common_pb2
assert common_pb2.SafetyLevel.Name(1) == 'LEVEL_0_READ'
print('OK')
"
```

---

## CI Integration (Planned)

```yaml
# .github/workflows/proto-ci.yml
name: Proto CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bufbuild/buf-setup-action@v1
      - run: buf lint
      - run: buf breaking --against 'https://github.com/${{ github.repository }}.git#branch=main'
  generate-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install grpcio-tools
      - run: ./scripts/generate_protos.sh python
      - run: git diff --exit-code  # Generated code must match committed code
```

---

## Directory Structure

```
AEGIS/
├── protos/ellie/           # Proto definitions (source of truth)
├── buf.yaml                # buf configuration
├── scripts/
│   ├── generate_protos.ps1 # Windows generation script
│   └── generate_protos.sh  # Linux/macOS generation script
├── ai-server/src/generated/ellie/  # Python generated code (committed)
├── browser-server/src/generated/   # Node.js generated code (committed, when generated)
└── android-server/src/main/proto/  # Symlink to protos/ (Gradle generates code)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `protoc` not found | Install via `pip install grpcio-tools` and use `python -m grpc_tools.protoc` |
| Import errors in generated code | Run the generation script (it fixes import paths) |
| `buf` not found | `npm install -g @bufbuild/buf` |
| Generated code outdated | Re-run `.\scripts\generate_protos.ps1 -Language python` |

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
