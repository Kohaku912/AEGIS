import sqlite3, json, time
db = sqlite3.connect("ai-server/data/audit.db")

# 1. Token usage by day
rows = db.execute(
    "SELECT date(timestamp_ms/1000, 'unixepoch', '+9 hours') as day, "
    "action, COUNT(*), SUM(tokens_used) FROM audit "
    "WHERE action IN (?, ?) GROUP BY day, action ORDER BY day DESC LIMIT 14",
    ("llm_call", "llm_tool_call")
).fetchall()
print("=== Token usage by day (JST) ===")
for r in rows:
    print("%s  %s: %d calls, %d tokens" % (r[0], r[1], r[2], r[3] or 0))

# 2. Last successful LLM calls
print()
print("=== Last 5 successful llm_call ===")
rows2 = db.execute(
    "SELECT timestamp_ms, model, tokens_used FROM audit "
    "WHERE action=? AND tokens_used > 0 ORDER BY timestamp_ms DESC LIMIT 5",
    ("llm_call",)
).fetchall()
for r in rows2:
    ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(r[0]/1000))
    print("%s  model=%s tokens=%d" % (ts, r[1], r[2]))

# 3. All-time total
print()
total = db.execute("SELECT SUM(tokens_used) FROM audit").fetchone()
print("All-time total tokens: %d" % (total[0] or 0))

# 4. llm_call callers last 3 hours
print()
print("=== llm_call entries (last 3 hours) ===")
cutoff = int(time.time() * 1000) - (3 * 3600 * 1000)
rows3 = db.execute(
    "SELECT timestamp_ms, model, detail_json FROM audit "
    "WHERE action=? AND timestamp_ms >= ? ORDER BY timestamp_ms",
    ("llm_call", cutoff)
).fetchall()
for r in rows3:
    detail = json.loads(r[2]) if r[2] else {}
    ts = time.strftime("%H:%M:%S", time.localtime(r[0]/1000))
    print("[%s] model=%s success=%s reason=%s" % (
        ts, r[1], detail.get("success", "?"), detail.get("reason", "")[:60]
    ))

# 5. llm_tool_call callers last 3 hours
print()
print("=== llm_tool_call entries (last 3 hours) ===")
rows4 = db.execute(
    "SELECT timestamp_ms, model, detail_json FROM audit "
    "WHERE action=? AND timestamp_ms >= ? ORDER BY timestamp_ms",
    ("llm_tool_call", cutoff)
).fetchall()
for r in rows4:
    detail = json.loads(r[2]) if r[2] else {}
    ts = time.strftime("%H:%M:%S", time.localtime(r[0]/1000))
    caller = detail.get("caller", "unknown")
    error = str(detail.get("error", ""))[:80]
    print("[%s] model=%s caller=%s error=%s" % (ts, r[1], caller, error))

# 6. Check for any non-autonomous LLM callers
print()
print("=== All unique action types with token usage ===")
rows5 = db.execute(
    "SELECT action, COUNT(*), SUM(tokens_used) FROM audit "
    "WHERE tokens_used > 0 GROUP BY action ORDER BY SUM(tokens_used) DESC"
).fetchall()
for r in rows5:
    print("%s: %d calls, %d tokens" % (r[0], r[1], r[2]))
