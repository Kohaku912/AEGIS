import { useQuery, useQueryClient } from "@tanstack/react-query";
import { FlaskConical, RotateCcw, Search, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import {
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

export function CapabilityCatalogPage() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<EntitySummary>();
  const [draft, setDraft] = useState<Record<string, unknown>>({});
  const [review, setReview] = useState(false);
  const [status, setStatus] = useState("");
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
      setDraft({
        ...values.effective,
        reason: "Updated from Capability Catalog",
        updated_by: "dashboard",
      });
      setReview(false);
    }
  }, [policy.data]);
  const filtered = (capabilities.data?.items || []).filter((item) =>
    `${item.title} ${item.id} ${item.subtitle} ${item.status}`
      .toLowerCase()
      .includes(query.toLowerCase()),
  );

  const save = async () => {
    if (!selected) return;
    setStatus("Saving reviewed policy to capability manifest...");
    try {
      await updateCapabilityRisk(selected.id, draft);
      setReview(false);
      setStatus(
        "Manifest updated permanently, catalog reloaded, and effective policy audited.",
      );
      await policy.refetch();
      await queryClient.invalidateQueries({
        queryKey: ["ui-resource", "capabilities"],
      });
    } catch (error) {
      setStatus(String(error instanceof Error ? error.message : error));
    }
  };
  const reset = async () => {
    if (!selected) return;
    if (!review) {
      setReview(true);
      setStatus(
        "Review reset: effective policy will return to the manifest values.",
      );
      return;
    }
    try {
      await resetCapabilityRisk(selected.id);
      setReview(false);
      setStatus("Override reset and effective policy reloaded.");
      await policy.refetch();
    } catch (error) {
      setStatus(String(error instanceof Error ? error.message : error));
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
          data-severity={
            status.toLowerCase().includes("failed") || status.includes("403")
              ? "warning"
              : "info"
          }
        >
          {status}
        </div>
      ) : null}
      <section className="capability-console__layout">
        <div className="capability-list">
          {filtered.map((item) => (
            <button
              type="button"
              aria-current={selected?.id === item.id}
              onClick={() => setSelected(item)}
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
                <h4>Override draft</h4>
                <label>
                  Risk
                  <select
                    value={String(draft.risk_level || "low")}
                    onChange={(event) => {
                      const riskLevel = event.currentTarget.value;
                      setDraft((value) => ({
                        ...value,
                        risk_level: riskLevel,
                      }));
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
                    checked={Boolean(draft.requires_approval)}
                    onChange={(event) => {
                      const checked = event.currentTarget.checked;
                      setDraft((value) => ({
                        ...value,
                        requires_approval: checked,
                      }));
                    }}
                  />
                  Requires approval
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={Boolean(draft.enabled ?? true)}
                    onChange={(event) => {
                      const checked = event.currentTarget.checked;
                      setDraft((value) => ({ ...value, enabled: checked }));
                    }}
                  />
                  Enabled
                </label>
                <label>
                  Reason
                  <input
                    value={String(draft.reason || "")}
                    onChange={(event) => {
                      const value = event.currentTarget.value;
                      setDraft((item) => ({ ...item, reason: value }));
                    }}
                  />
                </label>
                <div>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => setReview(true)}
                  >
                    <ShieldCheck size={14} />
                    Review changes
                  </button>
                  <a
                    className="secondary-button"
                    href={`/dashboard/capabilities/policy-simulation?capability_id=${encodeURIComponent(selected.id)}`}
                  >
                    <FlaskConical size={14} />
                    Test preview
                  </a>
                  <button
                    className="danger-button"
                    type="button"
                    onClick={() => void reset()}
                  >
                    <RotateCcw size={14} />
                    {review ? "Confirm manifest reset" : "Reset override"}
                  </button>
                </div>
              </section>
              {review ? (
                <section className="action-preview">
                  <h4>Policy change review</h4>
                  <dl>
                    <div>
                      <dt>Target</dt>
                      <dd>{selected.id}</dd>
                    </div>
                    <div>
                      <dt>Before</dt>
                      <dd>{summarize(values.effective)}</dd>
                    </div>
                    <div>
                      <dt>After</dt>
                      <dd>{summarize(draft)}</dd>
                    </div>
                    <div>
                      <dt>Impact</dt>
                      <dd>
                        PolicyEngine and ToolBroker will use this effective
                        policy immediately.
                      </dd>
                    </div>
                    <div>
                      <dt>Verification</dt>
                      <dd>
                        Reload CapabilityCatalog, compare effective policy, and
                        inspect capability.effective_policy.changed audit.
                      </dd>
                    </div>
                  </dl>
                  <footer>
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() => setReview(false)}
                    >
                      Cancel
                    </button>
                    <button
                      className="primary-button"
                      type="button"
                      onClick={() => void save()}
                    >
                      Save override
                    </button>
                  </footer>
                </section>
              ) : null}
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
