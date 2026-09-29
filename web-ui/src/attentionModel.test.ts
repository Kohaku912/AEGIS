import { describe, expect, it } from "vitest";
import { buildAttentionItems, filterAttention } from "./attentionModel";
import type { UiOverview } from "./types";

function overviewWith(attention: Array<Record<string, unknown>>, waiting: Array<Record<string, unknown>> = []): UiOverview {
  return {
    approvals: { data: { pending: [] } },
    attention: { data: { items: attention } },
    errors: { data: { items: [] } },
    servers: { data: { items: [] } },
    tasks: { data: { waiting } },
  } as unknown as UiOverview;
}

describe("attention model category assignment", () => {
  it("uses the upstream kind instead of sniffing the title text", () => {
    const items = buildAttentionItems(
      overviewWith([
        { id: "a1", kind: "approval", title: "Approval required", severity: "warning" },
        { id: "s1", kind: "server", title: "pc-server OFFLINE", severity: "critical" },
        { id: "n1", kind: "notification", title: "Task failed with error", severity: "info" },
      ]),
    );
    const byId = new Map(items.map((item) => [item.id, item]));

    expect(byId.get("attention:a1")?.kind).toBe("approval");
    expect(byId.get("attention:s1")?.kind).toBe("connection");
    // The title literally says "failed", but the upstream category is a plain
    // notification. The authoritative label must win over the text.
    expect(byId.get("attention:n1")?.kind).toBe("warning");
  });

  it("falls back to warning when the upstream kind is missing or unknown", () => {
    const items = buildAttentionItems(
      overviewWith([
        { id: "x1", title: "Config changed" },
        { id: "x2", kind: "something-new", title: "Input needed" },
      ]),
    );

    expect(items.find((item) => item.id === "attention:x1")?.kind).toBe("warning");
    expect(items.find((item) => item.id === "attention:x2")?.kind).toBe("warning");
  });

  it("classifies waiting tasks as approvals rather than input", () => {
    // `_waiting_tasks` only returns tasks awaiting approval and the task status
    // enum has no "input" state, so nothing should ever land in the input tab.
    const items = buildAttentionItems(
      overviewWith([], [{ task_id: "t1", title: "Approve deploy", status: "waiting_approval" }]),
    );

    expect(items.find((item) => item.id === "task-wait:t1")?.kind).toBe("approval");
    expect(filterAttention(items, "input")).toHaveLength(0);
    expect(filterAttention(items, "approvals")).toHaveLength(1);
  });
});
