"""Phase 3: the post-hoc ledger of irreversible operations.

Approval was retired as a constraint on 2026-09-27; the replacement for a
pre-execution gate is *post-hoc visibility*. These tests pin both halves of that
bargain:

* the **inventory** is derived from the manifests, so a newly added capability
  cannot silently escape it;
* the **occurrences** view joins the audit log on ``capability_id``, so nothing
  had to be instrumented for an irreversible action to be traceable;

and they pin that the ledger *observes only* — there is no endpoint that can
change a decision.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai import irreversibility
from aegis_ai.folder_registry import CapabilityManifest, FolderCapabilityRegistry
from aegis_schema import safety_vocab


def _capabilities_root() -> Path:
    return Path(__file__).resolve().parents[1] / "capabilities"


@pytest.fixture
def catalog() -> FolderCapabilityRegistry:
    return FolderCapabilityRegistry(str(_capabilities_root()))


class _FakeAudit:
    """Minimal stand-in for AuditManager's read surface."""

    def __init__(self, entries: list[dict]) -> None:
        self._entries = entries
        self.calls: list[dict] = []

    def list_recent(self, limit: int = 100, page: int = 1, **kwargs) -> dict:
        self.calls.append({"limit": limit, "page": page, **kwargs})
        return {
            "entries": self._entries,
            "page": page,
            "per_page": limit,
            "total": len(self._entries),
        }


# ── Inventory ───────────────────────────────────────────────────────────────

def test_inventory_equals_what_the_manifests_declare(catalog) -> None:
    """The inventory is derived, never hand-maintained — that is the whole point."""
    declared = {
        manifest.capability_id
        for manifest in catalog.list_all()
        if manifest.reversibility in {"difficult", "irreversible"}
    }
    assert declared, "expected some non-trivially-reversible capabilities"
    assert {
        entry["capability_id"]
        for entry in irreversibility.inventory(catalog, include_unknown=False)
    } == declared

    # The default view is exactly that set, plus whatever declares `unknown`.
    unknown = {
        manifest.capability_id
        for manifest in catalog.list_all()
        if manifest.reversibility == safety_vocab.UNKNOWN
    }
    assert {entry["capability_id"] for entry in irreversibility.inventory(catalog)} == (
        declared | unknown
    )


def test_the_irreversible_capabilities_are_exactly_these(catalog) -> None:
    assert sorted(irreversibility.summarize(catalog)["irreversible"]) == [
        "pc-server.shell.execute",
        "pc-server.shell.powershell",
        "pc-server.system.empty_recycle_bin",
    ]


def test_widening_the_threshold_widens_the_inventory(catalog) -> None:
    strict = irreversibility.inventory(catalog, threshold="irreversible", include_unknown=False)
    default = irreversibility.inventory(catalog, threshold="difficult", include_unknown=False)
    loose = irreversibility.inventory(catalog, threshold="recoverable", include_unknown=False)
    assert len(strict) == 3
    assert {e["capability_id"] for e in strict} < {e["capability_id"] for e in default}
    assert {e["capability_id"] for e in default} < {e["capability_id"] for e in loose}


def test_inventory_is_sorted_worst_first(catalog) -> None:
    severities = [
        irreversibility.SEVERITY.get(entry["reversibility"], 99)
        for entry in irreversibility.inventory(catalog, include_unknown=False)
    ]
    assert severities == sorted(severities, reverse=True)


@pytest.mark.parametrize("threshold", ["unknown", "banana", "", "IRREVERSIBLE"])
def test_threshold_must_be_a_severity_level(catalog, threshold: str) -> None:
    """``unknown`` is not on the scale, so it is not a valid threshold."""
    with pytest.raises(ValueError):
        irreversibility.inventory(catalog, threshold=threshold)


def test_unknown_is_surfaced_by_default_and_can_be_excluded(catalog) -> None:
    """An operation nobody described is what an owner wants to *see*, not hide."""
    with_unknown = {e["capability_id"] for e in irreversibility.inventory(catalog)}
    without = {
        e["capability_id"]
        for e in irreversibility.inventory(catalog, include_unknown=False)
    }
    assert "browser-server.page.browse" in with_unknown
    assert "browser-server.page.browse" not in without
    assert without < with_unknown


# ── Summary ─────────────────────────────────────────────────────────────────

def test_summary_tallies_cover_every_capability(catalog) -> None:
    ledger = irreversibility.summarize(catalog)
    assert ledger["total_capabilities"] == catalog.count()
    assert sum(ledger["by_reversibility"].values()) == ledger["total_capabilities"]
    assert sum(ledger["by_ownership_scope"].values()) == ledger["total_capabilities"]
    assert sum(ledger["by_blast_radius"].values()) == ledger["total_capabilities"]


def test_summary_exposes_the_delete_send_and_overwrite_buckets(catalog) -> None:
    """The plan names delete / send / purchase as the must-see categories."""
    effects = irreversibility.summarize(catalog)["by_destructive_effect"]
    for bucket in ("file_delete", "message_send", "data_overwrite", "process_terminate"):
        assert effects.get(bucket, 0) >= 1, f"expected at least one {bucket!r}"
    # `purchase` is in the vocabulary but no capability declares it: purchases are
    # a structural DENY in the policy engine, not a callable capability.
    assert effects.get("purchase", 0) == 0


def test_summary_lists_capabilities_that_declare_unknown(catalog) -> None:
    assert irreversibility.summarize(catalog)["declares_unknown"] == [
        "browser-server.page.browse"
    ]


def test_summary_never_reports_a_capability_twice(catalog) -> None:
    reportable = irreversibility.summarize(catalog)["reportable"]
    ids = [entry["capability_id"] for entry in reportable]
    assert len(ids) == len(set(ids))


# ── Annotation ──────────────────────────────────────────────────────────────

def test_annotation_of_a_silent_manifest_reads_unknown() -> None:
    entry = irreversibility.annotation(CapabilityManifest())
    assert entry["reversibility"] == safety_vocab.UNKNOWN
    assert entry["ownership_scope"] == safety_vocab.UNKNOWN
    assert entry["blast_radius"] == safety_vocab.UNKNOWN
    assert entry["destructive_effects"] == [safety_vocab.UNKNOWN]


def test_annotate_policy_result_copies_the_manifest_annotations() -> None:
    from policy_engine import PolicyDecision, PolicyResult

    manifest = CapabilityManifest(
        capability_id="pc-server.shell.execute",
        ownership_scope="system",
        reversibility="irreversible",
        destructive_effects=["file_delete", "data_overwrite"],
        data_loss_risk="high",
        active_work_loss_risk="high",
        blast_radius="system_wide",
    )
    result = PolicyResult(decision=PolicyDecision.ALLOW_WITH_AUDIT)
    irreversibility.annotate_policy_result(result, manifest)
    assert result.reversibility == "irreversible"
    assert result.ownership_scope == "system"
    assert result.blast_radius == "system_wide"
    assert result.data_loss_risk == "high"
    assert result.destructive_effects == ["file_delete", "data_overwrite"]


def test_annotate_policy_result_without_a_manifest_reads_unknown() -> None:
    from policy_engine import PolicyDecision, PolicyResult

    result = PolicyResult(decision=PolicyDecision.ALLOW)
    irreversibility.annotate_policy_result(result, None)
    assert result.reversibility == safety_vocab.UNKNOWN
    assert result.blast_radius == safety_vocab.UNKNOWN
    assert result.destructive_effects == [safety_vocab.UNKNOWN]


def test_annotate_policy_result_tolerates_a_missing_result() -> None:
    assert irreversibility.annotate_policy_result(None, None) is None


def test_broker_attaches_the_annotations_to_the_policy_result(tmp_path) -> None:
    """The annotations must reach the audit entry, not just the manifest.

    Uses a harmless local read (``ai-server.memory.search``) so nothing is
    actually performed — the assertion is about the policy result's provenance.
    """
    from policy_engine import PolicyEngine
    from tool_broker import ToolBroker, ToolExecutionRequest
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditLog
    from aegis_ai.capability_catalog import CapabilityCatalog

    data_dir = tmp_path / "data"
    catalog = CapabilityCatalog(
        capabilities_dir=str(_capabilities_root()),
        apps_dir=str(data_dir / "apps"),
        data_dir=str(data_dir),
    )
    broker = ToolBroker(
        registry=ToolRegistry(),
        policy_engine=PolicyEngine(data_dir=str(data_dir)),
        audit_log=AuditLog(path=str(data_dir / "audit.jsonl")),
        catalog=catalog,
    )
    cap_id = "ai-server.memory.search"
    result = broker.execute(ToolExecutionRequest(capability_id=cap_id, arguments={"query": "x"}))

    manifest = catalog.resolve(cap_id)
    assert manifest is not None
    assert result.policy_result is not None
    assert result.policy_result.reversibility == manifest.reversibility == "fully_reversible"
    assert result.policy_result.ownership_scope == manifest.ownership_scope == "aegis"
    assert result.policy_result.blast_radius == manifest.blast_radius == "single"


# ── Occurrences ─────────────────────────────────────────────────────────────

def test_occurrences_join_the_audit_log_on_capability_id(catalog) -> None:
    audit = _FakeAudit(
        [
            {
                "entry_id": "e1",
                "capability_id": "pc-server.shell.execute",
                "action": "tool_invoked",
                "decision": "ALLOW_WITH_AUDIT",
                "timestamp_ms": 1,
                "detail_summary": "ran a command",
            },
            {
                "entry_id": "e2",
                "capability_id": "ai-server.memory.search",
                "action": "tool_invoked",
                "decision": "ALLOW",
                "timestamp_ms": 2,
            },
            {
                "entry_id": "e3",
                "capability_id": "pc-server.system.empty_recycle_bin",
                "action": "tool_invoked",
                "decision": "ALLOW_WITH_AUDIT",
                "timestamp_ms": 3,
            },
        ]
    )
    result = irreversibility.occurrences(audit, catalog)
    assert [entry["entry_id"] for entry in result["entries"]] == ["e1", "e3"]
    assert result["scanned"] == 3
    assert result["total"] == 2

    shell = result["entries"][0]
    assert shell["reversibility"] == "irreversible"
    assert shell["blast_radius"] == "system_wide"
    assert "file_delete" in shell["destructive_effects"]


def test_occurrences_without_an_audit_manager_is_empty_not_an_error(catalog) -> None:
    assert irreversibility.occurrences(None, catalog) == {
        "entries": [],
        "total": 0,
        "scanned": 0,
        "threshold": "difficult",
    }


def test_occurrences_honours_include_unknown(catalog) -> None:
    audit = _FakeAudit(
        [{"entry_id": "e1", "capability_id": "browser-server.page.browse", "action": "tool_invoked"}]
    )
    assert irreversibility.occurrences(audit, catalog)["total"] == 1
    assert irreversibility.occurrences(audit, catalog, include_unknown=False)["total"] == 0


def test_occurrences_passes_paging_through(catalog) -> None:
    audit = _FakeAudit([])
    irreversibility.occurrences(audit, catalog, limit=7, page=3)
    assert audit.calls == [{"limit": 7, "page": 3}]


# ── Read API ────────────────────────────────────────────────────────────────

def _app(catalog, audit_manager=None):
    from flask import Flask

    from aegis_ai.web.routes.audit import init_audit_routes

    app = Flask(__name__)
    app.config["TESTING"] = True
    init_audit_routes(
        SimpleNamespace(
            app=app,
            _runtime=SimpleNamespace(
                tool_broker=SimpleNamespace(_catalog=catalog),
                audit_manager=audit_manager,
            ),
        )
    )
    return app


def test_irreversible_endpoint_returns_the_ledger(catalog) -> None:
    response = _app(catalog).test_client().get("/api/audit/irreversible")
    assert response.status_code == 200
    body = response.get_json()
    assert body["total_capabilities"] == catalog.count()
    assert "pc-server.shell.execute" in body["irreversible"]
    assert body["by_destructive_effect"]["file_delete"] >= 1


def test_irreversible_endpoint_honours_the_threshold_param(catalog) -> None:
    client = _app(catalog).test_client()
    strict = client.get("/api/audit/irreversible?threshold=irreversible&include_unknown=false")
    loose = client.get("/api/audit/irreversible?threshold=recoverable&include_unknown=false")
    assert strict.status_code == loose.status_code == 200
    assert len(strict.get_json()["reportable"]) < len(loose.get_json()["reportable"])


def test_irreversible_endpoint_rejects_an_unknown_threshold(catalog) -> None:
    response = _app(catalog).test_client().get("/api/audit/irreversible?threshold=banana")
    assert response.status_code == 400
    assert "threshold" in response.get_json()["error"]


def test_irreversible_endpoint_reports_503_without_a_catalog() -> None:
    response = _app(None).test_client().get("/api/audit/irreversible")
    assert response.status_code == 503


def test_occurrences_endpoint_returns_matched_entries(catalog) -> None:
    audit = _FakeAudit(
        [{"entry_id": "e1", "capability_id": "pc-server.shell.execute", "action": "tool_invoked"}]
    )
    response = _app(catalog, audit).test_client().get("/api/audit/irreversible/occurrences")
    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["entries"][0]["capability_id"] == "pc-server.shell.execute"


def test_occurrences_endpoint_clamps_paging(catalog) -> None:
    audit = _FakeAudit([])
    client = _app(catalog, audit).test_client()
    client.get("/api/audit/irreversible/occurrences?limit=99999&page=0")
    assert audit.calls == [{"limit": 1000, "page": 1}]


def test_the_ledger_api_is_read_only(catalog) -> None:
    """The ledger observes; it must not be able to change a decision."""
    app = _app(catalog)
    routes = {
        str(rule.rule): sorted(rule.methods - {"HEAD", "OPTIONS"})
        for rule in app.url_map.iter_rules()
    }
    assert routes["/api/audit/irreversible"] == ["GET"]
    assert routes["/api/audit/irreversible/occurrences"] == ["GET"]
