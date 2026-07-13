import type { UiEvent, UiOverview } from "../types";

export function ActivityPage({ overview, recentEvents = [] }: { overview: UiOverview; recentEvents?: UiEvent[] }) {
  const persistedEvents = (overview.activity?.data.recent || []).map((event) => ({
    type: String(event.type || event.event_type || "activity.updated"),
    message: String(event.message || event.title || ""),
    source_type: String(event.event_type || event.type || "activity"),
    server_id: String(event.server_id || ""),
    severity: String(event.severity || ""),
    source_updated_at: Number(event.occurred_at || 0)
  }));
  const liveEvents = recentEvents.map((event) => ({
    type: event.type,
    message: event.message || event.safe_message || "",
    source_type: event.source_type,
    server_id: event.server_id || "",
    severity: event.severity || "",
    source_updated_at: event.source_updated_at
  }));
  const events = [...liveEvents, ...persistedEvents].slice(0, 80);
  const groups = overview.activity?.data.groups || [];

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Activity</h2>
            <div className="muted">Persisted EventManager history grouped into operational activity.</div>
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
                </div>
              </div>
              <span className="mono muted">{String(group.server_id || group.capability_id || group.task_id || "event")}</span>
              <details className="inline-drawer">
                <summary>Details</summary>
                <pre>{JSON.stringify(group, null, 2)}</pre>
              </details>
            </div>
          )) : <div className="muted">No persisted activity has been reported yet.</div>}
        </div>
      </section>
      <section className="panel">
        <div className="panel__header"><h2>Recent Events</h2></div>
        <div className="grid">
          {events.map((event) => (
            <div className="list-row list-row--with-drawer" key={`${event.type}-${event.source_updated_at}-${event.message}`}>
              <div>
                <strong>{event.type}</strong>
                <div className="muted">{event.message || event.source_type}</div>
              </div>
              <span className="mono muted">{event.server_id || event.severity || "event"}</span>
              <details className="inline-drawer">
                <summary>Trace</summary>
                <pre>{JSON.stringify(event, null, 2)}</pre>
              </details>
            </div>
          ))}
          {events.length === 0 ? (overview.attention.data.items || []).map((item) => (
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
    </div>
  );
}
