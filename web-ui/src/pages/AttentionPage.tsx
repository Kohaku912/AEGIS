import { AlertTriangle, CheckCircle2, Server, ShieldQuestion } from "lucide-react";
import { Freshness } from "../components/Freshness";
import { PageHeader, ResponsiveDataView } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type AttentionRow = { id: string; kind: string; title: string; detail: string; status: string; time?: number; href: string };

export function AttentionPage({ overview }: { overview: UiOverview }) {
  const rows: AttentionRow[] = [
    ...(overview.approvals.data.pending || []).map((item) => ({ id: `approval-${item.approval_id}`, kind: "承認", title: item.summary || item.capability_id, detail: item.reason || item.expected_effect || "実行前の確認が必要です", status: "WAITING", time: item.created_at, href: `/dashboard/governance/approvals?approval=${item.approval_id}` })),
    ...(overview.errors?.data.items || []).filter((item) => !["resolved", "repaired"].includes(String(item.status || "").toLowerCase())).map((item, index) => ({ id: `error-${String(item.id || index)}`, kind: "エラー", title: String(item.title || item.error || item.message || "未解決エラー"), detail: String(item.recovery_hint || item.detail || "修復状況を確認してください"), status: String(item.status || item.severity || "ERROR"), time: Number(item.created_at || item.updated_at || 0), href: `/dashboard/repairs?error=${encodeURIComponent(String(item.id || index))}` })),
    ...overview.servers.data.items.filter((item) => ["OFFLINE", "DEGRADED"].includes(String(item.status).toUpperCase())).map((item) => ({ id: `server-${item.server_id}`, kind: "サーバー", title: item.server_id, detail: item.status_detail || item.degraded_reason || item.recovery_hint || "接続と依存関係を確認してください", status: String(item.status), time: item.health_checked_at, href: `/dashboard/infrastructure/servers?server=${item.server_id}` })),
    ...(overview.attention.data.items || []).map((item) => ({ id: `notice-${item.id}`, kind: item.kind || "注意", title: item.title, detail: item.message || item.recovery_hint || "確認してください", status: item.severity, time: item.created_at, href: "/dashboard/attention" })),
  ];
  const deduped = [...new Map(rows.map((row) => [row.id, row])).values()];
  return <div className="attention-page">
    <PageHeader title="対応が必要" description="承認、未解決エラー、オフライン／機能低下したサーバーを一か所で確認できます。">
      <Freshness generatedAt={overview.generated_at} sourceUpdatedAt={Math.min(overview.attention.source_updated_at, overview.servers.source_updated_at)} stale={overview.attention.stale || overview.servers.stale} />
    </PageHeader>
    {deduped.length === 0 ? <div className="attention-clear"><CheckCircle2 /><strong>現在、対応が必要な項目はありません。</strong></div> : <ResponsiveDataView
      headers={["種類", "対象", "内容", "状態", "次の操作"]}
      rows={deduped.map((row) => ({ id: row.id, onSelect: () => { window.location.href = row.href; }, cells: [row.kind, row.title, row.detail, <StatusBadge status={row.status} />, "開く"], card: <><header>{row.kind === "承認" ? <ShieldQuestion /> : row.kind === "サーバー" ? <Server /> : <AlertTriangle />}<strong>{row.title}</strong><StatusBadge status={row.status} /></header><p>{row.detail}</p><span>詳細を開く</span></> }))}
    />}
  </div>;
}
