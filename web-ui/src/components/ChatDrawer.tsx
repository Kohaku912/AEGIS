import { MessageSquare, Send, X } from "lucide-react";
import { FormEvent, useState } from "react";
import { sendChat } from "../api/client";

type Props = {
  open: boolean;
  onClose: () => void;
};

export function ChatDrawer({ open, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [log, setLog] = useState<Array<{ role: string; text: string }>>([]);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || busy) return;
    setMessage("");
    setLog((items) => [...items, { role: "user", text }]);
    setBusy(true);
    try {
      const result = await sendChat(text);
      setLog((items) => [...items, { role: "aegis", text: String(result.response || result.message || "Done.") }]);
    } catch (exc) {
      setLog((items) => [...items, { role: "system", text: exc instanceof Error ? exc.message : String(exc) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="chat-drawer" data-open={open} aria-hidden={!open}>
      <div className="chat-drawer__header">
        <h2><MessageSquare size={18} aria-hidden="true" /> Chat</h2>
        <button className="icon-button" onClick={onClose} title="Close chat">
          <X size={16} aria-hidden="true" />
        </button>
      </div>
      <div className="chat-log">
        {log.length === 0 ? <div className="muted">Chat is ready. Messages are sent through the existing AEGIS chat API.</div> : null}
        {log.map((item, index) => (
          <div className="list-row chat-log__item" key={`${item.role}-${index}`}>
            <div>
              <strong>{item.role}</strong>
              <div>{item.text}</div>
            </div>
          </div>
        ))}
      </div>
      <form className="chat-form" onSubmit={submit}>
        <textarea value={message} onChange={(event) => setMessage(event.target.value)} aria-label="Message" />
        <button className="icon-button" title="Send message" disabled={busy}>
          <Send size={16} aria-hidden="true" />
        </button>
      </form>
    </aside>
  );
}
