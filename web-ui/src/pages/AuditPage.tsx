import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { fetchAuditGroups } from "../api/client";
import { DataState, PageHeader, Pagination, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime } from "../i18n";

const PAGE_SIZE = 30;

export function AuditPage() {
  const [groups, setGroups] = useState<Array<Record<string, unknown>>>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [raw, setRaw] = useState(false);
  const [reload, setReload] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await fetchAuditGroups(page, PAGE_SIZE);
      setGroups(result.items);
      setTotal(result.total);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    void load();
  }, [load, reload]);

  const rows = groups.map((group, index) => {
    const id = String(group.group_id || `audit-group-${index}`);
    const title = String(group.group_title || group.title || group.group_type || "Audit group");
    const type = String(group.group_type || "operation");
    const end = Number(group.end_ms || group.started_at || 0);
    const entries = Number(group.entry_count || (Array.isArray(group.entries) ? group.entries.length : 0));
    const errors = Number(group.error_count || 0);
    const result = errors ? `${errors} error(s)` : "Recorded";
    return {
      id,
      cells: [formatDateTime(end), title, type, String(entries), result],
      card: <div className="log-card">
        <strong>{title}</strong>
        <p>{type} · {entries} entries · {result}</p>
        <small>{formatDateTime(end)}</small>
      </div>,
    };
  });

  return <div className="grid">
    <PageHeader title="Audit log" description="Causal groups of actions and decisions recorded by AEGIS.">
      <button type="button" className="secondary-button" onClick={() => setRaw((value) => !value)}>{raw ? "Grouped view" : "JSON view"}</button>
      <button type="button" className="secondary-button" onClick={() => setReload((value) => value + 1)} disabled={loading}>
        <RefreshCw size={14} aria-hidden="true" />Refresh
      </button>
    </PageHeader>
    <section className="panel">
      <DataState loading={loading} error={error} empty={!loading && !error && !groups.length} onRetry={() => setReload((value) => value + 1)} />
      {!loading && !error && groups.length && raw ? <pre className="mono">{JSON.stringify(groups, null, 2)}</pre> : null}
      {!loading && !error && rows.length && !raw ? <ResponsiveDataView
        headers={["Time", "Operation", "Type", "Entries", "Result"]}
        rows={rows}
      /> : null}
      <Pagination page={page} total={total} pageSize={PAGE_SIZE} onPage={setPage} />
    </section>
  </div>;
}
