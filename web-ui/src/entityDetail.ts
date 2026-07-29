import type { EntitySummary, UiOverview } from "./types";

export type DetailFact = {
  label: string;
  value: string;
  missing?: boolean;
};

/** Map human field labels used by DomainPage contracts onto likely record keys. */
const FIELD_KEYS: Record<string, string[]> = {
  Approvals: ["approvals", "pending_approvals", "approval_id", "approval_count"],
  "Failed tasks": ["failed_tasks", "failure_count", "failed_count"],
  "Blocked work": ["blocked_reason", "blocked", "waiting_reason"],
  "Missing permissions": ["permission_missing", "missing_permissions", "permissions"],
  "Offline systems": ["offline_servers", "offline", "degraded_servers"],
  "Budget warnings": ["budget_state", "budget_status", "autonomous_suppression"],
  "Security alerts": ["security_alerts", "severity", "security_events"],
  "Verification failures": ["verification", "verification_status", "verification_summary"],
  Version: ["version", "prompt_version", "image_version", "schema_version"],
  Goal: ["goal", "active_goal", "title", "objective"],
  Assumptions: ["assumptions", "plan_assumptions"],
  "Dependency graph": ["dependency_edges", "dependencies", "depends_on"],
  "Expected cost": ["expected_cost", "cost_summary", "estimated_cost"],
  Risk: ["risk", "risk_level", "severity"],
  "Approval points": ["approval_points", "requires_approval", "approval_required"],
  "Verification strategy": ["verification_strategy", "verification", "completion"],
  Commitment: ["title", "content", "summary", "commitment"],
  Person: ["person", "person_name", "counterpart", "participants"],
  "Due date": ["due_at", "due_date", "deadline"],
  "Conversation evidence": ["conversation_id", "evidence", "source_conversation"],
  "Related task": ["task_id", "related_task_id"],
  "Notification plan": ["notification_plan", "notify_at", "channel"],
  Confidence: ["confidence", "confidence_score"],
  Trigger: ["trigger", "kind", "event_type"],
  Condition: ["condition", "predicate", "when"],
  Action: ["action", "capability_id", "handler"],
  Cooldown: ["cooldown_seconds", "cooldown"],
  "Last fired": ["last_fired_at", "last_run_at", "last_triggered_at"],
  "Next evaluation": ["next_evaluation_at", "next_run_at", "next_tick_at"],
  Result: ["result", "last_result", "outcome"],
  Enabled: ["enabled", "active"],
  Assignment: ["assignment", "rule_id", "title"],
  "Server selection": ["server_id", "server_selection", "preferred_server"],
  "Capability policy": ["capability_pattern", "capability_id", "policy"],
  Escalation: ["escalation", "escalation_policy"],
  "Human threshold": ["human_threshold", "decision", "approval_required"],
  "Time limit": ["time_limit_seconds", "timeout_seconds", "deadline"],
  "Cost limit": ["cost_limit", "max_cost"],
  "Enabled / paused": ["enabled", "paused", "mode", "status"],
  "Last evaluation": ["last_evaluation_at", "last_run_at", "updated_at"],
  Suppression: ["suppression", "autonomous_suppression", "suppressed"],
  "Budget gate": ["budget_gate", "budget_state", "budget_status"],
  "Recent decisions": ["recent_decisions", "decision", "last_decision"],
  "Success rate": ["success_rate", "effectiveness", "ok_rate"],
  "Duplicate prevention": ["duplicate_prevention", "dedupe_key"],
  Type: ["type", "memory_type", "kind", "category"],
  Content: ["content", "body", "text", "message", "summary"],
  Source: ["source", "source_type", "owner"],
  Importance: ["importance", "priority"],
  Access: ["access", "permissions", "visibility"],
  Relations: ["relations", "related_ids", "related_posts"],
  Provenance: ["provenance", "origin", "trace_id"],
  "Forgetting policy": ["forgetting_policy", "retention", "ttl"],
  "Last sleep": ["last_sleep_at", "last_completed_at"],
  "Current phase": ["phase", "state", "current_phase"],
  Candidates: ["candidates", "candidate_count"],
  Duplicates: ["duplicates", "duplicate_count"],
  Contradictions: ["contradictions"],
  Lessons: ["lessons", "lesson_count"],
  Failures: ["failures", "failure_count"],
  "Next run": ["next_run_at", "next_sleep_at"],
  Preferences: ["preferences", "preference_summary"],
  Routines: ["routines"],
  Locations: ["locations", "location"],
  Relationships: ["relationships", "people"],
  Skills: ["skills"],
  Projects: ["projects"],
  Conflicts: ["conflicts"],
  Location: ["location", "where", "place"],
  Device: ["device", "device_id", "device_model", "device_status"],
  "Active application": ["active_application", "app", "foreground_app"],
  Activity: ["activity", "activity_label"],
  Attention: ["attention", "attention_level"],
  Availability: ["availability", "available", "summary"],
  Evidence: ["evidence", "sources"],
  "Last observation": ["last_observation_at", "updated_at", "observed_at"],
  "System prompt": ["system_prompt", "system_tokens", "system"],
  History: ["history", "history_tokens"],
  Memories: ["memories", "memory", "memory_tokens"],
  Events: ["events", "event_tokens"],
  "User state": ["user_state", "user_state_tokens"],
  "Tool schemas": ["tool_schema", "tool_schemas", "capability"],
  "Token allocation": ["token_allocation", "max_tokens", "budget"],
  "Retrieval reasons": ["retrieval_reasons", "reasons"],
  "Model registry": ["model", "provider", "registry"],
  Routing: ["routing", "profile_id", "route"],
  Fallback: ["fallback", "fallback_model"],
  Reasoning: ["reasoning_level", "reasoning"],
  "Token limits": ["max_tokens", "token_limit"],
  "Prompt usage": ["prompt_id", "usage_count", "prompt_usage"],
  "Dead prompts": ["dead", "unused"],
  "Evaluation / rollback": ["evaluation", "rollback", "version"],
  ID: ["id", "capability_id"],
  Server: ["server_id", "server"],
  Schema: ["input_schema", "schema", "params"],
  Approval: ["requires_approval", "approval_required", "risk"],
  Permissions: ["permissions", "only_master"],
  Completion: ["completion", "completion_check"],
  Verification: ["verification", "verification_status"],
  Latency: ["latency_ms", "latency", "avg_latency_ms"],
  Reason: ["reason", "generated_reason"],
  "Source task": ["source_task_id", "task_id"],
  "Source files": ["source_files", "files"],
  Tests: ["tests", "test_status"],
  "Security review": ["security_review", "reviewed"],
  "Promotion status": ["promotion_status", "status"],
  Usage: ["usage", "usage_count", "call_count"],
  Actor: ["actor", "owner", "caller"],
  Capability: ["capability_id", "capability"],
  Arguments: ["arguments", "args", "params"],
  Target: ["target", "path", "url"],
  Environment: ["environment", "env", "runtime_mode"],
  "Effective risk": ["effective_risk", "risk_level", "risk"],
  "Matching rule": ["matching_rule", "matched_rule", "rule_id"],
  Decision: ["decision", "policy_decision"],
  Identity: ["device_id", "id", "serial"],
  Model: ["model", "device_model"],
  OS: ["os", "os_version", "platform"],
  "App version": ["app_version", "version"],
  Network: ["network", "connection_mode", "ip"],
  Battery: ["battery", "battery_pct"],
  Screen: ["screen", "screen_on"],
  Role: ["role", "surface_role"],
  LAN: ["lan", "lan_reachable", "host"],
  Tailscale: ["tailscale", "tailscale_ip"],
  Cloudflare: ["cloudflare", "public_url"],
  gRPC: ["grpc", "grpc_port", "port"],
  SSE: ["sse", "stream"],
  HTTP: ["http", "http_port"],
  Heartbeat: ["heartbeat_age_seconds", "last_heartbeat", "heartbeat"],
  Direction: ["direction", "connection_direction"],
  Commit: ["commit", "git_commit", "revision"],
  Image: ["image", "image_tag"],
  "Last deployment": ["last_deployment_at", "deployed_at"],
  Rollback: ["rollback", "rollback_available"],
  "Config drift": ["config_drift", "drift"],
  Persistence: ["persistence", "volumes"],
  Database: ["database", "db"],
  ChromaDB: ["chroma", "chromadb"],
  Audit: ["audit", "audit_path"],
  Memory: ["memory", "memory_bytes"],
  Logs: ["logs", "log_bytes"],
  Reports: ["reports"],
  Backups: ["backups", "backup_count"],
  "Disk / retention": ["disk", "retention", "disk_free"],
  Channel: ["channel", "surface"],
  Participants: ["participants", "authors"],
  Messages: ["messages", "message_count", "body"],
  Drafts: ["drafts", "draft_count"],
  Sent: ["sent", "delivered"],
  Tasks: ["tasks", "task_id"],
  Delivery: ["delivery", "delivery_status"],
  Unread: ["unread", "unread_count"],
  Delivered: ["delivered", "delivered_count"],
  Failed: ["failed", "failed_count"],
  Suppressed: ["suppressed", "suppressed_count"],
  Expired: ["expired", "expires_at"],
  Acknowledged: ["acknowledged", "acked"],
  Connection: ["connection", "status", "mode"],
  Scene: ["scene", "scene_type", "display_scene"],
  Queue: ["queue", "display_queue", "queue_depth"],
  Priorities: ["priorities", "priority"],
  Privacy: ["privacy", "privacy_class", "privacy_mode"],
  Presentation: ["presentation", "title", "summary"],
  Acknowledgment: ["acknowledgment", "acknowledged"],
  "Reduced motion": ["reduced_motion"],
  "Global rules": ["global_rules", "policy"],
  "Capability rules": ["capability_rules"],
  "Data access": ["data_access"],
  "User presence": ["user_presence", "presence"],
  Passkeys: ["passkeys", "passkey_count"],
  Sessions: ["sessions", "session_count"],
  CSRF: ["csrf"],
  "Fresh auth": ["fresh_auth", "fresh_auth_required"],
  Secrets: ["secrets", "secret_scan"],
  Exposure: ["exposure", "public_exposure"],
  "Security events": ["security_events"],
  "Secret scan": ["secret_scan"],
  Display: ["display", "display_privacy"],
  Collection: ["collection"],
  Clipboard: ["clipboard"],
  Camera: ["camera"],
  Microphone: ["microphone"],
  Retention: ["retention"],
  Redaction: ["redaction"],
  Who: ["actor", "who", "owner"],
  What: ["action", "what", "title"],
  When: ["created_at", "updated_at", "timestamp", "when"],
  Why: ["reason", "why"],
  Before: ["before", "before_hash"],
  After: ["after", "after_hash"],
  Requests: ["request_count", "requests"],
  Input: ["input_tokens", "prompt_tokens"],
  Output: ["output_tokens", "completion_tokens"],
  "Cache hit / miss": ["input_cache_hit_tokens", "cache_hit_tokens"],
  Context: ["context_breakdown", "context_meta"],
  Cost: ["provider_reported_cost", "cost_usd", "cost"],
  "Retry loops": ["retry_group_id", "retry_loop_suspect"],
  Fingerprint: ["fingerprint", "error_fingerprint", "dedupe_key"],
  Active: ["active", "active_count"],
  Recovered: ["recovered"],
  Repeated: ["repeated", "repeat_count"],
  "API latency": ["api_latency_ms", "latency_ms"],
  "Manager latency": ["manager_latency_ms"],
  "Capability latency": ["capability_latency_ms"],
  "Event lag": ["event_lag_ms", "lag_ms"],
  Reconnects: ["reconnects", "reconnect_count"],
  CPU: ["cpu", "cpu_pct"],
  RAM: ["ram", "memory_bytes", "rss"],
  GPU: ["gpu"],
  "Production readiness": ["production_readiness", "ready"],
  "UI completeness": ["ui_completeness"],
  "Capability coverage": ["capability_coverage"],
  "Mock audit": ["mock_audit"],
  E2E: ["e2e", "e2e_status"],
  Soak: ["soak"],
  Backup: ["backup", "backup_status"],
};

export function factsForEntity(entity: EntitySummary | undefined, fieldLabels: string[]): DetailFact[] {
  if (!entity) return [];
  const data = flattenRecord(entity.data || {});
  data.status = entity.status;
  data.type = entity.type;
  data.title = entity.title;
  data.subtitle = entity.subtitle;
  data.owner = entity.owner || "AEGIS";
  data.updated_at = entity.updated_at ? new Date(entity.updated_at).toISOString() : "";
  data.id = entity.id;

  return fieldLabels.flatMap((label) => {
    const keys = FIELD_KEYS[label] || [slugKey(label)];
    const found = keys.map((key) => lookupValue(data, key)).find((value) => value !== undefined && value !== null && value !== "");
    if (found === undefined) {
      const loose = Object.entries(data).find(([key, value]) =>
        value !== undefined && value !== null && value !== "" && labelWords(label).every((word) => key.includes(word)),
      );
      if (loose) return [{ label, value: formatValue(loose[1]) }];
      return [];
    }
    return [{ label, value: formatValue(found) }];
  });
}

export function primaryFacts(entity: EntitySummary | undefined, limit = 12): DetailFact[] {
  if (!entity) return [];
  const preferred = [
    "id", "status", "title", "summary", "message", "content", "body", "capability_id", "server_id",
    "task_id", "approval_id", "phase", "mode", "risk_level", "reason", "result", "verification",
    "owner", "source", "created_at", "updated_at", "latency_ms", "host", "port", "version"
  ];
  const data = flattenRecord(entity.data || {});
  const facts: DetailFact[] = [
    { label: "Status", value: entity.status },
    { label: "Owner", value: entity.owner || "AEGIS" },
    { label: "Updated", value: entity.updated_at ? new Date(entity.updated_at).toLocaleString() : "No timestamp" },
  ];
  for (const key of preferred) {
    if (facts.length >= limit) break;
    if (!(key in data)) continue;
    if (["status", "title", "owner"].includes(key)) continue;
    facts.push({ label: humanize(key), value: formatValue(data[key]) });
  }
  if (facts.length < limit) {
    for (const [key, value] of Object.entries(data)) {
      if (facts.length >= limit) break;
      if (preferred.includes(key) || ["title", "subtitle"].includes(key)) continue;
      facts.push({ label: humanize(key), value: formatValue(value) });
    }
  }
  return facts;
}

export function pageContextFacts(pageId: string, overview: UiOverview): DetailFact[] {
  const mind = (overview.mind_summary?.data || overview.mind?.data || {}) as Record<string, unknown>;
  const autonomy = (mind.autonomy || {}) as Record<string, unknown>;
  const memory = (overview.memory?.data || mind.memory || {}) as Record<string, unknown>;
  const user = (overview.situation?.data || overview.user_situation?.data || overview.user_state?.data || {}) as Record<string, unknown>;
  const usage = overview.usage?.data || {};
  const errors = overview.repairs?.data || overview.errors?.data || {};
  const connection = overview.connection?.data || {};
  const capabilities = overview.capabilities?.data || {};
  const commitments = overview.commitments?.data || {};
  const notifications = overview.notifications?.data || {};
  const presentations = overview.presentations?.data || {};
  const core = overview.core?.data || {};
  const decision = overview.decision_context?.data || overview.agent_state?.data || {};
  const generated = overview.generated_capabilities?.data || {};
  const executions = overview.executions?.data || {};
  const social = overview.social?.data || {};
  const reports = overview.behavioral_reports?.data || {};
  const openLoops = overview.open_loops?.data || {};

  const onlyPresent = (facts: DetailFact[]) =>
    facts.filter((fact) => fact.value && fact.value !== "Not reported" && !fact.missing);

  if (pageId === "autonomy") {
    return onlyPresent([
      { label: "Mode", value: String(core.mode || autonomy.mode || "") },
      { label: "Profile", value: String(autonomy.profile || core.attention_level || "") },
      { label: "Next run", value: formatValue(autonomy.next_run_at || autonomy.next_scheduled_at || "") },
      { label: "Pressure", value: formatValue(autonomy.pressured_desires || autonomy.pressure || "") },
      { label: "Running", value: formatValue(autonomy.running ?? autonomy.enabled ?? "") },
    ]);
  }
  if (pageId === "situation" || pageId === "user-model") {
    return Object.entries(user)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .slice(0, 10)
      .map(([key, value]) => ({ label: humanize(key), value: formatValue(value) }));
  }
  if (pageId === "sleep" || pageId === "memory") {
    return Object.entries(memory)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .slice(0, 10)
      .map(([key, value]) => ({ label: humanize(key), value: formatValue(value) }));
  }
  if (pageId === "context" || pageId === "decision-context") {
    return onlyPresent([
      { label: "Summary", value: String(decision.summary || "").slice(0, 200) },
      { label: "Obligations", value: String((decision.obligations as unknown[] | undefined)?.length || "") },
      { label: "Identity", value: String(decision.identity || "") },
    ]);
  }
  if (pageId === "open-loops" || pageId === "commitments") {
    return onlyPresent([
      { label: "Open loops", value: String(openLoops.count || (openLoops.items as unknown[] | undefined)?.length || commitments.items && (commitments.items as unknown[]).length || "") },
      { label: "Summary", value: String(openLoops.summary || commitments.summary || "") },
    ]);
  }
  if (pageId === "notifications") {
    return onlyPresent([
      { label: "Unread", value: String(notifications.unread_count ?? "") },
      { label: "Recent", value: String((notifications.recent as unknown[] | undefined)?.length ?? "") },
    ]);
  }
  if (pageId === "presentation-surfaces") {
    return onlyPresent([
      { label: "Takeover", value: String((presentations.takeover as unknown[] | undefined)?.length ?? "") },
      { label: "Overlays", value: String((presentations.overlays as unknown[] | undefined)?.length ?? "") },
      { label: "Persistent", value: String((presentations.persistent as unknown[] | undefined)?.length ?? "") },
    ]);
  }
  if (pageId === "network" || pageId === "deployment" || pageId === "storage" || pageId === "performance" || pageId === "devices") {
    return onlyPresent([
      { label: "Online", value: `${connection.online_count ?? "?"} / ${connection.total_count ?? "?"}` },
      { label: "Quality", value: String(connection.quality || "") },
      { label: "Attention", value: String(connection.attention_count ?? "") },
    ]);
  }
  if (pageId === "errors" || pageId === "repairs") {
    const repairSummary = "summary" in errors ? String(errors.summary || "") : "";
    return onlyPresent([
      { label: "Repairs", value: String(errors.count || (errors.items as unknown[] | undefined)?.length || "") },
      { label: "Summary", value: repairSummary },
    ]);
  }
  if (pageId === "reports") {
    return onlyPresent([
      { label: "Summary", value: String(reports.summary || "") },
      { label: "Metrics", value: String(Object.keys((reports.metrics || {}) as Record<string, unknown>).length || "") },
    ]);
  }
  if (pageId === "conversations" || pageId === "social") {
    return onlyPresent([
      { label: "Pending", value: String((social.pending_decisions as unknown[] | undefined)?.length || (social.agora as Record<string, unknown> | undefined)?.pending_count || "") },
      { label: "Summary", value: String(social.summary || "") },
    ]);
  }
  if (pageId === "audit" || pageId === "security" || pageId === "privacy" || pageId === "policy") {
    return onlyPresent([
      { label: "Budget", value: String(usage.budget_state || usage.summary || "") },
    ]);
  }
  if (pageId === "generated-capabilities") {
    return onlyPresent([
      { label: "Generated", value: String(generated.count || (generated.items as unknown[] | undefined)?.length || "") },
      { label: "Summary", value: String(generated.summary || "") },
    ]);
  }
  if (pageId === "capability-executions") {
    return onlyPresent([
      { label: "Executions", value: String(executions.count || (executions.operations as unknown[] | undefined)?.length || "") },
      { label: "Summary", value: String(executions.summary || "") },
    ]);
  }
  if (pageId.includes("capability")) {
    return onlyPresent([
      { label: "Catalog", value: String(capabilities.count || (capabilities.items as unknown[] | undefined)?.length || "") },
      { label: "Approval required", value: String(capabilities.approval_required_count ?? "") },
      { label: "High risk", value: String(capabilities.high_risk_count ?? "") },
    ]);
  }
  if (pageId === "attention") {
    return onlyPresent([
      { label: "Attention items", value: String((overview.attention.data.items || []).length) },
      { label: "Pending approvals", value: String(overview.approvals.data.pending_count || 0) },
      { label: "Core health", value: String(core.health || "") },
    ]);
  }
  return [];
}

function flattenRecord(value: Record<string, unknown>, prefix = "", depth = 0): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  if (depth > 3) return out;
  for (const [key, item] of Object.entries(value)) {
    const path = prefix ? `${prefix}.${key}` : key;
    out[key] = item;
    out[path] = item;
    if (item && typeof item === "object" && !Array.isArray(item)) {
      Object.assign(out, flattenRecord(item as Record<string, unknown>, path, depth + 1));
    }
  }
  return out;
}

function lookupValue(data: Record<string, unknown>, key: string): unknown {
  if (key in data) return data[key];
  const lower = key.toLowerCase();
  const match = Object.entries(data).find(([candidate]) => candidate.toLowerCase() === lower || candidate.toLowerCase().endsWith(`.${lower}`));
  return match?.[1];
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") {
    if (value > 1_000_000_000_000) return new Date(value).toLocaleString();
    if (value > 1_000_000_000 && value < 10_000_000_000_000) return new Date(value).toLocaleString();
    return String(value);
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^\d{10,13}$/.test(trimmed)) {
      const numeric = Number(trimmed);
      const ms = numeric > 10_000_000_000 ? numeric : numeric * 1000;
      return new Date(ms).toLocaleString();
    }
    return trimmed.length > 280 ? `${trimmed.slice(0, 277)}...` : trimmed;
  }
  if (Array.isArray(value)) {
    if (!value.length) return "None";
    if (value.every((item) => typeof item !== "object")) return value.slice(0, 8).map(String).join(", ");
    return `${value.length} item(s)`;
  }
  const record = value as Record<string, unknown>;
  const summary = record.summary || record.status || record.message || record.title;
  if (summary !== undefined) return formatValue(summary);
  return Object.entries(record).slice(0, 4).map(([key, item]) => `${key}: ${typeof item === "object" ? "…" : String(item)}`).join(" · ") || "Structured value";
}

function slugKey(label: string): string {
  return label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

function labelWords(label: string): string[] {
  return label.toLowerCase().split(/[^a-z0-9]+/).filter((word) => word.length > 2);
}

function humanize(key: string): string {
  return key.replace(/[._]/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
