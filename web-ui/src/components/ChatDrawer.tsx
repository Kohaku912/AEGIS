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
      setLog((items) => [...items, { role: "AEGIS", text: String(result.response || result.message || "完了しました。") }]);
    } catch (exc) {
      setLog((items) => [...items, { role: "system", text: exc instanceof Error ? exc.message : String(exc) }]);
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }

  return (
    <aside className="chat-drawer" data-open={open} aria-hidden={!open} aria-label="AEGISチャット" aria-busy={busy}>
      <div className="chat-drawer__header">
        <h2><MessageSquare size={18} aria-hidden="true" /> AEGISと話す</h2>
        <button className="icon-button" onClick={onClose} title="チャットを閉じる" aria-label="チャットを閉じる">
          <X size={16} aria-hidden="true" />
        </button>
      </div>
      <div className="chat-log">
        {log.length === 0 ? <div className="muted">AEGISへの依頼や質問を入力してください。</div> : null}
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
        <textarea ref={inputRef} value={message} onChange={(event) => setMessage(event.target.value)} aria-label="メッセージ" disabled={busy} />
        <button className="icon-button" title={busy ? "送信中" : "送信"} aria-label={busy ? "送信中" : "メッセージを送信"} disabled={busy || !message.trim()}>
          <Send size={16} aria-hidden="true" />
        </button>
      </form>
      <div className="sr-only" aria-live="polite">{busy ? "メッセージを送信しています" : ""}</div>
    </aside>
  );
}
