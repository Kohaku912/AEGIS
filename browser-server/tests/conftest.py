"""Shared pytest configuration for the browser-server test suite.

This mirrors ``ai-server/tests/conftest.py``: the browser server carries its own
copy of the egress gate (``aegis_browser.egress``) with deliberately identical
semantics, so it gets the same ``--fail-on-empty`` discipline.

The browser server drives a real browser, which makes it the most egress-prone
component in AEGIS. The dangerous failure mode is not "a test fails" but "no test
runs" — a rename or a narrowed ``-k`` expression can leave the egress selection
empty while pytest reports the rest of the suite as passing. CI therefore passes
an explicit floor (65 as of 2026-09-28 — raise it when you add egress tests)::

    pytest -m egress --require-egress-tests=65
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("aegis")
    group.addoption(
        "--require-egress-tests",
        action="store",
        type=int,
        default=0,
        metavar="N",
        dest="require_egress_tests",
        help=(
            "Fail the run unless at least N tests marked 'egress' were collected. "
            "Implements the --fail-on-empty discipline. Default 0 (check disabled)."
        ),
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    floor = int(config.getoption("require_egress_tests") or 0)
    if floor <= 0:
        return

    collected = sum(1 for item in items if item.get_closest_marker("egress") is not None)
    if collected < floor:
        raise pytest.UsageError(
            f"--require-egress-tests={floor}, but only {collected} egress-marked test(s) "
            f"were collected. The browser-server egress suite has shrunk: the single "
            f"constraint is no longer covered by as much testing as CI expects."
        )
