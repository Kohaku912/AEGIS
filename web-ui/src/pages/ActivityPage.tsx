import type { UiEvent, UiOverview } from "../types";

export function ActivityPage({ overview, recentEvents = [] }: { overview: UiOverview; recentEvents?: UiEvent[] }) {
  const persistedEvents = (overview.activity?.data.recent || []).map((event) => ({
    type: String(event.type || event.event_type || "activity.updated"),
    message: String((event.presentation_event as Record<string, unknown> | undefined)?.summary || event.message || event.title || ""),
    source_type: String(event.event_type || event.type || "activity"),
    server_id: String(event.server_id || ""),
    severity: String(event.severity || ""),
    source_updated_at: Number(event.occurred_at || 0),
    scene_type: String((event.presentation_event as Record<string, unknown> | undefined)?.scene_type || event.scene_type || "event"),
    recommended_surfaces: Array.isArray((event.presentation_event as Record<string, unknown> | undefined)?.recommended_surfaces)
      ? ((event.presentation_event as Record<string, unknown>).recommended_surfaces as string[])
      : []
  }));
  const liveEvents = recentEvents.map((event) => ({
    type: event.type,
    message: event.presentation_event?.summary || event.message || event.safe_message || "",
    source_type: event.source_type,
    server_id: event.server_id || "",
    severity: event.severity || "",
    source_updated_at: event.source_updated_at,
    scene_type: event.presentation_event?.scene_type || event.scene_type || "event",
    recommended_surfaces: event.presentation_event?.recommended_surfaces || event.recommended_surfaces || []
  }));
  const events = [...liveEvents, ...persistedEvents].slice(0, 80);
  const groups = overview.activity?.data.groups || [];
  const replay = (overview.presentation_events?.data.items || []).slice(0, 18);

  return (
    <div className="grid">
      <section className="panel operational-replay">
        <div className="panel__header">
          <div>
            <h2>Operational Replay</h2>
            <div className="muted">PresentationEvent timeline shared by Web, Display, mobile, overlay, room, and developer console.</div>
          </div>
          <span className="freshness" data-stale={overview.presentation_events?.stale || false}>{overview.presentation_events?.data.source || "presentation_surface_contract"}</span>
        </div>
        <div className="replay-river">
          {replay.length ? replay.map((item) => (
            <article className="replay-step" data-priority={item.priority} data-scene={item.scene_type} key={item.event_id}>
              <span className="replay-step__scene">{item.scene_type}</span>
              <strong>{item.title}</strong>
              <p>{item.summary || item.detail || "No summary reported."}</p>
              <div className="replay-step__meta">
                <span>{item.priority}</span>
                <span>{item.source}</span>
                <span>{item.recommended_surfaces.slice(0, 4).join(" / ") || "no surface"}</span>
              </div>
            </article>
          )) : <div className="muted">No replayable presentation events have been reported yet.</div>}
        </div>
      </section>
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
              <details className="inline-drawer developer-only">
                <summary>Developer trace</summary>
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
              <details className="inline-drawer developer-only">
                <summary>Developer trace</summary>
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
