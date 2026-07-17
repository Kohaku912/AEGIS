import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Coins, Cpu, Database, Gauge, RefreshCw } from "lucide-react";
import { useMemo, useState } from "react";
import { fetchLlmRequests } from "../api/client";
import type { EntitySummary, UiOverview } from "../types";

const CONTEXT_KEYS = ["system", "history", "memory", "events", "capability", "tool_schema", "user_state"];

export function LLMUsagePage({ overview }: { overview: UiOverview }) {
  const [period, setPeriod] = useState("24h");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<EntitySummary>();
  const requests = useQuery({ queryKey: ["llm-requests", period], queryFn: () => fetchLlmRequests(period), staleTime: 10_000 });
  const filtered = (requests.data?.items || []).filter((item) => JSON.stringify(item).toLowerCase().includes(query.toLowerCase()));
  const totals = useMemo(() => aggregate(filtered), [filtered]);

  return (
    <div className="llm-console">
      <header className="llm-console__summary">
        <div><span>Observability / request accounting</span><h2>LLM Usage</h2><p>Audit-backed tokens, context composition, cache behavior, cost, latency, failures, and retry families.</p></div>
        <label>Period<select value={period} onChange={(event) => setPeriod(event.currentTarget.value)}><option value="1h">1 hour</option><option value="24h">24 hours</option><option value="7d">7 days</option><option value="30d">30 days</option></select></label>
      </header>
      <section className="llm-metrics">
        <Metric icon={Cpu} label="Requests" value={String(filtered.length)} />
        <Metric icon={Gauge} label="Input / output" value={`${totals.input.toLocaleString()} / ${totals.output.toLocaleString()}`} />
        <Metric icon={Database} label="Cache hit / miss" value={`${totals.cacheHit.toLocaleString()} / ${totals.cacheMiss.toLocaleString()}`} />
        <Metric icon={Coins} label="Provider cost" value={`$${totals.cost.toFixed(4)}`} />
        <Metric icon={AlertTriangle} label="Failures / retry suspects" value={`${totals.failures} / ${totals.retries}`} />
      </section>
      <div className="resource-toolbar"><label><input aria-label="Filter LLM requests" value={query} onChange={(event) => setQuery(event.currentTarget.value)} placeholder="Filter model, caller, prompt, request family..." /></label><button className="secondary-button" type="button" onClick={() => void requests.refetch()}><RefreshCw size={14} />Refresh audit</button></div>
      <section className="llm-console__layout">
        <div className="llm-request-list">
          {requests.isLoading ? <p>Loading audit-backed requests...</p> : null}
          {requests.isError ? <p className="warning-text">LLM usage records are unavailable.</p> : null}
          {filtered.map((item) => <button type="button" aria-current={selected?.id === item.id} onClick={() => setSelected(item)} key={item.id}><span>{formatTime(item.updated_at)}</span><strong>{String(item.data?.model || item.title)}</strong><small>{String(item.data?.caller || item.subtitle)} / {tokens(item.data)} tokens / {item.status}</small></button>)}
          {!requests.isLoading && !filtered.length ? <p>No LLM request matched this period and filter.</p> : null}
        </div>
        <aside className="llm-request-detail">
          {selected ? <RequestDetail item={selected} /> : <p>Select a request to inspect its exact context and cost accounting.</p>}
        </aside>
      </section>
      <footer className="llm-budget-rail"><strong>Budget and autonomy</strong><span>{String(overview.usage.data.budget_status || overview.usage.data.status || "Budget state not reported")}</span><span>{String(overview.usage.data.autonomous_suppression_reason || "No autonomous suppression reported")}</span></footer>
    </div>
  );
}

function RequestDetail({ item }: { item: EntitySummary }) {
  const detail = item.data || {};
  const context = (detail.context_breakdown || detail.context_tokens_by_section || detail.context_meta || {}) as Record<string, unknown>;
  const max = Math.max(1, ...CONTEXT_KEYS.map((key) => Number(context[key] || context[`${key}_tokens`] || 0)));
  return <><header><span>{item.status}</span><h3>{String(detail.model || item.title)}</h3><p>{String(detail.prompt_id || detail.profile_id || detail.caller || item.subtitle)}</p></header><dl><div><dt>Request</dt><dd>{String(detail.request_id || item.id)}</dd></div><div><dt>Provider</dt><dd>{String(detail.provider || "Not reported")}</dd></div><div><dt>Input / output</dt><dd>{Number(detail.input_tokens || 0).toLocaleString()} / {Number(detail.output_tokens || 0).toLocaleString()}</dd></div><div><dt>Cache hit / miss</dt><dd>{Number(detail.input_cache_hit_tokens || 0).toLocaleString()} / {Number(detail.input_cache_miss_tokens || 0).toLocaleString()}</dd></div><div><dt>Cost</dt><dd>${Number(detail.provider_reported_cost || detail.cost_usd || 0).toFixed(6)}</dd></div><div><dt>Latency</dt><dd>{Number(detail.latency_ms || 0).toLocaleString()} ms</dd></div><div><dt>Retry family</dt><dd>{String(detail.retry_group_id || detail.parent_trace_id || "None")}</dd></div></dl><section className="context-breakdown"><h4>Context breakdown</h4>{CONTEXT_KEYS.map((key) => { const value = Number(context[key] || context[`${key}_tokens`] || 0); return <div key={key}><span>{key.replace("_", " ")}</span><progress max={max} value={value} /><strong>{value.toLocaleString()}</strong></div>; })}</section></>;
}

function Metric({ icon: Icon, label, value }: { icon: typeof Cpu; label: string; value: string }) { return <article><Icon size={16} /><span>{label}</span><strong>{value}</strong></article>; }
function number(data: Record<string, unknown> | undefined, ...keys: string[]) { for (const key of keys) { const value = Number(data?.[key] || 0); if (value) return value; } return 0; }
function tokens(data: Record<string, unknown> | undefined) { return number(data, "total_tokens", "tokens_used") || number(data, "input_tokens") + number(data, "output_tokens"); }
function aggregate(items: EntitySummary[]) { return items.reduce((sum, item) => { const data = item.data; sum.input += number(data, "input_tokens", "prompt_tokens"); sum.output += number(data, "output_tokens", "completion_tokens"); sum.cacheHit += number(data, "input_cache_hit_tokens", "cache_hit_tokens"); sum.cacheMiss += number(data, "input_cache_miss_tokens", "cache_miss_tokens"); sum.cost += number(data, "provider_reported_cost", "cost_usd", "estimated_cost"); sum.failures += item.status.toLowerCase().includes("fail") || item.status.toLowerCase().includes("error") ? 1 : 0; sum.retries += Boolean(data?.retry_loop_suspect || data?.retry_group_id) ? 1 : 0; return sum; }, { input: 0, output: 0, cacheHit: 0, cacheMiss: 0, cost: 0, failures: 0, retries: 0 }); }
function formatTime(value?: number) { return value ? new Date(value).toLocaleTimeString() : "No time"; }
