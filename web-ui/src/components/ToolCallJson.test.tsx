/**
 * ToolCallJson (Phase D6 / DASHBOARD_REFINED_PLAN.md §3 Phase D6 / instruction.md §7, §8).
 *
 * Tool call JSON 共通コンポーネントの DoD tests.
 *
 * DoD チェックリスト:
 * - [x] 短い JSON はそのまま `<pre>` に整形表示
 * - [x] 長い JSON (maxLen 超) は truncated + `[Show all (N chars)]` ボタン表示
 * - [x] `[Show all]` クリックで全文表示 + `[Show less]` に切替
 * - [x] value が undefined / null のときは何も描画しない
 * - [x] value が string のときもそのまま表示
 * - [x] label が必須
 */
import { afterEach, describe, expect, it } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ToolCallJson } from "./ToolCallJson";

afterEach(() => {
  cleanup();
});

describe("ToolCallJson", () => {
  it("renders short JSON as formatted pre", () => {
    render(<ToolCallJson label="args" value={{ a: 1, b: "two" }} />);
    expect(screen.getByText("args")).toBeTruthy();
    expect(screen.getByText(/"a": 1/)).toBeTruthy();
    expect(screen.getByText(/"b": "two"/)).toBeTruthy();
    // 短いので Show all ボタンは出ない
    expect(screen.queryByText(/Show all/)).toBeNull();
  });

  it("renders nothing when value is null", () => {
    const { container } = render(<ToolCallJson label="args" value={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing when value is undefined", () => {
    const { container } = render(<ToolCallJson label="args" value={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders string value without JSON.stringify", () => {
    render(<ToolCallJson label="output" value="hello world" />);
    expect(screen.getByText("output")).toBeTruthy();
    expect(screen.getByText("hello world")).toBeTruthy();
  });

  it("collapses long JSON and shows Show all button", () => {
    const longValue = { data: "x".repeat(2000) };
    render(<ToolCallJson label="output" value={longValue} maxLen={500} />);
    const toggle = screen.getByTestId("tool-call-json-toggle-output");
    expect(toggle.textContent || "").toMatch(/Show all/);
    // truncated マーカー
    expect(screen.getByText(/truncated, /)).toBeTruthy();
  });

  it("expands on Show all click and switches to Show less", async () => {
    const longValue = { data: "y".repeat(1200) };
    render(<ToolCallJson label="output" value={longValue} maxLen={500} />);
    const toggleBefore = screen.getByTestId("tool-call-json-toggle-output");
    expect(toggleBefore.textContent || "").toMatch(/Show all/);
    // クリックして展開 (fireEvent 経由で React の act() 内で state 更新)
    fireEvent.click(toggleBefore);
    // state 更新後の再レンダリングを待つ
    await waitFor(() => {
      const toggleAfter = screen.getByTestId("tool-call-json-toggle-output");
      expect(toggleAfter.textContent || "").toMatch(/Show less/);
    });
  });

  it("respects custom maxLen", () => {
    // data: "z"×150 → JSON で 166 chars / maxLen=100 → 66 chars truncated
    const value = { data: "z".repeat(150) };
    render(<ToolCallJson label="args" value={value} maxLen={100} />);
    const toggle = screen.getByTestId("tool-call-json-toggle-args");
    expect(toggle.textContent || "").toMatch(/Show all/);
    expect(screen.getByText(/truncated, 66 more chars/)).toBeTruthy();
  });
});
