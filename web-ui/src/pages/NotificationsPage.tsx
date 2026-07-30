import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph, type Severity } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { text, time } from "./PageSupport";

export function NotificationsPage({ overview }: { overview: UiOverview }) {
  const items = overview.notifications.data.recent || [];
  return <div className="grid"><PageHeader title="通知" description={`未読 ${overview.notifications.data.unread_count || 0} 件`} /><section className="panel"><div className="compact-list">{items.map((item, index) => <article className="list-row" key={String(item.notification_id || item.id || index)}><SeverityGlyph severity={String(item.severity || "info").toLowerCase() as Severity} /><div><strong>{text(item.title, "通知")}</strong><p>{text(item.message || item.summary)}</p><small>{time(item.created_at || item.updated_at)}</small></div>{item.href ? <a href={String(item.href)}>開く</a> : null}</article>)}{!items.length ? <p className="muted">通知はありません。</p> : null}</div></section></div>;
}
