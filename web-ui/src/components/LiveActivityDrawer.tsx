import { Activity, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import type { UiEvent } from "../types";

export function LiveActivityDrawer({ events }: { events: UiEvent[] }) {
  const [open, setOpen] = useState(false);
  return (
    <aside className="live-activity" data-open={open} aria-label="Live activity">
      <button className="live-activity__handle" type="button" onClick={() => setOpen((value) => !value)}>
        <Activity size={15} /><strong>Live Activity</strong><span>{events.length} signals</span>{open ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
      </button>
      {open ? <div className="live-activity__stream">{events.slice(0, 12).map((event) => <article key={event.event_id || `${event.type}-${event.source_updated_at}`} data-severity={event.severity || "info"}><time>{new Date(event.occurred_at || event.generated_at).toLocaleTimeString()}</time><strong>{event.safe_title || event.type}</strong><span>{event.safe_message || event.message || event.status || "State updated"}</span></article>)}{!events.length ? <p>Waiting for live manager events.</p> : null}</div> : null}
    </aside>
  );
}
