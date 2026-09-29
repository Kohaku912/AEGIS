import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

export function ExecutionTracePage({
  overview,
  onNavigate,
}: {
  overview: UiOverview;
  onNavigate: (path: string) => void;
}) {
  const focus = overview.cockpit_focus?.data || {};
  const operations = overview.activity?.data.operations || [];
  const task = overview.current_task.data;
  const investigation = overview.cockpit_investigation?.data;
  const latestOperation = operations[0];
  const causalChain = normalizeCausalChain(latestOperation, focus, task, investigation);
  const workflow = Array.isArray(investigation?.workflow) && investigation.workflow.length
    ? investigation.workflow
    : ["observe", "activity", "session", "raw"];

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Execution Trace</h2>
            <div className="muted">実行中の流れ、直近の重要 operation、trace 画面への導線をまとめます。</div>
          </div>
          <Freshness
            generatedAt={overview.activity?.generated_at || overview.generated_at}
            sourceUpdatedAt={overview.activity?.source_updated_at || overview.generated_at}
            stale={Boolean(overview.activity?.stale)}
          />
        </div>
        <div className="home-summary-grid">
          <TraceCard
            title="Current focus"
            message={String(focus.title || task.title || "No current focus")}
            actionLabel="Open focus"
            onAction={() => onNavigate(String(focus.path || investigation?.focus_path || "/dashboard"))}
            badge={String(focus.kind || task.phase || "focus")}
          />
          <TraceCard
            title="Current task"
            message={task.current_action || task.next_action || task.title || "No active task"}
            actionLabel="Open tasks"
            onAction={() => onNavigate("/dashboard/work/tasks")}
            badge={task.phase || "idle"}
          />
          <TraceCard
            title="Agent timeline"
            message="Parallel sessions, abnormal traces, blocked runs"
            actionLabel="Open timeline"
            onAction={() => onNavigate("/dashboard/agent-timeline")}
            badge="trace"
          />
          <TraceCard
            title="Layer comparison"
            message="L1 / L2 / L3 bottleneck and route correlation"
            actionLabel="Open layers"
            onAction={() => onNavigate("/dashboard/layers")}
            badge="layers"
          />
        </div>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Causal rail</h2>
            <div className="muted">現在の focus から最新 operation、次の確認ポイントまでを 1 本のレールで追えます。</div>
          </div>
          <button className="secondary-button" type="button" onClick={() => onNavigate(String(investigation?.focus_path || "/dashboard/operations"))}>
            Inspect focus path
          </button>
        </div>
        <ol className="causal-chain execution-trace__chain">
          {causalChain.map((stage) => (
            <li key={stage.label} data-status={stage.status}>
              <strong>{stage.label}</strong>
              <span>{stage.summary}</span>
              {stage.detail ? <small>{stage.detail}</small> : null}
            </li>
          ))}
        </ol>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Investigate next</h2>
            <div className="muted">観測から session / layer まで同じ順序で深掘りできる導線です。</div>
          </div>
        </div>
        <div className="execution-trace__workflow" aria-label="Trace workflow">
          {workflow.map((step, index) => (
            <div className="execution-trace__workflow-step" key={`${step}-${index}`}>
              <span>{index + 1}</span>
              <strong>{String(step)}</strong>
            </div>
          ))}
        </div>
        <div className="command-controls">
          <button className="secondary-button" type="button" onClick={() => onNavigate(String(investigation?.paths?.home || "/dashboard"))}>
            Open cockpit
          </button>
          <button className="secondary-button" type="button" onClick={() => onNavigate(String(investigation?.paths?.operations || "/dashboard/operations"))}>
            Open operations
          </button>
          <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/agent-timeline")}>
            Open sessions
          </button>
          <button className="secondary-button" type="button" onClick={() => onNavigate(String(investigation?.paths?.layers || "/dashboard/layers"))}>
            Compare layers
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="panel__header">
          <h2>Recent meaningful operations</h2>
          <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/operations")}>
            Open operations
          </button>
        </div>
        <div className="timeline-list">
          {operations.length ? (
            operations.slice(0, 8).map((operation) => (
              <button
                className="timeline-item"
                data-priority={operation.priority}
                type="button"
                key={String(operation.operation_id || operation.title || operation.kind_label || "operation")}
                onClick={() =>
                  onNavigate(
                    operation.operation_id
                      ? `/dashboard/operations/${encodeURIComponent(String(operation.operation_id))}`
                      : "/dashboard/operations",
                  )
                }
              >
                <div>
                  <strong>{operation.title || operation.kind_label || "Operation"}</strong>
                  <div className="muted">
                    {operation.narrative || operation.what_happened || operation.summary || "Open operation details"}
                  </div>
                </div>
                <StatusBadge status={String(operation.status || operation.priority || "running")} />
              </button>
            ))
          ) : (
            <p className="muted">表示できる operation はまだありません。</p>
          )}
        </div>
      </section>
    </div>
  );
}

function normalizeCausalChain(
  operation: Record<string, unknown> | undefined,
  focus: Record<string, unknown>,
  task: UiOverview["current_task"]["data"],
  investigation:
    | {
        focus_path?: string;
        paths?: Record<string, string>;
        focus_links?: Record<string, unknown>;
        workflow?: string[];
      }
    | undefined,
) {
  const rawChain = Array.isArray(operation?.causal_chain) ? operation.causal_chain : [];
  if (rawChain.length) {
    return rawChain.map((entry, index) => {
      const item = typeof entry === "object" && entry ? entry as Record<string, unknown> : {};
      return {
        label: String(item.label || item.stage || `Step ${index + 1}`),
        summary: String(item.summary || item.message || "No summary"),
        detail: String(item.stage || ""),
        status: chainStatus(item.status),
      };
    });
  }
  return [
    {
      label: "Focus",
      summary: String(focus.title || task.title || "No active focus"),
      detail: String(focus.kind || task.phase || "focus"),
      status: "ok",
    },
    {
      label: "Task",
      summary: String(task.current_action || task.next_action || "No active task"),
      detail: String(task.capability_id || "No capability"),
      status: task.blocked_reason ? "pending" : "ok",
    },
    {
      label: "Operation",
      summary: String(operation?.title || operation?.summary || "No recent operation"),
      detail: String(operation?.status || "missing"),
      status: operation ? chainStatus(operation.status) : "missing",
    },
    {
      label: "Next jump",
      summary: String(investigation?.focus_path || "/dashboard/operations"),
      detail: "trace path",
      status: "ok",
    },
  ];
}

function chainStatus(value: unknown): string {
  const normalized = String(value || "").toLowerCase();
  if (["present", "ok", "passed", "success", "done", "complete", "completed"].includes(normalized)) return "ok";
  if (["pending", "waiting", "running", "blocked"].includes(normalized)) return "pending";
  if (["failed", "error", "skipped"].includes(normalized)) return "failed";
  if (["missing", "none", ""].includes(normalized)) return "missing";
  return normalized;
}

function TraceCard({
  title,
  message,
  actionLabel,
  onAction,
  badge,
}: {
  title: string;
  message: string;
  actionLabel: string;
  onAction: () => void;
  badge: string;
}) {
  return (
    <article className="panel">
      <div className="panel__header">
        <h2>{title}</h2>
        <StatusBadge status={badge} />
      </div>
      <p>{message}</p>
      <button className="secondary-button" type="button" onClick={onAction}>
        {actionLabel}
      </button>
    </article>
  );
}
