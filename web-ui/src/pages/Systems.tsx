import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";
import { serverDependencySummary, serverLabel } from "../displayModel";

export function Systems({ overview }: { overview: UiOverview }) {
  const servers = overview.servers.data.items || [];
  const android = servers.find((server) => server.server_id === "android-server");
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Systems</h2>
            <div className="muted">AI, PC, Android, Browser, Room, and Dev status with dependencies and recovery hints.</div>
          </div>
          <Freshness generatedAt={overview.servers.generated_at} sourceUpdatedAt={overview.servers.source_updated_at} stale={overview.servers.stale} />
        </div>
        <div className="topology-row" aria-label="Server topology">
          {servers.map((server, index) => (
            <div className="topology-node" data-status={String(server.status || "").toUpperCase()} key={server.server_id}>
              <strong>{serverLabel(server.server_id)}</strong>
              <span>{server.mode || "unknown"}</span>
              {index < servers.length - 1 ? <i aria-hidden="true" /> : null}
            </div>
          ))}
        </div>
        <div className="dependency-map" aria-label="Server dependency map">
          {servers.map((server) => (
            <div className="dependency-map__row" key={`${server.server_id}-deps`}>
              <strong>{serverLabel(server.server_id)}</strong>
              <span>{dependencyNames(server).join(" / ") || "No dependencies reported"}</span>
            </div>
          ))}
        </div>
      </section>
      <section className="systems-grid">
        {servers.map((server) => (
          <article className="panel system-card" key={server.server_id}>
            <div className="panel__header">
              <div>
                <h2>{serverLabel(server.server_id)}</h2>
                <div className="muted mono">{server.server_id}</div>
              </div>
              <StatusBadge status={server.status} detail={server.recovery_hint} />
            </div>
            <div className="metric-list">
              <div className="metric-row"><span>Endpoint</span><strong>{server.host || "host"}:{server.port || "-"}</strong></div>
              <div className="metric-row"><span>Mode</span><strong>{server.mode || "No data yet"}</strong></div>
              <div className="metric-row"><span>Capabilities</span><strong>{server.registered_capabilities || "No data yet"}</strong></div>
              <div className="metric-row"><span>Capability health</span><strong>{formatCapabilityHealth(server.capability_health)}</strong></div>
              <div className="metric-row"><span>Latency</span><strong>{formatLatency(server.latency_ms)}</strong></div>
              <div className="metric-row"><span>Heartbeat age</span><strong>{server.heartbeat_age_seconds ?? "No data yet"}</strong></div>
              <div className="metric-row"><span>Last healthy</span><strong>{lastHealthy(server)}</strong></div>
              <div className="metric-row"><span>Active task</span><strong className="mono">{server.active_task_id || "No active task"}</strong></div>
              <div className="metric-row"><span>Permissions</span><strong>{formatMissingPermissions(server.permission_missing)}</strong></div>
              <div className="metric-row"><span>Version</span><strong>{server.version || "No data yet"}</strong></div>
              <div className="metric-row"><span>Dependencies</span><strong>{serverDependencySummary(server)}</strong></div>
            </div>
            <div>
              <div className="muted">{server.status_detail || server.degraded_reason || "No active issue reported."}</div>
              {server.recovery_hint ? <div className="recovery-hint">{server.recovery_hint}</div> : null}
            </div>
          </article>
        ))}
      </section>
      <section className="panel">
        <div className="panel__header"><h2>Android Detail</h2></div>
        {android ? <AndroidDetail server={android} /> : <p className="muted">Android status is not reported.</p>}
      </section>
    </div>
  );
}

function dependencyNames(server: NonNullable<UiOverview["servers"]["data"]["items"][number]>): string[] {
  const dependencies = (server.dependencies || {}) as Record<string, unknown>;
  return Object.entries(dependencies)
    .filter(([, value]) => typeof value === "boolean" || typeof value === "string" || typeof value === "number")
    .slice(0, 4)
    .map(([key, value]) => `${key}:${String(value)}`);
}

function lastHealthy(server: NonNullable<UiOverview["servers"]["data"]["items"][number]>): string {
  const dependencies = (server.dependencies || {}) as Record<string, unknown>;
  return String(
    server.last_healthy_at ||
    dependencies.last_healthy_at ||
    dependencies.last_online_at ||
    server.health_checked_at ||
    dependencies.last_seen ||
    "No data yet"
  );
}

function formatLatency(value?: number): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "No data yet";
  return `${Math.round(value)} ms`;
}

function formatMissingPermissions(value?: string[] | boolean): string {
  if (value === true) return "Missing permission reported";
  if (value === false) return "None reported";
  if (!value || !value.length) return "None reported";
  return value.join(", ");
}

function formatCapabilityHealth(value?: Record<string, unknown>): string {
  if (!value || !Object.keys(value).length) return "No data yet";
  const ok = Number(value.ok ?? value.available ?? 0);
  const degraded = Number(value.degraded ?? 0);
  const unavailable = Number(value.unavailable ?? value.failed ?? 0);
  const parts = [];
  if (ok) parts.push(`${ok} ok`);
  if (degraded) parts.push(`${degraded} degraded`);
  if (unavailable) parts.push(`${unavailable} unavailable`);
  return parts.join(" / ") || Object.entries(value).slice(0, 3).map(([key, val]) => `${key}:${String(val)}`).join(" / ");
}

function AndroidDetail({ server }: { server: NonNullable<UiOverview["servers"]["data"]["items"][number]> }) {
  const dependencies = (server.dependencies || {}) as Record<string, unknown>;
  const availability = (dependencies.capability_availability || {}) as Record<string, Record<string, unknown>>;
  const permissions = (dependencies.permission_status || {}) as Record<string, unknown>;
  return (
    <div className="android-detail">
      <div className="stat-grid">
        <div className="stat"><span className="muted">Device</span><b>{String(dependencies.device_model || "No data yet")}</b></div>
        <div className="stat"><span className="muted">Connection</span><b>{String(server.mode || dependencies.connection_mode || "No data yet")}</b></div>
        <div className="stat"><span className="muted">Last seen</span><b>{String(dependencies.last_seen || "No data yet")}</b></div>
        <div className="stat"><span className="muted">Active approvals</span><b>{Array.isArray(dependencies.active_approvals) ? dependencies.active_approvals.length : 0}</b></div>
      </div>
      <div className="grid grid--three">
        <div>
          <h3>Permissions</h3>
          <div className="metric-list">
            {Object.entries(permissions).length ? Object.entries(permissions).map(([key, value]) => <div className="metric-row" key={key}><span>{key}</span><strong>{String(value)}</strong></div>) : <div className="metric-row"><span>Status</span><strong>No data yet</strong></div>}
          </div>
        </div>
        <div>
          <h3>Capabilities</h3>
          <div className="metric-list">
            {Object.entries(availability).slice(0, 8).map(([key, value]) => <div className="metric-row" key={key}><span className="mono">{key.replace("android-server.", "")}</span><strong>{String(value.available ?? "unknown")}</strong></div>)}
            {!Object.entries(availability).length ? <div className="metric-row"><span>Status</span><strong>No data yet</strong></div> : null}
          </div>
        </div>
        <div>
          <h3>Recovery</h3>
          <p className="muted">{server.recovery_hint || "No recovery action needed."}</p>
        </div>
      </div>
    </div>
  );
}

