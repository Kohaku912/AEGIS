import { Command, Search, ShieldCheck, Workflow, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const commands = [
  { id: "create-task", label: "Create new task", group: "Work", icon: Workflow, path: "/dashboard/work/tasks?create=1" },
  { id: "attention", label: "Review attention", group: "Command", icon: ShieldCheck, path: "/dashboard/attention" },
  { id: "approvals", label: "Review pending approvals", group: "Governance", icon: ShieldCheck, path: "/dashboard/governance/approvals" },
  { id: "failed-capabilities", label: "Show failing capabilities", group: "Capabilities", icon: Search, path: "/dashboard/capabilities/catalog?status=failing" },
  { id: "memory", label: "Search memory", group: "Intelligence", icon: Search, path: "/dashboard/intelligence/memory" },
  { id: "readiness", label: "Open production readiness", group: "Observability", icon: Command, path: "/dashboard/observability/reports" }
];

export function CommandPalette({ open, onOpenChange, navigate }: { open: boolean; onOpenChange: (open: boolean) => void; navigate: (path: string) => void }) {
  const [query, setQuery] = useState("");
  useEffect(() => { if (!open) setQuery(""); }, [open]);
  const results = useMemo(() => commands.filter((item) => `${item.label} ${item.group}`.toLowerCase().includes(query.toLowerCase())), [query]);
  if (!open) return null;
  return (
    <div className="palette-backdrop" role="presentation" onMouseDown={() => onOpenChange(false)}>
      <section className="command-palette" role="dialog" aria-modal="true" aria-label="Command palette" onMouseDown={(event) => event.stopPropagation()}>
        <header><Command size={18} /><input autoFocus value={query} onChange={(event) => setQuery(event.currentTarget.value)} placeholder="Type a command or resource..." /><button className="icon-button" type="button" onClick={() => onOpenChange(false)}><X size={16} /></button></header>
        <div className="command-palette__list">
          {results.map((item) => { const Icon = item.icon; return <button key={item.id} type="button" onClick={() => { navigate(item.path); onOpenChange(false); }}><Icon size={16} /><span><strong>{item.label}</strong><small>{item.group}</small></span></button>; })}
        </div>
        <footer>Dangerous commands open a review surface and require approval plus fresh passkey authentication.</footer>
      </section>
    </div>
  );
}
