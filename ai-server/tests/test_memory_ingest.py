from __future__ import annotations

from aegis_ai.integrations.agora.agora_types import AgoraPost
from aegis_ai.llm.memory_context import build_shared_memory_context
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.memory.memory_ingest import save_memory_payload, sync_agora_posts_to_memory
from aegis_ai.memory.person_memory import PersonMemory


def test_sync_agora_posts_to_memory_records_people_and_context(tmp_path) -> None:
    data_dir = tmp_path / "data"
    posts = [
        AgoraPost.from_dict(
            {
                "id": 101,
                "thread_id": 1,
                "author": {"id": 11, "name": "Alice"},
                "body": "Hi AEGIS, please remember that I prefer short updates.",
                "mentions": [{"id": 99, "name": "AEGIS"}],
                "reply_to": None,
                "created_at": "2026-06-16T10:00:00Z",
            }
        ),
        AgoraPost.from_dict(
            {
                "id": 102,
                "thread_id": 1,
                "author": {"id": 12, "name": "Bob"},
                "body": "Alice asked for short updates too.",
                "mentions": [{"id": 11, "name": "Alice"}],
                "reply_to": 101,
                "created_at": "2026-06-16T10:01:00Z",
            }
        ),
    ]

    result = sync_agora_posts_to_memory(posts=posts, data_dir=str(data_dir))

    assert result.ok is True
    assert result.posts[0]["author"]["name"] == "Alice"
    assert any(mention["name"] == "Alice" for mention in result.mentions)
    assert "AGORA: 2 new post(s)." in result.result

    person_memory = PersonMemory(path=str(data_dir / "memory" / "persons.jsonl"))
    names = {person.name for person in person_memory.get_all()}
    assert {"Alice", "Bob"}.issubset(names)

    context = build_shared_memory_context(query="Alice", data_dir=str(data_dir), profile="decision")
    assert "Known people:" in context.text
    assert "Alice" in context.text


def test_memory_save_routes_person_and_general_memory(tmp_path) -> None:
    data_dir = tmp_path / "data"

    person_result = save_memory_payload(
        {"content": "Alice prefers concise updates.", "entity": "Alice", "type": "person"},
        data_dir=str(data_dir),
    )
    assert person_result.ok is True
    assert person_result.saved_to == ["person_memory"]
    assert person_result.entity == "Alice"

    person_memory = PersonMemory(path=str(data_dir / "memory" / "persons.jsonl"))
    assert any(person.name == "Alice" for person in person_memory.get_all())

    general_result = save_memory_payload(
        {"content": "Alice prefers concise updates.", "type": "conversation"},
        data_dir=str(data_dir),
    )
    assert general_result.ok is True
    assert general_result.saved_to == ["advanced_memory"]

    advanced_memory = AdvancedMemory(data_dir=str(data_dir / "memory"))
    assert advanced_memory.get_stats()["conversations"] >= 1
