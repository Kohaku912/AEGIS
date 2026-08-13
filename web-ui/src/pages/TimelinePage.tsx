import { RefreshCw, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchPersonalDataEvent,
  fetchPersonalDataTimeline,
  fetchPersonalDataTimelineAll,
  searchPersonalData,
} from "../api/client";
import { DataState, PageHeader, Pagination } from "../components/DashboardPrimitives";
import type { UiOverview } from "../types";
import { asRecord, text, time } from "./PageSupport";

const PAGE_SIZE_OPTIONS = [
  { value: 50, label: "50" },
  { value: 100, label: "100" },
  { value: 500, label: "500" },
  { value: 0, label: "すべて" },
] as const;

const DEVICE_OPTIONS = [
  { value: "all", label: "All" },
  { value: "pc", label: "PC" },
  { value: "android", label: "Android" },
  { value: "room", label: "Room" },
  { value: "aegis", label: "AEGIS" },
] as const;

const INPUT_CATEGORIES = ["printable", "editing", "navigation", "function", "modifier", "system", "mouse"] as const;

const EVENT_LABELS: Record<string, string> = {
  "pc.input.typed": "キー入力",
  "pc.input.clicked": "クリック",
  "pc.ui.invoked": "クリック",
  "pc.ui.value_changed": "入力内容の変化",
  "pc.ui.focus_changed": "フォーカス移動",
  "pc.window.focused": "ウィンドウ切替",
  "pc.window.opened": "ウィンドウを開いた",
  "pc.window.closed": "ウィンドウを閉じた",
  "android.ui.tapped": "タップ",
  "android.ui.scrolled": "スクロール",
  "android.ui.focus_changed": "フォーカス移動",
  "android.ui.text_changed": "テキスト変化",
  "android.notification.posted": "通知",
  "android.screen.transition": "画面遷移",
  "android.app.foreground": "フォアグラウンド",
  "android.activity": "アクティビティ",
  "android.heartbeat": "ハートビート",
  "android.connected": "接続",
  "android.disconnected": "切断",
  "task.created": "タスク作成",
  "task.completed": "タスク完了",
  "task.running": "タスク実行中",
};

const HIDDEN_PAYLOAD_KEYS = new Set([
  "screenshot_jpeg_base64", "image_base64", "event_type", "timestamp_ms",
]);

const FIELD_LABELS: Record<string, string> = {
  app_name: "アプリ",
  process_name: "プロセス",
  package_name: "パッケージ",
  window_title: "ウィンドウ",
  active_window_title: "ウィンドウ",
  control_name: "コントロール",
  control_type: "コントロール種別",
  url: "URL",
  value: "内容",
  text: "テキスト",
  title: "タイトル",
  keys: "キー",
  mouse_buttons: "マウスボタン",
  click_x: "X",
  click_y: "Y",
  click_w: "幅",
  click_h: "高さ",
  keyboard_count: "キー回数",
  mouse_count: "クリック回数",
  input_target_category: "入力先",
  scroll_x: "スクロールX",
  scroll_y: "スクロールY",
  is_password: "パスワード欄",
  classification_hint: "分類",
  control_kind: "コントロール種別",
};

function isReplacementText(value: unknown): boolean {
  const textValue = String(value ?? "").trim();
  if (textValue.length < 3) return false;
  const marks = [...textValue].filter((char) => char === "?" || char === "\uFFFD").length;
  return marks >= 3 && marks / textValue.length >= 0.4;
}

function readable(value: unknown): string {
  const textValue = String(value ?? "").trim();
  return !textValue || isReplacementText(textValue) ? "" : textValue;
}

function formatValue(value: unknown): string {
  if (typeof value === "boolean") return value ? "はい" : "いいえ";
  if (typeof value === "number") return String(value);
  if (Array.isArray(value)) {
    return value.map((item) => readable(item) || String(item ?? "")).filter(Boolean).join(" + ");
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>)
      .filter(([, item]) => item !== 0 && item !== "" && item != null)
      .map(([key, item]) => `${key}×${item}`);
    return entries.join(" · ");
  }
  return readable(value);
}

function inputSummary(item: Record<string, unknown>): string {
  const payload = asRecord(item.payload);
  const parts: string[] = [];
  const keys = formatValue(payload.keys);
  if (keys) parts.push(keys);
  const buttons = formatValue(payload.mouse_buttons);
  const hasClick = payload.click_x != null || payload.click_y != null;
  if (buttons && hasClick) parts.push(`${buttons} (${payload.click_x}, ${payload.click_y})`);
  else if (hasClick) parts.push(`(${payload.click_x}, ${payload.click_y})`);
  else if (buttons) parts.push(buttons);
  if (!keys) {
    const counts = asRecord(payload.key_category_counts);
    for (const key of INPUT_CATEGORIES) {
      const count = Number(counts[key] || 0);
      if (count) parts.push(`${key}×${count}`);
    }
  }
  if (!parts.length) {
    const keyboard = Number(payload.keyboard_count || 0);
    const mouse = Number(payload.mouse_count || 0);
    if (keyboard) parts.push(`キー×${keyboard}`);
    if (mouse) parts.push(`クリック×${mouse}`);
  }
  return parts.join(" · ");
}

function eventLabel(eventType: string): string {
  return EVENT_LABELS[eventType] || eventType;
}

function payloadFields(item: Record<string, unknown>, all = false): Array<[string, string]> {
  const payload = asRecord(item.payload);
  const rows: Array<[string, string]> = [];
  const seen = new Set<string>();
  const push = (label: string, value: unknown) => {
    const textValue = typeof value === "string" ? readable(value) : formatValue(value);
    if (!textValue || seen.has(`${label}:${textValue}`)) return;
    seen.add(`${label}:${textValue}`);
    rows.push([label, textValue.length > 400 ? `${textValue.slice(0, 400)}…` : textValue]);
  };
  const app = readable(payload.app_name || payload.process_name || payload.package_name);
  const windowTitle = readable(payload.window_title || payload.active_window_title);
  push("アプリ", app);
  if (windowTitle && windowTitle !== app) push("ウィンドウ", windowTitle);
  push("コントロール", payload.control_name);
  push("URL", payload.url);
  const input = inputSummary(item);
  push("入力", input);
  push("内容", payload.value || payload.text);
  if (payload.is_password === true || payload.control_kind === "password") push("パスワード欄", "はい");
  if (!all) return rows;
  for (const [key, value] of Object.entries(payload)) {
    if (HIDDEN_PAYLOAD_KEYS.has(key)) continue;
    if (["app_name", "process_name", "package_name", "window_title", "active_window_title", "control_name", "url", "value", "text", "keys", "mouse_buttons", "click_x", "click_y", "key_category_counts"].includes(key)) continue;
    push(FIELD_LABELS[key] || key, value);
  }
  return rows;
}

export function TimelinePage({ overview: _overview }: { overview: UiOverview }) {
  const [device, setDevice] = useState("all");
  const [eventType, setEventType] = useState("all");
  const [eventTypes, setEventTypes] = useState<Array<{ event_type: string; count: number }>>([]);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [reload, setReload] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const deviceFilter = device === "all" ? "" : device;
      const typeFilter = eventType === "all" ? "" : eventType;
      if (query.trim()) {
        const result = await searchPersonalData(query.trim(), 50_000, deviceFilter);
        const filtered = typeFilter
          ? result.items.filter((item) => String(item.event_type || "") === typeFilter)
          : result.items;
        setItems(filtered);
        setTotal(filtered.length);
        const facets = await fetchPersonalDataTimeline(1, 1, deviceFilter);
        if (facets.eventTypes?.length) setEventTypes(facets.eventTypes);
        return;
      }
      const result = pageSize === 0
        ? await fetchPersonalDataTimelineAll(deviceFilter, typeFilter)
        : await fetchPersonalDataTimeline(page, pageSize, deviceFilter, typeFilter);
      setItems(result.items);
      setTotal(result.total);
      if (result.eventTypes?.length) setEventTypes(result.eventTypes);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  }, [device, eventType, page, pageSize, query]);

  useEffect(() => {
    void load();
  }, [load, reload]);

  async function openDetail(eventId: string) {
    if (!eventId) return;
    try {
      setDetail(await fetchPersonalDataEvent(eventId));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  }

  const facts = Array.isArray(detail?.facts) ? detail.facts as Array<Record<string, unknown>> : [];
  const inferences = Array.isArray(detail?.inferences) ? detail.inferences as Array<Record<string, unknown>> : [];
  const evidence = Array.isArray(detail?.evidence) ? detail.evidence as Array<Record<string, unknown>> : [];
  const showing = items.length;
  const facetTotal = eventTypes.reduce((sum, row) => sum + row.count, 0);
  const detailFields = useMemo(() => detail ? payloadFields(detail, true) : [], [detail]);

  return <div className="grid">
    <PageHeader title="Timeline" description="Personal Data Core のユーザーログ。記録した Event の詳細を辿れます。">
      <button type="button" className="secondary-button" onClick={() => setReload((value) => value + 1)} disabled={loading}>
        <RefreshCw size={14} aria-hidden="true" />Refresh
      </button>
    </PageHeader>
    <section className="panel">
      <div className="resource-toolbar">
        <label>Device <select value={device} onChange={(event) => { setDevice(event.currentTarget.value); setPage(1); }}>
          {DEVICE_OPTIONS.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}
        </select></label>
        <label>種類 <select value={eventType} onChange={(event) => { setEventType(event.currentTarget.value); setPage(1); }} aria-label="Event type">
          <option value="all">すべて ({facetTotal.toLocaleString() || total.toLocaleString()})</option>
          {eventTypes.map((row) => (
            <option value={row.event_type} key={row.event_type}>
              {eventLabel(row.event_type)} ({row.count.toLocaleString()})
            </option>
          ))}
        </select></label>
        <label>表示件数 <select aria-label="Page size" value={pageSize} onChange={(event) => { setPageSize(Number(event.currentTarget.value)); setPage(1); }}>
          {PAGE_SIZE_OPTIONS.map((option) => <option value={option.value} key={option.label}>{option.label}</option>)}
        </select></label>
        <label className="search-field"><Search size={14} aria-hidden="true" /><input value={query} onChange={(event) => { setQuery(event.currentTarget.value); setPage(1); }} placeholder="Search title, app, URL" /></label>
        <span className="muted">{loading ? "読み込み中…" : `${showing.toLocaleString()} / ${total.toLocaleString()} 件 · ${eventTypes.length} 種類`}</span>
      </div>
      <DataState loading={loading} error={error} empty={!loading && !error && !items.length} onRetry={() => setReload((value) => value + 1)} />
      {!loading && !error && items.length ? <div className="timeline-feed">
        {items.map((item, index) => {
          const eventTypeName = String(item.event_type || "");
          const fields = payloadFields(item);
          const title = readable(item.title) || fields.find(([label]) => label === "アプリ")?.[1] || eventLabel(eventTypeName);
          return <button type="button" className="timeline-feed__item" data-selected={detail?.id === item.id} onClick={() => { void openDetail(String(item.id || "")); }} key={String(item.id || index)}>
            <header>
              <strong>{eventLabel(eventTypeName)}</strong>
              <span className={`status-badge ${String(item.epistemics || "observed")}`}>{text(item.epistemics, "observed")}</span>
              <small>{time(item.timestamp_ms)} · {text(item.source_device)}/{text(item.source_sensor)}</small>
            </header>
            <p>{title}</p>
            {fields.length ? <dl>{fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl> : null}
          </button>;
        })}
      </div> : null}
      {pageSize === 0 || query.trim() ? null : <Pagination page={page} total={total} pageSize={pageSize} onPage={setPage} />}
    </section>
    {detail ? <section className="panel">
      <header><h2>{eventLabel(String(detail.event_type || ""))}</h2><span className="status-badge">{text(detail.epistemics)}</span></header>
      <p className="muted">{text(detail.event_type)} · {text(detail.source_device)}/{text(detail.source_sensor)} · {time(detail.timestamp_ms)}</p>
      {detailFields.length ? <dl className="timeline-detail">{detailFields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl> : null}
      <div>
        <h3>Facts</h3>
        {facts.length ? facts.map((fact) => <p key={String(fact.id)}>{text(fact.statement)}</p>) : <p className="muted">No facts linked.</p>}
      </div>
      <div>
        <h3>Inferences</h3>
        {inferences.length ? inferences.map((item) => <p key={String(item.id)}>{text(item.statement)} <span className="muted">({text(item.method)})</span></p>) : <p className="muted">No inferences.</p>}
      </div>
      <div>
        <h3>Evidence</h3>
        {evidence.length ? evidence.map((item) => <p key={String(item.id)} className="mono">{text(item.id)} · {text(item.codec)} · {text(item.byte_size)} bytes</p>) : <p className="muted">No raw evidence.</p>}
      </div>
    </section> : null}
  </div>;
}
