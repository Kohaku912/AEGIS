import type { UiOverview } from "../types";
import { summarizeMemory } from "../displayModel";

export function MindMemory({ overview }: { overview: UiOverview }) {
  const summary = summarizeMemory(overview);
  const memory = overview.mind_summary.data.memory as Record<string, unknown> | undefined;
  const user = overview.user_state.data;
  const commitments = overview.commitments.data.items || [];
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
              <b style={{ fontSize: 16 }}>{value}</b>
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
            <div className="metric-row"><span>Status</span><strong>{String(user.summary || user.status || "Not reported")}</strong></div>
            <div className="metric-row"><span>Available</span><strong>{String(user.available ?? "Not reported")}</strong></div>
            <div className="metric-row"><span>Updated</span><strong>{overview.user_state.stale ? "STALE" : "LIVE"}</strong></div>
          </div>
        </section>
        <section className="panel">
          <div className="panel__header"><h2>Commitments</h2></div>
          <div className="metric-list">
            <div className="metric-row"><span>Open commitments</span><strong>{commitments.length}</strong></div>
            <div className="metric-row"><span>Next commitment</span><strong>{String(commitments[0]?.title || commitments[0]?.summary || "Not reported")}</strong></div>
            <div className="metric-row"><span>Summary</span><strong>{overview.commitments.data.summary || "Not reported"}</strong></div>
          </div>
        </section>
      </div>
      <details className="developer-drawer">
        <summary>Developer raw state</summary>
        <pre className="mono muted">{JSON.stringify({ mind_summary: overview.mind_summary.data, user_state: overview.user_state.data, commitments: overview.commitments.data }, null, 2)}</pre>
      </details>
    </div>
  );
}

function describeMemoryStore(value: unknown): string {
  if (value === undefined || value === null) return "Not reported";
  if (typeof value === "number") return String(value);
  if (typeof value !== "object") return String(value);
  const record = value as Record<string, unknown>;
  const count = record.total || record.total_entries || record.total_episodes || record.entities || record.facts || record.active;
  if (count !== undefined) return String(count);
  const keys = Object.keys(record);
  return keys.length ? `${keys.length} fields` : "Empty";
}
