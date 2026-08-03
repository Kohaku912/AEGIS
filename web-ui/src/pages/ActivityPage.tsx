import { useMemo, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import { SeverityGlyph, type Severity } from "../components/viz/UxViz";
import type { UiEvent, UiOverview } from "../types";
import { text, time } from "./PageSupport";

const HIDDEN_BY_DEFAULT = /(heartbeat|telemetry|user_activity|foreground_app\.changed)/i;

type Props = {
  overview: UiOverview;
  recentEvents?: UiEvent[];
  developerMode?: boolean;
  detailId?: string;
  onNavigate?: (path: string) => void;
};

export function ActivityPage({
  overview,
  recentEvents = [],
  developerMode = false,
  detailId = "",
  onNavigate,
}: Props) {
  const [showNoise, setShowNoise] = useState(false);
  const [selectedId, setSelectedId] = useState(detailId);
  const history = (overview.activity?.data.recent || []) as Array<Record<string, unknown>>;
  const events = useMemo(() => {
    const merged: Array<Record<string, unknown>> = [
      ...recentEvents.map((item) => ({ ...item })),
      ...history,
    ];
    const byId = new Map<string, Record<string, unknown>>();
    for (const item of merged) {
      const id = String(item.event_id || item.id || `${item.type || item.event_type}-${item.generated_at || item.occurred_at}`);
      if (!byId.has(id)) byId.set(id, { ...item, event_id: id });
    }
    return [...byId.values()].sort(
      (a, b) => Number(b.occurred_at || b.generated_at || 0) - Number(a.occurred_at || a.generated_at || 0),
    );
  }, [history, recentEvents]);

  const visible = events.filter((item) => {
    if (showNoise || developerMode && showNoise) return true;
    const blob = `${item.type || ""} ${item.event_type || ""} ${item.safe_title || ""} ${item.safe_message || ""}`;
    return !HIDDEN_BY_DEFAULT.test(blob);
  });

  const selected = visible.find((item) => String(item.event_id) === selectedId) || visible[0];

  const select = (id: string) => {
    setSelectedId(id);
    onNavigate?.(`/dashboard/activity/${encodeURIComponent(id)}`);
  };

  return (
    <div className="grid activity-page">
      <PageHeader
        title="Raw Activity"
        description="開発者向けの低レベル Event Stream。通常の実行履歴（Operations）とは分離されています。"
      >
        <label className="developer-filter">
          <input
            type="checkbox"
            checked={showNoise}
            onChange={(event) => setShowNoise(event.currentTarget.checked)}
          />
          Developer Filter: heartbeat / telemetry
        </label>
      </PageHeader>

      <div className="judgment-split">
        <section className="panel">
          <div className="compact-list">
            {visible.map((item) => {
              const id = String(item.event_id);
              const title = text(item.safe_title || item.type || item.event_type, "event");
              return (
                <button
                  type="button"
                  className="list-row"
                  data-selected={selected?.event_id === id}
                  key={id}
                  onClick={() => select(id)}
                >
                  <SeverityGlyph severity={String(item.severity || "info").toLowerCase() as Severity} />
                  <div>
                    <strong>{title}</strong>
                    <p>{text(item.safe_message || item.message || item.summary)}</p>
                    <small>
                      {text(item.source_type || item.source || "manager")} · {time(item.occurred_at || item.generated_at)}
                      {item.operation_id ? ` · op ${String(item.operation_id).slice(0, 10)}` : ""}
                    </small>
                  </div>
                  <StatusBadge status={String(item.severity || "info")} />
                </button>
              );
            })}
            {!visible.length ? <p className="muted">表示可能なイベントはありません。</p> : null}
          </div>
        </section>

        <aside className="panel judgment-detail">
          {selected ? (
            <>
              <div className="panel__header">
                <h2>{text(selected.safe_title || selected.type || selected.event_type, "Event")}</h2>
                <StatusBadge status={String(selected.severity || "info")} />
              </div>
              <dl className="human-facts compact">
                <div><dt>Event Type</dt><dd>{text(selected.type || selected.event_type)}</dd></div>
                <div><dt>発行元</dt><dd>{text(selected.source_type || selected.source || "—")}</dd></div>
                <div><dt>Entity</dt><dd>{text(selected.entity_id || selected.affected_entity || "—")}</dd></div>
                <div><dt>変化</dt><dd>{text(selected.safe_message || selected.message || selected.summary)}</dd></div>
                <div><dt>Operation</dt><dd>{text(selected.operation_id || "—")}</dd></div>
                <div><dt>Task</dt><dd>{text(selected.task_id || "—")}</dd></div>
                <div><dt>Approval</dt><dd>{text(selected.approval_id || "—")}</dd></div>
                <div><dt>Capability</dt><dd>{text(selected.capability_id || "—")}</dd></div>
                <div><dt>Dedupe Key</dt><dd>{text(selected.dedupe_key || selected.correlation_id || "—")}</dd></div>
              </dl>
              {selected.operation_id ? (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => onNavigate?.(`/dashboard/operations/${encodeURIComponent(String(selected.operation_id))}`)}
                >
                  関連 Operation を開く
                </button>
              ) : null}
              {developerMode ? <pre className="developer-raw">{JSON.stringify(selected, null, 2)}</pre> : null}
            </>
          ) : (
            <p className="empty-copy">イベントを選択してください。</p>
          )}
        </aside>
      </div>
    </div>
  );
}
