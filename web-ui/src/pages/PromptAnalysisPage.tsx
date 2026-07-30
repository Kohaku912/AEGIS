import { useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { asRecord, KeyValues } from "./PageSupport";

export function PromptAnalysisPage({ overview }: { overview: UiOverview }) {
  const [result, setResult] = useState<Record<string, unknown>>(() => asRecord(overview.usage.data.context_breakdown || overview.usage.data));
  const [notice, setNotice] = useState("");
  const run = async () => {
    setNotice("分析中…");
    try {
      let response = await fetch("/api/prompt-analysis/run", { method: "POST", credentials: "include" });
      if (response.status === 404 || response.status === 405) response = await fetch("/api/prompt-analysis/run", { credentials: "include" });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      setResult(asRecord(await response.json()));
      setNotice("分析を更新しました。");
    } catch (error) {
      setNotice(`分析 API を利用できないため使用量データを表示しています: ${error instanceof Error ? error.message : String(error)}`);
    }
  };
  const sections = Object.entries(result);
  return <div className="grid"><PageHeader title="プロンプト分析" description="コンテキスト構成、トークン使用量、改善候補を確認します。"><button type="button" onClick={() => void run()}>分析を実行</button></PageHeader>{notice ? <p className="data-state" role="status">{notice}</p> : null}<section className="panel"><h2>コンテキスト内訳</h2><KeyValues data={result} /></section><section className="panel"><h2>分析セクション</h2><div className="compact-list">{sections.map(([key, value]) => <article className="list-row" key={key}><div><strong>{key}</strong><p>{typeof value === "object" ? JSON.stringify(value) : String(value)}</p></div></article>)}</div></section></div>;
}
