import { useMemo, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";

type ChainStage = {
  stage?: string;
  label?: string;
  summary?: string;
  status?: string;
  detail?: string;
};

type Operation = {
  operation_id?: string;
  kind?: string;
  kind_label?: string;
  title?: string;
  summary?: string;
  what_happened?: string;
  narrative?: string;
  status?: string;
  started_at?: number;
  updated_at?: number;
  tool_count?: number;
  error_count?: number;
  skip_reason?: string;
  decision?: string;
  steps?: Array<Record<string, unknown>>;
  causal_chain?: ChainStage[];
};

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
};

export function OperationsPage({ overview, developerMode = false }: Props) {
  const activity = overview.activity;
  const operations = (activity?.data.operations || []) as Operation[];
  const [selectedId, setSelectedId] = useState("");
  const selected = useMemo(
    () => operations.find((item) => item.operation_id === selectedId) || operations[0],
    [operations, selectedId],
  );

  return (
    <div className="judgment-page">
      <header className="judgment-page__hero">
        <div>
          <span>Operations</span>
          <h2>Causal chain of each AEGIS action</h2>
          <p>Trigger → Decision → Candidates → Goal → Execution → Result → Verification → Presentation → Follow-up → Learning</p>
        </div>
        <Freshness
          generatedAt={activity?.generated_at || 0}
          sourceUpdatedAt={activity?.source_updated_at || 0}
          stale={Boolean(activity?.stale)}
        />
      </header>

      <div className="judgment-split">
        <section className="panel">
          <div className="panel__header"><h2>Recent operations</h2></div>
          {operations.length === 0 ? (
            <p className="empty-copy">No operations yet. When AEGIS acts or deliberately skips, the chain appears here.</p>
          ) : (
            <ul className="operation-list">
              {operations.map((op) => (
                <li key={String(op.operation_id)}>
                  <button type="button" data-selected={selected?.operation_id === op.operation_id} onClick={() => setSelectedId(String(op.operation_id || ""))}>
                    <div>
                      <strong>{op.title || "Untitled"}</strong>
                      <p>{op.narrative || op.what_happened || op.summary || ""}</p>
                    </div>
                    <div className="operation-list__meta">
                      <StatusBadge status={String(op.status || op.kind || "ok")} />
                      <small>{op.updated_at ? new Date(op.updated_at).toLocaleString() : ""}</small>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <aside className="panel judgment-detail">
          {selected ? (
            <>
              <div className="panel__header">
                <h2>{selected.title}</h2>
                <StatusBadge status={String(selected.status || "ok")} />
              </div>
              <p className="human-summary">{selected.narrative || selected.what_happened || selected.summary}</p>
              <ol className="causal-chain">
                {(selected.causal_chain || []).map((stage) => (
                  <li key={String(stage.stage)} data-status={stage.status || "missing"}>
                    <strong>{stage.label || stage.stage}</strong>
                    <span>{stage.summary || "—"}</span>
                    {stage.detail ? <small>{stage.detail}</small> : null}
                  </li>
                ))}
              </ol>
              {developerMode ? (
                <pre className="developer-raw">{JSON.stringify({ steps: selected.steps, decision: selected.decision, skip_reason: selected.skip_reason }, null, 2)}</pre>
              ) : null}
            </>
          ) : (
            <p className="empty-copy">Select an operation to inspect its causal chain.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
