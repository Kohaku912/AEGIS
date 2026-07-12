import { ApprovalCard } from "../components/ApprovalCard";
import { Freshness } from "../components/Freshness";
import type { UiOverview } from "../types";

export function Approvals({ overview }: { overview: UiOverview }) {
  const approvals = overview.approvals.data.pending || [];
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h2>Approvals</h2>
          <div className="muted">Pending, high-risk, and expiring action requests.</div>
        </div>
        <Freshness generatedAt={overview.approvals.generated_at} sourceUpdatedAt={overview.approvals.source_updated_at} stale={overview.approvals.stale} />
      </div>
      <div className="grid">
        {approvals.map((approval) => <ApprovalCard approval={approval} key={approval.approval_id} />)}
        {!approvals.length ? <div className="attention-item" data-severity="normal">No pending approvals.</div> : null}
      </div>
    </section>
  );
}
