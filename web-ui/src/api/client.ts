import type { UiOverview } from "../types";

export async function fetchOverview(surface: "dashboard" | "display" = "dashboard"): Promise<UiOverview> {
  const endpoint = surface === "display" ? "/display/overview" : "/api/ui/overview";
  const response = await fetch(endpoint, { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Overview request failed: ${response.status}`);
  }
  return response.json();
}

export async function sendChat(message: string): Promise<Record<string, unknown>> {
  const response = await fetch("/api/chat/send", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }
  return response.json();
}

export async function resolveApproval(approvalId: string, decision: "approve" | "reject"): Promise<void> {
  const endpoint = decision === "approve" ? "approve" : "reject";
  const response = await fetch(`/api/approvals/${approvalId}/${endpoint}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  });
  if (!response.ok) {
    throw new Error(`Approval ${decision} failed: ${response.status}`);
  }
}
