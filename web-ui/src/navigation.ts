import { BriefcaseBusiness, Home, MessageSquare, Network, Settings } from "lucide-react";

export type DomainId = "home" | "work" | "communications" | "systems" | "administration";
export type PageId = string;
export type NavigationPage = { id: PageId; label: string; path: string; developerOnly?: boolean };
export type NavigationDomain = { id: DomainId; label: string; path: string; icon: typeof Home; pages: NavigationPage[] };

export const navigation: NavigationDomain[] = [
  {
    id: "home", label: "ホーム", path: "/dashboard", icon: Home,
    pages: [
      { id: "command-center", label: "概要", path: "/dashboard" },
      { id: "attention", label: "対応が必要", path: "/dashboard/attention" },
    ],
  },
  {
    id: "work", label: "仕事", path: "/dashboard/work/tasks", icon: BriefcaseBusiness,
    pages: [
      { id: "tasks", label: "タスク", path: "/dashboard/work/tasks" },
      { id: "goals", label: "目標と検証", path: "/dashboard/goals" },
      { id: "open-loops", label: "未完了事項", path: "/dashboard/open-loops" },
      { id: "continuations", label: "継続対応", path: "/dashboard/continuations" },
    ],
  },
  {
    id: "communications", label: "コミュニケーション", path: "/dashboard/communications/conversations", icon: MessageSquare,
    pages: [
      { id: "conversations", label: "チャット", path: "/dashboard/communications/conversations" },
      { id: "social", label: "Social / AGORA", path: "/dashboard/communications/social" },
      { id: "notifications", label: "通知", path: "/dashboard/communications/notifications" },
      { id: "presentation-surfaces", label: "プレゼンテーション", path: "/dashboard/communications/presentation-surfaces" },
    ],
  },
  {
    id: "systems", label: "システム", path: "/dashboard/infrastructure/servers", icon: Network,
    pages: [
      { id: "servers", label: "サーバー", path: "/dashboard/infrastructure/servers" },
      { id: "devices", label: "端末", path: "/dashboard/infrastructure/devices" },
      { id: "capability-catalog", label: "機能カタログ", path: "/dashboard/capabilities/catalog" },
      { id: "capability-executions", label: "実行履歴", path: "/dashboard/capabilities/executions" },
    ],
  },
  {
    id: "administration", label: "設定・管理", path: "/dashboard/governance/policy", icon: Settings,
    pages: [
      { id: "policy", label: "ポリシー", path: "/dashboard/governance/policy" },
      { id: "security", label: "セキュリティ", path: "/dashboard/governance/security" },
      { id: "privacy", label: "プライバシー", path: "/dashboard/governance/privacy" },
      { id: "policy-simulation", label: "ポリシーシミュレーション", path: "/dashboard/capabilities/policy-simulation", developerOnly: true },
      { id: "settings-autonomy", label: "設定", path: "/settings/autonomy" },
      { id: "activity", label: "監査・生ログ", path: "/dashboard/observability/activity", developerOnly: true },
      { id: "repairs", label: "修復フィード", path: "/dashboard/repairs", developerOnly: true },
      { id: "llm-usage", label: "LLM使用量", path: "/dashboard/observability/llm-usage", developerOnly: true },
      { id: "models-prompts", label: "モデルとプロンプト", path: "/dashboard/intelligence/models-prompts", developerOnly: true },
    ],
  },
];

const aliases: Array<[RegExp, PageId]> = [
  [/\/dashboard\/tasks|\/dashboard\/work(\/|$)/, "tasks"],
  [/\/dashboard\/governance\/approvals/, "attention"],
  [/\/dashboard\/observability\/errors/, "attention"],
  [/\/dashboard\/systems/, "servers"],
  [/\/dashboard\/memory|\/dashboard\/intelligence\/memory/, "models-prompts"],
];

export function routeState(pathname: string): { domain: DomainId; page: PageId } {
  const alias = aliases.find(([pattern]) => pattern.test(pathname));
  const target = alias?.[1];
  for (const domain of navigation) {
    const page = domain.pages.find((candidate) =>
      candidate.id === target || candidate.path === pathname || (candidate.path !== "/dashboard" && pathname.startsWith(candidate.path)),
    );
    if (page) return { domain: domain.id, page: page.id };
  }
  return { domain: "home", page: "command-center" };
}

export function pageDefinition(pageId: PageId) {
  for (const domain of navigation) {
    const page = domain.pages.find((candidate) => candidate.id === pageId);
    if (page) return { domain, page };
  }
  return { domain: navigation[0], page: navigation[0].pages[0] };
}
