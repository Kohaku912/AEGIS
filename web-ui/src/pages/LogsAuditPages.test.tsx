import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { UiOverview } from "../types";
import { AuditPage } from "./AuditPage";
import { LogsPage } from "./LogsPage";

const overview = {
  servers: { data: { items: [{ server_id: "ai-server", status: "ONLINE" }] } },
} as UiOverview;

describe("logs and audit pages", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders meaningful audit entry fields", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      entries: [{
        entry_id: "audit-1",
        timestamp_ms: Date.now(),
        action: "tool_execution",
        actor: "tool_broker",
        decision: "ALLOW",
        capability_id: "ai-server.workspace.read_file",
        detail: { result_summary: "Read the requested file" },
      }],
      page: 1,
      per_page: 50,
      total: 1,
      total_pages: 1,
    }), { status: 200, headers: { "Content-Type": "application/json" } }));

    render(<LogsPage overview={overview} />);

    await waitFor(() => expect(screen.getAllByText("tool_execution").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Read the requested file").length).toBeGreaterThan(0);
    expect(screen.getAllByText("ALLOW").length).toBeGreaterThan(0);
  });

  it("renders groups returned by the SQLite-backed audit API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      groups: [{
        group_id: "group-1",
        group_title: "Chat operation",
        group_type: "chat",
        end_ms: Date.now(),
        entry_count: 3,
        error_count: 0,
      }],
      page: 1,
      per_page: 30,
      total: 1,
      total_pages: 1,
    }), { status: 200, headers: { "Content-Type": "application/json" } }));

    render(<AuditPage />);

    await waitFor(() => expect(screen.getAllByText("Chat operation").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Recorded").length).toBeGreaterThan(0);
  });
});
