// L1PanelPage.tsx — DASHBOARD_V3_PLAN.md Phase L6
//
// L1 (知覚 / Router / 常時稼働) 専用パネル。
// LlmLayerPanel の薄いラッパー。

import { LlmLayerPanel } from "./LlmLayerPanel";

export function L1PanelPage() {
  return <LlmLayerPanel layer="L1" />;
}
