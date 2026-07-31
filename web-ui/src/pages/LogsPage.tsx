import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchActivityLogs } from "../api/client";
import { DataState, PageHeader, Pagination, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime, formatRelative } from "../i18n";
import type { UiOverview } from "../types";
import { asRecord } from "./PageSupport";

const PAGE_SIZE = 30;

function operationServers(operation: Record<string, unknown>): string[] {
  const steps = Array.isArray(operation.steps) ? operation.steps.map(asRecord) : [];
  return Array.from(new Set(
    steps
      .map((step) => String(step.capability_id || "").split(".")[0])
      .filter(Boolean),
  ));
}

function operationTarget(operation: Record<string, unknown>): string {
  const target = String(operation.target || "");
  if (target) return target;
  const servers = operationServers(operation);
  return servers.length ? servers.join(", ") : String(operation.kind_label || operation.kind || "AEGIS");
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
      const result = await fetchActivityLogs(page, PAGE_SIZE);
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
    () => server === "all"
      ? items
      : items.filter((operation) => operationServers(operation).includes(server)),
    [items, server],
  );

  const rows = visibleItems.map((operation, index) => {
    const timestamp = Number(operation.updated_at || operation.started_at || 0);
    const what = String(
      operation.what_happened
      || operation.narrative
      || operation.summary
      || "No result was recorded.",
    );
    const reason = String(operation.reason || operation.title || "No reason was recorded.");
    const outcome = String(operation.status || "recorded").replaceAll("_", " ");
    const target = operationTarget(operation);
    const steps = Array.isArray(operation.steps) ? operation.steps.map(asRecord) : [];
    const id = String(operation.operation_id || `${timestamp}-${index}`);
    return {
      id,
      cells: [formatDateTime(timestamp), what, target, outcome, reason],
      card: <div className="log-card">
        <div><strong>{what}</strong><span className="status-badge">{outcome}</span></div>
        <p><span className="muted">Target:</span> {target}</p>
        <p><span className="muted">Why:</span> {reason}</p>
        <small>{formatDateTime(timestamp)} · {String(operation.kind_label || operation.kind || "AEGIS")}</small>
        {steps.length ? <details>
          <summary>Show {steps.length} recorded step{steps.length === 1 ? "" : "s"}</summary>
          <ol>
            {steps.map((step, stepIndex) => <li key={`${id}-${stepIndex}`}>
              {String(step.narrative || step.summary || step.action || step.capability_id || "Recorded step")}
            </li>)}
          </ol>
        </details> : null}
      </div>,
    };
  });

  return <div className="grid">
    <PageHeader title="Logs" description="What AEGIS did, why it acted, and the result of each operation.">
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
        headers={["Time", "What AEGIS did", "Target", "Result", "Why"]}
        rows={rows}
      /> : null}
      {server !== "all" && !loading && !error ? <p className="muted">The server filter applies to the current page of operations.</p> : null}
      <Pagination page={page} total={total} pageSize={PAGE_SIZE} onPage={setPage} />
    </section>
  </div>;
}
