import { ExternalLink, Pin, PinOff, ShieldAlert, X } from "lucide-react";
import { primaryFacts } from "../entityDetail";
import type { EntitySummary } from "../types";

export function GlobalInspector({
  entity,
  onClose,
  onFollowRelation,
  pinned = false,
  onTogglePin
}: {
  entity?: EntitySummary;
  onClose: () => void;
  onFollowRelation?: (type: string, id: string) => void;
  pinned?: boolean;
  onTogglePin?: (entity: EntitySummary) => void;
}) {
  const facts = primaryFacts(entity, 14);
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
          <details className="developer-only">
            <summary>Developer data</summary>
            <pre>{JSON.stringify(entity.data, null, 2)}</pre>
          </details>
        </div>
      ) : (
        <p className="global-inspector__empty">Select any task, server, event, approval, or search result.</p>
      )}
    </aside>
  );
}
