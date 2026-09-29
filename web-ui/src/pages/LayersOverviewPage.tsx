import { LlmLayerPanel } from "./LlmLayerPanel";

export function LayersOverviewPage() {
  return (
    <div className="grid">
      <section className="panel">
        <div className="panel__header">
          <div>
            <h2>Layer Comparison</h2>
            <div className="muted">L1 / L2 / L3 を同じ文脈で並べて、現在の bottleneck layer を追えるようにします。</div>
          </div>
        </div>
      </section>
      <LlmLayerPanel layer="L1" />
      <LlmLayerPanel layer="L2" />
      <LlmLayerPanel layer="L3" />
    </div>
  );
}
