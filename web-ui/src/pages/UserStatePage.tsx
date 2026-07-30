import { PageHeader } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { asRecord, KeyValues } from "./PageSupport";

export function UserStatePage({ overview }: { overview: UiOverview }) {
  const situation = { ...(overview.user_situation?.data || overview.situation?.data || {}), ...overview.user_state.data };
  const facts = asRecord(situation.facts || situation.observations || situation.known);
  const estimates = asRecord(situation.estimates || situation.inferences || situation.assumptions);
  const reserved = new Set(["facts", "observations", "known", "estimates", "inferences", "assumptions"]);
  const direct = Object.fromEntries(Object.entries(situation).filter(([key]) => !reserved.has(key)));
  return <div className="grid"><PageHeader title="ユーザー状態" description="観測された事実と AEGIS の推定を分離して表示します。" /><div className="home-summary-grid"><section className="panel"><header><h2>事実</h2><span>観測 / 明示</span></header><KeyValues data={{ ...direct, ...facts }} /></section><section className="panel"><header><h2>推定</h2><span>不確実性を含む</span></header><KeyValues data={estimates} /></section></div></div>;
}
