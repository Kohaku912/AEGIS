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
      { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage" },
      { id: "prompt-analysis", label: "Prompt Analysis", path: "/dashboard/observability/prompt-analysis" },
      { id: "llm-config", label: "LLM Config", path: "/dashboard/intelligence/models-prompts" },
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
    path: "/dashboard/observability/events",
    icon: Activity,
    pages: [
      { id: "events", label: "イベント", path: "/dashboard/observability/events" },
      { id: "notifications", label: "通知", path: "/dashboard/communications/notifications" },
      { id: "audit", label: "Audit log", path: "/dashboard/observability/audit" },
      { id: "errors", label: "エラー", path: "/dashboard/observability/errors" },
      { id: "logs", label: "Logs", path: "/dashboard/observability/logs" },
    ],
  },
  {
    id: "personal",
    label: "個人",
    path: "/dashboard/personal-ai",
    icon: UserRound,
    pages: [
      { id: "personal-ai", label: "Personal AI", path: "/dashboard/personal-ai" },
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
      { id: "diagnostics", label: "システム診断", path: "/dashboard/diagnostics" },
      { id: "dashboard-settings", label: "Dashboard設定", path: "/dashboard/dashboard-settings" },
    ],
  },
];

const aliases: Array<[RegExp, PageId]> = [
  [/\/dashboard\/?$/, "home"],
  [/\/dashboard\/command-center/, "home"],
  [/\/dashboard\/tasks|\/dashboard\/work(\/|$)/, "tasks"],
  [/\/dashboard\/governance\/approvals/, "approvals"],
  [/\/dashboard\/observability\/errors/, "errors"],
  [/\/dashboard\/observability\/activity/, "audit"],
  [/\/dashboard\/systems/, "servers"],
  [/\/dashboard\/intelligence\/memory/, "memory"],
  [/\/dashboard\/communications\/social/, "agora"],
  [/\/dashboard\/capabilities\/executions/, "capability-catalog"],
  [/\/settings\/autonomy/, "settings-general"],
  [/\/dashboard\/goals/, "agent-state"],
  [/\/dashboard\/open-loops/, "agent-state"],
  [/\/dashboard\/continuations/, "agent-state"],
  [/\/dashboard\/repairs/, "errors"],
];

export function routeState(pathname: string): { domain: DomainId; page: PageId } {
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
