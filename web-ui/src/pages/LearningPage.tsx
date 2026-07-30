import { useEffect, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { PageHeader } from "../components/DashboardPrimitives";
import type { EntitySummary, UiOverview } from "../types";
import { text } from "./PageSupport";

export function LearningPage({ overview }: { overview: UiOverview }) {
  const [items, setItems] = useState<EntitySummary[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    fetchResourceEntities("memories", query, { limit: 100 }).then((result) => {
      if (alive) setItems(result.items.filter((item) => ["skill", "lesson", "procedure", "trace", "pattern"].some((kind) => `${item.type} ${item.data?.memory_type || ""}`.toLowerCase().includes(kind))));
    }).catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, [query]);
  const repairs = overview.repairs?.data.items || [];
  return <div className="grid">
    <PageHeader title="学習" description="獲得したスキル、教訓、行動パターンと根拠を確認します。" />
    <section className="panel"><label>検索 <input type="search" value={query} onChange={(event) => setQuery(event.currentTarget.value)} /></label>{error ? <p className="data-state data-state--error">{error}</p> : null}<div className="compact-list">{items.map((item) => <article className="list-row" key={item.id}><div><strong>{item.title}</strong><p>{item.subtitle}</p></div><div className="metric-list"><div className="metric-row"><span>パターン</span><strong>{text(item.data?.pattern || item.data?.memory_type || item.type)}</strong></div><div className="metric-row"><span>信頼度</span><strong>{text(item.data?.confidence, "未評価")}</strong></div></div></article>)}{!items.length ? <p className="muted">該当する学習記録はありません。</p> : null}</div></section>
    <section className="panel"><h2>修復から得た教訓</h2>{repairs.map((item, index) => <article className="list-row" key={String(item.id || index)}><div><strong>{text(item.summary || item.category, "教訓")}</strong><p>{text(item.lesson)}</p></div></article>)}</section>
  </div>;
}
