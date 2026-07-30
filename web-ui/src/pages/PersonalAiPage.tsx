import { useEffect, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { PageHeader } from "../components/DashboardPrimitives";
import type { EntitySummary, UiOverview } from "../types";
import { KeyValues } from "./PageSupport";

const tabs = ["hooks", "commitments", "delegations", "situation"] as const;
type Tab = typeof tabs[number];
const labels: Record<Tab, string> = { hooks: "Hooks", commitments: "Commitments", delegations: "Delegations", situation: "Situation" };

export function PersonalAiPage({ overview }: { overview: UiOverview }) {
  const [tab, setTab] = useState<Tab>("hooks");
  const [resources, setResources] = useState<Record<string, EntitySummary[]>>({});
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    Promise.all(tabs.slice(0, 3).map(async (resource) => [resource, (await fetchResourceEntities(resource, "", { limit: 100 })).items] as const))
      .then((results) => alive && setResources(Object.fromEntries(results)))
      .catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, []);
  const items = resources[tab] || [];
  return <div className="grid"><PageHeader title="Personal AI" description="個人向けのフック、約束、委任、状況認識を管理します。" /><div className="page-tabs" role="tablist">{tabs.map((item) => <button type="button" role="tab" aria-selected={tab === item} onClick={() => setTab(item)} key={item}>{labels[item]}</button>)}</div>{error ? <p className="data-state data-state--error">{error}</p> : null}<section className="panel">{tab === "situation" ? <KeyValues data={{ ...(overview.situation?.data || overview.user_situation?.data || {}), ...overview.user_state.data }} /> : <div className="compact-list">{items.map((item) => <article className="list-row" key={item.id}><div><strong>{item.title}</strong><p>{item.subtitle}</p></div><span>{item.status}</span></article>)}{!items.length ? <p className="muted">項目はありません。</p> : null}</div>}</section></div>;
}
