import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";
import { KeyValues, RecordList, asRecord, asRecords, recordSummary, recordTitle, text } from "./PageSupport";

export function PersonalContextPage({ overview }: { overview: UiOverview }) {
  const situation = { ...(overview.user_situation?.data || overview.situation?.data || {}), ...overview.user_state.data };
  const commitments = overview.commitments.data.items || [];
  const social = overview.social?.data || {};
  const loops = overview.open_loops?.data.items || [];
  const understanding = asRecord(overview.user_understanding?.data);
  const identity = asRecord(understanding.identity_profile);
  const preferences = asRecord(understanding.preferences);
  const constraints = asRecord(understanding.constraints);
  const shortHorizon = asRecords(understanding.short_horizon);
  const nextActions = asRecords(understanding.likely_next_actions);
  const deficits = asRecords(understanding.predicted_deficits);

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Personal Context</h2>
            <div className="muted">本人状況、commitments、social pending、関連 open loops を 1 画面で確認します。</div>
          </div>
          <Freshness
            generatedAt={overview.user_state.generated_at}
            sourceUpdatedAt={overview.user_state.source_updated_at}
            stale={overview.user_state.stale}
          />
        </div>
        <p className="muted">{text(understanding.summary, "本人理解の統合 snapshot はまだありません。")}</p>
      </section>
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Situation</h2></header>
          <KeyValues data={situation} />
        </section>
        <section className="panel">
          <header><h2>Identity profile</h2></header>
          <KeyValues data={{ ...identity, ...constraints }} />
        </section>
      </section>
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Short horizon</h2></header>
          <RecordList
            items={shortHorizon}
            empty="短期の needs はまだありません。"
            render={(item) => <div><strong>{recordTitle(item, "Need")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
        <section className="panel">
          <header><h2>Likely next</h2></header>
          <RecordList
            items={nextActions}
            empty="推定された次行動はありません。"
            render={(item) => <div><strong>{recordTitle(item, "Next action")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
      </section>
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Predicted deficits</h2></header>
          <RecordList
            items={deficits}
            empty="不足推定はありません。"
            render={(item) => <div><strong>{recordTitle(item, "Deficit")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
        <section className="panel">
          <header><h2>Preferences</h2></header>
          <KeyValues data={preferences} />
        </section>
      </section>
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Commitments</h2></header>
          <RecordList
            items={commitments.slice(0, 8)}
            empty="現在の commitments はありません。"
            render={(item) => (
              <div>
                <strong>{String(item.title || item.summary || "Commitment")}</strong>
                <p>{String(item.next_action || item.notification_plan || item.status || "")}</p>
              </div>
            )}
          />
        </section>
        <section className="panel">
          <header><h2>Social and loops</h2></header>
          <div className="compact-list">
            {Array.isArray(social.pending_decisions) && social.pending_decisions.length ? social.pending_decisions.slice(0, 4).map((item, index) => (
              <div className="list-row" key={String(item.item_id || index)}>
                <div>
                  <strong>{String(item.summary || item.body || "Social item")}</strong>
                  <div className="muted">{String(item.suggested_action || item.decision_reason || "")}</div>
                </div>
              </div>
            )) : <p className="muted">保留中の social 判断はありません。</p>}
            {loops.length ? loops.slice(0, 4).map((item, index) => (
              <div className="list-row" key={String(item.id || index)}>
                <div>
                  <strong>{String(item.title || item.kind || "Loop")}</strong>
                  <div className="muted">{String(item.next_action || item.waiting_reason || "")}</div>
                </div>
              </div>
            )) : null}
          </div>
        </section>
      </section>
    </div>
  );
}
