import { AlertTriangle, LockKeyhole, RefreshCw, ShieldAlert } from "lucide-react";

type StateKind = "loading" | "empty" | "stale" | "permission" | "unauthorized" | "fresh-auth" | "error" | "partial" | "disconnected";

type Props = {
  kind: StateKind;
  title: string;
  message: string;
  actionLabel?: string;
  actionHref?: string;
};

const icons = {
  loading: RefreshCw,
  empty: AlertTriangle,
  stale: AlertTriangle,
  permission: ShieldAlert,
  unauthorized: LockKeyhole,
  "fresh-auth": LockKeyhole,
  error: AlertTriangle,
  partial: AlertTriangle,
  disconnected: AlertTriangle,
};

export function UiState({ kind, title, message, actionLabel, actionHref }: Props) {
  const Icon = icons[kind];
  return (
    <section className="ui-state" data-kind={kind}>
      <Icon size={20} aria-hidden="true" />
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
      </div>
      {actionLabel && actionHref ? <a className="ghost-button" href={actionHref}>{actionLabel}</a> : null}
    </section>
  );
}

export function SectionState({ stale, error, empty, label }: { stale?: boolean; error?: string; empty?: boolean; label: string }) {
  if (error) return <UiState kind="error" title={`${label} unavailable`} message={error} />;
  if (stale) return <UiState kind="stale" title={`${label} is stale`} message="Showing the last known value while AEGIS waits for a fresh update." />;
  if (empty) return <UiState kind="empty" title={`No ${label.toLowerCase()} reported`} message="AEGIS has no current data for this section." />;
  return null;
}
