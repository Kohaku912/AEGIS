#!/usr/bin/env bash
# generate_protos.sh — Shell script for proto code generation
# Usage: ./scripts/generate_protos.sh [python|node|kotlin|all]
#
# Prerequisites:
#   Python: pip install grpcio-tools
#   buf:    npm install -g @bufbuild/buf
#   Node:   npm install -g grpc-tools grpc_tools_node_protoc_plugin

set -euo pipefail

LANGUAGE="${1:-python}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ── Step 1: Lint ──────────────────────────────────────────────
echo -e "\033[36m[1/3] buf lint...\033[0m"
cd "$ROOT_DIR"
buf lint
echo -e "\033[32m  ✅ Lint passed\033[0m"

# ── Step 2: Generate ──────────────────────────────────────────
echo -e "\033[36m[2/3] Generating code for: $LANGUAGE\033[0m"

cd "$ROOT_DIR"
case "$LANGUAGE" in
  python)
    OUT_DIR="ai-server/src/generated"
    mkdir -p "$OUT_DIR"

    python -m grpc_tools.protoc \
      -I protos \
      --python_out="$OUT_DIR" \
      --grpc_python_out="$OUT_DIR" \
      --pyi_out="$OUT_DIR" \
      protos/aegis/common.proto \
      protos/aegis/ai_server.proto \
      protos/aegis/pc_server.proto \
      protos/aegis/android_server.proto \
      protos/aegis/browser_server.proto \
      protos/aegis/room_server.proto \
      protos/aegis/dev_server.proto

    # Fix relative imports in generated files (Linux/macOS sed)
    for f in "$OUT_DIR"/*_pb2*.py; do
      sed -i '' 's/import aegis_common_pb2/from generated import common_pb2 as aegis_common_pb2/' "$f" 2>/dev/null || \
      sed -i 's/import aegis_common_pb2/from generated import common_pb2 as aegis_common_pb2/' "$f"
      sed -i '' 's/from aegis import/from generated import/' "$f" 2>/dev/null || \
      sed -i 's/from aegis import/from generated import/' "$f"
    done

    echo -e "\033[32m  ✅ Python stubs generated to: $OUT_DIR\033[0m"
    ;;
  node)
    OUT_DIR="browser-server/src/generated"
    mkdir -p "$OUT_DIR"

    if command -v grpc_tools_node_protoc &> /dev/null; then
      grpc_tools_node_protoc \
        --js_out="import_style=commonjs,binary:$OUT_DIR" \
        --grpc_out="grpc_js:$OUT_DIR" \
        --proto_path=protos \
        protos/aegis/*.proto
      echo -e "\033[32m  ✅ Node.js stubs generated to: $OUT_DIR\033[0m"
    else
      echo -e "\033[33m  ⚠️  grpc_tools_node_protoc not found."
      echo "     Install: npm install -g grpc-tools grpc_tools_node_protoc_plugin"
      echo "     Then re-run this script.\033[0m"
    fi
    ;;
  kotlin)
    echo -e "\033[33m  ⚠️  Kotlin code generation requires Gradle with protobuf plugin."
    echo "     See docs/proto-build.md for Gradle configuration."
    echo "     Generation happens automatically during Gradle build.\033[0m"
    ;;
  all)
    "$0" python
    "$0" node
    "$0" kotlin
    ;;
  *)
    echo "Unknown language: $LANGUAGE"
    echo "Usage: $0 [python|node|kotlin|all]"
    exit 1
    ;;
esac

# ── Step 3: Verify ────────────────────────────────────────────
echo -e "\033[36m[3/3] Verification...\033[0m"
cd "$ROOT_DIR"
case "$LANGUAGE" in
  python)
    FILE_COUNT=$(find "ai-server/src/generated" -name "*_pb2*.py" 2>/dev/null | wc -l)
    if [ "$FILE_COUNT" -gt 0 ]; then
      echo -e "\033[32m  ✅ $FILE_COUNT Python stub files generated\033[0m"
    else
      echo -e "\033[31m  ❌ No Python stubs found in ai-server/src/generated\033[0m"
    fi
    ;;
esac

echo -e "\033[32mDone.\033[0m"
