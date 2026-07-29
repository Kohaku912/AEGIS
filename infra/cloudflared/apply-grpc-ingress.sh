#!/usr/bin/env bash
# DEPRECATED: public gRPC hostname is blocked on Cloudflare Free
# (application/grpc → HTTP 403; long_lived_grpc not editable).
#
# Use instead:
#   bash infra/cloudflared/apply-warp-private-network.sh
#
# This wrapper forwards to the WARP private-network script.

set -euo pipefail
echo "DEPRECATED: apply-grpc-ingress.sh → apply-warp-private-network.sh" >&2
exec bash "$(dirname "$0")/apply-warp-private-network.sh"
