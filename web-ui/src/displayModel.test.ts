import { describe, expect, it } from "vitest";
import { buildDisplayDirectorState, mapUiEventToVisualEvent, serverNeedsDetail, summarizeMemory, summarizeServers } from "./displayModel";
import type { ServerItem, UiOverview } from "./types";

function envelope<T>(data: T) {
  return { generated_at: 1, source_updated_at: 1, status: "ok" as const, stale: false, error: "", data };
}

function emptyTask() {
  return { task_id: "", title: "", phase: "", current_action: "", next_action: "", blocked_reason: "" };
}

describe("display model", () => {
  it("keeps healthy servers compact and expands only actionable states", () => {
    const servers: ServerItem[] = [
      { server_id: "ai-server", status: "ONLINE" },
      { server_id: "pc-server", status: "DEGRADED", status_detail: "slow" },
      { server_id: "android-server", status: "ONLINE", status_detail: "permission missing" }
    ];
    expect(serverNeedsDetail(servers[0])).toBe(false);
    expect(serverNeedsDetail(servers[1])).toBe(true);
    expect(serverNeedsDetail(servers[2])).toBe(true);
    expect(summarizeServers(servers).ok).toBe(1);
  });

  it("maps structured ui events to visual effects without reparsing user text", () => {
    expect(mapUiEventToVisualEvent({
      event_id: "event-1",
      type: "tool.execution.failed",
      source_type: "tool.execution.failed",
      priority: "P0",
      visual_hint: { effect: "fracture", arc: "pc-server", duration_ms: 8000 },
      generated_at: 10,
      source_updated_at: 10,
      payload: {},
      capability_id: "pc-server.mouse.click",
      server_id: "",
      status: "failed",
      severity: "critical",
      message: "failed"
    }).effect).toBe("fracture");
  });

  it("summarizes memory without raw json rendering", () => {
    const overview = {
      schema_version: "ui-overview.v3",
      generated_at: 1,
      core: envelope({ active_goal: "ship ui", confidence: "high" }),
      connection: envelope({ quality: "good" }),
      display_scene: envelope({ phase: "Idle" }),
      presentations: envelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
      display_queue: envelope({ items: [], count: 0, persisted: true }),
      tasks: envelope({ primary: emptyTask(), active: [], waiting: [], scheduled: [], recent: [] }),
      activity: envelope({ recent: [], groups: [], count: 0 }),
      attention: envelope({ items: [] }),
      current_task: envelope({ task_id: "", title: "", phase: "", current_action: "", next_action: "", blocked_reason: "" }),
      servers: envelope({ items: [] }),
      capabilities: envelope({ items: [], count: 0 }),
      user_situation: envelope({}),
      user_state: envelope({}),
      mind: envelope({}),
      mind_summary: envelope({ memory: { episodic: 2, semantic: 3, last_consolidation: "today" }, autonomy: { desires: { growth: 4, social: 2 } } }),
      memory: envelope({ summary: {} }),
      notifications: envelope({ recent: [], unread_count: 0 }),
      approvals: envelope({ pending: [], pending_count: 0 }),
      commitments: envelope({ items: [] }),
      usage: envelope({}),
      errors: envelope({ items: [], count: 0 }),
      freshness: envelope({})
    } satisfies UiOverview;
    expect(summarizeMemory(overview)["Dominant desire"]).toBe("growth");
    expect(summarizeMemory(overview)["Memories used"]).toBe("5");
  });

  it("builds display director takeover from approval and dedupes events", () => {
    const now = Date.now();
    const overview = {
      schema_version: "ui-overview.v3",
      generated_at: 1,
      core: envelope({ health: "ONLINE", mode: "WAITING" }),
      connection: envelope({ quality: "good" }),
      display_scene: envelope({ phase: "Waiting for Approval", takeover: { active: false } }),
      presentations: envelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
      display_queue: envelope({ items: [], count: 0, persisted: true }),
      tasks: envelope({ primary: emptyTask(), active: [], waiting: [], scheduled: [], recent: [] }),
      activity: envelope({ recent: [], groups: [], count: 0 }),
      attention: envelope({ items: [] }),
      current_task: envelope({ task_id: "task-1", title: "Needs approval", phase: "waiting", current_action: "", next_action: "", blocked_reason: "" }),
      servers: envelope({ items: [] }),
      capabilities: envelope({ items: [], count: 0 }),
      user_situation: envelope({}),
      user_state: envelope({}),
      mind: envelope({}),
      mind_summary: envelope({}),
      memory: envelope({}),
      notifications: envelope({ recent: [], unread_count: 0 }),
      approvals: envelope({ pending: [{ approval_id: "approval-1", capability_id: "pc-server.mouse.click", summary: "Click safe surface" }], pending_count: 1 }),
      commitments: envelope({ items: [] }),
      usage: envelope({}),
      errors: envelope({ items: [], count: 0 }),
      freshness: envelope({})
    } satisfies UiOverview;

    const state = buildDisplayDirectorState(overview, [
      {
        event_id: "event-1",
        dedupe_key: "pc-server:running",
        type: "tool.execution.started",
        source_type: "tool.execution.started",
        generated_at: now,
        source_updated_at: now,
        priority: "P3",
        persistence: "ephemeral",
        payload: {},
        server_id: "pc-server",
        message: "Started"
      },
      {
        event_id: "event-2",
        dedupe_key: "pc-server:running",
        type: "tool.execution.started",
        source_type: "tool.execution.started",
        generated_at: now + 10,
        source_updated_at: now + 10,
        priority: "P3",
        persistence: "ephemeral",
        payload: {},
        server_id: "pc-server",
        message: "Started again"
      }
    ]);

    expect(state.takeover?.priority).toBe("P1");
    expect(state.takeover?.title).toBe("Approval required");
    expect(state.ambient.filter((item) => item.id === "pc-server:running")).toHaveLength(1);
  });

  it("keeps persistent items until resolved while expiring ephemeral duplicates", () => {
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now, displayScene: { phase: "Idle", takeover: { active: false } } });
    const state = buildDisplayDirectorState(overview, [
      {
        event_id: "old-ephemeral",
        dedupe_key: "heartbeat:ai-server",
        type: "status.changed",
        source_type: "status.changed",
        generated_at: now - 20_000,
        source_updated_at: now - 20_000,
        priority: "P3",
        persistence: "ephemeral",
        expires_at: now - 1,
        payload: {},
        message: "Old heartbeat"
      },
      {
        event_id: "approval-event",
        dedupe_key: "approval:1",
        type: "approval.created",
        source_type: "approval.created",
        generated_at: now - 20_000,
        source_updated_at: now - 20_000,
        priority: "P1",
        persistence: "until_resolved",
        expires_at: now - 1,
        payload: {},
        message: "Approval still pending"
      }
    ]);

    expect(state.takeover?.id).toBe("approval:1");
    expect(state.ambient.find((item) => item.id === "heartbeat:ai-server")).toBeUndefined();
  });

  it("restores persistent display queue items from the server-side overview", () => {
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now });
    overview.display_queue = envelope({
      persisted: true,
      count: 1,
      items: [
        {
          id: "server-queue:approval-1",
          event_id: "event-approval-1",
          priority: "P1",
          severity: "warning",
          title: "Approval required",
          message: "Review keyboard action",
          persistence: "until_resolved",
          created_at: now - 5_000,
          expires_at: 0,
          affected_servers: ["pc-server"],
          visual_hint: { effect: "containment", arc: "pc-server" }
        }
      ]
    });

    const state = buildDisplayDirectorState(overview, [], []);

    expect(state.takeover?.id).toBe("server-queue:approval-1");
    expect(state.takeover?.visualEvent?.effect).toBe("containment");
  });

  it("reconciles stale disconnect queue items against the current server snapshot", () => {
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now });
    overview.servers.data.items = [{ server_id: "android-server", status: "ONLINE" }];
    overview.display_queue = envelope({
      persisted: true,
      count: 1,
      items: [
        {
          id: "android-disconnected",
          priority: "P0",
          severity: "critical",
          title: "android.disconnected",
          message: "android.disconnected",
          persistence: "until_resolved",
          affected_servers: ["android-server"],
          visual_hint: { effect: "disconnect", arc: "android-server" }
        }
      ]
    });

    const state = buildDisplayDirectorState(overview, [], []);

    expect(state.takeover).toBeUndefined();
    expect(state.dock).toHaveLength(0);
  });

  it("does not render server-side display queue items that are already resolved", () => {
    const overview = minimalOverview();
    overview.display_queue = envelope({
      persisted: true,
      count: 1,
      items: [
        {
          id: "android-disconnected",
          priority: "P0",
          severity: "critical",
          title: "android.disconnected",
          message: "android.disconnected",
          persistence: "until_resolved",
          resolved_by: "status.changed:online",
          visual_hint: { effect: "disconnect" }
        }
      ]
    });

    expect(buildDisplayDirectorState(overview, [], []).takeover).toBeUndefined();
  });

  it("collapses repeated P2 event messages while retaining the newest event", () => {
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now });
    const common = {
      type: "agora.read.completed",
      source_type: "agora.read.completed",
      priority: "P2",
      persistence: "attention_dock",
      generated_at: now,
      payload: {},
      message: "AGORA: No new posts."
    };
    const state = buildDisplayDirectorState(overview, [
      { ...common, event_id: "agora-1", source_updated_at: now },
      { ...common, event_id: "agora-2", source_updated_at: now + 10 }
    ]);

    expect(state.dock.filter((item) => item.message === "AGORA: No new posts.")).toHaveLength(1);
    expect(state.dock.find((item) => item.message === "AGORA: No new posts.")?.id).toBe("agora-2");
  });

  it("surfaces offline, stale, and privacy display modes from display scene", () => {
    const overview = minimalOverview({
      freshnessStale: true,
      displayScene: { phase: "Privacy", takeover: { active: false }, privacy_mode: true, offline: true, stale: true }
    });
    const state = buildDisplayDirectorState(overview, [], []);
    expect(state.offline).toBe(true);
    expect(state.stale).toBe(true);
    expect(state.privacyMode).toBe(true);
    expect(state.sceneMode).toBe("Privacy");
  });

  it("keeps ui-overview v3 schema coverage explicit for primary sections", () => {
    const overview = minimalOverview();
    for (const key of [
      "core",
      "connection",
      "display_scene",
      "presentations",
      "display_queue",
      "tasks",
      "activity",
      "attention",
      "current_task",
      "servers",
      "capabilities",
      "user_situation",
      "mind",
      "memory",
      "notifications",
      "approvals",
      "commitments",
      "usage",
      "errors",
      "freshness"
    ] as const) {
      expect(overview[key]).toMatchObject({ generated_at: expect.any(Number), source_updated_at: expect.any(Number), status: expect.any(String), stale: expect.any(Boolean), error: expect.any(String) });
    }
  });
});

function minimalOverview(options: { generatedAt?: number; freshnessStale?: boolean; displayScene?: Record<string, unknown> } = {}): UiOverview {
  const generatedAt = options.generatedAt || Date.now();
  const makeEnvelope = <T,>(data: T, stale = false) => ({ generated_at: generatedAt, source_updated_at: generatedAt, status: "ok" as const, stale, error: "", data });
  return {
    schema_version: "ui-overview.v3",
    generated_at: generatedAt,
    core: makeEnvelope({ health: "ONLINE", mode: "IDLE" }),
    connection: makeEnvelope({ quality: "good" }),
    display_scene: makeEnvelope(options.displayScene || { phase: "Idle", takeover: { active: false }, privacy_mode: false, offline: false, stale: false }),
    presentations: makeEnvelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
    display_queue: makeEnvelope({ items: [], count: 0, persisted: true }),
    tasks: makeEnvelope({ primary: emptyTask(), active: [], waiting: [], scheduled: [], recent: [] }),
    activity: makeEnvelope({ recent: [], groups: [], count: 0 }),
    attention: makeEnvelope({ items: [] }),
    current_task: makeEnvelope(emptyTask()),
    servers: makeEnvelope({ items: [] }),
    capabilities: makeEnvelope({ items: [], count: 0 }),
    user_situation: makeEnvelope({}),
    user_state: makeEnvelope({}),
    mind: makeEnvelope({}),
    mind_summary: makeEnvelope({}),
    memory: makeEnvelope({}),
    notifications: makeEnvelope({ recent: [], unread_count: 0 }),
    approvals: makeEnvelope({ pending: [], pending_count: 0 }),
    commitments: makeEnvelope({ items: [] }),
    usage: makeEnvelope({}),
    errors: makeEnvelope({ items: [], count: 0 }),
    freshness: makeEnvelope({}, Boolean(options.freshnessStale))
  };
}
