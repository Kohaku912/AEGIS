import { PageHeader } from "../components/DashboardPrimitives";
import { SeverityGlyph, TopologyMiniMap } from "../components/viz/UxViz";
import type { UiOverview } from "../types";
import { KeyValues, text, time } from "./PageSupport";

export type DeviceServerId = "pc-server" | "browser-server" | "android-server" | "room-server";

const notes: Record<DeviceServerId, string> = {
  "pc-server": "Windows 操作、画面観測、承認付き入力を担当します。",
  "browser-server": "Web 閲覧とブラウザー自動操作を担当します。",
  "android-server": "モバイル通知、端末状態、承認付き操作を担当します。",
  "room-server": "環境センサーと承認付き IoT 制御を担当します。",
};

export function DevicePage({ overview, serverId }: { overview: UiOverview; serverId: DeviceServerId }) {
  const server = overview.servers.data.items.find((item) => item.server_id === serverId);
  const capabilityData = overview.capabilities?.data || {};
  const byServer = capabilityData.by_server && typeof capabilityData.by_server === "object" ? capabilityData.by_server as Record<string, unknown> : {};
  const status = String(server?.status || "UNCONFIGURED").toUpperCase();
  return <div className="grid"><PageHeader title={serverId} description={notes[serverId]}><a href="/api/status">全体ヘルス</a></PageHeader><section className="panel"><header><h2><SeverityGlyph severity={status === "ONLINE" ? "ok" : status === "OFFLINE" ? "critical" : "warning"} /> 接続状態: {status}</h2></header><div className="metric-list"><div className="metric-row"><span>能力数</span><strong>{text(byServer[serverId] ?? server?.registered_capabilities, "0")}</strong></div><div className="metric-row"><span>ハートビート経過</span><strong>{server?.heartbeat_age_seconds === undefined ? "不明" : `${server.heartbeat_age_seconds} 秒`}</strong></div><div className="metric-row"><span>最終ヘルス確認</span><strong>{time(server?.health_checked_at)}</strong></div><div className="metric-row"><span>エンドポイント</span><strong>{server ? `${server.host || "host"}:${server.port || "—"}` : "未構成"}</strong></div></div></section><div className="grid grid--three"><section className="panel"><h2>トポロジー</h2><TopologyMiniMap servers={overview.servers.data.items} /></section><section className="panel"><h2>詳細</h2><KeyValues data={(server || {}) as unknown as Record<string, unknown>} /></section><section className="panel"><h2>操作</h2><div className="metric-list"><a href="/api/status">ステータス API</a><a href="/dashboard/systems">全サーバー</a><a href="/dashboard/capabilities">能力カタログ</a></div></section></div></div>;
}
