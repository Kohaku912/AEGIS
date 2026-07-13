export type FreshnessEnvelope<T> = {
  generated_at: number;
  source_updated_at: number;
  status: "ok" | "error" | "partial";
  stale: boolean;
  error: string;
  data: T;
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
  created_at?: number;
  expires_at?: number;
  status?: string;
};

export type CurrentTask = {
  task_id: string;
  title: string;
  phase: string;
  current_action: string;
  next_action: string;
  blocked_reason: string;
  capability_id?: string;
  started_at?: number;
  updated_at?: number;
  steps?: Array<Record<string, unknown>>;
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
  display_queue?: FreshnessEnvelope<{
    items?: Array<Record<string, unknown>>;
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
