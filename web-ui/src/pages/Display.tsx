import { CoreSphere } from "../components/CoreSphere";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

export function Display({ overview }: { overview: UiOverview }) {
  const core = overview.core.data;
  const servers = overview.servers.data.items || [];
  const task = overview.current_task.data;
  const approvals = overview.approvals.data.pending || [];
  return (
    <main className="display-shell">
      <header className="top-bar">
        <div className="brand">
          <span className="brand__name">AEGIS</span>
          <span className="brand__sub">Dedicated Display / Read Only</span>
        </div>
        <StatusBadge status={String(core.health || "ONLINE")} />
      </header>
      <section className="display-grid">
        <aside className="panel">
          <div className="panel__header"><h2>AI State</h2></div>
          <div className="grid">
            <div className="stat"><span className="muted">Mode</span><b>{String(core.mode || "IDLE")}</b></div>
            <div className="stat"><span className="muted">Goal</span><b style={{ fontSize: 16 }}>{String(core.active_goal || "No active goal")}</b></div>
            <div className="stat"><span className="muted">Confidence</span><b>{String(core.confidence || "medium")}</b></div>
            <div className="stat"><span className="muted">Task</span><b style={{ fontSize: 16 }}>{task.title}</b></div>
          </div>
        </aside>
        <section className="display-core">
          <CoreSphere
            mode={String(core.mode || "IDLE")}
            health={String(core.health || "ONLINE")}
            activityLevel={Number(core.activity_level || 1)}
            confidence={String(core.confidence || "medium")}
            servers={servers}
          />
        </section>
        <aside className="panel">
          <div className="panel__header"><h2>Attention</h2></div>
          <div className="grid">
            {approvals.slice(0, 3).map((approval) => (
              <div className="attention-item" data-severity="warning" key={approval.approval_id}>
                <div>
                  <strong>Approval</strong>
                  <div className="muted">{approval.summary || approval.capability_id}</div>
                </div>
              </div>
            ))}
            {(overview.attention.data.items || []).filter((item) => item.kind !== "approval").slice(0, 5).map((item) => (
              <div className="attention-item" data-severity={item.severity} key={item.id}>
                <div>
                  <strong>{item.title}</strong>
                  <div className="muted">{item.message}</div>
                </div>
              </div>
            ))}
            {approvals.length === 0 && (overview.attention.data.items || []).length === 0 ? <div className="muted">No immediate attention required.</div> : null}
          </div>
        </aside>
      </section>
      <footer className="panel" style={{ marginTop: 24 }}>
        <div className="grid grid--three">
          {servers.slice(0, 6).map((server) => (
            <div className="list-row" key={server.server_id}>
              <div>
                <strong>{server.server_id}</strong>
                <div className="muted">{server.status_detail || server.recovery_hint || server.mode}</div>
              </div>
              <StatusBadge status={server.status} />
            </div>
          ))}
        </div>
      </footer>
    </main>
  );
}
