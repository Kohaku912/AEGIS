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
          <b className="mono" style={{ fontSize: 14 }}>{approval.capability_id}</b>
        </div>
        <div className="stat">
          <span className="muted">Target</span>
          <b style={{ fontSize: 14 }}>{approval.target || "Not specified"}</b>
        </div>
      </div>
      {approval.preview ? <pre className="panel mono" style={{ whiteSpace: "pre-wrap", margin: 0 }}>{approval.preview}</pre> : null}
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
