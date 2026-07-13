import { useEffect } from "react";
import type { UiEvent } from "../types";
import { displayReadQuery } from "./client";

type StreamSurface = "dashboard" | "display";

const lastEventIdBySurface: Partial<Record<StreamSurface, string>> = {};

export function useOverviewStream(onEvent: (event: UiEvent) => void, enabled = true, surface: StreamSurface = "dashboard"): void {
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
    const handler = (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data) as UiEvent;
        const streamEventId = event.lastEventId || payload.event_id || "";
        if (streamEventId) {
          lastEventIdBySurface[surface] = streamEventId;
          writeStoredLastEventId(surface, streamEventId);
        }
        onEvent(payload);
      } catch {
        // Ignore malformed stream frames; the next snapshot will recover state.
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
    return () => source.close();
  }, [enabled, onEvent, surface]);
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
