import { useEffect, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { asRecord, text } from "./PageSupport";

export function DiagnosticsPage({ overview }: { overview: UiOverview }) {
  const [memory, setMemory] = useState<Record<string, unknown>>({});
  useEffect(() => {
    let alive = true;
    fetch("/api/memory/stats", { credentials: "include" }).then((response) => response.ok ? response.json() : Promise.reject(response.status)).then((value) => alive && setMemory(asRecord(value))).catch(() => undefined);
    return () => { alive = false; };
  }, []);
  const servers = overview.servers.data.items;
  const checks = [
    ["設定", !overview.core.error, overview.core.error || overview.core.status],
    ["データベース", Boolean(memory.database || memory.total || overview.memory?.data), text(memory.database || "応答あり")],
    ["Chroma", Boolean(memory.chroma || memory.semantic || asRecord(overview.memory?.data.summary).semantic), text(memory.chroma || memory.semantic || "未報告")],
    ["サーバー", servers.every((server) => String(server.status).toUpperCase() === "ONLINE"), `${servers.filter((server) => String(server.status).toUpperCase() === "ONLINE").length}/${servers.length} online`],
    ["LLM", !overview.usage.error && overview.usage.status !== "error", overview.usage.error || text(overview.usage.data.summary, overview.usage.status)],
    ["能力カタログ", Boolean(overview.capabilities?.data.count || overview.capabilities?.data.items), text(overview.capabilities?.data.count, "未報告")],
    ["イベントバス", !overview.activity?.error && !overview.freshness.error, overview.activity?.error || overview.freshness.error || "応答あり"],
  ] as const;
  return <div className="grid"><PageHeader title="診断" description="主要ランタイム依存関係の読み取り専用チェックです。" /><section className="panel"><div className="compact-list">{checks.map(([name, passed, detail]) => <article className="list-row" key={name}><SeverityGlyph severity={passed ? "ok" : "warning"} label={passed ? "PASS" : "CHECK"} /><div><strong>{name}</strong><p>{String(detail)}</p></div></article>)}</div></section></div>;
}
