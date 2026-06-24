import sqlite3, json, time
db = sqlite3.connect("ai-server/data/audit.db")

gate_rows = db.execute(
    "SELECT MIN(timestamp_ms) FROM audit WHERE action=?",
    ("autonomous_llm_gate",)
).fetchone()
gate_start = gate_rows[0] if gate_rows and gate_rows[0] else 0

error_rows = db.execute(
    "SELECT MIN(timestamp_ms) FROM audit WHERE detail_json LIKE ?",
    ("%402%",)
).fetchone()
error_start = error_rows[0] if error_rows and error_rows[0] else int(time.time() * 1000)

print("Gate started: %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(gate_start/1000)))
print("First 402:    %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(error_start/1000)))
print("Window:       %d minutes" % ((error_start - gate_start) // 60000))

print()
print("=== llm_call between gate and 402 (per model) ===")
rows = db.execute(
    "SELECT model, COUNT(*), AVG(tokens_used), MAX(tokens_used), SUM(tokens_used) "
    "FROM audit WHERE action=? AND timestamp_ms >= ? AND timestamp_ms < ? "
    "GROUP BY model ORDER BY SUM(tokens_used) DESC",
    ("llm_call", gate_start, error_start)
).fetchall()
for r in rows:
    print("  model=%s calls=%d avg=%.0f max=%d total=%d" % (
        r[0] or "unknown", r[1], r[2] or 0, r[3] or 0, r[4] or 0
    ))

print()
print("=== llm_tool_call between gate and 402 (per model) ===")
rows2 = db.execute(
    "SELECT model, COUNT(*), AVG(tokens_used), MAX(tokens_used), SUM(tokens_used) "
    "FROM audit WHERE action=? AND timestamp_ms >= ? AND timestamp_ms < ? "
    "GROUP BY model ORDER BY SUM(tokens_used) DESC",
    ("llm_tool_call", gate_start, error_start)
).fetchall()
for r in rows2:
    print("  model=%s calls=%d avg=%.0f max=%d total=%d" % (
        r[0] or "unknown", r[1], r[2] or 0, r[3] or 0, r[4] or 0
    ))

print()
print("=== Callers in window ===")
rows3 = db.execute(
    "SELECT action, detail_json FROM audit "
    "WHERE action IN (?, ?) AND timestamp_ms >= ? AND timestamp_ms < ?",
    ("llm_call", "llm_tool_call", gate_start, error_start)
).fetchall()
from collections import Counter
callers = Counter()
for r in rows3:
    detail = json.loads(r[1]) if r[1] else {}
    caller = detail.get("caller", detail.get("profile", "unknown"))
    callers["%s/%s" % (r[0], caller)] += 1
for k, v in callers.most_common():
    print("  %s: %d" % (k, v))

print()
print("=== Hourly breakdown in window ===")
rows4 = db.execute(
    "SELECT date(timestamp_ms/1000, 'unixepoch', '+9 hours') as day, "
    "CAST(strftime('%H', timestamp_ms/1000, 'unixepoch', '+9 hours') AS INTEGER) as hour, "
    "action, COUNT(*), SUM(tokens_used) "
    "FROM audit WHERE action IN (?, ?) AND timestamp_ms >= ? AND timestamp_ms < ? "
    "GROUP BY day, hour, action ORDER BY day, hour",
    ("llm_call", "llm_tool_call", gate_start, error_start)
).fetchall()
for r in rows4:
    print("  %s %02d:00  %s: %d calls, %d tokens" % (r[0], r[1], r[2], r[3], r[4] or 0))

print()
total_calls = db.execute(
    "SELECT COUNT(*), SUM(tokens_used) FROM audit "
    "WHERE action=? AND timestamp_ms >= ? AND timestamp_ms < ?",
    ("llm_call", gate_start, error_start)
).fetchone()
print("=== Summary ===")
print("Total llm_call in window: %d calls, %d tokens" % (total_calls[0], total_calls[1] or 0))
