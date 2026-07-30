import type { ReactNode } from "react";

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

export function asRecords(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object") : [];
}

export function text(value: unknown, fallback = "—"): string {
  if (value === undefined || value === null || value === "") return fallback;
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function count(value: unknown): number {
  if (Array.isArray(value)) return value.length;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function time(value: unknown): string {
  const numeric = Number(value);
  if (!numeric) return "時刻不明";
  const milliseconds = numeric < 10_000_000_000 ? numeric * 1000 : numeric;
  return new Date(milliseconds).toLocaleString("ja-JP");
}

export function RecordList({ items, empty = "データはありません", render }: {
  items: Array<Record<string, unknown>>;
  empty?: string;
  render?: (item: Record<string, unknown>, index: number) => ReactNode;
}) {
  if (!items.length) return <p className="muted">{empty}</p>;
  return <div className="compact-list">{items.map((item, index) => (
    <article className="list-row" key={String(item.id || item.task_id || item.event_id || item.operation_id || item.title || index)}>
      {render ? render(item, index) : <div><strong>{text(item.title || item.name || item.type, "項目")}</strong><p>{text(item.summary || item.message || item.status)}</p></div>}
    </article>
  ))}</div>;
}

export function KeyValues({ data, limit = 20 }: { data: Record<string, unknown>; limit?: number }) {
  const entries = Object.entries(data).slice(0, limit);
  if (!entries.length) return <p className="muted">データはありません</p>;
  return <div className="metric-list">{entries.map(([key, value]) => (
    <div className="metric-row" key={key}><span>{key}</span><strong>{text(value)}</strong></div>
  ))}</div>;
}
