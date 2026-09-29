import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { InterruptionPage } from "./InterruptionPage";

const held = {
  notification: { notification_id: "notif-1", title: "Meeting in 10 minutes", body: "Standup starts at 10:00." },
  decision: { decision: "batch_later", reason: "User attention is occupied: focused." },
  batched_at: Date.now(),
};

const status = { emergency_stop: false, batched_count: 1, batched: [held] };

function json(body: unknown) {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}

type Call = { url: string; method: string; body: unknown };

function mockApi(overrides: { status?: unknown; afterStop?: unknown; flush?: unknown } = {}) {
  const calls: Call[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    calls.push({ url, method: String(init?.method || "GET"), body: init?.body });
    if (url.startsWith("/auth/me")) return json({ csrf_token: "test-csrf" });
    // The specific routes must be matched before the `/api/interruption` prefix.
    if (url.startsWith("/api/interruption/emergency-stop")) {
      return json(overrides.afterStop ?? { ...status, emergency_stop: true });
    }
    if (url.startsWith("/api/interruption/flush")) return json(overrides.flush ?? { items: [held] });
    if (url.startsWith("/api/interruption")) return json(overrides.status ?? status);
    throw new Error(`unexpected request: ${url}`);
  });
  return calls;
}

describe("interruption page", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("shows whether AEGIS may speak and what it is holding back", async () => {
    mockApi();

    render(<InterruptionPage />);

    await waitFor(() => expect(screen.getAllByText("Allowed").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Meeting in 10 minutes").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/User attention is occupied/).length).toBeGreaterThan(0);
  });

  it("releases the held notifications through the flush endpoint", async () => {
    const calls = mockApi();

    render(<InterruptionPage />);

    fireEvent.click(await screen.findByRole("button", { name: /Release now/ }));

    await waitFor(() => expect(screen.getAllByText("Released in this session").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Standup starts at 10:00.").length).toBeGreaterThan(0);
    const flush = calls.find((call) => call.url.startsWith("/api/interruption/flush"));
    expect(flush?.method).toBe("POST");
  });

  it("confirms before silencing, and only then posts the change", async () => {
    const calls = mockApi();

    render(<InterruptionPage />);

    fireEvent.click(await screen.findByRole("button", { name: /Silence everything/ }));

    // The dialog is a guard, not a formality: nothing may be sent until it is confirmed.
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(calls.some((call) => call.url.includes("emergency-stop"))).toBe(false);

    fireEvent.click(screen.getByRole("button", { name: /Confirm and run/ }));

    await waitFor(() => expect(screen.getAllByText("Silenced").length).toBeGreaterThan(0));
    const stop = calls.find((call) => call.url.includes("emergency-stop"));
    expect(stop?.method).toBe("POST");
    expect(JSON.parse(String(stop?.body))).toEqual({ active: true });
  });

  it("lets the user start listening again without a confirmation", async () => {
    const calls = mockApi({ status: { ...status, emergency_stop: true } });

    render(<InterruptionPage />);

    fireEvent.click(await screen.findByRole("button", { name: /Allow again/ }));

    await waitFor(() => expect(calls.some((call) => call.url.includes("emergency-stop"))).toBe(true));
    const stop = calls.find((call) => call.url.includes("emergency-stop"));
    expect(JSON.parse(String(stop?.body))).toEqual({ active: false });
    // Un-silencing is the safe direction, so it must not be gated behind a dialog.
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("surfaces a failed load instead of claiming nothing is held", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("nope", { status: 500 }));

    render(<InterruptionPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not load the interruption state/i);
    expect(screen.queryByText("Held back")).not.toBeInTheDocument();
  });
});
