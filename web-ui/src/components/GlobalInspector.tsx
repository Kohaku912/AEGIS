import { ExternalLink, Pin, PinOff, ShieldAlert, X } from "lucide-react";
import type { EntitySummary } from "../types";

export function GlobalInspector({ entity, onClose, onFollowRelation, pinned = false, onTogglePin }: { entity?: EntitySummary; onClose: () => void; onFollowRelation?: (type: string, id: string) => void; pinned?: boolean; onTogglePin?: (entity: EntitySummary) => void }) {
  return (
    <aside className="global-inspector" data-open={Boolean(entity)} aria-label="Global inspector">
      <header>
        <div><span>Inspector</span><strong>{entity?.type || "No selection"}</strong></div>
        <div>{entity ? <button className="icon-button" type="button" aria-pressed={pinned} onClick={() => onTogglePin?.(entity)} title={pinned ? "Remove from Command Center" : "Pin to Command Center"}>{pinned ? <PinOff size={16} /> : <Pin size={16} />}</button> : null}<button className="icon-button" type="button" onClick={onClose} title="Close inspector"><X size={16} /></button></div>
      </header>
      {entity ? (
        <div className="global-inspector__body">
          <div className="entity-identity" data-severity={entity.severity}>
            <span>{entity.status}</span>
            <h2>{entity.title}</h2>
            <p>{entity.subtitle}</p>
          </div>
          <dl className="inspector-facts">
            <div><dt>Owner</dt><dd>{entity.owner || "AEGIS"}</dd></div>
            <div><dt>Updated</dt><dd>{entity.updated_at ? new Date(entity.updated_at).toLocaleString() : "No timestamp"}</dd></div>
            <div><dt>Permissions</dt><dd>{entity.permissions.join(", ") || "View"}</dd></div>
          </dl>
          <section>
            <h3>Relations</h3>
            <div className="relation-list">
              {entity.relations.map((relation) => <button type="button" onClick={() => onFollowRelation?.(relation.type, relation.id)} key={`${relation.type}:${relation.id}`}><ExternalLink size={13} />{relation.type}: {relation.label || relation.id}</button>)}
              {!entity.relations.length ? <p>No related resources reported.</p> : null}
            </div>
          </section>
          <section>
            <h3>Available actions</h3>
            <div className="inspector-actions">
              {entity.available_actions.map((action) => <button className={action.level === "dangerous" ? "danger-button" : "secondary-button"} type="button" key={action.id}><ShieldAlert size={14} />{action.label}</button>)}
            </div>
            <p className="muted">Controlled and dangerous actions open a preview and never execute directly from the inspector.</p>
          </section>
          <details className="developer-only"><summary>Developer data</summary><pre>{JSON.stringify(entity.data, null, 2)}</pre></details>
        </div>
      ) : <p className="global-inspector__empty">Select any task, server, event, approval, or search result.</p>}
    </aside>
  );
}
