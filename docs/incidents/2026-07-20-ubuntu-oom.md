# Ubuntu OOM Incident - 2026-07-20

## Impact

The Ubuntu AI host became unresponsive. Cloudflare returned error 1033 because
the tunnel and Dashboard could no longer be reached. The host was manually
rebooted at approximately 13:46 JST.

## Evidence

- The previous boot journal ended without a normal shutdown record.
- The next boot performed ext4 orphan cleanup, confirming an unclean stop.
- At 13:33:21 the kernel recorded a global OOM and killed Chrome in the
  `aegis-browser-server-1` cgroup.
- The affected Browser container had no memory or PID limit.
- One hour after reboot it had again accumulated 802 PIDs and about 1.8 GiB of
  resident memory.
- Browser logs reported pending `BrowserSession._auto_reconnect()` tasks after
  task completion.

## Root Cause

`BrowserUseAgent` created a new browser-use `BrowserSession` for each task with
`keep_alive=True`, but did not stop that session. Chrome process trees and
auto-reconnect workers therefore survived completed tasks. Repeated autonomous
browser work eventually exhausted host memory. The dedicated display power
watcher also polled the expensive full UI Overview every five seconds, adding
avoidable AI Server pressure during the incident.

## Corrective Actions

- Browser sessions use `keep_alive=False` and are stopped in `finally`.
- Browser execution remains serialized while health requests use independent
  HTTP threads.
- Browser health exposes cgroup memory/PID pressure and returns 503 at the
  critical threshold so Docker can restart it.
- Docker limits Browser to 3 GiB memory, 4 GiB including swap, and 512 PIDs.
- Docker limits AI Server to 6 GiB memory, 8 GiB including swap, and 512 PIDs.
- Display power polling uses compact `/display/power-state`, bounded backoff,
  rate-limited errors, and fail-open display wake behavior.
- Ubuntu healthcheck fails when production memory/PID limits are absent.

## Acceptance Checks

```bash
docker inspect aegis-browser-server-1 \
  --format 'memory={{.HostConfig.Memory}} swap={{.HostConfig.MemorySwap}} pids={{.HostConfig.PidsLimit}}'
docker stats --no-stream aegis-ai-server-1 aegis-browser-server-1
curl -fsS http://127.0.0.1:8090/display/power-state
scripts/ubuntu/healthcheck.sh
```

The incident is considered contained when repeated real Browser tasks return
the Browser container to its idle process baseline and the host journal records
no new OOM event.

## Verification Record

- Two consecutive real Browser Agent tasks completed against a safe public test
  page and left no Chrome process behind.
- Browser returned to two process/thread entries and approximately 125-140 MiB
  after cleanup; cgroup `oom_kill` remained zero.
- Browser now runs with Docker init, explicitly reaps exited browser children,
  exposes zombie counts in health, and returned to `zombie_processes=0` after
  two further real tasks.
- The kiosk user service is bounded by `MemoryHigh=1G`, `MemoryMax=1536M`, and
  `TasksMax=512` so a display process failure cannot consume the whole host.
- After rebuilding and normalizing the Compose container names, Ubuntu
  `healthcheck.sh` passed with AI and Browser healthy.
- Cloudflare `/auth/login` returned HTTP 200 and unauthenticated `/dashboard`
  redirected to `/auth/login`.
- systemd restored AI, Cloudflare, the network watchdog, kiosk, and display
  power watcher after reboot; all are enabled and active.
