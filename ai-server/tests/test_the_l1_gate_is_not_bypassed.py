"""The L1 gate must never be silently bypassed.

``call_llm_with_tools`` consults the L1 gate by calling
``llm.generate(..., profile="l1_default")``. **Only ``LLMGateway.generate`` accepts that
keyword** — the providers (``MockLLMProvider``, ``openai_provider``,
``typesafe_provider``) do not, and a test double that omits ``generate`` altogether does
not either. When the object bound as ``llm`` cannot satisfy the call, the gate raises,
the exception is swallowed (the caller reads ``None`` as "no decision") and **the gate
never runs** — while the test stays green.

Measured 2026-10-04. ``ai-server/data/audit.db`` held 706 ``llm.first_stage.*.failed``
rows whose ``error`` was a fixed string, so two weeks of these bypasses were invisible.
Once the record carried the cause, two instances appeared within the hour:

  ``TypeError: MockLLMProvider.generate() got an unexpected keyword argument 'profile'``
  ``AttributeError: 'NativeToolLLM' object has no attribute 'generate'``

``NativeToolLLM`` exists only at ``tests/test_chat_tools.py`` and is driven by
``test_call_llm_with_tools_uses_native_tool_calling_for_multi_step_sequences``: the gate
raised, the double's missing method was never noticed, and the test still passed. It now
defines ``generate``, so that test exercises the gate for real.

The pin is **discovered, not hand-listed**: it reads the gate's call keywords from the
source, checks the object production binds, and resolves every ``call_llm_with_tools``
call site across ``src/`` and ``tests/`` — so the *next* incomplete double fails here
instead of writing a bypass row into the sink.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from aegis_ai.llm.gateway import LLMGateway

_AI_SERVER = Path(__file__).resolve().parents[1]
_ROOTS = (_AI_SERVER / "src", _AI_SERVER / "tests")
_CHAT_TOOLS = _AI_SERVER / "src" / "aegis_ai" / "web" / "chat_tools.py"

# The keyword arguments the L1 gate passes. Test 1 reads the real call and compares by
# **equality**, so adding or removing one fails here rather than widening the contract
# silently; test 5 keeps ``profile`` — the load-bearing one — from being quietly dropped
# from this set to make test 1 pass.
_GATE_KWARGS = frozenset(
    {"prompt", "system_prompt", "max_tokens", "context_meta", "json_mode", "profile"}
)

_GATEWAY_ACCEPTS = frozenset(inspect.signature(LLMGateway.generate).parameters)


def _gate_call_sites() -> list[tuple[int, frozenset[str]]]:
    """Every ``<obj>.generate(...)`` in ``chat_tools.py`` that carries ``profile=``."""
    tree = ast.parse(_CHAT_TOOLS.read_text(encoding="utf-8"))
    sites: list[tuple[int, frozenset[str]]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "generate"
        ):
            kwargs = frozenset(k.arg for k in node.keywords if k.arg)
            if "profile" in kwargs:
                sites.append((node.lineno, kwargs))
    return sorted(sites)


def _classes_with_generate(module: ast.Module) -> dict[str, frozenset[str] | None]:
    """Map each top-level class to its ``generate`` parameter set (``None`` = no method)."""
    found: dict[str, frozenset[str] | None] = {}
    for node in module.body:
        if not isinstance(node, ast.ClassDef):
            continue
        params: frozenset[str] | None = None
        for member in node.body:
            if isinstance(member, ast.FunctionDef) and member.name == "generate":
                args = member.args
                names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
                params = frozenset(names)
                break
        found[node.name] = params
    return found


def _walk_shallow(node: ast.AST):
    """Walk ``node`` without descending into nested functions/classes/lambdas."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        yield child
        yield from _walk_shallow(child)


def _assigned_class(func: ast.AST, name: str) -> str | None:
    """Resolve ``name = SomeClass(...)`` inside ``func`` (not its nested functions)."""
    for node in _walk_shallow(func):
        value: ast.expr | None = None
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            value, targets = node.value, list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            value, targets = node.value, [node.target]
        if value is None or not isinstance(value, ast.Call):
            continue
        if not isinstance(value.func, ast.Name):
            continue
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            return value.func.id
    return None


# Every function that receives the chat ``llm`` and consults the L1 gate. Production does
# not call ``call_llm_with_tools`` directly: ``chat_service`` / ``routes/chat`` pass the
# gateway to ``_call_llm_with_runtime``, which forwards it. The value is the positional
# index of the ``llm`` argument in that function's signature.
_TARGETS = {"call_llm_with_tools": 0, "_call_llm_with_runtime": 1}


class _SiteCollector(ast.NodeVisitor):
    """Collect the gate's call sites together with their nearest enclosing def."""

    def __init__(self) -> None:
        self.stack: list[ast.AST] = []
        self.found: list[tuple[ast.AST, ast.Call, int]] = []

    def _visit_func(self, node: ast.AST) -> None:
        self.stack.append(node)
        self.generic_visit(node)
        self.stack.pop()

    visit_FunctionDef = _visit_func
    visit_AsyncFunctionDef = _visit_func

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        name = (
            func.attr
            if isinstance(func, ast.Attribute)
            else (func.id if isinstance(func, ast.Name) else None)
        )
        if name in _TARGETS and self.stack:
            self.found.append((self.stack[-1], node, _TARGETS[name]))
        self.generic_visit(node)


def _resolve_sites() -> tuple[list[tuple[str, str, frozenset[str] | None]], list[tuple[str, str]]]:
    """Resolve every ``call_llm_with_tools`` site to what its ``llm`` accepts.

    Returns ``(checked, unresolved)`` where ``checked`` entries are
    ``(where, kind, accepted_params)`` with ``kind`` in ``{"gateway", "double"}``.
    Pass-through sites (the ``llm`` argument is a parameter of the enclosing function —
    ``chat_tools``' own recursion and ``dashboard_legacy._call_llm_with_runtime``) are
    skipped: the binding is resolved where the value is actually created.
    """
    checked: list[tuple[str, str, frozenset[str] | None]] = []
    unresolved: list[tuple[str, str]] = []
    for root in _ROOTS:
        for path in sorted(root.rglob("*.py")):
            try:
                module = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:  # pragma: no cover - a broken file fails elsewhere
                continue
            classes = _classes_with_generate(module)
            rel = path.relative_to(_AI_SERVER).as_posix()
            collector = _SiteCollector()
            collector.visit(module)
            for enclosing, call, position in collector.found:
                where = f"{rel}:{call.lineno}"
                keywords = {k.arg: k.value for k in call.keywords}
                expr = keywords.get("llm")
                if expr is None and len(call.args) > position:
                    expr = call.args[position]
                if expr is None:
                    unresolved.append((where, "no llm argument"))
                    continue
                params = {
                    a.arg
                    for a in enclosing.args.posonlyargs + enclosing.args.args + enclosing.args.kwonlyargs
                }
                if isinstance(expr, ast.Attribute):
                    if expr.attr != "llm_gateway":
                        unresolved.append((where, f"llm={ast.unparse(expr)} is not a gateway binding"))
                        continue
                    checked.append((where, "gateway", _GATEWAY_ACCEPTS))
                    continue
                if isinstance(expr, ast.Name):
                    if expr.id in params:
                        continue  # pass-through
                    cls = _assigned_class(enclosing, expr.id)
                    if cls is None or cls not in classes:
                        unresolved.append((where, f"llm={expr.id} does not resolve to a class"))
                        continue
                    checked.append((where, "double", classes[cls]))
                    continue
                unresolved.append((where, f"llm={ast.unparse(expr)} has an unrecognised shape"))
    return checked, unresolved


def test_the_gate_passes_exactly_the_recorded_keywords() -> None:
    sites = _gate_call_sites()
    assert len(sites) == 2, f"expected the two gate calls (tool + satisfaction), found {sites}"
    for lineno, kwargs in sites:
        assert kwargs == _GATE_KWARGS, f"chat_tools.py:{lineno} passes {sorted(kwargs)}"


def test_the_production_llm_accepts_every_gate_keyword() -> None:
    missing = _GATE_KWARGS - _GATEWAY_ACCEPTS
    assert not missing, f"LLMGateway.generate lacks {sorted(missing)}"


def test_every_call_site_binds_an_llm_that_accepts_the_gate_keywords() -> None:
    checked, unresolved = _resolve_sites()
    assert unresolved == [], f"unresolved call sites: {unresolved}"
    problems: list[str] = []
    for where, _kind, accepted in checked:
        if accepted is None:
            problems.append(f"{where}: the bound llm has no generate()")
            continue
        missing = _GATE_KWARGS - accepted
        if missing:
            problems.append(f"{where}: generate() lacks {sorted(missing)}")
    assert problems == [], "the L1 gate would be silently bypassed at: " + "; ".join(problems)


def test_the_scan_is_not_vacuous() -> None:
    checked, unresolved = _resolve_sites()
    assert unresolved == [], f"unresolved call sites: {unresolved}"
    kinds = [kind for _where, kind, _accepted in checked]
    assert kinds.count("gateway") >= 2, f"expected the production binders, found {checked}"
    assert kinds.count("double") >= 3, f"expected the test doubles, found {checked}"


def test_the_recorded_contract_keeps_the_load_bearing_keyword() -> None:
    # Without this, dropping ``profile`` from BOTH the call and _GATE_KWARGS would keep
    # test 1 green while the contract that makes the gate work had been deleted.
    assert "profile" in _GATE_KWARGS


# ---------------------------------------------------------------------------------------
# The same call shape — ``.generate(..., profile=...)`` — appears at 9 sites in ``src/``
# (measured 2026-10-04). Sweeping them shows the gate was the *only* site that swallowed a
# mismatch: the other guarded sites either fall back on ``TypeError`` or record the cause.
# Classifying them here means a new site cannot be added unclassified, and a new
# *unguarded* site cannot be added at all.
# ---------------------------------------------------------------------------------------
_PROFILE_SITES = {
    ("src/aegis_ai/analysis/prompt_usage.py", "_judge_record", "self._llm"):
        "TypeError -> retry without profile",
    ("src/aegis_ai/burden/metric.py", "assess", "self._llm"):
        "records the cause and continues",
    ("src/aegis_ai/desire/fulfillment.py", "_evaluate_with_llm._call", "llm_provider"):
        "TypeError -> retry without profile",
    ("src/aegis_ai/llm/gateway.py", "generate_json", "self"):
        "the gateway itself, which accepts profile",
    ("src/aegis_ai/llm/gateway.py", "request", "self"):
        "the gateway itself, which accepts profile",
    ("src/aegis_ai/social/manager.py", "_generate_json", "self._llm"):
        "unguarded on purpose: production binds the gateway, so a mismatch raises loudly",
    ("src/aegis_ai/temporal/activities/llm_activity.py", "_llm_generate", "gateway"):
        "returns a failure dict",
    ("src/aegis_ai/web/chat_tools.py", "_llm_wants_tools", "llm"):
        "the gate - the swallow this whole pin exists for",
    ("src/aegis_ai/web/chat_tools.py", "_llm_response_satisfies_without_tools", "llm"):
        "the gate",
}

# Unguarded sites that are nevertheless safe, each with its reason. A site that is neither
# guarded nor listed here can skip its work without anyone noticing — which is exactly how
# the 706 opaque ``llm.first_stage.*.failed`` rows were produced.
_UNGUARDED_AND_SAFE = {
    ("src/aegis_ai/llm/gateway.py", "generate_json", "self"),
    ("src/aegis_ai/llm/gateway.py", "request", "self"),
    ("src/aegis_ai/social/manager.py", "_generate_json", "self._llm"),
}

_CATCHES = ("TypeError", "Exception", "BaseException", "*")


def _profile_call_sites() -> dict[tuple[str, str, str], tuple[tuple[str, ...], bool]]:
    """Every ``.generate(..., profile=...)`` in ``src/`` -> (handler types, guarded)."""
    found: dict[tuple[str, str, str], tuple[tuple[str, ...], bool]] = {}

    def walk(node: ast.AST, fname: str, rel: str, handlers: tuple[tuple[str, ...], ...]) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fname = f"{fname}.{node.name}" if fname else node.name
        if isinstance(node, ast.Try):
            types = tuple(sorted(ast.unparse(h.type) if h.type else "*" for h in node.handlers))
            for child in node.body:
                walk(child, fname, rel, handlers + (types,))
            for branch in [h.body for h in node.handlers] + [node.orelse, node.finalbody]:
                for child in branch:
                    walk(child, fname, rel, handlers)
            return
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "generate"
            and any(k.arg == "profile" for k in node.keywords)
        ):
            flat = tuple(t for group in handlers for t in group)
            guarded = any(any(c in t for c in _CATCHES) for t in flat)
            found[(rel, fname, ast.unparse(node.func.value))] = (flat, guarded)
        for child in ast.iter_child_nodes(node):
            walk(child, fname, rel, handlers)

    for path in sorted((_AI_SERVER / "src").rglob("*.py")):
        try:
            module = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - a broken file fails elsewhere
            continue
        walk(module, "", path.relative_to(_AI_SERVER).as_posix(), ())
    return found


def test_every_profile_carrying_generate_site_is_classified() -> None:
    found = _profile_call_sites()
    assert set(found) == set(_PROFILE_SITES), (
        f"unclassified: {sorted(set(found) - set(_PROFILE_SITES))}; "
        f"stale (no longer present): {sorted(set(_PROFILE_SITES) - set(found))}"
    )


def test_no_unguarded_profile_site_can_skip_its_work_silently() -> None:
    found = _profile_call_sites()
    unguarded = {site for site, (_types, guarded) in found.items() if not guarded}
    assert unguarded == _UNGUARDED_AND_SAFE, (
        f"new unguarded site(s): {sorted(unguarded - _UNGUARDED_AND_SAFE)}; "
        f"no longer unguarded: {sorted(_UNGUARDED_AND_SAFE - unguarded)}"
    )


def test_the_profile_site_scan_is_not_vacuous() -> None:
    found = _profile_call_sites()
    assert len(found) >= 9, f"expected the 9 measured sites, found {len(found)}"
    assert any(guarded for _types, guarded in found.values()), "no guarded site found"
    assert any(not guarded for _types, guarded in found.values()), "no unguarded site found"
