import { describe, expect, it } from "vitest";
import { factsForEntity, pageContextFacts, primaryFacts } from "./entityDetail";
import type { EntitySummary, UiOverview } from "./types";

describe("entityDetail", () => {
  it("maps contract fields onto live entity values", () => {
    const entity: EntitySummary = {
      id: "task-1",
      type: "task",
      title: "Inspect desktop",
      subtitle: "pc-server",
      status: "running",
      severity: "normal",
      tags: ["task"],
      relations: [{ type: "capability", id: "pc-server.screenshot.get_screenshot" }],
      available_actions: [{ id: "inspect", label: "Inspect", level: "view" }],
      permissions: [],
      data: {
        goal: "Capture the current desktop",
        risk_level: "low",
        verification: { status: "passed", summary: "Screenshot verified" },
        cost_summary: "120 tokens",
        dependency_edges: [{ from: "observe", to: "capture" }],
      }
    };

    const facts = factsForEntity(entity, ["Goal", "Risk", "Verification strategy", "Expected cost", "Dependency graph"]);
    expect(facts.find((item) => item.label === "Goal")?.value).toContain("Capture the current desktop");
    expect(facts.find((item) => item.label === "Risk")?.value).toBe("low");
    expect(facts.find((item) => item.label === "Verification strategy")?.value).toContain("Screenshot verified");
    expect(facts.find((item) => item.label === "Expected cost")?.value).toBe("120 tokens");
    expect(facts.find((item) => item.label === "Dependency graph")?.missing).toBeFalsy();
  });

  it("exposes primary inspector facts without developer mode", () => {
    const facts = primaryFacts({
      id: "srv-1",
      type: "server",
      title: "PC Server",
      subtitle: "host",
      status: "online",
      severity: "normal",
      tags: [],
      relations: [],
      available_actions: [],
      permissions: [],
      data: { host: "192.168.50.176", port: 50052, latency_ms: 12, recovery_hint: "None" }
    });
    expect(facts.some((item) => item.label === "Host" && item.value.includes("192.168.50.176"))).toBe(true);
    expect(facts.some((item) => item.label === "Port" && item.value === "50052")).toBe(true);
  });

  it("builds page context from overview projections", () => {
    const overview = {
      core: { data: { mode: "AUTONOMOUS", health: "ONLINE" } },
      mind_summary: { data: { autonomy: { profile: "balanced", running: true, next_run_at: "soon" } } },
      attention: { data: { items: [{ id: "a1" }] } },
      approvals: { data: { pending_count: 2 } },
      commitments: { data: { items: [], summary: "none due" } },
      notifications: { data: { unread_count: 3, recent: [] } },
      usage: { data: {} },
      errors: { data: { count: 0 } },
      connection: { data: {} },
      capabilities: { data: {} },
      presentations: { data: {} },
      memory: { data: {} },
      user_state: { data: {} },
    } as unknown as UiOverview;

    const autonomy = pageContextFacts("autonomy", overview);
    expect(autonomy.find((item) => item.label === "Mode")?.value).toBe("AUTONOMOUS");
    expect(autonomy.find((item) => item.label === "Profile")?.value).toBe("balanced");

    const attention = pageContextFacts("attention", overview);
    expect(attention.find((item) => item.label === "Pending approvals")?.value).toBe("2");
  });
});
