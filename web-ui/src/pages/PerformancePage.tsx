import { useMemo, useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";
import { StatusBadge } from "../components/StatusBadge";
import type { UiOverview } from "../types";

type Props = {
  overview: UiOverview;
  developerMode?: boolean;
};

type MetricRow = {
  id: string;
  label: string;
  value: string;
  detail: string;
  status: string;
  serverId?: string;
};

function serverField(server: Record<string, unknown>, ...keys: string[]): unknown {
  for (const key of keys) {
    if (server[key] != null && server[key] !== "") return server[key];
  }
  return undefined;
}

export function PerformancePage({ overview, developerMode = false }: Props) {
  const servers = (overview.servers?.data.items || []) as Array<Record<string, unknown>>;
  const usage = (overview.usage?.data || {}) as Record<string, unknown>;
  const tasks = (overview.tasks?.data || {}) as Record<string, unknown>;
  const rows = useMemo(() => {
    const items: MetricRow[] = servers.map((server) => {
      const latency = Number(serverField(server, "latency_ms", "response_ms") || 0);
      const cpu = Number(serverField(server, "cpu_percent", "cpu") || 0);
      const ram = Number(serverField(server, "memory_percent", "ram_percent") || 0);
      const status = String(serverField(server, "status") || "UNKNOWN");
      const serverId = String(serverField(server, "server_id") || "");
      return {
        id: serverId,
        label: serverId,
        value: latency > 0 ? `${latency}ms` : status,
        detail: [
          cpu ? `CPU ${cpu}%` : "",
          ram ? `RAM ${ram}%` : "",
          serverField(server, "reconnect_count") != null ? `Reconnect ${serverField(server, "reconnect_count")}` : "",
          serverField(server, "error_rate") != null ? `Error ${serverField(server, "error_rate")}` : "",
        ]
          .filter(Boolean)
          .join(" · ") || String(serverField(server, "detail", "message") || "応答情報なし"),
        status,
        serverId,
      };
    });
    items.push({
      id: "llm-latency",
      label: "LLM Latency",
      value: usage.avg_latency_ms != null ? `${usage.avg_latency_ms}ms` : "—",
      detail: `Budget ${String(usage.budget_status || usage.status || "unknown")}`,
      status: String(usage.budget_status || "ok"),
    });
    const active = Array.isArray(tasks.active) ? tasks.active.length : 0;
    const waiting = Array.isArray(tasks.waiting) ? tasks.waiting.length : Number(tasks.waiting_approval_count || 0);
    items.push({
      id: "task-queue",
      label: "Task Queue",
      value: String(active || tasks.count || "—"),
      detail: `Waiting approval ${waiting}`,
      status: "ok",
    });
    return items;
  }, [servers, tasks, usage]);

  const [selectedId, setSelectedId] = useState(rows[0]?.id || "");
  const selected = rows.find((item) => item.id === selectedId) || rows[0];
  const relatedOps = ((overview.activity?.data.operations || []) as Array<Record<string, unknown>>).filter((op) => {
    if (!selected?.serverId) return false;
    const target = `${op.target_summary || ""} ${op.target || ""} ${JSON.stringify(op.steps || [])}`;
    return target.includes(selected.serverId) || target.includes(selected.serverId.replace("-server", ""));
  }).slice(0, 8);

  return (
    <div className="grid">
      <PageHeader
        title="Performance"
        description="Server 応答、LLM 遅延、キュー長、ユーザー影響を現在値として確認します。"
      />
      <div className="judgment-split">
        <section className="panel">
          <div className="compact-list">
            {rows.map((row) => (
              <button
                type="button"
                className="list-row"
                data-selected={selected?.id === row.id}
                key={row.id}
                onClick={() => setSelectedId(row.id)}
              >
                <div>
                  <strong>{row.label}</strong>
                  <p>{row.detail}</p>
                </div>
                <div>
                  <StatusBadge status={row.status} />
                  <strong>{row.value}</strong>
                </div>
              </button>
            ))}
            {!rows.length ? <p className="muted">メトリクスがまだありません。</p> : null}
          </div>
        </section>
        <aside className="panel judgment-detail">
          {selected ? (
            <>
              <div className="panel__header">
                <h2>{selected.label}</h2>
                <StatusBadge status={selected.status} />
              </div>
              <p className="human-summary">{selected.detail}</p>
              <dl className="human-facts compact">
                <div><dt>現在値</dt><dd>{selected.value}</dd></div>
                <div><dt>ユーザー影響</dt><dd>{selected.status.toLowerCase().includes("degrad") || selected.status.toLowerCase().includes("offline") ? "関連操作が遅延または失敗する可能性" : "通常影響なし"}</dd></div>
              </dl>
              <div className="panel__header"><h3>影響を受けた Operation</h3></div>
              <ul className="reason-list">
                {relatedOps.map((op) => (
                  <li key={String(op.operation_id)}>
                    <strong>{String(op.action_summary || op.what_happened || op.title || op.operation_id)}</strong>
                    <span>{String(op.result_status || op.status || "")}</span>
                  </li>
                ))}
                {!relatedOps.length ? <li className="empty-copy">関連 Operation はまだありません。</li> : null}
              </ul>
              {developerMode ? <pre className="developer-raw">{JSON.stringify(selected, null, 2)}</pre> : null}
            </>
          ) : (
            <p className="empty-copy">指標を選択してください。</p>
          )}
        </aside>
      </div>
    </div>
  );
}
