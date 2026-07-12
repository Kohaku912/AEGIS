type Props = {
  generatedAt: number;
  sourceUpdatedAt: number;
  stale?: boolean;
};

export function Freshness({ generatedAt, sourceUpdatedAt, stale = false }: Props) {
  const age = Math.max(0, generatedAt - sourceUpdatedAt);
  const label = stale ? `STALE ${formatAge(age)}` : age < 15_000 ? "LIVE" : `${formatAge(age)} ago`;
  return (
    <span className="freshness" data-stale={stale}>
      {label}
    </span>
  );
}

function formatAge(ms: number): string {
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h`;
}
