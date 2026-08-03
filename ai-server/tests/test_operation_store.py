"""Tests for first-class OperationStore."""

from __future__ import annotations

from aegis_ai.operations import OperationStore, build_causal_chain
from aegis_ai.operations.store import OperationRecord


def test_record_autonomous_cycle_persists_concrete_summaries(tmp_path) -> None:
    store = OperationStore(data_dir=tmp_path)
    record = store.record_autonomous_cycle(
        tasks=[
            {
                "capability_id": "ai-server.agora.read_posts",
                "what_was_done": "AGORAから未処理投稿を取得",
                "arguments": {"limit": 12},
                "changed_state": "inbox_count=12",
            }
        ],
        results=[{"success": True, "result": "12件取得し、2件を返信候補として分類"}],
        decision="social obligation review",
        candidates=["ai-server.agora.read_posts", "ai-server.agora.post"],
        timestamp_ms=1_700_000_000_000,
    )

    loaded = store.get(record.operation_id)
    assert loaded is not None
    assert "AGORA" in loaded.action_summary or "12件" in loaded.result_summary
    assert loaded.result_status == "success"
    assert "自律実行" not in loaded.action_summary
    assert loaded.causal_chain
    assert all("Decision Contextページ" not in str(stage.get("summary") or "") for stage in loaded.causal_chain)
    assert all("Execution completed" not in str(stage.get("summary") or "") for stage in loaded.causal_chain)


def test_non_action_cycle_records_reason(tmp_path) -> None:
    store = OperationStore(data_dir=tmp_path)
    record = store.record_autonomous_cycle(
        tasks=[],
        results=[],
        no_action_reason="ユーザーがゲーム中で緊急性が低いため通知を保留",
        timestamp_ms=1_700_000_000_100,
    )
    assert record.result_status == "non_action"
    assert "行動しなかった" in record.action_summary
    assert "ゲーム中" in record.result_summary


def test_build_causal_chain_omits_placeholder_prose() -> None:
    chain = build_causal_chain(
        OperationRecord(
            action_summary="Chromeでリポジトリを開いた",
            result_summary="最新Commitの変更内容を確認",
            purpose="変更内容の把握",
            decision_reason="成長欲求に基づく調査",
            goal="最新Commitを把握する",
            steps=[{"action": "open", "output_summary": "リポジトリを表示", "status": "ok"}],
            verification={"summary": "Goal達成"},
        )
    )
    joined = " ".join(str(stage.get("summary") or "") for stage in chain)
    assert "Decision Contextページを参照" not in joined
    assert "Execution completed" not in joined
    assert "報告したはず" not in joined
    assert "最新Commit" in joined or "リポジトリ" in joined
