import { Bell, ChevronDown, ChevronRight, Code2, Command as CommandIcon, MessageSquare, Plus, UserRound } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchOverview, fetchResourceEntity } from "./api/client";
import { useOverviewStream } from "./api/useOverviewStream";
import { isUiActivityNoise } from "./activityNoise";
import { ChatDrawer } from "./components/ChatDrawer";
import { CommandPalette } from "./components/CommandPalette";
import { GlobalInspector } from "./components/GlobalInspector";
import { GlobalSearch } from "./components/GlobalSearch";
import { LiveActivityDrawer } from "./components/LiveActivityDrawer";
import { StatusBadge } from "./components/StatusBadge";
import { UiState } from "./components/UiState";
import { entitiesFromOverview } from "./entityModel";
import { navigation, pageDefinition, routeState, type DomainId } from "./navigation";
import { ActivityPage } from "./pages/ActivityPage";
import { Approvals } from "./pages/Approvals";
import { CapabilityCatalogPage } from "./pages/CapabilityCatalogPage";
import { CommandCenter } from "./pages/CommandCenter";
import { Display } from "./pages/Display";
import { DomainPage } from "./pages/DomainPage";
import { JudgmentPage } from "./pages/JudgmentPage";
import { MindMemory } from "./pages/MindMemory";
import { LLMUsagePage } from "./pages/LLMUsagePage";
import { ModelsPromptsPage } from "./pages/ModelsPromptsPage";
import { OpenLoopsPage } from "./pages/OpenLoopsPage";
import { OperationsPage } from "./pages/OperationsPage";
import { PolicySimulationPage } from "./pages/PolicySimulationPage";
import { RuleManagementPage } from "./pages/RuleManagementPage";
import { Settings } from "./pages/Settings";
import { SocialPage } from "./pages/SocialPage";
import { Systems } from "./pages/Systems";
import type { EntitySummary, UiEvent, UiOverview } from "./types";

export function App() {
  const displayMode = window.location.pathname.startsWith("/display");
  const queryClient = useQueryClient();
  const [chatOpen, setChatOpen] = useState(window.location.pathname === "/chat");
  const [recentEvents, setRecentEvents] = useState<UiEvent[]>([]);
  const [route, setRoute] = useState(() => routeState(window.location.pathname));
  const [expanded, setExpanded] = useState<DomainId>(route.domain);
  const [selectedEntity, setSelectedEntity] = useState<EntitySummary>();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [developerMode, setDeveloperMode] = useState(() => window.localStorage.getItem("aegis.developer-mode") === "1");
  const [density, setDensity] = useState(() => window.localStorage.getItem("aegis.density") || "standard");
  const [pinnedEntities, setPinnedEntities] = useState<EntitySummary[]>(() => readPins());
  const followRelation = useCallback(async (type: string, id: string) => {
    const resources: Record<string, string> = { task: "tasks", approval: "approvals", capability: "capabilities", server: "servers", event: "events", memory: "memories", conversation: "events" };
    try { setSelectedEntity(await fetchResourceEntity(resources[type] || `${type}s`, id)); }
    catch { /* Keep the current entity visible when the related record is no longer retained. */ }
  }, []);
  const query = useQuery({
    queryKey: ["ui-overview", displayMode ? "display" : "dashboard"],
    queryFn: () => fetchOverview(displayMode ? "display" : "dashboard"),
    refetchInterval: displayMode ? 15_000 : 30_000
  });
  const onEvent = useCallback((event: UiEvent) => {
    if ("schema_version" in event) {
      void queryClient.invalidateQueries({ queryKey: ["ui-overview"] });
      return;
    }
    if (isUiActivityNoise(event)) {
      return;
    }
    setRecentEvents((items) => [event, ...items.filter((item) => item.event_id !== event.event_id)].slice(0, 40));
    void queryClient.invalidateQueries({ queryKey: ["ui-overview"] });
  }, [queryClient]);
  useOverviewStream(onEvent, !displayMode);

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
    return () => { window.removeEventListener("popstate", onPopState); window.removeEventListener("keydown", onKeyDown); };
  }, []);

  if (query.isLoading) return <LoadingDisplay displayMode={displayMode} />;
  if (query.isError || !query.data) return <ErrorDisplay message={query.error instanceof Error ? query.error.message : "Overview unavailable"} />;
  if (displayMode) return <Display overview={query.data} />;

  const overview = query.data;
  const definition = pageDefinition(route.page);
  const entities = entitiesFromOverview(overview, recentEvents);
  const attentionCount = (overview.attention.data.items || []).length;
  const approvalCount = overview.approvals.data.pending_count || 0;
  return (
    <div className="master-shell" data-domain={route.domain} data-developer-mode={developerMode} data-density={density}>
      <aside className="master-nav">
        <div className="brand"><span className="brand__name">AEGIS</span><span className="brand__sub">Master Control Plane</span></div>
        <nav aria-label="AEGIS management domains">
          {navigation.map((domain, index) => {
            const Icon = domain.icon;
            const open = expanded === domain.id;
            return (
              <section className="nav-domain" data-open={open} key={domain.id}>
                <button type="button" aria-expanded={open} aria-current={route.domain === domain.id ? "page" : undefined} onClick={() => setExpanded(open ? route.domain : domain.id)}>
                  <span className="nav-domain__number">{String(index + 1).padStart(2, "0")}</span><Icon size={16} /><strong>{domain.label}</strong>{open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </button>
                {open ? <div className="nav-domain__children">{domain.pages.map((page) => <button type="button" aria-current={route.page === page.id ? "page" : undefined} onClick={() => navigate(page.path)} key={page.id}>{page.label}</button>)}</div> : null}
              </section>
            );
          })}
        </nav>
        <footer><span>Passkey session</span><strong>Policy guarded</strong></footer>
      </aside>

      <div className="master-workspace">
        <header className="master-topbar">
          <GlobalSearch entities={entities} onSelect={setSelectedEntity} />
          <button className="palette-trigger" type="button" onClick={() => setPaletteOpen(true)}><CommandIcon size={15} /><span>Commands</span><kbd>Ctrl K</kbd></button>
          <button className="topbar-command" type="button" onClick={() => navigate("/dashboard/work/tasks?create=1")}><Plus size={15} />Create Task</button>
          <button className="topbar-signal" type="button" onClick={() => navigate("/dashboard/attention")}><Bell size={15} /><span>{attentionCount}</span></button>
          <button className="topbar-signal" type="button" onClick={() => navigate("/dashboard/governance/approvals")}><StatusBadge status={approvalCount ? "WAITING" : "READY"} /><span>{approvalCount}</span></button>
          <button className="icon-button" type="button" onClick={() => setChatOpen(true)} title="Open AEGIS chat"><MessageSquare size={16} /></button>
          <button className="icon-button developer-toggle" type="button" aria-pressed={developerMode} onClick={() => setDeveloperMode((value) => { const next = !value; window.localStorage.setItem("aegis.developer-mode", next ? "1" : "0"); return next; })} title="Toggle Developer Mode"><Code2 size={16} /></button>
          <label className="density-control"><span>Density</span><select aria-label="Interface density" value={density} onChange={(event) => { const next = event.currentTarget.value; setDensity(next); window.localStorage.setItem("aegis.density", next); }}><option value="comfortable">Comfortable</option><option value="standard">Standard</option><option value="compact">Compact</option></select></label>
          <a className="user-chip" href="/dashboard/security/passkeys"><UserRound size={15} /><span>Admin</span></a>
        </header>
        <header className="workspace-heading"><div><span>{definition.domain.label}</span><h1>{definition.page.label}</h1></div><div><StatusBadge status={String(overview.core.data.health || "ONLINE")} /><span className="workspace-heading__freshness">Updated {new Date(overview.generated_at).toLocaleTimeString()}</span></div></header>
        <main className="master-content">
          <Page pageId={route.page} overview={overview} recentEvents={recentEvents} onSelect={setSelectedEntity} pinnedEntities={pinnedEntities} developerMode={developerMode} />
        </main>
      </div>

      <GlobalInspector entity={selectedEntity} onClose={() => setSelectedEntity(undefined)} onFollowRelation={followRelation} pinned={Boolean(selectedEntity && pinnedEntities.some((item) => item.type === selectedEntity.type && item.id === selectedEntity.id))} onTogglePin={(entity) => setPinnedEntities((items) => togglePin(items, entity))} developerMode={developerMode} />
      <LiveActivityDrawer events={recentEvents} />
      <ChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} />
      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} navigate={navigate} />
    </div>
  );
}

function Page({ pageId, overview, recentEvents, onSelect, pinnedEntities, developerMode }: { pageId: string; overview: UiOverview; recentEvents: UiEvent[]; onSelect: (entity: EntitySummary) => void; pinnedEntities: EntitySummary[]; developerMode: boolean }) {
  if (pageId === "command-center") return <CommandCenter overview={overview} recentEvents={recentEvents} pinnedEntities={pinnedEntities} onSelect={onSelect} developerMode={developerMode} />;
  if (pageId === "open-loops" || pageId === "tasks" || pageId === "plans" || pageId === "commitments") {
    return <OpenLoopsPage overview={overview} developerMode={developerMode} />;
  }
  if (pageId === "goals") return <JudgmentPage overview={overview} developerMode={developerMode} focus="goals" />;
  if (pageId === "continuations") return <JudgmentPage overview={overview} developerMode={developerMode} focus="continuations" />;
  if (pageId === "initiative") return <JudgmentPage overview={overview} developerMode={developerMode} focus="initiative" />;
  if (pageId === "decision-context") return <JudgmentPage overview={overview} developerMode={developerMode} focus="decision-context" />;
  if (pageId === "repairs" || pageId === "errors") return <JudgmentPage overview={overview} developerMode={developerMode} focus="repairs" />;
  if (pageId === "reports") return <JudgmentPage overview={overview} developerMode={developerMode} focus="reports" />;
  if (pageId === "situation" || pageId === "user-model") {
    return <JudgmentPage overview={overview} developerMode={developerMode} focus="situation" />;
  }
  if (pageId === "operations" || pageId === "capability-executions") {
    return <OperationsPage overview={overview} developerMode={developerMode} />;
  }
  if (pageId === "social" || pageId === "conversations") {
    return <SocialPage overview={overview} developerMode={developerMode} />;
  }
  if (pageId === "approvals") return <Approvals overview={overview} />;
  if (pageId === "capability-catalog") return <CapabilityCatalogPage />;
  if (pageId === "servers") return <Systems overview={overview} />;
  if (pageId === "memory") return <MindMemory overview={overview} />;
  if (pageId === "activity") return <ActivityPage overview={overview} recentEvents={recentEvents} />;
  if (pageId === "llm-usage") return <LLMUsagePage overview={overview} />;
  if (pageId === "policy-simulation") return <PolicySimulationPage />;
  if (pageId === "models-prompts") return <ModelsPromptsPage />;
  if (pageId === "schedule") return <RuleManagementPage kind="hooks" />;
  if (pageId === "delegation") return <RuleManagementPage kind="delegations" />;
  if (pageId.startsWith("settings-")) return <Settings overview={overview} sectionId={pageId.replace("settings-", "")} />;
  return <DomainPage pageId={pageId} overview={overview} events={recentEvents} onSelect={onSelect} developerMode={developerMode} />;
}

function readPins(): EntitySummary[] {
  try { const value = JSON.parse(window.localStorage.getItem("aegis.pins") || "[]"); return Array.isArray(value) ? value.slice(0, 12) : []; }
  catch { return []; }
}

function togglePin(items: EntitySummary[], entity: EntitySummary): EntitySummary[] {
  const exists = items.some((item) => item.type === entity.type && item.id === entity.id);
  const next = exists ? items.filter((item) => item.type !== entity.type || item.id !== entity.id) : [...items, { ...entity, data: {} }].slice(-12);
  window.localStorage.setItem("aegis.pins", JSON.stringify(next));
  return next;
}

function LoadingDisplay({ displayMode }: { displayMode: boolean }) {
  return <main className={displayMode ? "display-shell center-shell" : "master-shell center-shell"}><UiState kind="loading" title="Loading AEGIS" message="Synchronizing Runtime managers and the spatial information model." /></main>;
}

function ErrorDisplay({ message }: { message: string }) {
  const lower = message.toLowerCase();
  const kind = lower.includes("401") || lower.includes("unauthorized") ? "unauthorized" : lower.includes("403") || lower.includes("forbidden") ? "permission" : lower.includes("fresh") ? "fresh-auth" : "error";
  const action = kind === "unauthorized" || kind === "fresh-auth" ? { label: "Authenticate with passkey", href: "/auth/login" } : undefined;
  return <main className="display-shell center-shell"><UiState kind={kind} title={kind === "fresh-auth" ? "Fresh passkey authentication required" : "AEGIS unavailable"} message={message} actionLabel={action?.label} actionHref={action?.href} /></main>;
}
