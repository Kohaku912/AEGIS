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

export function ActivityPage({ overview }: { overview: UiOverview; recentEvents?: unknown[] }) {
  const operations: OperationView[] = (overview.activity?.data.operations || []).map((op, index) => ({
    id: String(op.operation_id || `operation-${index}`),
    kind: String(op.kind || "operation"),
    kindLabel: String(op.kind_label || op.kind || "Operation"),
    title: String(op.title || "Untitled operation"),
    message: String(op.what_happened || op.summary || ""),
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
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>AEGIS Operations</h2>
            <div className="muted">One user instruction or autonomous run per entry — what AEGIS did, not device telemetry.</div>
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
                    <div className="muted">{op.message || "No summary yet."}</div>
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
              <div className="metric-list">
                <div className="metric-row"><span>Kind</span><strong>{selected.kindLabel}</strong></div>
                <div className="metric-row"><span>Status</span><strong>{selected.status || "unknown"}</strong></div>
                <div className="metric-row"><span>Priority</span><strong>{selected.priority}</strong></div>
                <div className="metric-row"><span>Tools</span><strong>{selected.toolCount}</strong></div>
                <div className="metric-row"><span>Errors</span><strong>{selected.errorCount}</strong></div>
                <div className="metric-row"><span>When</span><strong>{selected.updatedAt ? new Date(selected.updatedAt).toLocaleString() : "No timestamp"}</strong></div>
                <div className="metric-row"><span>What happened</span><strong>{selected.message || "No summary"}</strong></div>
                <div className="operation-steps">
                  <h3>Steps</h3>
                  {selected.steps.length ? selected.steps.map((step, index) => (
                    <div className="list-row" key={`${selected.id}-step-${index}`}>
                      <div>
                        <strong>{String(step.capability_id || step.action || `Step ${index + 1}`)}</strong>
                        <div className="muted">{String(step.summary || step.decision || "")}</div>
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
                <div className="muted">
                  {String(group.status || group.severity || "updated")} / {Number((group.events as unknown[])?.length || 0)} event(s)
                  {group.summary ? ` · ${String(group.summary)}` : ""}
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
