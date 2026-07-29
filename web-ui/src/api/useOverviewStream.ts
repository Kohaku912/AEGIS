import { useEffect } from "react";
import type { UiEvent } from "../types";
import { displayReadQuery } from "./client";

type StreamSurface = "dashboard" | "display";

const lastEventIdBySurface: Partial<Record<StreamSurface, string>> = {};

export type StreamState = "connecting" | "online" | "reconnecting" | "offline" | "malformed";

export function useOverviewStream(onEvent: (event: UiEvent) => void, enabled = true, surface: StreamSurface = "dashboard", onState?: (state: StreamState) => void): void {
  useEffect(() => {
    if (!enabled || typeof EventSource === "undefined") return;
    const displayQuery = displayReadQuery();
    const lastEventId = lastEventIdBySurface[surface] || readStoredLastEventId(surface);
    const replayQuery = lastEventId ? `last_event_id=${encodeURIComponent(lastEventId)}` : "";
    const query = [surface === "display" ? "surface=display" : "", displayQuery ? displayQuery.slice(1) : "", replayQuery]
      .filter(Boolean)
      .join("&");
    const url =
      surface === "display"
        ? `/api/ui/stream${query ? `?${query}` : ""}`
        : `/api/ui/stream${query ? `?${query}` : ""}`;
    const source = new EventSource(url, { withCredentials: true });
    let failures = 0;
    let offlineTimer = 0;
    onState?.("connecting");
    source.onopen = () => {
      failures = 0;
      window.clearTimeout(offlineTimer);
      onState?.("online");
    };
    source.onerror = () => {
      failures += 1;
      onState?.("reconnecting");
      window.clearTimeout(offlineTimer);
      offlineTimer = window.setTimeout(() => onState?.("offline"), failures >= 3 ? 2_000 : 10_000);
    };
    const handler = (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data) as UiEvent;
        const streamEventId = event.lastEventId || payload.event_id || "";
        if (streamEventId) {
          lastEventIdBySurface[surface] = streamEventId;
          writeStoredLastEventId(surface, streamEventId);
        }
        onEvent(payload);
      } catch (error) {
        onState?.("malformed");
        console.warn("AEGIS UI stream frame was malformed; requesting snapshot recovery.", error);
      }
    };
    for (const name of [
      "status.changed",
      "task.updated",
      "tool.execution.started",
      "tool.execution.completed",
      "tool.execution.failed",
      "approval.created",
      "approval.resolved",
      "notification.created",
      "chat.updated",
      "permission.changed",
      "connection.changed",
      "activity.updated"
    ]) {
      source.addEventListener(name, handler as EventListener);
    }
    source.addEventListener("ui.snapshot", handler as EventListener);
    return () => { window.clearTimeout(offlineTimer); source.close(); };
  }, [enabled, onEvent, onState, surface]);
}

function readStoredLastEventId(surface: StreamSurface): string {
  try {
    return window.sessionStorage.getItem(storageKey(surface)) || "";
  } catch {
    return "";
  }
}

function writeStoredLastEventId(surface: StreamSurface, eventId: string): void {
  try {
    window.sessionStorage.setItem(storageKey(surface), eventId);
  } catch {
    // Storage can be unavailable in privacy contexts; EventSource's native Last-Event-ID still covers live reconnects.
  }
}

function storageKey(surface: StreamSurface): string {
  return `aegis.ui.lastEventId.${surface}`;
}
