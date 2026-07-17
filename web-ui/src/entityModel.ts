import type { EntitySummary, UiEvent, UiOverview } from "./types";

export function entitiesFromOverview(overview: UiOverview, events: UiEvent[] = []): EntitySummary[] {
  const taskEntities = [
    ...(overview.tasks?.data.active || []),
    ...(overview.tasks?.data.waiting || []),
    ...(overview.tasks?.data.scheduled || []),
    ...(overview.tasks?.data.recent || [])
  ].map((item) => entity(item, "task", String(item.task_id || item.id || ""), String(item.title || item.original_instruction || "Task")));
  const serverEntities = (overview.servers.data.items || []).map((item) => entity(item as unknown as Record<string, unknown>, "server", item.server_id, item.server_type || item.server_id));
  const approvalEntities = (overview.approvals.data.pending || []).map((item) => entity(item as unknown as Record<string, unknown>, "approval", item.approval_id, item.summary || item.capability_id || "Approval"));
  const commitmentEntities = (overview.commitments.data.items || []).map((item) => entity(item, "commitment", String(item.commitment_id || item.id || ""), String(item.title || item.content || item.summary || "Commitment")));
  const notificationEntities = (overview.notifications.data.recent || []).map((item) => entity(item, "notification", String(item.notification_id || item.id || ""), String(item.title || item.message || "Notification")));
  const eventEntities = events.map((item) => entity(item as unknown as Record<string, unknown>, "event", String(item.event_id || `${item.type}-${item.source_updated_at}`), item.safe_title || item.type));
  const unique = new Map<string, EntitySummary>();
  for (const item of [...taskEntities, ...serverEntities, ...approvalEntities, ...commitmentEntities, ...notificationEntities, ...eventEntities]) {
    if (item.id) unique.set(`${item.type}:${item.id}`, item);
  }
  return [...unique.values()];
}

export function searchEntities(entities: EntitySummary[], query: string): EntitySummary[] {
  const value = query.trim().toLocaleLowerCase();
  if (!value) return entities.slice(0, 12);
  return entities.filter((item) => [item.title, item.subtitle, item.type, item.status, ...item.tags].join(" ").toLocaleLowerCase().includes(value)).slice(0, 30);
}

function entity(data: Record<string, unknown>, type: string, id: string, title: string): EntitySummary {
  const status = String(data.status || data.phase || data.state || "available");
  const severity = String(data.severity || (status.toLowerCase().includes("fail") || status.toLowerCase().includes("offline") ? "warning" : "normal"));
  return {
    id,
    type,
    title,
    subtitle: String(data.subtitle || data.summary || data.capability_id || data.status_detail || type),
    status,
    severity,
    created_at: numeric(data.created_at),
    updated_at: numeric(data.updated_at || data.last_seen),
    owner: String(data.owner || data.source || "AEGIS"),
    tags: [type, status, String(data.server_id || ""), String(data.capability_id || "")].filter(Boolean),
    relations: relationList(data),
    available_actions: actionsFor(type, status),
    permissions: type === "approval" ? ["fresh-auth"] : [],
    data
  };
}

function relationList(data: Record<string, unknown>): EntitySummary["relations"] {
  return [
    ["task", data.task_id],
    ["approval", data.approval_id],
    ["capability", data.capability_id],
    ["server", data.server_id],
    ["conversation", data.conversation_id]
  ].filter((entry) => entry[1]).map(([type, id]) => ({ type: String(type), id: String(id) }));
}

function actionsFor(type: string, status: string): EntitySummary["available_actions"] {
  const actions: EntitySummary["available_actions"] = [{ id: "inspect", label: "Inspect", level: "view" }];
  if (type === "task" && status.toLowerCase() === "running") actions.push({ id: "pause", label: "Pause", level: "safe" });
  if (type === "task" && status.toLowerCase().includes("fail")) actions.push({ id: "retry", label: "Preview retry", level: "controlled" });
  if (type === "approval") actions.push({ id: "review", label: "Review approval", level: "dangerous" });
  return actions;
}

function numeric(value: unknown): number | undefined {
  const result = Number(value || 0);
  return Number.isFinite(result) && result > 0 ? result : undefined;
}
