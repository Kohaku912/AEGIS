import { AlertTriangle, ArrowLeft, ArrowRight, Filter, Search, SlidersHorizontal } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { entitiesFromOverview } from "../entityModel";
import { factsForEntity, pageContextFacts, primaryFacts } from "../entityDetail";
import { pageDefinition } from "../navigation";
import type { EntitySummary, UiEvent, UiOverview } from "../types";

const PAGE_FIELDS: Record<string, string[]> = {
  attention: ["Approvals", "Failed tasks", "Blocked work", "Missing permissions", "Offline systems", "Budget warnings", "Security alerts", "Verification failures"],
  plans: ["Version", "Goal", "Assumptions", "Dependency graph", "Expected cost", "Risk", "Approval points", "Verification strategy"],
  commitments: ["Commitment", "Person", "Due date", "Conversation evidence", "Related task", "Notification plan", "Confidence"],
  schedule: ["Trigger", "Condition", "Action", "Cooldown", "Last fired", "Next evaluation", "Result", "Enabled"],
  delegation: ["Assignment", "Server selection", "Capability policy", "Escalation", "Human threshold", "Time limit", "Cost limit"],
  autonomy: ["Enabled / paused", "Last evaluation", "Next evaluation", "Suppression", "Budget gate", "Recent decisions", "Success rate", "Duplicate prevention"],
  memory: ["Type", "Content", "Source", "Confidence", "Importance", "Access", "Relations", "Provenance", "Forgetting policy"],
  sleep: ["Last sleep", "Current phase", "Candidates", "Duplicates", "Contradictions", "Lessons", "Failures", "Next run"],
  "user-model": ["Preferences", "Routines", "Locations", "Relationships", "Skills", "Projects", "Confidence", "Conflicts"],
  situation: ["Location", "Device", "Active application", "Activity", "Attention", "Availability", "Evidence", "Last observation"],
  context: ["System prompt", "History", "Memories", "Events", "User state", "Tool schemas", "Token allocation", "Retrieval reasons"],
  "models-prompts": ["Model registry", "Routing", "Fallback", "Reasoning", "Token limits", "Prompt usage", "Dead prompts", "Evaluation / rollback"],
  "capability-catalog": ["ID", "Server", "Schema", "Risk", "Approval", "Permissions", "Completion", "Verification", "Latency", "Success rate"],
  "generated-capabilities": ["Reason", "Source task", "Source files", "Tests", "Security review", "Promotion status", "Usage"],
  "capability-executions": ["Capability", "Task", "Server", "Arguments", "Result", "Verification", "Approval", "Duration", "Retry", "Error"],
  "policy-simulation": ["Actor", "Capability", "Arguments", "Target", "Environment", "Effective risk", "Matching rule", "Decision"],
  devices: ["Identity", "Model", "OS", "App version", "Network", "Battery", "Screen", "Permissions", "Capabilities", "Role"],
  network: ["LAN", "Tailscale", "Cloudflare", "gRPC", "SSE", "HTTP", "Heartbeat", "Direction"],
  deployment: ["Version", "Commit", "Image", "Target", "Last deployment", "Rollback", "Config drift", "Persistence"],
  storage: ["Database", "ChromaDB", "Audit", "Memory", "Logs", "Reports", "Backups", "Disk / retention"],
  conversations: ["Channel", "Participants", "Messages", "Drafts", "Sent", "Approvals", "Tasks", "Delivery"],
  notifications: ["Unread", "Delivered", "Failed", "Suppressed", "Expired", "Acknowledged", "Channel"],
  "presentation-surfaces": ["Connection", "Scene", "Queue", "Priorities", "Privacy", "Presentation", "Acknowledgment", "Reduced motion"],
  policy: ["Global rules", "Capability rules", "Data access", "Privacy", "Approval", "Budget", "Time", "User presence"],
  security: ["Passkeys", "Sessions", "CSRF", "Fresh auth", "Secrets", "Exposure", "Security events", "Secret scan"],
  privacy: ["Display", "Collection", "Clipboard", "Camera", "Microphone", "Location", "Retention", "Redaction"],
  audit: ["Who", "What", "When", "Why", "Before", "After", "Task", "Approval", "Result", "Device"],
  "llm-usage": ["Requests", "Model", "Input", "Output", "Cache hit / miss", "Context", "Memory", "Tool schema", "Cost", "Retry loops"],
  errors: ["Fingerprint", "Active", "Recovered", "Repeated", "Suppressed", "Verification", "Connection", "Capability"],
  performance: ["API latency", "Manager latency", "Capability latency", "Event lag", "Reconnects", "CPU", "RAM", "GPU", "Queue"],
  reports: ["Production readiness", "UI completeness", "Capability coverage", "Mock audit", "E2E", "Soak", "Security", "Backup", "Device"],
};

export function DomainPage({ pageId, overview, events, onSelect, developerMode = false }: { pageId: string; overview: UiOverview; events: UiEvent[]; onSelect: (entity: EntitySummary) => void; developerMode?: boolean }) {
  const definition = pageDefinition(pageId);
  const [query, setQuery] = useState("");
  const [savedView, setSavedView] = useState("all");
  const [statusFilter, setStatusFilter] = useState("");
  const [sort, setSort] = useState("updated_at");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState("");
  const resource = resourceForPage(pageId);
  const resourceQuery = useQuery({
    queryKey: ["ui-resource", resource, query, statusFilter, sort, page],
    queryFn: () => fetchResourceEntities(resource || "tasks", query, { page, limit: 25, status: statusFilter, sort }),
    enabled: Boolean(resource),
    staleTime: 5_000,
    retry: 1
  });
  const overviewEntities = useMemo(() => resourcesForPage(pageId, overview, events), [pageId, overview, events]);
  const entities = resourceQuery.data ? resourceQuery.data.items : overviewEntities;
  const filtered = entities.filter((item) => {
    if (!resource && !`${item.title} ${item.subtitle} ${item.status}`.toLowerCase().includes(query.toLowerCase())) return false;
    if (savedView === "attention") return item.severity !== "normal";
    if (savedView === "active") return ["running", "active", "online", "waiting"].includes(item.status.toLowerCase());
    if (savedView === "recent") return Boolean(item.updated_at && Date.now() - item.updated_at < 86_400_000);
    return true;
  });
  const selected = filtered.find((item) => item.id === selectedId) || filtered[0];
  const fields = PAGE_FIELDS[pageId] || ["Status", "Source", "Owner", "Updated", "Result", "Reason"];
  const contractFacts = factsForEntity(selected, fields);
  const fallbackFacts = primaryFacts(selected, 10);
  const contextFacts = pageContextFacts(pageId, overview).filter((fact) => !fact.missing && fact.value !== "Not reported");
  const reportedFacts = contractFacts.filter((fact) => !fact.missing && fact.value !== "Not reported");
  const detailFacts = developerMode
    ? (reportedFacts.length ? contractFacts : fallbackFacts)
    : (reportedFacts.length ? reportedFacts : fallbackFacts.filter((fact) => fact.value !== "Not reported"));


  useEffect(() => {
    if (selected && selected.id !== selectedId) setSelectedId(selected.id);
  }, [selected, selectedId]);

  const openEntity = (item: EntitySummary) => {
    setSelectedId(item.id);
    onSelect(item);
  };

  return (
    <div className="resource-page" data-domain={definition.domain.id}>
      <header className="resource-page__hero">
        <div>
          <span>{definition.domain.label}</span>
          <h2>{definition.page.label}</h2>
          <p>{pageDescription(pageId)}</p>
        </div>
        <div className="resource-page__counts">
          <strong>{resourceQuery.data?.total || entities.length}</strong>
          <span>reported entities</span>
        </div>
      </header>

      {contextFacts.length ? (
        <section className="resource-context" aria-label={`${definition.page.label} live context`}>
          {contextFacts.map((fact) => (
            <article key={fact.label}>
              <span>{fact.label}</span>
              <strong>{fact.value}</strong>
            </article>
          ))}
        </section>
      ) : null}

      <div className="resource-toolbar">
        <label>
          <Search size={15} />
          <input value={query} onChange={(event) => { setQuery(event.currentTarget.value); setPage(1); }} placeholder={`Search ${definition.page.label.toLowerCase()}`} />
        </label>
        <label className="filter-select">
          <Filter size={15} />
          <span>Status</span>
          <select value={statusFilter} onChange={(event) => { setStatusFilter(event.currentTarget.value); setPage(1); }}>
            <option value="">All states</option>
            {[...new Set(entities.map((item) => item.status).filter(Boolean))].sort().map((status) => <option value={status} key={status}>{status}</option>)}
          </select>
        </label>
        <label className="filter-select">
          <span>Sort</span>
          <select value={sort} onChange={(event) => { setSort(event.currentTarget.value); setPage(1); }}>
            <option value="updated_at">Recently updated</option>
            <option value="title">Title</option>
            <option value="status">Status</option>
            <option value="type">Type</option>
          </select>
        </label>
        <label className="saved-view-select">
          <SlidersHorizontal size={15} />
          <span>Saved view</span>
          <select value={savedView} onChange={(event) => setSavedView(event.currentTarget.value)}>
            <option value="all">All resources</option>
            <option value="attention">Needs attention</option>
            <option value="active">Active operations</option>
            <option value="recent">Updated today</option>
          </select>
        </label>
      </div>

      <section className="resource-layout">
        <div className="resource-list" aria-label={`${definition.page.label} list`}>
          {resourceQuery.isLoading ? <div className="resource-state"><span className="status-dot" />Loading live resources...</div> : null}
          {resourceQuery.isError ? <div className="resource-state resource-state--warning"><AlertTriangle size={17} />Live resource API is unavailable. Showing the latest overview snapshot.</div> : null}
          {filtered.map((item) => (
            <button
              className="resource-row"
              data-status={item.status.toUpperCase()}
              data-selected={selected?.id === item.id}
              type="button"
              key={`${item.type}:${item.id}`}
              onClick={() => openEntity(item)}
            >
              <span className="resource-row__domain">{item.type}</span>
              <span>
                <strong>{item.title}</strong>
                <small>{item.subtitle || itemPreview(item)}</small>
              </span>
              <span className="resource-row__status">{item.status}</span>
              <ArrowRight size={14} />
            </button>
          ))}
          {!filtered.length ? (
            <div className="resource-empty">
              <AlertTriangle size={20} />
              <strong>No matching live entities</strong>
              <p>{emptyMessage(pageId, overview)}</p>
            </div>
          ) : null}
        </div>

        <aside className="resource-detail" aria-label={`${definition.page.label} detail`}>
          {selected ? (
            <>
              <header>
                <span>{selected.type}</span>
                <h3>{selected.title}</h3>
                <p>{selected.subtitle || "Manager-backed resource detail"}</p>
              </header>
              <dl className="resource-detail__facts">
                {detailFacts.map((fact) => (
                  <div key={fact.label} data-missing={fact.missing || undefined}>
                    <dt>{fact.label}</dt>
                    <dd>{fact.value}</dd>
                  </div>
                ))}
              </dl>
              {developerMode && selected ? (
                <pre className="developer-raw">{JSON.stringify(selected.data || {}, null, 2)}</pre>
              ) : null}
              {selected.relations.length ? (
                <section>
                  <h4>Relations</h4>
                  <div className="relation-list">
                    {selected.relations.map((relation) => (
                      <span key={`${relation.type}:${relation.id}`}>{relation.type}: {relation.label || relation.id}</span>
                    ))}
                  </div>
                </section>
              ) : null}
              <footer>
                <button className="secondary-button" type="button" onClick={() => onSelect(selected)}>Open in Inspector</button>
              </footer>
            </>
          ) : (
            <div className="resource-empty">
              <strong>Select a resource</strong>
              <p>Operational values appear here from Manager projections, not placeholder field names.</p>
            </div>
          )}
        </aside>
      </section>

      {resource ? (
        <footer className="resource-pagination">
          <span>{resourceQuery.data?.total || 0} total / page {resourceQuery.data?.page || page}</span>
          <div>
            <button className="icon-button" type="button" title="Previous page" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}><ArrowLeft size={15} /></button>
            <button className="icon-button" type="button" title="Next page" disabled={!resourceQuery.data?.has_more} onClick={() => setPage((value) => value + 1)}><ArrowRight size={15} /></button>
          </div>
        </footer>
      ) : null}
    </div>
  );
}

function itemPreview(item: EntitySummary): string {
  const data = item.data || {};
  const candidates = [data.summary, data.message, data.content, data.body, data.reason, data.result, data.status_detail];
  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) return candidate.slice(0, 120);
  }
  return item.type;
}

function emptyMessage(pageId: string, overview: UiOverview): string {
  if (pageId === "attention") {
    return (overview.attention.data.items || []).length
      ? "Attention items exist in Overview; refine filters to show them."
      : "No attention items are currently reported by ApprovalManager or StatusManager.";
  }
  if (pageId === "commitments") return "CommitmentManager has no open commitments.";
  if (pageId === "notifications") return "NotificationManager has no recent notifications.";
  if (pageId === "generated-capabilities") return "No generated capabilities are registered yet.";
  if (pageId === "capability-executions") return "No execution history in the current overview window.";
  if (pageId === "errors") return "RepairManager has no recent repair events.";
  if (pageId === "reports") return "BehavioralEvaluation has no metrics yet.";
  if (pageId === "conversations" || pageId === "social") return "SocialManager has no inbox items yet.";
  return "Data appears when the backing manager reports it.";
}

function resourceForPage(pageId: string): string | undefined {
  if (["plans", "tasks", "open-loops"].includes(pageId)) return "tasks";
  if (pageId === "schedule") return "hooks";
  if (pageId === "delegation") return "delegations";
  if (pageId === "autonomy") return "autonomy";
  if (pageId === "commitments") return "commitments";
  if (["servers", "network", "deployment", "storage", "performance"].includes(pageId)) return "servers";
  if (pageId === "devices") return "devices";
  if (pageId === "memory") return "memories";
  if (pageId === "sleep") return "sleep";
  // Context is DecisionContext projection — do not hit memory resource API.
  if (pageId === "context" || pageId === "decision-context") return undefined;
  if (pageId === "user-model" || pageId === "situation") return undefined;
  if (pageId === "models-prompts") return "prompts";
  if (pageId === "capability-catalog") return "capabilities";
  // Generated and Executions use dedicated overview sections, not the full catalog.
  if (pageId === "generated-capabilities" || pageId === "capability-executions") return undefined;
  if (pageId === "policy-simulation") return "capabilities";
  if (pageId.includes("approval") || pageId === "attention") return "approvals";
  if (["audit", "security", "privacy", "policy", "llm-usage"].includes(pageId)) return "audit";
  // Errors → RepairManager overview; Reports → Behavioral Evaluation overview.
  if (pageId === "errors" || pageId === "reports") return undefined;
  if (pageId === "conversations" || pageId === "social") return undefined;
  if (pageId === "notifications") return "notifications";
  if (pageId === "presentation-surfaces") return "presentations";
  return undefined;
}

function resourcesForPage(pageId: string, overview: UiOverview, events: UiEvent[]): EntitySummary[] {
  const all = entitiesFromOverview(overview, events);
  if (pageId === "attention") {
    const attention = (overview.attention.data.items || []).map((item) => ({
      id: String(item.id),
      type: "attention",
      title: String(item.title || item.kind || "Attention"),
      subtitle: String(item.message || item.recovery_hint || item.kind || "attention"),
      status: String(item.severity || "info"),
      severity: String(item.severity || "normal"),
      updated_at: item.created_at,
      owner: "AEGIS",
      tags: [String(item.kind || "attention")],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: item as unknown as Record<string, unknown>
    }));
    return [...attention, ...all.filter((item) => item.severity !== "normal" || item.type === "approval")];
  }
  if (["plans", "tasks", "open-loops"].includes(pageId)) return all.filter((item) => item.type === "task");
  if (pageId === "commitments") return all.filter((item) => item.type === "commitment");
  if (["servers", "devices", "network", "deployment", "storage"].includes(pageId)) return all.filter((item) => item.type === "server");
  if (pageId === "notifications") return all.filter((item) => item.type === "notification");
  if (pageId === "generated-capabilities") {
    return ((overview.generated_capabilities?.data.items || []) as Array<Record<string, unknown>>).map((item, index) => ({
      id: String(item.capability_id || item.id || index),
      type: "generated_capability",
      title: String(item.short_name || item.capability_id || item.id || "Generated capability"),
      subtitle: String(item.description || item.origin || "generated"),
      status: String(item.status || item.promotion_status || "generated"),
      severity: "normal",
      updated_at: Number(item.updated_at || 0) || undefined,
      owner: "AEGIS",
      tags: ["generated"],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: item,
    }));
  }
  if (pageId === "capability-executions") {
    const ops = (overview.executions?.data.operations || overview.activity?.data.operations || []) as Array<Record<string, unknown>>;
    return ops.map((item, index) => ({
      id: String(item.operation_id || index),
      type: "execution",
      title: String(item.title || item.kind_label || "Execution"),
      subtitle: String(item.what_happened || item.summary || ""),
      status: String(item.status || "ok"),
      severity: Number(item.error_count || 0) > 0 ? "warning" : "normal",
      updated_at: Number(item.updated_at || item.started_at || 0) || undefined,
      owner: "AEGIS",
      tags: [String(item.kind || "operation")],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: item,
    }));
  }
  if (pageId === "context" || pageId === "decision-context") {
    const ctx = overview.decision_context?.data || overview.agent_state?.data || {};
    return [{
      id: "decision-context",
      type: "decision_context",
      title: "Decision context",
      subtitle: String(ctx.summary || "").slice(0, 160),
      status: "live",
      severity: "normal",
      owner: "AEGIS",
      tags: ["agent_state"],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: ctx as Record<string, unknown>,
    }];
  }
  if (pageId === "errors") {
    const items = (overview.repairs?.data.items || overview.errors?.data.items || []) as Array<Record<string, unknown>>;
    return items.map((item, index) => ({
      id: String(item.repair_id || item.id || index),
      type: "repair",
      title: String(item.category || item.title || "Repair"),
      subtitle: String(item.error || item.message || item.summary || ""),
      status: String(item.status || "recorded"),
      severity: "warning",
      updated_at: Number(item.updated_at || item.created_at || 0) || undefined,
      owner: "AEGIS",
      tags: ["repair"],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: item,
    }));
  }
  if (pageId === "reports") {
    const reports = overview.behavioral_reports?.data || {};
    return [{
      id: "behavioral-report",
      type: "behavioral_report",
      title: "Behavioral evaluation",
      subtitle: String(reports.summary || ""),
      status: "live",
      severity: "normal",
      owner: "AEGIS",
      tags: ["evaluation"],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: reports as Record<string, unknown>,
    }];
  }
  if (pageId === "conversations" || pageId === "social") {
    const items = (overview.social?.data.inbox || overview.social?.data.pending_decisions || []) as Array<Record<string, unknown>>;
    return items.map((item, index) => ({
      id: String(item.item_id || index),
      type: "social",
      title: String(item.channel || "Social"),
      subtitle: String(item.body || item.body_preview || item.summary || "").slice(0, 120),
      status: String(item.status || "pending"),
      severity: "normal",
      updated_at: Number(item.updated_at || item.created_at || 0) || undefined,
      owner: "AEGIS",
      tags: ["social"],
      relations: [],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" as const }],
      permissions: [],
      data: item,
    }));
  }
  if (["audit", "performance", "llm-usage"].includes(pageId)) return all.filter((item) => item.type === "event");
  if (pageId.includes("approval")) return all.filter((item) => item.type === "approval");
  return all;
}

function pageDescription(pageId: string): string {
  const descriptions: Record<string, string> = {
    attention: "Human attention ordered by cause, impact, and recommended recovery.",
    autonomy: "Autonomous decisions, pressure, suppression, effectiveness, and budget gates.",
    memory: "Searchable episodic, semantic, procedural, preference, people, skill, and lesson memory.",
    "capability-catalog": "Manifest, user override, effective policy, completion, verification, and execution health.",
    "generated-capabilities": "Capabilities created by codegen — not the full catalog.",
    "capability-executions": "Real operation and autonomous-cycle execution history.",
    network: "Connection topology and traffic direction across LAN, VPN, tunnel, gRPC, and event streams.",
    security: "Passkeys, sessions, fresh authentication, secrets, exposure, and security audit state.",
    "llm-usage": "Request-level tokens, context composition, cache behavior, cost, latency, and retry families.",
    commitments: "Open social and operational commitments with due dates and linked conversations.",
    situation: "Current user location, device, activity, attention, and availability evidence.",
    notifications: "Unread, delivered, failed, and suppressed notifications across channels.",
    errors: "RepairManager history: failures, recovery steps, and lessons.",
    reports: "BehavioralEvaluation metrics: restraint, goal achievement, continuity.",
    conversations: "Chat and AGORA social inbox via SocialManager.",
    context: "Live DecisionContext from AgentState used for initiative and planning.",
  };
  return descriptions[pageId] || "Overview, list, detail, relations, history, configuration, and actions for this AEGIS resource.";
}
