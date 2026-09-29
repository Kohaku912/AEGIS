import {
  Activity,
  Brain,
  Cable,
  Home,
  Settings,
  UserRound,
} from "lucide-react";

export type DomainId = "cockpit" | "observe" | "personal" | "settings";
export type PageId = string;
export type NavigationPage = { id: PageId; label: string; path: string; developerOnly?: boolean };
export type NavigationDomain = { id: DomainId; label: string; path: string; icon: typeof Home; pages: NavigationPage[] };

export const navigation: NavigationDomain[] = [
  {
    id: "cockpit",
    label: "Cockpit",
    path: "/dashboard",
    icon: Home,
    pages: [
      { id: "home", label: "Cockpit Home", path: "/dashboard" },
      { id: "control-hub", label: "Control Hub", path: "/dashboard/control-hub" },
      { id: "atlas", label: "Ops Atlas", path: "/dashboard/atlas" },
      { id: "interventions", label: "Interventions", path: "/dashboard/interventions" },
      { id: "execution-trace", label: "Execution Trace", path: "/dashboard/execution-trace" },
      { id: "layers", label: "Layer Comparison", path: "/dashboard/layers" },
      { id: "systems", label: "Systems", path: "/dashboard/systems" },
      { id: "attention", label: "対応待ち", path: "/dashboard/attention", developerOnly: true },
      { id: "open-loops", label: "オープンループ", path: "/dashboard/open-loops", developerOnly: true },
      { id: "judgment", label: "判断", path: "/dashboard/judgment", developerOnly: true },
      { id: "tasks", label: "タスク", path: "/dashboard/work/tasks", developerOnly: true },
      { id: "approvals", label: "承認", path: "/dashboard/approvals", developerOnly: true },
      { id: "autonomous", label: "自律実行", path: "/dashboard/autonomous", developerOnly: true },
      { id: "desires", label: "欲求", path: "/dashboard/desires", developerOnly: true },
      { id: "agent-state", label: "Agent State", path: "/dashboard/agent-state", developerOnly: true },
      { id: "agent-timeline", label: "Agent Timeline", path: "/dashboard/agent-timeline", developerOnly: true },
      { id: "memory", label: "記憶", path: "/dashboard/memory", developerOnly: true },
      { id: "learning", label: "学習", path: "/dashboard/learning", developerOnly: true },
      { id: "capability-catalog", label: "Capability", path: "/dashboard/capabilities/catalog", developerOnly: true },
      { id: "llm-l1", label: "L1 (知覚 / Router)", path: "/dashboard/llm/l1", developerOnly: true },
      { id: "llm-l2", label: "L2 (Autonomous Mind)", path: "/dashboard/llm/l2", developerOnly: true },
      { id: "llm-l3", label: "L3 (Deep Reasoner)", path: "/dashboard/llm/l3", developerOnly: true },
      { id: "servers", label: "サーバー", path: "/dashboard/infrastructure/servers", developerOnly: true },
      { id: "pc", label: "PC", path: "/dashboard/devices/pc", developerOnly: true },
      { id: "browser", label: "Browser", path: "/dashboard/devices/browser", developerOnly: true },
      { id: "android", label: "Android", path: "/dashboard/devices/android", developerOnly: true },
      { id: "room", label: "Room", path: "/dashboard/devices/room", developerOnly: true },
      { id: "agora", label: "AGORA", path: "/dashboard/communications/social", developerOnly: true },
      { id: "presentation-surfaces", label: "Presentation", path: "/dashboard/communications/presentation-surfaces", developerOnly: true },
    ],
  },
  {
    id: "observe",
    label: "Trace",
    path: "/dashboard/operations",
    icon: Activity,
    pages: [
      { id: "operations", label: "Operations", path: "/dashboard/operations", developerOnly: true },
      { id: "logs", label: "Logs", path: "/dashboard/observability/logs", developerOnly: true },
      { id: "raw-activity", label: "Activity", path: "/dashboard/activity", developerOnly: true },
      { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage", developerOnly: true },
      { id: "incidents", label: "Incidents & Repairs", path: "/dashboard/incidents", developerOnly: true },
      { id: "performance", label: "Performance", path: "/dashboard/observability/performance", developerOnly: true },
      { id: "audit", label: "Audit", path: "/dashboard/observability/audit", developerOnly: true },
      // Phase 3/5 — the post-hoc visibility that replaced the forced approval gate.
      // Kept alongside `audit` for now; promote out of developerOnly if the owner wants
      // it in the default navigation.
      { id: "irreversibility", label: "Irreversibility", path: "/dashboard/observability/irreversibility", developerOnly: true },
      { id: "behavioral-reports", label: "Behavioral Reports", path: "/dashboard/observability/behavioral-reports", developerOnly: true },
    ],
  },
  {
    id: "personal",
    label: "Personal",
    path: "/dashboard/personal-context",
    icon: UserRound,
    pages: [
      { id: "personal-context", label: "Personal Context", path: "/dashboard/personal-context" },
      { id: "personal-ai", label: "Personal AI", path: "/dashboard/personal-ai", developerOnly: true },
      { id: "timeline", label: "Timeline", path: "/dashboard/personal-data/timeline", developerOnly: true },
      { id: "user-state", label: "User State", path: "/dashboard/user-state", developerOnly: true },
    ],
  },
  {
    id: "settings",
    label: "Settings",
    path: "/settings/general",
    icon: Settings,
    pages: [
      { id: "settings-general", label: "設定", path: "/settings/general" },
      { id: "settings-all", label: "全設定", path: "/settings/all", developerOnly: true },
      { id: "llm-config", label: "Models & Prompts", path: "/dashboard/intelligence/models-prompts" },
      { id: "diagnostics", label: "システム診断", path: "/dashboard/diagnostics" },
      { id: "dashboard-settings", label: "Dashboard設定", path: "/dashboard/dashboard-settings" },
      { id: "notifications", label: "通知", path: "/dashboard/communications/notifications", developerOnly: true },
      { id: "prompt-analysis", label: "Prompt Analysis", path: "/dashboard/observability/prompt-analysis", developerOnly: true },
    ],
  },
];

const aliases: Array<[RegExp, PageId]> = [
  [/\/dashboard\/?$/, "home"],
  [/\/dashboard\/control-hub(\/|$)/, "control-hub"],
  [/\/dashboard\/atlas(\/|$)/, "atlas"],
  [/\/dashboard\/interventions(\/|$)/, "interventions"],
  [/\/dashboard\/execution-trace(\/|$)/, "execution-trace"],
  [/\/dashboard\/layers(\/|$)/, "layers"],
  [/\/dashboard\/systems(\/|$)/, "systems"],
  [/\/dashboard\/personal-context(\/|$)/, "personal-context"],
  [/\/dashboard\/command-center/, "home"],
  [/\/dashboard\/tasks|\/dashboard\/work(\/|$)/, "tasks"],
  [/\/dashboard\/approvals(\/|$)/, "approvals"],
  [/\/dashboard\/governance\/approvals/, "approvals"],
  [/\/dashboard\/autonomous(\/|$)/, "autonomous"],
  [/\/dashboard\/desires(\/|$)/, "desires"],
  [/\/dashboard\/agent-state(\/|$)/, "agent-state"],
  [/\/dashboard\/operations(\/|$)/, "operations"],
  [/\/dashboard\/activity(\/|$)/, "raw-activity"],
  [/\/dashboard\/incidents(\/|$)/, "incidents"],
  [/\/dashboard\/observability\/events/, "raw-activity"],
  [/\/dashboard\/observability\/logs/, "logs"],
  [/\/dashboard\/observability\/errors/, "incidents"],
  [/\/dashboard\/observability\/performance/, "performance"],
  [/\/dashboard\/observability\/behavioral-reports/, "behavioral-reports"],
  [/\/dashboard\/observability\/irreversibility/, "irreversibility"],
  [/\/dashboard\/observability\/llm-usage/, "llm-usage"],
  [/\/dashboard\/llm(\/|$)/, "llm-usage"],
  [/\/dashboard\/systems/, "systems"],
  [/\/dashboard\/personal-data\/timeline/, "timeline"],
  [/\/dashboard\/intelligence\/memory/, "memory"],
  [/\/dashboard\/intelligence\/models-prompts/, "llm-config"],
  [/\/dashboard\/communications\/social/, "agora"],
  [/\/dashboard\/communications\/presentation-surfaces/, "presentation-surfaces"],
  [/\/dashboard\/interruption(\/|$)/, "interruption"],
  [/\/dashboard\/capabilities\/executions/, "capability-catalog"],
  [/\/settings\/autonomy/, "settings-general"],
  [/\/dashboard\/goals/, "agent-state"],
  [/\/dashboard\/open-loops/, "open-loops"],
  [/\/dashboard\/judgment/, "judgment"],
  [/\/dashboard\/continuations/, "judgment"],
  [/\/dashboard\/repairs/, "incidents"],
  // Phase D7 — Agent Timeline
  [/\/dashboard\/agent-timeline(\/|$)/, "agent-timeline"],
  // DASHBOARD_V3_PLAN.md Phase L6 — LLM Layers
  [/\/dashboard\/llm\/l1(\/|$)/, "llm-l1"],
  [/\/dashboard\/llm\/l2(\/|$)/, "llm-l2"],
  [/\/dashboard\/llm\/l3(\/|$)/, "llm-l3"],
];

/** Detail IDs for deep-linkable observation pages. */
export function detailRoute(pathname: string): { page: PageId; detailId: string } | null {
  const patterns: Array<[RegExp, PageId]> = [
    [/^\/dashboard\/operations\/([^/]+)$/, "operations"],
    [/^\/dashboard\/activity\/([^/]+)$/, "raw-activity"],
    [/^\/dashboard\/incidents\/([^/]+)$/, "incidents"],
    [/^\/dashboard\/observability\/audit\/([^/]+)$/, "audit"],
    [/^\/dashboard\/audit\/([^/]+)$/, "audit"],
    [/^\/dashboard\/llm\/([^/]+)$/, "llm-usage"],
    [/^\/dashboard\/observability\/llm-usage\/([^/]+)$/, "llm-usage"],
    // Phase D4 — Agent Session 詳細
    [/^\/dashboard\/agent-sessions\/([^/]+)$/, "agent-session"],
  ];
  for (const [pattern, page] of patterns) {
    const match = pathname.match(pattern);
    if (match?.[1]) return { page, detailId: decodeURIComponent(match[1]) };
  }
  return null;
}

export function routeState(pathname: string): { domain: DomainId; page: PageId; detailId?: string } {
  const detail = detailRoute(pathname);
  if (detail) {
    const found = pageDefinition(detail.page);
    return { domain: found.domain.id, page: detail.page, detailId: detail.detailId };
  }
  for (const [pattern, pageId] of aliases) {
    if (pattern.test(pathname)) {
      const found = pageDefinition(pageId);
      return { domain: found.domain.id, page: pageId };
    }
  }
  for (const domain of navigation) {
    const exact = domain.pages.find((candidate) => candidate.path === pathname);
    if (exact) return { domain: domain.id, page: exact.id };
  }
  for (const domain of navigation) {
    const page = domain.pages
      .filter((candidate) => candidate.path !== "/dashboard")
      .sort((a, b) => b.path.length - a.path.length)
      .find((candidate) => pathname.startsWith(candidate.path));
    if (page) return { domain: domain.id, page: page.id };
  }
  return { domain: "cockpit", page: "home" };
}

export function pageDefinition(pageId: PageId) {
  for (const domain of navigation) {
    const page = domain.pages.find((candidate) => candidate.id === pageId);
    if (page) return { domain, page };
  }
  return { domain: navigation[0], page: navigation[0].pages[0] };
}

export function allPages(): NavigationPage[] {
  return navigation.flatMap((domain) => domain.pages);
}
