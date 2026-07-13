import type { UiOverview } from "../types";

export async function fetchOverview(surface: "dashboard" | "display" = "dashboard"): Promise<UiOverview> {
  const endpoint = surface === "display" ? `/display/overview${displayReadQuery()}` : "/api/ui/overview";
  const response = await fetch(endpoint, { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Overview request failed: ${response.status}`);
  }
  return response.json();
}

export function displayReadQuery(): string {
  if (typeof window === "undefined") return "";
  const token = new URLSearchParams(window.location.search).get("display_token");
  return token ? `?display_token=${encodeURIComponent(token)}` : "";
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

export async function fetchAuthMe(): Promise<Record<string, unknown>> {
  const response = await fetch("/auth/me", { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Auth session request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchSettings(): Promise<Record<string, unknown>> {
  const response = await fetch("/api/settings", { credentials: "include" });
  if (!response.ok) {
    throw new Error(`Settings request failed: ${response.status}`);
  }
  return response.json();
}

export async function updateSetting(section: string, key: string, value: unknown): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/settings", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ section, key, value })
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = String(payload.error || (Array.isArray(payload.errors) ? payload.errors.join(", ") : "") || response.status);
    throw new Error(message);
  }
  return payload;
}

export async function resetSettings(): Promise<Record<string, unknown>> {
  const csrf = String((await fetchAuthMe()).csrf_token || "");
  const response = await fetch("/api/settings/reset", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRF-Token": csrf }
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(String(payload.error || response.status));
  }
  return payload;
}
