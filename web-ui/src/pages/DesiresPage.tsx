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

type DesireCard = {
  pressure: number;
  desireValue: number;
  threshold: number;
  drift: number;
  status: string;
  etaSeconds: number | null;
};

function readPressure(
  id: string,
  pressureMap: Record<string, unknown>,
  statsMap: Record<string, unknown>,
): DesireCard {
  const detail = asRecord(pressureMap[id]);
  const statsPressures = asRecord(statsMap.pressures);
  const statsDesires = asRecord(statsMap.desires || statsMap);
  // API shape: { pressure, value(=desire level), threshold, drift_rate }
  // Never prefer `value` for pressure — that field is the desire satisfaction level.
  const pressure = Number(
    detail.pressure ?? statsPressures[id] ?? (typeof pressureMap[id] === "number" ? pressureMap[id] : 0) ?? 0,
  );
  const desireValue = Number(detail.desire_value ?? detail.value ?? statsDesires[id] ?? 0);
  const threshold = Number(detail.threshold ?? 5);
  const drift = Number(detail.drift_rate ?? asRecord(statsMap.drift_rates)[id] ?? 0);
  const etaRaw = detail.seconds_until_threshold ?? statsMap.seconds_until_threshold;
  const etaSeconds = etaRaw == null || etaRaw === "" ? null : Number(etaRaw);
  const status =
    pressure >= threshold ? "実行候補" : pressure > 0 ? "蓄積中" : "待機";
  return {
    pressure: Number.isFinite(pressure) ? pressure : 0,
    desireValue: Number.isFinite(desireValue) ? desireValue : 0,
    threshold: Number.isFinite(threshold) ? threshold : 5,
    drift: Number.isFinite(drift) ? drift : 0,
    status,
    etaSeconds: etaSeconds != null && Number.isFinite(etaSeconds) ? etaSeconds : null,
  };
}

function formatEta(seconds: number | null): string {
  if (seconds == null) return "—";
  if (seconds <= 0) return "到達";
  if (seconds < 60) return `${Math.ceil(seconds)}秒`;
  const minutes = Math.ceil(seconds / 60);
  return `約${minutes}分`;
}

export function DesiresPage({ overview }: { overview: UiOverview }) {
  const autonomy = asRecord(overview.mind_summary?.data?.autonomy || overview.mind?.data?.autonomy);
  const initialPressure = asRecord(overview.mind?.data?.pressure || autonomy.pressure || {});
  const [stats, setStats] = useState<Record<string, unknown>>(() =>
    asRecord(autonomy.desires ? { desires: autonomy.desires, pressures: autonomy.pressures } : autonomy),
  );
  const [pressure, setPressure] = useState<Record<string, unknown>>(initialPressure);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState<number>(Date.now());

  useEffect(() => {
    let alive = true;
    const load = () => {
      Promise.allSettled([
        fetch("/api/desires", { credentials: "include" }).then((response) =>
          response.ok ? response.json() : Promise.reject(response.status),
        ),
        fetch("/api/desires/pressure", { credentials: "include" }).then((response) =>
          response.ok ? response.json() : Promise.reject(response.status),
        ),
      ]).then(([desireResult, pressureResult]) => {
        if (!alive) return;
        if (desireResult.status === "fulfilled") {
          setStats(asRecord(desireResult.value));
          setError("");
        } else {
          setError("欲求 API を取得できませんでした");
        }
        if (pressureResult.status === "fulfilled") {
          const payload = asRecord(pressureResult.value);
          setPressure(asRecord(payload.pressures || payload.pressure || payload));
        }
        setUpdatedAt(Date.now());
      });
    };
    load();
    const timer = window.setInterval(load, 15_000);
    return () => {
      alive = false;
      window.clearInterval(timer);
    };
  }, []);

  const globalEta = Number(stats.seconds_until_threshold);
  return (
    <div className="grid">
      <PageHeader
        title="欲求状態"
        description={`行動圧力が閾値に達すると自律実行します。${error ? ` (${error})` : ""} 更新: ${new Date(updatedAt).toLocaleTimeString()}`}
      />
      <section className="panel">
        <div className="metric-list">
          <div className="metric-row">
            <span>次の閾値まで</span>
            <strong>{formatEta(Number.isFinite(globalEta) ? globalEta : null)}</strong>
          </div>
          <div className="metric-row">
            <span>平均圧力</span>
            <strong>{Number(stats.average_pressure || 0).toFixed(2)}</strong>
          </div>
        </div>
      </section>
      <div className="grid grid--three">
        {Object.entries(desireMeta).map(([id, label]) => {
          const card = readPressure(id, pressure, stats);
          const history = [
            Math.max(0, card.pressure - 0.8),
            Math.max(0, card.pressure - 0.4),
            card.pressure,
            Math.min(10, card.pressure + card.drift),
            card.pressure,
          ];
          return (
            <section className="panel" key={id}>
              <header>
                <h2>{label}</h2>
                <span className="mono">{id}</span>
              </header>
              <GaugeRing value={card.pressure} max={10} label="/ 10 圧力" />
              <Sparkline values={history} label={`${label} 圧力推移`} />
              <div className="metric-list">
                <div className="metric-row">
                  <span>圧力</span>
                  <strong>{card.pressure.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>閾値</span>
                  <strong>{card.threshold.toFixed(1)}</strong>
                </div>
                <div className="metric-row">
                  <span>充足値</span>
                  <strong>{card.desireValue.toFixed(1)}</strong>
                </div>
                <div className="metric-row">
                  <span>変化率</span>
                  <strong>{card.drift >= 0 ? "+" : ""}{card.drift.toFixed(2)}</strong>
                </div>
                <div className="metric-row">
                  <span>状態</span>
                  <strong>{text(card.status, card.status)}</strong>
                </div>
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
