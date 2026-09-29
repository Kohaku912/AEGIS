/**
 * Phase D7 DoD tests — AgentTimelinePage
 * (DASHBOARD_REFINED_PLAN.md §3 Phase D7 / instruction.md §17, §18).
 *
 * DoD チェックリスト:
 * - [x] Agent session 0 件で empty メッセージ表示
 * - [x] 各 session が行として表示され、status 別色クラスが付く
 * - [x] 検索 (filter) で agent_session_id / task_id / summary 部分一致フィルタ
 * - [x] 行クリックで onNavigate が `/dashboard/agent-sessions/<id>` で呼ばれる
 * - [x] Refresh ボタンで refetch が走る
 * - [x] running / completed / failed の集計が表示される
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AgentTimelinePage } from "./AgentTimelinePage";
import { fetchAgentSessions, type AgentSessionSummary } from "../api/client";

vi.mock("../api/client", () => ({
  fetchAgentSessions: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchAgentSessions);

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
}

function makeWrapper() {
  const queryClient = makeQueryClient();
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

function renderPage(onNavigate = vi.fn()) {
  return { onNavigate, ...render(<AgentTimelinePage onNavigate={onNavigate} />, { wrapper: makeWrapper() }) };
}

function makeSession(over: Partial<AgentSessionSummary> = {}): AgentSessionSummary {
  return {
    agent_session_id: "sess-1",
    task_id: "task-1",
    first_event_ms: 1700000000000,
    last_event_ms: 1700000005000,
    event_count: 3,
    kinds: ["agent.started", "agent.thinking", "agent.completed"],
    status: "completed",
    summary: "Demo",
    policy_allow_count: 0,
    policy_ask_count: 0,
    policy_deny_count: 0,
    highest_risk: "",
    approval_count: 0,
    pending_approval: false,
    causal_summary: "",
    root_cause: null,
    milestones: [],
    ...over,
  };
}

const multiSessions: AgentSessionSummary[] = [
  makeSession({
    agent_session_id: "sess-running-1",
    task_id: "task-7",
    status: "running",
    first_event_ms: 1700000002000,
    last_event_ms: 0,
    event_count: 2,
    summary: "executing tools",
    approval_count: 1,
    pending_approval: true,
    highest_risk: "HIGH_RISK",
    policy_ask_count: 1,
    causal_summary: "Current blocker: approval.created - Waiting for approval.",
    milestones: [
      {
        key: "ms-1",
        kind: "agent.started",
        label: "start",
        variant: "start",
        timestamp_ms: 1700000002000,
        trace_id: "trace-1",
        parent_id: "",
        activity_id: "",
      },
      {
        key: "ms-2",
        kind: "approval.created",
        label: "approval requested",
        variant: "approval",
        timestamp_ms: 1700000002600,
        trace_id: "trace-1",
        parent_id: "",
        activity_id: "",
      },
    ],
  }),
  makeSession({
    agent_session_id: "sess-done-1",
    task_id: "task-3",
    status: "completed",
    first_event_ms: 1700000000000,
    last_event_ms: 1700000010000,
    event_count: 5,
    summary: "finished work",
  }),
  makeSession({
    agent_session_id: "sess-fail-1",
    task_id: "task-9",
    status: "failed",
    first_event_ms: 1700000005000,
    last_event_ms: 1700000007000,
    event_count: 4,
    summary: "tool error",
  }),
];

describe("AgentTimelinePage (D7)", () => {
  beforeEach(() => {
    mockedFetch.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows empty message when no sessions", async () => {
    mockedFetch.mockResolvedValue({ sessions: [], count: 0, generated_at: 0 });
    renderPage();
    expect(await screen.findByText("表示可能な session はありません。")).toBeInTheDocument();
  });

  it("renders one row per session with status class and counts", async () => {
    mockedFetch.mockResolvedValue({ sessions: multiSessions, count: multiSessions.length, generated_at: 0 });
    renderPage();
    // 3 行のレンダリングを待つ
    await screen.findByTestId("agent-timeline-row-sess-running-1");
    expect(screen.getByTestId("agent-timeline-row-sess-done-1")).toBeInTheDocument();
    expect(screen.getByTestId("agent-timeline-row-sess-fail-1")).toBeInTheDocument();
    // status 別クラス
    const failBar = screen.getByTestId("agent-timeline-row-sess-fail-1").querySelector(".agent-timeline__bar");
    expect(failBar?.className).toContain("agent-timeline__bar--failed");
    const doneBar = screen.getByTestId("agent-timeline-row-sess-done-1").querySelector(".agent-timeline__bar");
    expect(doneBar?.className).toContain("agent-timeline__bar--completed");
    const runningBar = screen.getByTestId("agent-timeline-row-sess-running-1").querySelector(".agent-timeline__bar");
    expect(runningBar?.className).toContain("agent-timeline__bar--running");
    // 集計
    expect(screen.getByText(/running=1/)).toBeInTheDocument();
    expect(screen.getByText(/completed=1/)).toBeInTheDocument();
    expect(screen.getByText(/failed=1/)).toBeInTheDocument();
    expect(screen.getByText(/Current blocker: approval\.created/)).toBeInTheDocument();
    expect(screen.getAllByTitle(/approval requested/).length).toBeGreaterThan(0);
  });

  it("filters rows by agent_session_id, task_id, and summary (substring match)", async () => {
    mockedFetch.mockResolvedValue({ sessions: multiSessions, count: multiSessions.length, generated_at: 0 });
    renderPage();
    await screen.findByTestId("agent-timeline-row-sess-running-1");
    const input = screen.getByLabelText("Agent session 検索") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "task-3" } });
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-done-1")).toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-running-1")).not.toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-fail-1")).not.toBeInTheDocument();
    });
    // サマリ部分一致
    fireEvent.change(input, { target: { value: "tool error" } });
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-fail-1")).toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-done-1")).not.toBeInTheDocument();
    });
    // 部分一致クリアで全件復帰
    fireEvent.change(input, { target: { value: "" } });
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-done-1")).toBeInTheDocument();
      expect(screen.getByTestId("agent-timeline-row-sess-fail-1")).toBeInTheDocument();
      expect(screen.getByTestId("agent-timeline-row-sess-running-1")).toBeInTheDocument();
    });
  });

  it("filters rows by preset chips", async () => {
    mockedFetch.mockResolvedValue({ sessions: multiSessions, count: multiSessions.length, generated_at: 0 });
    renderPage();
    await screen.findByTestId("agent-timeline-row-sess-running-1");

    fireEvent.click(screen.getByRole("button", { name: "Pending approval" }));
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-running-1")).toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-done-1")).not.toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-fail-1")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "Failed" }));
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-fail-1")).toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-running-1")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "High risk" }));
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-running-1")).toBeInTheDocument();
      expect(screen.queryByTestId("agent-timeline-row-sess-done-1")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "All" }));
    await waitFor(() => {
      expect(screen.getByTestId("agent-timeline-row-sess-running-1")).toBeInTheDocument();
      expect(screen.getByTestId("agent-timeline-row-sess-done-1")).toBeInTheDocument();
      expect(screen.getByTestId("agent-timeline-row-sess-fail-1")).toBeInTheDocument();
    });
  });

  it("clicking a row navigates to agent-session detail", async () => {
    mockedFetch.mockResolvedValue({ sessions: multiSessions, count: multiSessions.length, generated_at: 0 });
    const onNavigate = vi.fn();
    renderPage(onNavigate);
    const row = await screen.findByTestId("agent-timeline-row-sess-done-1");
    const link = row.querySelector("button.link-button") as HTMLButtonElement;
    fireEvent.click(link);
    expect(onNavigate).toHaveBeenCalledWith("/dashboard/agent-sessions/sess-done-1");
  });

  it("Refresh button triggers a refetch", async () => {
    mockedFetch.mockResolvedValue({ sessions: multiSessions, count: multiSessions.length, generated_at: 0 });
    renderPage();
    await screen.findByTestId("agent-timeline-row-sess-done-1");
    const beforeCalls = mockedFetch.mock.calls.length;
    fireEvent.click(screen.getByRole("button", { name: "Refresh" }));
    await waitFor(() => {
      expect(mockedFetch.mock.calls.length).toBeGreaterThan(beforeCalls);
    });
  });
});
