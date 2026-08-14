import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChatDrawer } from "./ChatDrawer";

vi.mock("../api/client", () => ({
  createRequestId: () => "req-1",
  fetchChatHistory: vi.fn(async () => [{ user: "hello", bot: "hi there" }]),
  fetchAuthMe: vi.fn(async () => ({ csrf_token: "csrf" })),
  sendChat: vi.fn(),
  respondChat: vi.fn(),
}));

describe("ChatDrawer", () => {
  it("loads persisted history when opened", async () => {
    render(<ChatDrawer open onClose={() => undefined} />);
    await waitFor(() => {
      expect(screen.getByText("hello")).toBeInTheDocument();
      expect(screen.getByText("hi there")).toBeInTheDocument();
    });
  });
});
