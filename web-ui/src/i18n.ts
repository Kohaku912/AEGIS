export const messages = {
  appSubtitle: "Personal AI Control Center",
  developerMode: "Developer mode",
  updated: "Last updated",
  retry: "Retry",
  loading: "Loading",
  noData: "No data to display",
  search: "Search",
  status: "Status",
  all: "All",
  saveView: "Save current view",
  previous: "Previous",
  next: "Next",
  cancel: "Cancel",
  confirm: "Confirm and run",
  savedViews: "Saved views",
  currentFilters: "Current filters",
  deleteSavedView: "Delete saved view",
} as const;

export type MessageKey = keyof typeof messages;

export function formatDateTime(value: number | string | undefined): string {
  if (!value) return "Unavailable";
  const parsed = typeof value === "number" ? value : Date.parse(value);
  return Number.isFinite(parsed)
    ? new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "medium", timeZone: "Asia/Tokyo" }).format(parsed)
    : "Unavailable";
}

export function formatRelative(value: number | string | undefined, now = Date.now()): string {
  if (!value) return "";
  const parsed = typeof value === "number" ? value : Date.parse(value);
  const seconds = Math.max(0, Math.round((now - parsed) / 1000));
  if (seconds < 60) return `${seconds} seconds ago`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} minutes ago`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)} hours ago`;
  return `${Math.round(seconds / 86400)} days ago`;
}
