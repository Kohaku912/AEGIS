import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { ActivityPage } from "./ActivityPage";
import { Approvals } from "./Approvals";
import { CommandCenter } from "./CommandCenter";
import { MindMemory } from "./MindMemory";
import { Settings } from "./Settings";
import { Systems } from "./Systems";
import { Work } from "./Work";
import type { UiOverview } from "../types";

vi.mock("../components/CoreSphere", () => ({
  CoreSphere: () => <div data-testid="core-sphere-mock" />,
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
    render(<MindMemory overview={overview()} />);
    expect(screen.getByText("Mind & Memory")).toBeInTheDocument();
    expect(screen.getByText("Active goal")).toBeInTheDocument();
    const developer = screen.getByText("Developer raw state").closest("details");
    expect(developer).not.toBeNull();
    expect(within(developer as HTMLElement).getByText(/"advanced"/)).toBeInTheDocument();
  });

  it("renders Work queues and task detail", () => {
    render(<Work overview={overview()} />);
    expect(screen.getByRole("tablist", { name: "Work queues" })).toBeInTheDocument();
    expect(screen.getByText("Task Detail")).toBeInTheDocument();
    expect(screen.getAllByText("pc-server.screenshot.get_screenshot").length).toBeGreaterThan(0);
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
    expect(screen.getAllByText("Connection dropped").length).toBeGreaterThan(0);
    expect(screen.getByText("Audit-backed")).toBeInTheDocument();
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

    const mind = render(<MindMemory overview={data} />);
    expect(screen.getByText("User is available")).toBeInTheDocument();
    expect(screen.getByText("1 commitment")).toBeInTheDocument();
    expect(screen.getByText("Review UI")).toBeInTheDocument();
    mind.unmount();

    render(<ActivityPage overview={data} recentEvents={[event()]} />);
    expect(screen.getByText("connection.changed")).toBeInTheDocument();
    expect(screen.getAllByText("Connection dropped").length).toBeGreaterThan(0);
  });
});

function envelope<T>(data: T) {
  return { generated_at: 1000, source_updated_at: 1000, status: "ok" as const, stale: false, error: "", data };
}

function overview(): UiOverview {
  return {
    schema_version: "ui-overview.v3",
    generated_at: 1000,
    core: envelope({ active_goal: "Ship UI", confidence: "high", health: "ONLINE", mode: "EXECUTING", activity_level: 5, pending_approval_count: 1 }),
    connection: envelope({ quality: "degraded", online_count: 1, total_count: 2, attention_count: 1 }),
    display_scene: envelope({ phase: "Executing", takeover: { active: false }, privacy_mode: false, offline: false, stale: false }),
    presentations: envelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
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
    freshness: envelope({})
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
