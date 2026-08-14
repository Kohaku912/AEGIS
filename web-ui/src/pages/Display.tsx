import { useCallback, useEffect, useMemo, useState } from "react";
import { CognitiveField } from "../components/cognitive-field/CognitiveField";
import { StatusBadge } from "../components/StatusBadge";
import { useOverviewStream } from "../api/useOverviewStream";
import {
  attentionItems,
  buildDisplayDirectorState,
  mapUiEventToVisualEvent,
  missionPhase,
  normalizeStatus,
  recentDisplayEvents,
  serverLabel,
  serverNeedsDetail,
  summarizeUserState
} from "../displayModel";
import type { ServerItem, UiEvent, UiOverview, VisualEvent } from "../types";

export function Display({ overview: initialOverview }: { overview: UiOverview }) {
  const [overview, setOverview] = useState(initialOverview);
  const [events, setEvents] = useState<UiEvent[]>([]);
  const [visualEvents, setVisualEvents] = useState<VisualEvent[]>([]);

  useEffect(() => setOverview(initialOverview), [initialOverview]);

  const onStreamEvent = useCallback((event: UiEvent | UiOverview) => {
    if ("schema_version" in event) {
      setOverview(event);
      return;
    }
    setEvents((items) => [event, ...items].slice(0, 10));
    const visual = mapUiEventToVisualEvent(event);
    setVisualEvents((items) => [visual, ...items.filter((item) => item.expiresAt > Date.now())].slice(0, 12));
  }, []);
  useOverviewStream(onStreamEvent, true, "display");

  const core = overview.core.data;
  const servers = overview.servers.data.items || [];
  const task = overview.current_task.data;
  const attention = attentionItems(overview);
  const activeServerId = String(task.capability_id || "").split(".", 1)[0];
  const phase = missionPhase(overview);
  const userState = summarizeUserState(overview);
  const director = buildDisplayDirectorState(overview, events, visualEvents);
  const recentDirectorItems = useMemo(() => {
    const unique = new Map<string, (typeof director.dock)[number]>();
    for (const item of [...director.dock, ...director.ambient]) {
      if (!unique.has(item.id)) unique.set(item.id, item);
    }
    return recentDisplayEvents(overview, [...unique.values()]);
  }, [director.ambient, director.dock, overview]);

  return (
    <main
      className="display-shell"
      data-phase={phase}
      data-testid="display-shell"
      data-priority={director.takeover?.priority || "P3"}
      data-offline={director.offline}
      data-stale={director.stale}
      data-privacy={director.privacyMode}
    >
      <div className="display-state-ribbon" aria-label="Display state">
        <span>{director.offline ? "OFFLINE SNAPSHOT" : director.stale ? "STALE SNAPSHOT" : "LIVE DISPLAY"}</span>
        {director.privacyMode ? <span>PRIVACY MODE</span> : null}
      </div>
      <div className="display-global-hud" aria-label="Display HUD">
        <strong>AEGIS</strong>
        <span>{phase}</span>
        <span>{servers.filter((server) => normalizeStatus(server.status) === "ONLINE").length}/{servers.length || 0} online</span>
      </div>
      {director.takeover ? (
        <section className="display-takeover" data-priority={director.takeover.priority} aria-label="Display takeover">
          <span className="display-kicker">{director.takeover.priority} / {director.takeover.severity}</span>
          <strong>{redact(director.takeover.title, director.privacyMode)}</strong>
          <p>{director.privacyMode ? "Private information hidden." : director.takeover.message}</p>
        </section>
      ) : null}
      {director.overlays.filter((item) => item.priority === "P0" || item.priority === "P1").length ? (
        <aside className="display-overlay-stack" aria-label="Critical overlays">
          {director.overlays.filter((item) => item.priority === "P0" || item.priority === "P1").map((item) => (
            <article className="display-overlay" data-priority={item.priority} data-severity={item.severity} key={item.id}>
              <span>{item.priority}</span>
              <strong>{item.title}</strong>
              <p>{item.message}</p>
            </article>
          ))}
        </aside>
      ) : null}
      {director.overlays.filter((item) => item.priority === "P2").length ? (
        <aside className="display-warning-strip" aria-label="Warnings">
          {director.overlays.filter((item) => item.priority === "P2").map((item) => (
            <div className="display-warning-item" data-severity={item.severity} key={item.id}>
              <span className="display-warning-dot" aria-hidden="true" />
              <strong>{item.title}</strong>
            </div>
          ))}
        </aside>
      ) : null}
      <header className="display-top">
        <section className="display-card display-operation" aria-label="Current Operation">
          <span className="display-kicker">Current Operation</span>
          <h1>{redact(task.title || "No active task", director.privacyMode)}</h1>
          <p>{redact(task.current_action || task.next_action || task.blocked_reason || "Waiting for a meaningful signal.", director.privacyMode)}</p>
          <div className="display-meta">
            <StatusBadge status={String(core.mode || "IDLE")} />
            <span>{phase}</span>
          </div>
        </section>
        <div className="display-side-stack">
          <section className="display-card display-user-state" aria-label="User State" data-stale={userState.freshness === "STALE"}>
            <div className="display-user-state__heading">
              <span className="display-kicker">User State</span>
              <span className="display-user-state__freshness">{userState.freshness}</span>
            </div>
            <dl>
              <UserStateMetric label="Where" value={director.privacyMode ? "Hidden" : userState.where} confidence={userState.whereConfidence} />
              <UserStateMetric label="Attention" value={director.privacyMode ? "Hidden" : userState.attention} confidence={userState.attentionConfidence} />
              <UserStateMetric label="Activity" value={director.privacyMode ? "Hidden" : userState.activity} confidence={userState.activityConfidence} />
            </dl>
          </section>
          {attention.filter((item) => item.severity === "critical").length ? (
            <section className="display-card display-attention" aria-label="Critical Attention">
              <span className="display-kicker">Critical</span>
              {attention.filter((item) => item.severity === "critical").slice(0, 3).map((item) => (
                <article className="display-attention__item" data-severity={item.severity} key={item.id}>
                  <strong>{redact(item.title, director.privacyMode)}</strong>
                  <p>{redact(item.message || item.recovery_hint || "Review this signal.", director.privacyMode)}</p>
                </article>
              ))}
            </section>
          ) : null}
        </div>
      </header>

      <section className="display-core-stage" aria-label="AEGIS core">
        <CognitiveField
          mode={String(core.mode || "IDLE")}
          health={String(core.health || "ONLINE")}
          activityLevel={Number(core.activity_level || 1)}
          confidence={String(core.confidence || "medium")}
          servers={servers}
          visualEvents={visualEvents}
          activeServerId={activeServerId}
          nextServerId={nextServerId(task.steps)}
          approvalServerIds={(overview.approvals.data.pending || []).map((approval) => String(approval.capability_id || "").split(".", 1)[0])}
          currentAction={task.current_action || task.title}
          nextAction={task.next_action}
        />
      </section>

      <section className="display-bottom">
        <div className="display-card display-phase">
          <span className="display-kicker">Mission Phase</span>
          <strong>{phase}</strong>
          <p>{redact(String(core.active_goal || task.title || "Standing by."), director.privacyMode)}</p>
        </div>
        <div className="display-card display-events" aria-label="Recent Events">
          <span className="display-kicker">Recent Events</span>
          {recentDirectorItems.length ? (
            recentDirectorItems.map((item) => (
              <div className="event-row" data-severity={item.severity || "info"} data-priority={item.priority} key={item.id}>
                <span>{item.priority}</span>
                <strong>{redact(item.message || item.title, director.privacyMode)}</strong>
              </div>
            ))
          ) : (
            <div className="event-row" data-severity={director.offline || director.stale ? "warning" : "normal"}>
              <span>{director.offline ? "offline" : director.stale ? "stale" : "stream"}</span>
              <strong>{director.offline ? "Showing last known snapshot" : director.stale ? "Waiting for fresh events" : "Waiting for live events"}</strong>
            </div>
          )}
        </div>
      </section>

      <ServerRail servers={servers} activeServerId={activeServerId} />
    </main>
  );
}

function UserStateMetric({ label, value, confidence }: { label: string; value: string; confidence: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
      <small>{confidence}</small>
    </div>
  );
}

function ServerRail({ servers, activeServerId }: { servers: ServerItem[]; activeServerId: string }) {
  const ordered = useMemo(() => [...servers].sort((a, b) => serverLabel(a.server_id).localeCompare(serverLabel(b.server_id))), [servers]);
  return (
    <footer className="server-rail" aria-label="Server rail">
      {ordered.map((server) => {
        const expanded = serverNeedsDetail(server, activeServerId);
        return (
          <article className="server-rail__item" data-status={normalizeStatus(server.status)} data-expanded={expanded} key={server.server_id}>
            <span className="server-dot" aria-hidden="true" />
            <strong>{serverLabel(server.server_id)}</strong>
            {expanded ? <span className="server-rail__detail">{server.status_detail || server.degraded_reason || server.recovery_hint || normalizeStatus(server.status)}</span> : null}
          </article>
        );
      })}
    </footer>
  );
}

function nextServerId(steps: Array<Record<string, unknown>> | undefined): string {
  const pending = (steps || []).find((step) => String(step.status || "").toLowerCase() === "pending" || String(step.status || "").toLowerCase() === "ready");
  const capabilityId = String(pending?.capability_id || "");
  return capabilityId.split(".", 1)[0] || "";
}

function redact(value: string, privacyMode: boolean): string {
  return privacyMode ? "Private information hidden" : value;
}
