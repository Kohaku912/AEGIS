import { AlertTriangle, ChevronLeft, ChevronRight, LoaderCircle, Save, Trash2 } from "lucide-react";
import { type ReactNode, useEffect, useRef } from "react";
import { ja } from "../i18n";
import type { SavedView } from "../api/client";

export function PageHeader({ title, description, children }: { title: string; description?: string; children?: ReactNode }) {
  return <header className="page-header"><div><h2>{title}</h2>{description ? <p>{description}</p> : null}</div><div>{children}</div></header>;
}

export function DataState({ loading, error, empty, onRetry }: { loading?: boolean; error?: string; empty?: boolean; onRetry?: () => void }) {
  if (loading) return <div className="data-state" role="status"><LoaderCircle className="spin" size={18} />{ja.loading}</div>;
  if (error) return <div className="data-state data-state--error" role="alert"><AlertTriangle size={18} /><span>{error}</span>{onRetry ? <button type="button" onClick={onRetry}>{ja.retry}</button> : null}</div>;
  if (empty) return <div className="data-state">{ja.noData}</div>;
  return null;
}

export type ActionLevel = "view" | "safe" | "controlled" | "dangerous";
const actionLabels: Record<ActionLevel, string> = { view: "参照", safe: "安全", controlled: "要確認", dangerous: "危険" };

export function ActionButton({ level, busy, children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { level: ActionLevel; busy?: boolean }) {
  return <button {...props} type="button" className={`action-button action-button--${level}`} disabled={busy || props.disabled} aria-busy={busy}>
    <span className="action-button__level">{actionLabels[level]}</span>{busy ? "実行中…" : children}
  </button>;
}

export function ConfirmDialog({ open, title, details, dangerous, busy, onCancel, onConfirm }: {
  open: boolean; title: string; details: Record<string, unknown>; dangerous?: boolean; busy?: boolean; onCancel: () => void; onConfirm: () => void;
}) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    cancelRef.current?.focus();
    const close = (event: KeyboardEvent) => { if (event.key === "Escape" && !busy) onCancel(); };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [busy, onCancel, open]);
  if (!open) return null;
  return <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !busy) onCancel(); }}>
    <section className="confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <h3 id="confirm-title">{title}</h3>
      <dl>{Object.entries(details).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{String(value || "—")}</dd></div>)}</dl>
      <footer><button ref={cancelRef} type="button" className="secondary-button" onClick={onCancel} disabled={busy}>{ja.cancel}</button><ActionButton level={dangerous ? "dangerous" : "controlled"} busy={busy} onClick={onConfirm}>{ja.confirm}</ActionButton></footer>
    </section>
  </div>;
}

export function FilterBar({ query, status, statuses, onQuery, onStatus, children }: {
  query: string; status: string; statuses: string[]; onQuery: (value: string) => void; onStatus: (value: string) => void; children?: ReactNode;
}) {
  return <div className="filter-bar" role="search">
    <label><span>{ja.search}</span><input type="search" value={query} onChange={(event) => onQuery(event.currentTarget.value)} /></label>
    <label><span>{ja.status}</span><select value={status} onChange={(event) => onStatus(event.currentTarget.value)}><option value="">{ja.all}</option>{statuses.map((item) => <option value={item} key={item}>{item}</option>)}</select></label>
    {children}
  </div>;
}

export function Pagination({ page, total, pageSize, onPage }: { page: number; total: number; pageSize: number; onPage: (page: number) => void }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  return <nav className="pagination" aria-label="ページ"><button type="button" disabled={page <= 1} onClick={() => onPage(page - 1)}><ChevronLeft size={15} />{ja.previous}</button><span>{page} / {pages}</span><button type="button" disabled={page >= pages} onClick={() => onPage(page + 1)}>{ja.next}<ChevronRight size={15} /></button></nav>;
}

export function SavedViewPicker({ views, selected, onSelect, onSave, onDelete }: {
  views: SavedView[]; selected: string; onSelect: (id: string) => void; onSave: () => void; onDelete: (id: string) => void;
}) {
  return <div className="saved-view-picker"><label><span>保存ビュー</span><select value={selected} onChange={(event) => onSelect(event.currentTarget.value)}><option value="">現在の条件</option>{views.map((view) => <option value={view.id} key={view.id}>{view.name}</option>)}</select></label><button type="button" onClick={onSave}><Save size={15} />{ja.saveView}</button>{selected ? <button type="button" aria-label="保存ビューを削除" onClick={() => onDelete(selected)}><Trash2 size={15} /></button> : null}</div>;
}

export function ResponsiveDataView({ headers, rows, empty }: {
  headers: string[]; rows: Array<{ id: string; cells: ReactNode[]; card: ReactNode; onSelect?: () => void; selected?: boolean }>; empty?: ReactNode;
}) {
  if (!rows.length) return <>{empty}</>;
  return <div className="responsive-data">
    <div className="responsive-table" role="table"><div className="responsive-table__row responsive-table__head" role="row">{headers.map((header) => <span role="columnheader" key={header}>{header}</span>)}</div>{rows.map((row) => <button type="button" role="row" className="responsive-table__row" data-selected={row.selected} onClick={row.onSelect} key={row.id}>{row.cells.map((cell, index) => <span role="cell" key={`${row.id}-${index}`}>{cell}</span>)}</button>)}</div>
    <div className="responsive-cards">{rows.map((row) => <button type="button" data-selected={row.selected} onClick={row.onSelect} key={row.id}>{row.card}</button>)}</div>
  </div>;
}
