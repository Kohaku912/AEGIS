import { Command, Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { allPages } from "../navigation";
import { searchResourcesDetailed, type ApiWarning } from "../api/client";
import type { EntitySummary, UiOverview } from "../types";

type PaletteItem = {
  id: string;
  label: string;
  group: string;
  description?: string;
  path?: string;
  entity?: EntitySummary;
};

export function CommandPalette({
  open,
  onOpenChange,
  navigate,
  onSelectEntity,
  overview,
  pinnedEntities = [],
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  navigate: (path: string) => void;
  onSelectEntity?: (entity: EntitySummary) => void;
  overview: UiOverview;
  pinnedEntities?: EntitySummary[];
}) {
  const [query, setQuery] = useState("");
  const [remote, setRemote] = useState<EntitySummary[]>([]);
  const [warnings, setWarnings] = useState<ApiWarning[]>([]);
  const quickJumps = useMemo<PaletteItem[]>(
    () => [
      {
        id: "jump:focus",
        label: String(overview.cockpit_focus?.data.title || overview.current_task.data.title || "Current focus"),
        description: String(overview.cockpit_focus?.data.message || overview.current_task.data.current_action || "Open current focus"),
        group: "Quick jump",
        path: String(overview.cockpit_focus?.data.path || overview.cockpit_investigation?.data.focus_path || "/dashboard/execution-trace"),
      },
      {
        id: "jump:interventions",
        label: "Interventions",
        description: `${String(overview.cockpit_inbox?.data.count || 0)} item(s) need review`,
        group: "Quick jump",
        path: "/dashboard/interventions",
      },
      {
        id: "jump:layers",
        label: "Layer comparison",
        description: "Compare L1 / L2 / L3",
        group: "Quick jump",
        path: "/dashboard/layers",
      },
    ],
    [overview],
  );
  const pageItems = useMemo<PaletteItem[]>(
    () =>
      allPages().map((page) => ({
        id: `page:${page.id}`,
        label: page.label,
        group: "ページ",
        description: page.path,
        path: page.path,
      })),
    [],
  );
  const pinnedItems = useMemo<PaletteItem[]>(
    () =>
      pinnedEntities.map((entity) => ({
        id: `pin:${entity.type}:${entity.id}`,
        label: entity.title || entity.id,
        description: entity.subtitle || entity.status,
        group: "Pinned",
        entity,
      })),
    [pinnedEntities],
  );

  useEffect(() => {
    if (!open) {
      setQuery("");
      setRemote([]);
      setWarnings([]);
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
      setWarnings([]);
      return;
    }
    let cancelled = false;
    const handle = window.setTimeout(() => {
      void searchResourcesDetailed(normalizeQuery(query))
        .then(({ items, warnings: nextWarnings }) => {
          if (!cancelled) {
            setRemote(items.slice(0, 20));
            setWarnings(nextWarnings);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setRemote([]);
            setWarnings([]);
          }
        });
    }, 200);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [open, query]);

  const results = useMemo(() => {
    const q = query.toLowerCase().trim();
    const local = [...quickJumps, ...pinnedItems, ...pageItems].filter(
      (item) => !q || `${item.label} ${item.group} ${item.description || ""}`.toLowerCase().includes(q),
    );
    const extras: PaletteItem[] = remote.map((entity) => ({
      id: `entity:${entity.type}:${entity.id}`,
      label: entity.title || entity.id,
      description: entity.subtitle || entity.status,
      group: entity.type,
      entity,
    }));
    return [...local.slice(0, 12), ...extras].slice(0, 24);
  }, [pageItems, pinnedItems, query, quickJumps, remote]);

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
          {!query.trim() ? (
            <p className="muted">Quick jump / page / pinned resource / `kind:error` / `approval:pending` / `session:...`</p>
          ) : null}
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
                <small>{item.group}{item.description ? ` · ${item.description}` : ""}</small>
              </span>
            </button>
          ))}
          {warnings.length ? <p className="muted">{warnings.map((warning) => warning.message).join(" / ")}</p> : null}
          {!results.length ? <p className="muted">一致する項目がありません。</p> : null}
        </div>
        <footer>Ctrl+K · 危険操作は確認ダイアログを開きます</footer>
      </section>
    </div>
  );
}

function normalizeQuery(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  const [prefix, ...rest] = trimmed.split(":");
  const body = rest.join(":").trim();
  if (!body) return trimmed;
  if (["kind", "session", "approval", "task", "tool", "cost"].includes(prefix.toLowerCase())) {
    return `${prefix}:${body}`;
  }
  return trimmed;
}
