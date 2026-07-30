import { PageHeader } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { asRecord, KeyValues, RecordList } from "./PageSupport";

export function AgentStatePage({ overview }: { overview: UiOverview }) {
  const state = overview.agent_state?.data || {};
  const situation = overview.situation?.data || overview.user_situation?.data || overview.user_state.data;
  const constraints = asRecord(state.constraints || overview.decision_context?.data.constraints);
  const panels = [
    ["エージェント状態", state],
    ["判断コンテキスト", overview.decision_context?.data || {}],
    ["状況 / ユーザー状態", { ...situation, ...overview.user_state.data }],
    ["制約", constraints],
  ] as const;
  return <div className="grid">
    <PageHeader title="エージェント状態" description="判断に使用される構造化された運用状態を確認します。" />
    <div className="grid grid--three">{panels.map(([title, data]) => <section className="panel" key={title}><h2>{title}</h2><KeyValues data={data} /></section>)}</div>
    <div className="grid grid--three"><section className="panel"><h2>目標</h2><RecordList items={overview.goals?.data.open || overview.goals?.data.items || []} /></section><section className="panel"><h2>オープンループ</h2><RecordList items={overview.open_loops?.data.items || []} /></section><section className="panel"><h2>利用可能サーバー</h2><RecordList items={overview.servers.data.items.filter((server) => String(server.status).toUpperCase() === "ONLINE") as unknown as Array<Record<string, unknown>>} /></section></div>
  </div>;
}
