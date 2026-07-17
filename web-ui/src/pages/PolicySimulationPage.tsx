import { useQuery } from "@tanstack/react-query";
import { FlaskConical, Plus, ShieldAlert, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { fetchResourceEntities, simulatePolicy } from "../api/client";

type ArgumentRow = { id: number; key: string; value: string };
type Simulation = {
  capability_id?: string;
  decision?: string;
  reason?: string;
  effective_risk?: string;
  requires_approval?: boolean;
  fresh_auth_required?: boolean;
  matching_rule?: string;
  required_approval_type?: string | null;
  approval_expires_at_ms?: number | null;
  audit_required?: boolean;
  context?: string;
  executed?: boolean;
};

export function PolicySimulationPage() {
  const capabilities = useQuery({ queryKey: ["ui-resource", "capabilities"], queryFn: () => fetchResourceEntities("capabilities"), staleTime: 5_000 });
  const [capabilityId, setCapabilityId] = useState(
    () => new URLSearchParams(window.location.search).get("capability_id") || ""
  );
  const [context, setContext] = useState("tool_invocation");
  const [target, setTarget] = useState("");
  const [environment, setEnvironment] = useState("interactive_dashboard");
  const [rows, setRows] = useState<ArgumentRow[]>([{ id: 1, key: "", value: "" }]);
  const [result, setResult] = useState<Simulation>();
  const [status, setStatus] = useState("");
  const selected = useMemo(() => capabilities.data?.items.find((item) => item.id === capabilityId), [capabilities.data, capabilityId]);

  const run = async () => {
    if (!capabilityId) { setStatus("Select a capability before simulation."); return; }
    const args = Object.fromEntries(rows.filter((row) => row.key.trim()).map((row) => [row.key.trim(), parseValue(row.value)]));
    setStatus("Evaluating effective policy without execution...");
    try {
      const payload = await simulatePolicy({ capability_id: capabilityId, context, target, environment: { surface: environment }, arguments: args });
      setResult((payload.simulation || {}) as Simulation);
      setStatus("Simulation complete. No capability was executed.");
    } catch (error) {
      setResult(undefined);
      setStatus(error instanceof Error ? error.message : String(error));
    }
  };

  return <div className="policy-simulator">
    <header className="resource-page__hero"><div><span>Deterministic safety gate</span><h2>Policy Simulation</h2><p>Evaluate effective capability policy, approval requirements, and execution context without invoking a tool.</p></div><ShieldAlert size={28} /></header>
    <section className="policy-simulator__layout">
      <form onSubmit={(event) => { event.preventDefault(); void run(); }}>
        <label>Capability<select aria-label="Capability" value={capabilityId} onChange={(event) => { setCapabilityId(event.currentTarget.value); setResult(undefined); }}><option value="">Select an effective capability</option>{(capabilities.data?.items || []).map((item) => <option value={item.id} key={item.id}>{item.id}</option>)}</select></label>
        <div className="policy-simulator__facts"><span>Effective risk<strong>{String(selected?.data?.risk_level || selected?.data?.risk || "Not selected")}</strong></span><span>Server<strong>{selected?.subtitle || "Not selected"}</strong></span><span>Status<strong>{selected?.status || "Not selected"}</strong></span></div>
        <div className="form-grid"><label>Actor / execution context<select value={context} onChange={(event) => setContext(event.currentTarget.value)}><option value="tool_invocation">Interactive tool invocation</option><option value="event_trigger">Event trigger</option><option value="autonomous_task">Autonomous task</option></select></label><label>Environment<select value={environment} onChange={(event) => setEnvironment(event.currentTarget.value)}><option value="interactive_dashboard">Interactive dashboard</option><option value="scheduled_runtime">Scheduled runtime</option><option value="device_companion">Device companion</option></select></label></div>
        <label>Target<input value={target} onChange={(event) => setTarget(event.currentTarget.value)} placeholder="Optional target identifier" /></label>
        <fieldset><legend>Arguments</legend>{rows.map((row) => <div className="argument-row" key={row.id}><input aria-label="Argument name" value={row.key} onChange={(event) => setRows((items) => items.map((item) => item.id === row.id ? { ...item, key: event.currentTarget.value } : item))} placeholder="parameter" /><input aria-label="Argument value" value={row.value} onChange={(event) => setRows((items) => items.map((item) => item.id === row.id ? { ...item, value: event.currentTarget.value } : item))} placeholder="value" /><button className="icon-button" type="button" title="Remove argument" onClick={() => setRows((items) => items.length === 1 ? [{ ...items[0], key: "", value: "" }] : items.filter((item) => item.id !== row.id))}><Trash2 size={14} /></button></div>)}<button className="secondary-button" type="button" onClick={() => setRows((items) => [...items, { id: Math.max(0, ...items.map((item) => item.id)) + 1, key: "", value: "" }])}><Plus size={14} />Add argument</button></fieldset>
        <button className="primary-button" type="submit" disabled={!capabilityId}><FlaskConical size={15} />Simulate policy</button>
        <p className="form-status" role="status">{status}</p>
      </form>
      <aside className="simulation-result" data-decision={result?.decision || "NONE"}>{result ? <><span>Decision</span><h3>{result.decision}</h3><p>{result.reason}</p><dl><div><dt>Capability</dt><dd>{result.capability_id}</dd></div><div><dt>Effective risk</dt><dd>{result.effective_risk}</dd></div><div><dt>Matching rule</dt><dd>{result.matching_rule}</dd></div><div><dt>Approval</dt><dd>{result.requires_approval ? result.required_approval_type || "Required" : "Not required"}</dd></div><div><dt>Fresh auth</dt><dd>{result.fresh_auth_required ? "Required before execution" : "Not required by this risk result"}</dd></div><div><dt>Audit</dt><dd>{result.audit_required ? "Required" : "Optional"}</dd></div><div><dt>Context</dt><dd>{result.context}</dd></div><div><dt>Execution</dt><dd>{result.executed ? "Executed" : "Not executed"}</dd></div></dl></> : <><span>Simulation result</span><h3>Ready</h3><p>Select a capability and context. The PolicyEngine decision will appear here without calling ToolBroker.</p></>}</aside>
    </section>
  </div>;
}

function parseValue(value: string): unknown {
  const trimmed = value.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed !== "" && Number.isFinite(Number(trimmed))) return Number(trimmed);
  return value;
}
