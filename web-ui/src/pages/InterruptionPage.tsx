import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  fetchInterruptionStatus,
  releaseInterruptionBatch,
  setInterruptionEmergencyStop,
  type InterruptionStatus,
} from "../api/client";
import { ActionButton, ConfirmDialog, DataState, PageHeader, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime } from "../i18n";

const EMPTY: InterruptionStatus = { emergencyStop: false, batchedCount: 0, batched: [] };

/** A held entry is `{ notification: {...}, decision: {decision, reason}, batched_at }`. */
function nested(entry: Record<string, unknown>, key: string): Record<string, unknown> {
  const value = entry[key];
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function stamp(value: unknown): string {
  const ms = Number(value || 0);
  return ms ? formatDateTime(ms) : "—";
}

export function InterruptionPage() {
  const [status, setStatus] = useState<InterruptionStatus>(EMPTY);
  const [released, setReleased] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState("");
  const [confirmStop, setConfirmStop] = useState(false);
  const [reload, setReload] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setStatus(await fetchInterruptionStatus());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, reload]);

  const applyStop = async (active: boolean) => {
    setBusy(true);
    setActionError("");
    try {
      setStatus(await setInterruptionEmergencyStop(active));
      setConfirmStop(false);
    } catch (reason) {
      setActionError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const release = async () => {
    setBusy(true);
    setActionError("");
    try {
      setReleased(await releaseInterruptionBatch());
      setStatus(await fetchInterruptionStatus());
    } catch (reason) {
      setActionError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const heldRows = status.batched.map((entry, index) => {
    const notification = nested(entry, "notification");
    const decision = nested(entry, "decision");
    const id = String(notification.notification_id || `held-${index}`);
    const title = String(notification.title || "Untitled");
    const body = String(notification.body || "");
    const verdict = String(decision.decision || "unknown");
    const reason = String(decision.reason || "");
    return {
      id,
      cells: [title, verdict, reason, stamp(entry.batched_at)],
      card: <div className="log-card">
        <strong>{title}</strong>
        <p>{body}</p>
        <p>{verdict} — {reason}</p>
        <small>{stamp(entry.batched_at)}</small>
      </div>,
    };
  });

  const releasedRows = released.map((entry, index) => {
    const notification = nested(entry, "notification");
    const decision = nested(entry, "decision");
    const id = String(notification.notification_id || `released-${index}`);
    return {
      id,
      cells: [String(notification.title || "Untitled"), String(notification.body || ""), String(decision.decision || "unknown")],
      card: <div className="log-card">
        <strong>{String(notification.title || "Untitled")}</strong>
        <p>{String(notification.body || "")}</p>
        <small>{String(decision.decision || "unknown")}</small>
      </div>,
    };
  });

  return <div className="grid">
    <PageHeader
      title="Interruption"
      description="Whether AEGIS may speak to you right now, and what it is holding back. Held notifications wait here rather than being discarded, so nothing is lost by staying quiet."
    >
      <div className="filter-bar">
        <button type="button" className="ghost-button" onClick={() => setReload((value) => value + 1)} disabled={loading || busy}>
          <RefreshCw size={14} aria-hidden="true" />Refresh
        </button>
      </div>
    </PageHeader>

    <DataState
      loading={loading}
      error={error}
      onRetry={() => setReload((value) => value + 1)}
    />

    {actionError ? <p className="data-state data-state--error" role="alert">{actionError}</p> : null}

    {!loading && !error ? <section className="panel">
      <h3>Speaking to you</h3>
      <div className="stat-grid">
        <div className="stat">
          <span className="muted">State</span>
          <b>{status.emergencyStop ? "Silenced" : "Allowed"}</b>
        </div>
        <div className="stat">
          <span className="muted">Held back</span>
          <b>{status.batchedCount}</b>
        </div>
      </div>
      <p className="muted">
        {status.emergencyStop
          ? "Nothing will reach you until you allow it again. Held items keep accumulating."
          : "AEGIS decides per notification, based on your activity, quiet hours, and what you have said you want to hear about."}
      </p>
      <div className="filter-bar">
        {status.emergencyStop
          ? <button type="button" className="primary-button" disabled={busy} onClick={() => void applyStop(false)}>Allow again</button>
          : <ActionButton level="dangerous" busy={busy} onClick={() => setConfirmStop(true)}>Silence everything</ActionButton>}
      </div>
    </section> : null}

    {!loading && !error ? <section className="panel">
      <h3>Held back</h3>
      {status.batchedCount ? <p className="muted">
        {status.batchedCount} notification(s) are waiting. Releasing hands them to you now; the list
        below shows the most recent {status.batched.length}.
      </p> : <p className="muted">Nothing is being held back right now.</p>}
      {heldRows.length ? <ResponsiveDataView
        headers={["Notification", "Decision", "Why", "Held since"]}
        rows={heldRows}
      /> : null}
      {status.batchedCount ? <div className="filter-bar">
        <button type="button" className="primary-button" disabled={busy} onClick={() => void release()}>
          Release now
        </button>
      </div> : null}
    </section> : null}

    {!loading && !error && releasedRows.length ? <section className="panel">
      <h3>Released in this session</h3>
      <ResponsiveDataView
        headers={["Notification", "Body", "Decision"]}
        rows={releasedRows}
      />
    </section> : null}

    {!loading && !error ? <section className="panel">
      <h3>How this decides</h3>
      <p className="muted">
        Today the decision is a hand-written ladder: an emergency stop wins, then notifications you
        flagged as important, then quiet hours, then your current activity. It is a rule of thumb, not
        a model of how much a given interruption is worth to you — so treat a wrong call as expected
        and correctable, not as a considered judgement.
      </p>
    </section> : null}

    <ConfirmDialog
      open={confirmStop}
      title="Stop AEGIS from speaking to you?"
      dangerous
      busy={busy}
      details={{
        effect: "Nothing reaches you until you turn this back on.",
        held: `${status.batchedCount} notification(s) stay held and keep accumulating.`,
        reversible: "Yes — press \"Allow again\" on this page.",
      }}
      onCancel={() => setConfirmStop(false)}
      onConfirm={() => void applyStop(true)}
    />
  </div>;
}
