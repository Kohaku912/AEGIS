import { describe, expect, it } from "vitest";
import { buildDisplayDirectorState, eventAgentSessionId, liveOverlayPriority, mapUiEventToVisualEvent, pickLiveOverlayEvent, pickLiveOverlayEventForAgent, readableDisplayText, recentDisplayEvents, serverNeedsDetail, summarizeMemory, summarizeServers, summarizeTokenUsage, summarizeUserState } from "./displayModel";
import type { ServerItem, UiEvent, UiOverview } from "./types";

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

  it("summarizes the persistent display user state with freshness", () => {
    const overview = minimalOverview();
    overview.user_state = {
      ...overview.user_state,
      stale: true,
      data: {
        where: { label: "home", confidence: 0.91 },
        attention: { device: "pc", label: "focused", confidence: 0.82 },
        activity: { label: "coding", confidence: 0.73 },
        updated_at_ms: 1234
      }
    };

    expect(summarizeUserState(overview)).toEqual({
      where: "home",
      whereConfidence: "91%",
      attention: "pc / focused",
      attentionConfidence: "82%",
      activity: "coding",
      activityConfidence: "73%",
      freshness: "STALE",
      updatedAt: 1234
    });
  });

  it("falls back to situation string fields when nested user-state labels are empty", () => {
    const overview = minimalOverview();
    overview.user_state = envelope({});
    overview.user_situation = envelope({
      where: "desk",
      location: "office",
      attention: "phone",
      activity: "reading",
      updated_at_ms: 99
    });

    expect(summarizeUserState(overview)).toMatchObject({
      where: "desk",
      attention: "phone",
      activity: "reading",
      updatedAt: 99
    });
  });

  it("keeps leftover P0/P1 items in overlays after takeover claims one", () => {
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now });
    const state = buildDisplayDirectorState(overview, [
      {
        event_id: "crit-1",
        type: "tool.execution.failed",
        source_type: "tool.execution.failed",
        generated_at: now,
        source_updated_at: now,
        priority: "P0",
        persistence: "until_resolved",
        payload: {},
        message: "Disk full",
        severity: "critical"
      },
      {
        event_id: "crit-2",
        type: "approval.created",
        source_type: "approval.created",
        generated_at: now,
        source_updated_at: now,
        priority: "P1",
        persistence: "until_resolved",
        payload: {},
        message: "Needs review",
        severity: "warning"
      }
    ]);

    expect(state.takeover).toBeTruthy();
    expect(state.overlays.some((item) => ["P0", "P1"].includes(String(item.priority)))).toBe(true);
  });

  it("fills recent display events from presentation_events then operations", () => {
    const overview = minimalOverview();
    overview.presentation_events = envelope({
      items: [{
        event_id: "pe-1",
        scene_type: "notice",
        priority: "P2",
        severity: "info",
        source: "test",
        title: "Presented",
        summary: "Shown on display",
        affected_entities: [],
        persistence: "ephemeral",
        expires_at: 0,
        privacy_class: "normal",
        recommended_surfaces: [],
        visual_hint: {},
        available_actions: []
      }],
      count: 1
    });
    expect(recentDisplayEvents(overview, [])[0]?.title).toBe("Presented");

    overview.presentation_events = envelope({ items: [], count: 0 });
    overview.activity = envelope({
      recent: [],
      groups: [],
      operations: [{ operation_id: "op-1", title: "Opened file", what_happened: "Opened file", narrative: "Read notes" }],
      count: 1
    });
    expect(recentDisplayEvents(overview, [])[0]?.message).toBe("Read notes");
  });

  it("humanizes json telemetry and drops user_activity director noise", () => {
    expect(readableDisplayText('{"active_window_title":"Overwatch","pid":1}', "Event")).toBe("Overwatch");
    const now = Date.now();
    const overview = minimalOverview({ generatedAt: now });
    const state = buildDisplayDirectorState(overview, [
      {
        event_id: "noise-1",
        type: "pc.user_activity.snapshot",
        source_type: "pc.user_activity.snapshot",
        generated_at: now,
        source_updated_at: now,
        priority: "P2",
        persistence: "ephemeral",
        payload: {},
        message: '{"active_window_title":"Overwatch"}',
        severity: "info"
      }
    ]);
    expect(state.overlays.some((item) => item.message.includes("{"))).toBe(false);
    expect(state.ambient.some((item) => item.message.includes("{"))).toBe(false);
    overview.presentation_events = envelope({
      items: [{
        event_id: "pe-2",
        scene_type: "notice",
        priority: "P2",
        severity: "info",
        source: "test",
        title: "Presented",
        summary: "Shown on display",
        affected_entities: [],
        persistence: "ephemeral",
        expires_at: 0,
        privacy_class: "normal",
        recommended_surfaces: [],
        visual_hint: {},
        available_actions: []
      }],
      count: 1
    });
    expect(recentDisplayEvents(overview, [
      {
        id: "json",
        priority: "P2",
        severity: "info",
        title: "pc.user_activity.snapshot",
        message: '{"active_window_title":"Overwatch"}',
        persistence: "ephemeral",
        createdAt: now,
        expiresAt: 0,
        affectedServers: []
      }
    ])[0]?.title).toBe("Presented");
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

function eventOf(overrides: Partial<UiEvent>): UiEvent {
  return {
    event_id: "ev-1",
    type: "activity.updated",
    source_type: "activity.updated",
    generated_at: 1,
    source_updated_at: 1,
    payload: {},
    ...overrides
  };
}

describe("live overlay priority (Phase D2, instruction.md §20)", () => {
  it("approval.created is the highest priority", () => {
    expect(liveOverlayPriority(eventOf({ type: "approval.created" }))).toBe(0);
    expect(liveOverlayPriority(eventOf({ type: "approval.pending" }))).toBe(0);
  });

  it("failures rank above tool completions", () => {
    const failure = liveOverlayPriority(eventOf({ type: "agent.failed" }));
    const toolFailed = liveOverlayPriority(eventOf({ type: "tool.execution.failed" }));
    const toolDone = liveOverlayPriority(eventOf({ type: "agent.tool.completed", payload: { ok: true } }));
    const toolDoneFailed = liveOverlayPriority(eventOf({ type: "agent.tool.completed", payload: { ok: false } }));
    expect(failure).toBe(1);
    expect(toolFailed).toBe(1);
    expect(toolDoneFailed).toBe(1);
    expect(toolDone).toBe(4);
    expect(failure).toBeLessThan(toolDone);
  });

  it("critical severity is treated as a failure even if type is benign", () => {
    expect(liveOverlayPriority(eventOf({ type: "activity.updated", severity: "critical" }))).toBe(1);
  });

  it("agent.waiting and agent.verifying are mid-high priority", () => {
    expect(liveOverlayPriority(eventOf({ type: "agent.waiting" }))).toBe(2);
    expect(liveOverlayPriority(eventOf({ type: "agent.verifying" }))).toBe(2);
  });

  it("agent.thinking is below tool events", () => {
    expect(liveOverlayPriority(eventOf({ type: "agent.thinking" }))).toBe(5);
    expect(liveOverlayPriority(eventOf({ type: "agent.tool.started" }))).toBe(3);
  });

  it("activity.updated is the lowest explicit priority", () => {
    expect(liveOverlayPriority(eventOf({ type: "activity.updated" }))).toBe(8);
  });
});

describe("pickLiveOverlayEvent (Phase D2)", () => {
  it("returns undefined for empty or noise-only events", () => {
    expect(pickLiveOverlayEvent([])).toBeUndefined();
    expect(
      pickLiveOverlayEvent([
        eventOf({ type: "android.snapshot", source_type: "android.snapshot", event_id: "and-1" }),
      ]),
    ).toBeUndefined();
  });

  it("picks approval over failure and over tool started", () => {
    const approval = eventOf({ event_id: "a", type: "approval.created", generated_at: 100, payload: { capability_id: "x" } });
    const failure = eventOf({ event_id: "b", type: "agent.failed", generated_at: 200 });
    const tool = eventOf({ event_id: "c", type: "agent.tool.started", generated_at: 300 });
    expect(pickLiveOverlayEvent([tool, failure, approval])?.event_id).toBe("a");
  });

  it("picks the most recent event when priorities are equal", () => {
    const newer = eventOf({ event_id: "newer", type: "agent.thinking", generated_at: 500 });
    const older = eventOf({ event_id: "older", type: "agent.thinking", generated_at: 100 });
    expect(pickLiveOverlayEvent([older, newer])?.event_id).toBe("newer");
  });

  it("promotes a failed tool completion above a fresh thinking event", () => {
    const thinking = eventOf({ event_id: "think", type: "agent.thinking", generated_at: 1000 });
    const toolFailed = eventOf({ event_id: "tool-fail", type: "agent.tool.completed", payload: { ok: false }, generated_at: 1 });
    expect(pickLiveOverlayEvent([thinking, toolFailed])?.event_id).toBe("tool-fail");
  });
});

describe("eventAgentSessionId (Phase D8, instruction.md §19)", () => {
  it("prefers payload._trace_ids.agent_session_id over payload.agent_session_id", () => {
    const event = eventOf({
      event_id: "x",
      type: "agent.thinking",
      payload: {
        agent_session_id: "fallback",
        _trace_ids: { agent_session_id: "primary" },
      },
    });
    expect(eventAgentSessionId(event)).toBe("primary");
  });

  it("falls back to payload.agent_session_id when _trace_ids is missing", () => {
    const event = eventOf({
      event_id: "x",
      type: "agent.thinking",
      payload: { agent_session_id: "from-payload" },
    });
    expect(eventAgentSessionId(event)).toBe("from-payload");
  });

  it("returns empty string when no session id is present", () => {
    const event = eventOf({ event_id: "x", type: "agent.thinking" });
    expect(eventAgentSessionId(event)).toBe("");
  });
});

describe("pickLiveOverlayEventForAgent (Phase D8, instruction.md §19, §20)", () => {
  it("returns undefined for empty or noise-only events", () => {
    expect(pickLiveOverlayEventForAgent([])).toBeUndefined();
    expect(
      pickLiveOverlayEventForAgent([
        eventOf({ type: "android.snapshot", source_type: "android.snapshot", event_id: "and-1" }),
      ]),
    ).toBeUndefined();
  });

  it("groups by agent_session_id and picks the highest-priority session", () => {
    const sessionAThinking = eventOf({
      event_id: "a-think",
      type: "agent.thinking",
      generated_at: 500,
      payload: { agent_session_id: "session-A" },
    });
    const sessionAApproval = eventOf({
      event_id: "a-approval",
      type: "approval.created",
      generated_at: 100,
      payload: { agent_session_id: "session-A" },
    });
    const sessionBTool = eventOf({
      event_id: "b-tool",
      type: "agent.tool.started",
      generated_at: 800,
      payload: { agent_session_id: "session-B" },
    });
    // 複数 agent_session 並列 → Approval 優先 (session-A の approval が勝つ)
    expect(pickLiveOverlayEventForAgent([sessionAThinking, sessionAApproval, sessionBTool])?.event_id).toBe("a-approval");
  });

  it("prefers a session with fresher high-priority event over an older one", () => {
    const sessionAOld = eventOf({
      event_id: "a-old",
      type: "agent.thinking",
      generated_at: 100,
      payload: { agent_session_id: "session-A" },
    });
    const sessionBApproval = eventOf({
      event_id: "b-approval",
      type: "approval.created",
      generated_at: 200,
      payload: { agent_session_id: "session-B" },
    });
    // session-B の方が優先度高いので勝つ
    expect(pickLiveOverlayEventForAgent([sessionAOld, sessionBApproval])?.event_id).toBe("b-approval");
  });

  it("promotes failed tool completion from a different session above thinking", () => {
    const sessionAThinking = eventOf({
      event_id: "a-think",
      type: "agent.thinking",
      generated_at: 1000,
      payload: { agent_session_id: "session-A" },
    });
    const sessionBToolFailed = eventOf({
      event_id: "b-tool-fail",
      type: "agent.tool.completed",
      payload: { ok: false, agent_session_id: "session-B" },
      generated_at: 1,
    });
    expect(pickLiveOverlayEventForAgent([sessionAThinking, sessionBToolFailed])?.event_id).toBe("b-tool-fail");
  });

  it("treats events without agent_session_id as a single (unassigned) group", () => {
    const thinkingNoSession = eventOf({
      event_id: "no-sess-think",
      type: "agent.thinking",
      generated_at: 100,
    });
    const sessionATool = eventOf({
      event_id: "a-tool",
      type: "agent.tool.started",
      generated_at: 200,
      payload: { agent_session_id: "session-A" },
    });
    // session-A の方が優先度高い (Tool started < Thinking) ので session-A の tool が勝つ
    expect(pickLiveOverlayEventForAgent([thinkingNoSession, sessionATool])?.event_id).toBe("a-tool");
  });
});

describe("summarizeTokenUsage (Phase D9 — instruction.md §25)", () => {
  it("returns zero summary for empty or events without token info", () => {
    const usage = summarizeTokenUsage([]);
    expect(usage.event_count).toBe(0);
    expect(usage.input_tokens).toBe(0);
    expect(usage.output_tokens).toBe(0);
    expect(usage.cached_tokens).toBe(0);
    expect(usage.estimated_cost_usd).toBe(0);
    expect(usage.model).toBe("");

    const usage2 = summarizeTokenUsage([eventOf({ type: "agent.thinking" })]);
    expect(usage2.event_count).toBe(0);
  });

  it("reads token_usage object from payload", () => {
    const event = eventOf({
      type: "agent.completed",
      payload: {
        token_usage: {
          input_tokens: 1000,
          output_tokens: 200,
          cached_tokens: 50,
          model: "gpt-4o",
          estimated_cost_usd: 0.0123,
        },
      },
    });
    const usage = summarizeTokenUsage([event]);
    expect(usage.event_count).toBe(1);
    expect(usage.input_tokens).toBe(1000);
    expect(usage.output_tokens).toBe(200);
    expect(usage.cached_tokens).toBe(50);
    expect(usage.estimated_cost_usd).toBeCloseTo(0.0123);
    expect(usage.model).toBe("gpt-4o");
  });

  it("reads scalar token fields from payload directly", () => {
    const event = eventOf({
      type: "agent.completed",
      payload: {
        input_tokens: 500,
        output_tokens: 100,
        cached_tokens: 25,
        cost: 0.005,
        model: "claude-3-5-sonnet",
      },
    });
    const usage = summarizeTokenUsage([event]);
    expect(usage.event_count).toBe(1);
    expect(usage.input_tokens).toBe(500);
    expect(usage.output_tokens).toBe(100);
    expect(usage.cached_tokens).toBe(25);
    expect(usage.estimated_cost_usd).toBeCloseTo(0.005);
    expect(usage.model).toBe("claude-3-5-sonnet");
  });

  it("supports OpenAI-compatible usage fields (prompt_tokens / completion_tokens)", () => {
    const event = eventOf({
      type: "agent.completed",
      payload: {
        usage: { prompt_tokens: 800, completion_tokens: 150 },
        model: "gpt-3.5-turbo",
      },
    });
    const usage = summarizeTokenUsage([event]);
    expect(usage.event_count).toBe(1);
    expect(usage.input_tokens).toBe(800);
    expect(usage.output_tokens).toBe(150);
    expect(usage.model).toBe("gpt-3.5-turbo");
  });

  it("aggregates token usage across multiple events", () => {
    const events = [
      eventOf({
        type: "agent.completed",
        payload: { input_tokens: 100, output_tokens: 50, cost: 0.001, model: "gpt-4o" },
      }),
      eventOf({
        type: "agent.completed",
        payload: { input_tokens: 200, output_tokens: 80, cost: 0.002, model: "gpt-4o" },
      }),
      eventOf({
        type: "agent.thinking", // 集計対象外
        payload: { text: "ignore me" },
      }),
    ];
    const usage = summarizeTokenUsage(events);
    expect(usage.event_count).toBe(2);
    expect(usage.input_tokens).toBe(300);
    expect(usage.output_tokens).toBe(130);
    expect(usage.estimated_cost_usd).toBeCloseTo(0.003);
    expect(usage.model).toBe("gpt-4o");
  });
});
