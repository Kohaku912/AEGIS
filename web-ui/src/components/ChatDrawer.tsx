import { MessageSquare, Send, X } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { createRequestId, sendChat } from "../api/client";

type Props = {
  open: boolean;
  onClose: () => void;
};

export function ChatDrawer({ open, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [log, setLog] = useState<Array<{ role: string; text: string }>>([]);
  const [busy, setBusy] = useState(false);
  const inFlight = useRef(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (open) inputRef.current?.focus();
    const close = (event: KeyboardEvent) => { if (open && event.key === "Escape") onClose(); };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onClose, open]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || inFlight.current) return;
    inFlight.current = true;
    setMessage("");
    setLog((items) => [...items, { role: "user", text }]);
    setBusy(true);
    try {
      const result = await sendChat(text, createRequestId());
      setLog((items) => [...items, { role: "AEGIS", text: String(result.response || result.message || "Completed.") }]);
    } catch (exc) {
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
          {log.length === 0 ? <div className="muted">Enter a request or question for AEGIS.</div> : null}
          {log.map((item, index) => (
            <div className="list-row chat-log__item" key={`${item.role}-${index}`}>
              <div>
                <strong>{item.role}</strong>
                <div>{item.text}</div>
              </div>
            </div>
          ))}
        </div>
        <form className="chat-form" onSubmit={submit} aria-busy={busy}>
          <textarea ref={inputRef} value={message} onChange={(event) => setMessage(event.target.value)} aria-label="Message" disabled={busy} />
          <button className="icon-button" title={busy ? "Sending" : "Send"} aria-label={busy ? "Sending" : "Send message"} disabled={busy || !message.trim()}>
            <Send size={16} aria-hidden="true" />
          </button>
        </form>
        <div className="sr-only" aria-live="polite">{busy ? "Sending message" : ""}</div>
      </aside>
    </>
  );
}
