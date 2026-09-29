/**
 * AgentSessionPage (Phase D4 / DASHBOARD_REFINED_PLAN.md §3 Phase D4 / instruction.md §10).
 *
 * Agent 1 実行 = 1 `agent_session_id` (Phase D3) 単位の 9 tabs 画面:
 * Overview / Thinking / Tools / MCP / Files / Terminal / Approvals / Errors / Raw.
 *
 * 情報階層 (instruction.md §2):
 * - Overview:  session 単位の summary (task_id, status, event count, kind 一覧)
 * - Thinking:  agent.thinking イベントのテキスト列
 * - Tools:     agent.tool.started / agent.tool.completed + tool.execution.* イベント
 * - MCP:       tool フィールドに `mcp.*` を含む events
 * - Files:     tool フィールドに `file.*` を含む events
 * - Terminal:  tool フィールドに `terminal.*` を含む events
 * - Approvals: approval.* イベント
 * - Errors:    agent.failed + tool.execution.failed イベント
 * - Raw:       該当 session の全 event を JSON 折りたたみで表示
 *
 * `recentEvents` (SSE で流れてくる agent.* イベント) も合わせて表示する
 * (実行中の session は live 更新される).
 *
 * Phase D6 — Tool call の args / output / error を `<ToolCallJson>` で
 * 完全 JSON 表示。長い場合は 1000 文字超で `[Show all]` ボタンに切り替え
 * (instruction.md §7, §8).
 */

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchAgentSession,
  type AgentSessionChainItem,
  type AgentSessionDetail,
} from "../api/client";
import type { UiEvent } from "../types";
import { ToolCallJson } from "../components/ToolCallJson";
import { asRecord, asRecords, text, time } from "./PageSupport";
import { eventAgentSessionId, eventTraceIds, summarizeTokenUsage } from "../displayModel";

type TabId = "overview" | "chain" | "thinking" | "tools" | "mcp" | "files" | "terminal" | "approvals" | "errors" | "raw";

const TABS: Array<{ id: TabId; label: string; description: string }> = [
  { id: "overview", label: "Overview", description: "セッション概要 (task / status / event count)" },
  { id: "chain", label: "Chain", description: "trace / parent_id ベースの因果連鎖" },
  { id: "thinking", label: "Thinking", description: "agent.thinking イベントのテキスト列" },
  { id: "tools", label: "Tools", description: "Tool call 一覧" },
  { id: "mcp", label: "MCP", description: "MCP server 呼び出し" },
  { id: "files", label: "Files", description: "ファイル操作イベント" },
  { id: "terminal", label: "Terminal", description: "ターミナルコマンド実行" },
  { id: "approvals", label: "Approvals", description: "承認要求履歴" },
  { id: "errors", label: "Errors", description: "失敗 / 例外" },
  { id: "raw", label: "Raw", description: "全 event (JSON 折りたたみ)" },
];

const KIND_FOR_TAB: Record<TabId, string[]> = {
  overview: [],
  chain: [],
  thinking: ["agent.thinking"],
  tools: ["agent.tool.started", "agent.tool.completed", "tool.execution.started", "tool.execution.completed"],
  // Phase D5 — MCP / Approvals tabs に `policy.decision` も表示.
  // tool call → policy → approval → result の流れを 1 画面で可視化.
  mcp: ["agent.tool.started", "agent.tool.completed", "tool.execution.started", "tool.execution.completed", "policy.decision"],
  files: ["agent.tool.started", "agent.tool.completed", "tool.execution.started", "tool.execution.completed"],
  terminal: ["agent.tool.started", "agent.tool.completed", "tool.execution.started", "tool.execution.completed"],
  approvals: ["approval.created", "approval.approved", "approval.rejected", "approval.expired", "approval.cancelled", "agent.waiting", "policy.decision"],
  errors: ["agent.failed", "tool.execution.failed", "approval.failed"],
  raw: [],
};

const TOOL_PREFIX_FOR_TAB: Partial<Record<TabId, string>> = {
  mcp: "mcp.",
  files: "file.",
  terminal: "terminal.",
};

export function AgentSessionPage({
  agentSessionId,
  recentEvents,
  onNavigate,
}: {
  agentSessionId: string;
  recentEvents: UiEvent[];
  onNavigate: (path: string) => void;
}) {
  const [tab, setTab] = useState<TabId>("overview");
  const sessionQuery = useQuery({
    queryKey: ["agent-session", agentSessionId],
    queryFn: () => fetchAgentSession(agentSessionId, 500),
    enabled: Boolean(agentSessionId),
    refetchInterval: 15_000,
  });

  // SSE の recentEvents (該当 session の agent.* のみ) をマージ
  const liveSessionEvents = useMemo(() => {
    if (!agentSessionId) return [];
    return recentEvents.filter((event) => {
      const sid = eventAgentSessionId(event) || event.agent_session_id || event.payload?.agent_session_id;
      return sid === agentSessionId;
    });
  }, [recentEvents, agentSessionId]);

  const detail = sessionQuery.data;
  const found = detail?.found === true;
  const summary = detail?.summary;
  const persistedEvents = detail?.events ?? [];
  const chainItems = detail?.causal_chain?.length ? detail.causal_chain : buildChainItems(persistedEvents);

  // active tab に該当する events を computed
  const tabEvents = useMemo(() => {
    if (tab === "overview" || tab === "chain") return [];
    if (tab === "raw") return persistedEvents;
    const allowedKinds = new Set(KIND_FOR_TAB[tab] || []);
    const toolPrefix = TOOL_PREFIX_FOR_TAB[tab];
    return persistedEvents.filter((event) => {
      const kind = String(event.type || event.event_type || "");
      if (!allowedKinds.has(kind)) return false;
      if (toolPrefix) {
        const payload = asRecord(event.payload);
        // tool フィールド (agent.tool.*) または capability_id (policy.decision) で判定
        const tool = String(payload.tool || payload.capability_id || "");
        return tool.startsWith(toolPrefix);
      }
      return true;
    });
  }, [tab, persistedEvents]);

  return (
    <div className="grid agent-session-page">
      <header className="agent-session-page__header">
        <div>
          <span className="muted">Agent Session</span>
          <h1>{agentSessionId || "(no id)"}</h1>
          {summary?.task_id ? (
            <p className="muted">
              Task: <code>{summary.task_id}</code> · Status: <strong>{summary.status}</strong> · {summary.event_count} events
            </p>
          ) : null}
        </div>
        <button
          type="button"
          className="icon-button"
          onClick={() => onNavigate("/dashboard/operations")}
        >
          ← 一覧へ
        </button>
      </header>

      {sessionQuery.isLoading ? (
        <p className="muted">Loading agent session…</p>
      ) : !found ? (
        <section className="panel">
          <h2>Not Found</h2>
          <p className="muted">Agent session <code>{agentSessionId}</code> が見つかりません。Task 実行中ならこの ID は Live Overlay から取得できます。</p>
        </section>
      ) : (
        <>
          <nav className="agent-session-page__tabs" aria-label="Agent session tabs">
            {TABS.map((t) => (
              <button
                type="button"
                key={t.id}
                className="agent-session-page__tab"
                data-active={tab === t.id}
                onClick={() => setTab(t.id)}
                title={t.description}
              >
                {t.label}
              </button>
            ))}
          </nav>

          {tab === "overview" ? (
            <OverviewTab summary={summary} liveEvents={liveSessionEvents} detail={detail} chainItems={chainItems} />
          ) : tab === "chain" ? (
            <ChainTab chainItems={chainItems} />
          ) : tab === "raw" ? (
            <RawTab events={tabEvents} />
          ) : (
            <EventsTab
              tabId={tab}
              events={tabEvents}
              emptyMessage={`${TABS.find((t) => t.id === tab)?.label} イベントはありません`}
            />
          )}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tab components
// ---------------------------------------------------------------------------

function OverviewTab({
  summary,
  liveEvents,
  detail,
  chainItems,
}: {
  summary: AgentSessionDetail["summary"] | undefined;
  liveEvents: UiEvent[];
  detail: AgentSessionDetail | undefined;
  chainItems: AgentSessionChainItem[];
}) {
  if (!summary) return <p className="muted">セッション summary を取得できませんでした。</p>;
  const kindsCount = (summary.kinds || []).length;
  const durationMs = summary.last_event_ms - summary.first_event_ms;
  const causal = useMemo(() => summarizeCausalSignals(chainItems, summary), [chainItems, summary]);
  return (
    <div className="grid grid--two">
      <section className="panel">
        <h2>サマリ</h2>
        <dl className="metric-list">
          <div className="metric-row"><span>agent_session_id</span><strong><code>{summary.agent_session_id}</code></strong></div>
          <div className="metric-row"><span>task_id</span><strong>{text(summary.task_id, "(unknown)")}</strong></div>
          <div className="metric-row"><span>status</span><strong>{summary.status}</strong></div>
          <div className="metric-row"><span>event count</span><strong>{summary.event_count}</strong></div>
          <div className="metric-row"><span>duration</span><strong>{durationMs > 0 ? `${(durationMs / 1000).toFixed(1)}s` : "—"}</strong></div>
          <div className="metric-row"><span>first event</span><strong>{time(summary.first_event_ms)}</strong></div>
          <div className="metric-row"><span>last event</span><strong>{time(summary.last_event_ms)}</strong></div>
        </dl>
      </section>
      <section className="panel">
        <h2>Kind 一覧 ({kindsCount})</h2>
        {summary.kinds && summary.kinds.length ? (
          <ul className="compact-list">
            {summary.kinds.map((kind) => (
              <li key={kind}><code>{kind}</code></li>
            ))}
          </ul>
        ) : (
          <p className="muted">Kind なし</p>
        )}
      </section>
      {summary.summary ? (
        <section className="panel">
          <h2>完了 summary</h2>
          <p>{summary.summary}</p>
        </section>
      ) : null}
      {/* Phase D5 — Policy / Approval 集計 */}
      <section className="panel">
        <h2>Policy / Approval</h2>
        <dl className="metric-list">
          <div className="metric-row"><span>policy allow</span><strong>{summary.policy_allow_count ?? 0}</strong></div>
          <div className="metric-row"><span>policy ask</span><strong>{summary.policy_ask_count ?? 0}</strong></div>
          <div className="metric-row"><span>policy deny</span><strong>{summary.policy_deny_count ?? 0}</strong></div>
          <div className="metric-row"><span>highest risk</span><strong><code>{text(summary.highest_risk, "—")}</code></strong></div>
          <div className="metric-row"><span>approval count</span><strong>{summary.approval_count ?? 0}</strong></div>
          <div className="metric-row"><span>pending approval</span><strong>{summary.pending_approval ? "YES" : "no"}</strong></div>
        </dl>
      </section>
      <section className="panel">
        <h2>Causal Summary</h2>
        <dl className="metric-list">
          <div className="metric-row"><span>trace count</span><strong>{causal.traceCount}</strong></div>
          <div className="metric-row"><span>root events</span><strong>{causal.rootCount}</strong></div>
          <div className="metric-row"><span>milestones</span><strong>{summary.milestones?.length ?? 0}</strong></div>
          <div className="metric-row"><span>root cause</span><strong>{text(causal.rootCause, "—")}</strong></div>
          <div className="metric-row"><span>category</span><strong>{text(summary.root_cause?.category, "—")}</strong></div>
        </dl>
        {causal.summary ? <p>{causal.summary}</p> : <p className="muted">因果サマリはまだありません。</p>}
        {summary.milestones && summary.milestones.length ? (
          <ul className="compact-list">
            {summary.milestones.map((milestone) => (
              <li key={milestone.key}>
                <code>{milestone.label}</code> <span className="muted">{time(milestone.timestamp_ms)}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </section>
      {/* Phase D9 — Token / Cost (§25) */}
      <TokenCostPanel events={detail?.events || liveEvents} />
      <section className="panel">
        <h2>Live (SSE 受信中)</h2>
        {liveEvents.length ? (
          <ul className="compact-list">
            {liveEvents.slice(0, 8).map((event) => {
              const payload = asRecord(event.payload);
              const liveText = text(payload.text || payload.summary || "", "");
              return (
                <li key={String(event.event_id || event.payload?.event_id || Math.random())}>
                  <code>{String(event.type || event.source_type || "event")}</code>{" "}
                  <span className="muted">{time(event.generated_at || event.source_updated_at)}</span>
                  {liveText ? <p>{liveText}</p> : null}
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="muted">SSE でこの session のイベントは受信していません。</p>
        )}
      </section>
      {detail?.events && detail.events.length > 0 ? (
        <section className="panel">
          <h2>最新 5 event</h2>
          <ul className="compact-list">
            {detail.events.slice(-5).reverse().map((event) => {
              const payload = asRecord(event.payload);
              return (
                <li key={String(payload.event_id || event.event_id || Math.random())}>
                  <code>{text(event.type, "event")}</code>{" "}
                  <span className="muted">{time(payload.occurred_at_ms || event.timestamp)}</span>{" "}
                  {payload.state ? <em>({text(payload.state)})</em> : null}
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

function ChainTab({ chainItems }: { chainItems: AgentSessionChainItem[] }) {
  if (!chainItems.length) {
    return <section className="panel"><p className="muted">この session の因果チェーン情報はありません。</p></section>;
  }
  return (
    <section className="panel">
      <h2>Trace / Parent Chain ({chainItems.length})</h2>
      <ol className="causal-chain">
        {chainItems.map((item) => (
          <li key={item.key} data-status={item.status || "unknown"} style={{ marginLeft: `${Math.min(item.depth, 4) * 16}px` }}>
            <strong><code>{item.kind}</code></strong>{" "}
            <span className="muted">{time(item.timestamp_ms)}</span>{" "}
            {item.trace_id ? <small>trace=<code>{item.trace_id}</code></small> : null}{" "}
            {item.parent_id ? <small>parent=<code>{item.parent_id}</code></small> : null}
            {item.summary ? <div>{item.summary}</div> : null}
          </li>
        ))}
      </ol>
    </section>
  );
}

/**
 * Phase D9 (§25) — Token / Cost サマリパネル.
 *
 * events の payload から token_usage / cost / model 情報を集計し表示する。
 * 0 件 (情報なし) のときは "—" を表示し、event_count を控えめに添える。
 */
function TokenCostPanel({ events }: { events: Array<Record<string, unknown>> }) {
  const uiEvents = events as unknown as UiEvent[];
  const usage = useMemo(() => summarizeTokenUsage(uiEvents), [uiEvents]);
  const hasData = usage.event_count > 0;
  const fmt = (n: number) => n.toLocaleString("en-US");
  return (
    <section className="panel" data-testid="token-cost-panel">
      <h2>Token / Cost (§25)</h2>
      {hasData ? (
        <dl className="metric-list">
          <div className="metric-row"><span>Model</span><strong><code>{text(usage.model, "—")}</code></strong></div>
          <div className="metric-row"><span>Input tokens</span><strong data-testid="token-input">{fmt(usage.input_tokens)}</strong></div>
          <div className="metric-row"><span>Output tokens</span><strong data-testid="token-output">{fmt(usage.output_tokens)}</strong></div>
          <div className="metric-row"><span>Cached tokens</span><strong data-testid="token-cached">{fmt(usage.cached_tokens)}</strong></div>
          <div className="metric-row"><span>Duration</span><strong>—</strong></div>
          <div className="metric-row"><span>Estimated cost (USD)</span><strong data-testid="token-cost">${usage.estimated_cost_usd.toFixed(4)}</strong></div>
          <div className="metric-row"><span>events with token info</span><strong>{usage.event_count}</strong></div>
        </dl>
      ) : (
        <p className="muted">この session には token / cost 情報を含む event がありません。</p>
      )}
    </section>
  );
}

function EventsTab({
  tabId,
  events,
  emptyMessage,
}: {
  tabId: TabId;
  events: Array<Record<string, unknown>>;
  emptyMessage: string;
}) {
  if (!events.length) {
    return <section className="panel"><p className="muted">{emptyMessage}</p></section>;
  }
  return (
    <section className="panel">
      <h2>{TABS.find((t) => t.id === tabId)?.label} ({events.length})</h2>
      <ul className="compact-list">
        {events.map((event, idx) => {
          const payload = asRecord(event.payload);
          const kind = text(event.type, "event");
          // Phase D6 — tool call (agent.tool.* / tool.execution.*) は
          // args / output / error を `<ToolCallJson>` で完全 JSON 表示する。
          const isToolCall =
            kind === "agent.tool.started" ||
            kind === "agent.tool.completed" ||
            kind === "tool.execution.started" ||
            kind === "tool.execution.completed";
          // tool call 以外 (approval.* / agent.waiting / policy.decision / agent.failed 等) は
          // 既存の text プレビュー (text/summary/error/command/output の最初の 1 つ) を表示.
          const text_field = isToolCall
            ? ""
            : text(payload.text || payload.summary || payload.error || payload.command || payload.output || "", "");
          const extra_label = text(payload.approval_id, "");
          const trace = eventTraceIds({ payload });
          // Phase D5 — policy.decision は decision / risk_level / capability_id を強調表示
          const isPolicy = kind === "policy.decision";
          const decision = text(payload.decision, "");
          const risk = text(payload.risk_level, "");
          const cap = text(payload.capability_id, "");
          // Phase D6 — tool call の ok / duration
          const toolOk = payload.ok;
          const toolDuration = payload.duration_ms;
          return (
            <li key={String(payload.event_id || event.event_id || idx)} className="event-row">
              <div>
                <strong><code>{kind}</code></strong>{" "}
                <span className="muted">{time(payload.occurred_at_ms || event.timestamp)}</span>{" "}
                {isPolicy ? (
                  <>
                    <em>decision=<code>{decision}</code></em>{" "}
                    <em>risk=<code>{risk}</code></em>{" "}
                    <em>capability=<code>{cap}</code></em>{" "}
                  </>
                ) : (
                  <>
                    {payload.tool ? <em>tool=<code>{text(payload.tool)}</code></em> : null}{" "}
                  </>
                )}
                {payload.state ? <em>({text(payload.state)})</em> : null}{" "}
                {isToolCall && toolOk === false ? <em className="tool-call-failed">(failed)</em> : null}
                {isToolCall && typeof toolOk === "boolean" && toolOk ? <em className="tool-call-ok">(ok)</em> : null}
                {isToolCall && toolDuration ? <em>duration=<code>{String(toolDuration)}</code>ms</em> : null}
                {extra_label ? <em>id=<code>{extra_label}</code></em> : null}
                {trace.trace_id ? <em>trace=<code>{trace.trace_id}</code></em> : null}
                {trace.parent_id ? <em>parent=<code>{trace.parent_id}</code></em> : null}
                {trace.activity_id ? <em>activity=<code>{trace.activity_id}</code></em> : null}
              </div>
              {text_field ? <p>{text_field}</p> : null}
              {/* Phase D6 — tool call の args / output / error を `<ToolCallJson>` で表示 */}
              {isToolCall ? (
                <div className="tool-call-json-group">
                  {kind === "agent.tool.started" || kind === "tool.execution.started" ? (
                    <ToolCallJson label="args" value={payload.args} />
                  ) : null}
                  {kind === "agent.tool.completed" || kind === "tool.execution.completed" ? (
                    <>
                      <ToolCallJson label="output" value={payload.output} />
                      {payload.error ? <ToolCallJson label="error" value={payload.error} /> : null}
                    </>
                  ) : null}
                </div>
              ) : null}
            </li>
          );
        })}
      </ul>
    </section>
  );
}

function RawTab({ events }: { events: Array<Record<string, unknown>> }) {
  if (!events.length) {
    return <section className="panel"><p className="muted">この session に紐づく event はありません。</p></section>;
  }
  return (
    <section className="panel">
      <h2>Raw events ({events.length})</h2>
      <ul className="compact-list">
        {events.map((event, idx) => {
          const payload = asRecord(event.payload);
          const eid = text(payload.event_id || event.event_id, `event-${idx}`);
          const trace = eventTraceIds({ payload });
          return (
            <li key={eid}>
              <details>
                <summary>
                  <code>{text(event.type, "event")}</code>{" "}
                  <span className="muted">{time(payload.occurred_at_ms || event.timestamp)}</span>{" "}
                  <em>event_id=<code>{eid}</code></em>
                  {trace.trace_id ? <em> trace=<code>{trace.trace_id}</code></em> : null}
                </summary>
                <pre className="raw-json">{JSON.stringify(event, null, 2)}</pre>
              </details>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

type ChainItem = {
  key: string;
  kind: string;
  timestamp_ms: number;
  summary: string;
  parent_id: string;
  trace_id: string;
  activity_id: string;
  status: string;
  depth: number;
};

function buildChainItems(events: Array<Record<string, unknown>>): ChainItem[] {
  const normalized = events.map((event, index) => {
    const payload = asRecord(event.payload);
    const trace = eventTraceIds({ payload });
    const key = String(payload.event_id || event.event_id || `event-${index}`);
    return {
      key,
      kind: text(event.type, "event"),
      timestamp_ms: Number(payload.occurred_at_ms || event.timestamp || 0),
      summary: text(payload.summary || payload.text || payload.error || payload.reason || payload.tool || payload.capability_id || "", ""),
      parent_id: trace.parent_id,
      trace_id: trace.trace_id,
      activity_id: trace.activity_id,
      status: text(payload.state || payload.status || event.type, ""),
    };
  });
  const parentMap = new Map(normalized.map((item) => [item.key, item]));
  return normalized
    .sort((a, b) => a.timestamp_ms - b.timestamp_ms)
    .map((item) => ({
      ...item,
      depth: computeDepth(item, parentMap),
    }));
}

function computeDepth(
  item: { parent_id: string; key: string },
  parentMap: Map<string, { parent_id: string; key: string }>,
): number {
  let depth = 0;
  let currentParent = item.parent_id;
  const seen = new Set<string>();
  while (currentParent && parentMap.has(currentParent) && !seen.has(currentParent) && depth < 8) {
    seen.add(currentParent);
    depth += 1;
    currentParent = parentMap.get(currentParent)?.parent_id || "";
  }
  return depth;
}

function summarizeCausalSignals(
  items: AgentSessionChainItem[],
  summary?: AgentSessionDetail["summary"],
) {
  const traceCount = new Set(items.map((item) => item.trace_id).filter(Boolean)).size;
  const rootCount = items.filter((item) => !item.parent_id).length;
  const rootCause = summary?.root_cause;
  const fallbackBlocking = [...items]
    .reverse()
    .find((item) => item.kind === "agent.waiting" || item.kind.startsWith("approval.") || item.kind.includes("failed"));
  return {
    traceCount,
    rootCount,
    rootCause: rootCause
      ? `${rootCause.kind}${rootCause.summary ? `: ${rootCause.summary}` : ""}`
      : fallbackBlocking
        ? `${fallbackBlocking.kind}${fallbackBlocking.summary ? `: ${fallbackBlocking.summary}` : ""}`
        : "",
    summary:
      summary?.causal_summary ||
      (fallbackBlocking
        ? `現在の注目点は ${fallbackBlocking.kind}${fallbackBlocking.summary ? `: ${fallbackBlocking.summary}` : ""} です。`
        : items.length
          ? `${traceCount || 1} trace にまたがる ${items.length} event を確認できます。`
          : ""),
  };
}
