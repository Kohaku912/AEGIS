import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
};

export function SocialPage({ overview, developerMode = false }: Props) {
  const social = overview.social?.data || {};
  const pending = (social.pending_decisions || []) as Array<Record<string, unknown>>;
  const decided = (social.decided || []) as Array<Record<string, unknown>>;
  const agora = (social.agora || {}) as Record<string, unknown>;
  const counts = (agora.counts || {}) as Record<string, number>;

  return (
    <div className="judgment-page">
      <header className="judgment-page__hero">
        <div>
          <span>Communications</span>
          <h2>Social inbox & AGORA decisions</h2>
          <p>{String(social.summary || "See which social items AEGIS decided to answer, skip, or still needs to judge.")}</p>
        </div>
        <Freshness
          generatedAt={overview.social?.generated_at || 0}
          sourceUpdatedAt={overview.social?.source_updated_at || 0}
          stale={Boolean(overview.social?.stale)}
        />
      </header>

      <section className="judgment-chips">
        {Object.entries(counts).map(([key, value]) => (
          <span key={key} className="chip-static">{key}: {value}</span>
        ))}
        <span className="chip-static">pending: {Number(agora.pending_count || pending.length)}</span>
      </section>

      <div className="judgment-grid">
        <article className="panel">
          <div className="panel__header"><h2>Awaiting decision</h2></div>
          {pending.length === 0 ? (
            <p className="empty-copy">No social items waiting for a judgment.</p>
          ) : (
            pending.map((item) => (
              <div className="goal-card" key={String(item.item_id)}>
                <StatusBadge status={String(item.status || "pending")} />
                <strong>{String(item.channel || "social")}</strong>
                <p>{String(item.body || item.summary || item.body_preview || "").slice(0, 200)}</p>
                {item.decision_reason ? <small>{String(item.decision_reason)}</small> : null}
              </div>
            ))
          )}
        </article>
        <article className="panel">
          <div className="panel__header"><h2>Recent decisions</h2></div>
          {decided.length === 0 ? (
            <p className="empty-copy">No decided social items yet.</p>
          ) : (
            decided.slice(0, 12).map((item) => (
              <div className="goal-card" key={String(item.item_id)}>
                <StatusBadge status={String(item.status || "decided")} />
                <strong>{String(item.channel || "social")}</strong>
                <p>{String(item.body_preview || "").slice(0, 160)}</p>
                <small>{String(item.decision_reason || "Decision recorded")}</small>
              </div>
            ))
          )}
          {developerMode ? <pre className="developer-raw">{JSON.stringify(social.status || {}, null, 2)}</pre> : null}
        </article>
      </div>
    </div>
  );
}
