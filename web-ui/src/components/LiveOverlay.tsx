import { Circle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { eventAgentSessionId, liveOverlayPriority, pickLiveOverlayEventForAgent, readableDisplayText } from "../displayModel";
import { inferLayerFromEvent } from "../api/client";
import type { UiEvent } from "../types";

export interface LiveOverlayProps {
  events: UiEvent[];
  onClick?: (event: UiEvent) => void;
}

const OVERLAY_PRIORITY_LABEL: Record<number, string> = {
  0: "Approval required",
  1: "Error",
  2: "Agent waiting / verifying",
  3: "Tool started",
  4: "Tool completed",
  5: "Agent thinking",
  6: "Agent completed",
  7: "Approval resolved",
  8: "Activity update",
  9: "Live"
};

type OverlayToggles = {
  show: boolean;
  showThinking: boolean;
  showToolCalls: boolean;
};

const DEFAULT_TOGGLES: OverlayToggles = { show: true, showThinking: true, showToolCalls: true };

/**
 * LiveOverlay がクリックされたときの遷移先 URL を返す (Phase D8 / instruction.md §19).
 *
 * 優先順位: agent_session_id > task_id > approval_id > raw-activity fallback.
 * agent_session_id があれば Agent Session 詳細画面へ遷移する (D8)。
 */
export function liveOverlayClickTarget(event: UiEvent): string {
  const sessionId = eventAgentSessionId(event);
  if (sessionId) return `/dashboard/agent-sessions/${encodeURIComponent(sessionId)}`;
  if (event.task_id) return `/dashboard/operations/tasks/${event.task_id}`;
  if (event.approval_id) return `/dashboard/approvals/${event.approval_id}`;
  return "/dashboard/activity";
}

/**
 * LocalStorage から Live Overlay トグル設定を読み込む (Phase D9 / instruction.md §22).
 *
 * 設定がないときはデフォルト (すべて true) を返す。
 */
export function readLiveOverlayToggles(): OverlayToggles {
  if (typeof window === "undefined") return DEFAULT_TOGGLES;
  try {
    const raw = window.localStorage.getItem("aegis.dashboard.settings");
    if (!raw) return DEFAULT_TOGGLES;
    const parsed = JSON.parse(raw) as Partial<OverlayToggles> & {
      liveOverlayShow?: boolean;
      liveOverlayShowThinking?: boolean;
      liveOverlayShowToolCalls?: boolean;
    };
    return {
      show: parsed.liveOverlayShow ?? DEFAULT_TOGGLES.show,
      showThinking: parsed.liveOverlayShowThinking ?? DEFAULT_TOGGLES.showThinking,
      showToolCalls: parsed.liveOverlayShowToolCalls ?? DEFAULT_TOGGLES.showToolCalls,
    };
  } catch {
    return DEFAULT_TOGGLES;
  }
}

/**
 * Live Overlay — 画面下部に 38px 固定で表示される最重要 1 イベント枠.
 *
 * instruction.md §3, §4, §12, §20, §21:
 * - 位置: position: fixed; bottom: 0; left: 0; right: 0;
 * - 高さ: 38px (固定、展開しない)
 * - 内容: `<strong>● {priority_label}</strong> · {event type} · {message}`
 * - 優先順位: Approval > Error > Tool > Thinking > Progress
 * - クリック: onClick ハンドラで Agent Session / Activity Page 等を開く
 *
 * Phase D8: agent_session_id 単位で group 化し、agent_session 間で最優先を選ぶ
 * (instruction.md §19). 同時に実行されている Agent が複数あっても Overlay は 1 行
 * (instruction.md §19 "そのためOverlayは常に1行。")。
 *
 * Phase D9: instruction.md §22 のトグル (Show / Show thinking / Show tool calls) を
 * localStorage から読み取り、適用する。
 */
export function LiveOverlay({ events, onClick }: LiveOverlayProps) {
  const [toggles, setToggles] = useState<OverlayToggles>(() => readLiveOverlayToggles());

  // localStorage 変更を storage event で拾い、別タブからの設定変更にも追随
  useEffect(() => {
    const handle = (event: StorageEvent) => {
      if (event.key === "aegis.dashboard.settings") setToggles(readLiveOverlayToggles());
    };
    window.addEventListener("storage", handle);
    return () => window.removeEventListener("storage", handle);
  }, []);

  // 設定でイベントを filter (Phase D9 §22)
  const filteredEvents = useMemo(() => {
    if (!toggles.show) return [];
    if (!toggles.showThinking && !toggles.showToolCalls) return events; // 両方 OFF は素通し
    return events.filter((event) => {
      const type = (event.type || event.source_type || "").toLowerCase();
      if (!toggles.showThinking && (type === "agent.thinking" || type === "agent.started")) return false;
      if (!toggles.showToolCalls && (type === "agent.tool.started" || type === "agent.tool.completed" || type === "tool.execution.started" || type === "tool.execution.completed")) return false;
      return true;
    });
  }, [events, toggles]);

  const selected = useMemo(() => pickLiveOverlayEventForAgent(filteredEvents), [filteredEvents]);
  if (!selected) {
    return (
      <div className="live-overlay live-overlay--idle" role="status" aria-label="AEGIS live overlay (idle)">
        <span className="live-overlay__dot" aria-hidden="true">
          <Circle size={10} />
        </span>
        <strong>Live</strong>
        <span className="live-overlay__detail">AEGIS is idle</span>
      </div>
    );
  }
  const priority = liveOverlayPriority(selected);
  const type = selected.type || selected.source_type || "event";
  const message = readableDisplayText(selected.safe_message || selected.message, type);
  const label = OVERLAY_PRIORITY_LABEL[priority] || "Live";
  // DASHBOARD_V3_PLAN.md Phase L6 — layer 識別表示 ("L1: ..." / "L2: ..." / "L3: ..." / "MCP: ...")
  const layer = inferLayerFromEvent(type);
  const layerTag = `${layer}:`;
  const eventId = selected.event_id || `${type}-${selected.generated_at}`;
  const sessionId = eventAgentSessionId(selected);
  const sessionTag = sessionId ? sessionId.slice(0, 12) : null;
  const handleClick = onClick ? () => onClick(selected) : undefined;
  return (
    <button
      type="button"
      className="live-overlay"
      role="status"
      aria-label={`AEGIS live overlay — ${layerTag} ${label}: ${type}${sessionTag ? ` (session ${sessionTag})` : ""}`}
      data-event-id={eventId}
      data-priority={priority}
      data-severity={selected.severity || "info"}
      data-agent-session-id={sessionId || ""}
      data-layer={layer}
      onClick={handleClick}
    >
      <span className="live-overlay__dot" aria-hidden="true">
        <Circle size={10} />
      </span>
      <strong>{label}</strong>
      <span className="live-overlay__sep">·</span>
      <code className="live-overlay__layer" data-testid="live-overlay-layer">{layerTag}</code>
      {sessionTag ? (
        <>
          <span className="live-overlay__sep">·</span>
          <code className="live-overlay__type" data-testid="live-overlay-session">{sessionTag}</code>
        </>
      ) : null}
      <span className="live-overlay__sep">·</span>
      <code className="live-overlay__type">{type}</code>
      <span className="live-overlay__sep">·</span>
      <span className="live-overlay__detail">{message}</span>
    </button>
  );
}
