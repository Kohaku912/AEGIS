import { Activity, Brain, Clock, Cpu, Server } from "lucide-react";
import type { ReactNode } from "react";
import { AttentionStrip } from "../components/AttentionStrip";
import { CoreSphere } from "../components/CoreSphere";
import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import { serverLabel, serverNeedsDetail, summarizeMemory, summarizeServers } from "../displayModel";
import type { UiEvent, UiOverview } from "../types";

type Props = {
  overview: UiOverview;
  recentEvents: UiEvent[];
};

export function CommandCenter({ overview, recentEvents }: Props) {
  const core = overview.core.data;
  const servers = overview.servers.data.items || [];
  const task = overview.current_task.data;
  const usage = overview.usage.data;
  const serverSummary = summarizeServers(servers);
  const memorySummary = summarizeMemory(overview);
  const problemServers = servers.filter((server) => serverNeedsDetail(server));

  return (
    <>
      <section className="command-priority">
        <section className="panel command-operation">
          <div className="panel__header">
            <h2>Current Operation</h2>
            <StatusBadge status={String(core.mode || "IDLE")} />
          </div>
          <h3>{task.title || "No active task"}</h3>
          <p className="muted">{task.current_action || task.next_action || task.blocked_reason || "AEGIS is waiting for a meaningful signal or user request."}</p>
          <div className="stat-grid">
            <Metric icon={<Activity size={18} />} label="Activity" value={String(core.activity_level ?? 0)} />
            <Metric icon={<Brain size={18} />} label="Confidence" value={String(core.confidence || "Not reported")} />
            <Metric icon={<Cpu size={18} />} label="Approvals" value={String(core.pending_approval_count ?? 0)} />
            <Metric icon={<Clock size={18} />} label="Freshness" value={overview.freshness.stale ? "STALE" : "LIVE"} />
          </div>
        </section>
        <AttentionStrip items={overview.attention.data.items || []} />
      </section>

      <div className="grid grid--command">
        <section className="panel core-card">
          <CoreSphere
            mode={String(core.mode || "IDLE")}
            health={String(core.health || "ONLINE")}
            activityLevel={Number(core.activity_level || 1)}
            confidence={String(core.confidence || "medium")}
            servers={servers}
            visualEvents={[]}
            activeServerId={String(task.capability_id || "").split(".", 1)[0]}
            nextServerId=""
            approvalServerIds={(overview.approvals.data.pending || []).map((approval) => String(approval.capability_id || "").split(".", 1)[0])}
          />
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
        <section className="panel server-summary-card">
          <div className="panel__header"><h2>Systems</h2><Freshness {...freshProps(overview.servers)} /></div>
          <div className="server-summary-line">
            <Server size={18} />
            <strong>{serverSummary.ok} normal</strong>
            <span>{serverSummary.attention.length} need attention</span>
          </div>
          <div className="grid">
            {problemServers.length ? problemServers.slice(0, 4).map((server) => (
              <div className="list-row" key={server.server_id}>
                <div>
                  <strong>{serverLabel(server.server_id)}</strong>
                  <div className="muted">{server.status_detail || server.degraded_reason || server.recovery_hint || "Review server status."}</div>
                </div>
                <StatusBadge status={server.status} detail={server.recovery_hint} />
              </div>
            )) : <p className="muted">All configured systems are operating normally.</p>}
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Recent Events</h2><Freshness {...freshProps(overview.notifications)} /></div>
          <div className="grid">
            {recentEvents.length ? recentEvents.slice(0, 5).map((event) => (
              <div className="list-row" key={`${event.type}-${event.source_updated_at}-${event.message}`}>
                <div>
                  <strong>{event.type}</strong>
                  <div className="muted">{event.message || event.source_type}</div>
                </div>
              </div>
            )) : (overview.notifications.data.recent || []).slice(0, 5).map((item, index) => (
              <div className="list-row" key={String(item.notification_id || item.id || index)}>
                <div>
                  <strong>{String(item.title || "Notification")}</strong>
                  <div className="muted">{String(item.message || item.severity || "")}</div>
                </div>
              </div>
            ))}
            {recentEvents.length === 0 && (overview.notifications.data.recent || []).length === 0 ? <p className="muted">No recent events reported.</p> : null}
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Memory & Mind</h2><Freshness {...freshProps(overview.mind_summary)} /></div>
          <div className="grid">
            {Object.entries(memorySummary).map(([label, value]) => (
              <div className="stat" key={label}>
                <span className="muted">{label}</span>
                <b style={{ fontSize: 15 }}>{value}</b>
              </div>
            ))}
          </div>
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
