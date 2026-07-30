/** Shared visual primitives: glyphs, gauges, sparklines, topology, overlays. */

export type Severity = "critical" | "warning" | "info" | "ok" | "unknown";

const SEVERITY_GLYPH: Record<Severity, string> = {
  critical: "■",
  warning: "◆",
  info: "●",
  ok: "●",
  unknown: "○",
};

export function SeverityGlyph({
  severity = "info",
  label,
}: {
  severity?: Severity;
  label?: string;
}) {
  return (
    <span className="severity-glyph" data-severity={severity} title={label || severity} aria-label={label || severity}>
      <span aria-hidden="true">{SEVERITY_GLYPH[severity]}</span>
      {label ? <span className="severity-glyph__label">{label}</span> : null}
    </span>
  );
}

export function GaugeRing({
  value,
  max = 10,
  label,
  size = 72,
}: {
  value: number;
  max?: number;
  label?: string;
  size?: number;
}) {
  const ratio = Math.max(0, Math.min(1, max <= 0 ? 0 : value / max));
  const r = (size - 8) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - ratio);
  return (
    <div className="gauge-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
        <circle cx={size / 2} cy={size / 2} r={r} className="gauge-ring__track" fill="none" strokeWidth="6" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          className="gauge-ring__value"
          fill="none"
          strokeWidth="6"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="gauge-ring__text">
        <strong>{value.toFixed(1)}</strong>
        {label ? <span>{label}</span> : null}
      </div>
    </div>
  );
}

export function Sparkline({
  values,
  width = 120,
  height = 32,
  label,
}: {
  values: number[];
  width?: number;
  height?: number;
  label?: string;
}) {
  if (!values.length) {
    return <span className="sparkline sparkline--empty muted">{label || "No data"}</span>;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(1, values.length - 1)) * (width - 2) + 1;
      const y = height - 2 - ((value - min) / span) * (height - 4);
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <svg className="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label || "Trend"}>
      <polyline fill="none" points={points} />
    </svg>
  );
}

export function ProgressSteps({
  total,
  current,
  failed = 0,
}: {
  total: number;
  current: number;
  failed?: number;
}) {
  const safeTotal = Math.max(1, total);
  const ratio = Math.max(0, Math.min(1, current / safeTotal));
  return (
    <div className="progress-steps" aria-label={`Step ${current} of ${safeTotal}`}>
      <div className="progress-steps__bar">
        <span style={{ width: `${ratio * 100}%` }} data-failed={failed > 0} />
      </div>
      <span className="mono muted">
        {current}/{safeTotal}
        {failed ? ` · ${failed} failed` : ""}
      </span>
    </div>
  );
}

export function TopologyMiniMap({
  servers,
}: {
  servers: Array<{ server_id?: string; id?: string; status?: string }>;
}) {
  return (
    <div className="topology-mini" aria-label="Server topology">
      <div className="topology-mini__core">AI</div>
      <div className="topology-mini__ring">
        {servers.map((server) => {
          const id = String(server.server_id || server.id || "?");
          const short = id.replace(/-server$/, "").slice(0, 8);
          return (
            <span key={id} className="topology-mini__node" data-status={String(server.status || "UNKNOWN").toUpperCase()}>
              {short}
            </span>
          );
        })}
      </div>
    </div>
  );
}

export function CriticalOverlay({
  items,
  onOpen,
}: {
  items: Array<{ id: string; title: string; severity?: Severity }>;
  onOpen?: () => void;
}) {
  if (!items.length) return null;
  const top = items.slice(0, 3);
  return (
    <div className="critical-overlay" role="status" data-severity={top[0]?.severity || "warning"}>
      <div>
        <SeverityGlyph severity={top[0]?.severity || "warning"} />
        <strong>要対応 {items.length} 件</strong>
        <span>{top.map((item) => item.title).join(" · ")}</span>
      </div>
      {onOpen ? (
        <button type="button" onClick={onOpen}>
          開く
        </button>
      ) : null}
    </div>
  );
}
