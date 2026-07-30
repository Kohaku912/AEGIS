import { useEffect, useState } from "react";
import { PageHeader, Pagination } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { asRecord, asRecords, RecordList } from "./PageSupport";

export function LogsPage({ overview }: { overview: UiOverview }) {
  const [server, setServer] = useState("all");
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    const params = new URLSearchParams({ page: String(page), limit: "50" });
    if (server !== "all") params.set("server_id", server);
    fetch(`/api/audit?${params}`, { credentials: "include" }).then(async (response) => {
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      const payload = asRecord(await response.json());
      if (alive) { setItems(asRecords(payload.items || payload.entries || payload.records)); setTotal(Number(payload.total || 0)); setError(""); }
    }).catch((reason) => alive && setError(reason instanceof Error ? reason.message : String(reason)));
    return () => { alive = false; };
  }, [page, server]);
  return <div className="grid"><PageHeader title="ログ" description="専用ログストリームが利用可能になるまで監査 API をプロキシ表示します。" /><section className="panel"><label>サーバー <select value={server} onChange={(event) => { setServer(event.currentTarget.value); setPage(1); }}><option value="all">すべて</option>{overview.servers.data.items.map((item) => <option value={item.server_id} key={item.server_id}>{item.server_id}</option>)}</select></label><p className="muted">ストリーム接続先は各 `/api/...` ログエンドポイントです。現在は `/api/audit` を表示しています。</p>{error ? <p className="data-state data-state--error">{error}</p> : null}<RecordList items={items} /><Pagination page={page} total={total} pageSize={50} onPage={setPage} /></section></div>;
}
