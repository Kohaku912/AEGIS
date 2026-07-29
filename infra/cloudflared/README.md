# Cloudflare Tunnel — Android via WARP (private network)

Production path for Android **outside the LAN** (cellular / away from home Wi‑Fi).

**Do not** publish Core gRPC (`50051`) on a public hostname. Cloudflare Free
blocks `application/grpc` on public hostnames (`long_lived_grpc` is not
editable). Use **Zero Trust private networking + Cloudflare One (WARP)** instead.

## Architecture

```
Android (cellular)
  → Cloudflare One / WARP (team: kawaharahome)
  → Cloudflare edge
  → cloudflared on Ubuntu (tunnel AEGIS)
  → 192.168.50.41:50051  (plaintext gRPC / h2c)
```

On home Wi‑Fi the phone reaches `192.168.50.41:50051` directly. With WARP
enrolled, the **same address** works off-LAN because Split Tunnels Include
sends that CIDR into the tunnel.

| Setting | Value |
|---------|--------|
| Tunnel ID | `4939347a-cdf3-41f6-bb3e-646b883a54a3` (name: `AEGIS`) |
| Private CIDR | `192.168.50.41/32` |
| Team domain | `kawaharahome.cloudflareaccess.com` |
| WARP org name | `kawaharahome` |
| Split Tunnels | **Exclude** without `192.168.0.0/16` on **Default and any matching custom profile** (WARP onboarding profiles override Default) |
| Dashboard public hosts | `kawahara.pp.ua` / `aegis.kawahara.pp.ua` → `http://127.0.0.1:8090` |

## Apply / refresh (API)

Requires a token with Tunnel Edit + Zero Trust Networks Write + Device Write:

```bash
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=984d706b177f0a3abdfa2849fe3c1cff
export TUNNEL_ID=4939347a-cdf3-41f6-bb3e-646b883a54a3
bash infra/cloudflared/apply-warp-private-network.sh
```

This script:

1. Ensures teamnet route `192.168.50.41/32` → tunnel `AEGIS`
2. Enables `warp-routing` on the tunnel
3. Keeps Dashboard public hostnames (no public `grpc.*` ingress)
4. Sets Split Tunnels on **Default and matching custom profiles** (WARP
   onboarding profiles override Default) to Exclude **without** `192.168.0.0/16`.

## Android phone setup

1. Install **Cloudflare One** (formerly WARP) from Play Store.
2. Open the app → tap the menu → **Account** / organization → enter `kawaharahome`.
3. Complete device enrollment (Zero Trust login / policy as configured).
4. Turn WARP **Connected**, then toggle **OFF → ON** after any Split Tunnel
   policy change so Android refreshes routes.
5. Confirm VPN routes do **not** include `192.168.0.0/16 throw` (that exclusion
   makes Core unreachable on cellular).
6. In AEGIS Android Settings, keep Core host `192.168.50.41` port `50051` (plaintext).
7. Connect. Pairing token still required.

Verify off Wi‑Fi (airplane mode + cellular, or disable Wi‑Fi): AEGIS should stay
connected to Core.

## Dashboard-only public ingress

Remotely managed tunnels (token mode) only need HTTP ingress for the Dashboard:

```yaml
ingress:
  - hostname: kawahara.pp.ua
    service: http://127.0.0.1:8090
  - hostname: aegis.kawahara.pp.ua
    service: http://127.0.0.1:8090
  - service: http_status:404
warp-routing:
  enabled: true
```

Private gRPC is **not** an ingress hostname; it is a teamnet route.

## Deprecated: public `grpc.kawahara.pp.ua`

Earlier experiments used a public hostname with `http2Origin`. On Free plan,
Cloudflare returns HTTP **403** for `Content-Type: application/grpc`. Keep DNS
if desired, but do not point Android at it. Prefer deleting that public hostname
from the tunnel config (the apply script does this).

## Ops checks

```bash
# Tunnel has warp-routing + dashboard ingress only
# Route exists for 192.168.50.41/32
# Device profile include list contains 192.168.50.41/32

ss -lntp | grep 50051   # Core must listen on the LAN IP WARP targets
```
