// LlmLayerPanel.tsx — DASHBOARD_V3_PLAN.md Phase L6
//
// L1 / L2 / L3 専用パネルの共通 UI コンポーネント。
// 3 つの page (L1PanelPage / L2PanelPage / L3PanelPage) はこの component を
// layer props で呼び出す薄いラッパーとして実装する。
//
// 機能:
//   - レイヤー名 / 説明の表示
//   - kind 別件数 (stats) の表示
//   - イベント一覧 (timestamp / type / event_id / source / payload summary)
//   - 5 秒間隔の自動再フェッチ (簡易 SSE 代替)

import { useEffect, useMemo, useState } from "react";
import {
  fetchL1Events,
  fetchL1EventsStats,
  fetchL2Events,
  fetchL2EventsStats,
  fetchL3Events,
  fetchL3EventsStats,
  type LlmEvent,
  type LlmEventsResponse,
  type LlmEventsStats,
  type LlmLayer,
} from "../api/client";
import { eventTraceIds } from "../displayModel";

type LayerDescriptor = {
  layer: LlmLayer;
  title: string;
  description: string;
  kinds: string[];
};

const LAYER_DESCRIPTORS: Record<LlmLayer, LayerDescriptor> = {
  L1: {
    layer: "L1",
    title: "L1 — 知覚 / Router",
    description: "常時稼働する知覚・ルーティング層。EventBus を監視し、簡単なタスクは直接 Capability へルーティング、難しい問題は L2 へ escalate する。",
    kinds: ["l1.observation", "l1.decision", "l1.escalation", "l1.capability.invoked", "l1.capability.completed"],
  },
  L2: {
    layer: "L2",
    title: "L2 — Autonomous Mind",
    description: "定期的に (デフォルト 30 分) Memory / Desire / Task / L1 summary を統合的に参照し行動決定する自律思考層。",
    kinds: ["l2.thinking", "l2.decision", "l2.escalation"],
  },
  L3: {
    layer: "L3",
    title: "L3 — Deep Reasoner",
    description: "L2 の confidence < threshold または difficulty > threshold のとき呼ばれる深層推論層。読み取り系 capability は直接実行可能、書き込み系は L2 経由強制。",
    kinds: ["l3.invoked", "l3.completed", "l3.failed"],
  },
};

const REFRESH_MS = 5000;

const _fetchers: Record<LlmLayer, (kinds: string[], limit: number) => Promise<LlmEventsResponse>> = {
  L1: (kinds, limit) => fetchL1Events(kinds, limit),
  L2: (kinds, limit) => fetchL2Events(kinds, limit),
  L3: (kinds, limit) => fetchL3Events(kinds, limit),
};

const _statsFetchers: Record<LlmLayer, () => Promise<LlmEventsStats>> = {
  L1: fetchL1EventsStats,
  L2: fetchL2EventsStats,
  L3: fetchL3EventsStats,
};

export type LlmLayerPanelProps = {
  layer: LlmLayer;
};

export function LlmLayerPanel({ layer }: LlmLayerPanelProps) {
  const descriptor = LAYER_DESCRIPTORS[layer];
  const [events, setEvents] = useState<LlmEventsResponse | null>(null);
  const [stats, setStats] = useState<LlmEventsStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterKind, setFilterKind] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const tick = async () => {
      if (cancelled) return;
      try {
        const fetcher = _fetchers[layer];
        const statsFetcher = _statsFetchers[layer];
        const requestedKinds = filterKind ? [filterKind] : [];
        const [ev, st] = await Promise.all([fetcher(requestedKinds, 200), statsFetcher()]);
        if (cancelled) return;
        setEvents(ev);
        setStats(st);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (!cancelled) timer = setTimeout(tick, REFRESH_MS);
      }
    };
    void tick();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [layer, filterKind]);

  const filteredEvents = useMemo(() => events?.events || [], [events]);

  return (
    <section className="page-section" data-testid={`llm-layer-panel-${layer}`}>
      <header className="page-header">
        <h1>{descriptor.title}</h1>
        <p className="page-description">{descriptor.description}</p>
      </header>

      {error && (
        <div className="panel-error" role="alert">
          Failed to load {layer} events: {error}
        </div>
      )}

      {stats && (
        <div className="layer-stats" data-testid={`layer-stats-${layer}`}>
          <div className="layer-stats-total">
            <span className="label">Total</span>
            <span className="value">{stats.total}</span>
          </div>
          <div className="layer-stats-by-kind">
            {Object.entries(stats.by_kind).map(([kind, count]) => (
              <div key={kind} className="layer-stats-kind">
                <span className="kind">{kind}</span>
                <span className="count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="layer-filter">
        <label htmlFor={`kind-filter-${layer}`}>Filter by kind:</label>
        <select
          id={`kind-filter-${layer}`}
          value={filterKind}
          onChange={(e) => setFilterKind(e.target.value)}
        >
          <option value="">(all)</option>
          {descriptor.kinds.map((kind) => (
            <option key={kind} value={kind}>
              {kind}
            </option>
          ))}
        </select>
      </div>

      <div className="layer-events" data-testid={`layer-events-${layer}`}>
        <table className="events-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Type</th>
              <th>Event ID</th>
              <th>Source</th>
              <th>Trace</th>
              <th>Payload</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan={6} className="events-empty">
                  {events === null ? "Loading..." : "No events yet."}
                </td>
              </tr>
            ) : (
              filteredEvents.map((event) => <EventRow key={event.event_id || event.timestamp} event={event} />)
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function EventRow({ event }: { event: LlmEvent }) {
  const ts = event.timestamp || 0;
  const dateLabel = ts ? new Date(ts).toISOString() : "—";
  const trace = eventTraceIds({ payload: event.payload || {} });
  const payloadSummary = useMemo(() => {
    const payload = event.payload;
    if (!payload) return "—";
    const keys = Object.keys(payload);
    if (keys.length === 0) return "—";
    // 主要なフィールドを抜粋
    const summary: Record<string, unknown> = {};
    for (const k of keys) {
      const v = payload[k];
      if (typeof v === "string" || typeof v === "number" || typeof v === "boolean") {
        summary[k] = v;
      } else if (Array.isArray(v)) {
        summary[k] = `[${v.length} items]`;
      } else if (v && typeof v === "object") {
        summary[k] = "{...}";
      }
    }
    return JSON.stringify(summary);
  }, [event.payload]);

  return (
    <tr>
      <td className="events-cell-ts">{dateLabel}</td>
      <td className="events-cell-type">{event.type || "—"}</td>
      <td className="events-cell-id">{event.event_id || "—"}</td>
      <td className="events-cell-source">{event.source || "—"}</td>
      <td className="events-cell-trace">
        {trace.trace_id ? <div><strong>trace</strong> <code>{trace.trace_id}</code></div> : null}
        {trace.agent_session_id ? <div><strong>session</strong> <code>{trace.agent_session_id}</code></div> : null}
        {trace.parent_id ? <div><strong>parent</strong> <code>{trace.parent_id}</code></div> : null}
        {trace.activity_id ? <div><strong>activity</strong> <code>{trace.activity_id}</code></div> : null}
        {!trace.trace_id && !trace.agent_session_id && !trace.parent_id && !trace.activity_id ? "—" : null}
      </td>
      <td className="events-cell-payload">
        <code>{payloadSummary}</code>
      </td>
    </tr>
  );
}
