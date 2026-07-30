import { useEffect, useMemo, useState } from "react";
import { fetchSettings } from "../api/client";
import { PageHeader } from "../components/DashboardPrimitives";

function flatten(value: unknown, prefix = ""): Array<[string, unknown]> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [[prefix || "value", value]];
  return Object.entries(value as Record<string, unknown>).flatMap(([key, child]) => flatten(child, prefix ? `${prefix}.${key}` : key));
}

export function AllSettingsPage() {
  const [settings, setSettings] = useState<Record<string, unknown>>({});
  const [query, setQuery] = useState("");
  const [json, setJson] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    fetchSettings().then((value) => alive && setSettings(value)).catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, []);
  const rows = useMemo(() => flatten(settings).filter(([key, value]) => `${key} ${String(value)}`.toLowerCase().includes(query.toLowerCase())), [query, settings]);
  return <div className="grid"><PageHeader title="全設定" description="永続設定を検索可能なツリー表で確認します。"><button type="button" onClick={() => setJson((value) => !value)}>{json ? "表を表示" : "JSON を表示"}</button></PageHeader><section className="panel"><label>検索 <input type="search" value={query} onChange={(event) => setQuery(event.currentTarget.value)} /></label>{error ? <p className="data-state data-state--error">{error}</p> : null}{json ? <pre className="mono">{JSON.stringify(settings, null, 2)}</pre> : <div className="responsive-table" role="table"><div className="responsive-table__row responsive-table__head" role="row"><span role="columnheader">設定キー</span><span role="columnheader">値</span></div>{rows.map(([key, value]) => <div className="responsive-table__row" role="row" key={key}><span role="cell" className="mono">{key}</span><span role="cell">{typeof value === "object" ? JSON.stringify(value) : String(value ?? "null")}</span></div>)}</div>}</section></div>;
}
