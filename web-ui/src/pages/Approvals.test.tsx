import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Approvals } from "./Approvals";
import type { UiOverview } from "../types";

describe("Approvals", () => {
  it("shows approval identifiers and capability ids", () => {
    render(<Approvals overview={overview()} />);
    expect(screen.getAllByText("approval-1").length).toBeGreaterThan(0);
    expect(screen.getByText("pc-server.keyboard.type_text")).toBeInTheDocument();
  });
});

function envelope<T>(data: T) {
  return { generated_at: 1000, source_updated_at: 1000, status: "ok" as const, stale: false, error: "", data };
}

function overview(): UiOverview {
  return {
    schema_version: "ui-overview.v2",
    generated_at: 1000,
    core: envelope({}),
    attention: envelope({ items: [] }),
    current_task: envelope({ task_id: "", title: "", phase: "", current_action: "", next_action: "", blocked_reason: "" }),
    servers: envelope({ items: [] }),
    user_state: envelope({}),
    mind_summary: envelope({}),
    notifications: envelope({ recent: [], unread_count: 0 }),
    approvals: envelope({
      pending_count: 1,
      pending: [
        {
          approval_id: "approval-1",
          capability_id: "pc-server.keyboard.type_text",
          risk: "high",
          summary: "Type into safe test field"
        }
      ]
    }),
    commitments: envelope({ items: [] }),
    usage: envelope({}),
    freshness: envelope({})
  };
}
