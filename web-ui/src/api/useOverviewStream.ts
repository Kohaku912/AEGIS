import { useEffect } from "react";
import type { UiEvent } from "../types";

export function useOverviewStream(onEvent: (event: UiEvent) => void, enabled = true): void {
  useEffect(() => {
    if (!enabled || typeof EventSource === "undefined") return;
    const source = new EventSource("/api/ui/stream", { withCredentials: true });
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
  }, [enabled, onEvent]);
}
