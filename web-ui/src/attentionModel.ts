import type { UiOverview } from "./types";
import type { Severity } from "./components/viz/UxViz";

export type AttentionKind =
  | "approval"
  | "input"
  | "failure"
  | "connection"
  | "config"
  | "warning";

export type AttentionItem = {
  id: string;
  kind: AttentionKind;
  title: string;
  message: string;
  severity: Severity;
  occurredAt: number;
  relatedTaskId?: string;
  relatedServerId?: string;
  relatedApprovalId?: string;
  impact?: string;
  recommendedAction?: string;
  autoRecoverable?: boolean;
  urgency?: "P0" | "P1" | "P2" | "P3";
  raw?: Record<string, unknown>;
};

function severityFromStatus(status: string): Severity {
  const upper = status.toUpperCase();
  if (["OFFLINE", "CRITICAL", "FAILED", "ERROR"].includes(upper)) return "critical";
  if (["DEGRADED", "WAITING", "WARNING", "PERMISSION_MISSING"].includes(upper)) return "warning";
  if (["ONLINE", "READY", "COMPLETED", "OK"].includes(upper)) return "ok";
  return "info";
}

export function buildAttentionItems(overview: UiOverview): AttentionItem[] {
  const items: AttentionItem[] = [];

  for (const approval of overview.approvals.data.pending || []) {
    const id = String(approval.approval_id || "");
    if (!id) continue;
    items.push({
      id: `approval:${id}`,
      kind: "approval",
      title: String(approval.tool_name || approval.capability_id || "承認待ち"),
      message: String(approval.reason || approval.summary || approval.preview || "操作の承認が必要です"),
      severity: "warning",
      occurredAt: Number(approval.created_at || 0),
      relatedApprovalId: id,
      relatedTaskId: String(approval.task_id || ""),
      impact: String(approval.capability_id || ""),
      recommendedAction: "承認または拒否",
      autoRecoverable: false,
      urgency: "P1",
      raw: approval as unknown as Record<string, unknown>,
    });
  }

  for (const item of overview.attention.data.items || []) {
    const raw = item as unknown as Record<string, unknown>;
    const id = String(raw.id || raw.event_id || raw.title || Math.random());
    const text = `${raw.title || ""} ${raw.message || ""}`.toLowerCase();
    let kind: AttentionKind = "warning";
    if (text.includes("approval") || text.includes("承認")) kind = "approval";
    else if (text.includes("input") || text.includes("入力")) kind = "input";
    else if (text.includes("fail") || text.includes("error") || text.includes("失敗")) kind = "failure";
    else if (text.includes("offline") || text.includes("disconnect") || text.includes("接続")) kind = "connection";
    else if (text.includes("config") || text.includes("設定")) kind = "config";
    items.push({
      id: `attention:${id}`,
      kind,
      title: String(raw.title || "要対応"),
      message: String(raw.message || raw.summary || ""),
      severity: severityFromStatus(String(raw.severity || raw.status || "warning")),
      occurredAt: Number(raw.created_at || raw.updated_at || raw.occurred_at || 0),
      relatedTaskId: String(raw.task_id || ""),
      relatedServerId: String(raw.server_id || ""),
      relatedApprovalId: String(raw.approval_id || ""),
      recommendedAction: String(raw.recommended_action || "詳細を確認"),
      autoRecoverable: Boolean(raw.auto_recoverable),
      urgency: (String(raw.priority || "P2") as AttentionItem["urgency"]) || "P2",
      raw,
    });
  }

  for (const error of overview.errors?.data.items || []) {
    const status = String(error.status || "").toLowerCase();
    if (["resolved", "repaired", "ignored"].includes(status)) continue;
    const id = String(error.id || error.error_id || error.title || "");
    items.push({
      id: `error:${id}`,
      kind: "failure",
      title: String(error.title || error.message || "エラー"),
      message: String(error.message || error.summary || ""),
      severity: "critical",
      occurredAt: Number(error.last_seen_at || error.created_at || 0),
      relatedTaskId: String(error.task_id || ""),
      relatedServerId: String(error.server_id || ""),
      recommendedAction: String(error.recommended_action || "再試行または詳細確認"),
      autoRecoverable: false,
      urgency: "P0",
      raw: error,
    });
  }

  for (const server of overview.servers.data.items || []) {
    const raw = server as unknown as Record<string, unknown>;
    const status = String(server.status || "").toUpperCase();
    if (!["OFFLINE", "DEGRADED", "CRITICAL", "PERMISSION_MISSING"].includes(status)) continue;
    const id = String(server.server_id || raw.id || "");
    items.push({
      id: `server:${id}`,
      kind: status === "PERMISSION_MISSING" ? "config" : "connection",
      title: `${id} が ${status}`,
      message: String(raw.message || raw.last_error || "接続または健全性に問題があります"),
      severity: status === "OFFLINE" || status === "CRITICAL" ? "critical" : "warning",
      occurredAt: Number(raw.updated_at || raw.last_heartbeat_ms || 0),
      relatedServerId: id,
      recommendedAction: "再接続またはヘルスチェック",
      autoRecoverable: status === "DEGRADED",
      urgency: status === "OFFLINE" ? "P0" : "P1",
      raw,
    });
  }

  const waiting = overview.tasks?.data.waiting || [];
  for (const task of waiting) {
    const raw = task as unknown as Record<string, unknown>;
    const id = String(raw.task_id || raw.id || "");
    if (!id) continue;
    const needsInput = String(raw.status || "").toLowerCase().includes("input") || Boolean(raw.waiting_for_input);
    items.push({
      id: `task-wait:${id}`,
      kind: needsInput ? "input" : "approval",
      title: String(raw.title || "待機中タスク"),
      message: String(raw.current_action || raw.next_action || "ユーザー操作待ち"),
      severity: "warning",
      occurredAt: Number(raw.updated_at || raw.created_at || 0),
      relatedTaskId: id,
      relatedApprovalId: String(raw.approval_id || ""),
      recommendedAction: needsInput ? "入力を送る" : "承認を確認",
      autoRecoverable: false,
      urgency: "P1",
      raw,
    });
  }

  const seen = new Set<string>();
  return items
    .filter((item) => {
      if (seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    })
    .sort((a, b) => {
      const rank = { P0: 0, P1: 1, P2: 2, P3: 3 };
      const ur = (rank[a.urgency || "P3"] ?? 3) - (rank[b.urgency || "P3"] ?? 3);
      if (ur !== 0) return ur;
      return b.occurredAt - a.occurredAt;
    });
}

export function filterAttention(items: AttentionItem[], tab: string): AttentionItem[] {
  if (tab === "all" || !tab) return items;
  const map: Record<string, AttentionKind[]> = {
    approvals: ["approval"],
    input: ["input"],
    failures: ["failure"],
    connection: ["connection"],
    config: ["config"],
    warnings: ["warning"],
  };
  const kinds = map[tab];
  if (!kinds) return items;
  return items.filter((item) => kinds.includes(item.kind));
}
