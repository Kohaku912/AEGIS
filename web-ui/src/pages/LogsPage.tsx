import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchAuditEntries } from "../api/client";
import { DataState, PageHeader, Pagination, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime, formatRelative } from "../i18n";
import type { UiOverview } from "../types";
import { asRecord } from "./PageSupport";

const PAGE_SIZE = 50;

function entryServer(entry: Record<string, unknown>): string {
  const detail = asRecord(entry.detail);
  const explicit = String(entry.server_id || detail.server_id || detail.source_server || "");
  if (explicit) return explicit;
  const capability = String(entry.capability_id || detail.capability_id || "");
  return capability.includes(".") ? capability.split(".")[0] : "";
}

function entryDetail(entry: Record<string, unknown>): string {
  const detail = asRecord(entry.detail);
  return String(
    entry.detail_summary
    || entry.reason
    || detail.error
    || detail.result_summary
    || detail.message
    || entry.capability_id
    || entry.task_id
    || "No additional detail",
  );
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
      const result = await fetchAuditEntries(page, PAGE_SIZE);
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
    () => server === "all" ? items : items.filter((entry) => entryServer(entry) === server),
    [items, server],
  );

  const rows = visibleItems.map((entry, index) => {
    const timestamp = Number(entry.timestamp_ms || entry.created_at || 0);
    const action = String(entry.action || entry.event_type || "Unknown action");
    const actor = String(entry.actor || entry.source || entryServer(entry) || "AEGIS");
    const outcome = String(entry.decision || entry.status || (asRecord(entry.detail).error ? "ERROR" : "RECORDED"));
    const detail = entryDetail(entry);
    const id = String(entry.entry_id || entry.audit_id || `${timestamp}-${index}`);
    return {
      id,
      cells: [formatDateTime(timestamp), action, actor, outcome, detail],
      card: <div className="log-card">
        <div><strong>{action}</strong><span className="status-badge">{outcome}</span></div>
        <p>{detail}</p>
        <small>{formatDateTime(timestamp)} · {actor}</small>
      </div>,
    };
  });

  return <div className="grid">
    <PageHeader title="Logs" description="Recent audit-backed activity recorded by AEGIS.">
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
        headers={["Time", "Action", "Actor", "Outcome", "Details"]}
        rows={rows}
      /> : null}
      {server !== "all" && !loading && !error ? <p className="muted">The server filter applies to the current page of audit records.</p> : null}
      <Pagination page={page} total={total} pageSize={PAGE_SIZE} onPage={setPage} />
    </section>
  </div>;
}
