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

# Interpreter that has grpcio-tools installed. Override when the project venv is not
# what `python` resolves to, e.g.
#   PYTHON_BIN=.venv/Scripts/python.exe ./scripts/generate_protos.sh
PYTHON_BIN="${PYTHON_BIN:-python}"

# The canonical set. Every entry must exist: this list used to name
# pc_server.proto, browser_server.proto and dev_server.proto — dev_server.proto was
# deleted with the Dev Server and the other two never existed, so `protoc` failed on
# a missing file and the script could not run at all. That is why the room server's
# generated copy drifted without anyone noticing.
PROTO_FILES=(
  common
  ai_server
  android_server
  room_server
)

# Servers that keep their own generated copy of the shared contract, and the protos
# each one actually consumes. A server must not receive stubs it does not import:
# compiling the full set into every target dropped ai_server/android_server stubs
# into the room server, which uses neither.
PYTHON_TARGETS=(
  "ai-server/src/generated"
  "room-server/src/generated"
)
AI_SERVER_PROTOS=("${PROTO_FILES[@]}")
ROOM_SERVER_PROTOS=(common room_server)

# ── Step 1: Lint ──────────────────────────────────────────────
echo -e "\033[36m[1/3] buf lint...\033[0m"
cd "$ROOT_DIR"
if command -v buf > /dev/null 2>&1; then
  buf lint
  echo -e "\033[32m  ✅ Lint passed\033[0m"
else
  echo -e "\033[33m  ⚠️  buf not found — skipping lint\033[0m"
  echo "     Install: npm install -g @bufbuild/buf"
fi

# ── Step 2: Generate ──────────────────────────────────────────
echo -e "\033[36m[2/3] Generating code for: $LANGUAGE\033[0m"

cd "$ROOT_DIR"
case "$LANGUAGE" in
  python)
    generate_python() {
      local target="$1"
      shift
      local proto_paths=()
      local name
      for name in "$@"; do
        proto_paths+=("protos/aegis/$name.proto")
      done

      mkdir -p "$target"

      "$PYTHON_BIN" -m grpc_tools.protoc \
        -I protos \
        --python_out="$target" \
        --grpc_python_out="$target" \
        --pyi_out="$target" \
        "${proto_paths[@]}"

      # protoc emits `from aegis import ...`, but every consumer exposes the stubs
      # as the `generated.aegis` package. The old rewrite produced
      # `from generated import ...`, which imports a module that does not exist —
      # so it only ever appeared to work because nobody re-ran it.
      find "$target/aegis" \( -name "*_pb2*.py" -o -name "*.pyi" \) -print0 |
        while IFS= read -r -d '' f; do
          sed -i 's/^from aegis import /from generated.aegis import /' "$f"
        done

      echo -e "\033[32m  ✅ Python stubs -> $target\033[0m"
    }

    generate_python "ai-server/src/generated" "${AI_SERVER_PROTOS[@]}"
    generate_python "room-server/src/generated" "${ROOM_SERVER_PROTOS[@]}"
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
    for target in "${PYTHON_TARGETS[@]}"; do
      FILE_COUNT=$(find "$target" -name "*_pb2*.py" 2>/dev/null | wc -l)
      if [ "$FILE_COUNT" -gt 0 ]; then
        echo -e "\033[32m  ✅ $FILE_COUNT Python stub files in $target\033[0m"
      else
        echo -e "\033[31m  ❌ No Python stubs found in $target\033[0m"
      fi
    done
    ;;
esac

echo -e "\033[32mDone.\033[0m"
