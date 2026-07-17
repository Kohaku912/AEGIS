import { AlertTriangle, ArrowLeft, ArrowRight, Filter, Search, SlidersHorizontal } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { fetchResourceEntities } from "../api/client";
import { entitiesFromOverview } from "../entityModel";
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

export function DomainPage({ pageId, overview, events, onSelect }: { pageId: string; overview: UiOverview; events: UiEvent[]; onSelect: (entity: EntitySummary) => void }) {
  const definition = pageDefinition(pageId);
  const [query, setQuery] = useState("");
  const [savedView, setSavedView] = useState("all");
  const [statusFilter, setStatusFilter] = useState("");
  const [sort, setSort] = useState("updated_at");
  const [page, setPage] = useState(1);
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
  const fields = PAGE_FIELDS[pageId] || ["Current effective value", "Source", "Default", "Validation", "Pending changes", "History", "Restart required"];
  return (
    <div className="resource-page" data-domain={definition.domain.id}>
      <header className="resource-page__hero">
        <div><span>{definition.domain.label}</span><h2>{definition.page.label}</h2><p>{pageDescription(pageId)}</p></div>
        <div className="resource-page__counts"><strong>{entities.length}</strong><span>reported entities</span></div>
      </header>
      <div className="resource-toolbar">
        <label><Search size={15} /><input value={query} onChange={(event) => { setQuery(event.currentTarget.value); setPage(1); }} placeholder={`Search ${definition.page.label.toLowerCase()}`} /></label>
        <label className="filter-select"><Filter size={15} /><span>Status</span><select value={statusFilter} onChange={(event) => { setStatusFilter(event.currentTarget.value); setPage(1); }}><option value="">All states</option>{[...new Set(entities.map((item) => item.status).filter(Boolean))].sort().map((status) => <option value={status} key={status}>{status}</option>)}</select></label>
        <label className="filter-select"><span>Sort</span><select value={sort} onChange={(event) => { setSort(event.currentTarget.value); setPage(1); }}><option value="updated_at">Recently updated</option><option value="title">Title</option><option value="status">Status</option><option value="type">Type</option></select></label>
        <label className="saved-view-select"><SlidersHorizontal size={15} /><span>Saved view</span><select value={savedView} onChange={(event) => setSavedView(event.currentTarget.value)}><option value="all">All resources</option><option value="attention">Needs attention</option><option value="active">Active operations</option><option value="recent">Updated today</option></select></label>
      </div>
      <section className="resource-layout">
        <div className="resource-list" aria-label={`${definition.page.label} list`}>
          {resourceQuery.isLoading ? <div className="resource-state"><span className="status-dot" />Loading live resources...</div> : null}
          {resourceQuery.isError ? <div className="resource-state resource-state--warning"><AlertTriangle size={17} />Live resource API is unavailable. Showing the latest overview snapshot.</div> : null}
          {filtered.map((item) => (
            <button className="resource-row" data-status={item.status.toUpperCase()} type="button" key={`${item.type}:${item.id}`} onClick={() => onSelect(item)}>
              <span className="resource-row__domain">{item.type}</span>
              <span><strong>{item.title}</strong><small>{item.subtitle}</small></span>
              <span className="resource-row__status">{item.status}</span><ArrowRight size={14} />
            </button>
          ))}
          {!filtered.length ? <div className="resource-empty"><AlertTriangle size={20} /><strong>No matching live entities</strong><p>The management contract remains visible below; data appears when its Manager reports it.</p></div> : null}
        </div>
        <aside className="resource-schema">
          <h3>Operational detail</h3>
          <p>Summary, relation, history, configuration, and safe actions share the Global Inspector contract.</p>
          <div>{fields.map((field) => <span key={field}>{field}</span>)}</div>
          <footer>List APIs support stable IDs, search, filtering, sort, cursor, and time range.</footer>
        </aside>
      </section>
      {resource ? <footer className="resource-pagination"><span>{resourceQuery.data?.total || 0} total / page {resourceQuery.data?.page || page}</span><div><button className="icon-button" type="button" title="Previous page" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}><ArrowLeft size={15} /></button><button className="icon-button" type="button" title="Next page" disabled={!resourceQuery.data?.has_more} onClick={() => setPage((value) => value + 1)}><ArrowRight size={15} /></button></div></footer> : null}
    </div>
  );
}

function resourceForPage(pageId: string): string | undefined {
  if (["plans", "tasks"].includes(pageId)) return "tasks";
  if (pageId === "schedule") return "hooks";
  if (pageId === "delegation") return "delegations";
  if (pageId === "autonomy") return "autonomy";
  if (pageId === "commitments") return "commitments";
  if (["servers", "network", "deployment", "storage", "performance"].includes(pageId)) return "servers";
  if (pageId === "devices") return "devices";
  if (["memory", "context"].includes(pageId)) return "memories";
  if (pageId === "sleep") return "sleep";
  if (pageId === "user-model") return "user-models";
  if (pageId === "situation") return "situations";
  if (pageId === "models-prompts") return "prompts";
  if (["capability-catalog", "generated-capabilities", "capability-executions", "policy-simulation"].includes(pageId)) return "capabilities";
  if (pageId.includes("approval") || pageId === "attention") return "approvals";
  if (["audit", "errors", "reports", "llm-usage", "security", "privacy", "policy"].includes(pageId)) return "audit";
  if (pageId === "conversations") return "conversations";
  if (pageId === "notifications") return "notifications";
  if (pageId === "presentation-surfaces") return "presentations";
  return undefined;
}

function resourcesForPage(pageId: string, overview: UiOverview, events: UiEvent[]): EntitySummary[] {
  const all = entitiesFromOverview(overview, events);
  if (pageId === "attention") return all.filter((item) => item.severity !== "normal" || ["approval"].includes(item.type));
  if (["plans", "tasks"].includes(pageId)) return all.filter((item) => item.type === "task");
  if (pageId === "commitments") return all.filter((item) => item.type === "commitment");
  if (["servers", "devices", "network", "deployment", "storage"].includes(pageId)) return all.filter((item) => item.type === "server");
  if (pageId === "notifications") return all.filter((item) => item.type === "notification");
  if (["audit", "errors", "performance", "reports", "llm-usage"].includes(pageId)) return all.filter((item) => item.type === "event");
  if (pageId.includes("approval")) return all.filter((item) => item.type === "approval");
  return all;
}

function pageDescription(pageId: string): string {
  const descriptions: Record<string, string> = {
    attention: "Human attention ordered by cause, impact, and recommended recovery.",
    autonomy: "Autonomous decisions, pressure, suppression, effectiveness, and budget gates.",
    memory: "Searchable episodic, semantic, procedural, preference, people, skill, and lesson memory.",
    "capability-catalog": "Manifest, user override, effective policy, completion, verification, and execution health.",
    network: "Connection topology and traffic direction across LAN, VPN, tunnel, gRPC, and event streams.",
    security: "Passkeys, sessions, fresh authentication, secrets, exposure, and security audit state.",
    "llm-usage": "Request-level tokens, context composition, cache behavior, cost, latency, and retry families."
  };
  return descriptions[pageId] || "Overview, list, detail, relations, history, configuration, and actions for this AEGIS resource.";
}
