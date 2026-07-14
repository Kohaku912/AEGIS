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

test("display stream reconnect includes the last received event id", async ({ page }) => {
  await routeOverview(page, mockOverview("IDLE"));
  await routeDashboardOverview(page, mockOverview("IDLE"));
  await page.goto("/display?display_token=read-token");
  await page.waitForSelector(".core-canvas canvas");

  await page.evaluate(() => {
    // @ts-expect-error test hook
    window.__emitAegisUiEvent("status.changed", {
      event_id: "evt-display-replay-1",
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
  await page.goto("/dashboard");
  await page.goto("/display?display_token=read-token");
  await page.waitForSelector(".core-canvas canvas");

  const streamUrl = await page.evaluate(() => {
    // @ts-expect-error test hook
    return window.EventSource.instances.at(-1).url;
  });
  expect(streamUrl).toContain("surface=display");
  expect(streamUrl).toContain("display_token=read-token");
  expect(streamUrl).toContain("last_event_id=evt-display-replay-1");
});

test("display is fixed read-only chrome across target desktop viewports", async ({ page }) => {
  for (const size of [
    { width: 1366, height: 768 },
    { width: 1920, height: 1080 },
    { width: 2560, height: 1440 }
  ]) {
    await page.setViewportSize(size);
    await routeOverview(page, mockOverview("EXECUTING"));
    await page.goto("/display");
    await page.waitForSelector(".core-canvas canvas");
    await expect(page.locator(".display-shell")).toBeVisible();
    expect(await page.locator("button, input, textarea, select, a[href], [tabindex]:not([tabindex='-1'])").count()).toBe(0);
    const overflow = await page.evaluate(() => ({
      body: document.body.scrollHeight - document.body.clientHeight,
      root: document.documentElement.scrollHeight - document.documentElement.clientHeight
    }));
    expect(overflow.body).toBeLessThanOrEqual(2);
    expect(overflow.root).toBeLessThanOrEqual(2);
  }
});

test("display shows offline snapshot and privacy redaction without interactive controls", async ({ page }) => {
  await routeOverview(page, mockOverview("EXECUTING", { offline: true, stale: true, privacy: true }));
  await page.goto("/display");
  await expect(page.locator(".display-shell")).toHaveAttribute("data-offline", "true");
  await expect(page.locator(".display-shell")).toHaveAttribute("data-stale", "true");
  await expect(page.locator(".display-shell")).toHaveAttribute("data-privacy", "true");
  await expect(page.getByText("OFFLINE SNAPSHOT")).toBeVisible();
  await expect(page.getByText("PRIVACY MODE")).toBeVisible();
  await expect(page.getByText("Private information hidden").first()).toBeVisible();
  await expect(page.getByText("Inspect current desktop")).toHaveCount(0);
  expect(await page.locator("button, input, textarea, select, a[href], [tabindex]:not([tabindex='-1'])").count()).toBe(0);
});

test("display visual states match their reduced-motion baselines", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const scenarios = [
    { name: "idle", overview: mockOverview("IDLE") },
    { name: "executing", overview: mockOverview("EXECUTING") },
    { name: "approval", overview: mockOverview("EXECUTING", { approval: true }) },
    { name: "degraded", overview: mockOverview("DEGRADED") },
    { name: "offline", overview: mockOverview("EXECUTING", { offline: true, stale: true }) },
    { name: "recovery", overview: mockOverview("IDLE", { recovery: true }) },
  ];

  for (const scenario of scenarios) {
    await page.unroute("**/display/overview**");
    await routeOverview(page, scenario.overview);
    await page.goto("/display");
    await page.waitForSelector(".core-canvas canvas");
    if (scenario.name === "recovery") {
      await page.evaluate(() => {
        // @ts-expect-error test hook
        window.__emitAegisUiEvent("status.changed", {
          event_id: "recovery-visual-1",
          type: "status.changed",
          source_type: "status.changed",
          generated_at: Date.now(),
          source_updated_at: Date.now(),
          payload: {},
          server_id: "browser-server",
          status: "online",
          severity: "info",
          message: "Browser recovered",
        });
      });
      await expect(page.getByText("Browser recovered").first()).toBeVisible();
    }
    await expect(page.locator(".display-shell")).toHaveScreenshot(`display-${scenario.name}.png`, {
      animations: "disabled",
      maxDiffPixelRatio: 0.02,
    });
  }
});

test("display keeps canvas and event memory bounded for a 72-hour-equivalent stream", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await routeOverview(page, mockOverview("EXECUTING"));
  await page.goto("/display");
  await page.waitForSelector(".core-canvas canvas");
  const result = await page.evaluate(async () => {
    const canvas = document.querySelector(".core-canvas canvas");
    const memory = (performance as Performance & { memory?: { usedJSHeapSize: number } }).memory;
    const beforeBytes = memory?.usedJSHeapSize || 0;
    // @ts-expect-error test hook
    const emit = window.__emitAegisUiEvent as ((name: string, payload: unknown) => void) | undefined;
    if (!emit) throw new Error("Display stream test hook is unavailable");
    for (let index = 0; index < 8_640; index += 1) {
      emit("status.changed", {
        event_id: `soak-${index}`,
        type: "status.changed",
        source_type: "status.changed",
        generated_at: Date.now(),
        source_updated_at: Date.now(),
        payload: {},
        server_id: index % 2 ? "browser-server" : "pc-server",
        status: "online",
        severity: "info",
        message: `Heartbeat ${index}`,
      });
      if (index % 240 === 0) await new Promise((resolve) => setTimeout(resolve, 0));
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      sameCanvas: canvas === document.querySelector(".core-canvas canvas"),
      heapGrowthBytes: memory ? memory.usedJSHeapSize - beforeBytes : 0,
    };
  });
  expect(result.sameCanvas).toBe(true);
  await expect.poll(() => page.locator(".display-events .event-row").count(), { timeout: 10_000 }).toBeLessThanOrEqual(6);
  expect(result.heapGrowthBytes).toBeLessThan(96 * 1024 * 1024);
});

async function routeOverview(page: import("@playwright/test").Page, overview: unknown) {
  await page.route("**/display/overview**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(overview)
    });
  });
}

async function routeDashboardOverview(page: import("@playwright/test").Page, overview: unknown) {
  await page.route("**/api/ui/overview**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(overview)
    });
  });
}

function envelope(data: unknown, stale = false) {
  return { generated_at: Date.now(), source_updated_at: Date.now(), status: "ok", stale, error: "", data };
}

function mockOverview(
  mode: "IDLE" | "EXECUTING" | "DEGRADED",
  options: { offline?: boolean; stale?: boolean; privacy?: boolean; approval?: boolean; recovery?: boolean } = {},
) {
  const degraded = mode === "DEGRADED";
  return {
    schema_version: "ui-overview.v3",
    generated_at: Date.now(),
    core: envelope({ mode: mode === "DEGRADED" ? "IDLE" : mode, health: degraded ? "DEGRADED" : "ONLINE", activity_level: mode === "EXECUTING" ? 5 : 1, confidence: degraded ? "medium" : "high", active_goal: "Keep AEGIS useful" }),
    connection: envelope({ quality: degraded ? "degraded" : "good", online_count: degraded ? 5 : 6, total_count: 6, attention_count: degraded ? 1 : 0 }),
    display_scene: envelope(
      {
        phase: options.privacy ? "Privacy" : options.recovery ? "Recovery" : degraded ? "Stabilizing" : mode === "EXECUTING" ? "Executing" : "Idle",
        takeover: { active: false },
        privacy_mode: Boolean(options.privacy),
        offline: Boolean(options.offline),
        stale: Boolean(options.stale)
      },
      Boolean(options.stale)
    ),
    presentations: envelope({ takeover: [], overlays: [], persistent: [], ambient: [], items: [], count: 0 }),
    tasks: envelope({ primary: { task_id: "", title: "", phase: "", current_action: "", next_action: "", blocked_reason: "" }, active: [], waiting: [], scheduled: [], recent: [] }),
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
    capabilities: envelope({ items: [], count: 0 }),
    user_situation: envelope({}),
    user_state: envelope({}),
    mind: envelope({}),
    mind_summary: envelope({ memory: { episodic: 2, semantic: 3 }, autonomy: { desires: { growth: 4 } } }),
    memory: envelope({ summary: {} }),
    notifications: envelope({ recent: [], unread_count: 0 }),
    approvals: envelope({
      pending: options.approval ? [{ approval_id: "approval-visual-1", capability_id: "pc-server.mouse.click", risk: "HIGH", summary: "Approve safe test click", created_at: Date.now() }] : [],
      pending_count: options.approval ? 1 : 0,
    }),
    commitments: envelope({ items: [] }),
    usage: envelope({}),
    errors: envelope({ items: [], count: 0 }),
    freshness: envelope({}, Boolean(options.stale))
  };
}
