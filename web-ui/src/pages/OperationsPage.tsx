import { useEffect, useMemo, useState } from "react";
import { fetchOperation, fetchOperations } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";

type ChainStage = {
  stage?: string;
  label?: string;
  summary?: string;
  status?: string;
  detail?: string;
};

export type Operation = {
  operation_id?: string;
  kind?: string;
  kind_label?: string;
  source?: string;
  title?: string;
  action_summary?: string;
  summary?: string;
  what_happened?: string;
  narrative?: string;
  purpose?: string;
  decision_reason?: string;
  result_summary?: string;
  target?: string;
  target_summary?: string;
  status?: string;
  result_status?: string;
  priority?: string;
  goal_status?: string;
  verification_status?: string;
  next_action?: string;
  wait_reason?: string;
  skip_reason?: string;
  started_at?: number;
  updated_at?: number;
  duration_ms?: number;
  tool_count?: number;
  error_count?: number;
  steps?: Array<Record<string, unknown>>;
  causal_chain?: ChainStage[];
  linked_entity_ids?: Record<string, string[] | string>;
  trigger?: Record<string, unknown>;
  perceived?: string[];
  candidates?: string[];
  goal?: string;
  verification?: Record<string, unknown>;
  presentation?: Record<string, unknown>;
  follow_up?: Record<string, unknown>;
  learning?: Record<string, unknown>;
  changed_state?: string;
};

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
  detailId?: string;
  pathname?: string;
  onNavigate?: (path: string) => void;
};

const RESULT_LABELS: Record<string, string> = {
  success: "成功",
  partial: "部分成功",
  failed: "失敗",
  awaiting_approval: "承認待ち",
  non_action: "非行動",
  recorded: "記録済み",
};

const GOAL_LABELS: Record<string, string> = {
  achieved: "達成",
  unmet: "未達",
  in_progress: "進行中",
  not_applicable: "該当なし",
  unknown: "不明",
};

function formatDuration(ms?: number): string {
  if (!ms || ms <= 0) return "—";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.round(ms / 60_000)}m`;
}

function sourceLabel(op: Operation): string {
  const source = String(op.source || "");
  if (source === "user" || op.kind === "chat") return "ユーザー指示";
  if (source === "schedule" || op.kind === "schedule") return "Schedule";
  if (source === "event" || op.kind === "event") return "イベント";
  if (source === "autonomous" || op.kind === "autonomous") return "自律判断";
  return String(op.kind_label || op.kind || "操作");
}

export function actionTitle(op: Operation): string {
  const text = String(
    op.action_summary || op.what_happened || op.narrative || op.result_summary || op.title || "",
  ).trim();
  if (!text) return "内容未記録の操作";
  const banned = /^(自律実行|autonomous(\s+(run|cycle))?|system|chat|task)$/i;
  if (banned.test(text)) return String(op.result_summary || op.purpose || "観測結果あり");
  return text;
}

function linkedList(op: Operation, key: string): string[] {
  const raw = op.linked_entity_ids?.[key];
  if (Array.isArray(raw)) return raw.map(String).filter(Boolean);
  if (raw) return [String(raw)];
  return [];
}

export function OperationsPage({ overview, developerMode = false, detailId = "", pathname = "", onNavigate }: Props) {
  const activity = overview.activity;
  const overviewOps = (activity?.data.operations || []) as Operation[];
  const [remoteOps, setRemoteOps] = useState<Operation[]>([]);
  const routeDetailId =
    detailId
    || (() => {
      const path = pathname || (typeof window !== "undefined" ? window.location.pathname : "");
      const match = path.match(/^\/dashboard\/operations\/([^/]+)$/);
      return match?.[1] ? decodeURIComponent(match[1]) : "";
    })();
  const [selectedId, setSelectedId] = useState(routeDetailId);
  const [detail, setDetail] = useState<Operation | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    void fetchOperations(40)
      .then((items) => {
        if (!cancelled) setRemoteOps(items as Operation[]);
      })
      .catch((reason) => {
        if (!cancelled && !overviewOps.length) {
          setError(reason instanceof Error ? reason.message : String(reason));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [overview.generated_at]);

  useEffect(() => {
    if (routeDetailId) setSelectedId(routeDetailId);
  }, [routeDetailId]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    void fetchOperation(selectedId)
      .then((item) => {
        if (!cancelled) setDetail(item as Operation);
      })
      .catch(() => {
        if (!cancelled) setDetail(null);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const operations = useMemo(() => {
    const byId = new Map<string, Operation>();
    for (const op of [...remoteOps, ...overviewOps]) {
      const id = String(op.operation_id || "");
      if (!id || byId.has(id)) continue;
      byId.set(id, op);
    }
    return [...byId.values()].sort(
      (a, b) => Number(b.updated_at || b.started_at || 0) - Number(a.updated_at || a.started_at || 0),
    );
  }, [overviewOps, remoteOps]);

  const selected =
    detail?.operation_id === selectedId
      ? detail
      : operations.find((item) => item.operation_id === selectedId) || operations[0];

  const selectOperation = (id: string) => {
    setSelectedId(id);
    onNavigate?.(`/dashboard/operations/${encodeURIComponent(id)}`);
  };

  return (
    <div className="judgment-page operations-page">
      <header className="judgment-page__hero">
        <div>
          <span>Operations</span>
          <h2>何に対して、何を行い、どうなったか</h2>
          <p>Trigger → 認識 → 判断 → 候補 → Goal → 実行 → Verification → Presentation → Follow-up → Learning</p>
        </div>
        <Freshness
          generatedAt={activity?.generated_at || 0}
          sourceUpdatedAt={activity?.source_updated_at || 0}
          stale={Boolean(activity?.stale)}
        />
      </header>

      {error ? <p className="warning-text">{error}</p> : null}

      <div className="judgment-split">
        <section className="panel">
          <div className="panel__header"><h2>実行履歴</h2></div>
          {operations.length === 0 ? (
            <p className="empty-copy">まだ Operation がありません。行動または意図的な非行動が記録されるとここに表示されます。</p>
          ) : (
            <ul className="operation-list">
              {operations.map((op) => {
                const id = String(op.operation_id || "");
                const result = String(op.result_status || op.status || "recorded");
                return (
                  <li key={id}>
                    <button
                      type="button"
                      data-selected={selected?.operation_id === id}
                      onClick={() => selectOperation(id)}
                    >
                      <div>
                        <div className="operation-list__title-row">
                          <strong>{actionTitle(op)}</strong>
                          <span className="kind-badge">{sourceLabel(op)}</span>
                        </div>
                        <p>
                          <span className="muted">対象:</span> {op.target_summary || op.target || "—"}
                          {" · "}
                          <span className="muted">Goal:</span> {GOAL_LABELS[String(op.goal_status || "unknown")] || op.goal_status || "—"}
                          {" · "}
                          <span className="muted">次:</span> {op.next_action || op.wait_reason || op.skip_reason || "—"}
                        </p>
                      </div>
                      <div className="operation-list__meta">
                        <StatusBadge status={RESULT_LABELS[result] || result} />
                        <small>
                          {op.updated_at || op.started_at
                            ? new Date(Number(op.updated_at || op.started_at)).toLocaleString()
                            : ""}
                        </small>
                        <small>{formatDuration(op.duration_ms)}</small>
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <aside className="panel judgment-detail">
          {selected ? (
            <OperationDetail
              operation={selected}
              developerMode={developerMode}
              onNavigate={onNavigate}
            />
          ) : (
            <p className="empty-copy">Operation を選択すると因果順の詳細を表示します。</p>
          )}
        </aside>
      </div>
    </div>
  );
}

function OperationDetail({
  operation,
  developerMode,
  onNavigate,
}: {
  operation: Operation;
  developerMode: boolean;
  onNavigate?: (path: string) => void;
}) {
  const result = String(operation.result_status || operation.status || "recorded");
  const chain = operation.causal_chain || [];
  const steps = operation.steps || [];
  const trigger = operation.trigger || {};
  const proposed = Array.isArray(trigger.proposed_candidates)
    ? (trigger.proposed_candidates as Array<Record<string, unknown>>)
    : [];
  const selected =
    trigger.selected_candidate && typeof trigger.selected_candidate === "object"
      ? (trigger.selected_candidate as Record<string, unknown>)
      : null;
  const maxPressure = Boolean(trigger.max_pressure_mode);
  const tasks = linkedList(operation, "task");
  const approvals = linkedList(operation, "approval");
  const repairs = linkedList(operation, "repair");
  const audits = linkedList(operation, "audit");
  const goals = linkedList(operation, "goal");

  return (
    <>
      <div className="panel__header">
        <h2>{actionTitle(operation)}</h2>
        <StatusBadge status={RESULT_LABELS[result] || result} />
      </div>
      <p className="human-summary">
        {operation.result_summary || operation.what_happened || operation.narrative || operation.summary}
      </p>
      <dl className="human-facts compact">
        <div><dt>行動元</dt><dd>{sourceLabel(operation)}</dd></div>
        <div><dt>対象</dt><dd>{operation.target_summary || operation.target || "—"}</dd></div>
        <div><dt>目的</dt><dd>{operation.purpose || operation.goal || "—"}</dd></div>
        <div><dt>判断理由</dt><dd>{operation.decision_reason || operation.wait_reason || operation.skip_reason || "—"}</dd></div>
        <div><dt>Goal</dt><dd>{GOAL_LABELS[String(operation.goal_status || "unknown")] || operation.goal_status}</dd></div>
        <div><dt>Verification</dt><dd>{operation.verification_status || "—"}</dd></div>
        <div><dt>変化した状態</dt><dd>{operation.changed_state || "—"}</dd></div>
        <div><dt>次の行動</dt><dd>{operation.next_action || operation.wait_reason || "—"}</dd></div>
        <div><dt>所要時間</dt><dd>{formatDuration(operation.duration_ms)}</dd></div>
      </dl>

      {maxPressure || selected || proposed.length ? (
        <section className="operation-steps">
          <div className="panel__header"><h3>二段階判断</h3></div>
          <dl className="human-facts compact">
            <div><dt>最大圧モード</dt><dd>{maxPressure ? "はい" : "いいえ"}</dd></div>
            <div>
              <dt>選択した候補</dt>
              <dd>
                {selected
                  ? String(selected.capability_id || selected.title || selected.action || JSON.stringify(selected))
                  : "—"}
              </dd>
            </div>
          </dl>
          {proposed.length ? (
            <ol>
              {proposed.map((candidate, index) => (
                <li key={`${operation.operation_id}-candidate-${index}`}>
                  {String(candidate.capability_id || candidate.title || candidate.action || `候補 ${index + 1}`)}
                  {candidate.reason ? <small>{String(candidate.reason)}</small> : null}
                </li>
              ))}
            </ol>
          ) : null}
        </section>
      ) : null}

      <ol className="causal-chain">
        {chain.map((stage) => (
          <li key={String(stage.stage)} data-status={stage.status || "missing"}>
            <strong>{stage.label || stage.stage}</strong>
            <span>{stage.summary || "—"}</span>
            {stage.detail ? <small>{stage.detail}</small> : null}
          </li>
        ))}
      </ol>

      {steps.length ? (
        <section className="operation-steps">
          <div className="panel__header"><h3>実行 Step</h3></div>
          <ol>
            {steps.map((step, index) => (
              <li key={`${operation.operation_id}-step-${index}`}>
                <strong>{String(step.action || step.capability_id || `Step ${index + 1}`)}</strong>
                <p>{String(step.output_summary || step.narrative || step.summary || "")}</p>
                <small>
                  対象: {String(step.target || "—")}
                  {" · "}Capability: {String(step.capability_id || "—")}
                  {" · "}状態: {String(step.status || "ok")}
                </small>
                {step.input_summary ? <small>入力: {String(step.input_summary)}</small> : null}
                {step.changed_state ? <small>変化: {String(step.changed_state)}</small> : null}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      <section className="operation-links">
        <div className="panel__header"><h3>関連</h3></div>
        <div className="operation-link-row">
          {tasks.map((id) => (
            <button key={id} type="button" className="secondary-button" onClick={() => onNavigate?.(`/dashboard/work/tasks`)}>
              Task {id.slice(0, 12)}
            </button>
          ))}
          {goals.map((id) => (
            <button key={id} type="button" className="secondary-button" onClick={() => onNavigate?.(`/dashboard/agent-state`)}>
              Goal {id.slice(0, 12)}
            </button>
          ))}
          {approvals.map((id) => (
            <button key={id} type="button" className="secondary-button" onClick={() => onNavigate?.(`/dashboard/approvals`)}>
              Approval {id.slice(0, 12)}
            </button>
          ))}
          {repairs.map((id) => (
            <button key={id} type="button" className="secondary-button" onClick={() => onNavigate?.(`/dashboard/incidents/${encodeURIComponent(id)}`)}>
              Repair {id.slice(0, 12)}
            </button>
          ))}
          {audits.map((id) => (
            <button key={id} type="button" className="secondary-button" onClick={() => onNavigate?.(`/dashboard/audit/${encodeURIComponent(id)}`)}>
              Audit {id.slice(0, 12)}
            </button>
          ))}
          {!tasks.length && !goals.length && !approvals.length && !repairs.length && !audits.length ? (
            <p className="muted">関連エンティティはまだリンクされていません。</p>
          ) : null}
        </div>
      </section>

      {developerMode ? (
        <pre className="developer-raw">{JSON.stringify(operation, null, 2)}</pre>
      ) : null}
    </>
  );
}
