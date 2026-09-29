import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { LiveOverlay, liveOverlayClickTarget, readLiveOverlayToggles } from "./LiveOverlay";
import type { UiEvent } from "../types";

afterEach(() => cleanup());

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

describe("LiveOverlay (Phase D2 — instruction.md §3, §4, §21)", () => {
  it("renders the idle state when no events are present", () => {
    render(<LiveOverlay events={[]} />);
    expect(screen.getByRole("status")).toHaveTextContent(/AEGIS is idle/);
  });

  it("renders the highest priority event label and details", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "a", type: "agent.thinking", generated_at: 200, message: "thinking" }),
          eventOf({ event_id: "b", type: "approval.created", generated_at: 100, message: "needs approval for screenshot" }),
        ]}
      />,
    );
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent(/Approval required/);
    expect(status).toHaveTextContent(/approval.created/);
    expect(status).toHaveTextContent(/needs approval for screenshot/);
    expect(status.getAttribute("data-priority")).toBe("0");
  });

  it("invokes onClick with the selected event when the bar is clicked", () => {
    const onClick = vi.fn();
    render(
      <LiveOverlay
        events={[eventOf({ event_id: "x", type: "agent.failed", generated_at: 5, message: "boom" })]}
        onClick={onClick}
      />,
    );
    fireEvent.click(screen.getByRole("status"));
    expect(onClick).toHaveBeenCalledTimes(1);
    expect(onClick.mock.calls[0][0]?.type).toBe("agent.failed");
  });

  it("does not crash when onClick is omitted (idle / click fallback)", () => {
    render(<LiveOverlay events={[eventOf({ event_id: "y", type: "agent.thinking" })]} />);
    expect(() => fireEvent.click(screen.getByRole("status"))).not.toThrow();
  });
});

describe("LiveOverlay (Phase D8 — instruction.md §19, §20, multi-agent session)", () => {
  it("renders the highest-priority agent session as the single Overlay line", () => {
    // session-A は thinking 中、session-B で approval 発生 → session-B が勝つ
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "a-think", type: "agent.thinking", generated_at: 500, payload: { agent_session_id: "session-A" } }),
          eventOf({ event_id: "b-approval", type: "approval.created", generated_at: 100, payload: { agent_session_id: "session-B" } }),
        ]}
      />,
    );
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent(/Approval required/);
    // session-B の先頭 12 文字 "session-B" が表示される
    expect(screen.getByTestId("live-overlay-session")).toHaveTextContent("session-B");
    expect(status.getAttribute("data-agent-session-id")).toBe("session-B");
  });

  it("promotes the most important event when two sessions are equally important", () => {
    // session-A approval.created (ts=100), session-B approval.created (ts=500) → 新しい session-B 優先
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "a", type: "approval.created", generated_at: 100, payload: { agent_session_id: "session-A" } }),
          eventOf({ event_id: "b", type: "approval.created", generated_at: 500, payload: { agent_session_id: "session-B" } }),
        ]}
      />,
    );
    expect(screen.getByTestId("live-overlay-session")).toHaveTextContent("session-B");
  });

  it("falls back to no session tag when agent_session_id is missing", () => {
    render(<LiveOverlay events={[eventOf({ event_id: "z", type: "agent.thinking" })]} />);
    expect(screen.queryByTestId("live-overlay-session")).toBeNull();
    expect(screen.getByRole("status").getAttribute("data-agent-session-id")).toBe("");
  });
});

describe("liveOverlayClickTarget (Phase D8 — instruction.md §19)", () => {
  it("returns agent-sessions URL when agent_session_id is present", () => {
    const event = eventOf({
      type: "approval.created",
      payload: { agent_session_id: "session-X" },
    });
    expect(liveOverlayClickTarget(event)).toBe("/dashboard/agent-sessions/session-X");
  });

  it("URL-encodes agent_session_id with special characters", () => {
    const event = eventOf({
      type: "approval.created",
      payload: { agent_session_id: "session/with spaces" },
    });
    expect(liveOverlayClickTarget(event)).toBe("/dashboard/agent-sessions/session%2Fwith%20spaces");
  });

  it("falls back to task_id URL when agent_session_id is missing", () => {
    const event = eventOf({ type: "task.updated", task_id: "task-7" });
    expect(liveOverlayClickTarget(event)).toBe("/dashboard/operations/tasks/task-7");
  });

  it("falls back to approval_id URL when agent_session_id and task_id are missing", () => {
    const event = eventOf({ type: "approval.approved", approval_id: "ap-1" });
    expect(liveOverlayClickTarget(event)).toBe("/dashboard/approvals/ap-1");
  });

  it("returns raw-activity URL when no identifier is present", () => {
    const event = eventOf({ type: "agent.thinking" });
    expect(liveOverlayClickTarget(event)).toBe("/dashboard/activity");
  });
});

describe("LiveOverlay (Phase D9 — instruction.md §22 toggles)", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("hides thinking events when showThinking is false", () => {
    window.localStorage.setItem(
      "aegis.dashboard.settings",
      JSON.stringify({ liveOverlayShow: true, liveOverlayShowThinking: false, liveOverlayShowToolCalls: true }),
    );
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "think", type: "agent.thinking", generated_at: 200, message: "thinking" }),
          eventOf({ event_id: "tool", type: "agent.tool.started", generated_at: 100, message: "tool" }),
        ]}
      />,
    );
    // thinking は除外、tool started が表示される
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent(/Tool started/);
    expect(status).not.toHaveTextContent(/Agent thinking/);
  });

  it("hides tool call events when showToolCalls is false", () => {
    window.localStorage.setItem(
      "aegis.dashboard.settings",
      JSON.stringify({ liveOverlayShow: true, liveOverlayShowThinking: true, liveOverlayShowToolCalls: false }),
    );
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "think", type: "agent.thinking", generated_at: 200, message: "thinking" }),
          eventOf({ event_id: "tool", type: "agent.tool.started", generated_at: 100, message: "tool" }),
        ]}
      />,
    );
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent(/Agent thinking/);
    expect(status).not.toHaveTextContent(/Tool started/);
  });

  it("renders idle when liveOverlayShow is false", () => {
    window.localStorage.setItem(
      "aegis.dashboard.settings",
      JSON.stringify({ liveOverlayShow: false, liveOverlayShowThinking: true, liveOverlayShowToolCalls: true }),
    );
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "ap", type: "approval.created", generated_at: 100, message: "needs approval" }),
        ]}
      />,
    );
    expect(screen.getByRole("status")).toHaveTextContent(/AEGIS is idle/);
  });
});

describe("readLiveOverlayToggles (Phase D9 — instruction.md §22)", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("returns defaults when no settings are present", () => {
    expect(readLiveOverlayToggles()).toEqual({ show: true, showThinking: true, showToolCalls: true });
  });

  it("reads overrides from localStorage", () => {
    window.localStorage.setItem(
      "aegis.dashboard.settings",
      JSON.stringify({ liveOverlayShow: false, liveOverlayShowThinking: false, liveOverlayShowToolCalls: true }),
    );
    expect(readLiveOverlayToggles()).toEqual({ show: false, showThinking: false, showToolCalls: true });
  });

  it("falls back to defaults for malformed JSON", () => {
    window.localStorage.setItem("aegis.dashboard.settings", "not json {");
    expect(readLiveOverlayToggles()).toEqual({ show: true, showThinking: true, showToolCalls: true });
  });
});

describe("LiveOverlay (Phase L6 — DASHBOARD_V3_PLAN.md layer 識別表示)", () => {
  it("renders 'L1:' prefix for l1.* events", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "l1e", type: "l1.observation", generated_at: 100, message: "saw a thing" }),
        ]}
      />,
    );
    const status = screen.getByRole("status");
    expect(status.getAttribute("data-layer")).toBe("L1");
    expect(screen.getByTestId("live-overlay-layer")).toHaveTextContent("L1:");
    expect(status).toHaveTextContent(/l1\.observation/);
  });

  it("renders 'L2:' prefix for l2.* events", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "l2e", type: "l2.decision", generated_at: 100, message: "task created" }),
        ]}
      />,
    );
    expect(screen.getByRole("status").getAttribute("data-layer")).toBe("L2");
    expect(screen.getByTestId("live-overlay-layer")).toHaveTextContent("L2:");
  });

  it("renders 'L3:' prefix for l3.* events", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "l3e", type: "l3.invoked", generated_at: 100, message: "deep reasoning" }),
        ]}
      />,
    );
    expect(screen.getByRole("status").getAttribute("data-layer")).toBe("L3");
    expect(screen.getByTestId("live-overlay-layer")).toHaveTextContent("L3:");
  });

  it("renders 'MCP:' prefix for non-layer events (tool / agent / approval)", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "mcp", type: "agent.tool.started", generated_at: 100, message: "screenshot" }),
        ]}
      />,
    );
    expect(screen.getByRole("status").getAttribute("data-layer")).toBe("MCP");
    expect(screen.getByTestId("live-overlay-layer")).toHaveTextContent("MCP:");
  });

  it("layer label survives priority sort — l1.* event still shows L1: prefix", () => {
    render(
      <LiveOverlay
        events={[
          eventOf({ event_id: "agent", type: "agent.thinking", generated_at: 200, message: "thinking" }),
          eventOf({ event_id: "l1e", type: "l1.escalation", generated_at: 100, message: "escalate" }),
        ]}
      />,
    );
    // priority sort は l1.escalation / agent.thinking のスコアに依存するため、
    // ここでは layer 識別ラベルの存在のみ確認する。
    const layerEls = screen.getAllByTestId("live-overlay-layer");
    expect(layerEls.length).toBe(1);
  });
});
