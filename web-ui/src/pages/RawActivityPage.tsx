import { useEffect, useMemo, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph, type Severity } from "../components/viz/UxViz";
import { detailIdFromPath } from "../navigation";
import type { UiEvent, UiOverview } from "../types";
import { text, time } from "./PageSupport";

type Props = {
  overview: UiOverview;
  recentEvents?: UiEvent[];
  developerMode?: boolean;
  pathname?: string;
  onNavigate?: (path: string) => void;
};

const HIDDEN_UNLESS_DEV = new Set([
  "server.heartbeat",
  "android.heartbeat",
  "device.telemetry",
  "health.updated",
  "pc.user_activity.snapshot",
]);

export function RawActivityPage({ overview, recentEvents = [], developerMode = false, pathname = "", onNavigate }: Props) {
  const activity = overview.activity?.data.recent || [];
  const routeId = detailIdFromPath(pathname || window.location.pathname, "/dashboard/activity");
  const [selectedId, setSelectedId] = useState(routeId);
  useEffect(() => {
    if (routeId) setSelectedId(routeId);
  }, [routeId]);

  const select = (id: string) => {
    setSelectedId(id);
    onNavigate?.(`/dashboard/activity/${encodeURIComponent(id)}`);
  };

  const items = useMemo(() => {
    const merged = [...recentEvents, ...(activity as unknown as UiEvent[])];
    return merged.filter((item) => {
      const type = String(item.event_type || item.type || "").toLowerCase();
      if (!developerMode && (HIDDEN_UNLESS_DEV.has(type) || type.includes("heartbeat") || type.includes("telemetry"))) {
        return false;
      }
      return true;
    });
  }, [activity, recentEvents, developerMode]);

  const selected = items.find((item) => String(item.event_id || item.sequence) === selectedId) || items[0];

  return (
    <div className="grid judgment-split">
      <div>
        <PageHeader title="Raw Activity" description="開発者向けの低レベル Event Stream です。通常の実行履歴とは分離されています。" />
        <section className="panel">
          <div className="compact-list">
            {items.map((item, index) => {
              const id = String(item.event_id || item.sequence || index);
              return (
                <button type="button" className="list-row" key={id} data-selected={String(selected?.event_id || selected?.sequence) === id} onClick={() => select(id)}>
                  <SeverityGlyph severity={String(item.severity || item.priority || "info").toLowerCase() as Severity} />
                  <div>
                    <strong>{text(item.safe_title || item.type || item.event_type, "イベント")}</strong>
                    <p>{text(item.safe_message || item.message || item.payload)}</p>
                    <small>{text(item.source_type)} · {time(item.occurred_at || item.generated_at)}</small>
                  </div>
                </button>
              );
            })}
            {!items.length ? <p className="muted">表示可能なイベントはありません。</p> : null}
          </div>
        </section>
      </div>
      <aside className="panel judgment-detail">
        {selected ? (
          <>
            <div className="panel__header">
              <h2>{text(selected.safe_title || selected.event_type || selected.type, "Event")}</h2>
            </div>
            <p>{text(selected.safe_message || selected.message)}</p>
            <dl className="operation-facts">
              <div><dt>Event Type</dt><dd>{text(selected.event_type || selected.type)}</dd></div>
              <div><dt>発行元</dt><dd>{text(selected.source_type || (selected as { source?: string }).source)}</dd></div>
              <div><dt>Severity</dt><dd>{text(selected.severity || selected.priority, "info")}</dd></div>
              <div><dt>時刻</dt><dd>{time(selected.occurred_at || selected.generated_at)}</dd></div>
            </dl>
            {developerMode ? <pre className="developer-raw">{JSON.stringify(selected, null, 2)}</pre> : null}
          </>
        ) : (
          <p className="empty-copy">イベントを選択してください。</p>
        )}
      </aside>
    </div>
  );
}
