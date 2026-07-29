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
    <PageHeader title="Overview" description="Prioritizes what AEGIS is doing now and what needs your attention.">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.core.source_updated_at} stale={overview.core.stale} />
    </PageHeader>
    <a className="home-attention-hero" href="/dashboard/attention" data-clear={attention === 0}>
      {attention ? <AlertTriangle aria-hidden="true" /> : <CheckCircle2 aria-hidden="true" />}
      <div><span>Needs attention</span><strong>{attention ? `${attention} item(s) need review` : "No items currently need attention"}</strong></div>
      <ArrowRight aria-hidden="true" />
    </a>
    <div className="home-summary-grid">
      <section className="panel">
        <header><PlayCircle size={18} /><h2>Current work</h2></header>
        <h3>{task.title || "No task is currently running"}</h3>
        <p>{task.current_action || task.next_action || "Waiting for a new request or continuation condition."}</p>
        {task.task_id ? <a href={`/dashboard/work/tasks?task=${encodeURIComponent(task.task_id)}`}>Open task details <ArrowRight size={14} /></a> : null}
      </section>
      <section className="panel">
        <header><h2>AEGIS status</h2><StatusBadge status={String(overview.core.data.health || "DEGRADED")} /></header>
        <dl className="home-facts"><div><dt>Operating mode</dt><dd>{String(overview.core.data.mode || "IDLE")}</dd></div><div><dt>Servers</dt><dd>{servers.filter((server) => server.status === "ONLINE").length} / {servers.length} online</dd></div><div><dt>Pending approvals</dt><dd>{overview.approvals.data.pending_count || 0}</dd></div></dl>
      </section>
    </div>
    <section className="panel">
      <header><h2>Recent results</h2><Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.activity?.source_updated_at || overview.generated_at} stale={overview.activity?.stale} /></header>
      <div className="compact-list">{recent.length ? recent.map((item) => <article className="list-row" key={String(item.operation_id || item.title)}><div><strong>{item.title || item.kind_label || "Operation"}</strong><p>{item.narrative || item.what_happened || item.summary || "No details available"}</p></div><StatusBadge status={String(item.status || "completed")} /></article>) : <p className="muted">No recent operation results.</p>}</div>
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
