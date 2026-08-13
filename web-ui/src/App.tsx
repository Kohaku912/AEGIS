import { ChevronDown, ChevronRight, Code2, UserRound } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchOverview, fetchResourceEntity } from "./api/client";
import { useOverviewStream, type StreamState } from "./api/useOverviewStream";
import { isUiActivityNoise } from "./activityNoise";
import { ChatDrawer } from "./components/ChatDrawer";
import { CommandPalette } from "./components/CommandPalette";
import { GlobalInspector } from "./components/GlobalInspector";
import { GlobalStatusBar } from "./components/GlobalStatusBar";
import { LiveActivityDrawer } from "./components/LiveActivityDrawer";
import { StatusBadge } from "./components/StatusBadge";
import { UiState } from "./components/UiState";
import { entitiesFromOverview } from "./entityModel";
import { navigation, pageDefinition, routeState, type DomainId } from "./navigation";
import { AgentStatePage } from "./pages/AgentStatePage";
import { AllSettingsPage } from "./pages/AllSettingsPage";
import { Approvals } from "./pages/Approvals";
import { AttentionPage } from "./pages/AttentionPage";
import { AuditPage } from "./pages/AuditPage";
import { AutonomousPage } from "./pages/AutonomousPage";
import { BehavioralReportsPage } from "./pages/BehavioralReportsPage";
import { CapabilityCatalogPage } from "./pages/CapabilityCatalogPage";
import { DashboardSettingsPage } from "./pages/DashboardSettingsPage";
import { DesiresPage } from "./pages/DesiresPage";
import { DevicePage } from "./pages/DevicePage";
import { DiagnosticsPage } from "./pages/DiagnosticsPage";
import { Display } from "./pages/Display";
import { DomainPage } from "./pages/DomainPage";
import { HomePage } from "./pages/HomePage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { LearningPage } from "./pages/LearningPage";
import { LLMUsagePage } from "./pages/LLMUsagePage";
import { LogsPage } from "./pages/LogsPage";
import { MindMemory } from "./pages/MindMemory";
import { ModelsPromptsPage } from "./pages/ModelsPromptsPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { OperationsPage } from "./pages/OperationsPage";
import { PerformancePage } from "./pages/PerformancePage";
import { PersonalAiPage } from "./pages/PersonalAiPage";
import { PromptAnalysisPage } from "./pages/PromptAnalysisPage";
import { RawActivityPage } from "./pages/RawActivityPage";
import { Settings } from "./pages/Settings";
import { SocialPage } from "./pages/SocialPage";
import { Systems } from "./pages/Systems";
import { TimelinePage } from "./pages/TimelinePage";
import { UserStatePage } from "./pages/UserStatePage";
import { Work } from "./pages/Work";
import { formatDateTime, formatRelative, messages } from "./i18n";
import type { EntitySummary, UiEvent, UiOverview } from "./types";

export function App() {
  const displayMode = window.location.pathname.startsWith("/display");
  const queryClient = useQueryClient();
  const [chatOpen, setChatOpen] = useState(window.location.pathname === "/chat");
  const [recentEvents, setRecentEvents] = useState<UiEvent[]>([]);
  const [route, setRoute] = useState(() => routeState(window.location.pathname));
  const [expanded, setExpanded] = useState<DomainId>(route.domain);
  const detailId = route.detailId || "";
  const [selectedEntity, setSelectedEntity] = useState<EntitySummary>();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [navCollapsed, setNavCollapsed] = useState(() => window.localStorage.getItem("aegis.nav-collapsed") === "1");
  const [developerMode, setDeveloperMode] = useState(() => window.localStorage.getItem("aegis.developer-mode") === "1");
  const [density, setDensity] = useState(() => window.localStorage.getItem("aegis.density") || "standard");
  const [pinnedEntities, setPinnedEntities] = useState<EntitySummary[]>(() => readPins());
  const [streamState, setStreamState] = useState<StreamState>("connecting");

  const followRelation = useCallback(async (type: string, id: string) => {
    const resources: Record<string, string> = {
      task: "tasks",
      approval: "approvals",
      capability: "capabilities",
      server: "servers",
      event: "events",
      memory: "memories",
      audit: "audit",
      conversation: "events",
      setting: "settings",
    };
    try {
      setSelectedEntity(await fetchResourceEntity(resources[type] || `${type}s`, id));
    } catch (error) {
      setRecentEvents((items) =>
        [
          {
            type: "ui.related-resource.failed",
            source_type: "dashboard",
            generated_at: Date.now(),
            source_updated_at: Date.now(),
            severity: "warning",
            message: error instanceof Error ? error.message : String(error),
            payload: {},
          },
          ...items,
        ].slice(0, 40),
      );
    }
  }, []);

  const query = useQuery({
    queryKey: ["ui-overview", displayMode ? "display" : "dashboard"],
    queryFn: () => fetchOverview(displayMode ? "display" : "dashboard"),
    refetchInterval: Number(window.localStorage.getItem("aegis.refresh-ms") || (displayMode ? 15_000 : 30_000)),
  });

  const onEvent = useCallback(
    (event: UiEvent) => {
      if ("schema_version" in event) {
        void queryClient.invalidateQueries({ queryKey: ["ui-overview"] });
        return;
      }
      if (isUiActivityNoise(event)) return;
      setRecentEvents((items) => [event, ...items.filter((item) => item.event_id !== event.event_id)].slice(0, 40));
      void queryClient.invalidateQueries({ queryKey: ["ui-overview"] });
    },
    [queryClient],
  );
  const onStreamState = useCallback((state: StreamState) => setStreamState(state), []);
  useOverviewStream(onEvent, !displayMode, "dashboard", onStreamState);

  const navigate = useCallback((path: string) => {
    window.history.pushState(null, "", path);
    const next = routeState(path.split("?", 1)[0]);
    setRoute(next);
    setExpanded(next.domain);
  }, []);

  useEffect(() => {
    const onPopState = () => {
      const next = routeState(window.location.pathname);
      setRoute(next);
      setExpanded(next.domain);
      setChatOpen(window.location.pathname === "/chat");
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("popstate", onPopState);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("popstate", onPopState);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  if (query.isLoading) return <LoadingDisplay displayMode={displayMode} />;
  if (query.isError || !query.data) {
    return <ErrorDisplay message={query.error instanceof Error ? query.error.message : "Overview unavailable"} />;
  }
  if (displayMode) return <Display overview={query.data} />;

  const overview = query.data;
  const definition = pageDefinition(route.page);
  const entities = entitiesFromOverview(overview, recentEvents);

  return (
    <div
      className="master-shell"
      data-domain={route.domain}
      data-developer-mode={developerMode}
      data-density={density}
      data-nav-collapsed={navCollapsed}
    >
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <aside className="master-nav">
        <div className="brand">
          <span className="brand__name">AEGIS</span>
          <span className="brand__sub">{messages.appSubtitle}</span>
        </div>
        <button
          type="button"
          className="nav-collapse-toggle"
          onClick={() =>
            setNavCollapsed((value) => {
              const next = !value;
              window.localStorage.setItem("aegis.nav-collapsed", next ? "1" : "0");
              return next;
            })
          }
        >
          {navCollapsed ? "展開" : "折りたたみ"}
        </button>
        {!navCollapsed ? (
          <nav aria-label="AEGIS main navigation">
            {navigation.map((domain, index) => {
              const Icon = domain.icon;
              const open = expanded === domain.id;
              return (
                <section className="nav-domain" data-open={open} key={domain.id}>
                  <button
                    type="button"
                    aria-expanded={open}
                    aria-current={route.domain === domain.id ? "page" : undefined}
                    onClick={() => setExpanded(open ? route.domain : domain.id)}
                  >
                    <span className="nav-domain__number">{String(index + 1).padStart(2, "0")}</span>
                    <Icon size={16} />
                    <strong>{domain.label}</strong>
                    {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  </button>
                  {open ? (
                    <div className="nav-domain__children">
                      {domain.pages
                        .filter((page) => developerMode || !page.developerOnly)
                        .map((page) => (
                          <button
                            type="button"
                            aria-current={route.page === page.id ? "page" : undefined}
                            onClick={() => navigate(page.path)}
                            key={page.id}
                          >
                            {page.label}
                          </button>
                        ))}
                    </div>
                  ) : null}
                </section>
              );
            })}
          </nav>
        ) : null}
        <footer>
          <span>Passkey session</span>
          <strong>Policy protected</strong>
        </footer>
      </aside>

      <div className="master-workspace">
        <GlobalStatusBar
          overview={overview}
          onOpenSearch={() => setPaletteOpen(true)}
          onOpenChat={() => setChatOpen(true)}
          onNavigate={navigate}
        />
        <header className="workspace-heading">
          <div>
            <span>{definition.domain.label}</span>
            <h1>{definition.page.label}</h1>
          </div>
          <div>
            <StatusBadge status={String(overview.core.data.health || "DEGRADED")} />
            <span className="workspace-heading__freshness">
              {messages.updated}: {formatDateTime(overview.generated_at)} ({formatRelative(overview.generated_at)})
            </span>
            <button
              className="icon-button developer-toggle"
              type="button"
              aria-pressed={developerMode}
              onClick={() =>
                setDeveloperMode((value) => {
                  const next = !value;
                  window.localStorage.setItem("aegis.developer-mode", next ? "1" : "0");
                  return next;
                })
              }
              title={messages.developerMode}
              aria-label={messages.developerMode}
            >
              <Code2 size={16} />
            </button>
            <label className="density-control">
              <span>Density</span>
              <select
                aria-label="Display density"
                value={density}
                onChange={(event) => {
                  const next = event.currentTarget.value;
                  setDensity(next);
                  window.localStorage.setItem("aegis.density", next);
                }}
              >
                <option value="comfortable">Comfortable</option>
                <option value="standard">Standard</option>
                <option value="compact">Compact</option>
              </select>
            </label>
            <a className="user-chip" href="/dashboard/security/passkeys">
              <UserRound size={15} />
              <span>Admin</span>
            </a>
          </div>
        </header>
        {streamState === "offline" || streamState === "malformed" ? (
          <div className="data-state data-state--warning" role="status">
            {streamState === "offline"
              ? "リアルタイム接続が切断されています。自動再接続中です。"
              : "不正な更新を検出しました。最新スナップショットから復旧します。"}
          </div>
        ) : null}
        <main className="master-content" id="main-content" tabIndex={-1}>
          <Page
            pageId={route.page}
            overview={overview}
            recentEvents={recentEvents}
            onSelect={setSelectedEntity}
            onNavigate={navigate}
            pathname={window.location.pathname}
            detailId={detailId}
            pinnedEntities={pinnedEntities}
            developerMode={developerMode}
          />
        </main>
      </div>

      <GlobalInspector
        entity={selectedEntity}
        onClose={() => setSelectedEntity(undefined)}
        onFollowRelation={followRelation}
        pinned={Boolean(selectedEntity && pinnedEntities.some((item) => item.type === selectedEntity.type && item.id === selectedEntity.id))}
        onTogglePin={(entity) => setPinnedEntities((items) => togglePin(items, entity))}
        developerMode={developerMode}
      />
      <LiveActivityDrawer events={recentEvents} />
      <ChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} />
      <CommandPalette
        open={paletteOpen}
        onOpenChange={setPaletteOpen}
        navigate={navigate}
        onSelectEntity={setSelectedEntity}
      />
    </div>
  );
}

function Page({
  pageId,
  overview,
  recentEvents,
  onSelect,
  onNavigate,
  pathname = "",
  detailId = "",
  developerMode,
}: {
  pageId: string;
  overview: UiOverview;
  recentEvents: UiEvent[];
  onSelect: (entity: EntitySummary) => void;
  onNavigate: (path: string) => void;
  pathname?: string;
  detailId?: string;
  pinnedEntities: EntitySummary[];
  developerMode: boolean;
}) {
  if (pageId === "home" || pageId === "command-center") {
    return <HomePage overview={overview} onNavigate={onNavigate} />;
  }
  if (pageId === "attention") return <AttentionPage overview={overview} />;
  if (pageId === "tasks") return <Work overview={overview} />;
  if (pageId === "approvals") return <Approvals overview={overview} />;
  if (pageId === "autonomous") return <AutonomousPage overview={overview} />;
  if (pageId === "desires") return <DesiresPage overview={overview} />;
  if (pageId === "agent-state") return <AgentStatePage overview={overview} />;
  if (pageId === "memory") return <MindMemory overview={overview} />;
  if (pageId === "learning") return <LearningPage overview={overview} />;
  if (pageId === "capability-catalog") return <CapabilityCatalogPage />;
  if (pageId === "llm-usage") return <LLMUsagePage overview={overview} />;
  if (pageId === "prompt-analysis") return <PromptAnalysisPage overview={overview} />;
  if (pageId === "llm-config" || pageId === "models-prompts") return <ModelsPromptsPage />;
  if (pageId === "servers") return <Systems overview={overview} />;
  if (pageId === "pc") return <DevicePage overview={overview} serverId="pc-server" />;
  if (pageId === "browser") return <DevicePage overview={overview} serverId="browser-server" />;
  if (pageId === "android") return <DevicePage overview={overview} serverId="android-server" />;
  if (pageId === "room") return <DevicePage overview={overview} serverId="room-server" />;
  if (pageId === "agora" || pageId === "social" || pageId === "conversations") {
    return <SocialPage overview={overview} developerMode={developerMode} />;
  }
  if (pageId === "operations") {
    return (
      <OperationsPage
        overview={overview}
        developerMode={developerMode}
        pathname={pathname}
        detailId={detailId}
        onNavigate={onNavigate}
      />
    );
  }
  if (pageId === "logs") {
    return <LogsPage overview={overview} />;
  }
  if (pageId === "raw-activity" || pageId === "events") {
    return (
      <RawActivityPage
        overview={overview}
        recentEvents={recentEvents}
        developerMode={developerMode}
        pathname={pathname}
        onNavigate={onNavigate}
      />
    );
  }
  if (pageId === "incidents" || pageId === "errors") {
    return (
      <IncidentsPage
        overview={overview}
        pathname={pathname}
        detailId={detailId}
        developerMode={developerMode}
        onNavigate={onNavigate}
      />
    );
  }
  if (pageId === "performance") return <PerformancePage overview={overview} developerMode={developerMode} />;
  if (pageId === "behavioral-reports") return <BehavioralReportsPage overview={overview} />;
  if (pageId === "notifications") return <NotificationsPage overview={overview} />;
  if (pageId === "audit" || pageId === "activity") return <AuditPage />;
  if (pageId === "personal-ai") return <PersonalAiPage overview={overview} />;
  if (pageId === "timeline") return <TimelinePage overview={overview} />;
  if (pageId === "user-state") return <UserStatePage overview={overview} />;
  if (pageId === "settings-all") return <AllSettingsPage />;
  if (pageId === "diagnostics") return <DiagnosticsPage overview={overview} />;
  if (pageId === "dashboard-settings") return <DashboardSettingsPage />;
  if (pageId.startsWith("settings-")) {
    return <Settings overview={overview} sectionId={pageId.replace("settings-", "")} />;
  }
  return <DomainPage pageId={pageId} overview={overview} events={recentEvents} onSelect={onSelect} developerMode={developerMode} />;
}

function readPins(): EntitySummary[] {
  try {
    const value = JSON.parse(window.localStorage.getItem("aegis.pins") || "[]");
    return Array.isArray(value) ? value.slice(0, 12) : [];
  } catch {
    return [];
  }
}

function togglePin(items: EntitySummary[], entity: EntitySummary): EntitySummary[] {
  const exists = items.some((item) => item.type === entity.type && item.id === entity.id);
  const next = exists
    ? items.filter((item) => item.type !== entity.type || item.id !== entity.id)
    : [...items, { ...entity, data: {} }].slice(-12);
  window.localStorage.setItem("aegis.pins", JSON.stringify(next));
  return next;
}

function LoadingDisplay({ displayMode }: { displayMode: boolean }) {
  return (
    <main className={displayMode ? "display-shell center-shell" : "master-shell center-shell"}>
      <UiState kind="loading" title="Loading AEGIS" message="Synchronizing Runtime managers and the spatial information model." />
    </main>
  );
}

function ErrorDisplay({ message }: { message: string }) {
  const lower = message.toLowerCase();
  const kind =
    lower.includes("401") || lower.includes("unauthorized")
      ? "unauthorized"
      : lower.includes("403") || lower.includes("forbidden")
        ? "permission"
        : lower.includes("fresh")
          ? "fresh-auth"
          : "error";
  const action =
    kind === "unauthorized" || kind === "fresh-auth" ? { label: "Authenticate with passkey", href: "/auth/login" } : undefined;
  return (
    <main className="display-shell center-shell">
      <UiState
        kind={kind}
        title={kind === "fresh-auth" ? "Fresh passkey authentication required" : "AEGIS unavailable"}
        message={message}
        actionLabel={action?.label}
        actionHref={action?.href}
      />
    </main>
  );
}
