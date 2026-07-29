from __future__ import annotations

from aegis_ai.web.saved_view_manager import SavedViewManager


class _Audit:
    def __init__(self) -> None:
        self.entries = []

    def log_decision(self, **kwargs) -> None:
        self.entries.append(kwargs)


def test_saved_views_are_user_scoped_and_persisted(tmp_path) -> None:
    audit = _Audit()
    manager = SavedViewManager(str(tmp_path), audit)
    created = manager.create_view(
        "user-a",
        {
            "resource": "tasks",
            "name": "承認待ち",
            "query": "重要",
            "filters": {"status": "waiting_approval"},
            "sort": "updated_at",
            "page_size": 25,
        },
    )

    assert manager.list_views("user-a", "tasks")[0]["id"] == created["id"]
    assert manager.list_views("user-b", "tasks") == []

    reloaded = SavedViewManager(str(tmp_path))
    assert reloaded.list_views("user-a", "tasks")[0]["filters"]["status"] == "waiting_approval"
    assert audit.entries[0]["action"] == "saved_view.created"


def test_saved_view_cannot_be_changed_by_another_user(tmp_path) -> None:
    manager = SavedViewManager(str(tmp_path))
    created = manager.create_view("owner", {"resource": "tasks", "name": "My view"})

    assert manager.update_view("other", created["id"], {"name": "stolen"}) is None
    assert manager.delete_view("other", created["id"]) is False
    assert manager.list_views("owner")[0]["name"] == "My view"
