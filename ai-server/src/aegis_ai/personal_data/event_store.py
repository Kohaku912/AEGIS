"""SQLite event / observation / state / graph / FTS store for Personal Data Core."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from aegis_ai.personal_data.models import (
    Entity,
    Fact,
    Inference,
    MemoryDerivation,
    Observation,
    Relationship,
    StateSnapshot,
    TimelineEvent,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  source_device TEXT NOT NULL,
  source_sensor TEXT NOT NULL,
  event_type TEXT NOT NULL,
  epistemics TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 1.0,
  classification TEXT NOT NULL DEFAULT 'personal',
  location_json TEXT NOT NULL DEFAULT '{}',
  entity_ids_json TEXT NOT NULL DEFAULT '[]',
  evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  observation_ids_json TEXT NOT NULL DEFAULT '[]',
  provenance_json TEXT NOT NULL DEFAULT '{}',
  payload_json TEXT NOT NULL DEFAULT '{}',
  title TEXT NOT NULL DEFAULT '',
  retention_class TEXT NOT NULL DEFAULT 'long_event'
);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_events_device ON events(source_device, timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type, timestamp_ms);

CREATE TABLE IF NOT EXISTS observations (
  id TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  source_device TEXT NOT NULL,
  source_sensor TEXT NOT NULL,
  event_type TEXT NOT NULL DEFAULT '',
  epistemics TEXT NOT NULL DEFAULT 'observed',
  confidence REAL NOT NULL DEFAULT 1.0,
  classification TEXT NOT NULL DEFAULT 'personal',
  location_json TEXT NOT NULL DEFAULT '{}',
  entity_ids_json TEXT NOT NULL DEFAULT '[]',
  evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  provenance_json TEXT NOT NULL DEFAULT '{}',
  payload_json TEXT NOT NULL DEFAULT '{}',
  title TEXT NOT NULL DEFAULT '',
  retention_class TEXT NOT NULL DEFAULT 'long_event'
);
CREATE INDEX IF NOT EXISTS idx_obs_time ON observations(timestamp_ms);

CREATE TABLE IF NOT EXISTS states (
  id TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  source_device TEXT NOT NULL,
  source_sensor TEXT NOT NULL,
  event_type TEXT NOT NULL DEFAULT 'state.snapshot',
  epistemics TEXT NOT NULL DEFAULT 'generated',
  confidence REAL NOT NULL DEFAULT 1.0,
  classification TEXT NOT NULL DEFAULT 'personal',
  location_json TEXT NOT NULL DEFAULT '{}',
  entity_ids_json TEXT NOT NULL DEFAULT '[]',
  evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  provenance_json TEXT NOT NULL DEFAULT '{}',
  payload_json TEXT NOT NULL DEFAULT '{}',
  title TEXT NOT NULL DEFAULT '',
  retention_class TEXT NOT NULL DEFAULT 'forever_metadata',
  subject TEXT NOT NULL DEFAULT 'user'
);
CREATE INDEX IF NOT EXISTS idx_states_time ON states(timestamp_ms, source_device);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY,
  sha256 TEXT NOT NULL,
  codec TEXT NOT NULL,
  byte_size INTEGER NOT NULL,
  path TEXT NOT NULL,
  retention_class TEXT NOT NULL,
  timestamp_ms INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  source_device TEXT NOT NULL,
  mime TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_evidence_time ON evidence(timestamp_ms);

CREATE TABLE IF NOT EXISTS entities (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  attributes_json TEXT NOT NULL DEFAULT '{}',
  first_seen_ms INTEGER NOT NULL,
  last_seen_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS relationships (
  id TEXT PRIMARY KEY,
  from_id TEXT NOT NULL,
  rel_type TEXT NOT NULL,
  to_id TEXT NOT NULL,
  valid_from_ms INTEGER NOT NULL,
  valid_to_ms INTEGER,
  evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  event_ids_json TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_rel_from ON relationships(from_id, valid_from_ms);

CREATE TABLE IF NOT EXISTS facts (
  id TEXT PRIMARY KEY,
  statement TEXT NOT NULL,
  confidence REAL NOT NULL,
  timestamp_ms INTEGER NOT NULL,
  source_event_ids_json TEXT NOT NULL,
  source_evidence_ids_json TEXT NOT NULL DEFAULT '[]',
  epistemics TEXT NOT NULL DEFAULT 'observed'
);
CREATE INDEX IF NOT EXISTS idx_facts_time ON facts(timestamp_ms);

CREATE TABLE IF NOT EXISTS inferences (
  id TEXT PRIMARY KEY,
  statement TEXT NOT NULL,
  confidence REAL NOT NULL,
  timestamp_ms INTEGER NOT NULL,
  based_on_fact_ids_json TEXT NOT NULL DEFAULT '[]',
  based_on_event_ids_json TEXT NOT NULL DEFAULT '[]',
  method TEXT NOT NULL DEFAULT 'rule'
);

CREATE TABLE IF NOT EXISTS memory_derivations (
  id TEXT PRIMARY KEY,
  memory_id TEXT NOT NULL,
  fact_ids_json TEXT NOT NULL DEFAULT '[]',
  event_ids_json TEXT NOT NULL DEFAULT '[]',
  created_at_ms INTEGER NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(id UNINDEXED, title, payload, tokenize='unicode61');
"""


def _j(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _loads(raw: str, default: Any) -> Any:
    try:
        return json.loads(raw)
    except Exception:
        return default


class EventStore:
    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def insert_event(self, event: TimelineEvent) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO events (
                    id, timestamp_ms, duration_ms, source_device, source_sensor, event_type,
                    epistemics, confidence, classification, location_json, entity_ids_json,
                    evidence_ids_json, observation_ids_json, provenance_json, payload_json,
                    title, retention_class
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event.id, event.timestamp_ms, event.duration_ms, event.source_device,
                    event.source_sensor, event.event_type, event.epistemics, event.confidence,
                    event.classification, _j(event.location.model_dump()), _j(event.entity_ids),
                    _j(event.evidence_ids), _j(event.observation_ids), _j(event.provenance.model_dump()),
                    _j(event.payload), event.title, event.retention_class,
                ),
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO events_fts(id, title, payload) VALUES (?,?,?)",
                (event.id, event.title, _fts_text(event.payload)),
            )
            self._conn.commit()

    def insert_observation(self, obs: Observation) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO observations (
                    id, timestamp_ms, duration_ms, source_device, source_sensor, event_type,
                    epistemics, confidence, classification, location_json, entity_ids_json,
                    evidence_ids_json, provenance_json, payload_json, title, retention_class
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    obs.id, obs.timestamp_ms, obs.duration_ms, obs.source_device, obs.source_sensor,
                    obs.event_type, obs.epistemics, obs.confidence, obs.classification,
                    _j(obs.location.model_dump()), _j(obs.entity_ids), _j(obs.evidence_ids),
                    _j(obs.provenance.model_dump()), _j(obs.payload), obs.title, obs.retention_class,
                ),
            )
            self._conn.commit()

    def insert_state(self, state: StateSnapshot) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO states (
                    id, timestamp_ms, duration_ms, source_device, source_sensor, event_type,
                    epistemics, confidence, classification, location_json, entity_ids_json,
                    evidence_ids_json, provenance_json, payload_json, title, retention_class, subject
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    state.id, state.timestamp_ms, state.duration_ms, state.source_device,
                    state.source_sensor, state.event_type, state.epistemics, state.confidence,
                    state.classification, _j(state.location.model_dump()), _j(state.entity_ids),
                    _j(state.evidence_ids), _j(state.provenance.model_dump()), _j(state.payload),
                    state.title, state.retention_class, state.subject,
                ),
            )
            self._conn.commit()

    def insert_evidence_meta(self, row: dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO evidence (
                    id, sha256, codec, byte_size, path, retention_class, timestamp_ms,
                    duration_ms, source_device, mime, metadata_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"], row["sha256"], row["codec"], row["byte_size"], row["path"],
                    row["retention_class"], row["timestamp_ms"], row.get("duration_ms", 0),
                    row["source_device"], row.get("mime", ""), _j(row.get("metadata") or {}),
                ),
            )
            self._conn.commit()

    def upsert_entity(self, entity: Entity) -> None:
        with self._lock:
            existing = self._conn.execute("SELECT first_seen_ms FROM entities WHERE id=?", (entity.id,)).fetchone()
            first = existing["first_seen_ms"] if existing else entity.first_seen_ms
            self._conn.execute(
                """INSERT OR REPLACE INTO entities (id, kind, name, attributes_json, first_seen_ms, last_seen_ms)
                   VALUES (?,?,?,?,?,?)""",
                (entity.id, entity.kind, entity.name, _j(entity.attributes), first, entity.last_seen_ms),
            )
            self._conn.commit()

    def insert_relationship(self, rel: Relationship) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO relationships (
                    id, from_id, rel_type, to_id, valid_from_ms, valid_to_ms, evidence_ids_json, event_ids_json
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    rel.id, rel.from_id, rel.rel_type, rel.to_id, rel.valid_from_ms, rel.valid_to_ms,
                    _j(rel.evidence_ids), _j(rel.event_ids),
                ),
            )
            self._conn.commit()

    def insert_fact(self, fact: Fact) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO facts (
                    id, statement, confidence, timestamp_ms, source_event_ids_json,
                    source_evidence_ids_json, epistemics
                ) VALUES (?,?,?,?,?,?,?)""",
                (
                    fact.id, fact.statement, fact.confidence, fact.timestamp_ms,
                    _j(fact.source_event_ids), _j(fact.source_evidence_ids), fact.epistemics,
                ),
            )
            self._conn.execute(
                "INSERT OR REPLACE INTO events_fts(id, title, payload) VALUES (?,?,?)",
                (fact.id, fact.statement, fact.statement),
            )
            self._conn.commit()

    def insert_inference(self, inf: Inference) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO inferences (
                    id, statement, confidence, timestamp_ms, based_on_fact_ids_json,
                    based_on_event_ids_json, method
                ) VALUES (?,?,?,?,?,?,?)""",
                (
                    inf.id, inf.statement, inf.confidence, inf.timestamp_ms,
                    _j(inf.based_on_fact_ids), _j(inf.based_on_event_ids), inf.method,
                ),
            )
            self._conn.commit()

    def insert_memory_derivation(self, row: MemoryDerivation) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO memory_derivations (id, memory_id, fact_ids_json, event_ids_json, created_at_ms)
                   VALUES (?,?,?,?,?)""",
                (row.id, row.memory_id, _j(row.fact_ids), _j(row.event_ids), row.created_at_ms),
            )
            self._conn.commit()

    def timeline(
        self,
        *,
        from_ms: int = 0,
        to_ms: int = 0,
        device: str = "",
        event_type: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        clauses = ["timestamp_ms >= ?"]
        args: list[Any] = [from_ms]
        if to_ms:
            clauses.append("timestamp_ms <= ?")
            args.append(to_ms)
        if device:
            clauses.append("source_device = ?")
            args.append(device)
        if event_type:
            clauses.append("event_type = ?")
            args.append(event_type)
        where = " AND ".join(clauses)
        with self._lock:
            total = self._conn.execute(f"SELECT COUNT(*) FROM events WHERE {where}", args).fetchone()[0]
            rows = self._conn.execute(
                f"SELECT * FROM events WHERE {where} ORDER BY timestamp_ms DESC LIMIT ? OFFSET ?",
                [*args, limit, offset],
            ).fetchall()
        return [self._event_row(row) for row in rows], int(total)

    def event_type_counts(
        self,
        *,
        from_ms: int = 0,
        to_ms: int = 0,
        device: str = "",
    ) -> list[dict[str, Any]]:
        clauses = ["timestamp_ms >= ?"]
        args: list[Any] = [from_ms]
        if to_ms:
            clauses.append("timestamp_ms <= ?")
            args.append(to_ms)
        if device:
            clauses.append("source_device = ?")
            args.append(device)
        where = " AND ".join(clauses)
        with self._lock:
            rows = self._conn.execute(
                f"SELECT event_type, COUNT(*) AS count FROM events WHERE {where} "
                "GROUP BY event_type ORDER BY count DESC, event_type ASC",
                args,
            ).fetchall()
        return [{"event_type": str(row["event_type"]), "count": int(row["count"])} for row in rows]

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
            if row is None:
                return None
            event = self._event_row(row)
            obs_ids = event.get("observation_ids") or []
            observations = []
            for oid in obs_ids:
                obs = self._conn.execute("SELECT * FROM observations WHERE id=?", (oid,)).fetchone()
                if obs is not None:
                    observations.append(self._obs_row(obs))
            evidence = []
            for eid in event.get("evidence_ids") or []:
                ev = self._conn.execute("SELECT * FROM evidence WHERE id=?", (eid,)).fetchone()
                if ev is not None:
                    evidence.append(dict(ev))
            facts = [
                dict(r)
                for r in self._conn.execute(
                    "SELECT * FROM facts WHERE source_event_ids_json LIKE ?",
                    (f"%{event_id}%",),
                ).fetchall()
            ]
            inferences = [
                dict(r)
                for r in self._conn.execute(
                    "SELECT * FROM inferences WHERE based_on_event_ids_json LIKE ?",
                    (f"%{event_id}%",),
                ).fetchall()
            ]
        event["observations"] = observations
        event["evidence"] = evidence
        event["facts"] = facts
        event["inferences"] = inferences
        return event

    def search_fts(self, query: str, *, from_ms: int = 0, to_ms: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        with self._lock:
            try:
                hits = self._conn.execute(
                    "SELECT id FROM events_fts WHERE events_fts MATCH ? LIMIT ?",
                    (query, limit * 4),
                ).fetchall()
            except sqlite3.OperationalError:
                hits = self._conn.execute(
                    "SELECT id FROM events WHERE title LIKE ? OR payload_json LIKE ? LIMIT ?",
                    (f"%{query}%", f"%{query}%", limit * 4),
                ).fetchall()
        ids = [row["id"] for row in hits]
        out: list[dict[str, Any]] = []
        for event_id in ids:
            event = self.get_event(event_id) if False else None
            with self._lock:
                row = self._conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
            if row is None:
                continue
            item = self._event_row(row)
            if from_ms and item["timestamp_ms"] < from_ms:
                continue
            if to_ms and item["timestamp_ms"] > to_ms:
                continue
            out.append(item)
            if len(out) >= limit:
                break
        return out

    def neighbor_entities(self, entity_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """SELECT * FROM relationships WHERE from_id=? OR to_id=?
                   ORDER BY valid_from_ms DESC LIMIT ?""",
                (entity_id, entity_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_facts(self, *, from_ms: int = 0, to_ms: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        clauses = ["timestamp_ms >= ?"]
        args: list[Any] = [from_ms]
        if to_ms:
            clauses.append("timestamp_ms <= ?")
            args.append(to_ms)
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM facts WHERE {' AND '.join(clauses)} ORDER BY timestamp_ms DESC LIMIT ?",
                [*args, limit],
            ).fetchall()
        return [dict(row) for row in rows]

    def latest_state(self, device: str = "") -> dict[str, Any] | None:
        with self._lock:
            if device:
                row = self._conn.execute(
                    "SELECT * FROM states WHERE source_device=? ORDER BY timestamp_ms DESC LIMIT 1",
                    (device,),
                ).fetchone()
            else:
                row = self._conn.execute("SELECT * FROM states ORDER BY timestamp_ms DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def get_evidence_meta(self, evidence_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        return dict(row) if row else None

    def delete_before(self, cutoff_ms: int, *, retention_class: str) -> tuple[int, list[dict[str, Any]]]:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM events WHERE timestamp_ms < ? AND retention_class=?",
                (cutoff_ms, retention_class),
            )
            deleted = cur.rowcount
            self._conn.execute(
                "DELETE FROM observations WHERE timestamp_ms < ? AND retention_class=?",
                (cutoff_ms, retention_class),
            )
            ev = self._conn.execute(
                "SELECT id, path FROM evidence WHERE timestamp_ms < ? AND retention_class=?",
                (cutoff_ms, retention_class),
            ).fetchall()
            self._conn.execute(
                "DELETE FROM evidence WHERE timestamp_ms < ? AND retention_class=?",
                (cutoff_ms, retention_class),
            )
            self._conn.commit()
        return int(deleted), [dict(row) for row in ev]

    def export_range(self, from_ms: int, to_ms: int) -> dict[str, Any]:
        events, _ = self.timeline(from_ms=from_ms, to_ms=to_ms or 2**62, limit=100000)
        with self._lock:
            facts = [dict(r) for r in self._conn.execute(
                "SELECT * FROM facts WHERE timestamp_ms>=? AND timestamp_ms<=?", (from_ms, to_ms or 2**62)
            ).fetchall()]
            inferences = [dict(r) for r in self._conn.execute(
                "SELECT * FROM inferences WHERE timestamp_ms>=? AND timestamp_ms<=?", (from_ms, to_ms or 2**62)
            ).fetchall()]
        return {"events": events, "facts": facts, "inferences": inferences}

    def delete_ids(self, event_ids: list[str]) -> int:
        if not event_ids:
            return 0
        with self._lock:
            for event_id in event_ids:
                self._conn.execute("DELETE FROM events WHERE id=?", (event_id,))
                self._conn.execute("DELETE FROM events_fts WHERE id=?", (event_id,))
            self._conn.commit()
        return len(event_ids)

    def _event_row(self, row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["location"] = _loads(item.pop("location_json", "{}"), {})
        item["entity_ids"] = _loads(item.pop("entity_ids_json", "[]"), [])
        item["evidence_ids"] = _loads(item.pop("evidence_ids_json", "[]"), [])
        item["observation_ids"] = _loads(item.pop("observation_ids_json", "[]"), [])
        item["provenance"] = _loads(item.pop("provenance_json", "{}"), {})
        item["payload"] = _loads(item.pop("payload_json", "{}"), {})
        return item

    def _obs_row(self, row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["location"] = _loads(item.pop("location_json", "{}"), {})
        item["entity_ids"] = _loads(item.pop("entity_ids_json", "[]"), [])
        item["evidence_ids"] = _loads(item.pop("evidence_ids_json", "[]"), [])
        item["provenance"] = _loads(item.pop("provenance_json", "{}"), {})
        item["payload"] = _loads(item.pop("payload_json", "{}"), {})
        return item


def _fts_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("title", "app_name", "process_name", "url", "control_name", "package_name", "transcript", "window_title", "value"):
        value = payload.get(key)
        if value:
            parts.append(str(value))
    keys = payload.get("keys")
    if isinstance(keys, list):
        parts.extend(str(item) for item in keys if item)
    return " ".join(parts)
