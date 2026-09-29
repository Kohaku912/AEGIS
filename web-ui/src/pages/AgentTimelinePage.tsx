/**
 * AgentTimelinePage (Phase D7 / DASHBOARD_REFINED_PLAN.md §3 Phase D7 / instruction.md §18).
 *
 * 複数 Agent Session の並列 Timeline (Gantt chart) を表示するページ。
 * 横軸: 時間 (各 session の first_event_ms ~ last_event_ms)。
 * 縦軸: agent_session_id 単位 (1 session = 1 行)。
 * クリックで該当 Agent Session 詳細へ遷移。
 *
 * バックエンド: 既存 `/api/ui/agent-sessions` を `fetchAgentSessions(200)` で
 * 取得して使う (D4 で追加済み)。
 *
 * 設計判断:
 * - SVG ではなく CSS flex + absolute position で Gantt bar を描画
 *   (既存の `tokens.css` カラー変数をそのまま使える)
 * - status 別色 (running: cyan, completed: green, failed: red, unknown: gray)
 * - 検索: text input で `agent_session_id` / `task_id` 部分一致フィルタ
 * - 各 bar に `title` 属性でツールチップ (agent_session_id / 期間 / event count)
 */

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { fetchAgentSessions, type AgentSessionSummary } from "../api/client";
import { PageHeader } from "../components/DashboardPrimitives";
import { asRecord, text, time } from "./PageSupport";

type TimelineRow = AgentSessionSummary & {
  rowId: string;
  startMs: number;
  endMs: number;
};

type TimelinePreset = "all" | "running" | "failed" | "pending_approval" | "high_risk" | "policy_watch";

function toRows(sessions: AgentSessionSummary[]): TimelineRow[] {
  const now = Date.now();
  return sessions
    .map((session) => {
      const startMs = Number(session.first_event_ms || 0);
      // running の session は last_event_ms=0 のことがある → now まで描画
      const endMsRaw = Number(session.last_event_ms || 0);
      const endMs = endMsRaw > 0 ? endMsRaw : session.status === "running" ? now : startMs;
      return {
        ...session,
        rowId: String(session.agent_session_id || `${startMs}-${Math.random()}`),
        startMs,
        endMs,
      };
    })
    .filter((row) => row.startMs > 0)
    .sort((a, b) => b.startMs - a.startMs);
}

function statusClass(status: string): string {
  if (status === "running") return "agent-timeline__bar--running";
  if (status === "completed") return "agent-timeline__bar--completed";
  if (status === "failed") return "agent-timeline__bar--failed";
  return "agent-timeline__bar--unknown";
}

function causalSummary(row: TimelineRow): string {
  if (row.causal_summary) return row.causal_summary;
  if (row.root_cause?.summary) {
    return `${row.root_cause.kind}: ${row.root_cause.summary}`;
  }
  if (row.pending_approval) return `Pending approval is the current blocker (${row.approval_count} approval events).`;
  if (row.status === "failed") return row.summary ? `Failed: ${row.summary}` : "Failed without a final summary.";
  if (row.status === "running") return "Still executing without a final outcome.";
  return row.summary || "No explicit causal summary.";
}

function milestoneMarkers(row: TimelineRow): Array<{ key: string; left: number; label: string; className: string }> {
  const span = Math.max(1, row.endMs - row.startMs);
  if (row.milestones && row.milestones.length) {
    return row.milestones.map((milestone) => ({
      key: milestone.key,
      left: Math.max(0, Math.min(100, ((milestone.timestamp_ms - row.startMs) / span) * 100)),
      label: milestone.label,
      className: markerClass(milestone.variant),
    }));
  }
  const markers: Array<{ key: string; left: number; label: string; className: string }> = [
    { key: "start", left: 0, label: "start", className: "agent-timeline__marker--start" },
  ];
  if (row.pending_approval) {
    markers.push({ key: "approval", left: 60, label: `approval ${row.approval_count}`, className: "agent-timeline__marker--approval" });
  }
  if (row.policy_deny_count > 0) {
    markers.push({ key: "deny", left: 82, label: `deny ${row.policy_deny_count}`, className: "agent-timeline__marker--deny" });
  }
  if (row.status === "failed") {
    markers.push({ key: "failed", left: 100, label: "failed", className: "agent-timeline__marker--failed" });
  } else if (row.status === "completed") {
    markers.push({ key: "completed", left: 100, label: "done", className: "agent-timeline__marker--completed" });
  }
  return markers;
}

function markerClass(variant: string): string {
  if (variant === "start") return "agent-timeline__marker--start";
  if (variant === "approval" || variant === "approval_resolved") return "agent-timeline__marker--approval";
  if (variant === "deny") return "agent-timeline__marker--deny";
  if (variant === "failed") return "agent-timeline__marker--failed";
  if (variant === "completed") return "agent-timeline__marker--completed";
  return "agent-timeline__marker--start";
}

export function AgentTimelinePage({
  onNavigate,
}: {
  onNavigate: (path: string) => void;
}) {
  const sessionsQuery = useQuery({
    queryKey: ["agent-sessions-for-timeline", 200],
    queryFn: () => fetchAgentSessions(200),
    refetchInterval: 15_000,
  });
  const sessions = sessionsQuery.data?.sessions ?? [];
  const [filter, setFilter] = useState("");
  const [preset, setPreset] = useState<TimelinePreset>("all");

  const rows = useMemo(() => {
    const all = toRows(sessions);
    const filteredByPreset = all.filter((row) => matchesPreset(row, preset));
    if (!filter.trim()) return filteredByPreset;
    const q = filter.trim().toLowerCase();
    return filteredByPreset.filter((row) => {
      const sid = String(row.agent_session_id || "").toLowerCase();
      const tid = String(row.task_id || "").toLowerCase();
      const summary = String(row.summary || "").toLowerCase();
        const causal = String(row.causal_summary || row.root_cause?.summary || "").toLowerCase();
        return sid.includes(q) || tid.includes(q) || summary.includes(q) || causal.includes(q);
    });
  }, [sessions, filter, preset]);

  // 時間軸のレンジ: rows の startMs / endMs / now の最小・最大
  const range = useMemo(() => {
    const now = Date.now();
    if (!rows.length) return { from: now - 60 * 60 * 1000, to: now };
    let from = rows[0].startMs;
    let to = now;
    for (const row of rows) {
      if (row.startMs > 0 && row.startMs < from) from = row.startMs;
      if (row.endMs > to) to = row.endMs;
    }
    // 最低 60 秒幅を確保 (running session が瞬間で潰れないように)
    if (to - from < 60_000) {
      const mid = (to + from) / 2;
      from = mid - 30_000;
      to = mid + 30_000;
    }
    return { from, to };
  }, [rows]);

  const totalSpan = Math.max(1, range.to - range.from);
  const running = rows.filter((row) => row.status === "running").length;
  const completed = rows.filter((row) => row.status === "completed").length;
  const failed = rows.filter((row) => row.status === "failed").length;
  const pendingApproval = rows.filter((row) => row.pending_approval).length;
  const highRisk = rows.filter((row) => isHighRisk(row.highest_risk)).length;

  // 1分ごとに再描画 (running session の now ラインを更新)
  const [, setTick] = useState(0);
  useEffect(() => {
    const handle = window.setInterval(() => setTick((n) => n + 1), 60_000);
    return () => window.clearInterval(handle);
  }, []);

  return (
    <div className="grid agent-timeline-page">
      <PageHeader
        title="Agent Timeline (D7)"
        description="複数 Agent Session の並列 Timeline。1 行 = 1 session、横軸 = 時間、status 別色分け。"
      >
        <button
          type="button"
          className="secondary-button"
          onClick={() => sessionsQuery.refetch()}
          disabled={sessionsQuery.isFetching}
        >
          Refresh
        </button>
      </PageHeader>

      <section className="panel agent-timeline-page__toolbar">
        <label className="search-field">
          <Search size={14} aria-hidden="true" />
          <input
            value={filter}
            onChange={(event) => setFilter(event.currentTarget.value)}
            placeholder="agent_session_id / task_id / summary を部分一致検索"
            aria-label="Agent session 検索"
          />
        </label>
        <div className="agent-timeline-page__filters" aria-label="Agent session フィルタ">
          {[
            { id: "all", label: "All" },
            { id: "running", label: "Running" },
            { id: "failed", label: "Failed" },
            { id: "pending_approval", label: "Pending approval" },
            { id: "high_risk", label: "High risk" },
            { id: "policy_watch", label: "Policy watch" },
          ].map((option) => (
            <button
              key={option.id}
              type="button"
              className="secondary-button agent-timeline-page__filter"
              data-active={preset === option.id}
              aria-pressed={preset === option.id}
              onClick={() => setPreset(option.id as TimelinePreset)}
            >
              {option.label}
            </button>
          ))}
        </div>
        <span className="muted">
          {sessionsQuery.isLoading
            ? "読み込み中…"
            : `${rows.length} / ${sessions.length} session`}
        </span>
        <span className="muted">
          期間: {time(range.from)} → {time(range.to)}
        </span>
        <span className="muted">
          running={running} / completed={completed} / failed={failed}
        </span>
        <span className="muted">
          pending approval={pendingApproval} / high risk={highRisk}
        </span>
      </section>

      <section className="panel">
        {sessionsQuery.isError ? (
          <p className="muted">Agent session 一覧の取得に失敗しました。</p>
        ) : !rows.length ? (
          <p className="muted">表示可能な session はありません。</p>
        ) : (
          <ol className="agent-timeline" data-testid="agent-timeline">
            {rows.map((row) => {
              const left = ((row.startMs - range.from) / totalSpan) * 100;
              const width = Math.max(0.5, ((row.endMs - row.startMs) / totalSpan) * 100);
              const isLive = row.status === "running";
              return (
                <li
                  key={row.rowId}
                  className="agent-timeline__row"
                  data-status={row.status}
                  data-testid={`agent-timeline-row-${row.agent_session_id}`}
                >
                  <div className="agent-timeline__row-header">
                    <button
                      type="button"
                      className="link-button"
                      title={`Agent session 詳細へ: ${row.agent_session_id}`}
                      onClick={() => onNavigate(`/dashboard/agent-sessions/${encodeURIComponent(row.agent_session_id)}`)}
                    >
                      <code>{text(row.agent_session_id, "(no id)")}</code>
                    </button>
                    <span className="muted">
                      task=<code>{text(row.task_id, "—")}</code> · events=<strong>{row.event_count}</strong>
                    </span>
                    <span className="muted">
                      {time(row.startMs)} → {isLive ? "now" : time(row.endMs)}
                    </span>
                    <span className="muted">
                      approvals=<strong>{row.approval_count}</strong>
                      {row.pending_approval ? " · waiting approval" : ""}
                      {row.policy_ask_count || row.policy_deny_count
                        ? ` · policy ask=${row.policy_ask_count} deny=${row.policy_deny_count}`
                        : ""}
                    </span>
                    {row.highest_risk ? (
                      <span className="muted">
                        risk=<strong>{row.highest_risk}</strong>
                      </span>
                    ) : null}
                    <span className="muted">{causalSummary(row)}</span>
                    <span className={`status-badge agent-timeline__status agent-timeline__status--${row.status}`}>
                      {row.status}
                    </span>
                  </div>
                  <div className="agent-timeline__track" aria-hidden="true">
                    <div
                      className={`agent-timeline__bar ${statusClass(row.status)}`}
                      style={{ left: `${left}%`, width: `${width}%` }}
                      title={`${row.agent_session_id} · ${time(row.startMs)} → ${isLive ? "now" : time(row.endMs)} · ${row.event_count} events`}
                    />
                    <div className="agent-timeline__markers">
                      {milestoneMarkers(row).map((marker) => (
                        <span
                          key={marker.key}
                          className={`agent-timeline__marker ${marker.className}`}
                          style={{ left: `${left + (width * marker.left) / 100}%` }}
                          title={marker.label}
                        />
                      ))}
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </section>

      <section className="panel agent-timeline-page__legend">
        <h2>凡例</h2>
        <ul className="compact-list">
          <li>
            <span className="agent-timeline__legend-swatch agent-timeline__bar--running" /> running (cyan)
          </li>
          <li>
            <span className="agent-timeline__legend-swatch agent-timeline__bar--completed" /> completed (green)
          </li>
          <li>
            <span className="agent-timeline__legend-swatch agent-timeline__bar--failed" /> failed (red)
          </li>
          <li>
            <span className="agent-timeline__legend-swatch agent-timeline__bar--unknown" /> unknown (gray)
          </li>
        </ul>
      </section>
    </div>
  );
}

// avoid unused import warning on `asRecord` (PageSupport の補助関数を re-export する場合に備える)
void asRecord;

function matchesPreset(row: TimelineRow, preset: TimelinePreset): boolean {
  if (preset === "all") return true;
  if (preset === "running") return row.status === "running";
  if (preset === "failed") return row.status === "failed";
  if (preset === "pending_approval") return row.pending_approval;
  if (preset === "high_risk") return isHighRisk(row.highest_risk);
  if (preset === "policy_watch") return row.policy_ask_count > 0 || row.policy_deny_count > 0;
  return true;
}

function isHighRisk(value: string): boolean {
  const normalized = String(value || "").toLowerCase();
  return ["high", "critical", "high_risk", "forbidden", "approval_required"].includes(normalized);
}
