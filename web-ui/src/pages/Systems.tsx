import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

export function Systems({ overview }: { overview: UiOverview }) {
  const servers = overview.servers.data.items || [];
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h2>Systems</h2>
          <div className="muted">AI, PC, Android, Browser, Room, and Dev status.</div>
        </div>
        <Freshness generatedAt={overview.servers.generated_at} sourceUpdatedAt={overview.servers.source_updated_at} stale={overview.servers.stale} />
      </div>
      <div className="grid">
        {servers.map((server) => (
          <article className="list-row" key={server.server_id}>
            <div>
              <strong>{server.server_id}</strong>
              <div className="muted">
                {server.server_type || "service"} / {server.mode || "unknown"} / {server.host || "host"}:{server.port || "-"}
              </div>
              <div className="muted">{server.status_detail || server.degraded_reason || server.recovery_hint || "No recovery action needed."}</div>
            </div>
            <StatusBadge status={server.status} detail={server.recovery_hint} />
          </article>
        ))}
      </div>
    </section>
  );
}
