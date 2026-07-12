import type { UiOverview } from "../types";

export function ActivityPage({ overview }: { overview: UiOverview }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h2>Activity</h2>
          <div className="muted">Normalized recent signals from the overview service.</div>
        </div>
      </div>
      <div className="grid">
        {(overview.attention.data.items || []).map((item) => (
          <div className="list-row" key={item.id}>
            <div>
              <strong>{item.title}</strong>
              <div className="muted">{item.message}</div>
            </div>
            <span className="mono muted">{item.kind}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
