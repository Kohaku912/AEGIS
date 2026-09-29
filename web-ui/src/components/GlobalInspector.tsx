import { ExternalLink, Pin, PinOff, ShieldAlert, X } from "lucide-react";
import { primaryFacts } from "../entityDetail";
import type { EntitySummary } from "../types";

export function GlobalInspector({
  entity,
  onClose,
  onFollowRelation,
  onNavigate,
  pinned = false,
  onTogglePin,
  developerMode = false,
}: {
  entity?: EntitySummary;
  onClose: () => void;
  onFollowRelation?: (type: string, id: string) => void;
  onNavigate?: (path: string) => void;
  pinned?: boolean;
  onTogglePin?: (entity: EntitySummary) => void;
  developerMode?: boolean;
}) {
  const facts = primaryFacts(entity, 14).filter((fact) => !String(fact.value).includes("Not reported"));
  const jumpTargets = entity ? recommendedJumps(entity) : [];
  return (
    <aside className="global-inspector" data-open={Boolean(entity)} aria-label="Global inspector">
      <header>
        <div>
          <span>Inspector</span>
          <strong>{entity?.type || "No selection"}</strong>
        </div>
        <div>
          {entity ? (
            <button
              className="icon-button"
              type="button"
              aria-pressed={pinned}
              onClick={() => onTogglePin?.(entity)}
              title={pinned ? "Remove from Command Center" : "Pin to Command Center"}
            >
              {pinned ? <PinOff size={16} /> : <Pin size={16} />}
            </button>
          ) : null}
          <button className="icon-button" type="button" onClick={onClose} title="Close inspector">
            <X size={16} />
          </button>
        </div>
      </header>
      {entity ? (
        <div className="global-inspector__body">
          <div className="entity-identity" data-severity={entity.severity}>
            <span>{entity.status}</span>
            <h2>{entity.title}</h2>
            <p>{entity.subtitle}</p>
          </div>
          <dl className="inspector-facts">
            {facts.map((fact) => (
              <div key={fact.label}>
                <dt>{fact.label}</dt>
                <dd>{fact.value}</dd>
              </div>
            ))}
          </dl>
          {entity.tags.length ? (
            <section>
              <h3>Tags</h3>
              <div className="relation-list">
                {entity.tags.map((tag) => <span key={tag}>{tag}</span>)}
              </div>
            </section>
          ) : null}
          <section>
            <h3>Why important</h3>
            <p>{entityImportance(entity)}</p>
          </section>
          {jumpTargets.length ? (
            <section>
              <h3>Recommended jumps</h3>
              <div className="relation-list">
                {jumpTargets.map((target) => (
                  <button type="button" onClick={() => onNavigate?.(target.path)} key={target.path}>
                    <ExternalLink size={13} />
                    {target.label}
                  </button>
                ))}
              </div>
            </section>
          ) : null}
          <section>
            <h3>Relations</h3>
            <div className="relation-list">
              {entity.relations.map((relation) => (
                <button type="button" onClick={() => onFollowRelation?.(relation.type, relation.id)} key={`${relation.type}:${relation.id}`}>
                  <ExternalLink size={13} />
                  {relation.type}: {relation.label || relation.id}
                </button>
              ))}
              {!entity.relations.length ? <p>No related resources reported.</p> : null}
            </div>
          </section>
          <section>
            <h3>Available actions</h3>
            <div className="inspector-actions">
              {entity.available_actions.map((action) => (
                <button className={action.level === "dangerous" ? "danger-button" : "secondary-button"} type="button" key={action.id}>
                  <ShieldAlert size={14} />
                  {action.label}
                </button>
              ))}
            </div>
            <p className="muted">Controlled and dangerous actions open a preview and never execute directly from the inspector.</p>
          </section>
          {developerMode ? (
            <details className="developer-only" open>
              <summary>Developer data</summary>
              <pre>{JSON.stringify(entity.data, null, 2)}</pre>
            </details>
          ) : null}
        </div>
      ) : (
        <p className="global-inspector__empty">Select any task, server, event, approval, or search result.</p>
      )}
    </aside>
  );
}

function entityImportance(entity?: EntitySummary): string {
  if (!entity) return "Select any task, server, event, approval, or search result.";
  if (entity.severity === "warning" || /fail|error|offline|denied/i.test(entity.status)) {
    return "この項目は失敗・停止・要対応の兆候を持つため、まず原因追跡の起点として扱います。";
  }
  if (entity.type === "approval") {
    return "承認待ちは AEGIS の進行を直接止めるため、放置コストが高い対象です。";
  }
  if (entity.type === "task" || entity.type === "operation") {
    return "現在の実行文脈に近いため、trace と raw activity の両方を確認する価値があります。";
  }
  if (entity.type === "server") {
    return "サーバー状態は複数 task / capability に波及するため、まず健康状態と最近の異常を確認します。";
  }
  return "関連 relation と action から、次に掘るべき画面へそのまま移動できます。";
}

function recommendedJumps(entity: EntitySummary): Array<{ label: string; path: string }> {
  const data = entity.data || {};
  const paths = new Map<string, string>();
  if (entity.type === "approval") paths.set("Open approvals", "/dashboard/approvals");
  if (entity.type === "server") paths.set("Open systems", "/dashboard/systems");
  if (entity.type === "task" || entity.type === "operation") paths.set("Open execution trace", "/dashboard/execution-trace");
  if (typeof data.agent_session_id === "string" && data.agent_session_id) {
    paths.set("Open agent session", `/dashboard/agent-sessions/${encodeURIComponent(data.agent_session_id)}`);
  }
  if (typeof data.operation_id === "string" && data.operation_id) {
    paths.set("Open operation", `/dashboard/operations/${encodeURIComponent(data.operation_id)}`);
  }
  if (typeof data.task_id === "string" && data.task_id) {
    paths.set("Open tasks", "/dashboard/work/tasks");
  }
  if (typeof data.approval_id === "string" && data.approval_id) {
    paths.set("Open approvals", "/dashboard/approvals");
  }
  paths.set("Open raw activity", "/dashboard/activity");
  return [...paths.entries()].map(([label, path]) => ({ label, path }));
}
