import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  fetchIrreversibilityLedger,
  fetchIrreversibleOccurrences,
  type IrreversibilityLedger,
  type IrreversibleOccurrences,
} from "../api/client";
import { DataState, PageHeader, Pagination, ResponsiveDataView } from "../components/DashboardPrimitives";
import { formatDateTime } from "../i18n";

const THRESHOLDS = ["recoverable", "difficult", "irreversible"] as const;
const PAGE_SIZE = 50;

const EMPTY_LEDGER: IrreversibilityLedger = {
  totalCapabilities: 0,
  threshold: "difficult",
  includeUnknown: true,
  byReversibility: {},
  byOwnershipScope: {},
  byBlastRadius: {},
  byDataLossRisk: {},
  byDestructiveEffect: {},
  irreversible: [],
  declaresUnknown: [],
  reportable: [],
};

const EMPTY_OCCURRENCES: IrreversibleOccurrences = {
  entries: [],
  total: 0,
  scanned: 0,
  threshold: "difficult",
  watchedCapabilities: 0,
};

/** `destructive_effects` arrives as a list; `["unknown"]` means "not declared". */
function effectList(value: unknown): string {
  if (Array.isArray(value)) {
    return value.length ? value.map(String).join(", ") : "none";
  }
  const text = String(value ?? "").trim();
  return text || "unknown";
}

function Tally({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts);
  if (!entries.length) return null;
  return <div className="mini-panel">
    <h3>{title}</h3>
    <div className="metric-list">
      {entries.map(([label, count]) => <div className="metric-row" key={label}>
        <span>{label}</span>
        <strong>{count}</strong>
      </div>)}
    </div>
  </div>;
}

export function IrreversibilityPage() {
  const [threshold, setThreshold] = useState<string>("difficult");
  const [includeUnknown, setIncludeUnknown] = useState(true);
  const [ledger, setLedger] = useState<IrreversibilityLedger>(EMPTY_LEDGER);
  const [occurrences, setOccurrences] = useState<IrreversibleOccurrences>(EMPTY_OCCURRENCES);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextLedger, nextOccurrences] = await Promise.all([
        fetchIrreversibilityLedger(threshold, includeUnknown),
        fetchIrreversibleOccurrences(threshold, includeUnknown, page, PAGE_SIZE),
      ]);
      setLedger(nextLedger);
      setOccurrences(nextOccurrences);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [threshold, includeUnknown, page]);

  useEffect(() => {
    void load();
  }, [load, reload]);

  const capabilityRows = ledger.reportable.map((entry, index) => {
    const id = String(entry.capability_id || `irreversible-${index}`);
    const reversibility = String(entry.reversibility || "unknown");
    const blast = String(entry.blast_radius || "unknown");
    const effects = effectList(entry.destructive_effects);
    const scope = String(entry.ownership_scope || "unknown");
    return {
      id,
      cells: [id, reversibility, blast, effects, scope],
      card: <div className="log-card">
        <strong>{id}</strong>
        <p>{reversibility} · blast radius {blast}</p>
        <p>{effects}</p>
        <small>scope {scope}</small>
      </div>,
    };
  });

  const occurrenceRows = occurrences.entries.map((entry, index) => {
    const id = String(entry.entry_id || `occurrence-${index}`);
    const capability = String(entry.capability_id || "unknown");
    const decision = String(entry.decision || "unknown");
    const reversibility = String(entry.reversibility || "unknown");
    const effects = effectList(entry.destructive_effects);
    const at = Number(entry.timestamp_ms || 0);
    return {
      id,
      cells: [formatDateTime(at), capability, decision, reversibility, effects],
      card: <div className="log-card">
        <strong>{capability}</strong>
        <p>{decision} · {reversibility}</p>
        <p>{effects}</p>
        <small>{formatDateTime(at)}</small>
      </div>,
    };
  });

  const hasLedger = ledger.totalCapabilities > 0;

  return <div className="grid">
    <PageHeader
      title="Irreversibility ledger"
      description="What AEGIS cannot take back, enumerated from the capability manifests rather than maintained by hand. The forced approval gate is gone; this is the visibility that replaced it."
    >
      <div className="filter-bar">
        {THRESHOLDS.map((level) => <button
          key={level}
          type="button"
          className={level === threshold ? "primary-button" : "ghost-button"}
          aria-pressed={level === threshold}
          onClick={() => { setThreshold(level); setPage(1); }}
        >{level}</button>)}
        <label>
          <input
            type="checkbox"
            checked={includeUnknown}
            onChange={(event) => { setIncludeUnknown(event.target.checked); setPage(1); }}
          />
          Include undeclared
        </label>
        <button type="button" className="ghost-button" onClick={() => setReload((value) => value + 1)} disabled={loading}>
          <RefreshCw size={14} aria-hidden="true" />Refresh
        </button>
      </div>
    </PageHeader>

    <DataState
      loading={loading}
      error={error}
      empty={!loading && !error && !hasLedger}
      onRetry={() => setReload((value) => value + 1)}
    />

    {!loading && !error && hasLedger ? <section className="panel">
      <h3>Inventory</h3>
      <div className="stat-grid">
        <div className="stat">
          <span className="muted">Capabilities classified</span>
          <b>{ledger.totalCapabilities}</b>
        </div>
        <div className="stat">
          <span className="muted">At or above {ledger.threshold}</span>
          <b>{ledger.reportable.length}</b>
        </div>
        <div className="stat">
          <span className="muted">Irreversible</span>
          <b>{ledger.irreversible.length}</b>
        </div>
        <div className="stat">
          <span className="muted">Declaring unknown</span>
          <b>{ledger.declaresUnknown.length}</b>
        </div>
      </div>
      <p className="muted">
        {ledger.includeUnknown
          ? "Undeclared dimensions are counted as unknown rather than assumed harmless."
          : "Only capabilities with a declared severity are counted."}
      </p>
      {ledger.irreversible.length ? <p className="muted">
        Cannot be undone: {ledger.irreversible.join(", ")}
      </p> : null}
      {ledger.declaresUnknown.length ? <p className="muted">
        Declares an unknown dimension: {ledger.declaresUnknown.join(", ")}
      </p> : null}
    </section> : null}

    {!loading && !error && hasLedger ? <div className="stat-grid">
      <Tally title="By reversibility" counts={ledger.byReversibility} />
      <Tally title="By destructive effect" counts={ledger.byDestructiveEffect} />
      <Tally title="By blast radius" counts={ledger.byBlastRadius} />
      <Tally title="By data loss risk" counts={ledger.byDataLossRisk} />
    </div> : null}

    {!loading && !error && capabilityRows.length ? <section className="panel">
      <h3>Capabilities worth watching</h3>
      <ResponsiveDataView
        headers={["Capability", "Reversibility", "Blast radius", "Destructive effects", "Ownership scope"]}
        rows={capabilityRows}
      />
    </section> : null}

    {!loading && !error && hasLedger ? <section className="panel">
      <h3>What actually ran</h3>
      <p className="muted">
        {occurrences.total} irreversible action(s) in the scanned audit window
        ({occurrences.scanned} entries scanned, {occurrences.watchedCapabilities} capabilities watched).
      </p>
      {occurrenceRows.length ? <ResponsiveDataView
        headers={["Time", "Capability", "Decision", "Reversibility", "Destructive effects"]}
        rows={occurrenceRows}
      /> : <p className="empty-copy">Nothing irreversible has been recorded yet.</p>}
      <Pagination page={page} total={occurrences.total} pageSize={PAGE_SIZE} onPage={setPage} />
    </section> : null}
  </div>;
}
