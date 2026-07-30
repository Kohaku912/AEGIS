import { Freshness } from "../components/Freshness";
import { PageHeader } from "../components/DashboardPrimitives";
import { CriticalOverlay, ProgressSteps, SeverityGlyph, TopologyMiniMap, type Severity } from "../components/viz/UxViz";
import { buildAttentionItems } from "../attentionModel";
import type { UiOverview } from "../types";
import { asRecords, count, RecordList, text, time } from "./PageSupport";

type HomeProps = {
  overview: UiOverview;
  onNavigate?: (path: string) => void;
  onSelect?: (entity: Record<string, unknown>) => void;
};

export function HomePage({ overview, onNavigate, onSelect }: HomeProps) {
  const task = overview.current_task.data;
  const servers = overview.servers.data.items || [];
  const attention = buildAttentionItems(overview);
  const active = overview.tasks?.data.active || [];
  const waiting = overview.tasks?.data.waiting || [];
  const capabilities = asRecords(overview.capabilities?.data.items).slice(0, 5);
  const autonomous = overview.autonomous_logs?.data.cycles || overview.executions?.data.autonomous_cycles || [];
  const recent = overview.activity?.data.operations || [];
  const completed = recent.filter((item) => ["completed", "success", "ok"].includes(String(item.status || "").toLowerCase())).slice(0, 5);
  const offline = servers.filter((server) => String(server.status).toUpperCase() !== "ONLINE").length;
  const usage = overview.usage.data;
  const lastCycle = autonomous[0];
  const settings = asRecords(overview.core.data.recent_settings);
  const steps = task.steps || [];
  const go = (path: string) => (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (!onNavigate) return;
    event.preventDefault();
    onNavigate(path);
  };
  return <div className="home-page grid">
    <PageHeader title="AEGIS コックピット" description="現在の稼働、要対応項目、直近の成果を一画面で確認します。">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.core.source_updated_at} stale={overview.core.stale} />
    </PageHeader>
    <section className="panel stat-grid">
      {[
        ["健全性", text(overview.core.data.health, "不明")],
        ["実行中", active.length],
        ["入力待ち", waiting.filter((item) => String(item.status || "").includes("input") || item.waiting_for_input).length],
        ["承認待ち", overview.approvals.data.pending_count || 0],
        ["異常サーバー", offline],
        ["本日の LLM", text(usage.today_cost || usage.cost_today || usage.today_tokens || usage.summary)],
        ["最終自律実行", time(lastCycle?.created_at || lastCycle?.started_at || overview.initiative?.data.updated_at)],
      ].map(([label, value]) => <div className="stat" key={String(label)}><span className="muted">{label}</span><b>{value}</b></div>)}
    </section>
    <CriticalOverlay items={attention.map((item) => ({ id: item.id, title: item.title, severity: item.severity as Severity }))} onOpen={() => onNavigate ? onNavigate("/dashboard/attention") : window.location.assign("/dashboard/attention")} />
    <section className="panel">
      <header><h2>要対応</h2><a href="/dashboard/attention" onClick={go("/dashboard/attention")}>すべて表示</a></header>
      <RecordList items={attention.slice(0, 5).map((item) => item.raw || { id: item.id, title: item.title, message: item.message, severity: item.severity })} render={(item) => <><SeverityGlyph severity={String(item.severity || "warning") as Severity} /><button type="button" onClick={() => onSelect?.(item)}><strong>{text(item.title)}</strong><p>{text(item.message || item.summary)}</p></button></>} />
    </section>
    <div className="home-summary-grid">
      <section className="panel"><header><h2>現在の作業</h2></header><h3>{task.title || "実行中のタスクなし"}</h3><p>{task.current_action || task.next_action || "次の依頼を待機しています。"}</p><ProgressSteps total={Math.max(steps.length, 1)} current={steps.filter((step) => String(step.status).toLowerCase() === "completed").length} failed={steps.filter((step) => String(step.status).toLowerCase() === "failed").length} /></section>
      <section className="panel"><header><h2>サーバートポロジー</h2></header><TopologyMiniMap servers={servers} /></section>
    </div>
    <div className="grid grid--three">
      <section className="panel"><h2>最近完了した操作</h2><RecordList items={completed} /></section>
      <section className="panel"><h2>最近の自律実行</h2><RecordList items={autonomous.slice(0, 5)} /></section>
      <section className="panel"><h2>最近の能力</h2><RecordList items={capabilities} /></section>
    </div>
    {settings.length ? <section className="panel"><h2>最近変更した設定</h2><RecordList items={settings.slice(0, 5)} /></section> : null}
    <section className="panel">
      <header><h2>稼働サマリー</h2></header>
      <div className="metric-list"><div className="metric-row"><span>登録能力</span><strong>{count(overview.capabilities?.data.count)}</strong></div><div className="metric-row"><span>サーバー</span><strong>{servers.length - offline}/{servers.length} online</strong></div></div>
    </section>
  </div>;
}
