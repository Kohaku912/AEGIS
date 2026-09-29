import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  archiveUserState,
  checkStatusNow,
  continueTask,
  dismissNotification,
  fetchAutonomousStatus,
  fetchManagerTasks,
  fetchAutonomousThreshold,
  fetchMemorySleepStatus,
  fetchNotifications,
  fetchRepairStatus,
  fetchUserStateCurrent,
  fetchUserStateDays,
  fetchUserStateEvents,
  generateAutonomousDailyPlan,
  markNotificationRead,
  pollUserStatePc,
  runControlAction,
  setRepairDisabled,
  startAutonomous,
  stopAutonomous,
  triggerAutonomous,
  triggerMemorySleep,
  updateAutonomousThreshold,
} from "../api/client";
import { ConfirmDialog, PageHeader } from "../components/DashboardPrimitives";
import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";
import { RecordList, asRecord, asRecords, recordSummary, recordTitle, text, time } from "./PageSupport";

export function ControlHubPage({
  overview,
  onNavigate,
}: {
  overview: UiOverview;
  onNavigate: (path: string) => void;
}) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const [thresholdDraft, setThresholdDraft] = useState("");
  const [control, setControl] = useState<{ action: string; preview: Record<string, unknown> }>();
  const cockpitActions = overview.cockpit_actions?.data.items || [];
  const understanding = asRecord(overview.user_understanding?.data);
  const authority = asRecord(understanding.delegated_authority_state);
  const blockedCategories = Array.isArray(authority.blocked_categories) ? authority.blocked_categories : [];
  const approvals = overview.approvals?.data.pending || [];
  const goals = asRecords(overview.goals?.data.open);

  const notificationsQuery = useQuery({
    queryKey: ["control-hub", "notifications"],
    queryFn: () => fetchNotifications(false, 12),
  });
  const autonomousQuery = useQuery({
    queryKey: ["control-hub", "autonomous-status"],
    queryFn: fetchAutonomousStatus,
  });
  const thresholdQuery = useQuery({
    queryKey: ["control-hub", "autonomous-threshold"],
    queryFn: fetchAutonomousThreshold,
  });
  const sleepQuery = useQuery({
    queryKey: ["control-hub", "sleep-status"],
    queryFn: fetchMemorySleepStatus,
  });
  const userStateCurrentQuery = useQuery({
    queryKey: ["control-hub", "user-state-current"],
    queryFn: fetchUserStateCurrent,
  });
  const userStateEventsQuery = useQuery({
    queryKey: ["control-hub", "user-state-events"],
    queryFn: () => fetchUserStateEvents(6),
  });
  const userStateDaysQuery = useQuery({
    queryKey: ["control-hub", "user-state-days"],
    queryFn: fetchUserStateDays,
  });
  const repairQuery = useQuery({
    queryKey: ["control-hub", "repair"],
    queryFn: fetchRepairStatus,
  });
  const followupTasksQuery = useQuery({
    queryKey: ["control-hub", "followup-tasks"],
    queryFn: () => fetchManagerTasks({ source: "autonomous", limit: 30 }),
  });

  const followups = useMemo(() => {
    const live = asRecords(followupTasksQuery.data);
    const preferred = live.filter((item) => {
      const metadata = asRecord(item.metadata);
      const status = String(item.status || "").toLowerCase();
      return (
        status !== "completed"
        && status !== "cancelled"
        && status !== "expired"
        && Boolean(item.followup_kind || metadata.followup_kind || metadata.origin === "user_understanding")
      );
    });
    if (preferred.length) return preferred;
    return goals.filter((item) => {
      const metadata = asRecord(item.metadata);
      return Boolean(item.followup_kind || metadata.followup_kind || metadata.origin === "user_understanding");
    });
  }, [followupTasksQuery.data, goals]);

  const thresholdValue = useMemo(() => {
    const value = thresholdDraft.trim();
    if (value) return value;
    return String(thresholdQuery.data?.threshold ?? 2);
  }, [thresholdDraft, thresholdQuery.data?.threshold]);

  const perform = async (label: string, job: () => Promise<unknown>, refresh?: string[]) => {
    setBusyAction(label);
    setStatus(`${label} を実行しています...`);
    try {
      await job();
      if (refresh?.length) {
        await Promise.all(refresh.map((key) => queryClient.invalidateQueries({ queryKey: ["control-hub", key] })));
      }
      setStatus(`${label} が完了しました。`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : `${label} に失敗しました。`);
    } finally {
      setBusyAction("");
    }
  };

  const previewControl = async (action: string) => {
    setBusyAction(action);
    setStatus("Manager-backed action preview を生成しています...");
    try {
      const payload = await runControlAction(action);
      setControl({ action, preview: (payload.preview as Record<string, unknown>) || payload });
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "control preview に失敗しました。");
    } finally {
      setBusyAction("");
    }
  };

  const confirmControl = async () => {
    if (!control) return;
    const action = control.action;
    await perform(
      action,
      () => runControlAction(action, true),
      ["autonomous-status", "repair", "notifications"],
    );
    setControl(undefined);
  };

  return (
    <div className="grid">
      <PageHeader
        title="Control Hub"
        description="主要な運用操作を 1 画面で実行し、状態確認まで続けられる制御面です。"
      >
        <div className="command-controls">
          <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/atlas")}>
            Open Ops Atlas
          </button>
          <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/interventions")}>
            Open interventions
          </button>
        </div>
      </PageHeader>

      <section className="panel control-hub-hero">
        <div>
          <span className="muted">Unified operations</span>
          <h2>通知、autonomy、runtime 同期、repair をここから制御</h2>
          <p>
            調査ページへ移動する前に、まず今止める・流す・再取得するべき操作をまとめています。
          </p>
        </div>
        <div className="home-summary-grid">
          <Metric label="Controls" value={String(cockpitActions.length)} />
          <Metric label="Unread" value={String(notificationsQuery.data?.filter((item) => !item.read).length || 0)} />
          <Metric label="Autonomy" value={String(autonomousQuery.data?.running ? "Running" : "Stopped")} />
          <Metric label="Repair" value={String(repairQuery.data?.disabled ? "Disabled" : "Enabled")} />
        </div>
      </section>

      {status ? <div className="data-state">{status}</div> : null}

      <section className="control-hub-grid">
        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Authority and approvals</h2>
              <div className="muted">今どこで止まっているかと、委任境界をまとめて見ます。</div>
            </div>
            <StatusBadge status={approvals.length ? "waiting" : "ready"} />
          </div>
          <div className="control-hub-stack">
            <div className="mission-strip">
              <span>Pending approvals: <strong>{String(approvals.length)}</strong></span>
              <span>Blocked categories: <strong>{blockedCategories.length ? blockedCategories.join(", ") : "none"}</strong></span>
            </div>
            <p className="muted">{text(authority.summary, "委任状態の summary はありません。")}</p>
            <RecordList
              items={approvals.slice(0, 4)}
              empty="保留中の approval はありません。"
              render={(item) => (
                <div>
                  <strong>{recordTitle(item, "Approval")}</strong>
                  <p>{recordSummary(item)}</p>
                </div>
              )}
            />
            <div className="command-controls">
              <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/approvals")}>
                Open approvals
              </button>
              <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/personal-ai")}>
                Open authority view
              </button>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Follow-up backlog</h2>
              <div className="muted">user understanding から materialize された paused goal を確認します。</div>
            </div>
            <StatusBadge status={followups.length ? "paused" : "idle"} />
          </div>
          <div className="control-hub-stack">
            <RecordList
              items={followups.slice(0, 6)}
              empty="visible な follow-up goal はありません。"
              render={(item) => {
                const metadata = asRecord(item.metadata);
                const kind = text(item.followup_kind || metadata.followup_kind, "followup");
                const taskId = text(item.task_id, "");
                return (
                  <div>
                    <strong>{recordTitle(item, "Goal")}</strong>
                    <p>{recordSummary(item)}</p>
                    <small>{`${kind} / confidence ${text(item.confidence || metadata.confidence, "0")}`}</small>
                    {taskId !== "" ? (
                      <div className="command-controls">
                        <button
                          className="secondary-button"
                          type="button"
                          onClick={() =>
                            void perform(
                              "Continue follow-up",
                              () => continueTask(taskId),
                              ["followup-tasks", "autonomous-status"],
                            )
                          }
                        >
                          Continue
                        </button>
                      </div>
                    ) : null}
                  </div>
                );
              }}
            />
            <div className="command-controls">
              <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/agent-state")}>
                Open goals
              </button>
              <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/personal-ai")}>
                Open Personal AI
              </button>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Master controls</h2>
              <div className="muted">policy と audit を通るマスター操作です。</div>
            </div>
            <Freshness {...freshProps(overview.cockpit_actions || overview.core)} />
          </div>
          <div className="control-hub-actions">
            {cockpitActions.map((item) => (
              <button
                key={String(item.action || item.id || item.label)}
                className="atlas-page-card"
                type="button"
                onClick={() => void previewControl(String(item.action || item.id))}
                disabled={Boolean(busyAction)}
              >
                <strong>{String(item.label || item.action)}</strong>
                <span>{String(item.message || item.description || "Preview required")}</span>
                <small>{String(item.level || "controlled")}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Autonomous loop</h2>
              <div className="muted">start / stop / trigger / threshold / daily plan</div>
            </div>
            <StatusBadge status={String(autonomousQuery.data?.running ? "running" : "stopped")} />
          </div>
          <div className="control-hub-stack">
            <div className="mission-strip">
              <span>Running: <strong>{String(autonomousQuery.data?.running ?? false)}</strong></span>
              <span>Next: <strong>{text(autonomousQuery.data?.next_run_at || autonomousQuery.data?.next_run_ms, "—")}</strong></span>
            </div>
            <label className="metric-row">
              <span>Threshold</span>
              <input
                type="number"
                step="0.1"
                value={thresholdValue}
                onChange={(event) => setThresholdDraft(event.currentTarget.value)}
              />
            </label>
            <div className="command-controls">
              <button className="secondary-button" type="button" onClick={() => void perform("Autonomy start", startAutonomous, ["autonomous-status"])}>
                Start
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Autonomy stop", stopAutonomous, ["autonomous-status"])}>
                Stop
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Autonomy trigger", triggerAutonomous, ["autonomous-status"])}>
                Trigger now
              </button>
              <button
                className="secondary-button"
                type="button"
                onClick={() =>
                  void perform(
                    "Threshold update",
                    () => updateAutonomousThreshold(Number(thresholdValue || "0")),
                    ["autonomous-threshold", "autonomous-status"],
                  )
                }
              >
                Save threshold
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Daily plan", () => generateAutonomousDailyPlan(), ["autonomous-status"])}>
                Generate daily plan
              </button>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Runtime sync</h2>
              <div className="muted">status / memory / user state を明示的に再取得・同期します。</div>
            </div>
          </div>
          <div className="control-hub-stack">
            <div className="mission-strip">
              <span>Sleep: <strong>{text(sleepQuery.data?.running || sleepQuery.data?.sleeping, "—")}</strong></span>
              <span>User state events: <strong>{String(userStateEventsQuery.data?.events?.length || 0)}</strong></span>
            </div>
            <div className="command-controls">
              <button className="secondary-button" type="button" onClick={() => void perform("Status refresh", checkStatusNow)}>
                Check systems now
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Memory sleep", triggerMemorySleep, ["sleep-status"])}>
                Trigger memory sleep
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Archive user state", archiveUserState, ["user-state-days"])}>
                Archive user state
              </button>
              <button className="secondary-button" type="button" onClick={() => void perform("Poll PC state", pollUserStatePc, ["user-state-current", "user-state-events"])}>
                Poll PC now
              </button>
            </div>
            <div className="home-summary-grid">
              <Metric label="Current state keys" value={String(Object.keys(userStateCurrentQuery.data || {}).length)} />
              <Metric label="Recent events" value={String(userStateEventsQuery.data?.events?.length || 0)} />
              <Metric label="Archived days" value={String(Object.keys(userStateDaysQuery.data || {}).length)} />
              <Metric label="Sleep state" value={String(sleepQuery.data?.running || sleepQuery.data?.sleeping || "idle")} />
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Notifications</h2>
              <div className="muted">未読確認と read / dismiss をここで実行できます。</div>
            </div>
            <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/communications/notifications")}>
              Open full page
            </button>
          </div>
          <div className="compact-list">
            {(notificationsQuery.data || []).map((item, index) => {
              const notificationId = String(item.notification_id || item.id || index);
              return (
                <article className="list-row" key={notificationId}>
                  <div>
                    <strong>{text(item.title, "通知")}</strong>
                    <p>{text(item.message || item.summary)}</p>
                    <small>{time(item.created_at || item.updated_at)}</small>
                  </div>
                  <div className="command-controls">
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => void perform("Mark notification read", () => markNotificationRead(notificationId), ["notifications"])}
                    >
                      Read
                    </button>
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => void perform("Dismiss notification", () => dismissNotification(notificationId), ["notifications"])}
                    >
                      Dismiss
                    </button>
                  </div>
                </article>
              );
            })}
            {!notificationsQuery.data?.length ? <p className="muted">通知はありません。</p> : null}
          </div>
        </section>

        <section className="panel">
          <div className="panel__header">
            <div>
              <h2>Repair mode</h2>
              <div className="muted">repair manager の状態を確認し、disable を切り替えます。</div>
            </div>
            <StatusBadge status={String(repairQuery.data?.disabled ? "disabled" : "enabled")} />
          </div>
          <div className="control-hub-stack">
            <div className="mission-strip">
              <span>Disabled: <strong>{String(repairQuery.data?.disabled ?? false)}</strong></span>
              <span>Status: <strong>{text(repairQuery.data?.status, "—")}</strong></span>
            </div>
            <div className="command-controls">
              <button
                className="secondary-button"
                type="button"
                onClick={() => void perform("Disable repair", () => setRepairDisabled(true), ["repair"])}
              >
                Disable repair
              </button>
              <button
                className="secondary-button"
                type="button"
                onClick={() => void perform("Enable repair", () => setRepairDisabled(false), ["repair"])}
              >
                Enable repair
              </button>
              <button className="secondary-button" type="button" onClick={() => onNavigate("/dashboard/incidents")}>
                Open incidents
              </button>
            </div>
          </div>
        </section>
      </section>

      <ConfirmDialog
        open={Boolean(control)}
        title={`Control action: ${control?.action || ""}`}
        details={control?.preview || {}}
        dangerous={control?.action === "emergency-stop"}
        busy={Boolean(busyAction)}
        onCancel={() => setControl(undefined)}
        onConfirm={() => void confirmControl()}
      />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function freshProps(envelope?: { generated_at?: number | string; source_updated_at?: number | string; stale?: boolean }) {
  const generatedAt = Number(envelope?.generated_at || envelope?.source_updated_at || Date.now());
  const sourceUpdatedAt = Number(envelope?.source_updated_at || envelope?.generated_at || Date.now());
  return {
    generatedAt,
    sourceUpdatedAt,
    stale: Boolean(envelope?.stale),
  };
}
