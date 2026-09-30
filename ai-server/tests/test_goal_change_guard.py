"""The goal change stays applied.

AEGIS's goal was narrowed to a **single constraint**: user-information egress. The
constraint itself was **re-scoped 2026-09-30** (owner) — *unpermitted* disclosure is
forbidden, outbound connections are allowed, and disclosure **with the user's
permission** is allowed. Approval, reversibility, policy and reliability-proof were
removed as *constraints*; they survive only as post-hoc annotations (see
``docs/irreversibility-ledger.md``).

Phase 2 deleted the code that enforced them. Phase 5b deleted what still *read* as
a gate: the interpreter branches, the policy-store duplication, and the wire fields
and RPCs in the shared .proto contract. This module pins both.

It also pins the boundary the owner drew, in both directions: the mechanism that
*forces* approval must stay gone, while the ask-the-user surface that AEGIS may
invoke *voluntarily* must keep working.

It is the mirror of ``tests/test_egress_gate.py``: that suite protects the
constraint, this one protects the goal change. Without it, a well-meaning future
change could reintroduce an approval gate and no test would notice — the same
"declared but ineffective" shape, inverted.

Every assertion names the surface that was removed and why it must stay gone.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import io
import tokenize
from functools import cache
from pathlib import Path

import pytest

#: Removed enum members and methods. These identifiers are unambiguous: unlike
#: ``requires_approval`` (a live manifest annotation) or ``approval_required`` (a
#: live risk label), nothing legitimate may reintroduce them.
_REMOVED_IDENTIFIERS: tuple[str, ...] = (
    "ASK_APPROVAL",
    "APPROVAL_NEEDED",
    "WAITING_APPROVAL",
    "NEEDS_APPROVAL",
    "pause_for_approval",
    "resume_after_approval",
    "wait_for_approval",
    "list_waiting_approval",
    "_without_interactive_approval",
    "execute_approved",
)

#: Files that may legitimately still mention a removed identifier — and the exact
#: reason, because a stale rationale here silently widens the blind spot.
#:
#: Only generated protobuf stubs are exempt. They match because a ``reserved``
#: tombstone in the .proto (``reserved "POLICY_DECISION_ASK_APPROVAL";``) is
#: embedded verbatim in the serialized descriptor as a **bytes literal**, and
#: ``_code_and_values`` keeps ordinary string literals on purpose. A tombstone is
#: the opposite of a reintroduction: it instructs the compiler never to reuse that
#: name or number again.
#:
#: That justification is *proven*, not asserted — see
#: ``test_the_generated_stub_exemption_covers_only_tombstones``, which fails if the
#: tombstone disappears (making this exemption dead weight) or if the name ever
#: becomes a live enum member.
#:
#: ``"pb2"`` is sufficient on its own: every file under ``src/generated/aegis/``
#: carries it in its name. The broader ``"generated"`` token that used to sit here
#: was removed on 2026-09-28, so a future non-pb2 module placed under ``generated/``
#: is scanned like any other source.
_EXEMPT_PATH_PARTS: tuple[str, ...] = ("pb2",)

_SRC = Path(__file__).resolve().parents[1] / "src"
_REPO = Path(__file__).resolve().parents[2]

#: Directories that hold vendored or build output rather than project source.
_SKIP_DIRS: frozenset[str] = frozenset({".venv", "node_modules", "__pycache__", "build", ".git", ".aegis-local"})

#: Names that the goal change deleted from the **shared wire contract**, and that
#: no server's copy of that contract may declare as a live member again.
#:
#: ``approval_id`` is deliberately *absent* from this set. The owner's distinction
#: keeps the voluntary ask, and ``AndroidApprovalCommand`` / ``AndroidApprovalDecision``
#: carry that field on purpose. Banning it globally would break the very surface the
#: goal change promised to preserve — the over-deletion failure mode.
_REMOVED_WIRE_NAMES: frozenset[str] = frozenset(
    {
        "ApprovalRequest",
        "ApprovalStatus",
        "ApprovalType",
        "requires_approval",
        "is_approved",
        "was_approved",
        "AUDIT_ACTION_APPROVAL_REQUESTED",
        "AUDIT_ACTION_APPROVAL_GRANTED",
        "AUDIT_ACTION_APPROVAL_REJECTED",
        "POLICY_DECISION_ASK_APPROVAL",
    }
)


def _src_files() -> list[Path]:
    return [
        path
        for path in _SRC.rglob("*.py")
        if "__pycache__" not in path.parts
        and not any(part in str(path) for part in _EXEMPT_PATH_PARTS)
    ]


@cache
def _code_and_values(path: Path) -> str:
    """Return a file's source with docstrings and comments removed.

    The guard must distinguish two things that look identical to a grep:

    * a **docstring or comment** saying "``ASK_APPROVAL`` was removed" — legitimate,
      and the file that documents the goal change should be free to say so;
    * a **string literal or identifier** still *used* as a status, enum member or
      value — a reintroduction, which is what this guard exists to catch.

    So docstrings and comments are stripped, but ordinary string literals are kept.
    (That distinction is not academic: it is how the dead
    ``{"waiting_approval", "wait_for_approval"}`` set in
    ``autonomous/spontaneous_observation.py`` was found.)
    """
    source = path.read_text(encoding="utf-8", errors="replace")

    docstring_lines: set[int] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if not isinstance(
                node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                doc = body[0].value
                docstring_lines.update(
                    range(doc.lineno, (doc.end_lineno or doc.lineno) + 1)
                )

    kept: list[str] = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return source
    for token in tokens:
        if token.type == tokenize.COMMENT:
            continue
        if token.type == tokenize.STRING and token.start[0] in docstring_lines:
            continue
        kept.append(token.string)
    return "\n".join(kept)


# ── The approval subsystem is gone ────────────────────────────────────────────


@pytest.mark.parametrize("module_name", ["aegis_ai.approval", "approval"])
def test_the_approval_package_is_not_importable(module_name: str):
    """The whole approval subsystem was deleted, including its compatibility shim.

    If this fails, something re-added the package — which would restore approval as
    a constraint by the back door.
    """
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


def test_policy_engine_offers_no_approval_decision():
    from policy_engine import PolicyDecision

    members = {member.name for member in PolicyDecision}
    assert members == {"ALLOW", "ALLOW_WITH_AUDIT", "DENY", "UNAVAILABLE"}
    assert not hasattr(PolicyDecision, "ASK_APPROVAL")


def test_policy_engine_has_no_interactive_approval_downgrade():
    """``_without_interactive_approval()`` converted ASK_APPROVAL into an audit entry."""
    from policy_engine import PolicyEngine

    source = inspect.getsource(PolicyEngine)
    assert "_without_interactive_approval" not in source


# ── The tool broker has no approval status ────────────────────────────────────


def test_tool_broker_has_no_approval_status_or_result_field():
    from tool_broker import InvokeStatus, ToolExecutionRequest, ToolExecutionResult

    assert not hasattr(InvokeStatus, "APPROVAL_NEEDED")
    assert not hasattr(ToolExecutionResult, "approval_id")
    assert not hasattr(ToolExecutionRequest, "requires_approval")


# ── Task lifecycle has no approval states ─────────────────────────────────────


def test_task_statuses_have_no_approval_states():
    from aegis_ai.task.execution_engine import TaskFinalState
    from aegis_ai.task.task_manager import TaskStatus
    from aegis_ai.task_plan import StepStatus

    assert not hasattr(TaskStatus, "WAITING_APPROVAL")
    assert not hasattr(StepStatus, "NEEDS_APPROVAL")
    assert not hasattr(StepStatus, "APPROVED")
    assert not hasattr(TaskFinalState, "HAS_NEEDS_APPROVAL")


def test_execution_engine_has_no_pause_resume_surface():
    from aegis_ai.task.execution_engine import TaskExecutionEngine

    for method in ("pause_for_approval", "resume_after_approval", "wait_for_approval"):
        assert not hasattr(TaskExecutionEngine, method), f"{method} came back"


# ── Delegation has no approval outcome ────────────────────────────────────────


def test_delegation_has_no_approval_outcome():
    """Delegation rules now yield auto_allowed / forbidden / no_match only.

    ``approval_required`` was an outcome; it is now only a *risk label*. The module
    may still *document* the retirement — this checks it does not *use* it.
    """
    from aegis_ai.personal_ai import delegation

    code = _code_and_values(Path(inspect.getfile(delegation)))

    assert "approval_required" not in code, (
        "delegation.py still uses 'approval_required' as a decision value"
    )


# ── No plan-level approval gate remains (Phase 5b, 2026-09-28) ────────────────


def test_the_interpreter_no_longer_sets_an_approval_flag():
    """Phase 5b deleted the five branches that set ``approval_needed``.

    They were already inert — no enforcement point read the flag, and
    ``execution_engine`` has no approval branch at all — but they *read* as a
    gate, which is worse than useless: it makes the system look like it stops
    for confirmation when it does not. See ``PHASE5B_RULE_PROPOSAL.md``.
    """
    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

    source = _code_and_values(Path(inspect.getfile(LLMTaskInterpreter)))
    assert "approval_needed" not in source, (
        "LLMTaskInterpreter sets approval_needed again; that flag was retired in Phase 5b"
    )


def test_the_interpreter_does_not_decide_on_delegation_dimensions():
    """The delegation *decision* lives in the policy store, not in the interpreter.

    The prompt still declares the dimension vocabulary, because the LLM has to
    know which values are valid. What must not come back is the interpreter
    turning those values into a decision — encoding them here is exactly how the
    policy came to live in two places and drift apart.
    """
    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter

    source = _code_and_values(Path(inspect.getfile(LLMTaskInterpreter)))
    for accessor in (
        'get("scope")',
        'get("audience")',
        'get("content_sensitivity")',
        'get("reversibility")',
    ):
        assert accessor not in source, (
            f"the interpreter reads {accessor} to make a decision; "
            "ask the delegation store instead"
        )


@pytest.mark.parametrize("category", ["EXTERNAL_SEND", "DEVICE_ACTION", "PAYMENT"])
def test_a_risk_category_alone_never_blocks(category: str):
    """A risk category is an annotation; it must not block a plan.

    ``risk in {forbidden, blocked}`` was deliberately dropped as a deny axis
    (owner decision, 2026-09-28). The only deny left is a disabled capability.
    """
    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
    from aegis_ai.task_plan import PlanStep, RiskCategory, TaskPlan

    plan = TaskPlan(
        steps=[
            PlanStep(
                step_id="s",
                capability_id="pc-server.whatever.do",
                risk_category=getattr(RiskCategory, category),
            )
        ]
    )
    LLMTaskInterpreter()._validate_safety(plan)
    assert not plan.has_blocked_steps(), f"{category} must not block: it is an annotation"


def test_a_disabled_capability_is_still_blocked():
    """The one deny that survived Phase 5b — and it is a deny, not a question."""
    from types import SimpleNamespace

    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
    from aegis_ai.task_plan import PlanStep, TaskPlan

    class _Catalog:
        def resolve(self, _cap_id: str):
            return SimpleNamespace(enabled=False, risk_level="low")

    plan = TaskPlan(steps=[PlanStep(step_id="s", capability_id="pc-server.system.reboot")])
    LLMTaskInterpreter(capability_catalog=_Catalog())._validate_safety(plan)

    assert plan.has_blocked_steps()
    assert any("disabled" in note for note in plan.risk_notes)


def test_delegation_forbidden_blocks_the_plan_without_asking(tmp_path):
    """Phase 5b's only behaviour change: ``forbidden`` is a deny, not a question.

    The verdict must come from the same store ``ToolBroker`` enforces with, so
    the plan-level and execution-level answers cannot disagree.
    """
    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore
    from aegis_ai.task_plan import PlanStep, TaskPlan

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    store.upsert_rule(
        {
            "rule_id": "del_never",
            "capability_pattern": "pc-server.files.delete",
            "decision": "forbidden",
        }
    )

    plan = TaskPlan(steps=[PlanStep(step_id="s", capability_id="pc-server.files.delete")])
    LLMTaskInterpreter(delegation_store=store)._validate_safety(plan)

    assert plan.has_blocked_steps()
    assert any("Delegation policy denies" in note for note in plan.risk_notes)


def test_without_a_delegation_store_the_plan_still_proceeds():
    """An absent store must not become an accidental gate.

    ``None`` means "no policy attached", which is the same outcome as
    "no rule matched" — the plan proceeds.
    """
    from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
    from aegis_ai.task_plan import PlanStep, TaskPlan

    plan = TaskPlan(steps=[PlanStep(step_id="s", capability_id="pc-server.whatever.do")])
    LLMTaskInterpreter()._validate_safety(plan)

    assert not plan.has_blocked_steps()
    assert plan.risk_notes == []


# ── The wire contract carries no approval gate (Phase 5b, 2026-09-28) ─────────
#
# Everything above guards Python *code*. These guard the *contract*: the .proto
# files are shared with the Kotlin and Rust servers, so a removed approval field
# that creeps back into the schema would re-legalise the gate everywhere at once.
# Reading the regenerated stubs is the only way to test what the wire actually
# offers, rather than what a .proto file claims.


def test_common_proto_declares_no_approval_types():
    """``ApprovalStatus`` / ``ApprovalType`` / ``ApprovalRequest`` are gone."""
    from generated.aegis import common_pb2

    for name in ("ApprovalStatus", "ApprovalType", "ApprovalRequest"):
        assert not hasattr(common_pb2, name), f"{name} came back into common.proto"


def test_audit_and_policy_enums_have_no_approval_members():
    """The approval lifecycle is gone from both audit and policy vocabularies."""
    from generated.aegis import common_pb2

    audit = {value.name for value in common_pb2.AuditAction.DESCRIPTOR.values}
    assert not any("APPROVAL" in name for name in audit), audit

    policy = {value.name for value in common_pb2.PolicyDecisionType.DESCRIPTOR.values}
    assert policy == {
        "POLICY_DECISION_UNSPECIFIED",
        "POLICY_DECISION_ALLOW",
        "POLICY_DECISION_DENY",
    }, policy


def test_capability_and_tool_messages_carry_no_approval_fields():
    """The invocation path can no longer *express* "this needs a human first"."""
    from generated.aegis import common_pb2

    assert "requires_approval" not in common_pb2.Capability.DESCRIPTOR.fields_by_name
    for field in ("is_approved", "approval_id"):
        assert field not in common_pb2.ToolInvocationRequest.DESCRIPTOR.fields_by_name
    assert "was_approved" not in common_pb2.ToolInvocationResult.DESCRIPTOR.fields_by_name


def test_ai_server_offers_no_approval_rpcs():
    """The pending-approval queue (request / resolve / list) is not a service."""
    from generated.aegis import ai_server_pb2

    rpcs = set(ai_server_pb2.DESCRIPTOR.services_by_name["AIServer"].methods_by_name)
    assert not any("Approval" in name for name in rpcs), rpcs


def test_chat_response_carries_no_approval_signal():
    """A reply can no longer mean "I am blocked, go resolve the approval"."""
    from generated.aegis import ai_server_pb2

    fields = set(ai_server_pb2.ChatResponse.DESCRIPTOR.fields_by_name)
    assert "approval_needed" not in fields
    assert "approval_id" not in fields


def test_android_keeps_the_voluntary_ask_but_loses_the_unary_rpc():
    """The owner's distinction, pinned at the wire level.

    "Removing approval doesn't mean deleting approval itself — it means deleting
    the mechanism that *forces* you to get approval. But when AEGIS voluntarily
    asks the user for confirmation, the UI must still work."

    So the *queue* RPC must stay gone, and the *streamed ask* must stay present.
    Both halves are asserted, because satisfying only one of them is the failure
    mode that matters: over-deleting breaks the confirmation UI, under-deleting
    restores the gate.
    """
    from generated.aegis import android_server_pb2 as android

    rpcs = set(android.DESCRIPTOR.services_by_name["AndroidServer"].methods_by_name)
    assert "RequestApproval" not in rpcs, "the forced-approval RPC came back"

    # The ask-the-user transport, which AEGIS drives voluntarily.
    assert hasattr(android, "AndroidApprovalCommand")
    assert hasattr(android, "AndroidApprovalDecision")
    assert "approval_request" in android.AndroidServerCommand.DESCRIPTOR.fields_by_name
    assert "approval_decision" in android.AndroidClientMessage.DESCRIPTOR.fields_by_name


def test_a_tier_label_is_not_a_gate():
    """``LEVEL_2_APPROVAL`` survives deliberately — as a name, not a behaviour.

    It is a historical tier label. Renaming it would churn the Rust and Kotlin
    mirrors for no behavioural gain, so it stays and this test records *why*.
    """
    from generated.aegis import common_pb2

    levels = {value.name for value in common_pb2.SafetyLevel.DESCRIPTOR.values}
    assert "LEVEL_2_APPROVAL" in levels


def test_the_generated_stub_exemption_covers_only_tombstones():
    """Why ``pb2`` is exempt from the scan above — proven, not asserted.

    A ``reserved "NAME";`` tombstone is embedded verbatim in the serialized
    descriptor as a bytes literal, which ``_code_and_values`` keeps (it only strips
    docstrings and comments). So ``ASK_APPROVAL`` matches inside
    ``AddSerializedFile(...)``.

    This test makes the exemption self-retiring. If the tombstone ever vanishes the
    first assertion fails and tells you to delete the exemption; if the name ever
    becomes a live enum member the second fails and tells you the gate is back.
    """
    from generated.aegis import common_pb2

    stub = _SRC / "generated" / "aegis" / "common_pb2.py"
    assert "ASK_APPROVAL" in stub.read_text(encoding="utf-8"), (
        "the tombstone is gone from the descriptor — the 'pb2' exemption in "
        "_EXEMPT_PATH_PARTS is now dead weight and should be removed"
    )
    assert not hasattr(common_pb2.PolicyDecisionType, "ASK_APPROVAL")
    assert "POLICY_DECISION_ASK_APPROVAL" not in {
        value.name for value in common_pb2.PolicyDecisionType.DESCRIPTOR.values
    }


# ── Every server's copy of the contract agrees (2026-09-28) ───────────────────
#
# The wire-contract tests above read *this* server's regenerated stubs. That is
# the right thing to assert, but it is not sufficient: the .proto is shared, and
# each consumer keeps its own generated copy. On 2026-09-28 the room server's copy
# was found to still declare ``ApprovalRequest``, ``requires_approval`` and
# ``POLICY_DECISION_ASK_APPROVAL`` — a live reintroduction of the gate, sitting
# behind a green test suite.
#
# The blind spot was the scan list itself: the guard scanned ``ai-server/src`` and
# nothing else, so no server's mirror was ever examined. These tests close that
# gap by reading the **serialized descriptor** out of every ``*_pb2.py`` in the
# repository. That is the same evidence the .proto compiler produces, so it cannot
# be fooled by a stale hand-edited stub, and it needs no ``protoc`` at test time.


def _repo_stub_files() -> list[Path]:
    return [
        path
        for path in _REPO.rglob("*_pb2.py")
        if not any(part in _SKIP_DIRS for part in path.parts)
    ]


def _serialized_descriptors(path: Path) -> list[bytes]:
    """Pull the ``AddSerializedFile(b"...")`` payloads out of a generated stub.

    Reading the bytes rather than the module avoids a real problem: every server
    names its package ``generated.aegis``, so importing more than one of them in a
    single interpreter resolves to whichever is first on ``sys.path``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    found: list[bytes] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "AddSerializedFile"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, bytes)
        ):
            continue
        found.append(node.args[0].value)
    return found


def _declared_names(file_descriptor) -> set[str]:
    """Every name the descriptor declares as *live*: types, fields, enum members."""
    names: set[str] = set()
    for message in file_descriptor.message_type:
        names.add(message.name)
        names.update(field.name for field in message.field)
        names.update(oneof.name for oneof in message.oneof_decl)
        for nested in message.nested_type:
            names.add(nested.name)
            names.update(field.name for field in nested.field)
        for enum in message.enum_type:
            names.add(enum.name)
            names.update(value.name for value in enum.value)
    for enum in file_descriptor.enum_type:
        names.add(enum.name)
        names.update(value.name for value in enum.value)
    return names


def _reserved_names(file_descriptor) -> set[str]:
    """Names the descriptor carries only as tombstones — the opposite of live."""
    names: set[str] = set()
    for message in file_descriptor.message_type:
        names.update(message.reserved_name)
        for nested in message.nested_type:
            names.update(nested.reserved_name)
    for enum in file_descriptor.enum_type:
        names.update(enum.reserved_name)
    return names


def test_no_servers_stub_declares_a_removed_approval_member():
    """The reintroduction that actually happened, caught wherever it happens next.

    Every generated stub in the repo is checked, not just this server's. A stale
    mirror is indistinguishable from a live one to a client that imports it, so a
    mirror is a real reintroduction, not a cosmetic inconsistency.
    """
    from google.protobuf import descriptor_pb2

    offenders: list[str] = []
    descriptors = 0
    for path in _repo_stub_files():
        for payload in _serialized_descriptors(path):
            file_descriptor = descriptor_pb2.FileDescriptorProto.FromString(payload)
            descriptors += 1
            live = _declared_names(file_descriptor) & _REMOVED_WIRE_NAMES
            if live:
                offenders.append(f"{path.relative_to(_REPO)} declares {sorted(live)}")

    assert descriptors > 0, "no serialized descriptors were read — the scan is vacuous"
    assert offenders == [], (
        "the forced approval gate was removed from the shared contract, but these "
        "stub copies still declare it as live:\n  " + "\n  ".join(offenders)
    )


def test_the_cross_server_scan_reads_tombstones_rather_than_absence():
    """Guard the guard: prove the descriptor parser can tell reserved from live.

    If ``_declared_names`` simply returned nothing, the test above would pass
    while checking nothing at all. This asserts the opposite direction on the same
    input: the tombstone for a removed field is present *and* is classified as
    reserved, so absence in the live set means deletion, not a broken parser.
    """
    from google.protobuf import descriptor_pb2

    seen_reserved: set[str] = set()
    for path in _repo_stub_files():
        for payload in _serialized_descriptors(path):
            file_descriptor = descriptor_pb2.FileDescriptorProto.FromString(payload)
            seen_reserved |= _reserved_names(file_descriptor) & _REMOVED_WIRE_NAMES

    assert "requires_approval" in seen_reserved, (
        "no stub carries the requires_approval tombstone — either the tombstone was "
        "dropped (making the .proto unsafe to evolve) or the parser is not reading "
        "reserved names, which would make the scan above vacuous"
    )


def test_every_proto_copy_matches_the_canonical_one():
    """The Kotlin build compiles its own copy of the .proto; drift is invisible."""
    canonical = _REPO / "protos" / "aegis"
    mirror = _REPO / "android-server" / "app" / "src" / "main" / "proto" / "aegis"

    shared = sorted(path.name for path in mirror.glob("*.proto"))
    assert shared, "the Android proto mirror is empty — did the path move?"

    for name in shared:
        source = canonical / name
        assert source.exists(), f"{name} exists only in the Android mirror"
        assert source.read_text(encoding="utf-8") == (mirror / name).read_text(
            encoding="utf-8"
        ), f"{name} differs between protos/aegis/ and the Android mirror"


def test_servers_sharing_a_proto_share_the_generated_stub():
    """Same input, same generator, same output — otherwise one server is stale.

    This is the invariant whose absence let the room server drift: nothing tied
    its copy to the canonical one, and the generation script never wrote to it.
    """
    generated = {
        "ai-server": _SRC / "generated" / "aegis",
        "room-server": _REPO / "room-server" / "src" / "generated" / "aegis",
    }
    shared = ("common_pb2.py", "common_pb2.pyi", "room_server_pb2.py", "room_server_pb2.pyi")

    compared = 0
    for name in shared:
        texts = {}
        for server, directory in generated.items():
            path = directory / name
            assert path.exists(), f"{server} is missing {name}"
            texts[server] = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        assert len(set(texts.values())) == 1, (
            f"{name} differs between servers: "
            f"{[server for server, text in texts.items() if text != texts['ai-server']]} "
            "has drifted from ai-server. Re-run scripts/generate_protos.ps1."
        )
        compared += 1

    assert compared == len(shared)


# ── Nothing in src/ re-declares the removed surfaces ──────────────────────────


@pytest.mark.parametrize("identifier", _REMOVED_IDENTIFIERS)
def test_removed_identifier_does_not_reappear_in_src(identifier: str):
    """Catch a reintroduction anywhere in ``src/``, not just in the type that held it.

    Generated protobuf stubs are exempt, for one narrow and proven reason: they
    embed ``reserved`` tombstones from the .proto files (see
    ``_EXEMPT_PATH_PARTS``). Everything else under ``src/`` is scanned.
    """
    offenders = [
        str(path.relative_to(_SRC))
        for path in _src_files()
        if identifier in _code_and_values(path)
    ]
    assert offenders == [], (
        f"'{identifier}' was removed as part of the goal change but reappeared in: {offenders}"
    )


def test_the_scan_actually_covers_src():
    """Guard the guard: a broken scan would make every test above pass vacuously."""
    files = _src_files()
    assert len(files) > 300, f"only {len(files)} source files were scanned"
    assert any(path.name == "policy_engine.py" for path in files)
