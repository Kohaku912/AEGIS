import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { IrreversibilityPage } from "./IrreversibilityPage";

const ledger = {
  total_capabilities: 128,
  threshold: "difficult",
  include_unknown: true,
  by_reversibility: { recoverable: 40, difficult: 61, irreversible: 7, unknown: 20 },
  by_ownership_scope: { user: 100 },
  by_blast_radius: { device: 30 },
  by_data_loss_risk: { none: 90 },
  by_destructive_effect: { delete: 12 },
  irreversible: ["pc-server.file.delete"],
  declares_unknown: ["browser-server.web.navigate"],
  reportable: [{
    capability_id: "pc-server.file.delete",
    reversibility: "irreversible",
    blast_radius: "device",
    destructive_effects: ["delete"],
    ownership_scope: "user",
  }],
};

const occurrences = {
  entries: [{
    entry_id: "entry-1",
    capability_id: "pc-server.file.delete",
    decision: "ALLOW_WITH_AUDIT",
    reversibility: "irreversible",
    destructive_effects: ["delete"],
    timestamp_ms: Date.now(),
  }],
  total: 1,
  scanned: 512,
  threshold: "difficult",
  watched_capabilities: 7,
};

/** The page fires both endpoints at once; dispatch on the URL. */
function mockApi(overrides: { occurrences?: unknown } = {}) {
  const occurrenceBody = overrides.occurrences ?? occurrences;
  return vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const body = String(input).includes("/occurrences") ? occurrenceBody : ledger;
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  });
}

describe("irreversibility page", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders the inventory and the capabilities worth watching", async () => {
    mockApi();

    render(<IrreversibilityPage />);

    await waitFor(() => expect(screen.getAllByText("128").length).toBeGreaterThan(0));
    expect(screen.getAllByText("Declaring unknown").length).toBeGreaterThan(0);
    // The reportable capability appears in the table and in the "cannot be undone" summary.
    expect(screen.getAllByText(/pc-server\.file\.delete/).length).toBeGreaterThan(0);
  });

  it("renders what actually ran together with the scan window", async () => {
    mockApi();

    render(<IrreversibilityPage />);

    await waitFor(() => expect(screen.getAllByText(/irreversible action\(s\)/).length).toBeGreaterThan(0));
    expect(screen.getAllByText("ALLOW_WITH_AUDIT").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/512 entries scanned/).length).toBeGreaterThan(0);
  });

  it("asks for the undeclared dimensions only while the checkbox is on", async () => {
    const spy = mockApi();
    // Both endpoints must carry the flag. Scope each assertion to one endpoint, otherwise a
    // hardcoded value in one request is masked by the correct value in the other.
    const ledgerCalls = () => spy.mock.calls
      .map((call) => String(call[0]))
      .filter((url) => url.includes("/api/audit/irreversible?"));
    const occurrenceCalls = () => spy.mock.calls
      .map((call) => String(call[0]))
      .filter((url) => url.includes("/occurrences"));

    render(<IrreversibilityPage />);

    await waitFor(() => expect(ledgerCalls().length).toBeGreaterThan(0));
    expect(ledgerCalls()[0]).toContain("include_unknown=true");
    expect(occurrenceCalls()[0]).toContain("include_unknown=true");

    fireEvent.click(screen.getByLabelText(/Include undeclared/));

    await waitFor(() => {
      expect(ledgerCalls().some((url) => url.includes("include_unknown=false"))).toBe(true);
      expect(occurrenceCalls().some((url) => url.includes("include_unknown=false"))).toBe(true);
    });
  });

  it("says so plainly when nothing irreversible has been recorded", async () => {
    mockApi({ occurrences: { ...occurrences, entries: [], total: 0 } });

    render(<IrreversibilityPage />);

    await waitFor(() =>
      expect(screen.getAllByText("Nothing irreversible has been recorded yet.").length).toBeGreaterThan(0));
  });

  it("surfaces a failed load instead of showing an empty ledger", async () => {
    // Fail only the ledger call so the assertion does not depend on which of the two
    // parallel requests rejects first.
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      if (String(input).includes("/occurrences")) {
        return new Response(JSON.stringify(occurrences), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response("nope", { status: 500 });
    });

    render(<IrreversibilityPage />);

    // The alert carries the API's own message, so a swallowed error cannot pass this.
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not load the irreversibility ledger/i);
    // A failed request must not be reported as "no data".
    expect(screen.queryByText("Capabilities classified")).not.toBeInTheDocument();
  });
});
