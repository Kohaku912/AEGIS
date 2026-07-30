import { Command, Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { allPages } from "../navigation";
import { searchResources } from "../api/client";
import type { EntitySummary } from "../types";

type PaletteItem = {
  id: string;
  label: string;
  group: string;
  path?: string;
  entity?: EntitySummary;
};

export function CommandPalette({
  open,
  onOpenChange,
  navigate,
  onSelectEntity,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  navigate: (path: string) => void;
  onSelectEntity?: (entity: EntitySummary) => void;
}) {
  const [query, setQuery] = useState("");
  const [remote, setRemote] = useState<EntitySummary[]>([]);
  const pageItems = useMemo<PaletteItem[]>(
    () =>
      allPages().map((page) => ({
        id: `page:${page.id}`,
        label: page.label,
        group: "ページ",
        path: page.path,
      })),
    [],
  );

  useEffect(() => {
    if (!open) {
      setQuery("");
      setRemote([]);
      return;
    }
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") onOpenChange(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onOpenChange, open]);

  useEffect(() => {
    if (!open || query.trim().length < 2) {
      setRemote([]);
      return;
    }
    let cancelled = false;
    const handle = window.setTimeout(() => {
      void searchResources(query.trim())
        .then((items) => {
          if (!cancelled) setRemote(items.slice(0, 20));
        })
        .catch(() => {
          if (!cancelled) setRemote([]);
        });
    }, 200);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [open, query]);

  const results = useMemo(() => {
    const q = query.toLowerCase().trim();
    const local = pageItems.filter((item) => !q || `${item.label} ${item.group}`.toLowerCase().includes(q));
    const extras: PaletteItem[] = remote.map((entity) => ({
      id: `entity:${entity.type}:${entity.id}`,
      label: entity.title || entity.id,
      group: entity.type,
      entity,
    }));
    return [...local.slice(0, 12), ...extras].slice(0, 24);
  }, [pageItems, query, remote]);

  if (!open) return null;
  return (
    <div className="palette-backdrop" role="presentation" onMouseDown={() => onOpenChange(false)}>
      <section className="command-palette" role="dialog" aria-modal="true" aria-label="横断検索" onMouseDown={(event) => event.stopPropagation()}>
        <header>
          <Command size={18} />
          <input
            autoFocus
            aria-label="設定・タスク・Capability・記憶を検索"
            value={query}
            onChange={(event) => setQuery(event.currentTarget.value)}
            placeholder="ページ / タスク / Capability / 記憶 / 設定..."
          />
          <button className="icon-button" aria-label="Close" type="button" onClick={() => onOpenChange(false)}>
            <X size={16} />
          </button>
        </header>
        <div className="command-palette__list">
          {results.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                if (item.path) navigate(item.path);
                else if (item.entity && onSelectEntity) onSelectEntity(item.entity);
                onOpenChange(false);
              }}
            >
              <Search size={16} />
              <span>
                <strong>{item.label}</strong>
                <small>{item.group}</small>
              </span>
            </button>
          ))}
          {!results.length ? <p className="muted">一致する項目がありません。</p> : null}
        </div>
        <footer>Ctrl+K · 危険操作は確認ダイアログを開きます</footer>
      </section>
    </div>
  );
}
