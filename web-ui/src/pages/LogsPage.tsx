import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchJournalEvents } from "../api/client";
import { DataState, PageHeader, Pagination, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime, formatRelative } from "../i18n";
import type { UiOverview } from "../types";
import { asRecord, text } from "./PageSupport";

const PAGE_SIZE = 30;

function eventServer(item: Record<string, unknown>): string {
  const payload = asRecord(item.payload);
  const target = String(item.target || payload.capability_id || payload.server_id || "");
  return target.split(".")[0] || String(item.aggregate_type || "");
}

function shortTrace(value: unknown): string {
  const trace = String(value || "");
  if (!trace) return "—";
  return trace.length > 12 ? `${trace.slice(0, 8)}…${trace.slice(-4)}` : trace;
}

export function LogsPage({ overview }: { overview: UiOverview }) {
  const [server, setServer] = useState("all");
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState(0);
  const [reload, setReload] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await fetchJournalEvents(page, PAGE_SIZE);
      setItems(result.items);
      setTotal(result.total);
      setUpdatedAt(Date.now());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    void load();
  }, [load, reload]);

  const visibleItems = useMemo(
    () => server === "all" ? items : items.filter((item) => eventServer(item) === server),
    [items, server],
  );

  const rows = visibleItems.map((item, index) => {
    const timestamp = Number(item.timestamp_ms || item.updated_at || 0);
    const what = String(item.title || item.what_happened || item.event_type || "event");
    const summary = String(item.summary || item.reason || "");
    const target = String(item.target || item.aggregate_id || "—");
    const outcome = String(item.status || "recorded").replaceAll("_", " ");
    const id = String(item.id || item.sequence || `${timestamp}-${index}`);
    return {
      id,
      cells: [formatDateTime(timestamp), what, target, shortTrace(item.trace_id), outcome],
      card: <div className="log-card">
        <div><strong>{what}</strong><span className="status-badge">{outcome}</span></div>
        {summary ? <p>{summary}</p> : null}
        <p><span className="muted">Target:</span> {target}</p>
        <p><span className="muted">Trace:</span> <span className="mono">{text(item.trace_id, "—")}</span></p>
        <small>{formatDateTime(timestamp)} · {String(item.event_type || item.kind || "journal")} · seq {String(item.sequence || "—")}</small>
      </div>,
    };
  });

  return <div className="grid">
    <PageHeader title="Logs" description="Journal に記録されたイベントと OpenTelemetry の trace id です。">
      <button type="button" className="secondary-button" onClick={() => setReload((value) => value + 1)} disabled={loading}>
        <RefreshCw size={14} aria-hidden="true" />Refresh
      </button>
    </PageHeader>
    <section className="panel">
      <div className="resource-toolbar">
        <label>Server <select value={server} onChange={(event) => { setServer(event.currentTarget.value); setPage(1); }}>
          <option value="all">All servers</option>
          {overview.servers.data.items.map((item) => <option value={item.server_id} key={item.server_id}>{item.server_id}</option>)}
        </select></label>
        {updatedAt ? <span className="freshness">Last updated: {formatDateTime(updatedAt)} ({formatRelative(updatedAt)})</span> : null}
      </div>
      <DataState loading={loading} error={error} empty={!loading && !error && !rows.length} onRetry={() => setReload((value) => value + 1)} />
      {!loading && !error && rows.length ? <ResponsiveDataView
        headers={["Time", "Event", "Target", "Trace", "Result"]}
        rows={rows}
      /> : null}
      {server !== "all" && !loading && !error ? <p className="muted">The server filter applies to the current page of journal events.</p> : null}
      <Pagination page={page} total={total} pageSize={PAGE_SIZE} onPage={setPage} />
    </section>
  </div>;
}
