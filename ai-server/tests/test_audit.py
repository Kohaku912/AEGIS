"""Tests for AuditLog — Phase 1.5 append-only decision recording."""

from __future__ import annotations

from aegis_ai.audit import AuditEntry, AuditLog


class TestAuditLog:
    def test_append_entry(self):
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        entry = AuditEntry(
            action="tool_invoked",
            actor="aegis",
            capability_id="pc.screenshot",
            decision="ALLOW",
            reason="READ_ONLY capability",
        )
        log.append(entry)
        assert entry.entry_id != ""
        assert entry.timestamp_ms > 0

    def test_list_recent(self):
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        log.log_decision("test", "pc.a", "ALLOW")
        log.log_decision("test", "pc.b", "DENY")
        recent = log.list_recent(10)
        assert len(recent) == 2

    def test_log_decision_convenience(self):
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        entry = log.log_decision(
            action="policy_decision",
            capability_id="room.ir_send",
            decision="ASK_APPROVAL",
            reason="Requires user approval",
            actor="policy_engine",
            detail={"risk_level": 3},
        )
        assert entry.decision == "ASK_APPROVAL"
        assert entry.actor == "policy_engine"

    def test_append_only_no_delete(self):
        """AuditLog has no delete method — entries are append-only."""
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        log.log_decision("test", "pc.test", "ALLOW")
        # No delete/remove method exists on AuditLog
        assert not hasattr(log, "delete")
        assert not hasattr(log, "remove")
        assert not hasattr(log, "update")

    def test_thread_safety(self):
        """Multiple threads can write concurrently without corruption."""
        import threading

        log = AuditLog(path="data/test_audit_phase15.jsonl")
        errors = []

        def write_entries(prefix: str) -> None:
            try:
                for i in range(10):
                    log.log_decision("test", f"{prefix}.{i}", "ALLOW")
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=write_entries, args=(f"t{i}",)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(log.list_recent(100)) == 40

    def test_read_all_from_file(self):
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        log.log_decision("test", "pc.file_test", "ALLOW")
        records = log.read_all()
        assert len(records) >= 1
        assert "entry_id" in records[-1]

    def test_policy_decision_recorded(self):
        """PolicyDecision must always be recorded."""
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        log.log_decision("policy_decision", "pc.test", "DENY", reason="Explicit deny pattern")
        recent = log.list_recent(1)
        assert recent[0].action == "policy_decision"
        assert recent[0].decision == "DENY"

    def test_approval_decision_recorded(self):
        """ApprovalDecision must always be recorded."""
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        log.log_decision("approval_granted", "room.ir_send", "APPROVED",
                        reason="User approved one-time", actor="user")
        recent = log.list_recent(1)
        assert recent[0].action == "approval_granted"
        assert recent[0].decision == "APPROVED"
        assert recent[0].actor == "user"

    def test_all_required_fields(self):
        """AuditEntry must have action, decision, reason, timestamp, actor, capability_id."""
        log = AuditLog(path="data/test_audit_phase15.jsonl")
        entry = log.log_decision(
            action="tool_denied",
            capability_id="pc.delete_all",
            decision="DENY",
            reason="Explicit deny pattern",
            actor="policy_engine",
        )
        assert entry.action == "tool_denied"
        assert entry.decision == "DENY"
        assert entry.reason != ""
        assert entry.timestamp_ms > 0
        assert entry.actor == "policy_engine"
        assert entry.capability_id == "pc.delete_all"
