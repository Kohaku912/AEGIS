import { AlertTriangle, CheckCircle2, CircleOff, PauseCircle } from "lucide-react";
import type { ServerStatus } from "../types";

type Props = {
  status: string;
  detail?: string;
};

export function StatusBadge({ status, detail }: Props) {
  const normalized = (status || "UNKNOWN").toUpperCase();
  const labels: Record<ServerStatus, string> = {
    ONLINE: "オンライン",
    DEGRADED: "一部機能低下",
    OFFLINE: "オフライン",
    DISABLED: "無効",
    UNCONFIGURED: "未設定",
  };
  const Icon =
    normalized === "ONLINE" ? CheckCircle2 : normalized === "DISABLED" || normalized === "UNCONFIGURED" ? PauseCircle : normalized === "OFFLINE" ? CircleOff : AlertTriangle;
  return (
    <span className="status-badge" data-status={normalized} title={detail || normalized}>
      <Icon size={14} aria-hidden="true" />
      {labels[normalized as ServerStatus] || normalized}
    </span>
  );
}
