import type { ApprovalItem, AttentionItem, DisplayDirectorItem, DisplayDirectorState, ServerItem, UiEvent, UiOverview, VisualEvent } from "./types";

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
  const serverId = (event.visual_hint?.arc as CoreServerId) || (event.server_id as CoreServerId) || serverFromCapabilityId(capabilityId);
  const status = String(event.status || event.payload?.status || "");
  let effect: VisualEvent["effect"] = "pulse";
  const hintedEffect = normalizeVisualEffect(event.visual_hint?.effect);
  if (hintedEffect) effect = hintedEffect;
  else if (type === "approval.created") effect = "containment";
  else if (type === "approval.resolved") effect = "containment-resolved";
  else if (type.includes("failed") || status.toLowerCase() === "failed") effect = "fracture";
  else if (type.includes("completed")) effect = "complete";
  else if (type.includes("status") || type.includes("connection")) {
    effect = status.toLowerCase().includes("offline") ? "disconnect" : "recovery";
  }
  const now = Date.now();
  const createdAt = event.received_at || event.generated_at || now;
  const durationMs = Number(event.visual_hint?.duration_ms || 4500);
  return {
    id: event.event_id || `${event.type}-${event.source_updated_at}-${serverId}-${event.approval_id || ""}`,
    type,
    effect,
    serverId,
    capabilityId,
    status,
    severity: event.severity || "info",
    message: event.safe_message || event.message || type,
    createdAt,
    expiresAt: event.expires_at || createdAt + durationMs
  };
}

export function buildDisplayDirectorState(overview: UiOverview, events: UiEvent[], visualEvents: VisualEvent[] = []): DisplayDirectorState {
  const displayScene = asRecord(overview.display_scene?.data);
  const now = Date.now();
  const sceneTakeover = asRecord(displayScene.takeover);
  const eventItems = dedupeDirectorItems(events.map((event) => directorItemFromEvent(event)).filter(Boolean) as DisplayDirectorItem[]);
  const serverQueueItems = displayQueueDirectorItems(overview);
  const attentionItemsForDisplay = attentionItems(overview).map((item) => directorItemFromAttention(item));
  const presentationItems = presentationDirectorItems(overview);
  const all = dedupeDirectorItems(
    reconcileDirectorItems(
      overview,
      [...serverQueueItems, ...eventItems, ...attentionItemsForDisplay, ...presentationItems]
    )
  )
    .filter((item) => !item.expiresAt || item.expiresAt > now || item.persistence === "until_resolved")
    .sort(compareDirectorItems);
  const explicitTakeover = sceneTakeover.active
    ? {
        id: String(sceneTakeover.source_id || "display-scene-takeover"),
        priority: String(sceneTakeover.priority || "P1"),
        severity: String(sceneTakeover.severity || "warning"),
        title: String(sceneTakeover.title || "Attention required"),
        message: String(sceneTakeover.message || "Review AEGIS on phone or web."),
        persistence: "until_resolved",
        createdAt: overview.generated_at,
        expiresAt: Number(sceneTakeover.expires_at || 0),
        affectedServers: []
      }
    : undefined;

  const isServerOffline = (item: DisplayDirectorItem) => {
    const title = String(item.title || "").toLowerCase();
    const message = String(item.message || "").toLowerCase();
    return title.includes("offline") || message.includes("not connected") || message.includes("offline");
  };

  const takeover = explicitTakeover || all.find((item) => ["P0", "P1"].includes(String(item.priority)) && !isServerOffline(item));

  const serverOfflineItems = all.filter((item) => isServerOffline(item)).map((item) => ({
    ...item,
    priority: "P2",
    severity: "warning",
    persistence: "attention_dock"
  }));

  const warningItems = [
    ...all.filter((item) => item.id !== takeover?.id && String(item.priority) === "P2"),
    ...serverOfflineItems
  ].slice(0, 5);

  return {
    sceneMode: String(displayScene.phase || displayScene.mode || missionPhase(overview)),
    privacyMode: Boolean(displayScene.privacy_mode),
    offline: Boolean(displayScene.offline || String(overview.core.data.health || "").toUpperCase() === "OFFLINE"),
    stale: Boolean(overview.freshness.stale || displayScene.stale),
    takeover,
    overlays: warningItems,
    dock: all.filter((item) => item.id !== takeover?.id && item.persistence !== "ephemeral" && !isServerOffline(item)).slice(0, 6),
    ambient: [
      ...all.filter((item) => item.id !== takeover?.id && item.persistence === "ephemeral" && !isServerOffline(item)),
      ...visualEvents.map((event) => directorItemFromVisualEvent(event))
    ].slice(0, 8)
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
  const scenePhase = overview.display_scene?.data?.phase;
  if (scenePhase) return String(scenePhase);
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
    "Active goal": String(core.active_goal || "No data yet"),
    "Dominant desire": dominant || "No data yet",
    "Context confidence": String(core.confidence || mind.context_confidence || "No data yet"),
    "Memories used": memoriesUsed(memory),
    "Last consolidation": String(memory.last_consolidation || memory.last_consolidated_at || memory.last_sleep_at || "No data yet")
  };
}

export function taskBuckets(overview: UiOverview): Array<{ id: string; label: string; count: number; items: Array<Record<string, unknown>> }> {
  const task = overview.current_task.data;
  const tasks = overview.tasks?.data;
  const commitments = overview.commitments.data.items || [];
  const hasActive = Boolean(task.task_id || task.title);
  const active = tasks?.active?.length ? tasks.active : hasActive ? [task as unknown as Record<string, unknown>] : [];
  const waiting = tasks?.waiting?.length ? tasks.waiting : hasActive && (overview.approvals.data.pending_count > 0 || task.blocked_reason) ? [task as unknown as Record<string, unknown>] : [];
  return [
    { id: "active", label: "Active", count: active.length, items: active },
    { id: "waiting", label: "Waiting", count: waiting.length, items: waiting },
    { id: "scheduled", label: "Scheduled", count: tasks?.scheduled?.length || 0, items: tasks?.scheduled || [] },
    { id: "research", label: "Research", count: taskContains(task, "browser-server") ? active.length : 0, items: taskContains(task, "browser-server") ? active : [] },
    { id: "self-development", label: "Self-development", count: taskContains(task, "dev-server") ? active.length : 0, items: taskContains(task, "dev-server") ? active : [] },
    { id: "commitments", label: "Commitments", count: commitments.length, items: commitments },
    { id: "delegated", label: "Delegated", count: (tasks?.recent || []).filter((item) => Boolean(item.server_id || item.assignee || item.delegated_to)).length, items: (tasks?.recent || []).filter((item) => Boolean(item.server_id || item.assignee || item.delegated_to)) },
    { id: "completed", label: "Completed", count: (tasks?.recent || []).filter((item) => String(item.status || "").toLowerCase() === "completed").length || countSteps(task, "completed"), items: [] },
    { id: "failed", label: "Failed", count: (tasks?.recent || []).filter((item) => String(item.status || "").toLowerCase() === "failed").length || countSteps(task, "failed"), items: [] }
  ];
}

export function approvalBuckets(approvals: ApprovalItem[]): Array<{ id: string; label: string; items: ApprovalItem[] }> {
  const now = Date.now();
  return [
    { id: "pending", label: "Pending", items: approvals.filter((item) => normalizeApprovalStatus(item) === "PENDING") },
    { id: "expiring", label: "Expiring", items: approvals.filter((item) => item.expires_at && item.expires_at - now < 10 * 60 * 1000) },
    { id: "high-risk", label: "High risk", items: approvals.filter((item) => ["HIGH", "CRITICAL", "FORBIDDEN"].includes(String(item.risk || "").toUpperCase())) },
    { id: "resolved", label: "Resolved", items: approvals.filter((item) => ["APPROVED", "RESOLVED"].includes(normalizeApprovalStatus(item))) },
    { id: "rejected", label: "Rejected", items: approvals.filter((item) => normalizeApprovalStatus(item) === "REJECTED") },
    { id: "expired", label: "Expired", items: approvals.filter((item) => normalizeApprovalStatus(item) === "EXPIRED") },
    { id: "cancelled", label: "Cancelled", items: approvals.filter((item) => normalizeApprovalStatus(item) === "CANCELLED") },
    { id: "executed", label: "Executed", items: approvals.filter((item) => ["EXECUTED", "SUPERSEDED"].includes(normalizeApprovalStatus(item))) },
    { id: "failed", label: "Failed after approval", items: approvals.filter((item) => normalizeApprovalStatus(item).includes("FAILED")) }
  ];
}

export function settingSections(overview?: UiOverview): Array<{ id: string; label: string; summary: string; status: string }> {
  const pending = overview?.approvals.data.pending_count || 0;
  const memoryStats = overview ? summarizeMemory(overview) : {};
  return [
    { id: "autonomy", label: "Autonomy", summary: "Loop cadence, profile, and autonomous execution guardrails.", status: String(overview?.mind_summary.data?.autonomy ? "Configured" : "No data yet") },
    { id: "permissions", label: "Permissions", summary: "Capability risk, approval requirements, PC/Android operation limits.", status: pending ? `${pending} approval pending` : "Guarded" },
    { id: "servers", label: "Servers", summary: "AI, PC, Android, Browser, Room, and Dev endpoints.", status: `${overview?.servers.data.items?.length || 0} known` },
    { id: "privacy", label: "Privacy", summary: "Display privacy mode, redaction, local-only surfaces.", status: "Local-first" },
    { id: "notifications", label: "Notifications", summary: "Attention routing, persistent warnings, and quiet states.", status: `${overview?.notifications.data.unread_count || 0} unread` },
    { id: "models", label: "Models", summary: "LLM profiles, provider routing, and fresh-auth protected changes.", status: "Fresh auth required" },
    { id: "budgets", label: "Budgets", summary: "LLM usage, cost ceilings, and autonomous suppression.", status: String(overview?.usage.data?.summary || "Audit-backed") },
    { id: "memory", label: "Memory", summary: "Episodic, semantic, procedural retrieval and consolidation.", status: memoryStats["Memories used"] || "No data yet" },
    { id: "display", label: "Display", summary: "Read-only dedicated display, token, kiosk, privacy and power behavior.", status: "Read-only" },
    { id: "developer", label: "Developer", summary: "Debug drawers, raw JSON, audit traces, and dev server writes.", status: "Restricted" },
    { id: "backup", label: "Backup", summary: "Data volume, auth credentials, audit, memory, and override backups.", status: "Manual check" }
  ];
}

export function serverDependencySummary(server: ServerItem): string {
  const dependencies = asRecord(server.dependencies);
  const entries = Object.entries(dependencies);
  if (!entries.length) return "No dependencies reported";
  const unavailable = entries.filter(([, value]) => value === false || value === "false" || value === "missing").map(([key]) => key);
  if (unavailable.length) return `${unavailable.length} dependency issue(s): ${unavailable.slice(0, 3).join(", ")}`;
  return `${entries.length} dependencies reported`;
}

function directorItemFromEvent(event: UiEvent): DisplayDirectorItem | undefined {
  const visualEvent = mapUiEventToVisualEvent(event);
  const presentation = event.presentation_event;
  const priority = presentation?.priority || event.priority || priorityFromSeverity(event.severity || visualEvent.severity || "info");
  return {
    id: event.dedupe_key || event.event_id || visualEvent.id,
    priority,
    severity: presentation?.severity || event.severity || visualEvent.severity || "info",
    title: presentation?.title || event.safe_title || event.type || "AEGIS event",
    message: presentation?.summary || event.safe_message || event.message || event.source_type || "AEGIS event",
    persistence: presentation?.persistence || event.persistence || (priority === "P0" || priority === "P1" ? "until_resolved" : priority === "P2" ? "attention_dock" : "ephemeral"),
    createdAt: event.occurred_at || event.source_updated_at || event.generated_at || Date.now(),
    expiresAt: presentation?.expires_at || event.expires_at || visualEvent.expiresAt,
    affectedServers: event.affected_servers || (event.server_id ? [event.server_id] : []),
    visualEvent
  };
}

function directorItemFromAttention(item: AttentionItem): DisplayDirectorItem {
  const priority = item.kind === "approval" ? "P1" : priorityFromSeverity(item.severity);
  return {
    id: item.id,
    priority,
    severity: item.severity || "info",
    title: item.title,
    message: item.message || item.recovery_hint || "Review this signal.",
    persistence: priority === "P0" || priority === "P1" ? "until_resolved" : "attention_dock",
    createdAt: item.created_at || Date.now(),
    expiresAt: item.expires_at || 0,
    affectedServers: []
  };
}

function directorItemFromVisualEvent(event: VisualEvent): DisplayDirectorItem {
  return {
    id: event.id,
    priority: event.effect === "fracture" || event.effect === "disconnect" ? "P2" : "P3",
    severity: event.severity || "info",
    title: event.type,
    message: event.message,
    persistence: "ephemeral",
    createdAt: event.createdAt,
    expiresAt: event.expiresAt,
    affectedServers: event.serverId ? [event.serverId] : [],
    visualEvent: event
  };
}

function presentationDirectorItems(overview: UiOverview): DisplayDirectorItem[] {
  const data = overview.presentations?.data;
  if (!data) return [];
  const groups: Array<[string, string, Array<Record<string, unknown>> | undefined]> = [
    ["P0", "until_resolved", data.takeover],
    ["P2", "attention_dock", data.overlays],
    ["P2", "until_resolved", data.persistent],
    ["P3", "ephemeral", data.ambient]
  ];
  return groups.flatMap(([priority, persistence, items]) =>
    (items || []).map((item) => ({
      id: String(item.presentation_id || item.id || `${priority}-${item.title || "presentation"}`),
      priority,
      severity: priority === "P0" ? "critical" : priority === "P2" ? "warning" : "info",
      title: String(item.title || "Presentation"),
      message: String(item.summary || item.status || "Presentation update"),
      persistence,
      createdAt: Number(item.created_at || overview.generated_at),
      expiresAt: Number(item.expires_at || 0),
      affectedServers: []
    }))
  );
}

function displayQueueDirectorItems(overview: UiOverview): DisplayDirectorItem[] {
  const items = overview.display_queue?.data?.items || [];
  return items.filter((item) => !String(asRecord(item).resolved_by || "").trim()).map((item) => {
    const record = asRecord(item);
    const presentation = asRecord(record.presentation_event);
    const priority = String(record.priority || "P3");
    const visualHint = asRecord(record.visual_hint);
    return {
      id: String(record.id || record.event_id || record.title || "display-queue-item"),
      priority: String(presentation.priority || priority),
      severity: String(presentation.severity || record.severity || "info"),
      title: String(presentation.title || record.title || "AEGIS signal"),
      message: String(presentation.summary || record.message || record.title || "AEGIS signal"),
      persistence: String(presentation.persistence || record.persistence || (priority === "P0" || priority === "P1" ? "until_resolved" : "attention_dock")),
      createdAt: Number(record.created_at || record.updated_at || Date.now()),
      expiresAt: Number(presentation.expires_at || record.expires_at || 0),
      affectedServers: Array.isArray(record.affected_servers) ? record.affected_servers.map(String) : [],
      visualEvent: visualHint.effect
        ? {
            id: String(record.event_id || record.id || `${record.title || "queue"}-visual`),
            type: String(record.title || "display.queue"),
            effect: normalizeVisualEffect(visualHint.effect) || "pulse",
            serverId: String(visualHint.arc || (Array.isArray(record.affected_servers) ? record.affected_servers[0] : "") || "ai-server"),
            status: String(record.status || ""),
            severity: String(record.severity || "info"),
            message: String(record.message || record.title || "AEGIS signal"),
            createdAt: Number(record.created_at || Date.now()),
            expiresAt: Number(record.expires_at || Date.now() + Number(visualHint.duration_ms || 4500))
          }
        : undefined
    };
  });
}

function dedupeDirectorItems(items: DisplayDirectorItem[]): DisplayDirectorItem[] {
  const byId = new Map<string, DisplayDirectorItem>();
  for (const item of items) {
    const previous = byId.get(item.id);
    if (!previous || item.createdAt >= previous.createdAt || priorityRank(item.priority) < priorityRank(previous.priority)) {
      byId.set(item.id, item);
    }
  }
  const seen = new Map<string, DisplayDirectorItem>();
  for (const item of byId.values()) {
    const key = ["P0", "P1"].includes(String(item.priority))
      ? item.id
      : directorSemanticKey(item);
    const previous = seen.get(key);
    if (!previous || item.createdAt >= previous.createdAt || priorityRank(item.priority) < priorityRank(previous.priority)) {
      seen.set(key, item);
    }
  }
  return [...seen.values()];
}

function reconcileDirectorItems(overview: UiOverview, items: DisplayDirectorItem[]): DisplayDirectorItem[] {
  const serverStatuses = new Map(
    (overview.servers.data.items || []).map((server) => [server.server_id, normalizeStatus(server.status)])
  );
  return items.filter((item) => {
    if (item.visualEvent?.effect === "disconnect" && item.affectedServers.length) {
      const recovered = item.affectedServers.every(
        (serverId) => serverStatuses.get(serverId) === "ONLINE"
      );
      if (recovered) return false;
    }
    return true;
  });
}

function directorSemanticKey(item: DisplayDirectorItem): string {
  return [
    item.priority,
    item.title.trim().toLowerCase(),
    item.message.trim().toLowerCase(),
    [...item.affectedServers].sort().join(",")
  ].join("|");
}

function compareDirectorItems(a: DisplayDirectorItem, b: DisplayDirectorItem): number {
  return priorityRank(a.priority) - priorityRank(b.priority) || b.createdAt - a.createdAt;
}

function priorityFromSeverity(severity = "info"): string {
  const normalized = severity.toLowerCase();
  if (normalized === "critical") return "P0";
  if (normalized === "warning") return "P2";
  return "P3";
}

function priorityRank(priority: string): number {
  return { P0: 0, P1: 1, P2: 2, P3: 3 }[priority as "P0" | "P1" | "P2" | "P3"] ?? 4;
}

function normalizeVisualEffect(effect: unknown): VisualEvent["effect"] | "" {
  const value = String(effect || "");
  return ["pulse", "complete", "fracture", "containment", "containment-resolved", "disconnect", "recovery"].includes(value)
    ? (value as VisualEvent["effect"])
    : "";
}

function normalizeApprovalStatus(item: ApprovalItem): string {
  return String(item.status || "pending").toUpperCase();
}

function taskContains(task: { capability_id?: string; steps?: Array<Record<string, unknown>> }, fragment: string): boolean {
  if (String(task.capability_id || "").includes(fragment)) return true;
  return Boolean((task.steps || []).some((step) => String(step.capability_id || step.name || "").includes(fragment)));
}

function countSteps(task: { steps?: Array<Record<string, unknown>> }, status: string): number {
  return (task.steps || []).filter((step) => String(step.status || "").toLowerCase() === status).length;
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
  return total > 0 ? String(total) : "No data yet";
}
