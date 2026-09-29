import { useEffect, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { PageHeader } from "../components/DashboardPrimitives";
import type { EntitySummary, UiOverview } from "../types";
import { KeyValues, RecordList, asRecord, asRecords, recordSummary, recordTitle, text } from "./PageSupport";

const tabs = ["hooks", "commitments", "delegations", "situation"] as const;
type Tab = typeof tabs[number];
const labels: Record<Tab, string> = { hooks: "Hooks", commitments: "Commitments", delegations: "Delegations", situation: "Situation" };

export function PersonalAiPage({ overview }: { overview: UiOverview }) {
  const [tab, setTab] = useState<Tab>("hooks");
  const [resources, setResources] = useState<Record<string, EntitySummary[]>>({});
  const [error, setError] = useState("");
  const understanding = asRecord(overview.user_understanding?.data);
  const authority = asRecord(understanding.delegated_authority_state);
  const burden = asRecords(understanding.burden_reduction_opportunities);
  const improvements = asRecords(understanding.self_improvement_queue);
  const longHorizon = asRecords(understanding.long_horizon);
  const lifeHorizon = asRecords(understanding.life_horizon);
  useEffect(() => {
    let alive = true;
    Promise.all(tabs.slice(0, 3).map(async (resource) => [resource, (await fetchResourceEntities(resource, "", { limit: 100 })).items] as const))
      .then((results) => alive && setResources(Object.fromEntries(results)))
      .catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, []);
  const items = resources[tab] || [];
  return (
    <div className="grid">
      <PageHeader title="Personal AI" description="委任状態、将来 needs、自己改善キューを含む個人運用面を確認します。" />
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Delegated authority</h2></header>
          <p className="muted">{text(authority.summary, "委任状態の summary はありません。")}</p>
          <KeyValues data={authority} />
        </section>
        <section className="panel">
          <header><h2>Burden reduction</h2></header>
          <RecordList
            items={burden}
            empty="目立つ burden reduction opportunity はありません。"
            render={(item) => <div><strong>{recordTitle(item, "Opportunity")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
      </section>
      <section className="home-summary-grid">
        <section className="panel">
          <header><h2>Long horizon</h2></header>
          <RecordList
            items={longHorizon}
            empty="長期 horizon はありません。"
            render={(item) => <div><strong>{recordTitle(item, "Long horizon")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
        <section className="panel">
          <header><h2>Self-improvement queue</h2></header>
          <RecordList
            items={improvements}
            empty="自己改善キューは空です。"
            render={(item) => <div><strong>{recordTitle(item, "Improvement")}</strong><p>{recordSummary(item)}</p></div>}
          />
        </section>
      </section>
      <section className="panel">
        <header><h2>Life horizon</h2></header>
        <RecordList
          items={lifeHorizon}
          empty="人生スケールの horizon はまだ明示されていません。"
          render={(item) => <div><strong>{recordTitle(item, "Life horizon")}</strong><p>{recordSummary(item)}</p></div>}
        />
      </section>
      <div className="page-tabs" role="tablist">{tabs.map((item) => <button type="button" role="tab" aria-selected={tab === item} onClick={() => setTab(item)} key={item}>{labels[item]}</button>)}</div>
      {error ? <p className="data-state data-state--error">{error}</p> : null}
      <section className="panel">
        {tab === "situation" ? (
          <KeyValues data={{ ...(overview.situation?.data || overview.user_situation?.data || {}), ...overview.user_state.data }} />
        ) : (
          <div className="compact-list">
            {items.map((item) => <article className="list-row" key={item.id}><div><strong>{item.title}</strong><p>{item.subtitle}</p></div><span>{item.status}</span></article>)}
            {!items.length ? <p className="muted">項目はありません。</p> : null}
          </div>
        )}
      </section>
    </div>
  );
}
