"""Pytest plugin that deliberately breaks the egress gate.

Used by ``verify_egress_tests_catch_regression.py`` to answer the question a
regression suite can never answer about itself: *if the constraint were broken,
would these tests notice?*

Load it explicitly::

    pytest -p mutation_egress_allow_all tests/test_egress_gate.py

It forces ``EgressGate._evaluate`` — the single place every decision flows through —
to return ALLOW. The egress suite must then fail. If it still passes, the suite is
decorative.

No source file is modified: the patch lives in this process only, so the check is
safe to run repeatedly and cannot leave the tree dirty.
"""

from __future__ import annotations


def pytest_configure(config) -> None:
    from aegis_ai.egress import gate as gate_module

    if not hasattr(gate_module.EgressGate, "_evaluate"):
        raise RuntimeError(
            "mutation plugin: EgressGate._evaluate no longer exists, so the mutation "
            "would silently do nothing. Update this plugin alongside the gate."
        )

    allowed = gate_module.EgressDecision.ALLOW

    def _always_allow(self, request):  # noqa: ARG001 - signature must match
        return allowed, "MUTATED: the egress gate was disabled on purpose"

    gate_module.EgressGate._evaluate = _always_allow

    # Verify the mutation actually took effect. Without this, a rename or a changed
    # call path would turn the whole check into a no-op that always "proves" the
    # suite works — which is exactly the failure mode this plugin exists to rule out.
    probe = gate_module.EgressGate()
    request = gate_module.EgressRequest("https://example.com", purpose="llm.chat")
    if probe.check(request) is not allowed:
        raise RuntimeError("mutation plugin: the gate still denies — the mutation is inert")
