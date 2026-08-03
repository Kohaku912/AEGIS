import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { UiOverview } from "../types";
import { IncidentsPage } from "./IncidentsPage";
import { OperationsPage } from "./OperationsPage";
import { PerformancePage } from "./PerformancePage";

function overviewWithOps(operations: Array<Record<string, unknown>>): UiOverview {
  return {
    generated_at: Date.now(),
    activity: {
      generated_at: Date.now(),
      source_updated_at: Date.now(),
      stale: false,
      data: { operations },
    },
    servers: { data: { items: [{ server_id: "browser-server", status: "ONLINE", latency_ms: 42 }] } },
    usage: { data: { avg_latency_ms: 120, budget_status: "ok" } },
    tasks: { data: { running: [], waiting_approval_count: 0 } },
    errors: { data: { items: [] } },
    repairs: {
      data: {
        items: [{
          repair_id: "repair-1",
          title: "AGORAへの返信投稿に失敗",
          impact: "返信候補1件が未送信",
          status: "awaiting_user",
          attempt_count: 2,
          next_action: "認証を更新して再試行",
          operation_id: "op-agora-1",
        }],
      },
    },
  } as unknown as UiOverview;
}

describe("observation redesign pages", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("shows concrete AGORA operation detail instead of species labels", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("/api/operations/op-agora-1")) {
        return new Response(JSON.stringify({
          operation_id: "op-agora-1",
          action_summary: "AGORAから未処理投稿12件を取得し、2件を返信候補として分類",
          result_summary: "AGORAから未処理投稿12件を取得し、2件を返信候補として分類",
          purpose: "返信要否を判断",
          decision_reason: "未処理の社会的義務がある",
          target_summary: "AGORA",
          result_status: "success",
          goal_status: "achieved",
          verification_status: "passed",
          source: "autonomous",
          kind: "autonomous",
          kind_label: "自律判断",
          steps: [{
            action: "投稿を取得",
            capability_id: "ai-server.agora.read_posts",
            output_summary: "12件取得、2件を候補化",
            status: "ok",
          }],
          causal_chain: [
            { stage: "trigger", label: "Trigger", summary: "自律判断", status: "present" },
            { stage: "decision", label: "判断", summary: "返信要否を判断", status: "present" },
            { stage: "execution", label: "実行Step", summary: "12件取得、2件を候補化", status: "present" },
            { stage: "result", label: "結果", summary: "2件を返信候補として分類", status: "present" },
            { stage: "verification", label: "Verification", summary: "Goal達成", status: "present" },
          ],
          linked_entity_ids: { task: ["task-1"], approval: ["appr-1"] },
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(JSON.stringify({ items: [] }), { status: 200, headers: { "Content-Type": "application/json" } });
    });

    render(
      <OperationsPage
        overview={overviewWithOps([{
          operation_id: "op-agora-1",
          action_summary: "AGORAから未処理投稿12件を取得し、2件を返信候補として分類",
          target_summary: "AGORA",
          result_status: "success",
          goal_status: "achieved",
          source: "autonomous",
          updated_at: Date.now(),
        }])}
        detailId="op-agora-1"
      />,
    );

    await waitFor(() => {
      expect(screen.getAllByText(/AGORAから未処理投稿12件/).length).toBeGreaterThan(0);
    });
    expect(screen.queryByText(/^自律実行$/)).not.toBeInTheDocument();
    expect(screen.getAllByText(/返信要否を判断/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Goal達成|達成/).length).toBeGreaterThan(0);
  });

  it("renders intentional non-action with observation reason", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    render(
      <OperationsPage
        overview={overviewWithOps([{
          operation_id: "op-skip-1",
          action_summary: "行動しなかった：ユーザーがゲーム中で緊急性が低いため通知を保留",
          result_summary: "行動しなかった：ユーザーがゲーム中で緊急性が低いため通知を保留",
          result_status: "non_action",
          goal_status: "not_applicable",
          wait_reason: "ユーザーがゲーム中で緊急性が低いため通知を保留",
          source: "autonomous",
          updated_at: Date.now(),
          causal_chain: [
            { stage: "decision", label: "判断", summary: "ユーザーがゲーム中で緊急性が低いため通知を保留", status: "present" },
            { stage: "execution", label: "実行Step", summary: "行動なし", status: "skipped" },
          ],
        }])}
      />,
    );
    expect(screen.getAllByText(/行動しなかった：ユーザーがゲーム中/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/^自律実行をした$/)).not.toBeInTheDocument();
  });

  it("shows unmet goal when verification failed despite tool success", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    render(
      <OperationsPage
        overview={overviewWithOps([{
          operation_id: "op-unmet-1",
          action_summary: "ChromeでAEGISリポジトリを開き、最新Commitの変更内容を確認",
          result_status: "partial",
          goal_status: "unmet",
          verification_status: "failed",
          target_summary: "Browser",
          source: "user",
          updated_at: Date.now(),
        }])}
      />,
    );
    expect(screen.getAllByText(/未達/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/最新Commit/).length).toBeGreaterThan(0);
  });

  it("groups repairs into incidents with next action", () => {
    render(<IncidentsPage overview={overviewWithOps([])} />);
    expect(screen.getAllByText(/AGORAへの返信投稿に失敗/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/返信候補1件が未送信/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/認証を更新して再試行/).length).toBeGreaterThan(0);
  });

  it("renders performance metrics from servers", () => {
    render(<PerformancePage overview={overviewWithOps([])} />);
    expect(screen.getAllByText("browser-server").length).toBeGreaterThan(0);
    expect(screen.getAllByText("LLM Latency").length).toBeGreaterThan(0);
  });
});
