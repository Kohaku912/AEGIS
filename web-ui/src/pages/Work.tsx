import type { UiOverview } from "../types";
import { useEffect, useMemo, useState } from "react";
import { fetchResourceEntities, runTaskAction, sendChat } from "../api/client";
import { taskBuckets, serverFromCapabilityId, serverLabel } from "../displayModel";
import type { CurrentTask, EntitySummary } from "../types";

export function Work({ overview }: { overview: UiOverview }) {
  const overviewTask = overview.current_task.data;
  const [records, setRecords] = useState<EntitySummary[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [instruction, setInstruction] = useState("");
  const [preview, setPreview] = useState<{ action: string; detail: Record<string, unknown> }>();
  const [status, setStatus] = useState("");
  useEffect(() => { let active = true; fetchResourceEntities("tasks").then((page) => { if (active) setRecords(page.items); }).catch(() => undefined); return () => { active = false; }; }, []);
  const selectedRecord = useMemo(() => records.find((item) => item.id === selectedId) || records.find((item) => item.id === overviewTask.task_id), [overviewTask.task_id, records, selectedId]);
  const task = selectedRecord ? taskFromEntity(selectedRecord, overviewTask) : overviewTask;
  const buckets = taskBuckets(overview);
  const steps = task.steps || [];
  const activeCapability = task.capability_id || String(steps.find((step) => String(step.status || "").toLowerCase() === "running")?.capability_id || "");
  const pendingApprovals = (overview.approvals.data.pending || []).filter((approval) => approval.task_id === task.task_id || approval.capability_id === activeCapability);
  const usedMemory = overview.memory?.data?.summary || overview.mind_summary.data?.memory || {};
  const usage = overview.usage.data || {};
  const recentResult = [...steps].reverse().map((step) => resultPreview(step)).find(Boolean);
  const dependencyEdges = task.dependency_edges || [];
  const createRequested = new URLSearchParams(window.location.search).get("create") === "1";
  const createTask = async () => {
    if (!instruction.trim()) return;
    setStatus("Sending instruction through the LLM task interpretation path...");
    try { await sendChat(instruction); setInstruction(""); setStatus("Instruction accepted. AEGIS will create and plan the task through its normal LLM path."); }
    catch (error) { setStatus(error instanceof Error ? error.message : "Task instruction failed"); }
  };
  const previewAction = async (action: string) => {
    if (!task.task_id) return;
    try { const result = await runTaskAction(task.task_id, action); setPreview({ action, detail: result.preview as Record<string, unknown> }); }
    catch (error) { setStatus(error instanceof Error ? error.message : "Task action preview failed"); }
  };
  const confirmAction = async () => {
    if (!preview || !task.task_id) return;
    try { const result = await runTaskAction(task.task_id, preview.action, true); if (result.result) setStatus(`${preview.action} completed and Manager state was re-read.`); else setStatus(`${preview.action} requires its approval/fresh-auth execution workflow.`); setPreview(undefined); }
    catch (error) { setStatus(error instanceof Error ? error.message : "Task action failed"); }
  };
  return (
    <div className="grid">
      {createRequested ? <section className="panel task-create"><div><h2>Create Task</h2><p className="muted">The instruction is interpreted by the LLM; UI code does not classify or route user intent.</p></div><textarea aria-label="Task instruction" value={instruction} onChange={(event) => setInstruction(event.currentTarget.value)} placeholder="Describe the outcome you want AEGIS to achieve" /><footer><a className="secondary-button" href="/dashboard/work/tasks">Cancel</a><button className="primary-button" type="button" onClick={() => void createTask()}>Send to AEGIS</button></footer></section> : null}
      {status ? <div className="attention-item" data-severity={status.includes("failed") ? "warning" : "info"}>{status}</div> : null}
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Work</h2>
            <div className="muted">Tasks grouped by operational state. Active task detail is shown on the right.</div>
          </div>
        </div>
        <div className="tab-strip" role="tablist" aria-label="Work queues">
          {buckets.map((bucket) => (
            <button className="tab-chip" key={bucket.id} type="button" aria-selected={bucket.id === "active"}>
              <span>{bucket.label}</span>
              <strong>{bucket.count}</strong>
            </button>
          ))}
        </div>
      </section>
      <section className="work-layout">
        <div className="panel">
          <div className="panel__header"><h2>Task List</h2></div>
          <div className="grid">
            {records.length ? records.map((record) => (
              <button type="button" className="list-row task-list-row" data-selected={record.id === task.task_id} onClick={() => setSelectedId(record.id)} key={record.id}>
                <div>
                  <strong>{record.title || "Untitled task"}</strong>
                  <div className="muted">{record.status} / {String(record.data?.priority ?? "normal")} priority</div>
                </div>
                <span className="status-badge" data-status={record.status.toUpperCase()}>{record.status}</span>
              </button>
            )) : task.task_id || task.title ? <article className="list-row" data-selected="true"><div><strong>{task.title || "Untitled task"}</strong><div className="muted">{task.phase || "unknown"} / {steps.length} step(s)</div></div><span className="status-badge" data-status={String(task.phase || "ACTIVE").toUpperCase()}>{task.phase || "active"}</span></article> : (
              <div className="attention-item" data-severity="normal">No active task. Scheduled and historical queues will appear here when reported by Overview v3.</div>
            )}
          </div>
        </div>
        <div className="panel">
          <div className="panel__header">
            <div>
              <h2>Task Detail</h2>
              <div className="muted mono">{task.task_id || "No task id"}</div>
            </div>
          </div>
          <div className="stat-grid">
            <div className="stat"><span className="muted">Objective</span><b>{task.title || "No data yet"}</b></div>
            <div className="stat"><span className="muted">Phase</span><b>{task.phase || "No data yet"}</b></div>
            <div className="stat"><span className="muted">Current capability</span><b className="mono">{activeCapability || "No data yet"}</b></div>
            <div className="stat"><span className="muted">Execution server</span><b>{activeCapability ? serverLabel(serverFromCapabilityId(activeCapability)) : "No data yet"}</b></div>
          </div>
          <div className="task-narrative">
            <div><span className="muted">Original instruction</span><strong>{String(task.original_instruction || task.title || task.task_id || "No data yet")}</strong></div>
            <div><span className="muted">AI plan</span><strong>{String(task.plan_summary || "No data yet")}</strong></div>
            <div><span className="muted">Current action</span><strong>{task.current_action || "No data yet"}</strong></div>
            <div><span className="muted">Next action</span><strong>{task.next_action || "No data yet"}</strong></div>
            <div><span className="muted">Blocked reason</span><strong>{task.blocked_reason || "Not blocked"}</strong></div>
            <div><span className="muted">Latest result</span><strong>{recentResult || "No data yet"}</strong></div>
          </div>
          <div className="work-insight-grid" aria-label="Task operational context">
            <div className="mini-panel">
              <h3>Plan / Dependency</h3>
              <p className="muted">{steps.length ? `${steps.length} step plan, ${dependencyEdges.length} dependency edge(s).` : "No step plan reported."}</p>
            </div>
            <div className="mini-panel">
              <h3>Approvals</h3>
              <p className="muted">{pendingApprovals.length ? `${pendingApprovals.length} approval waiting for this task.` : "No approval currently blocks this task."}</p>
            </div>
            <div className="mini-panel">
              <h3>Memories Used</h3>
              <p className="muted">{memoryPreview(usedMemory)}</p>
            </div>
            <div className="mini-panel">
              <h3>Model / Cost</h3>
              <p className="muted">{String(task.cost_summary || usage.summary || usage.total_tokens || usage.cost || "No data yet")}</p>
            </div>
            <div className="mini-panel">
              <h3>Completion / Verification</h3>
              <p className="muted">{task.verification_summary || verificationPreview(steps) || "No verification result reported."}</p>
            </div>
            <div className="mini-panel">
              <h3>Audit / Output</h3>
              <p className="muted">{task.audit_group_id ? `Audit ${task.audit_group_id}. ` : ""}{String(task.final_output || (task as Record<string, unknown>).result || "No data yet")}</p>
            </div>
          </div>
          {dependencyEdges.length ? (
            <div className="dependency-chain" aria-label="Task dependency graph">
              {dependencyEdges.slice(0, 12).map((edge, index) => (
                <span key={`${String(edge.from)}-${String(edge.to)}-${index}`}>{String(edge.from)} {"->"} {String(edge.to)}</span>
              ))}
            </div>
          ) : null}
          <div className="step-list">
            {steps.map((step, index) => (
              <article className="step-row" key={String(step.step_id || index)}>
                <span className="step-index">{index + 1}</span>
                <div>
                  <strong>{String(step.description || step.capability_id || step.name || `Step ${index + 1}`)}</strong>
                  <div className="muted mono">{String(step.capability_id || step.name || "No capability reported")}</div>
                </div>
                <span className="status-badge" data-status={String(step.status || "UNKNOWN").toUpperCase()}>{String(step.status || "unknown")}</span>
              </article>
            ))}
            {!steps.length ? <div className="attention-item" data-severity="normal">No step history reported.</div> : null}
          </div>
          {task.task_id ? <div className="task-actions"><button className="secondary-button" type="button" onClick={() => void previewAction("pause")}>Pause</button><button className="secondary-button" type="button" onClick={() => void previewAction("resume")}>Resume</button><button className="secondary-button" type="button" onClick={() => void previewAction("retry")}>Retry</button><button className="danger-button" type="button" onClick={() => void previewAction("cancel")}>Cancel</button></div> : null}
          {preview ? <section className="action-preview"><h3>Review task action</h3><dl>{Object.entries(preview.detail).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{String(value)}</dd></div>)}</dl><footer><button className="secondary-button" type="button" onClick={() => setPreview(undefined)}>Cancel</button><button className="primary-button" type="button" onClick={() => void confirmAction()}>Confirm {preview.action}</button></footer></section> : null}
        </div>
      </section>
    </div>
  );
}

function taskFromEntity(entity: EntitySummary, fallback: CurrentTask): CurrentTask {
  const data = entity.data || {};
  return {
    ...fallback,
    ...(data as Partial<CurrentTask>),
    task_id: String(data.task_id || entity.id),
    title: String(data.title || entity.title),
    phase: String(data.phase || data.status || entity.status),
    current_action: String(data.current_action || data.current_step_name || "No action reported"),
    next_action: String(data.next_action || "No next action reported"),
    blocked_reason: String(data.blocked_reason || data.error || ""),
    steps: Array.isArray(data.steps) ? data.steps as Array<Record<string, unknown>> : [],
  };
}

function resultPreview(step: Record<string, unknown>): string {
  const result = step.result;
  if (!result) return "";
  if (typeof result === "string") return result.slice(0, 160);
  if (typeof result === "object") {
    const record = result as Record<string, unknown>;
    return String(record.summary || record.status || record.message || JSON.stringify(record).slice(0, 160));
  }
  return String(result);
}

function verificationPreview(steps: Array<Record<string, unknown>>): string {
  const verification = [...steps].reverse().map((step) => step.verification || step.completion || step.postcondition).find(Boolean);
  if (!verification) return "";
  if (typeof verification === "string") return verification;
  if (typeof verification === "object") {
    const record = verification as Record<string, unknown>;
    return String(record.status || record.summary || record.message || JSON.stringify(record).slice(0, 140));
  }
  return String(verification);
}

function memoryPreview(value: unknown): string {
  if (!value || typeof value !== "object") return "No data yet";
  const record = value as Record<string, unknown>;
  const parts = ["episodic", "semantic", "procedural", "advanced"]
    .map((key) => {
      const item = record[key];
      if (typeof item === "number" || typeof item === "string") return `${key}: ${item}`;
      if (item && typeof item === "object") {
        const itemRecord = item as Record<string, unknown>;
        return `${key}: ${itemRecord.total || itemRecord.count || itemRecord.total_entries || itemRecord.total_episodes || "reported"}`;
      }
      return "";
    })
    .filter(Boolean);
  return parts.length ? parts.join(", ") : "No data yet";
}

