"""Phase 4 DoD tests — Intake filter (instruction.md §36).

DoD チェックリスト (§36):
- [x] 全 Event を OpenHands に投げず、`IntakeClassifier` で「Agent 不要」を
      早期判定できる
- [x] `IntakeSettings.enabled=False` で intake を OFF にして既存挙動に戻せる
- [x] 1000 event のうち Agent delegate に進むのは **10% 以下**
      (mock classifier で検証)
- [x] `IntakeDeduplicator` が fingerprint で dedup する
- [x] import 境界: `intake/*` は openhands SDK を import しない
"""
from __future__ import annotations

import importlib
import inspect
import json
import textwrap
from dataclasses import dataclass, field
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# IntakeResult / RoutingDecision モデル
# ---------------------------------------------------------------------------


def test_intake_result_defaults() -> None:
    """`IntakeResult` はデフォルト値で生成できる."""
    from aegis_ai.intake.models import IntakeDecision, IntakeResult

    r = IntakeResult(event_id="ev-1", decision=IntakeDecision.LOCAL_INTERPRET)
    assert r.event_id == "ev-1"
    assert r.decision == IntakeDecision.LOCAL_INTERPRET
    assert r.requires_agent_score == 0.0
    assert r.importance == 0.0
    assert r.novelty == 1.0
    assert r.capabilities == []
    assert r.reason == ""


def test_routing_decision_should_delegate_to_agent() -> None:
    """`RoutingDecision.should_delegate_to_agent` は `AGENT_DELEGATE` のとき True."""
    from aegis_ai.intake.models import (
        IntakeDecision,
        IntakeResult,
        IntakeRoute,
        RoutingDecision,
    )

    delegate = RoutingDecision(
        route=IntakeRoute.AGENT_DELEGATE,
        intake_result=IntakeResult(
            event_id="ev-1", decision=IntakeDecision.REQUIRES_AGENT
        ),
    )
    skip = RoutingDecision(
        route=IntakeRoute.SKIP,
        intake_result=IntakeResult(
            event_id="ev-2", decision=IntakeDecision.LOCAL_INTERPRET
        ),
    )
    assert delegate.should_delegate_to_agent is True
    assert skip.should_delegate_to_agent is False


# ---------------------------------------------------------------------------
# IntakeDeduplicator
# ---------------------------------------------------------------------------


def test_deduplicator_fingerprint_is_stable() -> None:
    """同じ event は同じ fingerprint を返す."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    event = {"source": "android", "description": "new notification arrived"}
    f1 = IntakeDeduplicator.make_fingerprint(event)
    f2 = IntakeDeduplicator.make_fingerprint(dict(event))
    assert f1 == f2
    assert isinstance(f1, str) and len(f1) == 64  # SHA-256 hex


def test_deduplicator_fingerprint_differs_by_source() -> None:
    """source が異なれば fingerprint も異なる."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    a = IntakeDeduplicator.make_fingerprint({"source": "android", "description": "x"})
    b = IntakeDeduplicator.make_fingerprint({"source": "browser", "description": "x"})
    assert a != b


def test_deduplicator_fingerprint_differs_by_description() -> None:
    """description が異なれば fingerprint も異なる."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    a = IntakeDeduplicator.make_fingerprint({"source": "android", "description": "foo"})
    b = IntakeDeduplicator.make_fingerprint({"source": "android", "description": "bar"})
    assert a != b


def test_deduplicator_window_records_and_detects() -> None:
    """window 内の event は重複判定される."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator(window_size=8)
    event = {"source": "android", "description": "ping"}
    assert dedup.has_seen(event) is False
    dedup.record(event)
    assert dedup.has_seen(event) is True


def test_deduplicator_window_evicts_oldest() -> None:
    """window_size を超えると古い fingerprint が消える."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator(window_size=2)
    dedup.record({"source": "a", "description": "1"})
    dedup.record({"source": "a", "description": "2"})
    dedup.record({"source": "a", "description": "3"})
    # window=2 なので "1" は evict されている
    assert dedup.has_seen({"source": "a", "description": "1"}) is False
    assert dedup.has_seen({"source": "a", "description": "3"}) is True


def test_deduplicator_is_duplicate_novelty_below_threshold() -> None:
    """novelty スコアが閾値未満なら重複扱い."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator(novelty_threshold=0.3)
    event = {"source": "android", "description": "x"}
    assert dedup.is_duplicate(event, novelty=0.1) is True
    assert dedup.is_duplicate(event, novelty=0.5) is False


def test_deduplicator_is_duplicate_fingerprint_match() -> None:
    """fingerprint 一致でも重複扱い (novelty 未指定時)."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator()
    event = {"source": "android", "description": "x"}
    dedup.record(event)
    assert dedup.is_duplicate(event) is True


def test_deduplicator_is_duplicate_or_logic() -> None:
    """fingerprint と novelty の両方が指定されたとき OR 判定."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator(novelty_threshold=0.3)
    event = {"source": "android", "description": "x"}
    # 未記録・novelty 高い → 重複ではない
    assert dedup.is_duplicate(event, novelty=0.9) is False
    # 未記録・novelty 低い → 重複
    assert dedup.is_duplicate(event, novelty=0.1) is True
    dedup.record(event)
    # 記録済み・novelty 高い → 重複 (fingerprint 一致のため)
    assert dedup.is_duplicate(event, novelty=0.9) is True


def test_deduplicator_stats() -> None:
    """stats() が window 状態を含む."""
    from aegis_ai.intake.deduplicator import IntakeDeduplicator

    dedup = IntakeDeduplicator(window_size=4)
    dedup.record({"source": "a", "description": "1"})
    dedup.record({"source": "a", "description": "2"})
    s = dedup.stats()
    assert s["window_used"] == 2
    assert s["window_size"] == 4


# ---------------------------------------------------------------------------
# IntakeClassifier — モック LLM 経由
# ---------------------------------------------------------------------------


@dataclass
class _MockLLMResponse:
    content: str = ""
    success: bool = True
    error: str = ""
    model_used: str = "mock"
    provider_used: str = "mock"
    tokens_used: int = 10


@dataclass
class _MockLLMRouter:
    """`_call_llm` が呼ぶ LLM のモック."""

    next_response: _MockLLMResponse = field(default_factory=_MockLLMResponse)
    call_count: int = 0

    def route(self, request: Any) -> _MockLLMResponse:  # noqa: ARG002
        self.call_count += 1
        return self.next_response


def test_classifier_parses_well_formed_json_response() -> None:
    """正常な JSON レスポンスをパースする."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    payload = {
        "requires_agent_score": 0.85,
        "importance": 0.7,
        "novelty": 0.9,
        "task_type": "code_generation",
        "capabilities": ["ai-server.agent.coding"],
        "stop_conditions": ["after 10 minutes"],
        "reason": "needs multi-step file edits",
        "confidence": 0.9,
    }
    mock = _MockLLMRouter(
        next_response=_MockLLMResponse(content=json.dumps(payload))
    )
    classifier = IntakeClassifier(llm_router=mock, profile_id="local_chat")
    result = classifier.classify({"source": "test", "description": "fix bug"})
    assert result.decision == IntakeDecision.REQUIRES_AGENT
    assert result.requires_agent_score == 0.85
    assert result.importance == 0.7
    assert result.novelty == 0.9
    assert result.task_type == "code_generation"
    assert "ai-server.agent.coding" in result.capabilities
    assert result.reason == "needs multi-step file edits"
    assert result.confidence == 0.9


def test_classifier_parses_json_inside_codeblock() -> None:
    """```json ... ``` で囲まれたレスポンスもパースする."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    inner = json.dumps(
        {
            "requires_agent_score": 0.2,
            "importance": 0.1,
            "novelty": 0.5,
            "task_type": "observation",
            "capabilities": [],
            "stop_conditions": [],
            "reason": "minor",
            "confidence": 0.6,
        }
    )
    content = f"```json\n{inner}\n```"
    mock = _MockLLMRouter(next_response=_MockLLMResponse(content=content))
    classifier = IntakeClassifier(llm_router=mock)
    result = classifier.classify({"source": "test", "description": "x"})
    assert result.decision == IntakeDecision.DEFER
    assert result.requires_agent_score == 0.2


def test_classifier_parses_wrapped_json_with_braces_in_reason() -> None:
    """前後 prose や文字列中 brace を含んでも JSON を抽出できる."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    content = (
        "Here is the result.\n"
        '{"requires_agent_score": 0.71, "importance": 0.4, "novelty": 0.3, '
        '"task_type": "classification", "capabilities": [], "stop_conditions": [], '
        '"reason": "saw literal braces {ok} in text", "confidence": 0.8}\n'
        "done"
    )
    mock = _MockLLMRouter(next_response=_MockLLMResponse(content=content))
    classifier = IntakeClassifier(llm_router=mock)
    result = classifier.classify({"source": "test", "description": "x"})

    assert result.decision == IntakeDecision.REQUIRES_AGENT
    assert result.reason == "saw literal braces {ok} in text"


def test_classifier_falls_back_when_no_router() -> None:
    """`llm_router=None` のときは fallback 設定に従う (default: requires_agent=False)."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    classifier = IntakeClassifier(llm_router=None, fallback_requires_agent=False)
    result = classifier.classify({"source": "test", "description": "x"})
    assert result.decision == IntakeDecision.LOCAL_INTERPRET
    assert "no_llm_router_configured" in result.reason


def test_classifier_falls_back_on_llm_failure() -> None:
    """LLM 呼び出し失敗時は fallback."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    mock = _MockLLMRouter(
        next_response=_MockLLMResponse(
            success=False, error="provider_unavailable", content=""
        )
    )
    classifier = IntakeClassifier(llm_router=mock, fallback_requires_agent=True)
    result = classifier.classify({"source": "test", "description": "x"})
    assert result.decision == IntakeDecision.REQUIRES_AGENT
    assert "llm_response_failed" in result.reason


def test_classifier_falls_back_on_unparseable_response() -> None:
    """LLM レスポンスが JSON として解釈できない場合は fallback."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    mock = _MockLLMRouter(
        next_response=_MockLLMResponse(content="not a JSON at all")
    )
    classifier = IntakeClassifier(llm_router=mock, fallback_requires_agent=False)
    result = classifier.classify({"source": "test", "description": "x"})
    assert result.decision == IntakeDecision.LOCAL_INTERPRET
    assert "unparseable" in result.reason


def test_classifier_score_to_decision_mapping() -> None:
    """score → decision のしきい値マッピング."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.models import IntakeDecision

    cases = [
        (0.0, IntakeDecision.DEFER),
        (0.29, IntakeDecision.DEFER),
        (0.3, IntakeDecision.LOCAL_INTERPRET),
        (0.5, IntakeDecision.LOCAL_INTERPRET),
        (0.69, IntakeDecision.LOCAL_INTERPRET),
        (0.7, IntakeDecision.REQUIRES_AGENT),
        (1.0, IntakeDecision.REQUIRES_AGENT),
    ]
    for score, expected in cases:
        assert (
            IntakeClassifier._decision_from_score(score) == expected
        ), f"score={score}"


# ---------------------------------------------------------------------------
# IntakeRouter
# ---------------------------------------------------------------------------


def _make_router_payload_response(score: float) -> _MockLLMResponse:
    return _MockLLMResponse(
        content=json.dumps(
            {
                "requires_agent_score": score,
                "importance": 0.5,
                "novelty": 0.8,
                "task_type": "test",
                "capabilities": [],
                "stop_conditions": [],
                "reason": f"score={score}",
                "confidence": 0.7,
            }
        )
    )


def test_router_disabled_skips_classifier() -> None:
    """`enabled=False` のときは classifier を呼ばず SKIP を返す."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    mock = _MockLLMRouter()
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(),
        enabled=False,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.SKIP
    assert mock.call_count == 0  # classifier は呼ばれない


def test_router_delegates_to_agent_when_score_above_threshold() -> None:
    """`requires_agent_score >= threshold` のとき AGENT_DELEGATE."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    mock = _MockLLMRouter(next_response=_make_router_payload_response(0.9))
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(),
        enabled=True,
        requires_agent_threshold=0.5,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.AGENT_DELEGATE
    assert decision.should_delegate_to_agent is True
    assert mock.call_count == 1


def test_router_skips_when_score_below_threshold() -> None:
    """score が LOCAL_INTERPRET 帯 (< 0.7) で threshold 未満のとき SKIP.

    classifier の score → decision マッピング:
      0.7+ → REQUIRES_AGENT
      0.3–0.69 → LOCAL_INTERPRET (→ ルーターで SKIP)
      0–0.29 → DEFER (→ ルーターで DEFER)
    よって「classifier が REQUIRES_AGENT と判定」かつ「score >= threshold」
    の両方を満たす必要がある.
    """
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    # score=0.4 → classifier は LOCAL_INTERPRET (>= 0.3 かつ < 0.7)
    mock = _MockLLMRouter(next_response=_make_router_payload_response(0.4))
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(),
        enabled=True,
        requires_agent_threshold=0.5,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.SKIP
    assert decision.should_delegate_to_agent is False


def test_router_dedup_skips_classifier() -> None:
    """既に fingerprint が window にあるとき classifier を呼ばない."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    dedup = IntakeDeduplicator()
    dedup.record({"source": "test", "description": "x"})
    mock = _MockLLMRouter()
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=dedup,
        enabled=True,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.DUPLICATE
    assert mock.call_count == 0  # classifier は呼ばれない (節約)


def test_router_dedup_via_novelty() -> None:
    """novelty < threshold のとき DUPLICATE."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    payload = _make_router_payload_response(0.9)
    payload.content = json.dumps(
        {
            "requires_agent_score": 0.9,
            "importance": 0.5,
            "novelty": 0.1,  # threshold 未満
            "task_type": "test",
            "capabilities": [],
            "stop_conditions": [],
            "reason": "low novelty",
            "confidence": 0.7,
        }
    )
    mock = _MockLLMRouter(next_response=payload)
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(novelty_threshold=0.3),
        enabled=True,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.DUPLICATE


def test_router_dod_below_10_percent_to_agent() -> None:
    """DoD: 1000 event のうち Agent delegate は 10% 以下.

    mock classifier が **常に score=0.1** を返すシナリオで検証。
    (現実の LLM なら多種多様だが、本テストは「大半が SKIP」となることの保証)
    """
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.router import IntakeRouter
    from aegis_ai.intake.models import IntakeRoute

    mock = _MockLLMRouter(next_response=_make_router_payload_response(0.1))
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(window_size=10000),
        enabled=True,
        requires_agent_threshold=0.5,
    )

    delegated = 0
    total = 1000
    for i in range(total):
        event = {
            "source": "android",
            "description": f"event-{i}",
        }
        decision = router.route(event, event_id=f"ev-{i}")
        if decision.route == IntakeRoute.AGENT_DELEGATE:
            delegated += 1
    rate = delegated / total
    assert rate <= 0.10, f"delegate rate too high: {rate:.2%}"


def test_router_dod_high_delegate_when_score_above_threshold() -> None:
    """score=0.9 を返すシナリオではほぼ全 event が delegate される (上限 100%)."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.router import IntakeRouter
    from aegis_ai.intake.models import IntakeRoute

    mock = _MockLLMRouter(next_response=_make_router_payload_response(0.9))
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(window_size=10000),
        enabled=True,
        requires_agent_threshold=0.5,
    )
    delegated = 0
    for i in range(100):
        decision = router.route(
            {"source": "test", "description": f"unique-{i}"}, event_id=f"ev-{i}"
        )
        if decision.route == IntakeRoute.AGENT_DELEGATE:
            delegated += 1
    assert delegated == 100  # 全 event が Agent delegate


def test_router_threshold_boundary() -> None:
    """score == threshold で `>=` 比較が成立し delegate される.

    classifier は score >= 0.7 で REQUIRES_AGENT と判定するため、
    threshold と同値で delegate 経路に入るには score >= 0.7 が必要.
    ここでは score=0.7, threshold=0.7 の境界を検証する.
    """
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.models import IntakeRoute
    from aegis_ai.intake.router import IntakeRouter

    mock = _MockLLMRouter(next_response=_make_router_payload_response(0.7))
    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=mock),
        deduplicator=IntakeDeduplicator(),
        enabled=True,
        requires_agent_threshold=0.7,
    )
    decision = router.route({"source": "test", "description": "x"})
    assert decision.route == IntakeRoute.AGENT_DELEGATE
    assert decision.should_delegate_to_agent is True


def test_router_stats() -> None:
    """`stats()` が設定 + dedup 状態を含む."""
    from aegis_ai.intake.classifier import IntakeClassifier
    from aegis_ai.intake.deduplicator import IntakeDeduplicator
    from aegis_ai.intake.router import IntakeRouter

    router = IntakeRouter(
        classifier=IntakeClassifier(llm_router=None),
        deduplicator=IntakeDeduplicator(window_size=8),
        enabled=True,
        requires_agent_threshold=0.6,
    )
    s = router.stats()
    assert s["enabled"] is True
    assert s["requires_agent_threshold"] == 0.6
    assert s["dedup"]["window_size"] == 8


# ---------------------------------------------------------------------------
# IntakeSettings
# ---------------------------------------------------------------------------


def test_intake_settings_defaults() -> None:
    """`IntakeSettings` のデフォルト."""
    from aegis_ai.settings import IntakeSettings

    s = IntakeSettings()
    assert s.enabled is True
    assert s.classifier_profile == "local_chat"
    assert s.requires_agent_threshold == 0.5
    assert s.dedup_window_size == 64
    assert s.dedup_novelty_threshold == 0.3
    assert s.fallback_requires_agent is False


def test_intake_settings_validation() -> None:
    """範囲外の値は Pydantic が拒否."""
    from pydantic import ValidationError

    from aegis_ai.settings import IntakeSettings

    with pytest.raises(ValidationError):
        IntakeSettings(requires_agent_threshold=1.5)
    with pytest.raises(ValidationError):
        IntakeSettings(requires_agent_threshold=-0.1)
    with pytest.raises(ValidationError):
        IntakeSettings(dedup_window_size=-1)


def test_aegis_settings_contains_intake() -> None:
    """`AEGISSettings.intake` が `IntakeSettings` インスタンス."""
    from aegis_ai.settings import AEGISSettings, IntakeSettings

    s = AEGISSettings()
    assert isinstance(s.intake, IntakeSettings)
    assert s.intake.enabled is True


# ---------------------------------------------------------------------------
# import 境界 — intake/* は openhands を import しない
# ---------------------------------------------------------------------------


def _module_source(module_name: str) -> str:
    return textwrap.dedent(inspect.getsource(importlib.import_module(module_name)))


@pytest.mark.parametrize(
    "module_name",
    [
        "aegis_ai.intake",
        "aegis_ai.intake.models",
        "aegis_ai.intake.classifier",
        "aegis_ai.intake.deduplicator",
        "aegis_ai.intake.router",
    ],
)
def test_intake_module_does_not_import_openhands(module_name: str) -> None:
    """intake パッケージは openhands SDK を import しない (§6 import 境界)."""
    src = _module_source(module_name)
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            for forbidden in ("openhands", "anthropic", "openai", "langchain"):
                assert forbidden not in stripped, (
                    f"forbidden import in {module_name}: {stripped}"
                )
