import { useMemo, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";

type OpenLoop = {
  id?: string;
  kind?: string;
  title?: string;
  owner?: string;
  next_action?: string;
  waiting_reason?: string;
  due_at?: number;
  success_condition?: string;
  status?: string;
  confidence?: number;
  evidence_summary?: string;
  evidence?: Record<string, unknown>;
};

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
};

export function OpenLoopsPage({ overview, developerMode = false }: Props) {
  const section = overview.open_loops;
  const items = (section?.data.items || []) as OpenLoop[];
  const byKind = section?.data.by_kind || {};
  const [kind, setKind] = useState("");
  const [selectedId, setSelectedId] = useState("");

  const filtered = useMemo(
    () => items.filter((item) => !kind || item.kind === kind),
    [items, kind],
  );
  const selected = filtered.find((item) => item.id === selectedId) || filtered[0];

  return (
    <div className="judgment-page">
      <header className="judgment-page__hero">
        <div>
          <span>Open Loops</span>
          <h2>Unresolved work AEGIS still owns</h2>
          <p>{section?.data.summary || "Tasks, commitments, approvals, social obligations, and incidents in one list."}</p>
        </div>
        <Freshness
          generatedAt={section?.generated_at || 0}
          sourceUpdatedAt={section?.source_updated_at || 0}
          stale={Boolean(section?.stale)}
        />
      </header>

      <section className="judgment-chips" aria-label="Loop kinds">
        <button type="button" data-active={!kind} onClick={() => setKind("")}>All ({items.length})</button>
        {Object.entries(byKind).map(([key, count]) => (
          <button key={key} type="button" data-active={kind === key} onClick={() => setKind(key)}>
            {key} ({count})
          </button>
        ))}
      </section>

      <div className="judgment-split">
        <section className="panel">
          <div className="panel__header"><h2>Loops</h2></div>
          <div className="loop-table" role="table">
            <div className="loop-table__head" role="row">
              <span>Kind</span><span>Title</span><span>Owner</span><span>Next</span><span>Waiting</span><span>Due</span>
            </div>
            {filtered.length === 0 ? (
              <p className="empty-copy">No open loops. AEGIS has nothing waiting on user or system follow-through.</p>
            ) : (
              filtered.map((item) => (
                <button
                  key={String(item.id)}
                  type="button"
                  className="loop-table__row"
                  data-selected={selected?.id === item.id}
                  onClick={() => setSelectedId(String(item.id || ""))}
                >
                  <StatusBadge status={String(item.kind || "loop")} />
                  <strong>{item.title}</strong>
                  <span>{item.owner || "—"}</span>
                  <span>{item.next_action || "—"}</span>
                  <span>{item.waiting_reason || "—"}</span>
                  <span>{item.due_at ? new Date(item.due_at).toLocaleString() : "—"}</span>
                </button>
              ))
            )}
          </div>
        </section>

        <aside className="panel judgment-detail">
          {selected ? (
            <>
              <div className="panel__header">
                <h2>{selected.title}</h2>
                <StatusBadge status={String(selected.status || selected.kind || "open")} />
              </div>
              <dl className="human-facts">
                <div><dt>Owner</dt><dd>{selected.owner || "—"}</dd></div>
                <div><dt>Next action</dt><dd>{selected.next_action || "—"}</dd></div>
                <div><dt>Waiting reason</dt><dd>{selected.waiting_reason || "None"}</dd></div>
                <div><dt>Success condition</dt><dd>{selected.success_condition || "—"}</dd></div>
                <div><dt>Confidence</dt><dd>{selected.confidence != null ? `${Math.round(Number(selected.confidence) * 100)}%` : "—"}</dd></div>
                {selected.evidence_summary ? (
                  <div><dt>Evidence</dt><dd>{selected.evidence_summary}</dd></div>
                ) : null}
              </dl>
              {developerMode && selected.evidence ? (
                <pre className="developer-raw">{JSON.stringify(selected.evidence, null, 2)}</pre>
              ) : null}
            </>
          ) : (
            <p className="empty-copy">Select a loop to see ownership, waiting reason, and success condition.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
