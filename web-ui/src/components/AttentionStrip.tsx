import { AlertTriangle, Bell, ShieldAlert, WifiOff } from "lucide-react";
import type { AttentionItem } from "../types";

type Props = {
  items: AttentionItem[];
};

export function AttentionStrip({ items }: Props) {
  if (!items.length) {
    return (
      <section className="attention-strip" aria-label="Attention">
        <div className="attention-item" data-severity="normal">
          <div>
            <strong>No immediate attention required</strong>
            <div className="muted">All current UI signals are within normal bounds.</div>
          </div>
          <Bell size={18} aria-hidden="true" />
        </div>
      </section>
    );
  }
  return (
    <section className="attention-strip" aria-label="Attention">
      {items.slice(0, 6).map((item) => {
        const Icon = item.kind === "approval" ? ShieldAlert : item.kind === "server" ? WifiOff : AlertTriangle;
        return (
          <article className="attention-item" data-severity={item.severity} key={item.id}>
            <div>
              <strong>{item.title}</strong>
              <div className="muted">{item.message || item.recovery_hint || "Review this item."}</div>
            </div>
            <Icon size={20} aria-label={item.severity} />
          </article>
        );
      })}
    </section>
  );
}
