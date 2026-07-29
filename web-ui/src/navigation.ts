import { Activity, BrainCircuit, Command, MessageSquare, Network, Settings, ShieldCheck, Workflow } from "lucide-react";

export type DomainId =
  | "command"
  | "loops"
  | "judgment"
  | "communications"
  | "systems"
  | "governance"
  | "developer"
  | "configuration";
export type PageId = string;

export type NavigationDomain = {
  id: DomainId;
  label: string;
  path: string;
  icon: typeof Command;
  pages: Array<{ id: PageId; label: string; path: string }>;
};

/** User-facing navigation: judgment & progress first, not Manager inventory. */
export const navigation: NavigationDomain[] = [
  {
    id: "command",
    label: "Command",
    path: "/dashboard",
    icon: Command,
    pages: [
      { id: "command-center", label: "Command Center", path: "/dashboard" },
      { id: "attention", label: "Attention", path: "/dashboard/attention" },
      { id: "situation", label: "Situation", path: "/dashboard/situation" },
    ],
  },
  {
    id: "loops",
    label: "Open Loops",
    path: "/dashboard/open-loops",
    icon: Workflow,
    pages: [
      { id: "open-loops", label: "All Open Loops", path: "/dashboard/open-loops" },
      { id: "goals", label: "Goals & Verification", path: "/dashboard/goals" },
      { id: "continuations", label: "Continuations", path: "/dashboard/continuations" },
      { id: "approvals", label: "Approvals", path: "/dashboard/governance/approvals" },
    ],
  },
  {
    id: "judgment",
    label: "Judgment",
    path: "/dashboard/operations",
    icon: BrainCircuit,
    pages: [
      { id: "operations", label: "Operations", path: "/dashboard/operations" },
      { id: "initiative", label: "Initiative & Non-action", path: "/dashboard/initiative" },
      { id: "decision-context", label: "Decision Context", path: "/dashboard/decision-context" },
      { id: "repairs", label: "Repairs & Learning", path: "/dashboard/repairs" },
      { id: "reports", label: "Behavioral Reports", path: "/dashboard/observability/reports" },
      { id: "memory", label: "Memory", path: "/dashboard/intelligence/memory" },
    ],
  },
  {
    id: "communications",
    label: "Communications",
    path: "/dashboard/communications",
    icon: MessageSquare,
    pages: [
      { id: "social", label: "Social & AGORA", path: "/dashboard/communications/social" },
      { id: "conversations", label: "Chat", path: "/dashboard/communications/conversations" },
      { id: "notifications", label: "Notifications", path: "/dashboard/communications/notifications" },
      { id: "presentation-surfaces", label: "Presentations", path: "/dashboard/communications/presentation-surfaces" },
    ],
  },
  {
    id: "systems",
    label: "Systems",
    path: "/dashboard/infrastructure/servers",
    icon: Network,
    pages: [
      { id: "servers", label: "Servers", path: "/dashboard/infrastructure/servers" },
      { id: "devices", label: "Devices", path: "/dashboard/infrastructure/devices" },
      { id: "capability-catalog", label: "Capability Catalog", path: "/dashboard/capabilities/catalog" },
      { id: "generated-capabilities", label: "Generated Capabilities", path: "/dashboard/capabilities/generated" },
      { id: "capability-executions", label: "Executions", path: "/dashboard/capabilities/executions" },
    ],
  },
  {
    id: "governance",
    label: "Governance",
    path: "/dashboard/governance/policy",
    icon: ShieldCheck,
    pages: [
      { id: "policy", label: "Policy", path: "/dashboard/governance/policy" },
      { id: "security", label: "Security", path: "/dashboard/governance/security" },
      { id: "privacy", label: "Privacy", path: "/dashboard/governance/privacy" },
      { id: "policy-simulation", label: "Policy Simulation", path: "/dashboard/capabilities/policy-simulation" },
    ],
  },
  {
    id: "developer",
    label: "Developer",
    path: "/dashboard/observability/activity",
    icon: Activity,
    pages: [
      { id: "activity", label: "Raw Activity", path: "/dashboard/observability/activity" },
      { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage" },
      { id: "errors", label: "Repair Feed", path: "/dashboard/observability/errors" },
      { id: "audit", label: "Audit", path: "/dashboard/governance/audit" },
      { id: "models-prompts", label: "Models & Prompts", path: "/dashboard/intelligence/models-prompts" },
    ],
  },
  {
    id: "configuration",
    label: "Configuration",
    path: "/settings",
    icon: Settings,
    pages: [
      ...[
        "Autonomy",
        "Models",
        "Prompts",
        "Memory",
        "Context",
        "Capabilities",
        "Permissions",
        "Approvals",
        "Servers",
        "Devices",
        "Notifications",
        "Privacy",
        "Display",
        "Budgets",
        "Retention",
        "Developer",
        "Backup",
      ].map((label) => ({
        id: `settings-${label.toLowerCase()}`,
        label,
        path: `/settings/${label.toLowerCase()}`,
      })),
    ],
  },
];

export function routeState(pathname: string): { domain: DomainId; page: PageId } {
  for (const domain of navigation) {
    const page = domain.pages.find(
      (candidate) =>
        candidate.path === pathname ||
        (candidate.path !== "/dashboard" && pathname.startsWith(candidate.path)),
    );
    if (page) return { domain: domain.id, page: page.id };
  }
  if (pathname.includes("open-loops") || pathname.includes("/work") || pathname.includes("/tasks")) {
    return { domain: "loops", page: "open-loops" };
  }
  if (pathname.includes("operations")) return { domain: "judgment", page: "operations" };
  if (pathname.includes("initiative")) return { domain: "judgment", page: "initiative" };
  if (pathname.includes("decision-context") || pathname.includes("/context")) {
    return { domain: "judgment", page: "decision-context" };
  }
  if (pathname.includes("repairs") || pathname.includes("/errors")) return { domain: "judgment", page: "repairs" };
  if (pathname.includes("goals")) return { domain: "loops", page: "goals" };
  if (pathname.includes("continuations")) return { domain: "loops", page: "continuations" };
  if (pathname.includes("social") || pathname.includes("conversations") || pathname.includes("agora")) {
    return { domain: "communications", page: "social" };
  }
  if (pathname.includes("approvals")) return { domain: "loops", page: "approvals" };
  if (pathname.includes("servers") || pathname.includes("systems")) return { domain: "systems", page: "servers" };
  if (pathname.includes("memory") || pathname.includes("mind")) return { domain: "judgment", page: "memory" };
  if (pathname.includes("activity") || pathname.includes("audit")) return { domain: "developer", page: "activity" };
  if (pathname.includes("situation") || pathname.includes("user-model")) return { domain: "command", page: "situation" };
  if (pathname.startsWith("/settings")) return { domain: "configuration", page: "settings-autonomy" };
  return { domain: "command", page: "command-center" };
}

export function pageDefinition(pageId: PageId) {
  for (const domain of navigation) {
    const page = domain.pages.find((candidate) => candidate.id === pageId);
    if (page) return { domain, page };
  }
  return { domain: navigation[0], page: navigation[0].pages[0] };
}
