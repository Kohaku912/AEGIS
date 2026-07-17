import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, GitCompare, History, RotateCcw, TestTube2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchPrompt, fetchPrompts, fetchPromptVersions, rollbackPrompt, updatePrompt, validatePrompt } from "../api/client";

export function ModelsPromptsPage() {
  const queryClient = useQueryClient();
  const prompts = useQuery({ queryKey: ["prompts"], queryFn: fetchPrompts });
  const [selectedId, setSelectedId] = useState("");
  const detail = useQuery({ queryKey: ["prompt", selectedId], queryFn: () => fetchPrompt(selectedId), enabled: Boolean(selectedId) });
  const versions = useQuery({ queryKey: ["prompt-versions", selectedId], queryFn: () => fetchPromptVersions(selectedId), enabled: Boolean(selectedId) });
  const [draft, setDraft] = useState("");
  const [validation, setValidation] = useState<Record<string, unknown>>();
  const [review, setReview] = useState(false);
  const [rollbackId, setRollbackId] = useState("");
  const [status, setStatus] = useState("");
  useEffect(() => { if (!selectedId && prompts.data?.length) setSelectedId(String(prompts.data[0].prompt_id)); }, [prompts.data, selectedId]);
  useEffect(() => { if (detail.data) { setDraft(String(detail.data.template || "")); setValidation(undefined); setReview(false); } }, [detail.data]);
  const current = String(detail.data?.template || "");
  const diff = useMemo(() => lineDiff(current, draft), [current, draft]);
  const editable = Boolean(detail.data?.editable) && !Boolean(detail.data?.protected);

  const testCandidate = async () => {
    setStatus("Validating candidate structure and required variables...");
    try { const result = await validatePrompt(selectedId, draft); setValidation((result.candidate || {}) as Record<string, unknown>); setStatus(Boolean((result.candidate as Record<string, unknown>)?.valid) ? "Candidate passed validation. Review the diff before saving." : "Candidate validation failed."); }
    catch (error) { setStatus(error instanceof Error ? error.message : String(error)); }
  };
  const save = async () => {
    if (!review || !validation?.valid) return;
    setStatus("Saving fresh-authenticated prompt revision...");
    try { await updatePrompt(selectedId, draft); setReview(false); setValidation(undefined); setStatus("Prompt revision persisted and audited."); await queryClient.invalidateQueries({ queryKey: ["prompt", selectedId] }); await queryClient.invalidateQueries({ queryKey: ["prompt-versions", selectedId] }); }
    catch (error) { setStatus(error instanceof Error ? error.message : String(error)); }
  };
  const rollback = async () => {
    if (!rollbackId) return;
    setStatus("Restoring selected revision through fresh-authenticated rollback...");
    try { await rollbackPrompt(selectedId, rollbackId); setRollbackId(""); setStatus("Rollback persisted as a new revision and audited."); await detail.refetch(); await versions.refetch(); }
    catch (error) { setStatus(error instanceof Error ? error.message : String(error)); }
  };

  return <div className="prompt-console">
    <header className="resource-page__hero"><div><span>LLM configuration</span><h2>Models & Prompts</h2><p>Registry metadata is visible normally. Prompt contents and mutation controls are isolated in Developer Mode.</p></div><strong>{prompts.data?.length || 0} prompts</strong></header>
    <section className="prompt-console__layout">
      <aside className="prompt-list">{(prompts.data || []).map((prompt) => <button type="button" aria-current={selectedId === prompt.prompt_id} onClick={() => setSelectedId(String(prompt.prompt_id))} key={String(prompt.prompt_id)}><strong>{String(prompt.prompt_id)}</strong><span>v{String(prompt.version || "unknown")} / {prompt.protected ? "protected" : prompt.editable ? "editable" : "read-only"}</span><code>{String(prompt.hash || "")}</code></button>)}</aside>
      <main className="prompt-detail">{detail.data ? <><header><span>{detail.data.protected ? "Protected" : detail.data.editable ? "Editable" : "Read-only"}</span><h3>{selectedId}</h3><p>Version {String(detail.data.version)} / hash {String(detail.data.hash)}</p></header><section className="prompt-metadata"><div><span>Routing use</span><strong>PromptRegistry</strong></div><div><span>Mutation gate</span><strong>Developer Mode + fresh passkey</strong></div><div><span>Rollback</span><strong>{versions.data?.length || 0} persisted revisions</strong></div></section><div className="developer-gate">Enable Developer Mode in the top bar to inspect or modify prompt contents.</div><section className="prompt-editor developer-only"><label>Candidate template<textarea value={draft} readOnly={!editable} onChange={(event) => { setDraft(event.currentTarget.value); setValidation(undefined); setReview(false); }} /></label><div className="prompt-actions"><button className="secondary-button" type="button" disabled={!editable || draft === current} onClick={() => void testCandidate()}><TestTube2 size={14} />Validate candidate</button><button className="secondary-button" type="button" disabled={!validation?.valid || draft === current} onClick={() => setReview(true)}><GitCompare size={14} />Review diff</button></div>{validation ? <div className="validation-result" data-valid={Boolean(validation.valid)}><CheckCircle2 size={15} /><span>{validation.valid ? "Valid candidate" : (validation.errors as string[] || []).join(" ")}</span></div> : null}{review ? <section className="prompt-diff"><header><strong>Required review</strong><span>{diff.added} added / {diff.removed} removed / {diff.unchanged} unchanged lines</span></header><div><article><span>Current</span><pre>{current}</pre></article><article><span>Candidate</span><pre>{draft}</pre></article></div><footer><button className="secondary-button" type="button" onClick={() => setReview(false)}>Cancel</button><button className="primary-button" type="button" onClick={() => void save()}>Save tested revision</button></footer></section> : null}<section className="prompt-history"><h4><History size={14} />Revision history</h4>{(versions.data || []).map((version) => <label key={String(version.revision_id)}><input type="radio" name="rollback-revision" value={String(version.revision_id)} checked={rollbackId === version.revision_id} onChange={(event) => setRollbackId(event.currentTarget.value)} /><span><strong>{new Date(Number(version.created_at)).toLocaleString()}</strong><small>{String(version.before_hash)} → {String(version.after_hash)}</small></span></label>)}{rollbackId ? <div className="action-preview"><p>Rollback creates a new auditable revision. The selected pre-change template becomes effective.</p><button className="danger-button" type="button" onClick={() => void rollback()}><RotateCcw size={14} />Confirm rollback</button></div> : null}</section></section>{status ? <p className="form-status" role="status">{status}</p> : null}</> : <p>Select a prompt to inspect registry metadata.</p>}</main>
    </section>
  </div>;
}

function lineDiff(before: string, after: string) {
  const left = before.split("\n"); const right = after.split("\n");
  const unchanged = right.filter((line, index) => left[index] === line).length;
  return { added: Math.max(0, right.length - unchanged), removed: Math.max(0, left.length - unchanged), unchanged };
}
