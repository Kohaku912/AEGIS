import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { searchResources } from "../api/client";
import { searchEntities } from "../entityModel";
import type { EntitySummary } from "../types";

export function GlobalSearch({ entities, onSelect }: { entities: EntitySummary[]; onSelect: (entity: EntitySummary) => void }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [remote, setRemote] = useState<EntitySummary[]>([]);
  const [searching, setSearching] = useState(false);
  useEffect(() => {
    if (query.trim().length < 2) { setRemote([]); setSearching(false); return; }
    let active = true;
    setSearching(true);
    const timer = window.setTimeout(() => {
      searchResources(query).then((items) => { if (active) setRemote(items); }).catch(() => { if (active) setRemote([]); }).finally(() => { if (active) setSearching(false); });
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
        aria-label="Search all AEGIS resources"
        placeholder="Search tasks, memory, capabilities, devices..."
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
          {searching ? <p>Searching Manager records...</p> : null}
          {!results.length ? <p>No matching resources.</p> : null}
        </div>
      ) : null}
    </div>
  );
}
