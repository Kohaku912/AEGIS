import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { existsSync } from "node:fs";
import { join } from "node:path";

test.beforeEach(async ({ page }) => {
  const staticDir = process.env.AEGIS_E2E_STATIC_DIR;
  if (staticDir) {
    await page.route("**/*", async (route) => {
      const request = route.request();
      if (request.resourceType() === "document") {
        await route.fulfill({ path: join(staticDir, "index.html"), contentType: "text/html" });
        return;
      }
      await route.continue();
    });
    await page.route("**/assets/**", async (route) => {
      const path = join(staticDir, "assets", new URL(route.request().url()).pathname.split("/").pop() || "");
      if (!existsSync(path)) return route.abort();
      await route.fulfill({ path });
    });
  }
  await page.addInitScript(() => {
    class QuietEventSource extends EventTarget { close() {} }
    // @ts-expect-error deterministic UI stream for shell tests
    window.EventSource = QuietEventSource;
  });
  await page.route("**/api/ui/overview", (route) => route.fulfill({ json: overview() }));
  await page.route("**/api/ui/entities**", async (route) => {
    const resource = new URL(route.request().url()).searchParams.get("resource") || "task";
    await route.fulfill({ json: { items: [entity(resource)], page: 1, limit: 100, total: 1, has_more: false, generated_at: new Date().toISOString() } });
  });
  await page.route("**/api/ui/search**", (route) => route.fulfill({ json: { items: [entity("capability")], total: 1 } }));
  await page.route("**/api/ui/saved-views**", (route) => route.fulfill({ json: { items: [] } }));
  await page.route("**/api/capabilities/*/risk", (route) => route.fulfill({ json: { manifest: { risk_level: "READ_ONLY", requires_approval: false, enabled: true }, override: {}, effective: { risk_level: "low", requires_approval: false, enabled: true }, override_active: false } }));
  await page.route("**/api/approvals**", (route) => route.fulfill({ json: { items: [], page: 1, limit: 100, total: 0, has_more: false } }));
  await page.route("**/api/settings", (route) => route.fulfill({ json: { autonomy: { autonomous_loop_enabled: true }, budgets: { daily_budget_usd: 2 } } }));
  await page.route("**/auth/me", (route) => route.fulfill({ json: { csrf_token: "test", authenticated: true, fresh: true } }));
});

test("master shell exposes five English domains and command palette", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  const domains = ["Home", "Work", "Communication", "Systems", "Settings and Administration"];
  await expect(page.locator(".nav-domain > button")).toHaveCount(5);
  for (const label of domains) await expect(page.locator(".nav-domain > button", { hasText: label })).toBeVisible();
  await page.keyboard.press("Control+K");
  await expect(page.getByRole("dialog", { name: "Command palette" })).toBeVisible();
  await expect(page.getByText(/Dangerous actions open a confirmation dialog/)).toBeVisible();
});

test("capability catalog uses Manager entities and opens effective policy detail", async ({ page }) => {
  await page.goto("/dashboard/capabilities/catalog");
  await expect(page.getByRole("heading", { name: "Capability Catalog", level: 2 })).toBeVisible();
  await expect(page.getByText("Manager-backed capability")).toBeVisible();
  await page.getByText("Manager-backed capability").click();
  await expect(page.getByText("Policy controls")).toBeVisible();
  await expect(page.getByText("Execution contract")).toBeVisible();
});

test("changing capability risk applies immediately without review or draft", async ({ page }) => {
  const pageErrors: string[] = [];
  let riskPosts = 0;
  let effectiveRisk = "low";
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("**/api/capabilities/*/risk", async (route) => {
    if (route.request().method() === "POST") {
      riskPosts += 1;
      effectiveRisk = String(route.request().postDataJSON().risk_level);
    }
    await route.fulfill({
      json: {
        manifest: { risk_level: "READ_ONLY", requires_approval: false, enabled: true },
        override: { risk_level: effectiveRisk },
        effective: { risk_level: effectiveRisk, requires_approval: false, enabled: true },
        override_active: effectiveRisk !== "low",
      },
    });
  });
  await page.goto("/dashboard/capabilities/catalog");
  await page.getByText("Manager-backed capability").click();

  await page.getByLabel("Risk").selectOption("high_risk");

  await expect.poll(() => riskPosts).toBe(1);
  await expect(page.getByLabel("Risk")).toHaveValue("high_risk");
  await expect(page.getByText("Policy updated, catalog reloaded, and effective policy audited.")).toBeVisible();
  await expect(page.getByText("Override draft")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Review changes" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Test preview" })).toHaveCount(0);
  expect(pageErrors).toEqual([]);
});

test("global search reaches records outside the overview", async ({ page }) => {
  await page.goto("/dashboard");
  const search = page.getByLabel("Search AEGIS");
  await search.fill("capability record");
  await expect(page.locator(".global-search__results").getByText("Manager-backed capability")).toBeVisible();
});

test("chat rapid submit executes only once", async ({ page }) => {
  let sends = 0;
  await page.route("**/api/chat/send", async (route) => {
    sends += 1;
    await new Promise((resolve) => setTimeout(resolve, 150));
    await route.fulfill({ json: { response: "Accepted", request_id: "e2e" } });
  });
  await page.goto("/dashboard");
  await page.getByLabel("Talk to AEGIS").click();
  await page.getByRole("textbox", { name: "Message", exact: true }).fill("Run exactly once");
  await page.locator(".chat-form").evaluate((form) => {
    (form as HTMLFormElement).requestSubmit();
    (form as HTMLFormElement).requestSubmit();
  });
  await expect.poll(() => sends).toBe(1);
});

test("tasks are the central work surface", async ({ page }) => {
  await page.goto("/dashboard/work/tasks");
  await expect(page.getByRole("region", { name: "Task details" })).toContainText("Manager-backed tasks");
  await expect(page.getByRole("button", { name: /Dangerous.*Cancel/ })).toBeVisible();
});

test("density preference survives navigation and reload", async ({ page }) => {
  await page.goto("/dashboard");
  await page.getByLabel("Display density").selectOption("compact");
  await page.reload();
  await expect(page.locator(".master-shell")).toHaveAttribute("data-density", "compact");
});

test("settings stage edits and require explicit save", async ({ page }) => {
  let posts = 0;
  await page.route("**/api/settings", async (route) => {
    if (route.request().method() === "POST") { posts += 1; await route.fulfill({ json: { ok: true } }); return; }
    await route.fulfill({ json: { autonomy: { autonomous_loop_enabled: true }, budgets: { daily_budget_usd: 2 } } });
  });
  await page.route("**/auth/me", (route) => route.fulfill({ json: { csrf_token: "test" } }));
  await page.goto("/settings/autonomy");
  await page.getByLabel("Autonomous Loop Enabled").uncheck();
  await expect(page.getByRole("region", { name: "Pending settings changes" })).toBeVisible();
  expect(posts).toBe(0);
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect.poll(() => posts).toBe(1);
});

test("policy simulation reports a decision without executing a capability", async ({ page }) => {
  let simulations = 0;
  await page.route("**/api/policy/simulate", async (route) => {
    simulations += 1;
    const input = route.request().postDataJSON();
    await route.fulfill({ json: { simulation: { capability_id: input.capability_id, decision: "ALLOW", reason: "Risk level READ_ONLY - allowed.", effective_risk: "READ_ONLY", requires_approval: false, audit_required: false, context: input.context, executed: false } } });
  });
  await page.goto("/dashboard/capabilities/policy-simulation");
  await page.getByLabel("Capability").selectOption("capabilities-1");
  const simulate = page.getByRole("button", { name: "Simulate policy" });
  await simulate.evaluate((button) => button.scrollIntoView({ block: "center" }));
  await simulate.click({ force: true });
  await expect(page.locator(".simulation-result")).toHaveAttribute("data-decision", "ALLOW");
  await expect(page.getByText("Not executed", { exact: true })).toBeVisible();
  expect(simulations).toBe(1);
});

test("prompt management requires developer mode, validation, diff review, and fresh mutation", async ({ page }) => {
  let saves = 0;
  await page.route("**/api/llm/prompts", (route) => route.fulfill({ json: { prompts: [{ prompt_id: "chat.system", version: "1.0.0", editable: true, protected: false, hash: "abc" }] } }));
  await page.route("**/api/llm/prompts/chat.system/versions", (route) => route.fulfill({ json: { prompt_id: "chat.system", versions: [] } }));
  await page.route("**/api/llm/prompts/chat.system", async (route) => {
    if (route.request().method() === "PUT") { saves += 1; await route.fulfill({ json: { success: true } }); return; }
    await route.fulfill({ json: { prompt_id: "chat.system", template: "System {{user_name}}", version: "1.0.0", editable: true, protected: false, hash: "abc" } });
  });
  await page.route("**/api/llm/regression-test", (route) => route.fulfill({ json: { all_valid: true, candidate: { valid: true, errors: [], required_variables: ["user_name"] } } }));
  await page.goto("/dashboard/intelligence/models-prompts");
  await expect(page.getByText("Enable Developer Mode in the top bar")).toBeVisible();
  await page.getByTitle("Developer mode").click();
  await page.getByLabel("Candidate template").fill("Revised system {{user_name}}");
  await page.getByRole("button", { name: "Validate candidate" }).click({ force: true });
  await page.getByRole("button", { name: "Review diff" }).click({ force: true });
  await expect(page.getByText(/added.*removed.*unchanged/)).toBeVisible();
  await page.getByRole("button", { name: "Save tested revision" }).click({ force: true });
  await expect.poll(() => saves).toBe(1);
});

test("attention unifies approvals, errors, and offline servers", async ({ page }) => {
  await page.goto("/dashboard/attention");
  await expect(page.getByRole("heading", { name: "Needs Attention", level: 1 })).toBeVisible();
  await expect(page.getByText("No items currently need attention.")).toBeVisible();
});

test("all management domains remain usable at production display sizes", async ({ page }, testInfo) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const routes = [
    ["home", "/dashboard"],
    ["work", "/dashboard/work/tasks"],
    ["work", "/dashboard/open-loops"],
    ["systems", "/dashboard/capabilities/catalog"],
    ["systems", "/dashboard/infrastructure/servers"],
    ["communications", "/dashboard/communications/conversations"],
    ["home", "/dashboard/attention"],
    ["administration", "/dashboard/observability/activity"],
    ["administration", "/settings/autonomy"],
  ] as const;
  for (const size of [{ width: 1366, height: 768 }, { width: 1920, height: 1080 }, { width: 2560, height: 1440 }]) {
    await page.setViewportSize(size);
    for (const [domain, path] of routes) {
      await page.goto(path);
      await expect(page.locator(".master-shell")).toHaveAttribute("data-domain", domain);
      const overflow = await page.evaluate(() => ({
        horizontal: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        content: Math.max(0, ...[...document.querySelectorAll<HTMLElement>(".master-content *:not(.cognitive-field__accessible-summary)")].map((node) => node.scrollWidth - node.clientWidth)),
        offenders: [...document.querySelectorAll<HTMLElement>(".master-content *:not(.cognitive-field__accessible-summary)")]
          .map((node) => ({ name: `${node.tagName.toLowerCase()}.${node.className}`, overflow: node.scrollWidth - node.clientWidth }))
          .filter((item) => item.overflow > 8).sort((left, right) => right.overflow - left.overflow).slice(0, 4),
      }));
      expect(overflow.horizontal, `${domain} page viewport overflow at ${size.width}`).toBeLessThanOrEqual(2);
      expect(overflow.content, `${domain} component overflow at ${size.width}: ${JSON.stringify(overflow.offenders)}`).toBeLessThanOrEqual(8);
      await testInfo.attach(`${domain}-${size.width}x${size.height}`, { body: await page.screenshot(), contentType: "image/png" });
    }
  }
});

test("primary dashboard has no serious accessibility violations", async ({ page }) => {
  await page.goto("/dashboard");
  const results = await new AxeBuilder({ page }).disableRules(["color-contrast"]).analyze();
  expect(results.violations.filter((item) => ["critical", "serious"].includes(item.impact || ""))).toEqual([]);
});

function entity(resource: string) {
  return {
    id: `${resource}-1`, type: resource === "capabilities" ? "capability" : resource,
    title: resource === "capabilities" ? "Manager-backed capability" : `Manager-backed ${resource}`,
    subtitle: "Runtime Manager", status: "online", updated_at: "2026-07-17T00:00:00.000Z",
    badges: ["live"], related_ids: ["task-1"], detail: { source: "runtime" }
  };
}

function envelope<T>(data: T) { return { generated_at: Date.now(), source_updated_at: Date.now(), status: "ok", stale: false, error: "", data }; }

function overview() {
  return {
    schema_version: "ui-overview.v3", generated_at: 1_768_435_200_000,
    core: envelope({ health: "ONLINE", mode: "IDLE", active_goal: "Complete AEGIS", confidence: "high" }),
    connection: envelope({ quality: "online" }), display_scene: envelope({ phase: "Idle", privacy_mode: false, offline: false, stale: false }),
    tasks: envelope({ active: [], waiting: [], scheduled: [], recent: [] }),
    current_task: envelope({ task_id: "", title: "No active task", phase: "IDLE", current_action: "Observing", next_action: "Wait", blocked_reason: "" }),
    attention: envelope({ items: [], count: 0 }), servers: envelope({ items: [{ server_id: "ai-server", status: "online" }] }),
    approvals: envelope({ pending: [], pending_count: 0 }), notifications: envelope({ recent: [], unread_count: 0 }), commitments: envelope({ items: [] }),
    user_state: envelope({}), mind_summary: envelope({}), usage: envelope({}), freshness: envelope({}),
    activity: envelope({ recent: [], groups: [], count: 0 }), memory: envelope({}), capabilities: envelope({}), user_situation: envelope({}),
    presentation_events: envelope({ items: [], count: 0 }), surface_roles: envelope({ items: [], count: 0 }), display_queue: envelope({ items: [], count: 0 }),
    presentations: envelope({ items: [], count: 0 }), errors: envelope({ items: [], count: 0 })
  };
}
