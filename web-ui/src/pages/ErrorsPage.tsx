import { buildAttentionItems } from "../attentionModel";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { text, time } from "./PageSupport";

export function ErrorsPage({ overview }: { overview: UiOverview }) {
  const failures = buildAttentionItems(overview).filter((item) => item.kind === "failure");
  const errors = overview.errors?.data.items || [];
  const combined: Array<Record<string, unknown>> = [...failures.map((item) => ({ ...item.raw, id: item.id, title: item.title, message: item.message, created_at: item.occurredAt, severity: item.severity })), ...errors];
  const unique = [...new Map(combined.map((item, index) => [String(item.id || item.error_id || `${item.title}-${index}`), item])).values()];
  return <div className="grid"><PageHeader title="エラー" description="未解決の失敗、修復状況、推奨対応を集約します。" /><section className="panel"><div className="compact-list">{unique.map((item, index) => <article className="list-row" key={String(item.id || index)}><SeverityGlyph severity="critical" /><div><strong>{text(item.title || item.error, "エラー")}</strong><p>{text(item.message || item.summary)}</p><small>{time(item.created_at || item.last_seen_at)}</small></div><div><strong>{text(item.status, "未解決")}</strong><p>{text(item.recovery_hint || item.recommended_action, "詳細を確認")}</p></div></article>)}{!unique.length ? <p className="muted">未解決エラーはありません。</p> : null}</div></section></div>;
}
