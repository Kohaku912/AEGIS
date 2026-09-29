/**
 * ToolCallJson (Phase D6 / DASHBOARD_REFINED_PLAN.md §3 Phase D6 / instruction.md §7, §8).
 *
 * Tool call の arguments / result / error を `<pre>` で表示する共通コンポーネント。
 * 長い JSON は maxLen 文字 (デフォルト 1000) を超えると自動で折りたたみ、
 * `[Show all (N chars)]` ボタンで全文表示に切替可能。
 *
 * 使い方:
 *   <ToolCallJson label="args" value={payload.args} />
 *   <ToolCallJson label="output" value={payload.output} maxLen={2000} />
 *
 * 設計判断:
 * - `JSON.stringify(value, null, 2)` で整形 (esbuild の transformer で動作)
 * - value が undefined / null のときは何も描画しない
 * - value がプリミティブ (string / number / boolean) のときはそのまま `<pre>` に表示
 * - 展開状態は useState で local 管理 (Phase D6 DoD: `[Show all]` ボタン)
 */

import { useState } from "react";

export function ToolCallJson({
  label,
  value,
  maxLen = 1000,
}: {
  label: string;
  value: unknown;
  maxLen?: number;
}) {
  const [expanded, setExpanded] = useState(false);
  if (value === undefined || value === null) return null;

  let json: string;
  if (typeof value === "string") {
    json = value;
  } else {
    try {
      json = JSON.stringify(value, null, 2);
    } catch {
      json = String(value);
    }
  }
  const totalLen = json.length;
  const needsTruncation = totalLen > maxLen;
  const showAll = expanded || !needsTruncation;
  const preview = needsTruncation ? json.slice(0, maxLen) : json;

  return (
    <div className="tool-call-json">
      <div className="tool-call-json__label">
        <strong>{label}</strong>
        {needsTruncation ? (
          <>
            {" "}
            <button
              type="button"
              className="link-button"
              onClick={() => setExpanded((s) => !s)}
              data-testid={`tool-call-json-toggle-${label}`}
              aria-expanded={expanded}
            >
              {expanded ? "[Show less]" : `[Show all (${totalLen} chars)]`}
            </button>
          </>
        ) : null}
      </div>
      <pre className="raw-json tool-call-json__pre">
        {showAll
          ? json
          : `${preview}\n… (truncated, ${totalLen - maxLen} more chars)`}
      </pre>
    </div>
  );
}
