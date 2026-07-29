type Props = {
  generatedAt: number;
  sourceUpdatedAt: number;
  stale?: boolean;
};

export function Freshness({ generatedAt, sourceUpdatedAt, stale = false }: Props) {
  const label = `${stale ? "古いデータ" : "更新"}: ${formatDateTime(sourceUpdatedAt)}（${formatRelative(sourceUpdatedAt, generatedAt)}）`;
  return (
    <span className="freshness" data-stale={stale}>
      {label}
    </span>
  );
}
import { formatDateTime, formatRelative } from "../i18n";
