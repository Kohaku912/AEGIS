import { Activity, BrainCircuit, Boxes, Command, MessageSquare, Network, Settings, ShieldCheck, Workflow } from "lucide-react";

export type DomainId = "command" | "work" | "intelligence" | "capabilities" | "infrastructure" | "communications" | "governance" | "observability" | "configuration";
export type PageId = string;

export type NavigationDomain = {
  id: DomainId;
  label: string;
  path: string;
  icon: typeof Command;
  pages: Array<{ id: PageId; label: string; path: string }>;
};

export const navigation: NavigationDomain[] = [
  { id: "command", label: "Command", path: "/dashboard", icon: Command, pages: [
    { id: "command-center", label: "Command Center", path: "/dashboard" },
    { id: "attention", label: "Attention Center", path: "/dashboard/attention" }
  ] },
  { id: "work", label: "Work", path: "/dashboard/work/tasks", icon: Workflow, pages: [
    { id: "tasks", label: "Tasks", path: "/dashboard/work/tasks" },
    { id: "plans", label: "Plans", path: "/dashboard/work/plans" },
    { id: "commitments", label: "Commitments", path: "/dashboard/work/commitments" },
    { id: "schedule", label: "Schedule & Hooks", path: "/dashboard/work/schedule" },
    { id: "delegation", label: "Delegation", path: "/dashboard/work/delegation" }
  ] },
  { id: "intelligence", label: "Intelligence", path: "/dashboard/intelligence/autonomy", icon: BrainCircuit, pages: [
    { id: "autonomy", label: "Autonomy", path: "/dashboard/intelligence/autonomy" },
    { id: "memory", label: "Memory", path: "/dashboard/intelligence/memory" },
    { id: "sleep", label: "Consolidation & Sleep", path: "/dashboard/intelligence/sleep" },
    { id: "user-model", label: "User Model", path: "/dashboard/intelligence/user-model" },
    { id: "situation", label: "User Situation", path: "/dashboard/intelligence/situation" },
    { id: "context", label: "Context Builder", path: "/dashboard/intelligence/context" },
    { id: "models-prompts", label: "Models & Prompts", path: "/dashboard/intelligence/models-prompts" }
  ] },
  { id: "capabilities", label: "Capabilities", path: "/dashboard/capabilities/catalog", icon: Boxes, pages: [
    { id: "capability-catalog", label: "Catalog", path: "/dashboard/capabilities/catalog" },
    { id: "generated-capabilities", label: "Generated", path: "/dashboard/capabilities/generated" },
    { id: "capability-executions", label: "Executions", path: "/dashboard/capabilities/executions" },
    { id: "policy-simulation", label: "Policy Simulation", path: "/dashboard/capabilities/policy-simulation" }
  ] },
  { id: "infrastructure", label: "Infrastructure", path: "/dashboard/infrastructure/servers", icon: Network, pages: [
    { id: "servers", label: "Servers", path: "/dashboard/infrastructure/servers" },
    { id: "devices", label: "Devices", path: "/dashboard/infrastructure/devices" },
    { id: "network", label: "Network", path: "/dashboard/infrastructure/network" },
    { id: "deployment", label: "Deployment", path: "/dashboard/infrastructure/deployment" },
    { id: "storage", label: "Storage", path: "/dashboard/infrastructure/storage" }
  ] },
  { id: "communications", label: "Communications", path: "/dashboard/communications/conversations", icon: MessageSquare, pages: [
    { id: "conversations", label: "Conversations", path: "/dashboard/communications/conversations" },
    { id: "notifications", label: "Notifications", path: "/dashboard/communications/notifications" },
    { id: "presentation-surfaces", label: "Presentation Surfaces", path: "/dashboard/communications/presentation-surfaces" }
  ] },
  { id: "governance", label: "Governance", path: "/dashboard/governance/approvals", icon: ShieldCheck, pages: [
    { id: "approvals", label: "Approvals", path: "/dashboard/governance/approvals" },
    { id: "policy", label: "Policy", path: "/dashboard/governance/policy" },
    { id: "security", label: "Security", path: "/dashboard/governance/security" },
    { id: "privacy", label: "Privacy", path: "/dashboard/governance/privacy" },
    { id: "audit", label: "Audit", path: "/dashboard/governance/audit" }
  ] },
  { id: "observability", label: "Observability", path: "/dashboard/observability/activity", icon: Activity, pages: [
    { id: "activity", label: "Activity", path: "/dashboard/observability/activity" },
    { id: "llm-usage", label: "LLM Usage", path: "/dashboard/observability/llm-usage" },
    { id: "errors", label: "Errors", path: "/dashboard/observability/errors" },
    { id: "performance", label: "Performance", path: "/dashboard/observability/performance" },
    { id: "reports", label: "Reports", path: "/dashboard/observability/reports" }
  ] },
  { id: "configuration", label: "Configuration", path: "/settings", icon: Settings, pages: [
    ...["Autonomy", "Models", "Prompts", "Memory", "Context", "Capabilities", "Permissions", "Approvals", "Servers", "Devices", "Notifications", "Privacy", "Display", "Budgets", "Retention", "Developer", "Backup"].map((label) => ({ id: `settings-${label.toLowerCase()}`, label, path: `/settings/${label.toLowerCase()}` }))
  ] }
];

export function routeState(pathname: string): { domain: DomainId; page: PageId } {
  for (const domain of navigation) {
    const page = domain.pages.find((candidate) => candidate.path === pathname || (candidate.path !== "/dashboard" && pathname.startsWith(candidate.path)));
    if (page) return { domain: domain.id, page: page.id };
  }
  if (pathname.includes("approvals")) return { domain: "governance", page: "approvals" };
  if (pathname.includes("servers") || pathname.includes("systems")) return { domain: "infrastructure", page: "servers" };
  if (pathname.includes("memory") || pathname.includes("mind")) return { domain: "intelligence", page: "memory" };
  if (pathname.includes("activity") || pathname.includes("audit")) return { domain: "observability", page: "activity" };
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
