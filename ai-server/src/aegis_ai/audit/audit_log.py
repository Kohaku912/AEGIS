# -*- coding: utf-8 -*-
'''Audit Log - SQLite-backed, append-only, immutable decision record.'''

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.audit.context import get_audit_group

logger = logging.getLogger('aegis_ai.audit.audit_log')


@dataclass
class AuditEntry:
    timestamp_ms: int = 0
    action: str = ''
    actor: str = ''
    capability_id: str = ''
    decision: str = ''
    reason: str = ''
    detail: dict[str, Any] = field(default_factory=dict)
    entry_id: str = ''
    profile_id: str = ''
    prompt_id: str = ''
    prompt_version: str = ''
    prompt_hash: str = ''
    model: str = ''
    max_tokens: int = 0
    temperature: float = 0.0
    reasoning_level: str = ''
    provider: str = ''
    tokens_used: int = 0
    duration_ms: int = 0
    approval_id: str = ''
    approval_channel: str = ''
    approval_user: str = ''
    request_id: str = ''
    task_id: str = ''
    source_desire: str = ''
    risk_level: str = ''
    audit_group_id: str = ''
    audit_group_type: str = ''
    audit_group_title: str = ''


_CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT UNIQUE NOT NULL,
    timestamp_ms INTEGER NOT NULL,
    action TEXT NOT NULL DEFAULT '',
    actor TEXT NOT NULL DEFAULT '',
    capability_id TEXT NOT NULL DEFAULT '',
    decision TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    detail_json TEXT NOT NULL DEFAULT '{}',
    profile_id TEXT NOT NULL DEFAULT '',
    prompt_id TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    prompt_hash TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    max_tokens INTEGER NOT NULL DEFAULT 0,
    temperature REAL NOT NULL DEFAULT 0.0,
    reasoning_level TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL DEFAULT '',
    tokens_used INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    approval_id TEXT NOT NULL DEFAULT '',
    approval_channel TEXT NOT NULL DEFAULT '',
    approval_user TEXT NOT NULL DEFAULT '',
    request_id TEXT NOT NULL DEFAULT '',
    task_id TEXT NOT NULL DEFAULT '',
    source_desire TEXT NOT NULL DEFAULT '',
    risk_level TEXT NOT NULL DEFAULT '',
    audit_group_id TEXT NOT NULL DEFAULT '',
    audit_group_type TEXT NOT NULL DEFAULT '',
    audit_group_title TEXT NOT NULL DEFAULT ''
)
'''

_CREATE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit(timestamp_ms)',
    'CREATE INDEX IF NOT EXISTS idx_audit_action ON audit(action)',
    'CREATE INDEX IF NOT EXISTS idx_audit_task ON audit(task_id)',
    'CREATE INDEX IF NOT EXISTS idx_audit_approval ON audit(approval_id)',
    'CREATE INDEX IF NOT EXISTS idx_audit_entry_id ON audit(entry_id)',
    'CREATE INDEX IF NOT EXISTS idx_audit_group ON audit(audit_group_id)',
]


class AuditLog:
    def __init__(self, path: str = 'data/audit.jsonl') -> None:
        db_path = Path(path).with_suffix('.db')
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._path = Path(path)
        self._lock = threading.Lock()
        self._entries: list[AuditEntry] = []
        self._conn: sqlite3.Connection | None = None
        self._init_db()
        self._migrate_jsonl_if_needed()
        self.close()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.execute(_CREATE_TABLE)
        self._ensure_group_columns(conn)
        for idx in _CREATE_INDEXES:
            conn.execute(idx)
        conn.commit()

    def _ensure_group_columns(self, conn: sqlite3.Connection) -> None:
        existing = {row[1] for row in conn.execute('PRAGMA table_info(audit)').fetchall()}
        columns = {
            'audit_group_id': "TEXT NOT NULL DEFAULT ''",
            'audit_group_type': "TEXT NOT NULL DEFAULT ''",
            'audit_group_title': "TEXT NOT NULL DEFAULT ''",
        }
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f'ALTER TABLE audit ADD COLUMN {name} {definition}')

    def _migrate_jsonl_if_needed(self) -> None:
        if not self._path.exists():
            return
        conn = self._get_conn()
        count = conn.execute('SELECT COUNT(*) FROM audit').fetchone()[0]
        if count > 0:
            return
        try:
            records = []
            with open(self._path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        continue
            if not records:
                return
            for r in records:
                self._insert_record(conn, r)
            conn.commit()
            logger.info('Migrated %d entries from JSONL to SQLite', len(records))
        except Exception:
            logger.debug('JSONL migration failed', exc_info=True)

    def _insert_record(self, conn: sqlite3.Connection, record: dict[str, Any]) -> None:
        try:
            conn.execute(
                '''INSERT OR IGNORE INTO audit
                (entry_id, timestamp_ms, action, actor, capability_id, decision, reason,
                 detail_json, profile_id, prompt_id, prompt_version, prompt_hash,
                 model, max_tokens, temperature, reasoning_level, provider,
                 tokens_used, duration_ms, approval_id, approval_channel,
                 approval_user, request_id, task_id, source_desire, risk_level,
                 audit_group_id, audit_group_type, audit_group_title)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (
                    record.get('entry_id', ''),
                    record.get('timestamp_ms', 0),
                    record.get('action', ''),
                    record.get('actor', ''),
                    record.get('capability_id', ''),
                    record.get('decision', ''),
                    record.get('reason', ''),
                    json.dumps(record.get('detail', {}), ensure_ascii=False),
                    record.get('profile_id', ''),
                    record.get('prompt_id', ''),
                    record.get('prompt_version', ''),
                    record.get('prompt_hash', ''),
                    record.get('model', ''),
                    record.get('max_tokens', 0),
                    record.get('temperature', 0.0),
                    record.get('reasoning_level', ''),
                    record.get('provider', ''),
                    record.get('tokens_used', 0),
                    record.get('duration_ms', 0),
                    record.get('approval_id', ''),
                    record.get('approval_channel', ''),
                    record.get('approval_user', ''),
                    record.get('request_id', ''),
                    record.get('task_id', ''),
                    record.get('source_desire', ''),
                    record.get('risk_level', ''),
                    record.get('audit_group_id', ''),
                    record.get('audit_group_type', ''),
                    record.get('audit_group_title', ''),
                )
            )
        except sqlite3.IntegrityError:
            pass

    def append(self, entry: AuditEntry) -> None:
        self._apply_group_context(entry)
        if not entry.entry_id:
            entry.entry_id = f'audit_{int(time.time() * 1000)}_{os.urandom(4).hex()}'
        if not entry.timestamp_ms:
            entry.timestamp_ms = int(time.time() * 1000)
        record = {
            'entry_id': entry.entry_id, 'timestamp_ms': entry.timestamp_ms,
            'action': entry.action, 'actor': entry.actor,
            'capability_id': entry.capability_id, 'decision': entry.decision,
            'reason': entry.reason, 'detail': entry.detail,
            'profile_id': entry.profile_id, 'prompt_id': entry.prompt_id,
            'prompt_version': entry.prompt_version, 'prompt_hash': entry.prompt_hash,
            'model': entry.model, 'max_tokens': entry.max_tokens,
            'temperature': entry.temperature, 'reasoning_level': entry.reasoning_level,
            'provider': entry.provider, 'tokens_used': entry.tokens_used,
            'duration_ms': entry.duration_ms, 'approval_id': entry.approval_id,
            'approval_channel': entry.approval_channel, 'approval_user': entry.approval_user,
            'request_id': entry.request_id, 'task_id': entry.task_id,
            'source_desire': entry.source_desire, 'risk_level': entry.risk_level,
            'audit_group_id': entry.audit_group_id,
            'audit_group_type': entry.audit_group_type,
            'audit_group_title': entry.audit_group_title,
        }
        with self._lock:
            conn = self._get_conn()
            self._insert_record(conn, record)
            conn.commit()
            self.close()
            self._entries.append(entry)

    def _apply_group_context(self, entry: AuditEntry) -> None:
        ctx = get_audit_group()
        if ctx is not None:
            if not entry.audit_group_id:
                entry.audit_group_id = ctx.group_id
            if not entry.audit_group_type:
                entry.audit_group_type = ctx.group_type
            if not entry.audit_group_title:
                entry.audit_group_title = ctx.group_title
        if not entry.audit_group_id:
            detail = entry.detail if isinstance(entry.detail, dict) else {}
            fallback_id = (
                entry.task_id
                or str(detail.get('task_id') or '')
                or entry.request_id
                or str(detail.get('request_id') or '')
                or entry.approval_id
                or str(detail.get('approval_id') or '')
            )
            if fallback_id:
                entry.audit_group_id = fallback_id
                entry.audit_group_type = 'task' if entry.task_id or detail.get('task_id') else 'approval'
                entry.audit_group_title = entry.audit_group_title or fallback_id

    def list_recent(self, n: int = 50) -> list[AuditEntry]:
        with self._lock:
            entries = list(self._entries)
        return entries[-n:] if n < len(entries) else entries

    def read_all(self) -> list[dict[str, Any]]:
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 10000').fetchall()
            return [self._row_to_dict(r) for r in rows]

    def read_page(self, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        offset = (page - 1) * per_page
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.row_factory = sqlite3.Row
            total = conn.execute('SELECT COUNT(*) FROM audit').fetchone()[0]
            rows = conn.execute('SELECT * FROM audit ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
            entries = [self._row_to_dict(r) for r in rows]
            total_pages = max(1, (total + per_page - 1) // per_page)
            return {'entries': entries, 'page': page, 'per_page': per_page, 'total': total, 'total_pages': total_pages}

    def count(self) -> int:
        with sqlite3.connect(str(self._db_path)) as conn:
            return conn.execute('SELECT COUNT(*) FROM audit').fetchone()[0]

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        detail_json = d.pop('detail_json', '{}')
        try:
            d['detail'] = json.loads(detail_json) if detail_json else {}
        except Exception:
            d['detail'] = {}
        d.pop('id', None)
        return d

    def log_decision(self, action: str, capability_id: str, decision: str, reason: str = '', actor: str = 'aegis', detail: dict[str, Any] | None = None, audit_group_id: str = '', audit_group_type: str = '', audit_group_title: str = '') -> AuditEntry:
        entry = AuditEntry(action=action, capability_id=capability_id, decision=decision, reason=reason, actor=actor, detail=detail or {}, audit_group_id=audit_group_id, audit_group_type=audit_group_type, audit_group_title=audit_group_title)
        self.append(entry)
        return entry

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            conn = self._get_conn()
            conn.execute('DELETE FROM audit')
            conn.commit()
            self.close()

    def log_approval(self, action: str, approval_id: str = '', capability_id: str = '', channel: str = '', user: str = '', request_id: str = '', task_id: str = '', source_desire: str = '', risk_level: str = '', detail: dict[str, Any] | None = None, audit_group_id: str = '', audit_group_type: str = '', audit_group_title: str = '') -> AuditEntry:
        entry = AuditEntry(action=action, capability_id=capability_id, approval_id=approval_id, approval_channel=channel, approval_user=user, request_id=request_id, task_id=task_id, source_desire=source_desire, risk_level=risk_level, detail=detail or {}, audit_group_id=audit_group_id, audit_group_type=audit_group_type, audit_group_title=audit_group_title)
        self.append(entry)
        return entry
