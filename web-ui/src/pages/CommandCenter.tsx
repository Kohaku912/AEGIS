import { Activity, Brain, Clock, Cpu } from "lucide-react";
import type { ReactNode } from "react";
import { AttentionStrip } from "../components/AttentionStrip";
import { CoreSphere } from "../components/CoreSphere";
import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type Props = {
  overview: UiOverview;
};

export function CommandCenter({ overview }: Props) {
  const core = overview.core.data;
  const servers = overview.servers.data.items || [];
  const task = overview.current_task.data;
  const usage = overview.usage.data;
  return (
    <>
      <AttentionStrip items={overview.attention.data.items || []} />
      <div className="grid grid--command">
        <section className="panel core-card">
          <CoreSphere
            mode={String(core.mode || "IDLE")}
            health={String(core.health || "ONLINE")}
            activityLevel={Number(core.activity_level || 1)}
            confidence={String(core.confidence || "medium")}
            servers={servers}
          />
          <div className="grid">
            <div className="panel__header">
              <h2>Current Operation</h2>
              <StatusBadge status={String(core.mode || "IDLE")} />
            </div>
            <div>
              <h3>{task.title}</h3>
              <p className="muted">{task.current_action || task.next_action || "AEGIS is waiting for a meaningful signal or user request."}</p>
            </div>
            <div className="stat-grid">
              <Metric icon={<Activity size={18} />} label="Activity" value={String(core.activity_level ?? 0)} />
              <Metric icon={<Brain size={18} />} label="Confidence" value={String(core.confidence || "unknown")} />
              <Metric icon={<Cpu size={18} />} label="Approvals" value={String(core.pending_approval_count ?? 0)} />
              <Metric icon={<Clock size={18} />} label="Freshness" value={overview.freshness.stale ? "STALE" : "LIVE"} />
            </div>
          </div>
        </section>
        <section className="panel">
          <div className="panel__header">
            <h2>AI State</h2>
            <Freshness {...freshProps(overview.core)} />
          </div>
          <div className="grid">
            <div className="stat">
              <span className="muted">Active goal</span>
              <b style={{ fontSize: 16 }}>{String(core.active_goal || "No active goal")}</b>
            </div>
            <div className="stat">
              <span className="muted">Attention level</span>
              <b style={{ fontSize: 16 }}>{String(core.attention_level || "normal")}</b>
            </div>
            <div className="stat">
              <span className="muted">LLM usage</span>
              <b style={{ fontSize: 16 }}>{String(usage.summary || usage.total_tokens || "Audit-backed")}</b>
            </div>
          </div>
        </section>
      </div>
      <div className="grid grid--three" style={{ marginTop: 16 }}>
        <section className="panel">
          <div className="panel__header"><h2>Server Health</h2><Freshness {...freshProps(overview.servers)} /></div>
          <div className="grid">
            {servers.slice(0, 6).map((server) => (
              <div className="list-row" key={server.server_id}>
                <div>
                  <strong>{server.server_id}</strong>
                  <div className="muted">{server.status_detail || server.mode || "No detail"}</div>
                </div>
                <StatusBadge status={server.status} detail={server.recovery_hint} />
              </div>
            ))}
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Notifications</h2><Freshness {...freshProps(overview.notifications)} /></div>
          <div className="grid">
            {(overview.notifications.data.recent || []).slice(0, 5).map((item, index) => (
              <div className="list-row" key={String(item.notification_id || item.id || index)}>
                <div>
                  <strong>{String(item.title || "Notification")}</strong>
                  <div className="muted">{String(item.message || item.severity || "")}</div>
                </div>
              </div>
            ))}
            {(overview.notifications.data.recent || []).length === 0 ? <p className="muted">No recent notifications.</p> : null}
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Memory & Mind</h2><Freshness {...freshProps(overview.mind_summary)} /></div>
          <pre className="mono muted" style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(overview.mind_summary.data, null, 2).slice(0, 900)}</pre>
        </section>
      </div>
    </>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="stat">
      <span className="muted">{icon} {label}</span>
      <b>{value}</b>
    </div>
  );
}

function freshProps(section: { generated_at: number; source_updated_at: number; stale: boolean }) {
  return { generatedAt: section.generated_at, sourceUpdatedAt: section.source_updated_at, stale: section.stale };
}
