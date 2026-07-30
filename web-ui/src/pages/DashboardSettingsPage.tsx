import { useState } from "react";
import { PageHeader } from "../components/DashboardPrimitives";

type DashboardSettings = {
  density: "comfortable" | "compact";
  developer: boolean;
  language: "ja" | "en";
  theme: "system" | "dark" | "light";
  pinnedPages: string;
  refreshInterval: number;
};

const defaults: DashboardSettings = { density: "comfortable", developer: false, language: "ja", theme: "system", pinnedPages: "/dashboard,/dashboard/attention", refreshInterval: 30 };

export function DashboardSettingsPage() {
  const [settings, setSettings] = useState<DashboardSettings>(() => {
    try { return { ...defaults, ...JSON.parse(localStorage.getItem("aegis.dashboard.settings") || "{}") }; } catch { return defaults; }
  });
  const update = <K extends keyof DashboardSettings>(key: K, value: DashboardSettings[K]) => {
    const next = { ...settings, [key]: value };
    setSettings(next);
    localStorage.setItem("aegis.dashboard.settings", JSON.stringify(next));
  };
  return <div className="grid"><PageHeader title="ダッシュボード設定" description="このブラウザーに保存される表示と更新の設定です。" /><section className="panel"><div className="metric-list"><label className="metric-row"><span>密度</span><select value={settings.density} onChange={(event) => update("density", event.currentTarget.value as DashboardSettings["density"])}><option value="comfortable">標準</option><option value="compact">コンパクト</option></select></label><label className="metric-row"><span>開発者表示</span><input type="checkbox" checked={settings.developer} onChange={(event) => update("developer", event.currentTarget.checked)} /></label><label className="metric-row"><span>言語</span><select value={settings.language} onChange={(event) => update("language", event.currentTarget.value as DashboardSettings["language"])}><option value="ja">日本語</option><option value="en">English</option></select></label><label className="metric-row"><span>テーマ</span><select value={settings.theme} onChange={(event) => update("theme", event.currentTarget.value as DashboardSettings["theme"])}><option value="system">システム</option><option value="dark">ダーク</option><option value="light">ライト</option></select></label><label className="metric-row"><span>ピン留めページ</span><input value={settings.pinnedPages} onChange={(event) => update("pinnedPages", event.currentTarget.value)} /></label><label className="metric-row"><span>更新間隔（秒）</span><input type="number" min={5} value={settings.refreshInterval} onChange={(event) => update("refreshInterval", Number(event.currentTarget.value))} /></label></div></section></div>;
}
