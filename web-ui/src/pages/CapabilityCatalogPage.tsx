import { useQuery, useQueryClient } from "@tanstack/react-query";
import { RotateCcw, Search } from "lucide-react";
import { useEffect, useState } from "react";
import {
  ApiError,
  fetchCapabilityRisk,
  fetchResourceEntities,
  resetCapabilityRisk,
  updateCapabilityRisk,
} from "../api/client";
import type { EntitySummary } from "../types";

type Policy = {
  manifest?: Record<string, unknown>;
  override?: Record<string, unknown>;
  effective?: Record<string, unknown>;
  override_active?: boolean;
};

type PolicyError = {
  message: string;
  freshAuthRequired: boolean;
};

const APPROVAL_RISKS = new Set(["approval_required", "high_risk", "critical"]);

function policyFromRisk(riskLevel: string): Record<string, unknown> {
  return {
    risk_level: riskLevel,
    requires_approval: APPROVAL_RISKS.has(riskLevel),
  };
}

function policyFromApprovalToggle(
  current: Record<string, unknown>,
  checked: boolean,
): Record<string, unknown> {
  const risk = String(current.risk_level || "low");
  if (checked) {
    return {
      requires_approval: true,
      risk_level: APPROVAL_RISKS.has(risk) ? risk : "approval_required",
    };
  }
  return {
    requires_approval: false,
    risk_level: APPROVAL_RISKS.has(risk) ? "safe" : risk,
  };
}

export function CapabilityCatalogPage() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<EntitySummary>();
  const [editablePolicy, setEditablePolicy] = useState<Record<string, unknown>>({});
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const [saveError, setSaveError] = useState<PolicyError>();
  const capabilities = useQuery({
    queryKey: ["ui-resource", "capabilities"],
    queryFn: () => fetchResourceEntities("capabilities", "", { limit: 1000 }),
    staleTime: 5_000,
  });
  const policy = useQuery({
    queryKey: ["capability-policy", selected?.id],
    queryFn: () => fetchCapabilityRisk(selected!.id),
    enabled: Boolean(selected),
  });
  const values = (policy.data || {}) as Policy;
  useEffect(() => {
    if (values.effective) {
      setEditablePolicy({
        ...values.effective,
        reason: "Updated from Capability Catalog",
        updated_by: "dashboard",
      });
    }
  }, [policy.data]);
  const filtered = (capabilities.data?.items || []).filter((item) =>
    `${item.title} ${item.id} ${item.subtitle} ${item.status}`
      .toLowerCase()
      .includes(query.toLowerCase()),
  );

  const applyChange = async (change: Record<string, unknown>) => {
    if (!selected || saving) return;
    const previous = editablePolicy;
    const next = {
      ...editablePolicy,
      ...change,
      reason: "Updated from Capability Catalog",
      updated_by: "dashboard",
    };
    setEditablePolicy(next);
    setSaving(true);
    setSaveError(undefined);
    setStatus("Saving policy change...");
    try {
      await updateCapabilityRisk(selected.id, next);
      setStatus(
        "Policy updated, catalog reloaded, and effective policy audited.",
      );
      await policy.refetch();
      await queryClient.invalidateQueries({
        queryKey: ["ui-resource", "capabilities"],
      });
    } catch (error) {
      setEditablePolicy(previous);
      setStatus("");
      setSaveError(policyError(error));
    } finally {
      setSaving(false);
    }
  };
  const reset = async () => {
    if (!selected || saving) return;
    setSaving(true);
    setSaveError(undefined);
    setStatus("Resetting override to manifest policy...");
    try {
      await resetCapabilityRisk(selected.id);
      setStatus("Override reset and effective policy reloaded.");
      await policy.refetch();
      await queryClient.invalidateQueries({
        queryKey: ["ui-resource", "capabilities"],
      });
    } catch (error) {
      setStatus("");
      setSaveError(policyError(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="capability-console">
      <header>
        <div>
          <span>CapabilityCatalog / effective policy</span>
          <h2>Capability Catalog</h2>
          <p>
            Manifest definitions are the source of truth. Risk edits write
            permanently into capability JSON, then reload the live catalog.
          </p>
        </div>
        <strong>{capabilities.data?.total || 0} capabilities</strong>
      </header>
      <label className="memory-search">
        <Search size={15} />
        <input
          aria-label="Search capabilities"
          value={query}
          onChange={(event) => setQuery(event.currentTarget.value)}
          placeholder="Search ID, server, status, approval, or risk"
        />
      </label>
      {status ? (
        <div
          className="attention-item"
          data-severity="info"
          role="status"
          aria-live="polite"
        >
          {status}
        </div>
      ) : null}
      {saveError ? (
        <div
          className="attention-item"
          data-severity="critical"
          role="alert"
          aria-live="assertive"
        >
          <div>
            <strong>Capability policy was not changed.</strong>
            <p>{saveError.message}</p>
          </div>
          {saveError.freshAuthRequired ? (
            <a
              className="primary-button"
              href={`/auth/login?next=${encodeURIComponent(window.location.pathname + window.location.search)}`}
            >
              Authenticate with passkey
            </a>
          ) : null}
        </div>
      ) : null}
      <section className="capability-console__layout">
        <div className="capability-list">
          {filtered.map((item) => (
            <button
              type="button"
              aria-current={selected?.id === item.id}
              onClick={() => {
                setSelected(item);
                setStatus("");
                setSaveError(undefined);
              }}
              key={item.id}
            >
              <span>{item.subtitle}</span>
              <strong>{item.title}</strong>
              <code>{item.id}</code>
              <small>
                {String(
                  item.data?.risk_level || item.data?.risk || item.status,
                )}{" "}
                / {String(item.data?.enabled ?? "enabled")}
              </small>
            </button>
          ))}
          {!filtered.length ? <p>No capability matches this view.</p> : null}
        </div>
        <aside className="capability-detail">
          {selected ? (
            <>
              <header>
                <span>{selected.status}</span>
                <h3>{selected.title}</h3>
                <code>{selected.id}</code>
                <p>{String(selected.data?.description || selected.subtitle)}</p>
              </header>
              <div className="policy-comparison">
                <PolicyColumn label="Manifest" values={values.manifest} />
                <PolicyColumn
                  label="Override"
                  values={values.override}
                  active={values.override_active}
                />
                <PolicyColumn label="Effective" values={values.effective} />
              </div>
              <section className="capability-contract">
                <h4>Execution contract</h4>
                {[
                  "input_schema",
                  "output_schema",
                  "preconditions",
                  "completion_conditions",
                  "verification",
                  "postconditions",
                  "timeout",
                  "retry_policy",
                  "source_file",
                ].map((key) => (
                  <div key={key}>
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong>{summarize(selected.data?.[key])}</strong>
                  </div>
                ))}
              </section>
              <section className="policy-editor">
                <h4>Policy controls</h4>
                <p>Changes are saved and applied immediately.</p>
                <label>
                  Risk
                  <select
                    value={String(editablePolicy.risk_level || "low")}
                    disabled={saving}
                    onChange={(event) => {
                      const riskLevel = event.currentTarget.value;
                      void applyChange(policyFromRisk(riskLevel));
                    }}
                  >
                    {[
                      "low",
                      "safe",
                      "approval_required",
                      "high_risk",
                      "critical",
                    ].map((value) => (
                      <option value={value} key={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={Boolean(editablePolicy.requires_approval)}
                    disabled={saving}
                    onChange={(event) => {
                      const checked = event.currentTarget.checked;
                      void applyChange(policyFromApprovalToggle(editablePolicy, checked));
                    }}
                  />
                  Requires approval
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={Boolean(editablePolicy.enabled ?? true)}
                    disabled={saving}
                    onChange={(event) => {
                      const checked = event.currentTarget.checked;
                      void applyChange({ enabled: checked });
                    }}
                  />
                  Enabled
                </label>
                <div>
                  <button
                    className="danger-button"
                    type="button"
                    disabled={saving}
                    onClick={() => void reset()}
                  >
                    <RotateCcw size={14} />
                    Reset override
                  </button>
                </div>
              </section>
            </>
          ) : (
            <p>
              Select a capability to inspect manifest, override, effective
              policy, verification, history, and actions.
            </p>
          )}
        </aside>
      </section>
    </div>
  );
}

function PolicyColumn({
  label,
  values,
  active,
}: {
  label: string;
  values?: Record<string, unknown>;
  active?: boolean;
}) {
  return (
    <article data-active={active}>
      <span>
        {label}
        {active ? " / active" : ""}
      </span>
      <strong>{String(values?.risk_level || "Not set")}</strong>
      <small>Approval: {String(values?.requires_approval ?? "Not set")}</small>
      <small>Enabled: {String(values?.enabled ?? "Not set")}</small>
    </article>
  );
}
function summarize(value: unknown): string {
  if (value === undefined || value === null || value === "")
    return "Not reported";
  if (Array.isArray(value))
    return value.length
      ? `${value.length} item(s): ${value.slice(0, 4).map(String).join(", ")}`
      : "Empty";
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    return entries.length
      ? entries
          .slice(0, 6)
          .map(
            ([key, item]) =>
              `${key}: ${typeof item === "object" ? "structured" : String(item)}`,
          )
          .join(" / ")
      : "Empty";
  }
  return String(value);
}

function policyError(error: unknown): PolicyError {
  if (error instanceof ApiError) {
    const freshAuthRequired =
      error.status === 403 &&
      (error.code === "fresh_passkey_required" ||
        error.message.toLowerCase().includes("fresh"));
    if (freshAuthRequired) {
      return {
        freshAuthRequired: true,
        message:
          "Your passkey authentication is no longer fresh. Authenticate again, then select the policy value once more.",
      };
    }
    if (
      error.status === 403 &&
      (error.code.toLowerCase().includes("csrf") ||
        error.message.toLowerCase().includes("csrf"))
    ) {
      return {
        freshAuthRequired: false,
        message:
          "The session security token expired. Reload the page and try again.",
      };
    }
    return {
      freshAuthRequired: false,
      message: `${error.message} (HTTP ${error.status})`,
    };
  }
  return {
    freshAuthRequired: false,
    message: error instanceof Error ? error.message : String(error),
  };
}
