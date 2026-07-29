import { useState } from "react";
import type { UiOverview } from "../types";

type OperationView = {
  id: string;
  kind: string;
  kindLabel: string;
  title: string;
  message: string;
  status: string;
  priority: string;
  updatedAt: number;
  toolCount: number;
  errorCount: number;
  steps: Array<Record<string, unknown>>;
  raw: Record<string, unknown>;
};

function stepLabel(step: Record<string, unknown>, index: number): string {
  const narrative = String(step.narrative || step.summary || "").trim();
  if (narrative) return narrative;
  const capability = String(step.capability_id || "").trim();
  if (capability) {
    const leaf = capability.split(".").pop() || capability;
    return `Ran ${leaf.replace(/_/g, " ")}`;
  }
  const action = String(step.action || "").trim();
  if (action) return action.replace(/_/g, " ");
  return `Step ${index + 1}`;
}

function stepMeta(step: Record<string, unknown>): string {
  const capability = String(step.capability_id || "").trim();
  const action = String(step.action || "").trim();
  const bits = [action && action !== capability ? action.replace(/_/g, " ") : "", capability].filter(Boolean);
  return bits.join(" · ");
}

export function ActivityPage({ overview }: { overview: UiOverview; recentEvents?: unknown[] }) {
  const operations: OperationView[] = (overview.activity?.data.operations || []).map((op, index) => ({
    id: String(op.operation_id || `operation-${index}`),
    kind: String(op.kind || "operation"),
    kindLabel: String(op.kind_label || op.kind || "Operation"),
    title: String(op.title || "Untitled operation"),
    message: String((op as Record<string, unknown>).narrative || op.what_happened || op.summary || ""),
    status: String(op.status || ""),
    priority: String(op.priority || (op.error_count ? "P1" : "P3")),
    updatedAt: Number(op.updated_at || op.started_at || 0),
    toolCount: Number(op.tool_count || 0),
    errorCount: Number(op.error_count || 0),
    steps: Array.isArray(op.steps) ? op.steps : [],
    raw: op as Record<string, unknown>,
  }));

  const groups = overview.activity?.data.groups || [];
  const [selectedId, setSelectedId] = useState("");
  const selected = operations.find((item) => item.id === selectedId) || operations[0];

  return (
    <div className="grid activity-page">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>AEGIS Operations</h2>
            <div className="muted">What AEGIS did, in plain language — not raw telemetry.</div>
          </div>
          <span className="freshness" data-stale={overview.activity?.stale || false}>{overview.activity?.data.source || "audit_manager"}</span>
        </div>
        <div className="work-layout">
          <div className="panel">
            <div className="panel__header"><h2>Recent Operations</h2></div>
            <div className="grid">
              {operations.map((op) => (
                <button
                  type="button"
                  className="list-row task-list-row"
                  data-selected={selected?.id === op.id}
                  key={op.id}
                  onClick={() => setSelectedId(op.id)}
                >
                  <div>
                    <strong>{op.kindLabel}: {op.title}</strong>
                    <div className="activity-narrative-preview">{op.message || "No summary yet."}</div>
                  </div>
                  <span className="mono muted">{op.status || op.priority}</span>
                </button>
              ))}
              {!operations.length ? <div className="muted">No AEGIS operations have been recorded yet.</div> : null}
            </div>
          </div>
          <div className="panel">
            <div className="panel__header"><h2>Operation Detail</h2></div>
            {selected ? (
              <div className="activity-detail">
                <p className="activity-narrative">{selected.message || "No natural-language summary was recorded for this operation."}</p>
                <div className="metric-list compact">
                  <div className="metric-row"><span>Kind</span><strong>{selected.kindLabel}</strong></div>
                  <div className="metric-row"><span>Status</span><strong>{selected.status || "unknown"}</strong></div>
                  <div className="metric-row"><span>When</span><strong>{selected.updatedAt ? new Date(selected.updatedAt).toLocaleString() : "No timestamp"}</strong></div>
                  <div className="metric-row"><span>Tools / errors</span><strong>{selected.toolCount} / {selected.errorCount}</strong></div>
                </div>
                <div className="operation-steps">
                  <h3>What happened, step by step</h3>
                  {selected.steps.length ? selected.steps.map((step, index) => (
                    <div className="list-row" key={`${selected.id}-step-${index}`}>
                      <div>
                        <strong>{stepLabel(step, index)}</strong>
                        {stepMeta(step) ? <div className="muted mono">{stepMeta(step)}</div> : null}
                      </div>
                      <span className="mono muted">{String(step.status || "")}</span>
                    </div>
                  )) : <p className="muted">No step details recorded for this operation.</p>}
                </div>
              </div>
            ) : <p className="muted">Select an operation to inspect what AEGIS did.</p>}
            <details className="inline-drawer developer-only">
              <summary>Developer trace</summary>
              <pre>{JSON.stringify(selected?.raw || {}, null, 2)}</pre>
            </details>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Event Groups</h2>
            <div className="muted">Secondary EventManager grouping (AEGIS actions only; status noise filtered).</div>
          </div>
          <span className="freshness" data-stale={overview.activity?.stale || false}>{overview.activity?.data.source || "event_manager"}</span>
        </div>
        <div className="grid">
          {groups.length ? groups.slice(0, 12).map((group) => (
            <div className="list-row list-row--with-drawer" key={String(group.group_id || group.title)}>
              <div>
                <strong>{String(group.title || group.group_id || "Activity")}</strong>
                <div className="activity-narrative-preview">
                  {String(group.summary || group.status || group.severity || "updated")}
                  {Number((group.events as unknown[])?.length || 0) ? ` · ${Number((group.events as unknown[])?.length || 0)} event(s)` : ""}
                </div>
              </div>
              <span className="mono muted">{String(group.capability_id || group.task_id || group.operation_type || "event")}</span>
            </div>
          )) : <div className="muted">No persisted activity groups yet.</div>}
        </div>
      </section>
    </div>
  );
}
