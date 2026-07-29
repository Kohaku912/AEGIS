import { BriefcaseBusiness, Home, MessageSquare, Network, Settings } from "lucide-react";

export type DomainId = "home" | "work" | "communications" | "systems" | "administration";
export type PageId = string;
export type NavigationPage = { id: PageId; label: string; path: string; developerOnly?: boolean };
export type NavigationDomain = { id: DomainId; label: string; path: string; icon: typeof Home; pages: NavigationPage[] };

export const navigation: NavigationDomain[] = [
  {
    id: "home", label: "Home", path: "/dashboard", icon: Home,
    pages: [
      { id: "command-center", label: "Overview", path: "/dashboard" },
      { id: "attention", label: "Needs Attention", path: "/dashboard/attention" },
    ],
  },
  {
    id: "work", label: "Work", path: "/dashboard/work/tasks", icon: BriefcaseBusiness,
    pages: [
      { id: "tasks", label: "Tasks", path: "/dashboard/work/tasks" },
      { id: "goals", label: "Goals and Verification", path: "/dashboard/goals" },
      { id: "open-loops", label: "Open Loops", path: "/dashboard/open-loops" },
      { id: "continuations", label: "Continuations", path: "/dashboard/continuations" },
    ],
  },
  {
    id: "communications", label: "Communication", path: "/dashboard/communications/conversations", icon: MessageSquare,
    pages: [
      { id: "conversations", label: "Chat", path: "/dashboard/communications/conversations" },
      { id: "social", label: "Social / AGORA", path: "/dashboard/communications/social" },
      { id: "notifications", label: "Notifications", path: "/dashboard/communications/notifications" },
      { id: "presentation-surfaces", label: "Presentations", path: "/dashboard/communications/presentation-surfaces" },
    ],
  },
  {
    id: "systems", label: "Systems", path: "/dashboard/infrastructure/servers", icon: Network,
    pages: [
      { id: "servers", label: "Servers", path: "/dashboard/infrastructure/servers" },
      { id: "devices", label: "Devices", path: "/dashboard/infrastructure/devices" },
      { id: "capability-catalog", label: "Capability Catalog", path: "/dashboard/capabilities/catalog" },
      { id: "capability-executions", label: "Executions", path: "/dashboard/capabilities/executions" },
    ],
  },
  {
    id: "administration", label: "Settings and Administration", path: "/dashboard/governance/policy", icon: Settings,
    pages: [
      { id: "policy", label: "Policy", path: "/dashboard/governance/policy" },
      { id: "security", label: "Security", path: "/dashboard/governance/security" },
      { id: "privacy", label: "Privacy", path: "/dashboard/governance/privacy" },
      { id: "policy-simulation", label: "Policy Simulation", path: "/dashboard/capabilities/policy-simulation", developerOnly: true },
      { id: "settings-autonomy", label: "Settings", path: "/settings/autonomy" },
      { id: "activity", label: "Audit and Raw Logs", path: "/dashboard/observability/activity", developerOnly: true },
      { id: "repairs", label: "Repair Feed", path: "/dashboard/repairs", developerOnly: true },
      { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage", developerOnly: true },
      { id: "models-prompts", label: "Models and Prompts", path: "/dashboard/intelligence/models-prompts", developerOnly: true },
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
