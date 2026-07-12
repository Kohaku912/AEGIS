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
  attention: FreshnessEnvelope<{ items: AttentionItem[]; count?: number }>;
  current_task: FreshnessEnvelope<CurrentTask>;
  servers: FreshnessEnvelope<{ items: ServerItem[] }>;
  user_state: FreshnessEnvelope<Record<string, unknown>>;
  mind_summary: FreshnessEnvelope<Record<string, unknown>>;
  notifications: FreshnessEnvelope<{ recent?: Array<Record<string, unknown>>; unread_count?: number }>;
  approvals: FreshnessEnvelope<{ pending: ApprovalItem[]; pending_count: number }>;
  commitments: FreshnessEnvelope<{ items: Array<Record<string, unknown>>; summary?: string }>;
  usage: FreshnessEnvelope<Record<string, unknown>>;
  freshness: FreshnessEnvelope<Record<string, unknown>>;
};

export type UiEvent = {
  type: string;
  source_type: string;
  generated_at: number;
  source_updated_at: number;
  payload: Record<string, unknown>;
};
