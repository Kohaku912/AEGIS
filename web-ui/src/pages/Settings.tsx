import { KeyRound, ShieldCheck, SlidersHorizontal } from "lucide-react";

export function Settings() {
  return (
    <div className="grid grid--three">
      <section className="panel">
        <div className="panel__header"><h2><ShieldCheck size={18} /> Security</h2></div>
        <p className="muted">Passkey-only sessions and fresh authentication are enforced by the backend middleware.</p>
        <a className="primary-button" href="/dashboard/security/passkeys"><KeyRound size={16} /> Passkeys</a>
      </section>
      <section className="panel">
        <div className="panel__header"><h2><SlidersHorizontal size={18} /> Existing Settings</h2></div>
        <p className="muted">Detailed legacy-compatible settings APIs remain available after authentication.</p>
        <a className="ghost-button" href="/api/settings">Settings API</a>
      </section>
      <section className="panel">
        <div className="panel__header"><h2>Display</h2></div>
        <p className="muted">The dedicated display opens read-only status and presentation UI, not this admin dashboard.</p>
        <a className="ghost-button" href="/display">Open Display</a>
      </section>
    </div>
  );
}
