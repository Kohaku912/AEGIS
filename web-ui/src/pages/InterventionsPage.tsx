import { Freshness } from "../components/Freshness";
import { StatusBadge } from "../components/StatusBadge";
import type { CockpitInboxItem, UiOverview } from "../types";

export function InterventionsPage({
  overview,
  onNavigate,
}: {
  overview: UiOverview;
  onNavigate: (path: string) => void;
}) {
  const inbox = overview.cockpit_inbox?.data.items || [];
  const approvals = overview.approvals.data.pending || [];
  const loops = overview.open_loops?.data.items || [];
  const incidents = overview.errors?.data.items || [];
  const queue = [...inbox].sort((left, right) => interventionPriority(left) - interventionPriority(right));
  const primary = queue[0];

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Interventions</h2>
            <div className="muted">未処理リスク、承認待ち、ループ、修復対象を 1 画面でまとめて確認します。</div>
          </div>
          <Freshness
            generatedAt={overview.cockpit_inbox?.generated_at || overview.generated_at}
            sourceUpdatedAt={overview.cockpit_inbox?.source_updated_at || overview.generated_at}
            stale={Boolean(overview.cockpit_inbox?.stale)}
          />
        </div>
        <div className="interventions-hero">
          <div className="interventions-hero__summary">
            <div className="home-summary-grid">
              <Metric label="Inbox" value={String(overview.cockpit_inbox?.data.count || inbox.length)} />
              <Metric label="Approvals" value={String(overview.approvals.data.pending_count || approvals.length)} />
              <Metric label="Open loops" value={String(overview.open_loops?.data.count || loops.length)} />
              <Metric label="Incidents" value={String(overview.errors?.data.count || incidents.length)} />
            </div>
          </div>
          <article className="interventions-start">
            <span className="muted">Start here</span>
            <h3>{primary ? primary.title : "No immediate intervention"}</h3>
            <p>{primary ? interventionReason(primary) : "即時介入が必要な項目はありません。通常監視を継続できます。"}</p>
            {primary ? (
              <div className="interventions-meta">
                <StatusBadge status={primary.severity || primary.status || primary.kind} detail={kindLabel(primary.kind)} />
                <span>{primary.next_action || "Open detail"}</span>
              </div>
            ) : null}
            {primary ? (
              <button className="primary-button" type="button" onClick={() => onNavigate(primary.path || defaultPath(primary))}>
                Open primary item
              </button>
            ) : null}
          </article>
        </div>
      </section>

      <section className="panel">
        <div className="panel__header">
          <h2>Priority inbox</h2>
          <div className="muted">重要度、停滞理由、次の一手が上から読める順に並びます。</div>
        </div>
        <div className="compact-list interventions-queue">
          {queue.length ? (
            queue.map((item, index) => (
              <button
                className="list-row interventions-row"
                type="button"
                key={item.id}
                onClick={() => onNavigate(item.path || defaultPath(item))}
              >
                <div className="interventions-row__rank" aria-hidden="true">
                  #{index + 1}
                </div>
                <div>
                  <strong>{item.title}</strong>
                  <div className="muted">{interventionReason(item)}</div>
                  <div className="interventions-meta">
                    <span>Kind: {kindLabel(item.kind)}</span>
                    <span>Next: {item.next_action || item.message || "Inspect item"}</span>
                  </div>
                </div>
                <StatusBadge status={item.severity || item.status || item.kind} detail={item.kind} />
              </button>
            ))
          ) : (
            <p className="muted">現在、即時介入が必要な項目はありません。</p>
          )}
        </div>
      </section>

      <section className="home-summary-grid">
        <BucketPanel
          title="Approvals"
          actionLabel="Open approvals"
          onAction={() => onNavigate("/dashboard/approvals")}
          items={approvals.map((approval) => ({
            id: approval.approval_id,
            title: approval.summary || approval.capability_id,
            message: approval.reason || approval.preview || "Approval pending",
            badge: approval.status || approval.risk || "pending",
          }))}
        />
        <BucketPanel
          title="Open loops"
          actionLabel="Open loops"
          onAction={() => onNavigate("/dashboard/open-loops")}
          items={(loops as CockpitInboxItem[]).slice(0, 6).map((loop) => ({
            id: loop.id,
            title: loop.title,
            message: loop.message || loop.next_action || "Loop requires follow-through",
            badge: loop.status || loop.kind,
          }))}
        />
        <BucketPanel
          title="Incidents"
          actionLabel="Open incidents"
          onAction={() => onNavigate("/dashboard/incidents")}
          items={(incidents || []).slice(0, 6).map((incident) => ({
            id: String(incident.id || incident.capability_id || incident.created_at),
            title: String(incident.title || "Repair required"),
            message: String(incident.message || incident.summary || "Inspect incident"),
            badge: String(incident.status || incident.severity || "open"),
          }))}
        />
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="panel">
      <span className="muted">{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function BucketPanel({
  title,
  actionLabel,
  onAction,
  items,
}: {
  title: string;
  actionLabel: string;
  onAction: () => void;
  items: Array<{ id: string; title: string; message: string; badge: string }>;
}) {
  return (
    <section className="panel">
      <div className="panel__header">
        <h2>{title}</h2>
        <button className="secondary-button" type="button" onClick={onAction}>
          {actionLabel}
        </button>
      </div>
      <div className="compact-list">
        {items.length ? (
          items.map((item) => (
            <div className="list-row" key={item.id}>
              <div>
                <strong>{item.title}</strong>
                <div className="muted">{item.message}</div>
              </div>
              <StatusBadge status={item.badge} />
            </div>
          ))
        ) : (
          <p className="muted">項目はありません。</p>
        )}
      </div>
    </section>
  );
}

function defaultPath(item: CockpitInboxItem): string {
  if (item.kind === "approval") return "/dashboard/approvals";
  if (item.kind === "degraded_system") return "/dashboard/infrastructure/servers";
  if (item.kind === "error") return "/dashboard/incidents";
  if (item.kind === "blocked_task") return "/dashboard/work/tasks";
  return "/dashboard/open-loops";
}

function interventionPriority(item: CockpitInboxItem): number {
  const severityWeight = severityRank(item.severity || item.status);
  const kindBonus =
    item.kind === "approval"
      ? -3
      : item.kind === "blocked_task"
        ? -2
        : item.kind === "error"
          ? -1
          : 0;
  return severityWeight * 10 + kindBonus;
}

function severityRank(value: string): number {
  const normalized = String(value || "").toLowerCase();
  if (normalized === "critical") return 0;
  if (normalized === "warning" || normalized === "high" || normalized === "pending") return 1;
  if (normalized === "info" || normalized === "medium" || normalized === "open") return 2;
  return 3;
}

function interventionReason(item: CockpitInboxItem): string {
  if (item.kind === "approval") return "承認待ちのため、関連フローがそこで止まっています。";
  if (item.kind === "blocked_task") return "次の処理に進むためのフォローアップが未完了です。";
  if (item.kind === "degraded_system") return "依存システムの劣化が他の調査・実行速度に影響します。";
  if (item.kind === "error") return "エラー原因の切り分けと再発防止の確認が必要です。";
  return item.message || item.next_action || "優先して確認すべき項目です。";
}

function kindLabel(kind: string): string {
  if (kind === "approval") return "Approval";
  if (kind === "blocked_task") return "Blocked task";
  if (kind === "degraded_system") return "System";
  if (kind === "error") return "Incident";
  return kind || "Item";
}
