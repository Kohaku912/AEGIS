from __future__ import annotations

from aegis_ai.audit import AuditLog, AuditManager
from aegis_ai.verification import (
    VerificationRequest,
    VerificationResult,
    VerificationService,
    VerificationStatus,
    VerificationStrategy,
)
from tool_broker import ExecutionSource


def test_verification_service_records_to_canonical_audit_manager(tmp_path) -> None:
    audit_log = AuditLog(tmp_path / "audit.db")
    audit_manager = AuditManager(audit_log=audit_log, data_dir=tmp_path)
    service = VerificationService(audit_log=audit_manager)
    request = VerificationRequest(
        capability_id="pc-server.screenshot.get_screenshot",
        request_id="request-1",
        task_id="task-1",
        source=ExecutionSource.USER_EXPLICIT,
        verification_strategy=VerificationStrategy.PC_SCREEN_OBSERVATION,
    )
    result = VerificationResult(
        verification_id="verification-1",
        status=VerificationStatus.VERIFIED,
        confidence=1.0,
        reason="Observed expected state.",
    )

    service.record_verification(request, result)

    entries = audit_manager.list_recent(limit=10)["entries"]
    assert len(entries) == 1
    assert entries[0]["action"] == "verification"
    assert entries[0]["actor"] == "user_explicit"
    assert entries[0]["decision"] == "verified"
    assert entries[0]["detail"]["task_id"] == "task-1"
