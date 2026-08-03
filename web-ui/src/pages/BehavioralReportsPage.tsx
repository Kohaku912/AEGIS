import { useMemo, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { text } from "./PageSupport";

const METRIC_LABELS: Record<string, string> = {
  goal_achievement: "Goal達成率",
  goal_verification: "Goal検証率",
  follow_through: "Follow-through率",
  continuation_completion: "Continuation完了率",
  intentional_non_action: "意図的な非行動率",
  social_response: "Social対応率",
  user_correction: "User Correction反映率",
  auto_repair: "自動修復成功率",
  recurrence: "同じ失敗の再発率",
  cost_efficiency: "Cost効率",
  open_loops: "未解決Open Loop数",
  restraint: "抑制率",
  continuity: "継続率",
};

export function BehavioralReportsPage({ overview }: { overview: UiOverview }) {
  const reports = overview.behavioral_reports?.data || {};
  const metrics = (reports.metrics || {}) as Record<string, number | string>;
  const evidence = (reports.evidence || {}) as Record<string, unknown>;
  const [selected, setSelected] = useState("");
  const entries = useMemo(
    () => Object.entries(metrics).filter(([, value]) => value !== undefined && value !== null),
    [metrics],
  );
  const current = selected || entries[0]?.[0] || "";
  const related = evidence[current];

  return (
    <div className="judgment-split">
      <div className="grid">
        <PageHeader title="Behavioral Reports" description="長期的に改善しているかを指標と比較で確認します。" />
        <p className="muted">{text(reports.summary, "行動評価の集計です。")}</p>
        <section className="panel">
          <div className="compact-list">
            {entries.map(([key, value]) => (
              <button type="button" className="list-row" key={key} data-selected={current === key} onClick={() => setSelected(key)}>
                <div>
                  <strong>{METRIC_LABELS[key] || key}</strong>
                  <p>{formatMetric(value)}</p>
                </div>
              </button>
            ))}
            {!entries.length ? <p className="muted">行動指標はまだありません。</p> : null}
          </div>
        </section>
      </div>
      <aside className="panel judgment-detail">
        <div className="panel__header"><h2>{METRIC_LABELS[current] || current || "指標詳細"}</h2></div>
        <p>数値の根拠になった Operation / Goal / Incident / Social Item を確認できます。</p>
        {related ? (
          <pre className="developer-raw">{JSON.stringify(related, null, 2)}</pre>
        ) : (
          <p className="empty-copy">この指標の根拠データはまだ紐づいていません。</p>
        )}
      </aside>
    </div>
  );
}

function formatMetric(value: number | string) {
  if (typeof value === "number") {
    if (value >= 0 && value <= 1) return `${Math.round(value * 100)}%`;
    return String(value);
  }
  return String(value);
}
