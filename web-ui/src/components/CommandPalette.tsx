import { Command, Search, ShieldCheck, Workflow, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const commands = [
  { id: "create-task", label: "新しいタスクを作成", group: "仕事", icon: Workflow, path: "/dashboard/work/tasks?create=1" },
  { id: "attention", label: "対応が必要な項目を確認", group: "ホーム", icon: ShieldCheck, path: "/dashboard/attention" },
  { id: "approvals", label: "承認待ちを確認", group: "ホーム", icon: ShieldCheck, path: "/dashboard/attention" },
  { id: "failed-capabilities", label: "問題のある機能を表示", group: "システム", icon: Search, path: "/dashboard/capabilities/catalog?status=failing" },
  { id: "memory", label: "記憶を検索", group: "設定・管理", icon: Search, path: "/dashboard/intelligence/memory" },
  { id: "readiness", label: "本番準備状況を表示", group: "設定・管理", icon: Command, path: "/dashboard/observability/reports" }
];

export function CommandPalette({ open, onOpenChange, navigate }: { open: boolean; onOpenChange: (open: boolean) => void; navigate: (path: string) => void }) {
  const [query, setQuery] = useState("");
  useEffect(() => {
    if (!open) { setQuery(""); return; }
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") onOpenChange(false); };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onOpenChange, open]);
  const results = useMemo(() => commands.filter((item) => `${item.label} ${item.group}`.toLowerCase().includes(query.toLowerCase())), [query]);
  if (!open) return null;
  return (
    <div className="palette-backdrop" role="presentation" onMouseDown={() => onOpenChange(false)}>
      <section className="command-palette" role="dialog" aria-modal="true" aria-label="コマンドパレット" onMouseDown={(event) => event.stopPropagation()}>
        <header><Command size={18} /><input autoFocus aria-label="コマンドを検索" value={query} onChange={(event) => setQuery(event.currentTarget.value)} placeholder="コマンドを入力…" /><button className="icon-button" aria-label="閉じる" type="button" onClick={() => onOpenChange(false)}><X size={16} /></button></header>
        <div className="command-palette__list">
          {results.map((item) => { const Icon = item.icon; return <button key={item.id} type="button" onClick={() => { navigate(item.path); onOpenChange(false); }}><Icon size={16} /><span><strong>{item.label}</strong><small>{item.group}</small></span></button>; })}
        </div>
        <footer>危険な操作は確認画面を開き、必要に応じて承認と再認証を要求します。</footer>
      </section>
    </div>
  );
}
