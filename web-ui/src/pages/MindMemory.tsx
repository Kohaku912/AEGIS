import type { UiOverview } from "../types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Link2, Search, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchResourceEntities, forgetMemory, updateMemory } from "../api/client";
import type { EntitySummary } from "../types";
import { summarizeMemory } from "../displayModel";

export function MindMemory({ overview }: { overview: UiOverview }) {
  const summary = summarizeMemory(overview);
  const memory = overview.mind_summary.data.memory as Record<string, unknown> | undefined;
  const user = overview.user_state.data;
  const commitments = overview.commitments.data.items || [];
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<EntitySummary>();
  const [draft, setDraft] = useState("");
  const [action, setAction] = useState<"edit" | "forget" | "">("");
  const [status, setStatus] = useState("");
  const memories = useQuery({
    queryKey: ["ui-resource", "memories", search],
    queryFn: () => fetchResourceEntities("memories", search),
    staleTime: 5_000,
  });
  useEffect(() => {
    setDraft(String(selected?.data?.content || ""));
    setAction("");
  }, [selected]);

  const commitEdit = async () => {
    if (!selected) return;
    setStatus("Saving reviewed memory change...");
    try {
      await updateMemory(selected.id, { content: draft });
      setAction("");
      setStatus("Memory updated and event recorded.");
      await queryClient.invalidateQueries({ queryKey: ["ui-resource", "memories"] });
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Memory update failed");
    }
  };
  const commitForget = async () => {
    if (!selected) return;
    setStatus("Requesting privacy-safe removal...");
    try {
      await forgetMemory(selected.id);
      setSelected(undefined);
      setAction("");
      setStatus("Memory was removed by its owning store.");
      await queryClient.invalidateQueries({ queryKey: ["ui-resource", "memories"] });
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Memory removal failed");
    }
  };
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Mind & Memory</h2>
            <div className="muted">Operational summary, not raw internal state.</div>
          </div>
        </div>
        <div className="stat-grid">
          {Object.entries(summary).map(([label, value]) => (
            <div className="stat" key={label}>
              <span className="muted">{label}</span>
              <b className="stat__value">{value}</b>
            </div>
          ))}
        </div>
      </section>
      <div className="grid grid--three">
        <section className="panel">
          <div className="panel__header"><h2>Memory Stores</h2></div>
          <div className="metric-list">
            {["advanced", "episodic", "semantic", "procedural", "skill", "lesson", "workflow", "experiential"].map((key) => (
              <div className="metric-row" key={key}>
                <span>{key}</span>
                <strong>{describeMemoryStore((memory || {})[key])}</strong>
              </div>
            ))}
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>User Situation</h2></div>
          <div className="metric-list">
            <div className="metric-row"><span>Status</span><strong>{String(user.summary || user.status || "No data yet")}</strong></div>
            <div className="metric-row"><span>Available</span><strong>{String(user.available ?? "No data yet")}</strong></div>
            <div className="metric-row"><span>Updated</span><strong>{overview.user_state.stale ? "STALE" : "LIVE"}</strong></div>
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Commitments</h2></div>
          <div className="metric-list">
            <div className="metric-row"><span>Open commitments</span><strong>{commitments.length}</strong></div>
            <div className="metric-row"><span>Next commitment</span><strong>{String(commitments[0]?.title || commitments[0]?.summary || "No data yet")}</strong></div>
            <div className="metric-row"><span>Summary</span><strong>{overview.commitments.data.summary || "No data yet"}</strong></div>
          </div>
        </section>
      </div>
      <section className="panel memory-browser">
        <div className="panel__header">
          <div><h2>Memory Records</h2><div className="muted">Content and provenance from MemoryManager, separated from the command summary.</div></div>
          <span className="freshness" data-stale={memories.isError}>{memories.data?.total || 0} records</span>
        </div>
        <label className="memory-search"><Search size={15} /><input aria-label="Search memory records" value={search} onChange={(event) => setSearch(event.currentTarget.value)} placeholder="Search content, source, task, person, or capability" /></label>
        {status ? <div className="attention-item" data-severity={status.includes("failed") || status.includes("not_editable") ? "warning" : "info"}>{status}</div> : null}
        <div className="memory-browser__layout">
          <div className="memory-records">
            {memories.isLoading ? <p className="muted">Loading MemoryManager records...</p> : null}
            {(memories.data?.items || []).map((item) => (
              <button type="button" aria-current={selected?.id === item.id} onClick={() => setSelected(item)} key={item.id}>
                <span>{String(item.data?.memory_type || item.data?.type || "memory")}</span>
                <strong>{item.title}</strong>
                <small>{item.subtitle} / {item.status}</small>
              </button>
            ))}
            {!memories.isLoading && !(memories.data?.items || []).length ? <p className="muted">No memory matched this view.</p> : null}
          </div>
          <aside className="memory-detail">
            {selected ? (
              <>
                <header><span>{String(selected.data?.memory_type || selected.type)}</span><h3>{selected.title}</h3><p>{String(selected.data?.content || selected.subtitle)}</p></header>
                <dl>
                  <div><dt>Confidence</dt><dd>{String(selected.data?.confidence ?? "Not scored")}</dd></div>
                  <div><dt>Importance</dt><dd>{String(selected.data?.importance ?? "Not scored")}</dd></div>
                  <div><dt>Source</dt><dd>{String(selected.data?.source || selected.owner)}</dd></div>
                  <div><dt>Relations</dt><dd>{selected.relations.map((relation) => `${relation.type}:${relation.id}`).join(", ") || "None"}</dd></div>
                </dl>
                <div className="memory-actions">
                  <button className="secondary-button" type="button" onClick={() => setAction("edit")}><Archive size={14} />Edit</button>
                  <button className="danger-button" type="button" onClick={() => setAction("forget")}><ShieldAlert size={14} />Forget</button>
                  <button className="secondary-button" type="button" disabled><Link2 size={14} />Link</button>
                </div>
              </>
            ) : <p className="muted">Select a record to inspect content, provenance, relations, consolidation, and safe actions.</p>}
          </aside>
        </div>
        {selected && action ? (
          <section className="action-preview" aria-label="Memory action preview">
            <h3>{action === "edit" ? "Review memory edit" : "Review memory removal"}</h3>
            <dl>
              <div><dt>Target</dt><dd>{selected.id}</dd></div>
              <div><dt>Impact</dt><dd>{action === "edit" ? "Updates context used in future retrieval." : "Removes this record from its owning persistent store."}</dd></div>
              <div><dt>Risk</dt><dd>{action === "edit" ? "Controlled" : "Dangerous"}</dd></div>
              <div><dt>Rollback</dt><dd>{action === "edit" ? "Manual correction remains available." : "No automatic rollback after confirmed removal."}</dd></div>
              <div><dt>Verification</dt><dd>Re-query MemoryManager and confirm Event/Audit state.</dd></div>
            </dl>
            {action === "edit" ? <textarea aria-label="Memory content draft" value={draft} onChange={(event) => setDraft(event.currentTarget.value)} /> : null}
            <footer><button className="secondary-button" type="button" onClick={() => setAction("")}>Cancel</button><button className={action === "forget" ? "danger-button" : "primary-button"} type="button" onClick={() => void (action === "edit" ? commitEdit() : commitForget())}>Confirm {action}</button></footer>
          </section>
        ) : null}
      </section>
      <details className="developer-drawer developer-only">
        <summary>Developer raw state</summary>
        <pre className="mono muted">{JSON.stringify({ mind_summary: overview.mind_summary.data, user_state: overview.user_state.data, commitments: overview.commitments.data }, null, 2)}</pre>
      </details>
    </div>
  );
}

function describeMemoryStore(value: unknown): string {
  if (value === undefined || value === null) return "No data yet";
  if (typeof value === "number") return String(value);
  if (typeof value !== "object") return String(value);
  const record = value as Record<string, unknown>;
  const count = record.total || record.total_entries || record.total_episodes || record.entities || record.facts || record.active;
  if (count !== undefined) return String(count);
  const keys = Object.keys(record);
  return keys.length ? `${keys.length} fields` : "Empty";
}

