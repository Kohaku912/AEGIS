import { useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { asRecord, asRecords, KeyValues, RecordList, text, time } from "./PageSupport";

export function AutonomousPage({ overview }: { overview: UiOverview }) {
  const [notice, setNotice] = useState("");
  const summary = asRecord(overview.mind_summary.data.autonomy || overview.mind_summary.data.autonomous);
  const cycles = overview.autonomous_logs?.data.cycles || overview.executions?.data.autonomous_cycles || [];
  const decisions = overview.initiative?.data.recent_decisions || [];
  const candidates = asRecords(summary.candidates).length ? asRecords(summary.candidates) : decisions;
  const enabled = Boolean(summary.enabled ?? summary.running ?? cycles.length);
  const control = async (action: "start" | "stop" | "trigger") => {
    setNotice("処理中…");
    try {
      const response = await fetch(`/api/autonomous/${action}`, { method: "POST", credentials: "include" });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      setNotice(action === "trigger" ? "自律サイクルを要求しました。" : `自律運転を${action === "start" ? "開始" : "停止"}しました。`);
    } catch (error) {
      setNotice(`操作失敗: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  return <div className="grid">
    <PageHeader title="自律運転" description="実行状態、候補、見送り理由、履歴を確認します。"><a href="/dashboard/settings">自律設定</a></PageHeader>
    <section className="panel"><header><h2><SeverityGlyph severity={enabled ? "ok" : "info"} /> {enabled ? "ON" : "OFF"}</h2><div><button type="button" onClick={() => void control(enabled ? "stop" : "start")}>{enabled ? "停止" : "開始"}</button><button type="button" onClick={() => void control("trigger")}>今すぐ実行</button></div></header>{notice ? <p role="status">{notice}</p> : null}<div className="metric-list"><div className="metric-row"><span>最終実行</span><strong>{time(cycles[0]?.created_at || cycles[0]?.started_at)}</strong></div><div className="metric-row"><span>候補数</span><strong>{candidates.length}</strong></div><div className="metric-row"><span>概要</span><strong>{text(overview.initiative?.data.summary || summary.summary)}</strong></div></div></section>
    <div className="grid grid--three"><section className="panel"><h2>候補</h2><RecordList items={candidates.slice(0, 10)} /></section><section className="panel"><h2>見送り理由</h2><KeyValues data={overview.initiative?.data.no_action_reasons || asRecord(summary.skip_reasons)} /></section><section className="panel"><h2>最近の見送り</h2><RecordList items={overview.initiative?.data.recent_non_actions || []} /></section></div>
    <section className="panel"><h2>実行履歴</h2><RecordList items={cycles} /></section>
  </div>;
}
