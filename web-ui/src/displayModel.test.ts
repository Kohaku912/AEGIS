import { describe, expect, it } from "vitest";
import { mapUiEventToVisualEvent, serverNeedsDetail, summarizeMemory, summarizeServers } from "./displayModel";
import type { ServerItem, UiOverview } from "./types";

function envelope<T>(data: T) {
  return { generated_at: 1, source_updated_at: 1, status: "ok" as const, stale: false, error: "", data };
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
      type: "tool.execution.failed",
      source_type: "tool.execution.failed",
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
      schema_version: "ui-overview.v2",
      generated_at: 1,
      core: envelope({ active_goal: "ship ui", confidence: "high" }),
      attention: envelope({ items: [] }),
      current_task: envelope({ task_id: "", title: "", phase: "", current_action: "", next_action: "", blocked_reason: "" }),
      servers: envelope({ items: [] }),
      user_state: envelope({}),
      mind_summary: envelope({ memory: { episodic: 2, semantic: 3, last_consolidation: "today" }, autonomy: { desires: { growth: 4, social: 2 } } }),
      notifications: envelope({ recent: [], unread_count: 0 }),
      approvals: envelope({ pending: [], pending_count: 0 }),
      commitments: envelope({ items: [] }),
      usage: envelope({}),
      freshness: envelope({})
    } satisfies UiOverview;
    expect(summarizeMemory(overview)["Dominant desire"]).toBe("growth");
    expect(summarizeMemory(overview)["Memories used"]).toBe("5");
  });
});
