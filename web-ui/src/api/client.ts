import type { EntitySummary, UiOverview } from "../types";

export type ApiWarning = { resource?: string; message: string };

export type EntityPage = {
  items: EntitySummary[];
  page: number;
  limit: number;
  total: number;
  has_more: boolean;
  generated_at: string;
  status?: "ok" | "partial";
  partial?: boolean;
  warnings?: ApiWarning[];
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
    public readonly requestId = "",
    public readonly retryable = status >= 500,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function responsePayload(response: Response): Promise<Record<string, unknown>> {
  try {
    return await response.json() as Record<string, unknown>;
  } catch {
    return {};
  }
}

async function requireJson<T>(response: Response, fallback: string, accepted: number[] = []): Promise<T> {
  const payload = await responsePayload(response);
  if (!response.ok && !accepted.includes(response.status)) {
    throw new ApiError(
      String(payload.message || payload.error || fallback),
      response.status,
      String(payload.error || "request_failed"),
      String(payload.request_id || response.headers.get("X-Request-ID") || ""),
      Boolean(payload.retryable ?? response.status >= 500),
    );
  }
  return payload as T;
}

export async function fetchOverview(surface: "dashboard" | "display" = "dashboard"): Promise<UiOverview> {
  const endpoint = surface === "display" ? `/display/overview${displayReadQuery()}` : "/api/ui/overview";
  const response = await fetch(endpoint, { credentials: "include" });
  return requireJson<UiOverview>(response, "Could not load the overview");
}

export async function fetchResourceEntities(
  resource: string,
  query = "",
  options: { page?: number; limit?: number; status?: string; sort?: string; order?: "asc" | "desc" } = {}
): Promise<EntityPage> {
  const params = new URLSearchParams({
    resource,
    limit: String(options.limit || 100),
    page: String(options.page || 1),
    sort: options.sort || "updated_at",
    order: options.order || "desc"
  });
  if (query.trim()) params.set("q", query.trim());
  if (options.status) params.set("status", options.status);
  const response = await fetch(`/api/ui/entities?${params}`, { credentials: "include" });
  const payload = await requireJson<EntityPage>(response, "Could not load the list");
  return { ...payload, items: (payload.items || []).map(normalizeEntity) };
}

export async function fetchResourceEntity(resource: string, entityId: string): Promise<EntitySummary> {
  const response = await fetch(`/api/ui/entities/${encodeURIComponent(resource)}/${encodeURIComponent(entityId)}`, { credentials: "include" });
  return normalizeEntity(await requireJson<EntitySummary>(response, "Could not load related data"));
}

export async function searchResources(query: string): Promise<EntitySummary[]> {
  return (await searchResourcesDetailed(query)).items;
}

export async function searchResourcesDetailed(query: string): Promise<{ items: EntitySummary[]; warnings: ApiWarning[] }> {
  if (!query.trim()) return { items: [], warnings: [] };
  const params = new URLSearchParams({ q: query.trim(), limit: "40" });
  const response = await fetch(`/api/ui/search?${params}`, { credentials: "include" });
  const payload = await requireJson<EntityPage>(response, "Search failed", [206]);
  return { items: (payload.items || []).map(normalizeEntity), warnings: payload.warnings || [] };
}

export async function updateMemory(memoryId: string, patch: Record<string, unknown>): Promise<EntitySummary> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/memories/${encodeURIComponent(memoryId)}`, {
    method: "PATCH", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify({ patch })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(String(payload.error || payload.message || response.status));
  return normalizeEntity(payload);
}

export async function forgetMemory(memoryId: string): Promise<void> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/memories/${encodeURIComponent(memoryId)}`, { method: "DELETE", credentials: "include", headers: { "X-CSRF-Token": csrf } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(String(payload.error || payload.message || response.status));
}

export async function fetchLlmRequests(period = "24h"): Promise<EntityPage> {
  const response = await fetch(`/api/llm/requests?${new URLSearchParams({ period, limit: "200" })}`, { credentials: "include" });
  if (!response.ok) throw new Error(`LLM request history failed: ${response.status}`);
  const payload = await response.json() as EntityPage;
  return { ...payload, items: (payload.items || []).map(normalizeEntity) };
}

export type AuditPageResult = {
  items: Array<Record<string, unknown>>;
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  eventTypes?: Array<{ event_type: string; count: number }>;
};

export async function fetchAuditGroups(page = 1, limit = 30): Promise<AuditPageResult> {
  const response = await fetch(`/api/audit/grouped?${new URLSearchParams({ page: String(page), limit: String(limit) })}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load audit groups");
  const groups = Array.isArray(payload.groups) ? payload.groups as Array<Record<string, unknown>> : [];
  return {
    items: groups,
    page: Number(payload.page || page),
    limit: Number(payload.per_page || limit),
    total: Number(payload.total ?? payload.count ?? groups.length),
    totalPages: Number(payload.total_pages || 1),
  };
}

export async function fetchJournalEvents(page = 1, limit = 50): Promise<AuditPageResult> {
  const response = await fetch(`/api/journal/events?${new URLSearchParams({ page: String(page), limit: String(limit) })}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load journal events");
  const items = Array.isArray(payload.items) ? payload.items as Array<Record<string, unknown>> : [];
  return {
    items,
    page: Number(payload.page || page),
    limit: Number(payload.limit || limit),
    total: Number(payload.total || items.length),
    totalPages: Number(payload.total_pages || 1),
  };
}

function asCounts(value: unknown): Record<string, number> {
  if (!value || typeof value !== "object") return {};
  const counts: Record<string, number> = {};
  for (const [key, count] of Object.entries(value as Record<string, unknown>)) {
    counts[key] = Number(count || 0);
  }
  return counts;
}

export type IrreversibilityLedger = {
  totalCapabilities: number;
  threshold: string;
  includeUnknown: boolean;
  byReversibility: Record<string, number>;
  byOwnershipScope: Record<string, number>;
  byBlastRadius: Record<string, number>;
  byDataLossRisk: Record<string, number>;
  byDestructiveEffect: Record<string, number>;
  irreversible: string[];
  declaresUnknown: string[];
  reportable: Array<Record<string, unknown>>;
};

export async function fetchIrreversibilityLedger(
  threshold = "difficult",
  includeUnknown = true,
): Promise<IrreversibilityLedger> {
  const params = new URLSearchParams({ threshold, include_unknown: String(includeUnknown) });
  const response = await fetch(`/api/audit/irreversible?${params}`, { credentials: "include" });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load the irreversibility ledger");
  const reportable = Array.isArray(payload.reportable)
    ? (payload.reportable as Array<Record<string, unknown>>)
    : [];
  return {
    totalCapabilities: Number(payload.total_capabilities || 0),
    threshold: String(payload.threshold || threshold),
    includeUnknown: Boolean(payload.include_unknown ?? includeUnknown),
    byReversibility: asCounts(payload.by_reversibility),
    byOwnershipScope: asCounts(payload.by_ownership_scope),
    byBlastRadius: asCounts(payload.by_blast_radius),
    byDataLossRisk: asCounts(payload.by_data_loss_risk),
    byDestructiveEffect: asCounts(payload.by_destructive_effect),
    irreversible: Array.isArray(payload.irreversible) ? (payload.irreversible as string[]).map(String) : [],
    declaresUnknown: Array.isArray(payload.declares_unknown)
      ? (payload.declares_unknown as string[]).map(String)
      : [],
    reportable,
  };
}

export type IrreversibleOccurrences = {
  entries: Array<Record<string, unknown>>;
  total: number;
  scanned: number;
  threshold: string;
  watchedCapabilities: number;
};

export async function fetchIrreversibleOccurrences(
  threshold = "difficult",
  includeUnknown = true,
  page = 1,
  limit = 50,
): Promise<IrreversibleOccurrences> {
  const params = new URLSearchParams({
    threshold,
    include_unknown: String(includeUnknown),
    page: String(page),
    limit: String(limit),
  });
  const response = await fetch(`/api/audit/irreversible/occurrences?${params}`, { credentials: "include" });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load irreversible occurrences");
  const entries = Array.isArray(payload.entries) ? (payload.entries as Array<Record<string, unknown>>) : [];
  return {
    entries,
    total: Number(payload.total ?? entries.length),
    scanned: Number(payload.scanned || 0),
    threshold: String(payload.threshold || threshold),
    watchedCapabilities: Number(payload.watched_capabilities || 0),
  };
}

export type InterruptionStatus = {
  emergencyStop: boolean;
  batchedCount: number;
  batched: Array<Record<string, unknown>>;
};

function asInterruptionStatus(payload: Record<string, unknown>): InterruptionStatus {
  return {
    emergencyStop: Boolean(payload.emergency_stop),
    batchedCount: Number(payload.batched_count || 0),
    batched: Array.isArray(payload.batched) ? (payload.batched as Array<Record<string, unknown>>) : [],
  };
}

export async function fetchInterruptionStatus(): Promise<InterruptionStatus> {
  const response = await fetch("/api/interruption", { credentials: "include" });
  return asInterruptionStatus(
    await requireJson<Record<string, unknown>>(response, "Could not load the interruption state"));
}

/**
 * Release everything the interruption controller is holding.
 *
 * The server hands the held items back rather than delivering them itself, so the
 * caller is responsible for showing them.
 */
export async function releaseInterruptionBatch(): Promise<Array<Record<string, unknown>>> {
  const payload = await csrfJson<{ items?: Array<Record<string, unknown>> }>(
    "/api/interruption/flush",
    "POST",
    {},
    "Could not release the held notifications",
  );
  return Array.isArray(payload.items) ? payload.items : [];
}

export async function setInterruptionEmergencyStop(active: boolean): Promise<InterruptionStatus> {
  return asInterruptionStatus(
    await csrfJson<Record<string, unknown>>(
      "/api/interruption/emergency-stop",
      "POST",
      { active },
      "Could not change the interruption state",
    ));
}

export async function fetchPersonalDataTimeline(
  page = 1,
  limit = 50,
  device = "",
  eventType = "",
): Promise<AuditPageResult> {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (device) params.set("device", device);
  if (eventType) params.set("event_type", eventType);
  const response = await fetch(`/api/personal-data/timeline?${params}`, { credentials: "include" });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load personal timeline");
  const items = Array.isArray(payload.items) ? payload.items as Array<Record<string, unknown>> : [];
  const eventTypes = Array.isArray(payload.event_types)
    ? (payload.event_types as Array<Record<string, unknown>>).map((row) => ({
      event_type: String(row.event_type || ""),
      count: Number(row.count || 0),
    })).filter((row) => row.event_type)
    : [];
  const total = Number(payload.total || items.length);
  return {
    items,
    page,
    limit: Number(payload.limit || limit),
    total,
    totalPages: Math.max(1, Math.ceil(total / Math.max(1, limit))),
    eventTypes,
  };
}

/** Fetch every matching PDC event (paged under the API cap). */
export async function fetchPersonalDataTimelineAll(
  device = "",
  eventType = "",
  pageLimit = 50_000,
): Promise<AuditPageResult> {
  const first = await fetchPersonalDataTimeline(1, pageLimit, device, eventType);
  if (first.total <= first.items.length) return first;
  const pages = Math.ceil(first.total / pageLimit);
  const items = [...first.items];
  for (let page = 2; page <= pages; page += 1) {
    const chunk = await fetchPersonalDataTimeline(page, pageLimit, device, eventType);
    items.push(...chunk.items);
  }
  return { ...first, items, limit: items.length, page: 1, totalPages: 1 };
}

export async function fetchPersonalDataEvent(eventId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`/api/personal-data/events/${encodeURIComponent(eventId)}`, { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load personal-data event");
}

export async function searchPersonalData(query: string, limit = 10_000, device = ""): Promise<AuditPageResult> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (device) params.set("device", device);
  const response = await fetch(`/api/personal-data/search?${params}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not search personal data");
  const items = Array.isArray(payload.items) ? payload.items as Array<Record<string, unknown>> : [];
  const total = Number(payload.total || items.length);
  return { items, page: 1, limit, total, totalPages: 1 };
}

export async function fetchOperations(limit = 40): Promise<Array<Record<string, unknown>>> {
  const response = await fetch(`/api/operations?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load operations");
  if (Array.isArray(payload.items)) {
    return payload.items.map((item) => {
      if (item && typeof item === "object" && "data" in item) {
        const entity = item as { data?: Record<string, unknown>; id?: string };
        return { ...(entity.data || {}), operation_id: entity.data?.operation_id || entity.id };
      }
      return item as Record<string, unknown>;
    });
  }
  if (Array.isArray(payload.operations)) return payload.operations as Array<Record<string, unknown>>;
  return [];
}

export async function fetchOperation(operationId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`/api/operations/${encodeURIComponent(operationId)}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load operation");
  if (payload.data && typeof payload.data === "object") {
    return payload.data as Record<string, unknown>;
  }
  return payload;
}

export async function fetchCapabilityRisk(capabilityId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`/api/capabilities/${encodeURIComponent(capabilityId)}/risk`, { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load the capability policy");
}

export async function updateCapabilityRisk(capabilityId: string, change: Record<string, unknown>): Promise<Record<string, unknown>> {
  const auth = await fetchAuthMe();
  const csrf = String(auth.csrf_token || "");
  const response = await fetch(`/api/capabilities/${encodeURIComponent(capabilityId)}/risk`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify(change) });
  return requireJson<Record<string, unknown>>(response, "Could not update the capability policy");
}

export async function resetCapabilityRisk(capabilityId: string): Promise<Record<string, unknown>> {
  const auth = await fetchAuthMe();
  const csrf = String(auth.csrf_token || "");
  const response = await fetch(`/api/capabilities/${encodeURIComponent(capabilityId)}/risk/reset`, { method: "POST", credentials: "include", headers: { "X-CSRF-Token": csrf } });
  return requireJson<Record<string, unknown>>(response, "Could not reset the capability policy");
}

async function csrfJson<T>(path: string, method: string, body?: Record<string, unknown>, fallback = "Request failed"): Promise<T> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(path, {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify(body || {}),
  });
  return requireJson<T>(response, fallback);
}

export async function runControlAction(action: string, confirmed = false): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/ui/control-actions", { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify({ action, confirmed }) });
  return requireJson<Record<string, unknown>>(response, "Action failed", [202]);
}

export async function runTaskAction(taskId: string, action: string, confirmed = false): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/tasks/${encodeURIComponent(taskId)}/actions`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf }, body: JSON.stringify({ action, confirmed }) });
  return requireJson<Record<string, unknown>>(response, "Task action failed", [202]);
}

export async function fetchManagerTasks(options: {
  status?: string;
  source?: string;
  limit?: number;
} = {}): Promise<Array<Record<string, unknown>>> {
  const params = new URLSearchParams();
  if (options.status) params.set("status", options.status);
  if (options.source) params.set("source", options.source);
  params.set("limit", String(options.limit || 50));
  const response = await fetch(`/api/tasks?${params.toString()}`, { credentials: "include" });
  const payload = await requireJson<{ tasks?: Array<Record<string, unknown>> }>(
    response,
    "Could not load tasks",
  );
  return payload.tasks || [];
}

export async function continueTask(taskId: string): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>(
    `/api/tasks/${encodeURIComponent(taskId)}/continue`,
    "POST",
    {},
    "Could not continue the task",
  );
}

export type DashboardNotification = {
  notification_id?: string;
  id?: string;
  title?: string;
  message?: string;
  summary?: string;
  href?: string;
  severity?: string;
  status?: string;
  read?: boolean;
  created_at?: number;
  updated_at?: number;
  [key: string]: unknown;
};

export async function fetchNotifications(unreadOnly = false, limit = 50): Promise<DashboardNotification[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (unreadOnly) params.set("unread", "true");
  const response = await fetch(`/api/notifications?${params}`, { credentials: "include" });
  const payload = await requireJson<{ notifications?: DashboardNotification[] }>(response, "Could not load notifications");
  return payload.notifications || [];
}

export async function markNotificationRead(notificationId: string): Promise<DashboardNotification> {
  return csrfJson<DashboardNotification>(
    `/api/notifications/${encodeURIComponent(notificationId)}/read`,
    "POST",
    {},
    "Could not mark the notification as read",
  );
}

export async function dismissNotification(notificationId: string): Promise<DashboardNotification> {
  return csrfJson<DashboardNotification>(
    `/api/notifications/${encodeURIComponent(notificationId)}/dismiss`,
    "POST",
    {},
    "Could not dismiss the notification",
  );
}

export type AutonomousStatus = Record<string, unknown>;

export async function fetchAutonomousStatus(): Promise<AutonomousStatus> {
  const response = await fetch("/api/autonomous/status", { credentials: "include" });
  return requireJson<AutonomousStatus>(response, "Could not load autonomous status");
}

export async function triggerAutonomous(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/autonomous/trigger", "POST", {}, "Could not trigger autonomy");
}

export async function startAutonomous(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/autonomous/start", "POST", {}, "Could not start autonomy");
}

export async function stopAutonomous(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/autonomous/stop", "POST", {}, "Could not stop autonomy");
}

export async function fetchAutonomousThreshold(): Promise<{ threshold?: number }> {
  const response = await fetch("/api/autonomous/threshold", { credentials: "include" });
  return requireJson<{ threshold?: number }>(response, "Could not load the threshold");
}

export async function updateAutonomousThreshold(threshold: number): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>(
    "/api/autonomous/threshold",
    "POST",
    { threshold },
    "Could not update the threshold",
  );
}

export async function generateAutonomousDailyPlan(date = ""): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>(
    "/api/autonomous/daily-plan",
    "POST",
    date ? { date } : {},
    "Could not generate the daily plan",
  );
}

export async function fetchMemorySleepStatus(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/memory/sleep/status", { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load sleep status");
}

export async function triggerMemorySleep(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/memory/sleep", "POST", {}, "Could not start memory sleep");
}

export async function checkStatusNow(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/status/check-now", "POST", {}, "Could not refresh system status");
}

export async function fetchUserStateCurrent(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/user-state/current", { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load the current user state");
}

export async function fetchUserStateEvents(limit = 10): Promise<{ events?: Array<Record<string, unknown>> }> {
  const response = await fetch(`/api/user-state/events?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<{ events?: Array<Record<string, unknown>> }>(response, "Could not load user state events");
}

export async function fetchUserStateDays(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/user-state/days", { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load user state days");
}

export async function archiveUserState(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/user-state/archive/run", "POST", {}, "Could not archive user state");
}

export async function pollUserStatePc(): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>("/api/user-state/poll-pc", "POST", {}, "Could not poll the PC state");
}

export async function fetchRepairStatus(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/repair", { credentials: "include" });
  return requireJson<Record<string, unknown>>(response, "Could not load repair status");
}

export async function setRepairDisabled(disabled: boolean): Promise<Record<string, unknown>> {
  return csrfJson<Record<string, unknown>>(
    "/api/repair/disable",
    "POST",
    { disabled },
    "Could not update the repair mode",
  );
}

async function promptMutation(path: string, method: string, body: Record<string, unknown>): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(path, {
    method,
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify(body)
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(String(payload.error || response.status));
  return payload;
}

export async function fetchPrompts(): Promise<Array<Record<string, unknown>>> {
  const response = await fetch("/api/llm/prompts", { credentials: "include" });
  if (!response.ok) throw new Error(`Prompt registry failed: ${response.status}`);
  const payload = await response.json();
  return payload.prompts || [];
}

export async function fetchPrompt(promptId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`/api/llm/prompts/${encodeURIComponent(promptId)}`, { credentials: "include" });
  if (!response.ok) throw new Error(`Prompt detail failed: ${response.status}`);
  return response.json();
}

export async function fetchPromptVersions(promptId: string): Promise<Array<Record<string, unknown>>> {
  const response = await fetch(`/api/llm/prompts/${encodeURIComponent(promptId)}/versions`, { credentials: "include" });
  if (!response.ok) throw new Error(`Prompt versions failed: ${response.status}`);
  const payload = await response.json();
  return payload.versions || [];
}

export async function validatePrompt(promptId: string, template: string): Promise<Record<string, unknown>> {
  return promptMutation("/api/llm/regression-test", "POST", { prompt_id: promptId, template });
}

export async function updatePrompt(promptId: string, template: string): Promise<Record<string, unknown>> {
  return promptMutation(`/api/llm/prompts/${encodeURIComponent(promptId)}`, "PUT", { template });
}

export async function rollbackPrompt(promptId: string, revisionId: string): Promise<Record<string, unknown>> {
  return promptMutation(`/api/llm/prompts/${encodeURIComponent(promptId)}/rollback`, "POST", { revision_id: revisionId });
}

function normalizeEntity(item: EntitySummary & { related_ids?: string[]; badges?: string[]; detail?: Record<string, unknown>; risk_level?: string }): EntitySummary {
  const updated = Date.parse(String(item.updated_at || ""));
  const status = String(item.status || "unknown");
  const severity = status.toLowerCase().includes("fail") || status.toLowerCase().includes("offline") || status.toLowerCase().includes("error") ? "warning" : "normal";
  return {
    id: String(item.id || ""),
    type: String(item.type || "resource"),
    title: String(item.title || item.id || "Untitled resource"),
    subtitle: String(item.subtitle || item.type || ""),
    status,
    severity: item.severity || severity,
    updated_at: Number.isFinite(updated) ? updated : undefined,
    owner: item.owner || "AEGIS",
    tags: item.tags || item.badges || [],
    relations: item.relations || (item.related_ids || []).map((id) => ({ type: "related", id })),
    available_actions: item.available_actions || [{ id: "inspect", label: "Inspect", level: "view" }],
    permissions: item.permissions || [],
    data: item.data || item.detail || {}
  };
}

export function displayReadQuery(): string {
  if (typeof window === "undefined") return "";
  const token = new URLSearchParams(window.location.search).get("display_token");
  return token ? `?display_token=${encodeURIComponent(token)}` : "";
}

// ---------------------------------------------------------------------------
// Agent Sessions (Phase D4 / DASHBOARD_REFINED_PLAN.md §3 Phase D4)
// ---------------------------------------------------------------------------

export type AgentSessionSummary = {
  agent_session_id: string;
  task_id: string;
  first_event_ms: number;
  last_event_ms: number;
  event_count: number;
  kinds: string[];
  status: "running" | "completed" | "failed" | "unknown";
  summary: string;
  // Phase D5 — Policy / Approval 表示統合
  policy_allow_count: number;
  policy_ask_count: number;
  policy_deny_count: number;
  highest_risk: string;
  approval_count: number;
  pending_approval: boolean;
  causal_summary?: string;
  root_cause?: AgentSessionRootCause | null;
  milestones?: AgentSessionMilestone[];
};

export type AgentSessionRootCause = {
  kind: string;
  summary: string;
  timestamp_ms: number;
  trace_id: string;
  parent_id: string;
  activity_id: string;
  category: string;
  confidence: number;
};

export type AgentSessionMilestone = {
  key: string;
  kind: string;
  label: string;
  variant: string;
  timestamp_ms: number;
  trace_id: string;
  parent_id: string;
  activity_id: string;
};

export type AgentSessionChainItem = {
  key: string;
  kind: string;
  timestamp_ms: number;
  summary: string;
  status: string;
  trace_id: string;
  parent_id: string;
  activity_id: string;
  depth: number;
};

export type AgentSessionList = {
  generated_at: number;
  count: number;
  sessions: AgentSessionSummary[];
};

export type AgentSessionDetail = {
  generated_at: number;
  agent_session_id: string;
  found: boolean;
  summary: AgentSessionSummary;
  events: Array<Record<string, unknown>>;
  causal_chain?: AgentSessionChainItem[];
};

export type AgentSessionEvents = {
  generated_at: number;
  agent_session_id: string;
  count: number;
  kinds: string[] | null;
  events: Array<Record<string, unknown>>;
};

export async function fetchAgentSessions(limit = 50): Promise<AgentSessionList> {
  const response = await fetch(`/api/ui/agent-sessions?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<AgentSessionList>(response, "Could not load agent sessions");
}

export async function fetchAgentSession(agentSessionId: string, limit = 500): Promise<AgentSessionDetail> {
  const response = await fetch(`/api/ui/agent-sessions/${encodeURIComponent(agentSessionId)}?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<AgentSessionDetail>(response, "Could not load agent session", [404]);
}

export async function fetchAgentSessionEvents(
  agentSessionId: string,
  kinds: string[],
  limit = 500,
): Promise<AgentSessionEvents> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (kinds.length) params.set("kinds", kinds.join(","));
  const response = await fetch(`/api/ui/agent-sessions/${encodeURIComponent(agentSessionId)}/events?${params}`, {
    credentials: "include",
  });
  return requireJson<AgentSessionEvents>(response, "Could not load agent session events");
}

// ---------------------------------------------------------------------------
// L1 / L2 / L3 panels (DASHBOARD_V3_PLAN.md Phase L6)
//
// L1 = 知覚 / Router / 常時稼働
// L2 = Autonomous Mind / 自律思考
// L3 = Deep Reasoner / 深層推論
//
// 各 layer の event を EventManager.persisted events から読み取り専用で取得する。
// バックエンド実装: aegis_ai.web.routes.l1_routes / l2_routes / l3_routes
// ---------------------------------------------------------------------------

export type LlmLayer = "L1" | "L2" | "L3";

export type LlmEvent = {
  event_id?: string;
  type?: string;
  source?: string;
  timestamp?: number;
  payload?: Record<string, unknown>;
  [key: string]: unknown;
};

export type LlmEventsResponse = {
  generated_at: number;
  layer: LlmLayer;
  count: number;
  kinds: string[] | null;
  events: LlmEvent[];
};

export type LlmEventsStats = {
  generated_at: number;
  layer: LlmLayer;
  total: number;
  by_kind: Record<string, number>;
};

export async function fetchL1Events(kinds: string[] = [], limit = 200): Promise<LlmEventsResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (kinds.length) params.set("kinds", kinds.join(","));
  const response = await fetch(`/api/l1/events?${params}`, { credentials: "include" });
  return requireJson<LlmEventsResponse>(response, "Could not load L1 events");
}

export async function fetchL1EventsRecent(limit = 1): Promise<LlmEventsResponse> {
  const response = await fetch(`/api/l1/events/recent?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<LlmEventsResponse>(response, "Could not load L1 recent events");
}

export async function fetchL1EventsStats(): Promise<LlmEventsStats> {
  const response = await fetch("/api/l1/events/stats", { credentials: "include" });
  return requireJson<LlmEventsStats>(response, "Could not load L1 stats");
}

export async function fetchL2Events(kinds: string[] = [], limit = 200): Promise<LlmEventsResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (kinds.length) params.set("kinds", kinds.join(","));
  const response = await fetch(`/api/l2/events?${params}`, { credentials: "include" });
  return requireJson<LlmEventsResponse>(response, "Could not load L2 events");
}

export async function fetchL2EventsRecent(limit = 1): Promise<LlmEventsResponse> {
  const response = await fetch(`/api/l2/events/recent?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<LlmEventsResponse>(response, "Could not load L2 recent events");
}

export async function fetchL2EventsStats(): Promise<LlmEventsStats> {
  const response = await fetch("/api/l2/events/stats", { credentials: "include" });
  return requireJson<LlmEventsStats>(response, "Could not load L2 stats");
}

export async function fetchL3Events(kinds: string[] = [], limit = 200): Promise<LlmEventsResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (kinds.length) params.set("kinds", kinds.join(","));
  const response = await fetch(`/api/l3/events?${params}`, { credentials: "include" });
  return requireJson<LlmEventsResponse>(response, "Could not load L3 events");
}

export async function fetchL3EventsRecent(limit = 1): Promise<LlmEventsResponse> {
  const response = await fetch(`/api/l3/events/recent?${new URLSearchParams({ limit: String(limit) })}`, {
    credentials: "include",
  });
  return requireJson<LlmEventsResponse>(response, "Could not load L3 recent events");
}

export async function fetchL3EventsStats(): Promise<LlmEventsStats> {
  const response = await fetch("/api/l3/events/stats", { credentials: "include" });
  return requireJson<LlmEventsStats>(response, "Could not load L3 stats");
}

/**
 * event_type / event_id 文字列から layer (L1 / L2 / L3 / MCP) を推定する。
 * Live Overlay のラベル ("L1: ..." / "L2: ..." / "L3: ..." / "MCP: ...") に使う。
 */
export function inferLayerFromEvent(eventType: string | undefined | null): LlmLayer | "MCP" {
  const value = String(eventType || "");
  if (value.startsWith("l1.")) return "L1";
  if (value.startsWith("l2.")) return "L2";
  if (value.startsWith("l3.")) return "L3";
  return "MCP";
}

export function createRequestId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    return [...bytes].map((value) => value.toString(16).padStart(2, "0")).join("");
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export type ChatHistoryEntry = {
  timestamp?: number;
  timestamp_ms?: number;
  message_id?: string;
  user?: string;
  bot?: string;
  conversation_id?: string;
};

export type ChatSendResult = {
  response?: string;
  message?: string;
  request_id?: string;
  needs_user_input?: boolean;
  question?: string;
  options?: string[];
  pending_context?: Record<string, unknown>;
  tool_results?: Array<{ function?: string; success?: boolean; result?: string }>;
};

export async function fetchChatHistory(): Promise<ChatHistoryEntry[]> {
  const response = await fetch("/api/chat/history", { credentials: "include" });
  const payload = await requireJson<ChatHistoryEntry[] | { items?: ChatHistoryEntry[] }>(
    response,
    "Could not load chat history",
  );
  return Array.isArray(payload) ? payload : payload.items || [];
}

export async function sendChat(message: string, requestId = createRequestId()): Promise<ChatSendResult> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/chat/send", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ text: message, request_id: requestId })
  });
  return requireJson<ChatSendResult>(response, "Could not send the chat message");
}

export async function respondChat(
  answer: string,
  pendingContext: Record<string, unknown> = {},
): Promise<ChatSendResult> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/chat/respond", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ response: answer, pending_context: pendingContext }),
  });
  return requireJson<ChatSendResult>(response, "Could not continue the chat");
}

export type SavedView = {
  id: string;
  resource: string;
  name: string;
  query: string;
  filters: Record<string, string>;
  sort: string;
  order: "asc" | "desc";
  page_size: number;
  created_at: number;
  updated_at: number;
};

export async function fetchSavedViews(resource: string): Promise<SavedView[]> {
  const response = await fetch(`/api/ui/saved-views?${new URLSearchParams({ resource })}`, { credentials: "include" });
  const payload = await requireJson<{ items: SavedView[] }>(response, "Could not load saved views");
  return payload.items || [];
}

export async function createSavedView(input: Omit<SavedView, "id" | "created_at" | "updated_at">): Promise<SavedView> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/ui/saved-views", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify(input),
  });
  return requireJson<SavedView>(response, "Could not create the saved view");
}

export async function deleteSavedView(viewId: string): Promise<void> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/ui/saved-views/${encodeURIComponent(viewId)}`, {
    method: "DELETE",
    credentials: "include",
    headers: { "X-CSRF-Token": csrf },
  });
  await requireJson(response, "Could not delete the saved view");
}

export async function resolveApproval(approvalId: string, decision: "approve" | "reject"): Promise<void> {
  const endpoint = decision === "approve" ? "approve" : "reject";
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/approvals/${approvalId}/${endpoint}`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrf,
    },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({} as Record<string, unknown>));
    const detail = String(payload.error || payload.message || response.status);
    if (detail.includes("fresh_passkey") || response.status === 403 && detail.includes("fresh")) {
      throw new Error("Fresh passkey required. Open /auth/login, authenticate, then approve again.");
    }
    if (detail.includes("CSRF") || response.status === 403 && detail.toLowerCase().includes("csrf")) {
      throw new Error("CSRF token missing or expired. Refresh the page and try again.");
    }
    throw new Error(`Approval ${decision} failed: ${detail}`);
  }
}

export async function fetchAuthMe(): Promise<Record<string, unknown>> {
  const response = await fetch("/auth/me", { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Auth session request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchSettings(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/settings", { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Settings request failed: ${response.status}`);
  }
  return response.json();
}

export async function updateSetting(section: string, key: string, value: unknown): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/settings", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ section, key, value })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = String(payload.error || (Array.isArray(payload.errors) ? payload.errors.join(", ") : "") || response.status);
    throw new Error(message);
  }
  return payload;
}

export async function resetSettings(): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/settings/reset", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRF-Token": csrf }
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(String(payload.error || response.status));
  }
  return payload;
}
