import { Activity, Brain, Clock, Cpu, Radio, Server, ShieldAlert, UserRound } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { runControlAction } from "../api/client";
import { AttentionStrip } from "../components/AttentionStrip";
import { CognitiveField } from "../components/cognitive-field/CognitiveField";
import { Freshness } from "../components/Freshness";
import { SectionState } from "../components/UiState";
import { StatusBadge } from "../components/StatusBadge";
import { missionPhase, serverLabel, serverNeedsDetail, summarizeMemory, summarizeServers } from "../displayModel";
import type { EntitySummary, UiEvent, UiOverview } from "../types";

type Props = {
  overview: UiOverview;
  recentEvents?: UiEvent[];
  pinnedEntities?: EntitySummary[];
  onSelect?: (entity: EntitySummary) => void;
};

export function CommandCenter({ overview, pinnedEntities = [], onSelect }: Props) {
  const core = overview.core.data;
  const servers = overview.servers.data.items || [];
  const task = overview.current_task.data;
  const usage = overview.usage.data;
  const user = overview.user_situation?.data || overview.user_state.data || {};
  const commitments = overview.commitments.data.items || [];
  const errors = overview.errors?.data.items || [];
  const connection = overview.connection?.data || {};
  const serverSummary = summarizeServers(servers);
  const memorySummary = summarizeMemory(overview);
  const problemServers = servers.filter((server) => serverNeedsDetail(server));
  const phase = missionPhase(overview);
  const criticalCount = [...(overview.attention.data.items || []), ...errors].filter((item) => String(item.severity || "").toLowerCase() === "critical").length;
  const operations = overview.activity?.data.operations || [];
  const timeline = (
    operations.length
      ? operations.map((op) => ({
          id: String(op.operation_id || op.title || "operation"),
          title: `${op.kind_label || op.kind || "Operation"}: ${op.title || "Untitled"}`,
          message: String(op.what_happened || op.summary || ""),
          priority: String(op.priority || (op.error_count ? "P1" : "P3")),
          status: String(op.status || ""),
          steps: op.steps || [],
        }))
      : (overview.activity?.data.groups || [])
          .filter((group) => String(group.operation_type || "") !== "system")
          .map((group, index) => ({
            id: String(group.group_id || index),
            title: String(group.title || "Activity"),
            message: String(group.summary || `${Number((group.events as unknown[])?.length || 0)} event(s)`),
            priority: String(group.severity || "P3") === "critical" ? "P1" : "P3",
            status: String(group.status || ""),
            steps: [],
          }))
  ).slice(0, 8);
  const [control, setControl] = useState<{ action: string; preview: Record<string, unknown> }>();
  const [controlStatus, setControlStatus] = useState("");
  const previewControl = async (action: string) => {
    setControlStatus("Building Manager-backed action preview...");
    try {
      const payload = await runControlAction(action);
      setControl({ action, preview: payload.preview as Record<string, unknown> });
      setControlStatus("");
    } catch (error) {
      setControlStatus(error instanceof Error ? error.message : "Control preview failed");
    }
  };
  const confirmControl = async () => {
    if (!control) return;
    setControlStatus("Executing and verifying control action...");
    try {
      await runControlAction(control.action, true);
      setControl(undefined);
      setControlStatus("Control action verified and audited.");
    } catch (error) {
      setControlStatus(error instanceof Error ? error.message : "Control action failed");
    }
  };

  return (
    <div className="command-center">
      <section className="command-hud" aria-label="Command HUD">
        <HudMetric icon={<Radio size={16} />} label="Core" value={`${String(core.mode || "IDLE")} / ${String(core.health || "ONLINE")}`} />
        <HudMetric icon={<Activity size={16} />} label="Phase" value={phase} />
        <HudMetric icon={<Server size={16} />} label="Connection" value={`${connection.online_count ?? serverSummary.ok}/${connection.total_count ?? servers.length} online`} />
        <HudMetric icon={<ShieldAlert size={16} />} label="Approvals" value={String(core.pending_approval_count ?? overview.approvals.data.pending_count ?? 0)} />
        <HudMetric icon={<Brain size={16} />} label="Profile" value={String((overview.mind_summary.data.autonomy as Record<string, unknown> | undefined)?.profile || core.attention_level || "normal")} />
        <HudMetric icon={<Clock size={16} />} label="Freshness" value={overview.freshness.stale ? "STALE" : "LIVE"} />
      </section>

      <section className="command-attention">
        <AttentionStrip items={overview.attention.data.items || []} />
        <SectionState stale={overview.attention.stale} error={overview.attention.error} empty={(overview.attention.data.items || []).length === 0 && criticalCount > 0} label="Attention" />
      </section>

      <section className="command-controls" aria-label="Master controls">
        <a href="/chat"><Brain size={14} />Instruct AEGIS</a>
        <button type="button" onClick={() => void previewControl("pause-autonomy")}><Activity size={14} />Pause autonomy</button>
        <button type="button" onClick={() => void previewControl("pause-all-tasks")}><Clock size={14} />Pause all tasks</button>
        <button type="button" onClick={() => void previewControl("refresh-all-servers")}><Server size={14} />Refresh systems</button>
        <a href="/settings/privacy"><ShieldAlert size={14} />Privacy mode</a>
        <a href="/dashboard/communications/presentation-surfaces"><Radio size={14} />Present</a>
        <button className="command-controls__emergency" type="button" onClick={() => void previewControl("emergency-stop")}><ShieldAlert size={14} />Emergency stop</button>
      </section>
      {controlStatus ? <div className="attention-item" data-severity={controlStatus.includes("failed") ? "warning" : "info"}>{controlStatus}</div> : null}
      {control ? (
        <section className="action-preview command-control-preview" aria-label="Control action preview">
          <h3>Review master control action</h3>
          <dl>{Object.entries(control.preview).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{String(value)}</dd></div>)}</dl>
          <footer><button className="secondary-button" type="button" onClick={() => setControl(undefined)}>Cancel</button><button className={control.action === "emergency-stop" ? "danger-button" : "primary-button"} type="button" onClick={() => void confirmControl()}>Confirm action</button></footer>
        </section>
      ) : null}

      {pinnedEntities.length ? <section className="command-pins" aria-label="Pinned resources"><span>Pinned</span>{pinnedEntities.map((entity) => <button type="button" onClick={() => onSelect?.(entity)} key={`${entity.type}:${entity.id}`}><strong>{entity.title}</strong><small>{entity.type} / {entity.status}</small></button>)}</section> : null}

      <section className="command-grid-12">
        <article className="panel command-operation command-span-8">
          <div className="panel__header">
            <div>
              <h2>Current Operation</h2>
              <div className="muted mono">{task.task_id || "no active task id"}</div>
            </div>
            <StatusBadge status={String(core.mode || "IDLE")} />
          </div>
          <h3>{task.title || "No active task"}</h3>
          <p className="command-operation__action">{task.current_action || task.next_action || task.blocked_reason || "AEGIS is waiting for a meaningful signal or user request."}</p>
          <div className="operation-map" aria-label="Operation map">
            <span data-active="true">Observe</span>
            <span data-active={phase === "Planning"}>Plan</span>
            <span data-active={phase === "Executing"}>Execute</span>
            <span data-active={Boolean(task.verification_summary)}>Verify</span>
            <span data-active={String(task.phase).toLowerCase() === "completed"}>Complete</span>
          </div>
          <div className="mission-strip" aria-label="Mission context">
            <span>Next: <strong>{task.next_action || "No data yet"}</strong></span>
            <span>Capability: <strong>{task.capability_id || "No data yet"}</strong></span>
            <span>Verification: <strong>{task.verification_summary || "No data yet"}</strong></span>
            <span>Blocked: <strong>{task.blocked_reason || "No"}</strong></span>
          </div>
          {task.conversation_id ? (
            <a className="operation-conversation-link" href={`/chat?conversation_id=${encodeURIComponent(task.conversation_id)}`}>
              Open related conversation
            </a>
          ) : null}
        </article>

        <article className="panel command-ai-state command-span-4">
          <div className="panel__header">
            <h2>AI State</h2>
            <Freshness {...freshProps(overview.core)} />
          </div>
          <Metric icon={<Brain size={18} />} label="Active goal" value={String(core.active_goal || "No active goal")} compact />
          <Metric icon={<Activity size={18} />} label="Confidence" value={String(core.confidence || "No data yet")} compact />
          <Metric icon={<Cpu size={18} />} label="LLM budget" value={String(usage.budget_state || usage.autonomous_suppression || usage.cost_state || "No data yet")} compact />
          <Metric icon={<ShieldAlert size={18} />} label="Critical" value={String(criticalCount)} compact />
        </article>

        <section className="panel core-card command-span-8">
          <CognitiveField
            mode={String(core.mode || "IDLE")}
            health={String(core.health || "ONLINE")}
            activityLevel={Number(core.activity_level || 1)}
            confidence={String(core.confidence || "medium")}
            servers={servers}
            visualEvents={[]}
            activeServerId={String(task.capability_id || "").split(".", 1)[0]}
            nextServerId={nextServerFromTask(task)}
            approvalServerIds={(overview.approvals.data.pending || []).map((approval) => String(approval.capability_id || "").split(".", 1)[0])}
            currentAction={task.current_action || task.title}
            nextAction={task.next_action}
          />
        </section>

        <section className="panel command-situation command-span-4">
          <div className="panel__header"><h2>Situation</h2><UserRound size={16} /></div>
          <div className="metric-list">
            <Row label="User" value={String(user.summary || user.availability || "No data yet")} />
            <Row label="Commitments" value={overview.commitments.data.summary || `${commitments.length} active`} />
            <Row label="Usage" value={String(usage.summary || usage.total_tokens || "Audit-backed")} />
            <Row label="Open issues" value={String(errors.length || overview.errors?.data.count || 0)} />
          </div>
        </section>

        <section className="panel command-span-4 server-summary-card">
          <div className="panel__header"><h2>Systems</h2><Freshness {...freshProps(overview.servers)} /></div>
          <div className="server-summary-line">
            <Server size={18} />
            <strong>{serverSummary.ok} normal</strong>
            <span>{serverSummary.attention.length} need attention</span>
          </div>
          <div className="compact-list">
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

        <section className="panel command-span-4">
          <div className="panel__header"><h2>Memory & Mind</h2><Freshness {...freshProps(overview.mind_summary)} /></div>
          <div className="metric-list">
            {Object.entries(memorySummary).map(([label, value]) => <Row label={label} value={value} key={label} />)}
          </div>
        </section>

        <section className="panel command-span-4">
          <div className="panel__header"><h2>Recent Operation Timeline</h2><Freshness {...freshProps(overview.activity || overview.notifications)} /></div>
          <div className="timeline-list">
            {timeline.length ? timeline.map((item) => (
              <div className="timeline-item" data-priority={item.priority} key={item.id}>
                <span>{item.priority}</span>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.message}</p>
                  {item.status ? <small className="muted">{item.status}{item.steps.length ? ` · ${item.steps.length} step(s)` : ""}</small> : null}
                </div>
              </div>
            )) : <p className="muted">No recent AEGIS operations reported.</p>}
          </div>
        </section>
      </section>
    </div>
  );
}

function HudMetric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return <div className="hud-metric"><span>{icon}{label}</span><strong>{value}</strong></div>;
}

function Metric({ icon, label, value, compact = false }: { icon: ReactNode; label: string; value: string; compact?: boolean }) {
  return (
    <div className={compact ? "stat stat--compact" : "stat"}>
      <span className="muted">{icon} {label}</span>
      <b>{value}</b>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return <div className="metric-row"><span>{label}</span><strong>{value}</strong></div>;
}

function nextServerFromTask(task: { steps?: Array<Record<string, unknown>> }): string {
  const pending = (task.steps || []).find((step) => ["pending", "ready"].includes(String(step.status || "").toLowerCase()));
  return String(pending?.capability_id || "").split(".", 1)[0] || "";
}

function freshProps(section: { generated_at: number; source_updated_at: number; stale: boolean }) {
  return { generatedAt: section.generated_at, sourceUpdatedAt: section.source_updated_at, stale: section.stale };
}

