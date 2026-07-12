import type { AttentionItem, ServerItem, UiEvent, UiOverview, VisualEvent } from "./types";

export const CORE_SERVER_IDS = ["ai-server", "pc-server", "android-server", "browser-server", "room-server", "dev-server"] as const;

export type CoreServerId = (typeof CORE_SERVER_IDS)[number];

export function serverFromCapabilityId(capabilityId = ""): CoreServerId {
  const prefix = capabilityId.split(".", 1)[0] as CoreServerId;
  return CORE_SERVER_IDS.includes(prefix) ? prefix : "ai-server";
}

export function serverLabel(serverId: string): string {
  const labels: Record<string, string> = {
    "ai-server": "AI",
    "pc-server": "PC",
    "android-server": "Android",
    "browser-server": "Browser",
    "room-server": "Room",
    "dev-server": "Dev"
  };
  return labels[serverId] || serverId.replace("-server", "");
}

export function normalizeStatus(status = ""): string {
  return status.trim().toUpperCase() || "UNKNOWN";
}

export function serverNeedsDetail(server: ServerItem, activeServerId = ""): boolean {
  const status = normalizeStatus(server.status);
  const detailText = `${server.status_detail || ""} ${server.degraded_reason || ""} ${server.recovery_hint || ""}`.toLowerCase();
  return (
    server.server_id === activeServerId ||
    ["DEGRADED", "OFFLINE", "UNCONFIGURED", "DISABLED", "RECOVERING"].includes(status) ||
    detailText.includes("permission") ||
    detailText.includes("missing") ||
    detailText.includes("recover")
  );
}

export function summarizeServers(servers: ServerItem[]): { ok: number; attention: ServerItem[] } {
  const attention = servers.filter((server) => serverNeedsDetail(server));
  return { ok: Math.max(0, servers.length - attention.length), attention };
}

export function mapUiEventToVisualEvent(event: UiEvent): VisualEvent {
  const type = event.type || event.source_type || "activity.updated";
  const capabilityId = event.capability_id || String(event.payload?.capability_id || "");
  const serverId = (event.server_id as CoreServerId) || serverFromCapabilityId(capabilityId);
  const status = String(event.status || event.payload?.status || "");
  let effect: VisualEvent["effect"] = "pulse";
  if (type === "approval.created") effect = "containment";
  else if (type === "approval.resolved") effect = "containment-resolved";
  else if (type.includes("failed") || status.toLowerCase() === "failed") effect = "fracture";
  else if (type.includes("completed")) effect = "complete";
  else if (type.includes("status") || type.includes("connection")) {
    effect = status.toLowerCase().includes("offline") ? "disconnect" : "recovery";
  }
  return {
    id: `${event.type}-${event.source_updated_at}-${serverId}-${event.approval_id || ""}`,
    type,
    effect,
    serverId,
    capabilityId,
    status,
    severity: event.severity || "info",
    message: event.message || type,
    createdAt: event.generated_at || Date.now(),
    expiresAt: (event.generated_at || Date.now()) + 4_500
  };
}

export function attentionItems(overview: UiOverview): AttentionItem[] {
  const pendingApprovals = overview.approvals.data.pending || [];
  const attention = overview.attention.data.items || [];
  const approvalItems: AttentionItem[] = pendingApprovals.map((approval) => ({
    id: approval.approval_id,
    kind: "approval",
    severity: "warning",
    title: "Approval required",
    message: approval.summary || approval.capability_id || "Review requested action",
    created_at: approval.created_at,
    expires_at: approval.expires_at
  }));
  return [...approvalItems, ...attention.filter((item) => item.kind !== "approval")];
}

export function missionPhase(overview: UiOverview): string {
  const core = overview.core.data;
  const task = overview.current_task.data;
  const pending = overview.approvals.data.pending_count || 0;
  if (pending > 0) return "Waiting for Approval";
  if (String(core.health || "").toUpperCase() === "OFFLINE") return "Offline";
  if (String(core.health || "").toUpperCase() === "DEGRADED") return "Stabilizing";
  if (task.task_id || String(core.mode || "").toUpperCase() === "EXECUTING") return "Executing";
  return "Idle";
}

export function summarizeMemory(overview: UiOverview): Record<string, string> {
  const mind = overview.mind_summary.data || {};
  const core = overview.core.data || {};
  const memory = asRecord(mind.memory);
  const autonomy = asRecord(mind.autonomy);
  const desires = asRecord(autonomy.desires || autonomy.pressures || autonomy.desire_state);
  const dominant = dominantDesire(desires);
  return {
    "Active goal": String(core.active_goal || "Not reported"),
    "Dominant desire": dominant || "Not reported",
    "Context confidence": String(core.confidence || mind.context_confidence || "Not reported"),
    "Memories used": memoriesUsed(memory),
    "Last consolidation": String(memory.last_consolidation || memory.last_consolidated_at || memory.last_sleep_at || "Not reported")
  };
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function dominantDesire(desires: Record<string, unknown>): string {
  let best = "";
  let bestValue = Number.NEGATIVE_INFINITY;
  for (const [key, value] of Object.entries(desires)) {
    const numeric = typeof value === "number" ? value : typeof value === "object" && value ? Number((value as Record<string, unknown>).value || (value as Record<string, unknown>).pressure) : Number(value);
    if (Number.isFinite(numeric) && numeric > bestValue) {
      best = key;
      bestValue = numeric;
    }
  }
  return best;
}

function memoriesUsed(memory: Record<string, unknown>): string {
  const direct = memory.memories_used || memory.used || memory.context_items;
  if (direct !== undefined) return String(direct);
  const total = ["episodic", "semantic", "procedural"].reduce((sum, key) => {
    const value = Number(memory[key] || 0);
    return Number.isFinite(value) ? sum + value : sum;
  }, 0);
  return total > 0 ? String(total) : "Not reported";
}
