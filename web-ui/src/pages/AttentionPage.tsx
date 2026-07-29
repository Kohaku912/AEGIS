import { AlertTriangle, CheckCircle2, Server, ShieldQuestion } from "lucide-react";
import { Freshness } from "../components/Freshness";
import { PageHeader, ResponsiveDataView } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type AttentionRow = { id: string; kind: string; title: string; detail: string; status: string; time?: number; href: string };

export function AttentionPage({ overview }: { overview: UiOverview }) {
  const rows: AttentionRow[] = [
    ...(overview.approvals.data.pending || []).map((item) => ({ id: `approval-${item.approval_id}`, kind: "Approval", title: item.summary || item.capability_id, detail: item.reason || item.expected_effect || "Confirmation is required before execution", status: "WAITING", time: item.created_at, href: `/dashboard/governance/approvals?approval=${item.approval_id}` })),
    ...(overview.errors?.data.items || []).filter((item) => !["resolved", "repaired"].includes(String(item.status || "").toLowerCase())).map((item, index) => ({ id: `error-${String(item.id || index)}`, kind: "Error", title: String(item.title || item.error || item.message || "Unresolved error"), detail: String(item.recovery_hint || item.detail || "Review the repair status"), status: String(item.status || item.severity || "ERROR"), time: Number(item.created_at || item.updated_at || 0), href: `/dashboard/repairs?error=${encodeURIComponent(String(item.id || index))}` })),
    ...overview.servers.data.items.filter((item) => ["OFFLINE", "DEGRADED"].includes(String(item.status).toUpperCase())).map((item) => ({ id: `server-${item.server_id}`, kind: "Server", title: item.server_id, detail: item.status_detail || item.degraded_reason || item.recovery_hint || "Check connectivity and dependencies", status: String(item.status), time: item.health_checked_at, href: `/dashboard/infrastructure/servers?server=${item.server_id}` })),
    ...(overview.attention.data.items || []).map((item) => ({ id: `notice-${item.id}`, kind: item.kind || "Notice", title: item.title, detail: item.message || item.recovery_hint || "Review this item", status: item.severity, time: item.created_at, href: "/dashboard/attention" })),
  ];
  const deduped = [...new Map(rows.map((row) => [row.id, row])).values()];
  return <div className="attention-page">
    <PageHeader title="Needs Attention" description="Review approvals, unresolved errors, and offline or degraded servers in one place.">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={Math.min(overview.attention.source_updated_at, overview.servers.source_updated_at)} stale={overview.attention.stale || overview.servers.stale} />
    </PageHeader>
    {deduped.length === 0 ? <div className="attention-clear"><CheckCircle2 /><strong>No items currently need attention.</strong></div> : <ResponsiveDataView
      headers={["Type", "Target", "Details", "Status", "Next action"]}
      rows={deduped.map((row) => ({ id: row.id, onSelect: () => { window.location.href = row.href; }, cells: [row.kind, row.title, row.detail, <StatusBadge status={row.status} />, "Open"], card: <><header>{row.kind === "Approval" ? <ShieldQuestion /> : row.kind === "Server" ? <Server /> : <AlertTriangle />}<strong>{row.title}</strong><StatusBadge status={row.status} /></header><p>{row.detail}</p><span>Open details</span></> }))}
    />}
  </div>;
}
