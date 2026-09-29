/**
 * Phase D4 + D5 + D6 DoD tests — AgentSessionPage (DASHBOARD_REFINED_PLAN.md §3 Phase D4 / D5 / D6).
 *
 * DoD チェックリスト:
 * - [x] agent_sessionId 空 / 404 時に Not Found 表示
 * - [x] 10 tabs (Overview / Chain / Thinking / Tools / MCP / Files / Terminal / Approvals / Errors / Raw) が表示される
 * - [x] Overview tab に summary 情報 (agent_session_id / task_id / status / event_count) が表示
 * - [x] Thinking tab は `agent.thinking` イベントだけ表示
 * - [x] Tools tab は `agent.tool.*` / `tool.execution.*` イベントを表示
 * - [x] MCP tab は `mcp.*` tool だけ表示
 * - [x] Files tab は `file.*` tool だけ表示
 * - [x] Terminal tab は `terminal.*` tool だけ表示
 * - [x] Approvals tab は `approval.*` / `agent.waiting` イベントを表示
 * - [x] Errors tab は `agent.failed` / `tool.execution.failed` だけ表示
 * - [x] Raw tab は全 event を JSON 折りたたみで表示
 * - [x] Phase D5: Policy / Approval 集計が Overview に表示、MCP / Approvals に policy.decision 表示
 * - [x] Phase D6: Tool call の args / output を `<ToolCallJson>` で完全 JSON 表示
 * - [x] Phase D6: 1000 文字超の output は `[Show all]` ボタンで展開
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AgentSessionPage } from "./AgentSessionPage";
import type { UiEvent } from "../types";

vi.mock("../api/client", () => ({
  fetchAgentSession: vi.fn(),
  fetchAgentSessionEvents: vi.fn(),
}));

import { fetchAgentSession } from "../api/client";

const mockedFetch = vi.mocked(fetchAgentSession);

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
}

function renderPage(agentSessionId: string, recentEvents: UiEvent[] = []) {
  const queryClient = makeQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <AgentSessionPage agentSessionId={agentSessionId} recentEvents={recentEvents} onNavigate={() => undefined} />
    </QueryClientProvider>
  );
}

const baseSummary = {
  agent_session_id: "sess-1",
  task_id: "task-7",
  first_event_ms: 1700000000000,
  last_event_ms: 1700000005000,
  event_count: 5,
  kinds: ["agent.started", "agent.thinking", "agent.tool.started", "agent.tool.completed", "agent.completed"],
  status: "completed" as const,
  summary: "Done",
  policy_allow_count: 0,
  policy_ask_count: 0,
  policy_deny_count: 0,
  highest_risk: "",
  approval_count: 0,
  pending_approval: false,
  causal_summary: "",
  root_cause: null,
  milestones: [],
};

const baseEvents = [
  {
    type: "agent.started",
    event_id: "e1",
    timestamp: 1700000000000,
    payload: { event_id: "e1", task_id: "task-7", agent_session_id: "sess-1", state: "started", occurred_at_ms: 1700000000000 },
  },
  {
    type: "agent.thinking",
    event_id: "e2",
    timestamp: 1700000001000,
    payload: { event_id: "e2", task_id: "task-7", agent_session_id: "sess-1", state: "thinking", text: "Let me think about this.", occurred_at_ms: 1700000001000 },
  },
  {
    type: "agent.tool.started",
    event_id: "e3",
    timestamp: 1700000002000,
    payload: { event_id: "e3", task_id: "task-7", agent_session_id: "sess-1", state: "tool_started", tool: "mcp.github.create_issue", occurred_at_ms: 1700000002000 },
  },
  {
    type: "agent.tool.completed",
    event_id: "e4",
    timestamp: 1700000003000,
    payload: { event_id: "e4", task_id: "task-7", agent_session_id: "sess-1", state: "tool_completed", tool: "mcp.github.create_issue", ok: true, occurred_at_ms: 1700000003000 },
  },
  {
    type: "agent.tool.started",
    event_id: "e5",
    timestamp: 1700000004000,
    payload: { event_id: "e5", task_id: "task-7", agent_session_id: "sess-1", state: "tool_started", tool: "file.write", occurred_at_ms: 1700000004000 },
  },
  {
    type: "agent.completed",
    event_id: "e6",
    timestamp: 1700000005000,
    payload: { event_id: "e6", task_id: "task-7", agent_session_id: "sess-1", state: "completed", summary: "All done", occurred_at_ms: 1700000005000 },
  },
];

beforeEach(() => {
  mockedFetch.mockReset();
});

afterEach(() => {
  cleanup();
});

describe("AgentSessionPage", () => {
  it("shows Not Found when API returns 404", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-missing",
      found: false,
      summary: { ...baseSummary, agent_session_id: "sess-missing", event_count: 0, kinds: [] },
      events: [],
    });
    renderPage("sess-missing");
    expect(await screen.findByText(/Not Found/)).toBeTruthy();
  });

  it("renders 9 tabs when session is found", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    for (const label of ["Overview", "Chain", "Thinking", "Tools", "MCP", "Files", "Terminal", "Approvals", "Errors", "Raw"]) {
      expect(await screen.findByRole("button", { name: label })).toBeTruthy();
    }
  });

  it("Overview tab shows summary fields", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    const overview = await screen.findByText("サマリ");
    const overviewSection = overview.closest("section");
    expect(overviewSection).toBeTruthy();
    const scope = within(overviewSection!);
    expect(scope.getByText(/sess-1/)).toBeTruthy();
    expect(scope.getByText("completed")).toBeTruthy();
    expect(scope.getByText("5")).toBeTruthy();
  });

  it("Thinking tab filters agent.thinking only", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    const thinkingTab = await screen.findByRole("button", { name: "Thinking" });
    thinkingTab.click();
    expect(await screen.findByText(/Let me think about this/)).toBeTruthy();
  });

  it("MCP tab filters tool prefix 'mcp.'", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    const mcpTab = await screen.findByRole("button", { name: "MCP" });
    mcpTab.click();
    // started + completed の 2 イベントが期待される
    const matches = await screen.findAllByText(/mcp\.github\.create_issue/);
    expect(matches.length).toBeGreaterThanOrEqual(2);
  });

  it("Files tab filters tool prefix 'file.'", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    const filesTab = await screen.findByRole("button", { name: "Files" });
    filesTab.click();
    expect(await screen.findByText(/file\.write/)).toBeTruthy();
  });

  it("Errors tab shows agent.failed events", async () => {
    const events = [
      ...baseEvents,
      {
        type: "agent.failed",
        event_id: "e7",
        timestamp: 1700000006000,
        payload: {
          event_id: "e7",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "failed",
          error: "boom",
          occurred_at_ms: 1700000006000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, status: "failed" as const, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const errorsTab = await screen.findByRole("button", { name: "Errors" });
    errorsTab.click();
    expect(await screen.findByText(/boom/)).toBeTruthy();
  });

  it("Approvals tab shows approval.created events", async () => {
    const events = [
      ...baseEvents,
      {
        type: "approval.created",
        event_id: "e8",
        timestamp: 1700000007000,
        payload: {
          event_id: "e8",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "approval",
          approval_id: "apr-1",
          occurred_at_ms: 1700000007000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const approvalsTab = await screen.findByRole("button", { name: "Approvals" });
    approvalsTab.click();
    expect(await screen.findByText(/apr-1/)).toBeTruthy();
  });

  it("Raw tab shows all events as collapsible details", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    renderPage("sess-1");
    const rawTab = await screen.findByRole("button", { name: "Raw" });
    rawTab.click();
    expect(await screen.findByText(/Raw events \(/)).toBeTruthy();
  });

  it("filters live SSE events by agent_session_id in Overview", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents,
    });
    const liveEvents: UiEvent[] = [
      {
        type: "agent.thinking",
        event_id: "live-1",
        generated_at: 1700000010000,
        source_updated_at: 1700000010000,
        severity: "info",
        source_type: "agent.thinking",
        payload: { _trace_ids: { agent_session_id: "sess-1", trace_id: "trace-live" }, text: "live thought" },
        agent_session_id: "sess-1",
      } as unknown as UiEvent,
      {
        type: "agent.thinking",
        event_id: "live-2",
        generated_at: 1700000011000,
        source_updated_at: 1700000011000,
        severity: "info",
        source_type: "agent.thinking",
        payload: { agent_session_id: "OTHER", text: "should not appear" },
        agent_session_id: "OTHER",
      } as unknown as UiEvent,
    ];
    renderPage("sess-1", liveEvents);
    const liveSection = await screen.findByText("Live (SSE 受信中)");
    const scope = within(liveSection.closest("section")!);
    expect(scope.getByText(/live thought/)).toBeTruthy();
    expect(scope.queryByText(/should not appear/)).toBeNull();
  });

  it("Chain tab renders parent-linked causal sequence", async () => {
    const events = [
      {
        type: "agent.started",
        event_id: "root-1",
        timestamp: 1700000000000,
        payload: { event_id: "root-1", agent_session_id: "sess-1", occurred_at_ms: 1700000000000, summary: "Root event", _trace_ids: { agent_session_id: "sess-1", trace_id: "trace-1" } },
      },
      {
        type: "agent.waiting",
        event_id: "child-1",
        timestamp: 1700000001000,
        payload: { event_id: "child-1", agent_session_id: "sess-1", occurred_at_ms: 1700000001000, reason: "Waiting for approval", _trace_ids: { agent_session_id: "sess-1", trace_id: "trace-1", parent_id: "root-1" } },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    fireEvent.click(await screen.findByRole("button", { name: "Chain" }));
    expect(await screen.findByText(/Trace \/ Parent Chain/)).toBeTruthy();
    expect(screen.getAllByText(/trace-1/).length).toBeGreaterThan(0);
    expect(screen.getByText(/root-1/)).toBeTruthy();
    expect(screen.getByText(/Waiting for approval/)).toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // Phase D5 — Policy / Approval 表示統合
  // ---------------------------------------------------------------------------

  it("Overview tab shows Policy / Approval summary section (D5)", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, policy_allow_count: 3, policy_ask_count: 1, policy_deny_count: 0, highest_risk: "HIGH_RISK", approval_count: 2, pending_approval: true },
      events: baseEvents,
    });
    renderPage("sess-1");
    const header = await screen.findByText("Policy / Approval");
    const section = header.closest("section");
    expect(section).toBeTruthy();
    const scope = within(section!);
    // approval count は 2 にして policy_ask_count=1 と区別する
    expect(scope.getByText("3")).toBeTruthy(); // allow
    expect(scope.getByText("2")).toBeTruthy(); // approval count (unique)
    expect(scope.getByText("YES")).toBeTruthy(); // pending
    expect(scope.getByText(/HIGH_RISK/)).toBeTruthy();
  });

  it("Overview tab prefers backend causal summary and milestones", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: {
        ...baseSummary,
        causal_summary: "Current blocker: approval.created - Waiting for human confirmation.",
        root_cause: {
          kind: "approval.created",
          summary: "Waiting for human confirmation.",
          timestamp_ms: 1700000002500,
          trace_id: "trace-approval",
          parent_id: "",
          activity_id: "",
          category: "approval_pending",
          confidence: 0.82,
        },
        milestones: [
          {
            key: "m1",
            kind: "agent.started",
            label: "start",
            variant: "start",
            timestamp_ms: 1700000000000,
            trace_id: "trace-approval",
            parent_id: "",
            activity_id: "",
          },
          {
            key: "m2",
            kind: "approval.created",
            label: "approval requested",
            variant: "approval",
            timestamp_ms: 1700000002500,
            trace_id: "trace-approval",
            parent_id: "",
            activity_id: "",
          },
        ],
      },
      events: baseEvents,
      causal_chain: [],
    });
    renderPage("sess-1");
    expect(await screen.findByText(/Current blocker: approval\.created/)).toBeTruthy();
    expect(screen.getByText("approval_pending")).toBeTruthy();
    expect(screen.getByText(/approval requested/)).toBeTruthy();
  });

  it("MCP tab shows policy.decision with decision/risk/capability (D5)", async () => {
    const events = [
      ...baseEvents,
      {
        type: "policy.decision",
        event_id: "pol-1",
        timestamp: 1700000002500,
        payload: {
          event_id: "pol-1",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "policy",
          decision: "ASK_APPROVAL",
          risk_level: "HIGH_RISK",
          capability_id: "mcp.slack.post_message",
          reason: "Risk level HIGH_RISK — approval required.",
          occurred_at_ms: 1700000002500,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length, policy_ask_count: 1, highest_risk: "HIGH_RISK" },
      events,
    });
    renderPage("sess-1");
    const mcpTab = await screen.findByRole("button", { name: "MCP" });
    mcpTab.click();
    // ASK_APPROVAL テキストと capability_id (baseEvents の mcp.github.create_issue とは別物)
    expect(await screen.findByText(/ASK_APPROVAL/)).toBeTruthy();
    expect(await screen.findByText(/mcp\.slack\.post_message/)).toBeTruthy();
  });

  it("Approvals tab shows policy.decision with risk level (D5)", async () => {
    const events = [
      ...baseEvents,
      {
        type: "approval.created",
        event_id: "apr-1",
        timestamp: 1700000002500,
        payload: {
          event_id: "apr-1",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "approval",
          approval_id: "apr-id-1",
          occurred_at_ms: 1700000002500,
        },
      },
      {
        type: "policy.decision",
        event_id: "pol-2",
        timestamp: 1700000002600,
        payload: {
          event_id: "pol-2",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "policy",
          decision: "DENY",
          risk_level: "FORBIDDEN",
          capability_id: "mcp.github.delete_repo",
          occurred_at_ms: 1700000002600,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length, policy_deny_count: 1, highest_risk: "FORBIDDEN", approval_count: 1, pending_approval: false },
      events,
    });
    renderPage("sess-1");
    const approvalsTab = await screen.findByRole("button", { name: "Approvals" });
    approvalsTab.click();
    expect(await screen.findByText(/apr-id-1/)).toBeTruthy();
    expect(await screen.findByText(/FORBIDDEN/)).toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // Phase D6 — MCP / Tool call 完全 JSON 表示 (instruction.md §7, §8)
  // ---------------------------------------------------------------------------

  it("Tools tab shows agent.tool.started args in ToolCallJson (D6)", async () => {
    const events = [
      ...baseEvents,
      {
        type: "agent.tool.started",
        event_id: "e-tools-1",
        timestamp: 1700000008000,
        payload: {
          event_id: "e-tools-1",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "tool_started",
          tool: "mcp.github.create_issue",
          args: { title: "Bug report", body: "Steps to reproduce...", labels: ["bug", "p0"] },
          occurred_at_ms: 1700000008000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const toolsTab = await screen.findByRole("button", { name: "Tools" });
    toolsTab.click();
    // ToolCallJson の label "args" が表示され、整形 JSON が <pre> 内に展開される
    expect(await screen.findByText("args")).toBeTruthy();
    expect(await screen.findByText(/"title": "Bug report"/)).toBeTruthy();
    expect(await screen.findByText(/"labels":/)).toBeTruthy();
  });

  it("Tools tab shows agent.tool.completed output in ToolCallJson (D6)", async () => {
    const events = [
      ...baseEvents,
      {
        type: "agent.tool.completed",
        event_id: "e-tools-2",
        timestamp: 1700000009000,
        payload: {
          event_id: "e-tools-2",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "tool_completed",
          tool: "mcp.github.create_issue",
          ok: true,
          output: { url: "https://github.com/foo/bar/issues/42", number: 42 },
          duration_ms: 1234,
          _trace_ids: { agent_session_id: "sess-1", trace_id: "trace-42", parent_id: "parent-41", activity_id: "act-9" },
          occurred_at_ms: 1700000009000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const toolsTab = await screen.findByRole("button", { name: "Tools" });
    toolsTab.click();
    // ToolCallJson の label "output" が表示され、整形 JSON が <pre> 内に展開される
    expect(await screen.findByText("output")).toBeTruthy();
    expect(await screen.findByText(/"url": "https:\/\/github.com\/foo\/bar\/issues\/42"/)).toBeTruthy();
    expect(await screen.findByText(/"number": 42/)).toBeTruthy();
    // duration_ms も強調表示される
    expect(await screen.findByText(/1234/)).toBeTruthy();
    expect(await screen.findByText(/trace-42/)).toBeTruthy();
    expect(await screen.findByText(/parent-41/)).toBeTruthy();
  });

  // ---------------------------------------------------------------------------
  // Phase D9 — Token / Cost (instruction.md §25)
  // ---------------------------------------------------------------------------

  it("Overview tab shows Token / Cost panel when payload.token_usage is present (D9)", async () => {
    const events = [
      ...baseEvents,
      {
        type: "agent.completed",
        event_id: "e-tok-1",
        timestamp: 1700000020000,
        payload: {
          event_id: "e-tok-1",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "completed",
          token_usage: {
            model: "deepseek-chat",
            input_tokens: 1234,
            output_tokens: 567,
            cached_tokens: 100,
            cost: 0.0023,
          },
          occurred_at_ms: 1700000020000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const panel = await screen.findByTestId("token-cost-panel");
    expect(panel).toBeTruthy();
    expect(within(panel).getByTestId("token-input").textContent).toBe("1,234");
    expect(within(panel).getByTestId("token-output").textContent).toBe("567");
    expect(within(panel).getByTestId("token-cached").textContent).toBe("100");
    expect(within(panel).getByTestId("token-cost").textContent).toBe("$0.0023");
    expect(within(panel).getByText(/deepseek-chat/)).toBeTruthy();
  });

  it("Overview tab reads scalar token fields from payload directly (D9)", async () => {
    const events = [
      {
        type: "llm.token",
        event_id: "e-tok-2",
        timestamp: 1700000021000,
        payload: {
          event_id: "e-tok-2",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "llm",
          model: "gpt-4o-mini",
          input_tokens: 5000,
          output_tokens: 1000,
          cached_tokens: 200,
          cost: 0.011,
          occurred_at_ms: 1700000021000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const panel = await screen.findByTestId("token-cost-panel");
    expect(within(panel).getByTestId("token-input").textContent).toBe("5,000");
    expect(within(panel).getByTestId("token-output").textContent).toBe("1,000");
    expect(within(panel).getByTestId("token-cached").textContent).toBe("200");
    expect(within(panel).getByTestId("token-cost").textContent).toBe("$0.0110");
  });

  it("Overview tab shows empty state when no token info events exist (D9)", async () => {
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: baseSummary,
      events: baseEvents, // すべて token_info なし
    });
    renderPage("sess-1");
    const panel = await screen.findByTestId("token-cost-panel");
    expect(within(panel).getByText(/token \/ cost 情報を含む event がありません/)).toBeTruthy();
  });

  it("ToolCallJson collapses long output and expands on click (D6)", async () => {
    const longOutput = "x".repeat(1500);
    const events = [
      ...baseEvents,
      {
        type: "agent.tool.completed",
        event_id: "e-tools-3",
        timestamp: 1700000010000,
        payload: {
          event_id: "e-tools-3",
          task_id: "task-7",
          agent_session_id: "sess-1",
          state: "tool_completed",
          tool: "file.read",
          ok: true,
          output: longOutput,
          occurred_at_ms: 1700000010000,
        },
      },
    ];
    mockedFetch.mockResolvedValue({
      generated_at: 0,
      agent_session_id: "sess-1",
      found: true,
      summary: { ...baseSummary, event_count: events.length },
      events,
    });
    renderPage("sess-1");
    const toolsTab = await screen.findByRole("button", { name: "Tools" });
    toolsTab.click();
    // Show all ボタンが表示される (1500 chars)
    const toggle = await screen.findByTestId("tool-call-json-toggle-output");
    expect(toggle.textContent || "").toMatch(/Show all/);
    // 展開前は truncated マーカーが含まれる
    expect(await screen.findByText(/truncated, 500 more chars/)).toBeTruthy();
    // クリックして展開 (fireEvent 経由で React の act() 内で state 更新)
    fireEvent.click(toggle);
    // state 更新後の再レンダリングを待つ
    await waitFor(() => {
      const toggleExpanded = screen.getByTestId("tool-call-json-toggle-output");
      expect(toggleExpanded.textContent || "").toMatch(/Show less/);
    });
  });
});
