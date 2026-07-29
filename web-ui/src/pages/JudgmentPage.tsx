import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
  /** Narrow the page to one judgment facet when opened from nav. */
  focus?: "all" | "initiative" | "decision-context" | "goals" | "continuations" | "repairs" | "reports" | "situation";
};

export function JudgmentPage({ overview, developerMode = false, focus = "all" }: Props) {
  const initiative = overview.initiative?.data || {};
  const context = overview.decision_context?.data || overview.agent_state?.data || {};
  const goals = overview.goals?.data || {};
  const repairs = overview.repairs?.data || overview.errors?.data || {};
  const reports = overview.behavioral_reports?.data || {};
  const continuations = overview.continuations?.data || {};
  const situation = overview.situation?.data || overview.user_situation?.data || overview.user_state?.data || {};
  const nonActions = (initiative.recent_non_actions || []) as Array<Record<string, unknown>>;
  const openGoals = (goals.open || goals.items || []) as Array<Record<string, unknown>>;
  const repairItems = (repairs.items || []) as Array<Record<string, unknown>>;
  const continuationItems = (continuations.open || continuations.due || []) as Array<Record<string, unknown>>;
  const funnel = (initiative.funnel || {}) as Record<string, number>;
  const reasons = (initiative.no_action_reasons || {}) as Record<string, number>;

  const show = (panel: Props["focus"]) => focus === "all" || focus === panel;

  const title =
    focus === "initiative" ? "Initiative & non-action"
    : focus === "decision-context" ? "Decision context"
    : focus === "goals" ? "Goals & verification"
    : focus === "continuations" ? "Continuations"
    : focus === "repairs" ? "Repairs & learning"
    : focus === "reports" ? "Behavioral reports"
    : focus === "situation" ? "Current situation"
    : "Why AEGIS acted — or did not";

  const subtitle =
    focus === "situation"
      ? String(situation.summary || "User state from a single Situation projection.")
      : String(initiative.summary || context.summary || "Initiative, goals, repairs, and behavioral evidence.");

  return (
    <div className="judgment-page">
      <header className="judgment-page__hero">
        <div>
          <span>Judgment</span>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <Freshness
          generatedAt={overview.initiative?.generated_at || overview.decision_context?.generated_at || overview.goals?.generated_at || 0}
          sourceUpdatedAt={overview.initiative?.source_updated_at || overview.decision_context?.source_updated_at || overview.goals?.source_updated_at || 0}
          stale={Boolean(overview.initiative?.stale || overview.decision_context?.stale || overview.goals?.stale)}
        />
      </header>

      <section className="judgment-grid">
        {show("situation") ? (
          <article className="panel">
            <div className="panel__header"><h2>Situation</h2></div>
            <p className="human-summary">{String(situation.summary || "")}</p>
            <dl className="human-facts compact">
              {Object.entries(situation)
                .filter(([key, value]) => key !== "summary" && value != null && value !== "" && typeof value !== "object")
                .slice(0, 12)
                .map(([key, value]) => (
                  <div key={key}><dt>{key.replace(/_/g, " ")}</dt><dd>{String(value)}</dd></div>
                ))}
            </dl>
            {developerMode ? <pre className="developer-raw">{JSON.stringify(situation, null, 2)}</pre> : null}
          </article>
        ) : null}

        {show("initiative") ? (
          <article className="panel">
            <div className="panel__header"><h2>Initiative funnel</h2></div>
            <dl className="human-facts compact">
              {Object.entries(funnel).slice(0, 10).map(([key, value]) => (
                <div key={key}><dt>{key.replace(/_/g, " ")}</dt><dd>{value}</dd></div>
              ))}
              {!Object.keys(funnel).length ? <p className="empty-copy">No funnel data yet.</p> : null}
            </dl>
          </article>
        ) : null}

        {show("initiative") ? (
          <article className="panel">
            <div className="panel__header"><h2>Why no action</h2></div>
            <ul className="reason-list">
              {Object.entries(reasons).slice(0, 12).map(([reason, count]) => (
                <li key={reason}><strong>{count}×</strong><span>{reason}</span></li>
              ))}
              {!Object.keys(reasons).length ? <li className="empty-copy">No deliberate non-actions recorded.</li> : null}
            </ul>
            <div className="panel__header" style={{ marginTop: "1rem" }}><h3>Recent non-actions</h3></div>
            <ul className="reason-list">
              {nonActions.slice(-8).reverse().map((item, index) => (
                <li key={`${item.created_at}-${index}`}>
                  <StatusBadge status={String(item.decision || "no_action")} />
                  <span>{String(item.reason || "")}</span>
                </li>
              ))}
            </ul>
          </article>
        ) : null}

        {show("goals") ? (
          <article className="panel">
            <div className="panel__header"><h2>Open goals & unmet verification</h2></div>
            {openGoals.slice(0, 8).map((goal) => (
              <div className="goal-card" key={String(goal.task_id || goal.title)}>
                <strong>{String(goal.title || goal.goal || "Goal")}</strong>
                <p>{String(goal.success_condition || "")}</p>
                {Array.isArray(goal.unmet_conditions) && goal.unmet_conditions.length ? (
                  <ul>
                    {(goal.unmet_conditions as Array<Record<string, unknown>>).slice(0, 4).map((item, idx) => (
                      <li key={idx}>{String(item.summary || item.status || item.check || "unmet")}</li>
                    ))}
                  </ul>
                ) : (
                  <small>Verification conditions not yet unmet or not reported</small>
                )}
                {developerMode && goal.evidence ? (
                  <pre className="developer-raw">{JSON.stringify(goal.evidence, null, 2)}</pre>
                ) : null}
              </div>
            ))}
            {!openGoals.length ? <p className="empty-copy">No open goals with verification graphs.</p> : null}
          </article>
        ) : null}

        {show("continuations") ? (
          <article className="panel">
            <div className="panel__header"><h2>Continuations</h2></div>
            <p className="human-summary">{String(continuations.summary || "")}</p>
            {continuationItems.slice(0, 10).map((item, index) => (
              <div className="goal-card" key={String(item.continuation_id || item.id || index)}>
                <strong>{String(item.title || item.kind || "Continuation")}</strong>
                <p>{String(item.next_action || item.summary || item.reason || "")}</p>
                {item.due_at ? <small>Due {new Date(Number(item.due_at)).toLocaleString()}</small> : null}
              </div>
            ))}
            {!continuationItems.length ? <p className="empty-copy">No open continuations.</p> : null}
          </article>
        ) : null}

        {show("repairs") ? (
          <article className="panel">
            <div className="panel__header"><h2>Repairs & learning</h2></div>
            {repairItems.slice(0, 8).map((item, index) => (
              <div className="goal-card" key={String(item.repair_id || item.id || index)}>
                <strong>{String(item.category || item.title || "Repair")}</strong>
                <p>{String(item.error || item.message || item.summary || "")}</p>
                {item.next_action || item.lesson ? <small>{String(item.next_action || item.lesson)}</small> : null}
              </div>
            ))}
            {!repairItems.length ? <p className="empty-copy">No repair history yet.</p> : null}
          </article>
        ) : null}

        {show("reports") ? (
          <article className="panel">
            <div className="panel__header"><h2>Behavioral reports</h2></div>
            <p className="human-summary">{String(reports.summary || "")}</p>
            <dl className="human-facts compact">
              {Object.entries((reports.metrics || {}) as Record<string, number>).map(([key, value]) => (
                <div key={key}><dt>{key.replace(/_/g, " ")}</dt><dd>{typeof value === "number" ? `${Math.round(value * 100)}%` : String(value)}</dd></div>
              ))}
            </dl>
            {developerMode ? <pre className="developer-raw">{JSON.stringify(reports.evidence || {}, null, 2)}</pre> : null}
          </article>
        ) : null}

        {show("decision-context") ? (
          <article className="panel">
            <div className="panel__header"><h2>Decision context</h2></div>
            <p className="human-summary">{String(context.summary || "").slice(0, 600)}</p>
            {Array.isArray(context.obligations) && context.obligations.length ? (
              <ul className="reason-list">
                {(context.obligations as Array<Record<string, unknown>>).slice(0, 8).map((item) => (
                  <li key={String(item.obligation_id || item.summary)}>
                    <StatusBadge status={String(item.kind || "obligation")} />
                    <span>{String(item.summary || "")}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-copy">No obligations in AgentState right now.</p>
            )}
            {developerMode ? <pre className="developer-raw">{JSON.stringify(context.context_meta || context.context || {}, null, 2)}</pre> : null}
          </article>
        ) : null}
      </section>
    </div>
  );
}
