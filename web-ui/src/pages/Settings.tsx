import { Archive, Bell, BrainCircuit, Code2, DatabaseBackup, Eye, KeyRound, Lock, MonitorCog, ServerCog, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchSettings, resetSettings, updateSetting } from "../api/client";
import { settingSections } from "../displayModel";
import type { UiOverview } from "../types";

export function Settings({ overview, sectionId }: { overview: UiOverview; sectionId?: string }) {
  const sections = settingSections(overview);
  const [settings, setSettings] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  const [staged, setStaged] = useState<Record<string, string | number | boolean>>({});
  const [resetArmed, setResetArmed] = useState(false);
  const [history, setHistory] = useState<Array<{ key: string; before: unknown; after: unknown; at: number }>>([]);
  const editable = useMemo(() => editableSettings(settings).filter((item) => !sectionId || settingMatchesSection(item, sectionId)), [settings, sectionId]);
  const selectedSection = sectionId ? sections.find((section) => section.id === sectionId) : undefined;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchSettings()
      .then((payload) => {
        if (!cancelled) setSettings(payload);
      })
      .catch((error) => {
        if (!cancelled) setStatus(error instanceof Error ? error.message : "Settings unavailable");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const save = async () => {
    const changes = Object.entries(staged);
    if (!changes.length) return;
    setStatus(`Saving ${changes.length} reviewed change${changes.length === 1 ? "" : "s"}...`);
    try {
      for (const [compoundKey, value] of changes) {
        const separator = compoundKey.indexOf(".");
        await updateSetting(compoundKey.slice(0, separator), compoundKey.slice(separator + 1), value);
      }
      setHistory((items) => [
        ...changes.map(([key, after]) => ({ key, before: editable.find((item) => `${item.section}.${item.key}` === key)?.value, after, at: Date.now() })),
        ...items
      ].slice(0, 12));
      setSettings(await fetchSettings());
      setStaged({});
      setStatus("Saved. Effective settings were updated through SettingsStore and audited.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Save failed";
      setStatus(message.includes("fresh_passkey_required") ? "Fresh passkey authentication required. Reopen login, authenticate, then retry." : message);
    }
  };

  const reset = async () => {
    if (!resetArmed) { setResetArmed(true); setStatus("Review reset: this will restore every setting to its default. Select Reset all again to continue."); return; }
    setStatus("Resetting...");
    try {
      await resetSettings();
      setSettings(await fetchSettings());
      setStaged({});
      setResetArmed(false);
      setStatus("Settings reset to defaults.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Reset failed");
    }
  };

  const icons: Record<string, typeof ShieldCheck> = {
    autonomy: SlidersHorizontal,
    permissions: ShieldCheck,
    servers: ServerCog,
    privacy: Lock,
    notifications: Bell,
    models: BrainCircuit,
    budgets: Archive,
    memory: DatabaseBackup,
    display: MonitorCog,
    developer: Code2,
    backup: Eye
  };
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>{selectedSection?.label || labelize(sectionId || "Settings")}</h2>
            <div className="muted">Dedicated configuration surface. Sensitive changes remain protected by passkey fresh auth and CSRF.</div>
          </div>
          <a className="primary-button" href="/dashboard/security/passkeys"><KeyRound size={16} /> Passkeys</a>
        </div>
        <div className="settings-grid">
          {sections.filter((section) => !sectionId || section.id === sectionId).map((section) => {
            const Icon = icons[section.id] || SlidersHorizontal;
            return (
              <article className="settings-tile" key={section.id}>
                <div className="settings-tile__icon"><Icon size={18} aria-hidden="true" /></div>
                <div>
                  <strong>{section.label}</strong>
                  <p>{section.summary}</p>
                  <span className="muted">{section.status}</span>
                </div>
              </article>
            );
          })}
        </div>
      </section>
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Effective Configuration</h2>
            <div className="muted">Loaded from SettingsStore. Changes remain drafts until reviewed and saved.</div>
          </div>
          <div className="settings-actions">
            <a className="secondary-button" href="/api/settings/export">Export</a>
            <button className="danger-button" onClick={reset} type="button">{resetArmed ? "Confirm reset all" : "Reset all"}</button>
          </div>
        </div>
        {status ? <div className="attention-item" data-severity={status.includes("required") || status.includes("failed") ? "warning" : "info"}>{status}</div> : null}
        {loading ? <div className="muted">Loading settings...</div> : null}
        <div className="settings-editor">
          {editable.map((item) => (
            <label className="settings-control" key={`${item.section}.${item.key}`}>
              <span>
                <strong>{item.label}</strong>
                <small>{item.section}.{item.key}</small>
                <small>Source: SettingsStore · Default: managed schema · Validation: typed value · Restart: {restartRequired(item) ? "required" : "not required"}</small>
              </span>
              {typeof item.value === "boolean" ? (
                <input
                  type="checkbox"
                  checked={Boolean(staged[`${item.section}.${item.key}`] ?? item.value)}
                  onChange={(event) => { const value = event.currentTarget.checked; setStaged((values) => ({ ...values, [`${item.section}.${item.key}`]: value })); }}
                />
              ) : typeof item.value === "number" ? (
                <input
                  type="number"
                  value={Number(staged[`${item.section}.${item.key}`] ?? item.value)}
                  onChange={(event) => { const value = Number(event.currentTarget.value); setStaged((values) => ({ ...values, [`${item.section}.${item.key}`]: value })); }}
                />
              ) : (
                <input
                  value={String(staged[`${item.section}.${item.key}`] ?? item.value ?? "")}
                  onChange={(event) => { const value = event.currentTarget.value; setStaged((values) => ({ ...values, [`${item.section}.${item.key}`]: value })); }}
                />
              )}
            </label>
          ))}
          {!editable.length && !loading ? <div className="muted">No simple editable settings were reported.</div> : null}
        </div>
        {Object.keys(staged).length ? (
          <section className="settings-review" aria-label="Pending settings changes">
            <header><div><strong>Review changes</strong><small>{Object.keys(staged).length} unsaved</small></div><div><button className="secondary-button" type="button" onClick={() => { setStaged({}); setStatus("Draft changes discarded."); }}>Cancel</button><button className="primary-button" type="button" onClick={() => void save()}>Save changes</button></div></header>
            {Object.entries(staged).map(([key, after]) => { const before = editable.find((item) => `${item.section}.${item.key}` === key)?.value; return <div className="settings-diff" key={key}><code>{key}</code><span>{String(before)}</span><span aria-hidden="true">→</span><strong>{String(after)}</strong></div>; })}
          </section>
        ) : null}
        {history.length ? <details className="settings-history"><summary>Recent changes in this session</summary>{history.map((item) => <div key={`${item.key}-${item.at}`}><code>{item.key}</code><span>{String(item.before)} → {String(item.after)}</span><button className="secondary-button" type="button" onClick={() => setStaged((values) => ({ ...values, [item.key]: item.before as string | number | boolean }))}>Rollback draft</button><time>{new Date(item.at).toLocaleTimeString()}</time></div>)}</details> : null}
      </section>
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Surface Roles</h2>
            <div className="muted">PresentationEvent routing contract. Each device renders the same event with its own limits.</div>
          </div>
          <span className="freshness" data-stale={overview.surface_roles?.stale || false}>{overview.surface_roles?.data.source || "surface contract"}</span>
        </div>
        <div className="surface-role-grid">
          {(overview.surface_roles?.data.items || []).map((role) => (
            <article className="surface-role" data-interactive={role.interactive} key={role.surface_id}>
              <div>
                <strong>{role.surface_id.replace(/_/g, " ")}</strong>
                <p>{role.role}</p>
              </div>
              <div className="surface-role__meta">
                <span>{role.interactive ? "interactive" : "read-only"}</span>
                <span>{role.priorities.join("/")}</span>
                <span>{role.privacy_levels.join("/")}</span>
              </div>
              <div className="surface-role__scenes">{role.scenes.slice(0, 8).join(" / ")}</div>
            </article>
          ))}
          {!(overview.surface_roles?.data.items || []).length ? <div className="muted">Surface role contract is not reported.</div> : null}
        </div>
      </section>
      <section className="panel">
        <div className="panel__header"><h2>Guardrails</h2></div>
        <div className="metric-list">
          <div className="metric-row"><span>Authentication</span><strong>Passkey-only in production</strong></div>
          <div className="metric-row"><span>Fresh auth</span><strong>Required for risk, approval, secrets, LLM, and dangerous operations</strong></div>
          <div className="metric-row"><span>Policy direction</span><strong>Settings can add restrictions; PolicyEngine must not be weakened by UI</strong></div>
          <div className="metric-row"><span>Legacy API</span><strong><a href="/api/settings">Available for compatibility</a></strong></div>
        </div>
      </section>
    </div>
  );
}

function editableSettings(settings: Record<string, unknown>): Array<{ section: string; key: string; label: string; value: string | number | boolean }> {
  const preferred = new Set([
    "autonomous_loop_enabled",
    "support_agent_enabled",
    "self_dev_proposal_enabled",
    "pc_server_enabled",
    "android_server_enabled",
    "browser_server_enabled",
    "room_server_enabled",
    "dev_server_enabled",
    "clipboard_capture_enabled",
    "camera_snapshot_enabled",
    "display_privacy_mode",
    "notifications_enabled",
    "daily_budget_usd",
    "monthly_budget_usd",
    "memory_budget_tokens"
  ]);
  const result: Array<{ section: string; key: string; label: string; value: string | number | boolean }> = [];
  for (const [section, rawSection] of Object.entries(settings)) {
    if (!rawSection || typeof rawSection !== "object" || Array.isArray(rawSection)) continue;
    for (const [key, value] of Object.entries(rawSection as Record<string, unknown>)) {
      if (!preferred.has(key) && result.length >= 24) continue;
      if (typeof value === "boolean" || typeof value === "number" || typeof value === "string") {
        result.push({ section, key, label: labelize(key), value });
      }
    }
  }
  return result.sort((a, b) => Number(preferred.has(b.key)) - Number(preferred.has(a.key))).slice(0, 32);
}

function labelize(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function settingMatchesSection(item: { section: string; key: string }, sectionId: string): boolean {
  const value = `${item.section}.${item.key}`.toLowerCase();
  const families: Record<string, string[]> = {
    autonomy: ["autonom", "support_agent", "self_dev"], models: ["model", "provider", "llm"], prompts: ["prompt"], memory: ["memory", "chroma"], context: ["context", "history", "token"],
    capabilities: ["capabilit", "tool"], permissions: ["permission", "clipboard", "camera", "microphone", "location"], approvals: ["approval", "risk"], servers: ["server", "host", "port"], devices: ["device", "android", "pc_"],
    notifications: ["notification"], privacy: ["privacy", "redact"], display: ["display", "presentation", "motion"], budgets: ["budget", "cost"], retention: ["retention", "archive", "ttl"], developer: ["developer", "debug", "mock"], backup: ["backup", "restore"]
  };
  const tokens = families[sectionId] || [sectionId];
  return tokens.some((token) => value.includes(token));
}

function restartRequired(item: { section: string; key: string }): boolean {
  const value = `${item.section}.${item.key}`.toLowerCase();
  return ["server", "host", "port", "provider", "database", "tls"].some((token) => value.includes(token));
}

