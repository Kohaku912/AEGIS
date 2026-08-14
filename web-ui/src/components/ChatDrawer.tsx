import { MessageSquare, Send, X } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import {
  createRequestId,
  fetchChatHistory,
  respondChat,
  sendChat,
  type ChatSendResult,
} from "../api/client";

type LogItem = { role: string; text: string };
type AskUser = { question: string; options: string[]; pendingContext: Record<string, unknown> };

type Props = {
  open: boolean;
  onClose: () => void;
};

function applyResult(result: ChatSendResult): { lines: LogItem[]; ask?: AskUser } {
  if (result.needs_user_input) {
    return {
      lines: [{ role: "AEGIS", text: String(result.question || "AEGIS needs a decision.") }],
      ask: {
        question: String(result.question || ""),
        options: Array.isArray(result.options) ? result.options.map(String) : [],
        pendingContext: result.pending_context || {},
      },
    };
  }
  const lines: LogItem[] = [];
  for (const tool of result.tool_results || []) {
    const name = String(tool.function || "tool");
    const ok = tool.success === false ? "failed" : "ok";
    lines.push({ role: "tool", text: `${name} (${ok})${tool.result ? `: ${tool.result}` : ""}` });
  }
  if (result.approval_needed) {
    const id = String(result.approval_id || "");
    lines.push({
      role: "system",
      text: id ? `Approval needed: ${id}` : "Approval needed. Open Approvals to continue.",
    });
  }
  lines.push({ role: "AEGIS", text: String(result.response || result.message || "Completed.") });
  return { lines };
}

export function ChatDrawer({ open, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [log, setLog] = useState<LogItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [ask, setAsk] = useState<AskUser>();
  const inFlight = useRef(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
    const conversationId = new URLSearchParams(window.location.search).get("conversation_id") || "";
    void fetchChatHistory()
      .then((entries) => {
        const items: LogItem[] = [];
        for (const entry of entries) {
          if (conversationId && entry.conversation_id && entry.conversation_id !== conversationId) continue;
          if (entry.user) items.push({ role: "user", text: String(entry.user) });
          if (entry.bot) items.push({ role: "AEGIS", text: String(entry.bot) });
        }
        setLog(items);
      })
      .catch((exc) => {
        setLog([{ role: "system", text: exc instanceof Error ? exc.message : String(exc) }]);
      });
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onClose, open]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || inFlight.current || ask) return;
    inFlight.current = true;
    setMessage("");
    setLog((items) => [...items, { role: "user", text }]);
    setBusy(true);
    try {
      const result = await sendChat(text, createRequestId());
      const next = applyResult(result);
      setAsk(next.ask);
      setLog((items) => [...items, ...next.lines]);
    } catch (exc) {
      setLog((items) => [...items, { role: "system", text: exc instanceof Error ? exc.message : String(exc) }]);
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  async function answer(choice: string) {
    if (!ask || inFlight.current) return;
    inFlight.current = true;
    setLog((items) => [...items, { role: "user", text: choice }]);
    setBusy(true);
    try {
      const result = await respondChat(choice, ask.pendingContext);
      const next = applyResult(result);
      setAsk(next.ask);
      setLog((items) => [...items, ...next.lines]);
    } catch (exc) {
      setAsk(undefined);
      setLog((items) => [...items, { role: "system", text: exc instanceof Error ? exc.message : String(exc) }]);
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  return (
    <>
      {open ? <button type="button" className="chat-backdrop" aria-label="Close chat overlay" onClick={onClose} /> : null}
      <aside className="chat-drawer" data-open={open} aria-hidden={!open} aria-label="AEGIS chat" aria-busy={busy}>
        <div className="chat-drawer__header">
          <h2><MessageSquare size={18} aria-hidden="true" /> Talk to AEGIS</h2>
          <button className="icon-button" onClick={onClose} title="Close chat" aria-label="Close chat">
            <X size={16} aria-hidden="true" />
          </button>
        </div>
        <div className="chat-log">
          {log.length === 0 && !ask ? <div className="muted">Enter a request or question for AEGIS.</div> : null}
          {log.map((item, index) => (
            <div className="list-row chat-log__item" key={`${item.role}-${index}`}>
              <div>
                <strong>{item.role}</strong>
                <div>{item.text}</div>
                {item.role === "system" && item.text.startsWith("Approval needed:") ? (
                  <a href="/dashboard/approvals">Open Approvals</a>
                ) : null}
              </div>
            </div>
          ))}
          {ask ? (
            <div className="list-row chat-log__item">
              <div>
                <strong>Choose</strong>
                <div className="chat-ask">
                  {ask.options.length ? ask.options.map((option) => (
                    <button key={option} type="button" className="secondary-button" disabled={busy} onClick={() => void answer(option)}>
                      {option}
                    </button>
                  )) : (
                    <form
                      onSubmit={(event) => {
                        event.preventDefault();
                        const field = event.currentTarget.elements.namedItem("ask") as HTMLInputElement | null;
                        const value = field?.value.trim() || "";
                        if (value) void answer(value);
                      }}
                    >
                      <input name="ask" aria-label="Answer" disabled={busy} />
                      <button type="submit" disabled={busy}>Send</button>
                    </form>
                  )}
                </div>
              </div>
            </div>
          ) : null}
        </div>
        <form className="chat-form" onSubmit={submit} aria-busy={busy}>
          <textarea ref={inputRef} value={message} onChange={(event) => setMessage(event.target.value)} aria-label="Message" disabled={busy || Boolean(ask)} />
          <button className="icon-button" title={busy ? "Sending" : "Send"} aria-label={busy ? "Sending" : "Send message"} disabled={busy || Boolean(ask) || !message.trim()}>
            <Send size={16} />
          </button>
        </form>
        <div className="sr-only" aria-live="polite">{busy ? "Sending message" : ""}</div>
      </aside>
    </>
  );
}
