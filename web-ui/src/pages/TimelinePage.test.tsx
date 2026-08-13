import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { UiOverview } from "../types";
import { TimelinePage } from "./TimelinePage";

const overview = {
  servers: { data: { items: [{ server_id: "pc-server", status: "ONLINE" }] } },
} as UiOverview;

describe("personal data timeline", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders observed timeline events separately from inferences", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({
      items: [{
        id: "pdc_1",
        timestamp_ms: Date.now(),
        source_device: "pc",
        source_sensor: "uia",
        event_type: "pc.input.typed",
        title: "chrome · printable×3",
        epistemics: "observed",
        payload: {
          keyboard_count: 3,
          keys: ["Ctrl", "L", "A"],
          mouse_buttons: ["LButton"],
          click_x: 120,
          click_y: 480,
          app_name: "chrome",
          window_title: "AGORA",
          control_name: "???????????????? Timeline ????????????",
          value: "??????????????????????????s",
        },
      }],
      total: 1,
      event_types: [
        { event_type: "pc.input.typed", count: 1 },
        { event_type: "android.ui.scrolled", count: 3 },
      ],
      source: "personal_data",
    }), { status: 200, headers: { "Content-Type": "application/json" } }));

    render(<TimelinePage overview={overview} />);
    await waitFor(() => expect(screen.getAllByText("キー入力").length).toBeGreaterThan(0));
    expect(screen.getAllByText("chrome").length).toBeGreaterThan(0);
    expect(screen.getAllByText("AGORA").length).toBeGreaterThan(0);
    expect(screen.getByText(/Ctrl \+ L \+ A/)).toBeTruthy();
    expect(screen.getByText(/LButton \(120, 480\)/)).toBeTruthy();
    expect(screen.queryByText(/\?{5,}/)).toBeNull();
    expect(screen.getAllByText("observed").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Event type")).toBeTruthy();
    expect(screen.getByText(/キー入力 \(1\)/)).toBeTruthy();
    expect((screen.getByLabelText("Page size") as HTMLSelectElement).value).toBe("50");
  });
});
