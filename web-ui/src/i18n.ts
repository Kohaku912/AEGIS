export const ja = {
  appSubtitle: "個人AI コントロールセンター",
  commands: "コマンド",
  createTask: "タスクを作成",
  chat: "AEGISと話す",
  developerMode: "開発者モード",
  updated: "最終更新",
  retry: "再試行",
  loading: "読み込み中",
  noData: "表示できるデータはありません",
  needsAttention: "対応が必要",
  tasks: "タスク",
  search: "検索",
  status: "状態",
  all: "すべて",
  saveView: "現在の表示を保存",
  previous: "前へ",
  next: "次へ",
  cancel: "キャンセル",
  confirm: "確認して実行",
  send: "送信",
} as const;

export function formatDateTime(value: number | string | undefined): string {
  if (!value) return "未取得";
  const parsed = typeof value === "number" ? value : Date.parse(value);
  return Number.isFinite(parsed)
    ? new Intl.DateTimeFormat("ja-JP", { dateStyle: "medium", timeStyle: "medium", timeZone: "Asia/Tokyo" }).format(parsed)
    : "未取得";
}

export function formatRelative(value: number | string | undefined, now = Date.now()): string {
  if (!value) return "";
  const parsed = typeof value === "number" ? value : Date.parse(value);
  const seconds = Math.max(0, Math.round((now - parsed) / 1000));
  if (seconds < 60) return `${seconds}秒前`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}分前`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)}時間前`;
  return `${Math.round(seconds / 86400)}日前`;
}
