import { ApprovalCard } from "../components/ApprovalCard";
import { useEffect, useMemo, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { Freshness } from "../components/Freshness";
import type { ApprovalItem, EntitySummary, UiOverview } from "../types";
import { approvalBuckets, serverFromCapabilityId, serverLabel } from "../displayModel";

export function Approvals({ overview }: { overview: UiOverview }) {
  const [history, setHistory] = useState<ApprovalItem[]>([]);
  const [activeBucket, setActiveBucket] = useState("pending");
  const [selectedId, setSelectedId] = useState("");
  const [historyError, setHistoryError] = useState("");
  useEffect(() => {
    let active = true;
    fetchResourceEntities("approvals").then((page) => { if (active) setHistory(page.items.map(approvalFromEntity)); }).catch((error) => { if (active) setHistoryError(String(error)); });
    return () => { active = false; };
  }, []);
  const approvals = history.length ? history : overview.approvals.data.pending || [];
  const buckets = approvalBuckets(approvals);
  const visible = buckets.find((bucket) => bucket.id === activeBucket)?.items || approvals;
  const selected = useMemo(() => visible.find((item) => item.approval_id === selectedId) || visible[0], [selectedId, visible]);
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
            <button className="tab-chip" type="button" key={bucket.id} aria-selected={bucket.id === activeBucket} onClick={() => { setActiveBucket(bucket.id); setSelectedId(""); }}>
              <span>{bucket.label}</span>
              <strong>{bucket.items.length}</strong>
            </button>
          ))}
        </div>
      </section>
      {historyError ? <div className="attention-item" data-severity="warning">Approval history is unavailable; showing the pending Overview snapshot.</div> : null}
      <section className="approval-layout">
        <aside className="panel">
          <div className="panel__header"><h2>Queue</h2></div>
          <div className="grid">
            {visible.map((approval) => (
              <button type="button" className="list-row approval-queue-row" data-selected={approval.approval_id === selected?.approval_id} key={approval.approval_id} onClick={() => setSelectedId(approval.approval_id)}>
                <div>
                  <strong>{approval.summary || approval.capability_id}</strong>
                  <div className="muted mono">{approval.approval_id}</div>
                </div>
                <span className="status-badge" data-status={String(approval.status || "pending").toUpperCase()}>{approval.status || approval.risk || "pending"}</span>
              </button>
            ))}
            {!visible.length ? <div className="attention-item" data-severity="normal">No approvals in this lifecycle state.</div> : null}
          </div>
        </aside>
        <main>
          {selected ? <ApprovalCard approval={selected} readonly={String(selected.status || "pending").toLowerCase() !== "pending"} /> : <section className="panel"><div className="attention-item" data-severity="normal">No approval is selected.</div></section>}
        </main>
        <aside className="panel">
          <div className="panel__header"><h2>Context</h2></div>
          {selected ? (
            <div className="metric-list">
              <div className="metric-row"><span>Related task</span><strong className="mono">{selected.task_id || overview.current_task.data.task_id || "No data yet"}</strong></div>
              <div className="metric-row"><span>Target server</span><strong>{serverLabel(serverFromCapabilityId(selected.capability_id))}</strong></div>
              <div className="metric-row"><span>Risk rationale</span><strong>{selected.reason || "No data yet"}</strong></div>
              <div className="metric-row"><span>Side effects</span><strong>{formatContextValue(selected.side_effects)}</strong></div>
              <div className="metric-row"><span>Previous action</span><strong>{String(selected.previous_action || relatedEvents[0]?.message || relatedEvents[0]?.title || "No data yet")}</strong></div>
              <div className="metric-row"><span>Similar past action</span><strong>{String(selected.similar_action_summary || relatedEvents[1]?.message || "No data yet")}</strong></div>
              <div className="metric-row"><span>Fresh auth</span><strong>{selected.fresh_auth_required ? "Required" : "Not required"}</strong></div>
              <div className="metric-row"><span>Post-approval effect</span><strong>{String(selected.expected_effect || "No data yet")}</strong></div>
              <div className="metric-row"><span>Audit</span><strong>{selected.request_id || selected.step_id || "No data yet"}</strong></div>
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

function approvalFromEntity(entity: EntitySummary): ApprovalItem {
  const data = entity.data || {};
  return {
    approval_id: String(data.approval_id || entity.id),
    request_id: String(data.request_id || ""),
    task_id: String(data.task_id || ""),
    step_id: String(data.step_id || ""),
    capability_id: String(data.capability_id || ""),
    tool_name: String(data.tool_name || ""),
    risk: String(data.risk_level || data.risk || ""),
    reason: String(data.approval_reason || data.reason || ""),
    summary: String(data.user_facing_summary || data.summary || entity.title),
    target: String(data.target || data.arguments_summary || ""),
    preview: String(data.preview || data.arguments_summary || ""),
    side_effects: String(data.possible_side_effects || data.side_effects || ""),
    expected_effect: String(data.expected_outcome || data.expected_effect || ""),
    fresh_auth_required: Boolean(data.fresh_auth_required),
    created_at: Number(data.created_at || 0),
    expires_at: Number(data.expires_at || 0),
    status: String(data.status || entity.status || "pending"),
  };
}

function formatContextValue(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "None reported";
  return String(value || "No data yet");
}

