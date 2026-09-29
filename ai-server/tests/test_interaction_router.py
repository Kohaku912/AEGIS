from __future__ import annotations

from aegis_ai.interaction.message import Message, Response
from aegis_ai.interaction.router import InteractionRouter


def test_handle_support_feedback_requires_structured_metadata() -> None:
    router = InteractionRouter()

    response = router._handle_support_feedback(
        Message(text="thanks, looks good"),
        response=Response(),
    )

    assert "metadata.feedback_decision" in response.text


def test_handle_support_feedback_accepts_patch() -> None:
    router = InteractionRouter()

    response = router._handle_support_feedback(
        Message(text="", metadata={"feedback_patch": {"detail_level": "brief"}}),
        response=Response(),
    )

    assert "structured feedback patch" in response.text
    assert response.metadata["feedback_patch"] == {"detail_level": "brief"}
