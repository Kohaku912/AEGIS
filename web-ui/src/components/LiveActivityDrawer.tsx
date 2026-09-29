import { Activity, ChevronDown, ChevronUp } from "lucide-react";
import { useMemo, useState } from "react";
import { isUiActivityNoise } from "../activityNoise";
import type { UiEvent } from "../types";

/**
 * Live Activity Log — Phase D2 で「詳細ログ drawer」に役割縮小.
 *
 * 画面下部の Live Overlay (sticky 38px) は「最重要 1 イベント」を
 * 常時表示し、この Drawer は展開時に最近の 12 イベント詳細ログを
 * 提供する (instruction.md §3, §4).
 */
export function LiveActivityDrawer({ events }: { events: UiEvent[] }) {
  const [open, setOpen] = useState(false);
  const visible = useMemo(() => events.filter((event) => !isUiActivityNoise(event)).slice(0, 12), [events]);
  return (
    <aside className="live-activity" data-open={open} aria-label="Live activity log">
      <button className="live-activity__handle" type="button" onClick={() => setOpen((value) => !value)}>
        <Activity size={15} /><strong>Live Activity Log</strong><span>{visible.length} signals</span>{open ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
      </button>
      {open ? (
        <div className="live-activity__stream">
          {visible.map((event) => (
            <article key={event.event_id || `${event.type}-${event.source_updated_at}`} data-severity={event.severity || "info"}>
              <time>{new Date(event.occurred_at || event.generated_at).toLocaleTimeString()}</time>
              <strong>{event.safe_title || event.type}</strong>
              <span>{event.safe_message || event.message || event.status || "State updated"}</span>
            </article>
          ))}
          {!visible.length ? <p>Waiting for live AEGIS operations.</p> : null}
        </div>
      ) : null}
    </aside>
  );
}
