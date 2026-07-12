import type { UiOverview } from "../types";

export function Work({ overview }: { overview: UiOverview }) {
  const task = overview.current_task.data;
  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <h2>Work</h2>
          <div className="muted">Active task, waiting state, and execution phase.</div>
        </div>
      </div>
      <div className="grid">
        <div className="stat">
          <span className="muted">Current task</span>
          <b style={{ fontSize: 18 }}>{task.title}</b>
          <p className="muted">{task.current_action || task.blocked_reason || "No active execution."}</p>
        </div>
        {(task.steps || []).map((step, index) => (
          <div className="list-row" key={String(step.step_id || index)}>
            <div>
              <strong>{String(step.description || step.capability_id || `Step ${index + 1}`)}</strong>
              <div className="muted">{String(step.status || "unknown")}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
