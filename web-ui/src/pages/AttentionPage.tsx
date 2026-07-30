import { useMemo, useState } from "react";
import { resolveApproval } from "../api/client";
import { buildAttentionItems, filterAttention } from "../attentionModel";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { time } from "./PageSupport";

const tabs = [
  ["all", "すべて"], ["approvals", "承認待ち"], ["input", "入力待ち"], ["failures", "失敗"],
  ["connection", "接続異常"], ["config", "設定不備"], ["warnings", "警告"],
] as const;

export function AttentionPage({ overview }: { overview: UiOverview }) {
  const [tab, setTab] = useState("all");
  const [notice, setNotice] = useState("");
  const items = useMemo(() => filterAttention(buildAttentionItems(overview), tab), [overview, tab]);
  const decide = async (approvalId: string, decision: "approve" | "reject") => {
    try {
      await resolveApproval(approvalId, decision);
      setNotice(decision === "approve" ? "承認しました。" : "拒否しました。");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : String(error));
    }
  };
  return <div className="attention-page">
    <PageHeader title="要対応" description="承認、入力、障害、接続、設定に関する対応事項を優先度順に表示します。" />
    <div className="page-tabs" role="tablist">{tabs.map(([id, label]) => <button type="button" role="tab" aria-selected={tab === id} onClick={() => setTab(id)} key={id}>{label}</button>)}</div>
    {notice ? <p className="data-state" role="status">{notice}</p> : null}
    <section className="panel">
      {!items.length ? <p className="muted">この分類に対応事項はありません。</p> : items.map((item) => <article className="list-row" key={item.id}>
        <SeverityGlyph severity={item.severity} label={item.urgency} />
        <div>
          <strong>{item.title}</strong><p>{item.message}</p>
          <dl className="metric-list">
            <div className="metric-row"><span>発生日時</span><strong>{time(item.occurredAt)}</strong></div>
            <div className="metric-row"><span>関連タスク</span><strong>{item.relatedTaskId || "—"}</strong></div>
            <div className="metric-row"><span>影響</span><strong>{item.impact || item.relatedServerId || "要確認"}</strong></div>
            <div className="metric-row"><span>推奨対応</span><strong>{item.recommendedAction || "詳細を確認"}</strong></div>
            <div className="metric-row"><span>自動復旧</span><strong>{item.autoRecoverable ? "可能" : "不可 / 不明"}</strong></div>
          </dl>
          <div className="list-actions">
            {item.relatedApprovalId ? <><button type="button" onClick={() => void decide(item.relatedApprovalId!, "approve")}>承認</button><button type="button" onClick={() => void decide(item.relatedApprovalId!, "reject")}>拒否</button></> : null}
            {item.relatedTaskId ? <a href={`/dashboard/work/tasks?task=${encodeURIComponent(item.relatedTaskId)}`}>タスクを開く</a> : null}
            {item.relatedServerId ? <a href={`/dashboard/systems/${encodeURIComponent(item.relatedServerId)}`}>サーバーを開く</a> : null}
          </div>
        </div>
      </article>)}
    </section>
  </div>;
}
