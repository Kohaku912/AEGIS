import type { UiEvent, UiOverview } from "../types";

export function ActivityPage({ overview, recentEvents = [] }: { overview: UiOverview; recentEvents?: UiEvent[] }) {
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h2>Activity</h2>
          <div className="muted">Normalized recent signals from the overview service.</div>
        </div>
      </div>
      <div className="grid">
        {recentEvents.map((event) => (
          <div className="list-row" key={`${event.type}-${event.source_updated_at}-${event.message}`}>
            <div>
              <strong>{event.type}</strong>
              <div className="muted">{event.message || event.source_type}</div>
            </div>
            <span className="mono muted">{event.server_id || event.severity || "event"}</span>
          </div>
        ))}
        {recentEvents.length === 0 ? (overview.attention.data.items || []).map((item) => (
          <div className="list-row" key={item.id}>
            <div>
              <strong>{item.title}</strong>
              <div className="muted">{item.message}</div>
            </div>
            <span className="mono muted">{item.kind}</span>
          </div>
        )) : null}
      </div>
    </section>
  );
}
