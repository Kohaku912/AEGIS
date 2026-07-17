export type FreshnessEnvelope<T> = {
  generated_at: number;
  source_updated_at: number;
  status: "ok" | "error" | "partial";
  stale: boolean;
  error: string;
  data: T;
};

export type EntitySummary = {
  id: string;
  type: string;
  title: string;
  subtitle: string;
  status: string;
  severity: string;
  created_at?: number;
  updated_at?: number;
  owner?: string;
  tags: string[];
  relations: Array<{ type: string; id: string; label?: string }>;
  available_actions: Array<{ id: string; label: string; level: "view" | "safe" | "controlled" | "dangerous" }>;
  permissions: string[];
  data?: Record<string, unknown>;
};

export type AttentionItem = {
  id: string;
  kind: string;
  severity: "critical" | "warning" | "info" | "normal" | string;
  title: string;
  message: string;
  created_at?: number;
  expires_at?: number;
  recovery_hint?: string;
};

export type ServerItem = {
  server_id: string;
  server_type?: string;
  status: string;
  registered_capabilities?: string;
  heartbeat_age_seconds?: number;
  host?: string;
  port?: number;
  version?: string;
  mode?: string;
  status_detail?: string;
  degraded_reason?: string;
  recovery_hint?: string;
  dependencies?: Record<string, unknown>;
  health_checked_at?: number;
  latency_ms?: number;
  last_healthy_at?: number | string;
  active_task_id?: string;
  permission_missing?: boolean;
  capability_health?: Record<string, unknown>;
  recovery_state?: string;
};

export type ApprovalItem = {
  approval_id: string;
  request_id?: string;
  task_id?: string;
  step_id?: string;
  capability_id: string;
  tool_name?: string;
  risk?: string;
  reason?: string;
  summary?: string;
  target?: string;
  preview?: string;
  side_effects?: string;
  previous_action?: string;
  similar_action_summary?: string;
  expected_effect?: string;
  fresh_auth_required?: boolean;
  created_at?: number;
  expires_at?: number;
  status?: string;
};

export type CurrentTask = {
  task_id: string;
  title: string;
  phase: string;
  original_instruction?: string;
  plan_summary?: string;
  dependency_edges?: Array<Record<string, unknown>>;
  current_action: string;
  next_action: string;
  blocked_reason: string;
  verification_summary?: string;
  final_output?: string;
  audit_group_id?: string;
  conversation_id?: string;
  cost_summary?: string;
  capability_id?: string;
  started_at?: number;
  updated_at?: number;
  steps?: Array<Record<string, unknown>>;
};

export type SurfaceRole = {
  surface_id: string;
  role: string;
  interactive: boolean;
  privacy_levels: string[];
  priorities: string[];
  max_text_chars: number;
  max_display_ms: number;
  actions: string[];
  scenes: string[];
};

export type PresentationEvent = {
  event_id: string;
  scene_type: string;
  priority: "P0" | "P1" | "P2" | "P3" | string;
  severity: string;
  source: string;
  title: string;
  summary: string;
  detail?: string;
  affected_entities: string[];
  task_id?: string;
  approval_id?: string;
  persistence: string;
  expires_at: number;
  privacy_class: string;
  recommended_surfaces: string[];
  visual_hint: {
    effect?: VisualEvent["effect"] | string;
    arc?: string;
    color?: string;
    duration_ms?: number;
  };
  available_actions: Array<Record<string, unknown>>;
};

export type UiOverview = {
  schema_version: string;
  generated_at: number;
  core: FreshnessEnvelope<Record<string, unknown>>;
  connection?: FreshnessEnvelope<Record<string, unknown>>;
  display_scene?: FreshnessEnvelope<Record<string, unknown>>;
  presentations?: FreshnessEnvelope<{
    takeover?: Array<Record<string, unknown>>;
    overlays?: Array<Record<string, unknown>>;
    persistent?: Array<Record<string, unknown>>;
    ambient?: Array<Record<string, unknown>>;
    items?: Array<Record<string, unknown>>;
    count?: number;
  }>;
  presentation_events?: FreshnessEnvelope<{ items?: PresentationEvent[]; count?: number; source?: string }>;
  surface_roles?: FreshnessEnvelope<{ items?: SurfaceRole[]; count?: number; source?: string }>;
  display_queue?: FreshnessEnvelope<{
    items?: Array<Record<string, unknown> & { presentation_event?: PresentationEvent }>;
    count?: number;
    source?: string;
    persisted?: boolean;
  }>;
  tasks?: FreshnessEnvelope<{
    primary?: CurrentTask;
    active?: Array<Record<string, unknown>>;
    waiting?: Array<Record<string, unknown>>;
    scheduled?: Array<Record<string, unknown>>;
    recent?: Array<Record<string, unknown>>;
  }>;
  activity?: FreshnessEnvelope<{
    recent?: Array<Record<string, unknown>>;
    groups?: Array<Record<string, unknown>>;
    count?: number;
    source?: string;
  }>;
  attention: FreshnessEnvelope<{ items: AttentionItem[]; count?: number }>;
  current_task: FreshnessEnvelope<CurrentTask>;
  servers: FreshnessEnvelope<{ items: ServerItem[] }>;
  capabilities?: FreshnessEnvelope<Record<string, unknown>>;
  user_situation?: FreshnessEnvelope<Record<string, unknown>>;
  user_state: FreshnessEnvelope<Record<string, unknown>>;
  mind?: FreshnessEnvelope<Record<string, unknown>>;
  mind_summary: FreshnessEnvelope<Record<string, unknown>>;
  memory?: FreshnessEnvelope<Record<string, unknown>>;
  notifications: FreshnessEnvelope<{ recent?: Array<Record<string, unknown>>; unread_count?: number }>;
  approvals: FreshnessEnvelope<{ pending: ApprovalItem[]; pending_count: number }>;
  commitments: FreshnessEnvelope<{ items: Array<Record<string, unknown>>; summary?: string }>;
  usage: FreshnessEnvelope<Record<string, unknown>>;
  errors?: FreshnessEnvelope<{ items?: Array<Record<string, unknown>>; count?: number }>;
  freshness: FreshnessEnvelope<Record<string, unknown>>;
};

export type UiEvent = {
  event_id?: string;
  sequence?: number;
  type: string;
  event_type?: string;
  source_type: string;
  occurred_at?: number;
  received_at?: number;
  generated_at: number;
  source_updated_at: number;
  priority?: "P0" | "P1" | "P2" | "P3" | string;
  dedupe_key?: string;
  persistence?: "until_resolved" | "attention_dock" | "ephemeral" | string;
  expires_at?: number;
  resolved_by?: string;
  affected_servers?: string[];
  affected_capabilities?: string[];
  safe_title?: string;
  safe_message?: string;
  visual_hint?: {
    effect?: VisualEvent["effect"] | string;
    arc?: string;
    color?: string;
    duration_ms?: number;
  };
  presentation_event?: PresentationEvent;
  scene_type?: string;
  privacy_class?: string;
  recommended_surfaces?: string[];
  available_actions?: Array<Record<string, unknown>>;
  payload: Record<string, unknown>;
  capability_id?: string;
  server_id?: string;
  status?: string;
  approval_id?: string;
  task_id?: string;
  severity?: string;
  message?: string;
};

export type DisplayDirectorItem = {
  id: string;
  priority: "P0" | "P1" | "P2" | "P3" | string;
  severity: string;
  title: string;
  message: string;
  persistence: string;
  createdAt: number;
  expiresAt: number;
  affectedServers: string[];
  visualEvent?: VisualEvent;
};

export type DisplayDirectorState = {
  sceneMode: string;
  privacyMode: boolean;
  offline: boolean;
  stale: boolean;
  takeover?: DisplayDirectorItem;
  overlays: DisplayDirectorItem[];
  dock: DisplayDirectorItem[];
  ambient: DisplayDirectorItem[];
};

export type VisualEvent = {
  id: string;
  type: string;
  effect: "pulse" | "complete" | "fracture" | "containment" | "containment-resolved" | "disconnect" | "recovery";
  serverId: string;
  capabilityId?: string;
  status?: string;
  severity?: string;
  message: string;
  createdAt: number;
  expiresAt: number;
};
