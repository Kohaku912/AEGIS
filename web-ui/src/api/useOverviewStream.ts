import { useEffect } from "react";
import type { UiEvent } from "../types";
import { displayReadQuery } from "./client";

type StreamSurface = "dashboard" | "display";

export function useOverviewStream(onEvent: (event: UiEvent) => void, enabled = true, surface: StreamSurface = "dashboard"): void {
  useEffect(() => {
    if (!enabled || typeof EventSource === "undefined") return;
    const displayQuery = displayReadQuery();
    const url =
      surface === "display"
        ? `/api/ui/stream?surface=display${displayQuery ? `&${displayQuery.slice(1)}` : ""}`
        : "/api/ui/stream";
    const source = new EventSource(url, { withCredentials: true });
    const handler = (event: MessageEvent<string>) => {
      try {
        onEvent(JSON.parse(event.data));
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
