import { AlertTriangle, ArrowRight, CheckCircle2, PlayCircle } from "lucide-react";
import { Freshness } from "../components/Freshness";
import { PageHeader } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

export function HomePage({ overview }: { overview: UiOverview }) {
  const task = overview.current_task.data;
  const attention = attentionCount(overview);
  const recent = overview.activity?.data.operations?.slice(0, 5) || [];
  const servers = overview.servers.data.items || [];
  return <div className="home-page">
    <PageHeader title="概要" description="AEGISが今していることと、あなたの対応が必要なことを優先して表示します。">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.core.source_updated_at} stale={overview.core.stale} />
    </PageHeader>
    <a className="home-attention-hero" href="/dashboard/attention" data-clear={attention === 0}>
      {attention ? <AlertTriangle aria-hidden="true" /> : <CheckCircle2 aria-hidden="true" />}
      <div><span>対応が必要</span><strong>{attention ? `${attention}件の確認事項があります` : "現在、対応が必要な項目はありません"}</strong></div>
      <ArrowRight aria-hidden="true" />
    </a>
    <div className="home-summary-grid">
      <section className="panel">
        <header><PlayCircle size={18} /><h2>現在の仕事</h2></header>
        <h3>{task.title || "実行中のタスクはありません"}</h3>
        <p>{task.current_action || task.next_action || "新しい依頼または継続条件を待っています。"}</p>
        {task.task_id ? <a href={`/dashboard/work/tasks?task=${encodeURIComponent(task.task_id)}`}>タスク詳細を開く <ArrowRight size={14} /></a> : null}
      </section>
      <section className="panel">
        <header><h2>AEGISの状態</h2><StatusBadge status={String(overview.core.data.health || "DEGRADED")} /></header>
        <dl className="home-facts"><div><dt>動作モード</dt><dd>{String(overview.core.data.mode || "IDLE")}</dd></div><div><dt>サーバー</dt><dd>{servers.filter((server) => server.status === "ONLINE").length} / {servers.length} オンライン</dd></div><div><dt>承認待ち</dt><dd>{overview.approvals.data.pending_count || 0}件</dd></div></dl>
      </section>
    </div>
    <section className="panel">
      <header><h2>直近の結果</h2><Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.activity?.source_updated_at || overview.generated_at} stale={overview.activity?.stale} /></header>
      <div className="compact-list">{recent.length ? recent.map((item) => <article className="list-row" key={String(item.operation_id || item.title)}><div><strong>{item.title || item.kind_label || "処理"}</strong><p>{item.narrative || item.what_happened || item.summary || "詳細はありません"}</p></div><StatusBadge status={String(item.status || "completed")} /></article>) : <p className="muted">直近の処理結果はありません。</p>}</div>
    </section>
  </div>;
}

function attentionCount(overview: UiOverview): number {
  const base = overview.attention.data.items?.length || 0;
  const approvals = overview.approvals.data.pending_count || 0;
  const errors = overview.errors?.data.items?.filter((item) => !["resolved", "repaired"].includes(String(item.status || "").toLowerCase())).length || 0;
  const servers = overview.servers.data.items.filter((item) => ["OFFLINE", "DEGRADED"].includes(String(item.status).toUpperCase())).length;
  return base + approvals + errors + servers;
}
