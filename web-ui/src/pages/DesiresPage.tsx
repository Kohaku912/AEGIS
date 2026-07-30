import { useEffect, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { GaugeRing, Sparkline } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { asRecord, text } from "./PageSupport";

const desireMeta = {
  user_support: "ユーザー支援",
  social: "社会性",
  growth: "成長",
} as const;

export function DesiresPage({ overview }: { overview: UiOverview }) {
  const initial = asRecord(asRecord(overview.mind_summary.data.autonomy).desires || overview.mind?.data.desires);
  const [desires, setDesires] = useState<Record<string, unknown>>(initial);
  const [pressure, setPressure] = useState<Record<string, unknown>>(() => asRecord(overview.mind?.data.pressure));
  useEffect(() => {
    let alive = true;
    Promise.allSettled([
      fetch("/api/desires", { credentials: "include" }).then((response) => response.ok ? response.json() : Promise.reject(response.status)),
      fetch("/api/desires/pressure", { credentials: "include" }).then((response) => response.ok ? response.json() : Promise.reject(response.status)),
    ]).then(([desireResult, pressureResult]) => {
      if (!alive) return;
      if (desireResult.status === "fulfilled") setDesires(asRecord(desireResult.value.desires || desireResult.value));
      if (pressureResult.status === "fulfilled") setPressure(asRecord(pressureResult.value.pressure || pressureResult.value));
    });
    return () => { alive = false; };
  }, []);
  return <div className="grid">
    <PageHeader title="欲求状態" description="AEGIS の行動圧を 3 軸で表示します。" />
    <div className="grid grid--three">{Object.entries(desireMeta).map(([id, label]) => {
      const raw = desires[id];
      const detail = asRecord(raw);
      const value = Number(detail.value ?? detail.level ?? raw ?? 0);
      const pressureDetail = asRecord(pressure[id]);
      const pressureValue = Number(pressureDetail.value ?? pressureDetail.pressure ?? pressure[id] ?? 0);
      const threshold = Number(pressureDetail.threshold ?? detail.threshold ?? 5);
      const history = Array.isArray(detail.history) ? detail.history.map(Number).filter(Number.isFinite) : [value * .92, value * .96, value, value * .98, value];
      return <section className="panel" key={id}><header><h2>{label}</h2><span className="mono">{id}</span></header><GaugeRing value={value} max={10} label="/ 10" /><Sparkline values={history} label={`${label} 推移`} /><div className="metric-list"><div className="metric-row"><span>圧力</span><strong>{pressureValue.toFixed(1)}</strong></div><div className="metric-row"><span>閾値</span><strong>{threshold.toFixed(1)}</strong></div><div className="metric-row"><span>状態</span><strong>{text(detail.status, pressureValue >= threshold ? "実行候補" : "蓄積中")}</strong></div></div></section>;
    })}</div>
  </div>;
}
