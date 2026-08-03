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
};

export async function fetchAuditEntries(page = 1, limit = 50): Promise<AuditPageResult> {
  const response = await fetch(`/api/audit?${new URLSearchParams({ page: String(page), limit: String(limit) })}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load logs");
  return {
    items: Array.isArray(payload.entries) ? payload.entries as Array<Record<string, unknown>> : [],
    page: Number(payload.page || page),
    limit: Number(payload.per_page || limit),
    total: Number(payload.total || 0),
    totalPages: Number(payload.total_pages || 1),
  };
}

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

export async function fetchActivityLogs(page = 1, limit = 30): Promise<AuditPageResult> {
  const response = await fetch(`/api/audit/grouped?${new URLSearchParams({ page: String(page), limit: String(limit) })}`, {
    credentials: "include",
  });
  const payload = await requireJson<Record<string, unknown>>(response, "Could not load activity logs");
  const operations = Array.isArray(payload.operations)
    ? payload.operations as Array<Record<string, unknown>>
    : Array.isArray(payload.groups)
      ? payload.groups as Array<Record<string, unknown>>
      : [];
  return {
    items: operations,
    page: Number(payload.page || page),
    limit: Number(payload.per_page || limit),
    total: Number(payload.total ?? payload.count ?? operations.length),
    totalPages: Number(payload.total_pages || 1),
  };
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

export async function simulatePolicy(input: Record<string, unknown>): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/policy/simulate", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify(input)
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(String(payload.error || response.status));
  return payload;
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

export async function updateManagedRule(kind: "hooks" | "delegations", id: string, patch: Record<string, unknown>, confirmed = false): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch(`/api/${kind}/${encodeURIComponent(id)}`, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ patch, confirmed })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok && response.status !== 202) throw new Error(String(payload.error || response.status));
  return payload;
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

export function createRequestId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    return [...bytes].map((value) => value.toString(16).padStart(2, "0")).join("");
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export async function sendChat(message: string, requestId = createRequestId()): Promise<Record<string, unknown>> {
  const response = await fetch("/api/chat/send", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: message, request_id: requestId })
  });
  return requireJson<Record<string, unknown>>(response, "Could not send the chat message");
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
