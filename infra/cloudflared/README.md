# Cloudflare Tunnel — Android gRPC

Production path for Android **outside the LAN** (cellular / away from home Wi‑Fi).
Do **not** publish host port `50051` to the public WAN. Terminate TLS at
Cloudflare and keep Access Service Auth in front of the tunnel hostname.

## Hostname

| Public | Origin |
|--------|--------|
| `grpc.kawahara.pp.ua:443` | `http://192.168.50.41:50051` (production publishes Core on the LAN bind; not loopback-only) |

LAN Wi‑Fi may still use plaintext `192.168.50.41:50051`. The Android app tries
LAN first on Wi‑Fi, then falls back to this Cloudflare hostname.

## Ingress snippet

Merge into the host cloudflared config (typically `/etc/cloudflared/config.yml`):

```yaml
ingress:
  - hostname: grpc.kawahara.pp.ua
    service: http://192.168.50.41:50051
    originRequest:
      # gRPC requires HTTP/2 to the origin
      http2Origin: true
  # ... existing dashboard / other hostnames ...
  - service: http_status:404
```

> Note: if Core is rebound to `127.0.0.1:50051` only, change the origin to
> `http://127.0.0.1:50051`.

Then:

```bash
# Route DNS (once)
cloudflared tunnel route dns <TUNNEL_NAME> grpc.kawahara.pp.ua

sudo systemctl restart cloudflared
```

## Cloudflare dashboard

1. Zone **Network** → enable **gRPC** for the zone (or hostname).
2. Zero Trust → Access → Applications → Add application for `grpc.kawahara.pp.ua`.
3. Policy: **Service Auth** only (no public bypass).
4. Create a **Service Token**; store Client ID / Client Secret in Android Settings
   (or Intent extras). Never bake them into the APK or commit them.

Android sends headers on every gRPC call:

- `cf-access-client-id`
- `cf-access-client-secret`

AEGIS pairing token remains required for Core auth.

## Remotely managed tunnels (token mode)

Production Ubuntu runs `cloudflared tunnel run --token ...` (no local
`config.yml`). Public hostnames are managed in Zero Trust → Networks → Tunnels
or via API:

```bash
export CLOUDFLARE_API_TOKEN=...   # Tunnel Edit + DNS Edit
export CLOUDFLARE_ACCOUNT_ID=984d706b177f0a3abdfa2849fe3c1cff
export TUNNEL_ID=4939347a-cdf3-41f6-bb3e-646b883a54a3
bash infra/cloudflared/apply-grpc-ingress.sh
```

Required published applications (correct origins):

| Hostname | Service |
|----------|---------|
| `kawahara.pp.ua` | `http://127.0.0.1:8090` |
| `aegis.kawahara.pp.ua` | `http://127.0.0.1:8090` |
| `grpc.kawahara.pp.ua` | `http://192.168.50.41:50051` with `http2Origin: true` |

Do **not** use `https://localhost:50051` — AI gRPC is plaintext HTTP/2 on the LAN bind.

```bash
# From any network: TLS edge responds
curl -sI --http2 https://grpc.kawahara.pp.ua/ | head

# Confirm Core bind on the Ubuntu host (LAN and/or loopback — not 0.0.0.0 WAN)
ss -lntp | grep 50051
```

## Example config file

See [ingress.grpc.example.yml](ingress.grpc.example.yml).
