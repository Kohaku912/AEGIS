import { useEffect, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { asRecord, asRecords, RecordList } from "./PageSupport";

export function AuditPage() {
  const [payload, setPayload] = useState<Record<string, unknown>>({});
  const [raw, setRaw] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    const load = async () => {
      let response = await fetch("/api/audit/grouped", { credentials: "include" });
      if (response.status === 404) response = await fetch("/api/audit?limit=100", { credentials: "include" });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      return asRecord(await response.json());
    };
    load().then((value) => alive && setPayload(value)).catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, []);
  const groups = asRecords(payload.groups);
  const items = asRecords(payload.items || payload.entries || payload.records);
  return <div className="grid"><PageHeader title="監査" description="操作の因果関係と監査記録を表示します。"><button type="button" onClick={() => setRaw((value) => !value)}>{raw ? "グループ表示" : "JSON 表示"}</button></PageHeader>{error ? <p className="data-state data-state--error">{error}</p> : null}<section className="panel">{raw ? <pre className="mono">{JSON.stringify(payload, null, 2)}</pre> : <><h2>グループ</h2><RecordList items={groups.length ? groups : items} /></>}</section></div>;
}
