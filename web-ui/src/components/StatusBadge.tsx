import { AlertTriangle, CheckCircle2, CircleOff, PauseCircle } from "lucide-react";

type Props = {
  status: string;
  detail?: string;
};

export function StatusBadge({ status, detail }: Props) {
  const normalized = (status || "UNKNOWN").toUpperCase();
  const Icon =
    normalized === "ONLINE" ? CheckCircle2 : normalized === "DISABLED" || normalized === "UNCONFIGURED" ? PauseCircle : normalized === "OFFLINE" ? CircleOff : AlertTriangle;
  return (
    <span className="status-badge" data-status={normalized} title={detail || normalized}>
      <Icon size={14} aria-hidden="true" />
      {normalized}
    </span>
  );
}
