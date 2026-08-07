#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    exec_path = Path("/app/data/autonomous/execution_log.jsonl")
    fail_caps: Counter[str] = Counter()
    fail_samples: dict[str, list[str]] = defaultdict(list)
    if exec_path.exists():
        lines = exec_path.read_text(encoding="utf-8", errors="replace").splitlines()[-300:]
        for line in lines:
            try:
                e = json.loads(line)
            except Exception:
                continue
            for i, r in enumerate(e.get("results") or []):
                if r.get("success") is True:
                    continue
                tasks = e.get("tasks") or []
                t = tasks[i] if i < len(tasks) else {}
                cap = str(t.get("capability_id") or r.get("capability_id") or "?")
                err = str(r.get("result") or r.get("error") or "")[:240]
                fail_caps[cap] += 1
                if len(fail_samples[cap]) < 4:
                    fail_samples[cap].append(err.replace("\n", " "))

    print("===EXEC_FAIL_CAPS===")
    for cap, n in fail_caps.most_common(30):
        print(f"{n:4d} {cap}")
        for s in fail_samples[cap]:
            print("   ", s[:200])

    db = Path("/app/data/audit.db")
    if db.exists():
        con = sqlite3.connect(str(db))
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        print("===AUDIT_TABLES===", tables)
        for t in tables:
            cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
            print(f"  {t}:", cols)
        for t in tables:
            try:
                rows = cur.execute(
                    f"SELECT * FROM {t} ORDER BY rowid DESC LIMIT 5"
                ).fetchall()
                print(f"===SAMPLE {t}===")
                for r in rows:
                    print(" ", str(r)[:300])
            except Exception as ex:
                print("sample fail", t, ex)
        # try flexible search
        for t in tables:
            cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]
            text_cols = [c for c in cols if c.lower() in {
                "action", "decision", "reason", "capability_id", "detail", "message", "status"
            }]
            if not text_cols:
                continue
            where = " OR ".join(
                f"CAST({c} AS TEXT) LIKE '%fail%' OR CAST({c} AS TEXT) LIKE '%FAIL%' OR CAST({c} AS TEXT) LIKE '%DENY%' OR CAST({c} AS TEXT) LIKE '%ERROR%'"
                for c in text_cols
            )
            try:
                q = f"SELECT * FROM {t} WHERE {where} ORDER BY rowid DESC LIMIT 40"
                rows = cur.execute(q).fetchall()
                print(f"===FAILISH {t} count={len(rows)}===")
                for r in rows[:20]:
                    print(" ", str(r)[:350])
            except Exception as ex:
                print("query fail", t, ex)
        con.close()

    # docker logs hint via file if any
    for p in [
        Path("/app/data/tasks/task_manager.jsonl"),
        Path("/app/data/operations/operations.jsonl"),
        Path("/app/data/social/social_inbox.json"),
    ]:
        print("EXISTS", p, p.exists())

    ops = Path("/app/data/operations/operations.jsonl")
    if ops.exists():
        fails: Counter[str] = Counter()
        samples: dict[str, list[str]] = defaultdict(list)
        for line in ops.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]:
            try:
                e = json.loads(line)
            except Exception:
                continue
            blob = json.dumps(e, ensure_ascii=False).lower()
            if "fail" not in blob and e.get("success") is not False:
                continue
            cap = str(e.get("capability_id") or e.get("action_summary") or e.get("action") or "?")[:100]
            fails[cap] += 1
            if len(samples[cap]) < 2:
                samples[cap].append(str(e)[:220])
        print("===OPS_FAILISH===")
        for k, n in fails.most_common(20):
            print(n, k)
            for s in samples[k]:
                print("  ", s)

    # inbox failed
    inbox = Path("/app/data/social/social_inbox.json")
    if inbox.exists():
        data = json.loads(inbox.read_text(encoding="utf-8"))
        items = data.get("items") or []
        st = Counter(str(i.get("status")) for i in items)
        print("===INBOX_STATUS===", dict(st))
        for i in items:
            if str(i.get("status")) in {"failed", "retry_pending"}:
                print(
                    i.get("status"),
                    i.get("channel"),
                    str(i.get("decision_reason") or "")[:180],
                    str(i.get("body") or "")[:80],
                )


if __name__ == "__main__":
    main()
