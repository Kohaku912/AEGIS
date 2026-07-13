import type { UiOverview } from "../types";
import { taskBuckets, serverFromCapabilityId, serverLabel } from "../displayModel";

export function Work({ overview }: { overview: UiOverview }) {
  const task = overview.current_task.data;
  const buckets = taskBuckets(overview);
  const steps = task.steps || [];
  const activeCapability = task.capability_id || String(steps.find((step) => String(step.status || "").toLowerCase() === "running")?.capability_id || "");
  const pendingApprovals = (overview.approvals.data.pending || []).filter((approval) => approval.task_id === task.task_id || approval.capability_id === activeCapability);
  const usedMemory = overview.memory?.data?.summary || overview.mind_summary.data?.memory || {};
  const usage = overview.usage.data || {};
  const recentResult = [...steps].reverse().map((step) => resultPreview(step)).find(Boolean);
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Work</h2>
            <div className="muted">Tasks grouped by operational state. Active task detail is shown on the right.</div>
          </div>
        </div>
        <div className="tab-strip" role="tablist" aria-label="Work queues">
          {buckets.map((bucket) => (
            <button className="tab-chip" key={bucket.id} type="button" aria-selected={bucket.id === "active"}>
              <span>{bucket.label}</span>
              <strong>{bucket.count}</strong>
            </button>
          ))}
        </div>
      </section>
      <section className="work-layout">
        <div className="panel">
          <div className="panel__header"><h2>Task List</h2></div>
          <div className="grid">
            {task.task_id || task.title ? (
              <article className="list-row" data-selected="true">
                <div>
                  <strong>{task.title || "Untitled task"}</strong>
                  <div className="muted">{task.phase || "unknown"} / {steps.length} step(s)</div>
                </div>
                <span className="status-badge" data-status={String(task.phase || "ACTIVE").toUpperCase()}>{task.phase || "active"}</span>
              </article>
            ) : (
              <div className="attention-item" data-severity="normal">No active task. Scheduled and historical queues will appear here when reported by Overview v3.</div>
            )}
          </div>
        </div>
        <div className="panel">
          <div className="panel__header">
            <div>
              <h2>Task Detail</h2>
              <div className="muted mono">{task.task_id || "No task id"}</div>
            </div>
          </div>
          <div className="stat-grid">
            <div className="stat"><span className="muted">Objective</span><b style={{ fontSize: 16 }}>{task.title || "Not reported"}</b></div>
            <div className="stat"><span className="muted">Phase</span><b>{task.phase || "Not reported"}</b></div>
            <div className="stat"><span className="muted">Current capability</span><b className="mono" style={{ fontSize: 14 }}>{activeCapability || "Not reported"}</b></div>
            <div className="stat"><span className="muted">Execution server</span><b>{activeCapability ? serverLabel(serverFromCapabilityId(activeCapability)) : "Not reported"}</b></div>
          </div>
          <div className="task-narrative">
            <div><span className="muted">Original instruction</span><strong>{String(task.title || task.task_id || "Not reported")}</strong></div>
            <div><span className="muted">Current action</span><strong>{task.current_action || "Not reported"}</strong></div>
            <div><span className="muted">Next action</span><strong>{task.next_action || "Not reported"}</strong></div>
            <div><span className="muted">Blocked reason</span><strong>{task.blocked_reason || "Not blocked"}</strong></div>
            <div><span className="muted">Latest result</span><strong>{recentResult || "Not reported"}</strong></div>
          </div>
          <div className="work-insight-grid" aria-label="Task operational context">
            <div className="mini-panel">
              <h3>Plan / Dependency</h3>
              <p className="muted">{steps.length ? `${steps.length} step plan, executed through ${activeCapability ? serverLabel(serverFromCapabilityId(activeCapability)) : "reported server"}.` : "No step plan reported."}</p>
            </div>
            <div className="mini-panel">
              <h3>Approvals</h3>
              <p className="muted">{pendingApprovals.length ? `${pendingApprovals.length} approval waiting for this task.` : "No approval currently blocks this task."}</p>
            </div>
            <div className="mini-panel">
              <h3>Memories Used</h3>
              <p className="muted">{memoryPreview(usedMemory)}</p>
            </div>
            <div className="mini-panel">
              <h3>Model / Cost</h3>
              <p className="muted">{String(usage.summary || usage.total_tokens || usage.cost || "Not reported")}</p>
            </div>
            <div className="mini-panel">
              <h3>Completion / Verification</h3>
              <p className="muted">{verificationPreview(steps) || "No verification result reported."}</p>
            </div>
            <div className="mini-panel">
              <h3>Final Output</h3>
              <p className="muted">{String((task as Record<string, unknown>).final_output || (task as Record<string, unknown>).result || "Not reported")}</p>
            </div>
          </div>
          <div className="step-list">
            {steps.map((step, index) => (
              <article className="step-row" key={String(step.step_id || index)}>
                <span className="step-index">{index + 1}</span>
                <div>
                  <strong>{String(step.description || step.capability_id || step.name || `Step ${index + 1}`)}</strong>
                  <div className="muted mono">{String(step.capability_id || step.name || "No capability reported")}</div>
                </div>
                <span className="status-badge" data-status={String(step.status || "UNKNOWN").toUpperCase()}>{String(step.status || "unknown")}</span>
              </article>
            ))}
            {!steps.length ? <div className="attention-item" data-severity="normal">No step history reported.</div> : null}
          </div>
        </div>
      </section>
    </div>
  );
}

function resultPreview(step: Record<string, unknown>): string {
  const result = step.result;
  if (!result) return "";
  if (typeof result === "string") return result.slice(0, 160);
  if (typeof result === "object") {
    const record = result as Record<string, unknown>;
    return String(record.summary || record.status || record.message || JSON.stringify(record).slice(0, 160));
  }
  return String(result);
}

function verificationPreview(steps: Array<Record<string, unknown>>): string {
  const verification = [...steps].reverse().map((step) => step.verification || step.completion || step.postcondition).find(Boolean);
  if (!verification) return "";
  if (typeof verification === "string") return verification;
  if (typeof verification === "object") {
    const record = verification as Record<string, unknown>;
    return String(record.status || record.summary || record.message || JSON.stringify(record).slice(0, 140));
  }
  return String(verification);
}

function memoryPreview(value: unknown): string {
  if (!value || typeof value !== "object") return "Not reported";
  const record = value as Record<string, unknown>;
  const parts = ["episodic", "semantic", "procedural", "advanced"]
    .map((key) => {
      const item = record[key];
      if (typeof item === "number" || typeof item === "string") return `${key}: ${item}`;
      if (item && typeof item === "object") {
        const itemRecord = item as Record<string, unknown>;
        return `${key}: ${itemRecord.total || itemRecord.count || itemRecord.total_entries || itemRecord.total_episodes || "reported"}`;
      }
      return "";
    })
    .filter(Boolean);
  return parts.length ? parts.join(", ") : "Not reported";
}
