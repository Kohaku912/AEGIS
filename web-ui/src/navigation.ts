import {
  Activity,
  Brain,
  Cable,
  Home,
  Settings,
  UserRound,
} from "lucide-react";

export type DomainId = "ops" | "intel" | "connect" | "observe" | "personal" | "settings";
export type PageId = string;
export type NavigationPage = { id: PageId; label: string; path: string; developerOnly?: boolean };
export type NavigationDomain = { id: DomainId; label: string; path: string; icon: typeof Home; pages: NavigationPage[] };

export const navigation: NavigationDomain[] = [
  {
    id: "ops",
    label: "運用",
    path: "/dashboard",
    icon: Home,
    pages: [
      { id: "home", label: "ホーム", path: "/dashboard" },
      { id: "attention", label: "対応待ち", path: "/dashboard/attention" },
      { id: "tasks", label: "タスク", path: "/dashboard/work/tasks" },
      { id: "approvals", label: "承認", path: "/dashboard/approvals" },
      { id: "autonomous", label: "自律実行", path: "/dashboard/autonomous" },
      { id: "desires", label: "欲求", path: "/dashboard/desires" },
      { id: "agent-state", label: "Agent State", path: "/dashboard/agent-state" },
    ],
  },
  {
    id: "intel",
    label: "知能",
    path: "/dashboard/memory",
    icon: Brain,
    pages: [
      { id: "memory", label: "記憶", path: "/dashboard/memory" },
      { id: "learning", label: "学習", path: "/dashboard/learning" },
      { id: "capability-catalog", label: "Capability", path: "/dashboard/capabilities/catalog" },
    ],
  },
  {
    id: "connect",
    label: "接続",
    path: "/dashboard/infrastructure/servers",
    icon: Cable,
    pages: [
      { id: "servers", label: "サーバー", path: "/dashboard/infrastructure/servers" },
      { id: "pc", label: "PC", path: "/dashboard/devices/pc" },
      { id: "browser", label: "Browser", path: "/dashboard/devices/browser" },
      { id: "android", label: "Android", path: "/dashboard/devices/android" },
      { id: "room", label: "Room", path: "/dashboard/devices/room" },
      { id: "agora", label: "AGORA", path: "/dashboard/communications/social" },
    ],
  },
  {
    id: "observe",
    label: "観測",
    path: "/dashboard/operations",
    icon: Activity,
    pages: [
      { id: "operations", label: "Operations", path: "/dashboard/operations" },
      { id: "logs", label: "Logs", path: "/dashboard/observability/logs" },
      { id: "raw-activity", label: "Raw Activity", path: "/dashboard/activity", developerOnly: true },
      { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage" },
      { id: "incidents", label: "Incidents & Repairs", path: "/dashboard/incidents" },
      { id: "performance", label: "Performance", path: "/dashboard/observability/performance" },
      { id: "audit", label: "Audit", path: "/dashboard/observability/audit", developerOnly: true },
      { id: "behavioral-reports", label: "Behavioral Reports", path: "/dashboard/observability/behavioral-reports" },
    ],
  },
  {
    id: "personal",
    label: "個人",
    path: "/dashboard/personal-ai",
    icon: UserRound,
    pages: [
      { id: "personal-ai", label: "Personal AI", path: "/dashboard/personal-ai" },
      { id: "timeline", label: "Timeline", path: "/dashboard/personal-data/timeline" },
      { id: "user-state", label: "User State", path: "/dashboard/user-state" },
    ],
  },
  {
    id: "settings",
    label: "設定",
    path: "/settings/general",
    icon: Settings,
    pages: [
      { id: "settings-general", label: "設定", path: "/settings/general" },
      { id: "settings-all", label: "全設定", path: "/settings/all" },
      { id: "llm-config", label: "Models & Prompts", path: "/dashboard/intelligence/models-prompts" },
      { id: "prompt-analysis", label: "Prompt Analysis", path: "/dashboard/observability/prompt-analysis", developerOnly: true },
      { id: "diagnostics", label: "システム診断", path: "/dashboard/diagnostics" },
      { id: "dashboard-settings", label: "Dashboard設定", path: "/dashboard/dashboard-settings" },
      { id: "notifications", label: "通知", path: "/dashboard/communications/notifications" },
    ],
  },
];

const aliases: Array<[RegExp, PageId]> = [
  [/\/dashboard\/?$/, "home"],
  [/\/dashboard\/command-center/, "home"],
  [/\/dashboard\/tasks|\/dashboard\/work(\/|$)/, "tasks"],
  [/\/dashboard\/governance\/approvals/, "approvals"],
  [/\/dashboard\/operations(\/|$)/, "operations"],
  [/\/dashboard\/activity(\/|$)/, "raw-activity"],
  [/\/dashboard\/incidents(\/|$)/, "incidents"],
  [/\/dashboard\/observability\/events/, "raw-activity"],
  [/\/dashboard\/observability\/logs/, "logs"],
  [/\/dashboard\/observability\/errors/, "incidents"],
  [/\/dashboard\/observability\/performance/, "performance"],
  [/\/dashboard\/observability\/behavioral-reports/, "behavioral-reports"],
  [/\/dashboard\/observability\/llm-usage/, "llm-usage"],
  [/\/dashboard\/llm(\/|$)/, "llm-usage"],
  [/\/dashboard\/systems/, "servers"],
  [/\/dashboard\/personal-data\/timeline/, "timeline"],
  [/\/dashboard\/intelligence\/memory/, "memory"],
  [/\/dashboard\/intelligence\/models-prompts/, "llm-config"],
  [/\/dashboard\/communications\/social/, "agora"],
  [/\/dashboard\/capabilities\/executions/, "capability-catalog"],
  [/\/settings\/autonomy/, "settings-general"],
  [/\/dashboard\/goals/, "agent-state"],
  [/\/dashboard\/open-loops/, "agent-state"],
  [/\/dashboard\/continuations/, "agent-state"],
  [/\/dashboard\/repairs/, "incidents"],
];

/** Extract a detail id from `/prefix/{id}` style paths. */
export function detailIdFromPath(pathname: string, prefix: string): string {
  const normalized = prefix.endsWith("/") ? prefix.slice(0, -1) : prefix;
  if (!pathname.startsWith(`${normalized}/`)) return "";
  const rest = pathname.slice(normalized.length + 1).split(/[/?#]/, 1)[0];
  return rest ? decodeURIComponent(rest) : "";
}

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
  return { domain: "ops", page: "home" };
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
