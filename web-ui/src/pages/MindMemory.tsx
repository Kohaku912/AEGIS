import type { UiOverview } from "../types";

export function MindMemory({ overview }: { overview: UiOverview }) {
  return (
    <div className="grid grid--three">
      <section className="panel">
        <div className="panel__header"><h2>Mind Summary</h2></div>
        <pre className="mono muted" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(overview.mind_summary.data, null, 2)}</pre>
      </section>
      <section className="panel">
        <div className="panel__header"><h2>User State</h2></div>
        <pre className="mono muted" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(overview.user_state.data, null, 2)}</pre>
      </section>
      <section className="panel">
        <div className="panel__header"><h2>Commitments</h2></div>
        <pre className="mono muted" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(overview.commitments.data, null, 2)}</pre>
      </section>
    </div>
  );
}
