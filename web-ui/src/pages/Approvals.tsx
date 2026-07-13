import { ApprovalCard } from "../components/ApprovalCard";
import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";
import { approvalBuckets, serverFromCapabilityId, serverLabel } from "../displayModel";

export function Approvals({ overview }: { overview: UiOverview }) {
  const approvals = overview.approvals.data.pending || [];
  const selected = approvals[0];
  const buckets = approvalBuckets(approvals);
  const relatedEvents = (overview.activity?.data.recent || []).filter((event) =>
    selected
      ? String(event.approval_id || event.task_id || event.capability_id || "").includes(selected.approval_id) ||
        String(event.task_id || "") === selected.task_id ||
        String(event.capability_id || "") === selected.capability_id
      : false
  );
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Approvals</h2>
            <div className="muted">Every approval is shown with risk, target, reason, preview, and task context.</div>
          </div>
          <Freshness generatedAt={overview.approvals.generated_at} sourceUpdatedAt={overview.approvals.source_updated_at} stale={overview.approvals.stale} />
        </div>
        <div className="tab-strip" role="tablist" aria-label="Approval filters">
          {buckets.map((bucket) => (
            <button className="tab-chip" type="button" key={bucket.id} aria-selected={bucket.id === "pending"}>
              <span>{bucket.label}</span>
              <strong>{bucket.items.length}</strong>
            </button>
          ))}
        </div>
      </section>
      <section className="approval-layout">
        <aside className="panel">
          <div className="panel__header"><h2>Queue</h2></div>
          <div className="grid">
            {approvals.map((approval) => (
              <article className="list-row" data-selected={approval.approval_id === selected?.approval_id} key={approval.approval_id}>
                <div>
                  <strong>{approval.summary || approval.capability_id}</strong>
                  <div className="muted mono">{approval.approval_id}</div>
                </div>
                <span className="status-badge" data-status="WAITING">{approval.risk || "risk"}</span>
              </article>
            ))}
            {!approvals.length ? <div className="attention-item" data-severity="normal">No pending approvals.</div> : null}
          </div>
        </aside>
        <main>
          {selected ? <ApprovalCard approval={selected} /> : <section className="panel"><div className="attention-item" data-severity="normal">No action is waiting for approval.</div></section>}
        </main>
        <aside className="panel">
          <div className="panel__header"><h2>Context</h2></div>
          {selected ? (
            <div className="metric-list">
              <div className="metric-row"><span>Related task</span><strong className="mono">{selected.task_id || overview.current_task.data.task_id || "Not reported"}</strong></div>
              <div className="metric-row"><span>Target server</span><strong>{serverLabel(serverFromCapabilityId(selected.capability_id))}</strong></div>
              <div className="metric-row"><span>Risk rationale</span><strong>{selected.reason || "Not reported"}</strong></div>
              <div className="metric-row"><span>Side effects</span><strong>{formatContextValue(selected.side_effects)}</strong></div>
              <div className="metric-row"><span>Previous action</span><strong>{String(selected.previous_action || relatedEvents[0]?.message || relatedEvents[0]?.title || "Not reported")}</strong></div>
              <div className="metric-row"><span>Similar past action</span><strong>{String(selected.similar_action_summary || relatedEvents[1]?.message || "Not reported")}</strong></div>
              <div className="metric-row"><span>Fresh auth</span><strong>{selected.fresh_auth_required ? "Required" : "Not required"}</strong></div>
              <div className="metric-row"><span>Post-approval effect</span><strong>{String(selected.expected_effect || "Not reported")}</strong></div>
              <div className="metric-row"><span>Audit</span><strong>{selected.request_id || selected.step_id || "Not reported"}</strong></div>
              <div className="approval-safety-note">Bulk approval is not available. Each high-risk action must be reviewed independently with fresh authentication when required.</div>
            </div>
          ) : (
            <p className="muted">Approval context appears here when an action is pending.</p>
          )}
        </aside>
      </section>
    </div>
  );
}

function formatContextValue(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "None reported";
  return String(value || "Not reported");
}
