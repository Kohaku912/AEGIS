import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { searchResourcesDetailed } from "../api/client";
import { searchEntities } from "../entityModel";
import type { EntitySummary } from "../types";

export function GlobalSearch({ entities, onSelect }: { entities: EntitySummary[]; onSelect: (entity: EntitySummary) => void }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [remote, setRemote] = useState<EntitySummary[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [warnings, setWarnings] = useState<string[]>([]);
  useEffect(() => {
    if (query.trim().length < 2) { setRemote([]); setSearching(false); return; }
    let active = true;
    setSearching(true);
    const timer = window.setTimeout(() => {
      searchResourcesDetailed(query).then((result) => { if (active) { setRemote(result.items); setWarnings(result.warnings.map((item) => `${item.resource || "データ源"}: ${item.message}`)); setError(""); } }).catch((reason) => { if (active) { setError(reason instanceof Error ? reason.message : String(reason)); } }).finally(() => { if (active) setSearching(false); });
    }, 180);
    return () => { active = false; window.clearTimeout(timer); };
  }, [query]);
  const results = useMemo(() => {
    const combined = new Map<string, EntitySummary>();
    for (const item of [...searchEntities(entities, query), ...remote]) combined.set(`${item.type}:${item.id}`, item);
    return [...combined.values()].slice(0, 40);
  }, [entities, query, remote]);
  return (
    <div className="global-search" data-open={open}>
      <Search size={16} aria-hidden="true" />
      <input
        aria-label="AEGIS全体を検索"
        placeholder="タスク、記憶、機能、端末を検索…"
        value={query}
        onChange={(event) => { setQuery(event.currentTarget.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onKeyDown={(event) => { if (event.key === "Escape") setOpen(false); }}
      />
      {open && query ? (
        <div className="global-search__results" role="listbox">
          {results.map((item) => (
            <button key={`${item.type}:${item.id}`} type="button" onClick={() => { onSelect(item); setOpen(false); }}>
              <span data-domain={item.type}>{item.type}</span>
              <strong>{item.title}</strong>
              <small>{item.status}</small>
            </button>
          ))}
          {searching ? <p>検索中…</p> : null}
          {error ? <p role="alert">検索APIエラー: {error}</p> : null}
          {warnings.length ? <p role="status">一部検索失敗: {warnings.join(" / ")}</p> : null}
          {!results.length && !error ? <p>一致する項目はありません。</p> : null}
        </div>
      ) : null}
    </div>
  );
}
