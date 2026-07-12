import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    class MockEventSource extends EventTarget {
      static instances: MockEventSource[] = [];
      url: string;
      withCredentials: boolean;
      constructor(url: string, init?: EventSourceInit) {
        super();
        this.url = url;
        this.withCredentials = Boolean(init?.withCredentials);
        MockEventSource.instances.push(this);
      }
      close() {}
    }
    // @ts-expect-error test hook
    window.EventSource = MockEventSource;
    // @ts-expect-error test hook
    window.__emitAegisUiEvent = (name: string, payload: unknown) => {
      for (const source of MockEventSource.instances) {
        source.dispatchEvent(new MessageEvent(name, { data: JSON.stringify(payload) }));
      }
    };
  });
});

test("display shell prioritizes operation and keeps server rail compact", async ({ page }) => {
  await routeOverview(page, mockOverview("IDLE"));
  await page.goto("/display");
  await expect(page.getByText("Current Operation")).toBeVisible();
  await expect(page.getByText("Mission Phase")).toBeVisible();
  await expect(page.locator(".core-canvas canvas")).toBeVisible();
  await expect(page.locator(".server-rail")).toBeVisible();
  await expect(page.locator(".server-rail__item[data-expanded='true']")).toHaveCount(1);
});

test("display applies approval, degraded, offline, and recovery visual states without recreating canvas", async ({ page }) => {
  await routeOverview(page, mockOverview("EXECUTING"));
  await page.goto("/display");
  await page.waitForSelector(".core-canvas canvas");
  await page.evaluate(() => {
    // @ts-expect-error test hook
    window.__aegisCanvas = document.querySelector(".core-canvas canvas");
  });

  await page.evaluate(() => {
    // @ts-expect-error test hook
    window.__emitAegisUiEvent("approval.created", {
      type: "approval.created",
      source_type: "approval.created",
      generated_at: Date.now(),
      source_updated_at: Date.now(),
      payload: {},
      capability_id: "pc-server.mouse.click",
      server_id: "pc-server",
      status: "created",
      severity: "warning",
      message: "Approval required"
    });
  });
  await expect(page.getByText("Approval required").first()).toBeVisible({ timeout: 1000 });

  await page.evaluate(() => {
    // @ts-expect-error test hook
    window.__emitAegisUiEvent("status.changed", {
      type: "status.changed",
      source_type: "status.changed",
      generated_at: Date.now(),
      source_updated_at: Date.now(),
      payload: {},
      server_id: "browser-server",
      status: "offline",
      severity: "critical",
      message: "Browser disconnected"
    });
  });
  await expect(page.getByText("Browser disconnected").first()).toBeVisible({ timeout: 1000 });

  await page.waitForTimeout(15_200);
  expect(await page.evaluate(() => {
    // @ts-expect-error test hook
    return document.querySelector(".core-canvas canvas") === window.__aegisCanvas;
  })).toBe(true);
});

test("display supports reduced motion with static readable state", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await routeOverview(page, mockOverview("DEGRADED"));
  await page.goto("/display");
  await expect(page.locator(".core-legend__item")).toHaveCount(6);
  await expect(page.locator("[data-phase='Stabilizing']")).toBeVisible();
  await expect(page.locator(".core-canvas canvas")).toBeVisible();
});

test("display propagates read token to overview and stream requests", async ({ page }) => {
  await routeOverview(page, mockOverview("IDLE"));
  await page.goto("/display?display_token=read-token");
  await page.waitForSelector(".core-canvas canvas");

  const streamUrl = await page.evaluate(() => {
    // @ts-expect-error test hook
    return window.EventSource.instances[0].url;
  });
  expect(streamUrl).toContain("surface=display");
  expect(streamUrl).toContain("display_token=read-token");
});

async function routeOverview(page: import("@playwright/test").Page, overview: unknown) {
  await page.route("**/display/overview**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(overview)
    });
  });
}

function envelope(data: unknown) {
  return { generated_at: Date.now(), source_updated_at: Date.now(), status: "ok", stale: false, error: "", data };
}

function mockOverview(mode: "IDLE" | "EXECUTING" | "DEGRADED") {
  const degraded = mode === "DEGRADED";
  return {
    schema_version: "ui-overview.v2",
    generated_at: Date.now(),
    core: envelope({ mode: mode === "DEGRADED" ? "IDLE" : mode, health: degraded ? "DEGRADED" : "ONLINE", activity_level: mode === "EXECUTING" ? 5 : 1, confidence: degraded ? "medium" : "high", active_goal: "Keep AEGIS useful" }),
    attention: envelope({ items: degraded ? [{ id: "server-browser", kind: "server", severity: "warning", title: "Browser degraded", message: "Recovering" }] : [] }),
    current_task: envelope({
      task_id: mode === "EXECUTING" ? "task-1" : "",
      title: mode === "EXECUTING" ? "Inspect current desktop" : "No active task",
      phase: mode.toLowerCase(),
      current_action: mode === "EXECUTING" ? "Execute pc-server.screenshot.get_screenshot" : "",
      next_action: "",
      blocked_reason: "",
      capability_id: mode === "EXECUTING" ? "pc-server.screenshot.get_screenshot" : "",
      steps: [{ status: "pending", capability_id: "browser-server.page.browse" }]
    }),
    servers: envelope({
      items: [
        { server_id: "ai-server", status: "ONLINE", status_detail: "Ready" },
        { server_id: "pc-server", status: "ONLINE", status_detail: "Ready" },
        { server_id: "android-server", status: "ONLINE", status_detail: "Ready" },
        { server_id: "browser-server", status: degraded ? "DEGRADED" : "ONLINE", status_detail: degraded ? "Recovering" : "Ready" },
        { server_id: "room-server", status: "UNCONFIGURED", status_detail: "Not installed yet" },
        { server_id: "dev-server", status: "ONLINE", status_detail: "Ready" }
      ]
    }),
    user_state: envelope({}),
    mind_summary: envelope({ memory: { episodic: 2, semantic: 3 }, autonomy: { desires: { growth: 4 } } }),
    notifications: envelope({ recent: [], unread_count: 0 }),
    approvals: envelope({ pending: [], pending_count: 0 }),
    commitments: envelope({ items: [] }),
    usage: envelope({}),
    freshness: envelope({})
  };
}
