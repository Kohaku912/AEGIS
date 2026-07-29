import type { UiEvent } from "./types";

/** Device/status telemetry that is not an AEGIS operation. */
export function isUiActivityNoise(event: Pick<UiEvent, "event_type" | "source_type" | "type" | "safe_title" | "safe_message" | "message" | "status" | "server_id"> & Record<string, unknown>): boolean {
  const eventType = String(event.event_type || event.source_type || event.type || "").toLowerCase();
  const title = String(event.safe_title || event.title || event.safe_message || event.message || "").toLowerCase();
  const haystack = `${eventType} ${title} ${String(event.status || "").toLowerCase()}`;

  if (eventType === "android.approval.decided" || eventType === "android.approval.decision" || eventType === "android.chat") {
    return false;
  }
  if (eventType.startsWith("android.")) return true;
  if (String(event.server_id || "") === "android-server" && !event.task_id && !event.approval_id && !event.capability_id) {
    return true;
  }
  return ["heartbeat", "telemetry", "user_activity", "foreground_app", "current_app", "activitychange", "activity_change", "activity changed"].some(
    (token) => haystack.includes(token)
  );
}
