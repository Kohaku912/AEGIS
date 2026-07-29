import { cleanup, render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { ActivityPage } from "./ActivityPage";
import { Approvals } from "./Approvals";
import { CommandCenter } from "./CommandCenter";
import { JudgmentPage } from "./JudgmentPage";
import { MindMemory } from "./MindMemory";
import { OpenLoopsPage } from "./OpenLoopsPage";
import { OperationsPage } from "./OperationsPage";
import { Settings } from "./Settings";
import { SocialPage } from "./SocialPage";
import { Systems } from "./Systems";
import { Work } from "./Work";
import type { UiOverview } from "../types";
import { navigation } from "../navigation";

vi.mock("../components/cognitive-field/CognitiveField", () => ({
  CognitiveField: () => <div data-testid="cognitive-field-mock" />,
}));

describe("dashboard v2 pages", () => {
  afterEach(() => cleanup());

  beforeAll(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it("renders Mind & Memory summary without standard raw JSON", () => {
    renderMindMemory(overview());
    expect(screen.getByText("Mind & Memory")).toBeInTheDocument();
    expect(screen.getByText("Active goal")).toBeInTheDocument();
    const developer = screen.getByText("Developer raw state").closest("details");
    expect(developer).not.toBeNull();
    expect(within(developer as HTMLElement).getByText(/"advanced"/)).toBeInTheDocument();
  });

  it("renders Work queues and task detail", () => {
    render(<Work overview={overview()} />);
    expect(screen.getByRole("tablist", { name: "Work queues" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Task details" })).toBeInTheDocument();
    expect(screen.getAllByText("pc-server.screenshot.get_screenshot").length).toBeGreaterThan(0);
  });

  it("renders Open Loops with owner and next action", () => {
    render(<OpenLoopsPage overview={overview()} />);
    expect(screen.getByText("Unresolved work AEGIS still owns")).toBeInTheDocument();
    expect(screen.getAllByText("Follow up on review").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Approve or reject").length).toBeGreaterThan(0);
  });

  it("renders Operation causal chain stages", () => {
    render(<OperationsPage overview={overview()} />);
    expect(screen.getByText("Causal chain of each AEGIS action")).toBeInTheDocument();
    expect(screen.getByText("Trigger")).toBeInTheDocument();
    expect(screen.getByText("Learning")).toBeInTheDocument();
  });

  it("renders Initiative non-action and Social AGORA pending", () => {
    render(<JudgmentPage overview={overview()} focus="initiative" />);
    expect(screen.getByText("Why no action")).toBeInTheDocument();
    expect(screen.getAllByText("budget gate").length).toBeGreaterThan(0);

    cleanup();
    render(<SocialPage overview={overview()} />);
    expect(screen.getByText("Social inbox & AGORA decisions")).toBeInTheDocument();
    expect(screen.getByText(/hello from agora/i)).toBeInTheDocument();
  });
  it("keeps five task-oriented navigation domains", () => {
    expect(navigation.map((domain) => domain.id)).toEqual([
      "home",
      "work",
      "communications",
      "systems",
      "administration",
    ]);
    expect(navigation.find((domain) => domain.id === "work")?.pages.some((page) => page.id === "open-loops")).toBe(true);
  });

  it("renders Systems topology and Android detail", () => {
    render(<Systems overview={overview()} />);
    expect(screen.getByLabelText("Server topology")).toBeInTheDocument();
    expect(screen.getByText("Android Detail")).toBeInTheDocument();
    const androidDetail = screen.getByText("Android Detail").closest(".panel");
    expect(androidDetail).not.toBeNull();
    expect(within(androidDetail as HTMLElement).getByText("21121210G")).toBeInTheDocument();
  });

  it("renders Settings sections instead of legacy-only links", () => {
    render(<Settings overview={overview()} />);
    expect(screen.getByText("Autonomy")).toBeInTheDocument();
    expect(screen.getAllByText("Permissions").length).toBeGreaterThan(0);
    expect(screen.getByText("Backup")).toBeInTheDocument();
    expect(screen.getByText("Passkeys")).toBeInTheDocument();
  });

  it("keeps manager-to-api-to-ui coverage visible across primary pages", () => {
    const data = overview();

    const { unmount } = render(<CommandCenter overview={data} recentEvents={[event()]} />);
    expect(screen.getByText("Inspect desktop")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open related conversation" })).toHaveAttribute(
      "href",
      "/chat?conversation_id=conversation-1",
    );
    expect(screen.getAllByText("Connection dropped").length).toBeGreaterThan(0);
    expect(screen.getByText(/1 open/i)).toBeInTheDocument();
    unmount();

    const work = render(<Work overview={data} />);
    expect(screen.getByText("Capture screen")).toBeInTheDocument();
    expect(screen.getByText("Verify output")).toBeInTheDocument();
    work.unmount();

    const approvals = render(<Approvals overview={data} />);
    expect(screen.getAllByText("approval-1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Type into safe field").length).toBeGreaterThan(0);
    approvals.unmount();

    const systems = render(<Systems overview={data} />);
    expect(screen.getByText("21121210G")).toBeInTheDocument();
    expect(screen.getAllByText(/device\.get_status/).length).toBeGreaterThan(0);
    systems.unmount();

    const mind = renderMindMemory(data);
    expect(screen.getByText("User is available")).toBeInTheDocument();
    expect(screen.getByText("1 commitment")).toBeInTheDocument();
    expect(screen.getByText("Review UI")).toBeInTheDocument();
    mind.unmount();

    render(<ActivityPage overview={data} recentEvents={[event()]} />);
    expect(screen.getByText("AEGIS Operations")).toBeInTheDocument();
    expect(screen.getByText("User instruction: Inspect desktop")).toBeInTheDocument();
    expect(screen.getAllByText("Captured a screenshot of the desktop.").length).toBeGreaterThan(0);
    expect(screen.getByText("Task task-1")).toBeInTheDocument();
  });
});

function renderMindMemory(data: UiOverview) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><MindMemory overview={data} /></QueryClientProvider>);
}

function envelope<T>(data: T) {
  return { generated_at: 1000, source_updated_at: 1000, status: "ok" as const, stale: false, error: "", data };
}

function overview(): UiOverview {
  return {
    schema_version: "ui-overview.v4",
    generated_at: 1000,
    core: envelope({ active_goal: "Ship UI", confidence: "high", health: "ONLINE", mode: "EXECUTING", activity_level: 5, pending_approval_count: 1 }),
    connection: envelope({ quality: "degraded", online_count: 1, total_count: 2, attention_count: 1 }),
    display_scene: envelope({ phase: "Executing", takeover: { active: false }, privacy_mode: false, offline: false, stale: false }),
    presentations: envelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
    presentation_events: envelope({
      items: [
        {
          event_id: "presentation-event-1",
          scene_type: "approval",
          priority: "P1",
          severity: "warning",
          source: "approval_manager",
          title: "shared approval",
          summary: "Approval can be opened on Web or mobile.",
          affected_entities: ["approval-1"],
          approval_id: "approval-1",
          persistence: "until_resolved",
          expires_at: 2000,
          privacy_class: "sensitive",
          recommended_surfaces: ["web_dashboard", "mobile_app", "android_notification", "dedicated_display"],
          visual_hint: { effect: "containment", arc: "pc-server" },
          available_actions: [{ id: "open_approval", surface: "web_dashboard", target_id: "approval-1" }]
        }
      ],
      count: 1,
      source: "presentation_surface_contract"
    }),
    surface_roles: envelope({
      items: [
        {
          surface_id: "dedicated_display",
          role: "Read-only state display",
          interactive: false,
          privacy_levels: ["public", "normal"],
          priorities: ["P0", "P1", "P2", "P3"],
          max_text_chars: 420,
          max_display_ms: 0,
          actions: [],
          scenes: ["idle", "approval", "critical"]
        }
      ],
      count: 1,
      source: "presentation_surface_contract"
    }),
    tasks: envelope({
      primary: {
        task_id: "task-1",
        title: "Inspect desktop",
        phase: "running",
        current_action: "Capture screen",
        next_action: "Verify output",
        blocked_reason: "",
        capability_id: "pc-server.screenshot.get_screenshot",
        steps: [],
      },
      active: [{ task_id: "task-1", title: "Inspect desktop", status: "running" }],
      waiting: [],
      scheduled: [{ task_id: "task-2", title: "Later task", status: "scheduled" }],
      recent: [],
    }),
    attention: envelope({ items: [{ id: "attention-1", kind: "server", severity: "warning", title: "Connection dropped", message: "PC server needs attention" }], count: 1 }),
    current_task: envelope({
      task_id: "task-1",
      title: "Inspect desktop",
      phase: "running",
      current_action: "Capture screen",
      next_action: "Verify output",
      blocked_reason: "",
      capability_id: "pc-server.screenshot.get_screenshot",
      conversation_id: "conversation-1",
      steps: [
        {
          step_id: "step-1",
          status: "completed",
          capability_id: "pc-server.screenshot.get_screenshot",
          result: { status: "ok" }
        }
      ]
    }),
    servers: envelope({
      items: [
        { server_id: "ai-server", status: "ONLINE", mode: "grpc", registered_capabilities: "Core" },
        { server_id: "android-server", status: "ONLINE", mode: "reverse_stream", registered_capabilities: "17", dependencies: { device_model: "21121210G", capability_availability: { "android-server.device.get_status": { available: true } } } }
      ]
    }),
    capabilities: envelope({ count: 18, by_server: { "android-server": 17 }, items: [{ capability_id: "android-server.device.get_status" }] }),
    user_situation: envelope({ summary: "User is available", available: true }),
    user_state: envelope({ summary: "User is available", available: true }),
    mind_summary: envelope({ memory: { advanced: { entities: 2, facts: 3 }, episodic: { total_episodes: 4 }, semantic: { total_entries: 5 }, last_consolidation: "recent" }, autonomy: { desires: { growth: 4, social: 2 } } }),
    mind: envelope({ dominant_desire: "growth" }),
    memory: envelope({ summary: { episodic: 4, semantic: 5, procedural: 1, last_consolidation: "recent" } }),
    notifications: envelope({ recent: [{ notification_id: "notification-1", title: "Connection dropped", message: "PC server needs attention" }], unread_count: 1 }),
    approvals: envelope({ pending: [{ approval_id: "approval-1", capability_id: "pc-server.keyboard.type_text", summary: "Type into safe field", risk: "high", reason: "Writes to desktop", task_id: "task-1" }], pending_count: 1 }),
    commitments: envelope({ items: [{ title: "Review UI" }], summary: "1 commitment" }),
    usage: envelope({ summary: "Audit-backed" }),
    errors: envelope({ items: [{ message: "Connection dropped", severity: "warning" }], count: 1 }),
    activity: envelope({
      source: "audit_manager+event_manager",
      count: 1,
      operations: [
        {
          operation_id: "req-chat-1",
          kind: "chat",
          kind_label: "User instruction",
          title: "Inspect desktop",
          summary: "Captured a screenshot of the desktop.",
          what_happened: "Captured a screenshot of the desktop.",
          narrative: "Captured a screenshot of the desktop.",
          status: "success",
          started_at: 1000,
          updated_at: 2000,
          tool_count: 1,
          error_count: 0,
          priority: "P2",
          causal_chain: [
            { stage: "trigger", label: "Trigger", summary: "User instruction", status: "present" },
            { stage: "decision_context", label: "Decision Context", summary: "AgentState", status: "present" },
            { stage: "candidates_and_non_action", label: "Candidates And Non Action", summary: "Tool steps selected", status: "present" },
            { stage: "goal", label: "Goal", summary: "Inspect desktop", status: "present" },
            { stage: "execution", label: "Execution", summary: "1 succeeded", status: "present" },
            { stage: "result", label: "Result", summary: "Captured a screenshot of the desktop.", status: "present" },
            { stage: "verification", label: "Verification", summary: "Execution completed", status: "present" },
            { stage: "presentation", label: "Presentation", summary: "Reported", status: "present" },
            { stage: "follow_up", label: "Follow Up", summary: "", status: "missing" },
            { stage: "learning", label: "Learning", summary: "", status: "missing" },
          ],
          steps: [
            {
              action: "tool_execution",
              capability_id: "pc-server.screenshot.get_screenshot",
              summary: "Captured a screenshot of the desktop.",
              narrative: "Captured a screenshot of the desktop.",
              status: "ok",
            },
          ],
        },
      ],
      groups: [
        {
          group_id: "task:task-1",
          title: "Task task-1",
          summary: "Capture screen",
          status: "running",
          operation_type: "capability",
          events: [{ title: "Capture screen" }],
        },
      ],
      recent: [],
    }),
    freshness: envelope({}),
    open_loops: envelope({
      items: [
        {
          id: "loop-1",
          kind: "commitment",
          title: "Follow up on review",
          owner: "User",
          next_action: "Approve or reject",
          waiting_reason: "Waiting for user",
          success_condition: "Review complete",
          status: "open",
          confidence: 0.8,
          evidence_summary: "Linked conversation",
        },
      ],
      count: 1,
      by_kind: { commitment: 1 },
      summary: "1 open",
    }),
    initiative: envelope({
      funnel: { triggers_observed: 3, actions_executed: 1 },
      no_action_reasons: { "budget gate": 2 },
      recent_non_actions: [{ decision: "no_action", reason: "budget gate", created_at: 1000 }],
      summary: "Triggers 3; executed 1; top non-action: budget gate",
    }),
    goals: envelope({
      open: [{ title: "Ship UI", success_condition: "Dashboard usable", unmet_conditions: [{ summary: "Verification pending" }], status: "running" }],
      open_count: 1,
      summary: "1 open goal(s)",
    }),
    social: envelope({
      pending_decisions: [{ item_id: "agora-1", channel: "agora", body: "hello from agora", status: "pending" }],
      decided: [],
      agora: { pending_count: 1, counts: { pending: 1 } },
      summary: "1 social item(s) awaiting decision",
    }),
    repairs: envelope({ items: [{ category: "llm", summary: "Provider recovered", lesson: "Retry later" }], count: 1 }),
    behavioral_reports: envelope({ metrics: { restraint: 0.8, goal_achievement: 0.5 }, summary: "Restraint 80%" }),
    decision_context: envelope({ summary: "User available; one obligation open", obligations: [{ kind: "commitment", summary: "Review UI" }] }),
    executions: envelope({ operations: [], count: 0, summary: "0 recent operation(s)" }),
    generated_capabilities: envelope({ items: [], count: 0, summary: "0 generated capability(ies)" }),
  };
}

function event() {
  return {
    event_id: "event-1",
    type: "connection.changed",
    source_type: "status.changed",
    generated_at: 1000,
    source_updated_at: 1000,
    payload: {},
    server_id: "pc-server",
    severity: "warning",
    message: "Connection dropped",
  };
}
