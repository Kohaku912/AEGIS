import { useEffect, useMemo, useState } from "react";
import { buildAttentionItems } from "../attentionModel";
import { PageHeader } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import { SeverityGlyph } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { text, time } from "./PageSupport";

type Props = {
  overview: UiOverview;
  detailId?: string;
  pathname?: string;
  developerMode?: boolean;
  onNavigate?: (path: string) => void;
};

export function IncidentsPage({ overview, detailId = "", pathname = "", developerMode = false, onNavigate }: Props) {
  const failures = (() => {
    try {
      return buildAttentionItems(overview).filter((item) => item.kind === "failure");
    } catch {
      return [];
    }
  })();
  const errors = overview.errors?.data.items || [];
  const repairs = (overview.repairs?.data.items || []) as Array<Record<string, unknown>>;
  const combined = useMemo(() => {
    const items: Array<Record<string, unknown>> = [
      ...repairs.map((item) => ({
        ...item,
        id: String(item.repair_id || item.id || ""),
        title: String(item.title || item.category || item.error || "障害"),
        message: String(item.message || item.summary || item.error || ""),
        status: String(item.status || item.state || "open"),
        created_at: Number(item.created_at || item.started_at || item.last_seen_at || 0),
        attempt_count: Number(item.attempt_count || item.retry_count || 0),
        next_action: String(item.next_action || item.recommended_action || item.lesson || ""),
        impact: String(item.impact || item.affected || ""),
        operation_id: String(item.operation_id || ""),
        task_id: String(item.task_id || ""),
      })),
      ...failures.map((item) => {
        const raw = (item.raw || {}) as Record<string, unknown>;
        return {
          ...raw,
          id: item.id,
          title: item.title,
          message: item.message,
          created_at: item.occurredAt,
          severity: item.severity,
          status: String(raw.status || "open"),
          next_action: String(raw.recovery_hint || raw.recommended_action || ""),
        };
      }),
      ...errors.map((item, index) => ({
        ...item,
        id: String(item.id || item.error_id || `error-${index}`),
        title: String(item.title || item.error || "エラー"),
        message: String(item.message || item.summary || ""),
        created_at: Number(item.created_at || item.last_seen_at || 0),
        status: String(item.status || "open"),
        next_action: String(item.recovery_hint || item.recommended_action || ""),
      })),
    ];
    const byId = new Map<string, Record<string, unknown>>();
    for (const item of items) {
      const id = String(item.id || item.repair_id || item.title);
      if (!byId.has(id)) byId.set(id, item);
    }
    return [...byId.values()].sort((a, b) => Number(b.created_at || 0) - Number(a.created_at || 0));
  }, [errors, failures, repairs]);

  const routeDetailId =
    detailId
    || (() => {
      const path = pathname || (typeof window !== "undefined" ? window.location.pathname : "");
      const match = path.match(/^\/dashboard\/incidents\/([^/]+)$/);
      return match?.[1] ? decodeURIComponent(match[1]) : "";
    })();
  const [selectedId, setSelectedId] = useState(routeDetailId || String(combined[0]?.id || ""));
  useEffect(() => {
    if (routeDetailId) setSelectedId(routeDetailId);
  }, [routeDetailId]);

  const selected = combined.find((item) => String(item.id) === selectedId) || combined[0];

  const select = (id: string) => {
    setSelectedId(id);
    onNavigate?.(`/dashboard/incidents/${encodeURIComponent(id)}`);
  };

  return (
    <div className="grid">
      <PageHeader
        title="Incidents & Repairs"
        description="同じ障害を一つの Incident としてまとめ、失敗・再試行・修復・最終結果を時系列で確認します。"
      />
      <div className="judgment-split">
        <section className="panel">
          <div className="compact-list">
            {combined.map((item) => {
              const id = String(item.id);
              return (
                <button type="button" className="list-row" data-selected={selected?.id === id} key={id} onClick={() => select(id)}>
                  <SeverityGlyph severity="critical" />
                  <div>
                    <strong>{text(item.title, "障害")}</strong>
                    <p>{text(item.impact || item.message)}</p>
                    <small>{time(item.created_at)} · 試行 {Number(item.attempt_count || 0)} 回</small>
                  </div>
                  <StatusBadge status={text(item.status, "open")} />
                </button>
              );
            })}
            {!combined.length ? <p className="muted">未解決の障害はありません。</p> : null}
          </div>
        </section>
        <aside className="panel judgment-detail">
          {selected ? (
            <>
              <div className="panel__header">
                <h2>{text(selected.title, "Incident")}</h2>
                <StatusBadge status={text(selected.status, "open")} />
              </div>
              <p className="human-summary">{text(selected.message)}</p>
              <dl className="human-facts compact">
                <div><dt>影響</dt><dd>{text(selected.impact || selected.message || "—")}</dd></div>
                <div><dt>状態</dt><dd>{text(selected.status, "open")}</dd></div>
                <div><dt>試行回数</dt><dd>{Number(selected.attempt_count || 0)}</dd></div>
                <div><dt>次に必要な対応</dt><dd>{text(selected.next_action || "—")}</dd></div>
                <div><dt>Operation</dt><dd>{text(selected.operation_id || "—")}</dd></div>
                <div><dt>Task</dt><dd>{text(selected.task_id || "—")}</dd></div>
                <div><dt>Lesson</dt><dd>{text(selected.lesson || "—")}</dd></div>
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
            <p className="empty-copy">Incident を選択してください。</p>
          )}
        </aside>
      </div>
    </div>
  );
}
