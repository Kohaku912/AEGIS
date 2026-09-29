// LlmLayerPanel.test.tsx — DASHBOARD_V3_PLAN.md Phase L6
//
// L1 / L2 / L3 専用パネルの UI / data fetch / filter 動作のテスト。
// fetch をモックし、layer ごとに events / stats を返す。

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { LlmLayerPanel } from "./LlmLayerPanel";
import type { LlmEvent } from "../api/client";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

type FetchMock = ReturnType<typeof vi.fn>;

function mockFetchSequence(handlers: Array<(url: string) => unknown>): FetchMock {
  const fn = vi.fn();
  handlers.forEach((handler) => {
    fn.mockImplementationOnce((url: string) =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: async () => handler(url),
      } as Response),
    );
  });
  // 2 回目以降の tick で再利用される
  fn.mockImplementation((url: string) =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: async () => handlers[0](url),
    } as Response),
  );
  globalThis.fetch = fn as unknown as typeof fetch;
  return fn;
}

const sampleL1Event: LlmEvent = {
  event_id: "l1-001",
  type: "l1.observation",
  source: "l1_router",
  timestamp: 1_700_000_000_000,
  payload: {
    value: 0.8,
    priority: 0.7,
    required_intelligence: "high",
    action_type: "escalate",
    reason: "complex",
    _trace_ids: { agent_session_id: "sess-1", trace_id: "trace-l1", parent_id: "parent-l0" },
  },
};

const sampleL1CapEvent: LlmEvent = {
  event_id: "l1-002",
  type: "l1.capability.invoked",
  source: "l1_executor",
  timestamp: 1_700_000_001_000,
  payload: { capability_id: "pc-server.screenshot.get_screenshot", risk_level: "low" },
};

describe("LlmLayerPanel (Phase L6 — DASHBOARD_V3_PLAN.md layer 別パネル)", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("L1 layer: fetches /api/l1/events and /api/l1/events/stats and renders title", async () => {
    mockFetchSequence([
      (url) => {
        if (url.includes("/api/l1/events/stats")) {
          return {
            generated_at: 1,
            layer: "L1",
            total: 2,
            by_kind: {
              "l1.observation": 1,
              "l1.decision": 0,
              "l1.escalation": 0,
              "l1.capability.invoked": 1,
              "l1.capability.completed": 0,
            },
          };
        }
        return {
          generated_at: 1,
          layer: "L1",
          count: 2,
          kinds: ["l1.observation", "l1.decision", "l1.escalation", "l1.capability.invoked", "l1.capability.completed"],
          events: [sampleL1Event, sampleL1CapEvent],
        };
      },
    ]);

    render(<LlmLayerPanel layer="L1" />);
    expect(screen.getByTestId("llm-layer-panel-L1")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/L1 — 知覚 \/ Router/);

    await waitFor(() => {
      expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/l1\.observation/);
    });
    expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/l1\.capability\.invoked/);
    // event_id
    expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/l1-001/);
    expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/trace-l1/);
    expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/sess-1/);
  });

  it("L2 layer: fetches /api/l2/events and renders L2 title", async () => {
    mockFetchSequence([
      (url) => {
        if (url.includes("/api/l2/events/stats")) {
          return { generated_at: 1, layer: "L2", total: 1, by_kind: { "l2.decision": 1, "l2.thinking": 0, "l2.escalation": 0 } };
        }
        return {
          generated_at: 1,
          layer: "L2",
          count: 1,
          kinds: ["l2.thinking", "l2.decision", "l2.escalation"],
          events: [
            { event_id: "l2-001", type: "l2.decision", source: "l2_mind", timestamp: 1_700_000_000_000, payload: { action_type: "task" } },
          ],
        };
      },
    ]);

    render(<LlmLayerPanel layer="L2" />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/L2 — Autonomous Mind/);

    await waitFor(() => {
      expect(screen.getByTestId("layer-events-L2")).toHaveTextContent(/l2\.decision/);
    });
  });

  it("L3 layer: fetches /api/l3/events and renders L3 title", async () => {
    mockFetchSequence([
      (url) => {
        if (url.includes("/api/l3/events/stats")) {
          return { generated_at: 1, layer: "L3", total: 2, by_kind: { "l3.invoked": 1, "l3.completed": 1, "l3.failed": 0 } };
        }
        return {
          generated_at: 1,
          layer: "L3",
          count: 2,
          kinds: ["l3.invoked", "l3.completed", "l3.failed"],
          events: [
            { event_id: "l3-001", type: "l3.invoked", source: "l3_reasoner", timestamp: 1_700_000_000_000, payload: { problem: "hard" } },
            { event_id: "l3-002", type: "l3.completed", source: "l3_reasoner", timestamp: 1_700_000_001_000, payload: { recommended_action: "task" } },
          ],
        };
      },
    ]);

    render(<LlmLayerPanel layer="L3" />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/L3 — Deep Reasoner/);

    await waitFor(() => {
      expect(screen.getByTestId("layer-events-L3")).toHaveTextContent(/l3\.invoked/);
    });
    expect(screen.getByTestId("layer-events-L3")).toHaveTextContent(/l3\.completed/);
  });

  it("renders an error message when fetch fails", async () => {
    globalThis.fetch = vi.fn(() => Promise.reject(new Error("network down"))) as unknown as typeof fetch;
    render(<LlmLayerPanel layer="L1" />);
    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/network down/);
    });
  });

  it("renders an empty-state message when there are no events", async () => {
    mockFetchSequence([
      (url) => {
        if (url.includes("/api/l1/events/stats")) {
          return { generated_at: 1, layer: "L1", total: 0, by_kind: {} };
        }
        return { generated_at: 1, layer: "L1", count: 0, kinds: [], events: [] };
      },
    ]);
    render(<LlmLayerPanel layer="L1" />);
    await waitFor(() => {
      expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/No events yet/);
    });
  });

  it("renders the description and kind filter for the requested layer", async () => {
    mockFetchSequence([
      (url) => {
        if (url.includes("/api/l2/events/stats")) {
          return { generated_at: 1, layer: "L2", total: 0, by_kind: {} };
        }
        return { generated_at: 1, layer: "L2", count: 0, kinds: null, events: [] };
      },
    ]);
    render(<LlmLayerPanel layer="L2" />);
    // description
    expect(screen.getByText(/Memory \/ Desire \/ Task \/ L1 summary/)).toBeInTheDocument();
    // kind filter options
    const select = document.getElementById("kind-filter-L2") as HTMLSelectElement;
    expect(select).toBeInTheDocument();
    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toContain("l2.thinking");
    expect(options).toContain("l2.decision");
    expect(options).toContain("l2.escalation");
  });

  it("passes the selected kind to the backend fetcher", async () => {
    const fetchMock = mockFetchSequence([
      (url) => {
        if (url.includes("/api/l1/events/stats")) {
          return { generated_at: 1, layer: "L1", total: 1, by_kind: { "l1.observation": 1 } };
        }
        return {
          generated_at: 1,
          layer: "L1",
          count: 1,
          kinds: ["l1.observation"],
          events: [sampleL1Event],
        };
      },
    ]);

    render(<LlmLayerPanel layer="L1" />);
    await waitFor(() => {
      expect(screen.getByTestId("layer-events-L1")).toHaveTextContent(/l1\.observation/);
    });
    const select = document.getElementById("kind-filter-L1") as HTMLSelectElement;
    select.value = "l1.observation";
    select.dispatchEvent(new Event("change", { bubbles: true }));
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes("kinds=l1.observation"))).toBe(true);
    });
  });
});
