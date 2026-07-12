import { expect, test } from "@playwright/test";

test("display shell has a visible core canvas", async ({ page }) => {
  await page.route("**/display/overview", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(mockOverview())
    });
  });
  await page.goto("/display");
  await expect(page.getByText("Dedicated Display / Read Only")).toBeVisible();
  await expect(page.locator(".core-canvas canvas")).toBeVisible();
});

function envelope(data: unknown) {
  return { generated_at: Date.now(), source_updated_at: Date.now(), status: "ok", stale: false, error: "", data };
}

function mockOverview() {
  return {
    schema_version: "ui-overview.v2",
    generated_at: Date.now(),
    core: envelope({ mode: "IDLE", health: "ONLINE", activity_level: 1, confidence: "high" }),
    attention: envelope({ items: [] }),
    current_task: envelope({ task_id: "", title: "No active task", phase: "idle", current_action: "", next_action: "", blocked_reason: "" }),
    servers: envelope({ items: [{ server_id: "ai-server", status: "ONLINE", status_detail: "Ready" }] }),
    user_state: envelope({}),
    mind_summary: envelope({}),
    notifications: envelope({ recent: [], unread_count: 0 }),
    approvals: envelope({ pending: [], pending_count: 0 }),
    commitments: envelope({ items: [] }),
    usage: envelope({}),
    freshness: envelope({})
  };
}
