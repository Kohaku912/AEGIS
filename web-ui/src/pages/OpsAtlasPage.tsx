import { navigation } from "../navigation";
import { PageHeader } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";

export function OpsAtlasPage({
  overview,
  onNavigate,
}: {
  overview: UiOverview;
  onNavigate: (path: string) => void;
}) {
  const systemCount = overview.servers.data.items?.length || 0;
  const approvalCount = overview.approvals.data.pending_count || 0;
  const notificationCount = overview.notifications.data.unread_count || 0;
  const openLoops = overview.open_loops?.data.count || 0;
  const pages = navigation.flatMap((domain) => domain.pages);
  const surfaces = [
    {
      title: "Interventions & approvals",
      summary: `${approvalCount} pending approvals · ${openLoops} open loops`,
      description: "承認、ブロック、例外、介入タスクの確認入口です。",
      path: "/dashboard/interventions",
    },
    {
      title: "Operations & audit",
      summary: `${(overview.activity?.data.operations || []).length} visible operations`,
      description: "operation / activity / audit / session を因果順で追います。",
      path: "/dashboard/operations",
    },
    {
      title: "Systems & devices",
      summary: `${systemCount} systems in topology`,
      description: "PC / Browser / Android / Room / server health を確認します。",
      path: "/dashboard/systems",
    },
    {
      title: "Personal context",
      summary: `${(overview.commitments.data.items || []).length} commitments`,
      description: "Personal AI / user state / personal data timeline を辿ります。",
      path: "/dashboard/personal-context",
    },
    {
      title: "Notifications & presentation",
      summary: `${notificationCount} unread notifications`,
      description: "通知・presentation surfaces・social inbox の入口です。",
      path: "/dashboard/communications/notifications",
    },
    {
      title: "Models & prompts",
      summary: String(overview.usage.data.summary || overview.usage.data.budget_state || "model state"),
      description: "LLM usage / prompts / layer panels / diagnostics へ進みます。",
      path: "/dashboard/intelligence/models-prompts",
    },
  ];

  return (
    <div className="grid">
      <PageHeader
        title="Ops Atlas"
        description="ダッシュボード上の全情報面・全操作面へ最短で入るための総合索引です。"
      />

      <section className="panel atlas-hero">
        <div className="atlas-hero__copy">
          <span className="muted">Everything index</span>
          <h2>すべての監視・調査・操作導線を 1 画面に集約</h2>
          <p>
            「どこに何があるか」を覚えなくても、Cockpit / Trace / Personal / Settings
            の全ページと主要情報面へここから直接移動できます。
          </p>
        </div>
        <div className="atlas-hero__metrics home-summary-grid">
          <Metric label="Pages" value={String(pages.length)} />
          <Metric label="Domains" value={String(navigation.length)} />
          <Metric label="Systems" value={String(systemCount)} />
          <Metric label="Unread" value={String(notificationCount)} />
        </div>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Information surfaces</h2>
            <div className="muted">主要情報面を目的別にまとめています。</div>
          </div>
        </div>
        <div className="atlas-surface-grid">
          {surfaces.map((surface) => (
            <button
              className="atlas-surface-card"
              key={surface.title}
              type="button"
              onClick={() => onNavigate(surface.path)}
            >
              <strong>{surface.title}</strong>
              <span>{surface.summary}</span>
              <p>{surface.description}</p>
            </button>
          ))}
        </div>
      </section>

      <section className="atlas-domain-grid">
        {navigation.map((domain) => (
          <section className="panel atlas-domain" key={domain.id}>
            <div className="panel__header">
              <div>
                <h2>{domain.label}</h2>
                <div className="muted">{domain.pages.length} pages</div>
              </div>
              <button className="secondary-button" type="button" onClick={() => onNavigate(domain.path)}>
                Open domain
              </button>
            </div>
            <div className="atlas-page-list">
              {domain.pages.map((page) => (
                <button
                  className="atlas-page-card"
                  key={page.id}
                  type="button"
                  onClick={() => onNavigate(page.path)}
                >
                  <strong>{page.label}</strong>
                  <span>{page.path}</span>
                  {page.developerOnly ? <small>developer surface</small> : <small>primary surface</small>}
                </button>
              ))}
            </div>
          </section>
        ))}
      </section>
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
