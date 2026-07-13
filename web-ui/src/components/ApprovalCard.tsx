import { Check, ShieldAlert, X } from "lucide-react";
import { useState } from "react";
import { resolveApproval } from "../api/client";
import type { ApprovalItem } from "../types";

type Props = {
  approval: ApprovalItem;
  readonly?: boolean;
};

export function ApprovalCard({ approval, readonly = false }: Props) {
  const [busy, setBusy] = useState<string>("");
  const [error, setError] = useState("");

  async function decide(decision: "approve" | "reject") {
    setBusy(decision);
    setError("");
    try {
      await resolveApproval(approval.approval_id, decision);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy("");
    }
  }

  return (
    <article className="approval-card">
      <div className="panel__header">
        <div>
          <strong>{approval.summary || approval.tool_name || "Approval required"}</strong>
          <div className="muted mono">{approval.approval_id}</div>
        </div>
        <span className="status-badge" data-status="WAITING">
          <ShieldAlert size={14} aria-hidden="true" />
          {approval.risk || "risk"}
        </span>
      </div>
      <div className="muted">{approval.reason || "Review the requested action before allowing it to continue."}</div>
      <div className="stat-grid">
        <div className="stat">
          <span className="muted">Capability</span>
          <b className="mono stat__value--small">{approval.capability_id}</b>
        </div>
        <div className="stat">
          <span className="muted">Target</span>
          <b className="stat__value--small">{approval.target || "Not specified"}</b>
        </div>
      </div>
      <div className="approval-detail-grid">
        <Detail label="Side effects" value={approval.side_effects} />
        <Detail label="Previous action" value={approval.previous_action} />
        <Detail label="Similar history" value={approval.similar_action_summary} />
        <Detail label="Expected effect" value={approval.expected_effect} />
        <Detail label="Fresh auth" value={approval.fresh_auth_required ? "Required" : "Not required for this request"} />
        <Detail label="Task" value={approval.task_id || "Not linked"} />
      </div>
      {approval.preview ? <pre className="approval-preview mono">{approval.preview}</pre> : null}
      {error ? <div className="attention-item" data-severity="critical">{error}</div> : null}
      {!readonly ? (
        <div className="approval-card__actions">
          <button className="primary-button" onClick={() => decide("approve")} disabled={!!busy}>
            <Check size={16} aria-hidden="true" /> {busy === "approve" ? "Approving" : "Approve"}
          </button>
          <button className="danger-button" onClick={() => decide("reject")} disabled={!!busy}>
            <X size={16} aria-hidden="true" /> {busy === "reject" ? "Rejecting" : "Reject"}
          </button>
        </div>
      ) : null}
    </article>
  );
}

function Detail({ label, value }: { label: string; value?: unknown }) {
  const text = Array.isArray(value) ? value.join(", ") : String(value || "Not reported");
  return (
    <div className="approval-detail">
      <span>{label}</span>
      <strong>{text}</strong>
    </div>
  );
}
