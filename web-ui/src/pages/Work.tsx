import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createRequestId, createSavedView, deleteSavedView, fetchResourceEntities, fetchSavedViews, runTaskAction, sendChat, type SavedView } from "../api/client";
import { ActionButton, ConfirmDialog, DataState, FilterBar, PageHeader, Pagination, ResponsiveDataView, SavedViewPicker, type ActionLevel } from "../components/DashboardPrimitives";
import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import { formatDateTime } from "../i18n";
import type { EntitySummary, UiOverview } from "../types";

const taskStatuses = ["running", "pending", "waiting_approval", "paused", "blocked", "completed", "failed", "cancelled"];
const actionLevel: Record<string, ActionLevel> = { pause: "safe", resume: "controlled", retry: "controlled", cancel: "dangerous" };

export function Work({ overview }: { overview: UiOverview }) {
  const overviewEntity = entityFromOverview(overview);
  const [records, setRecords] = useState<EntitySummary[]>(() => overviewEntity ? [overviewEntity] : []);
  const [selectedId, setSelectedId] = useState(() => new URLSearchParams(window.location.search).get("task") || overviewEntity?.id || "");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [warnings, setWarnings] = useState<string[]>([]);
  const [views, setViews] = useState<SavedView[]>([]);
  const [selectedView, setSelectedView] = useState("");
  const [instruction, setInstruction] = useState("");
  const [creating, setCreating] = useState(false);
  const createLock = useRef(false);
  const [notice, setNotice] = useState("");
  const [preview, setPreview] = useState<{ action: string; detail: Record<string, unknown> }>();
  const [actionBusy, setActionBusy] = useState(false);
  const createRequested = new URLSearchParams(window.location.search).get("create") === "1";

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchResourceEntities("tasks", query, { page, limit: pageSize, status: statusFilter, sort: "updated_at", order: "desc" });
      setRecords(result.items);
      setTotal(result.total);
      setWarnings((result.warnings || []).map((warning) => `${warning.resource || "Data source"}: ${warning.message}`));
      setError("");
      if (!selectedId && result.items[0]) setSelectedId(result.items[0].id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, query, selectedId, statusFilter]);

  useEffect(() => { const timer = window.setTimeout(() => void load(), 180); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { fetchSavedViews("tasks").then(setViews).catch((reason) => setNotice(`Saved views API: ${reason instanceof Error ? reason.message : String(reason)}`)); }, []);

  const selected = useMemo(() => records.find((item) => item.id === selectedId) || records[0], [records, selectedId]);
  const data = selected?.data || {};
  const steps = Array.isArray(data.steps) ? data.steps as Array<Record<string, unknown>> : overview.current_task.data.task_id === selected?.id ? overview.current_task.data.steps || [] : [];
  const relatedApprovals = overview.approvals.data.pending.filter((approval) => approval.task_id === selected?.id);
  const relatedErrors = (overview.errors?.data.items || []).filter((item) => String(item.task_id || "") === selected?.id);

  const createTask = async () => {
    const text = instruction.trim();
    if (!text || createLock.current) return;
    createLock.current = true;
    setCreating(true);
    try {
      await sendChat(text, createRequestId());
      setInstruction("");
      setNotice("Request accepted. AEGIS will create the goal and execution plan.");
      await load();
    } catch (reason) {
      setNotice(`Could not create the task: ${reason instanceof Error ? reason.message : String(reason)}`);
    } finally {
      createLock.current = false;
      setCreating(false);
    }
  };

  const requestAction = async (action: string) => {
    if (!selected) return;
    setActionBusy(true);
    try {
      const result = await runTaskAction(selected.id, action);
      setPreview({ action, detail: {
        Target: selected.title,
        Impact: String((result.preview as Record<string, unknown> | undefined)?.impact || `Run ${action}`),
        Reversibility: String((result.preview as Record<string, unknown> | undefined)?.reversibility || (action === "cancel" ? "This action may not be reversible" : "The task can be resumed or retried")),
        Verification: String((result.preview as Record<string, unknown> | undefined)?.verification || "Reload Task Manager state after execution"),
      } });
    } catch (reason) {
      setNotice(`Could not preview the action: ${reason instanceof Error ? reason.message : String(reason)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const confirmAction = async () => {
    if (!preview || !selected) return;
    setActionBusy(true);
    try {
      const result = await runTaskAction(selected.id, preview.action, true);
      setNotice(result.result ? "Action completed and state verified." : "Approval or additional authentication is required. Check Needs Attention.");
      setPreview(undefined);
      await load();
    } catch (reason) {
      setNotice(`Action failed: ${reason instanceof Error ? reason.message : String(reason)}`);
    } finally {
      setActionBusy(false);
    }
  };

  const saveView = async () => {
    const name = window.prompt("Saved view name");
    if (!name?.trim()) return;
    try {
      const view = await createSavedView({ resource: "tasks", name: name.trim(), query, filters: { status: statusFilter }, sort: "updated_at", order: "desc", page_size: pageSize });
      setViews((items) => [view, ...items]);
      setSelectedView(view.id);
    } catch (reason) {
      setNotice(`Could not save the view: ${reason instanceof Error ? reason.message : String(reason)}`);
    }
  };

  const selectView = (id: string) => {
    setSelectedView(id);
    const view = views.find((item) => item.id === id);
    if (!view) return;
    setQuery(view.query);
    setStatusFilter(view.filters.status || "");
    setPageSize(view.page_size);
    setPage(1);
  };

  const removeView = async (id: string) => {
    try { await deleteSavedView(id); setViews((items) => items.filter((item) => item.id !== id)); setSelectedView(""); }
    catch (reason) { setNotice(`Could not delete the view: ${reason instanceof Error ? reason.message : String(reason)}`); }
  };

  return <div className="tasks-page">
    <PageHeader title="Tasks" description="Manage goals, plans, execution, approvals, verification, and results as one workflow.">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={overview.tasks?.source_updated_at || overview.current_task.source_updated_at} stale={overview.tasks?.stale || overview.current_task.stale} />
    </PageHeader>
    {createRequested ? <section className="panel task-create"><h3>Give AEGIS a new task</h3><p>Describe the outcome you want in natural language.</p><textarea aria-label="Desired outcome" value={instruction} onChange={(event) => setInstruction(event.currentTarget.value)} disabled={creating} /><footer><a className="secondary-button" href="/dashboard/work/tasks">Cancel</a><ActionButton level="controlled" busy={creating} onClick={() => void createTask()}>Send to AEGIS</ActionButton></footer></section> : null}
    {notice ? <div className="data-state" role="status" aria-live="polite">{notice}</div> : null}
    {warnings.length ? <div className="data-state data-state--warning" role="status">Some data could not be loaded: {warnings.join(" / ")}</div> : null}
    <FilterBar query={query} status={statusFilter} statuses={taskStatuses} onQuery={(value) => { setQuery(value); setPage(1); }} onStatus={(value) => { setStatusFilter(value); setPage(1); }}>
      <SavedViewPicker views={views} selected={selectedView} onSelect={selectView} onSave={() => void saveView()} onDelete={(id) => void removeView(id)} />
    </FilterBar>
    <div className="tab-strip" role="tablist" aria-label="Work queues">
      {[["", "All"], ["running", "Running"], ["waiting_approval", "Awaiting approval"], ["completed", "Completed"], ["failed", "Failed"]].map(([value, label]) => <button className="tab-chip" role="tab" aria-selected={statusFilter === value} type="button" onClick={() => { setStatusFilter(value); setPage(1); }} key={value || "all"}>{label}</button>)}
    </div>
    <div className="tasks-layout">
      <section className="panel task-master">
        <DataState loading={loading} error={error} empty={!records.length} onRetry={() => void load()} />
        {!loading && !error ? <ResponsiveDataView headers={["Task", "Status", "Owner", "Last updated"]} rows={records.map((record) => ({
          id: record.id, selected: record.id === selected?.id, onSelect: () => setSelectedId(record.id),
          cells: [<strong>{record.title}</strong>, <StatusBadge status={record.status} />, record.owner || "AEGIS", formatDateTime(record.updated_at)],
          card: <><header><strong>{record.title}</strong><StatusBadge status={record.status} /></header><p>{String(record.data?.goal || record.subtitle || "No goal set")}</p><small>{formatDateTime(record.updated_at)}</small></>,
        }))} /> : null}
        <Pagination page={page} total={total} pageSize={pageSize} onPage={setPage} />
      </section>
      <section className="panel task-detail" aria-label="Task details">
        {selected ? <><header><div><span className="mono">{selected.id}</span><h2>{selected.title}</h2></div><StatusBadge status={selected.status} /></header>
          <dl className="task-facts"><div><dt>Goal</dt><dd>{String(data.goal || data.objective || selected.title)}</dd></div><div><dt>Decision Context</dt><dd>{String(data.decision_context_summary || data.plan_summary || "No record")}</dd></div><div><dt>Current action</dt><dd>{String(data.current_action || data.current_step_name || "Waiting")}</dd></div><div><dt>Next action</dt><dd>{String(data.next_action || "Not set")}</dd></div><div><dt>Verification</dt><dd>{String(data.verification_summary || data.verification_status || "Not verified")}</dd></div><div><dt>Final result</dt><dd>{String(data.final_output || data.result_summary || "Incomplete")}</dd></div></dl>
          <section className="task-timeline"><h3>Execution timeline</h3>{steps.map((step, index) => <article key={String(step.step_id || index)}><span>{index + 1}</span><div><strong>{String(step.description || step.name || step.capability_id || `Step ${index + 1}`)}</strong><small>{String(step.capability_id || "")}</small></div><StatusBadge status={String(step.status || "pending")} /></article>)}{relatedApprovals.map((approval) => <article key={approval.approval_id}><span>Approval</span><div><strong>{approval.summary || approval.capability_id}</strong><small>{approval.reason}</small></div><StatusBadge status="WAITING" /></article>)}{relatedErrors.map((item, index) => <article key={String(item.id || index)}><span>Incident</span><div><strong>{String(item.title || item.message || "Error")}</strong><small>{String(item.recovery_hint || "")}</small></div><StatusBadge status="ERROR" /></article>)}</section>
          <div className="task-actions">{["pause", "resume", "retry", "cancel"].map((action) => <ActionButton level={actionLevel[action]} busy={actionBusy} onClick={() => void requestAction(action)} key={action}>{({ pause: "Pause", resume: "Resume", retry: "Retry", cancel: "Cancel" } as Record<string, string>)[action]}</ActionButton>)}</div>
        </> : <DataState empty />}
      </section>
    </div>
    <ConfirmDialog open={Boolean(preview)} title={`Task action: ${preview?.action || ""}`} details={preview?.detail || {}} dangerous={preview?.action === "cancel"} busy={actionBusy} onCancel={() => setPreview(undefined)} onConfirm={() => void confirmAction()} />
  </div>;
}

function entityFromOverview(overview: UiOverview): EntitySummary | undefined {
  const task = overview.current_task.data;
  if (!task.task_id && !task.title) return undefined;
  return {
    id: task.task_id || "current-task",
    type: "task",
    title: task.title || "Current task",
    subtitle: task.current_action || "",
    status: task.phase || "running",
    severity: task.blocked_reason ? "warning" : "normal",
    updated_at: task.updated_at || overview.current_task.source_updated_at,
    owner: "AEGIS",
    tags: [],
    relations: [],
    available_actions: [],
    permissions: ["view"],
    data: { ...task },
  };
}
