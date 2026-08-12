import { MessageSquare, Search } from "lucide-react";
import { SeverityGlyph } from "./viz/UxViz";
import type { UiOverview } from "../types";

function onlineCount(overview: UiOverview): number {
  return (overview.servers.data.items || []).filter((item) => String(item.status).toUpperCase() === "ONLINE").length;
}

function errorCount(overview: UiOverview): number {
  return (overview.errors?.data.items || []).filter(
    (item) => !["resolved", "repaired", "ignored"].includes(String(item.status || "").toLowerCase()),
  ).length;
}

function autonomousOn(overview: UiOverview): boolean {
  const mind = overview.mind_summary?.data || overview.mind?.data || {};
  const autonomy = (mind as Record<string, unknown>).autonomy as Record<string, unknown> | undefined;
  if (typeof autonomy?.enabled === "boolean") return autonomy.enabled;
  if (typeof autonomy?.running === "boolean") return autonomy.running;
  return String((mind as Record<string, unknown>).mode || overview.core.data.mode || "").toUpperCase() !== "STOPPED";
}

function llmStatus(overview: UiOverview): string {
  const usage = overview.usage?.data || {};
  const tokens = Number(usage.total_tokens || 0);
  const calls = Number(usage.total_calls || usage.total_requests || 0);
  if (tokens > 0) return `${Math.round(tokens).toLocaleString()} tok`;
  if (calls > 0) return `${calls} calls`;
  const state = String(usage.budget_state || usage.provider_status || "");
  if (state && state !== "not_reported") return state;
  const health = String(overview.core.data.health || "UNKNOWN").toUpperCase();
  return health === "ONLINE" ? "ready" : health.toLowerCase();
}

function runningCount(overview: UiOverview): number {
  return (overview.tasks?.data.active || []).length;
}

export function GlobalStatusBar({
  overview,
  onOpenSearch,
  onOpenChat,
  onNavigate,
}: {
  overview: UiOverview;
  onOpenSearch: () => void;
  onOpenChat: () => void;
  onNavigate: (path: string) => void;
}) {
  const health = String(overview.core.data.health || "UNKNOWN");
  const activeCount = runningCount(overview);
  const approvals = overview.approvals.data.pending_count || 0;
  const errors = errorCount(overview);
  const serversOnline = onlineCount(overview);
  const serversTotal = (overview.servers.data.items || []).length;
  const auto = autonomousOn(overview);
  const llm = llmStatus(overview);

  return (
    <header className="global-status-bar" aria-label="AEGIS global status">
      <button type="button" className="gsb-chip" data-severity={health === "ONLINE" ? "ok" : "warning"} onClick={() => onNavigate("/dashboard")}>
        <SeverityGlyph severity={health === "ONLINE" ? "ok" : "warning"} />
        <span>稼働</span>
        <strong>{health}</strong>
      </button>
      <button type="button" className="gsb-chip" data-on={auto} onClick={() => onNavigate("/dashboard/autonomous")}>
        <span>自律</span>
        <strong>{auto ? "ON" : "OFF"}</strong>
      </button>
      <button type="button" className="gsb-chip" onClick={() => onNavigate("/dashboard/work/tasks")}>
        <span>実行中</span>
        <strong>{activeCount}</strong>
      </button>
      <button type="button" className="gsb-chip" data-severity={approvals ? "warning" : "ok"} onClick={() => onNavigate("/dashboard/approvals")}>
        <span>承認待ち</span>
        <strong>{approvals}</strong>
      </button>
      <button type="button" className="gsb-chip" data-severity={errors ? "critical" : "ok"} onClick={() => onNavigate("/dashboard/observability/errors")}>
        <span>エラー</span>
        <strong>{errors}</strong>
      </button>
      <button type="button" className="gsb-chip" onClick={() => onNavigate("/dashboard/infrastructure/servers")}>
        <span>接続</span>
        <strong>
          {serversOnline}/{serversTotal}
        </strong>
      </button>
      <button type="button" className="gsb-chip" onClick={() => onNavigate("/dashboard/observability/llm-usage")}>
        <span>LLM</span>
        <strong>{llm}</strong>
      </button>
      <span className="gsb-chip gsb-chip--static">
        <span>更新</span>
        <strong>{new Date(overview.generated_at).toLocaleTimeString()}</strong>
      </span>
      <div className="gsb-actions">
        <button type="button" className="gsb-action" onClick={onOpenSearch} aria-label="全体検索">
          <Search size={15} />
          <span>検索</span>
          <kbd>Ctrl K</kbd>
        </button>
        <button type="button" className="gsb-action" onClick={onOpenChat} aria-label="Chatを開く">
          <MessageSquare size={15} />
          <span>Chat</span>
        </button>
      </div>
    </header>
  );
}
