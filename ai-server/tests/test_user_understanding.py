from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.user_model import UserModelStore
from aegis_ai.user_understanding import UserUnderstandingService


class _UserStateManager:
    def get_current_user_state(self):
        return {
            "attention": {"device": "pc", "label": "pc_active", "confidence": 0.8},
            "activity": {"label": "coding", "confidence": 0.7},
            "updated_at_ms": 1234,
        }


class _CommitmentManager:
    def list_commitments(self, status: str | None = None):
        items = [
            {
                "commitment_id": "commit-1",
                "title": "Send status report",
                "status": "open",
                "next_action": "Draft the reply",
                "due_at_ms": 1,
                "updated_at": 2,
            }
        ]
        if status:
            return [item for item in items if item["status"] == status]
        return items


class _DelegationPolicy:
    def get_summary(self):
        return {"rules": [{"rule_id": "rule-1", "decision": "auto_allowed"}], "counts": {"auto_allowed": 1}}


class _PersonMemory:
    def list_all(self):
        return [SimpleNamespace(to_dict=lambda: {"name": "Kohaku", "relationship": "master", "last_seen_ms": 10})]


class _PersonalDataCore:
    def recent_facts(self, limit: int = 20):
        return [{"id": "fact-1", "statement": "User is working on AEGIS UI.", "confidence": 0.9, "timestamp_ms": 11}]


class _TaskManager:
    def list_tasks(self, limit: int = 100):
        return [{"task_id": "task-1", "title": "Stabilize repair flow", "status": "failed", "updated_at": 12}]


class _RepairManager:
    def list_history(self, limit: int = 50):
        return [{"repair_id": "repair-1", "category": "tool_failed", "error": "Something broke", "final_result": "needs_followup", "timestamp": 13}]


def test_user_understanding_builds_snapshot(tmp_path) -> None:
    model_store = UserModelStore(data_dir=str(tmp_path / "user_model"))
    model_store.update(
        {
            "preferred_language": "ja",
            "preferred_tone": "polite",
            "detail_level": "detailed",
            "autonomy_level": "high",
            "long_term_goals": [{"title": "Reduce admin burden"}],
        }
    )
    service = UserUnderstandingService(
        data_dir=str(tmp_path / "user_understanding"),
        user_model_store=model_store,
        user_state_manager=_UserStateManager(),
        commitment_manager=_CommitmentManager(),
        delegation_policy=_DelegationPolicy(),
        person_memory=_PersonMemory(),
        personal_data_core=_PersonalDataCore(),
        task_manager=_TaskManager(),
        repair_manager=_RepairManager(),
    )

    snapshot = service.build_snapshot("status report")
    data = snapshot.to_dict()

    assert data["identity_profile"]["current_activity"] == "coding"
    assert data["likely_next_actions"][0]["title"] in {"Respond to current user intent", "Draft the reply"}
    assert data["predicted_deficits"]
    assert data["delegated_authority_state"]["blocked_categories"] == ["payment"]
    assert data["self_improvement_queue"]


def test_record_user_feedback_accepts_structured_patch(tmp_path) -> None:
    store = UserModelStore(data_dir=str(tmp_path / "user_model"))

    store.record_user_feedback('{"preference_patch":{"detail_level":"brief","notification_preference":"minimal"}}')

    model = store.get()
    assert model.detail_level.value == "brief"
    assert model.notification_preference.value == "minimal"


def test_record_user_feedback_does_not_keyword_patch_free_text(tmp_path) -> None:
    store = UserModelStore(data_dir=str(tmp_path / "user_model"))

    store.record_user_feedback("もっと自動でやって")

    assert store.get().autonomy_level.value == "medium"
