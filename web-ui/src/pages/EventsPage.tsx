import { useMemo, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph, type Severity } from "../components/viz/UxViz";
import type { UiEvent, UiOverview } from "../types";
import { text, time } from "./PageSupport";

export function EventsPage({ overview, recentEvents = [] }: { overview: UiOverview; recentEvents?: UiEvent[] }) {
  const [tab, setTab] = useState<"realtime" | "all">("realtime");
  const activity = overview.activity?.data.recent || [];
  const items = useMemo(() => tab === "realtime" ? recentEvents : [...recentEvents, ...activity as unknown as UiEvent[]], [activity, recentEvents, tab]);
  return <div className="grid"><PageHeader title="イベント" description="上流でノイズ除去されたリアルタイムイベントと履歴です。" /><div className="page-tabs" role="tablist"><button type="button" role="tab" aria-selected={tab === "realtime"} onClick={() => setTab("realtime")}>リアルタイム</button><button type="button" role="tab" aria-selected={tab === "all"} onClick={() => setTab("all")}>すべて</button></div><section className="panel"><div className="compact-list">{items.map((item, index) => <article className="list-row" key={String(item.event_id || item.sequence || index)}><SeverityGlyph severity={String(item.severity || item.priority || "info").toLowerCase() as Severity} /><div><strong>{text(item.safe_title || item.type || item.event_type, "イベント")}</strong><p>{text(item.safe_message || item.message || item.payload)}</p><small>{text(item.source_type)} · {time(item.occurred_at || item.generated_at)}</small></div></article>)}{!items.length ? <p className="muted">イベントはありません。</p> : null}</div></section></div>;
}
