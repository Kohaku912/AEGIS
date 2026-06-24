import sqlite3, json, time
db = sqlite3.connect("ai-server/data/audit.db")

gate_start = 1750425705000  # 2026-06-20 21:41:45 JST approx

print("=== LLM calls after 30-min gate (2026-06-20 21:41 JST) ===")
print()

# All llm_call after gate
rows = db.execute(
    "SELECT timestamp_ms, model, tokens_used, detail_json FROM audit "
    "WHERE action=? AND timestamp_ms >= ? ORDER BY timestamp_ms",
    ("llm_call", gate_start)
).fetchall()

success_count = 0
fail_count = 0
success_tokens = 0
by_model = {}

for r in rows:
    detail = json.loads(r[3]) if r[3] else {}
    model = r[1] or "unknown"
    tokens = r[2] or 0
    success = detail.get("success", False)
    error = str(detail.get("error", ""))[:60]
    ts = time.strftime("%m/%d %H:%M", time.localtime(r[0]/1000))

    if success:
        success_count += 1
        success_tokens += tokens
        if model not in by_model:
            by_model[model] = {"calls": 0, "tokens": 0, "max_tokens": 0}
        by_model[model]["calls"] += 1
        by_model[model]["tokens"] += tokens
        by_model[model]["max_tokens"] = max(by_model[model]["max_tokens"], tokens)
    else:
        fail_count += 1

# Per-model stats for SUCCESSFUL calls
print("Per-model stats (successful calls only):")
for model, stats in sorted(by_model.items(), key=lambda x: -x[1]["tokens"]):
    avg = stats["tokens"] / stats["calls"] if stats["calls"] > 0 else 0
    print("  model=%s  calls=%d  avg_tokens=%.0f  max_tokens=%d  total=%d" % (
        model, stats["calls"], avg, stats["max_tokens"], stats["tokens"]
    ))

print()
print("Successful calls: %d (%d tokens)" % (success_count, success_tokens))
print("Failed calls: %d" % fail_count)
print("Total calls: %d" % len(rows))

# Also check llm_tool_call
print()
print("=== llm_tool_call after gate ===")
rows2 = db.execute(
    "SELECT timestamp_ms, model, tokens_used, detail_json FROM audit "
    "WHERE action=? AND timestamp_ms >= ? ORDER BY timestamp_ms",
    ("llm_tool_call", gate_start)
).fetchall()

tool_success = 0
tool_fail = 0
for r in rows2:
    detail = json.loads(r[3]) if r[3] else {}
    error = str(detail.get("error", ""))
    if "402" in error or "Insufficient" in error:
        tool_fail += 1
    else:
        tool_success += 1

print("Successful: %d" % tool_success)
print("Failed (402): %d" % tool_fail)
print("Total: %d" % len(rows2))

# Hourly breakdown after gate
print()
print("=== Hourly breakdown after gate (successful only) ===")
rows3 = db.execute(
    "SELECT date(timestamp_ms/1000, 'unixepoch', '+9 hours') as day, "
    "CAST(strftime('%H', timestamp_ms/1000, 'unixepoch', '+9 hours') AS INTEGER) as hour, "
    "COUNT(*), SUM(tokens_used) "
    "FROM audit WHERE action=? AND timestamp_ms >= ? AND tokens_used > 0 "
    "GROUP BY day, hour ORDER BY day, hour",
    ("llm_call", gate_start)
).fetchall()
for r in rows3:
    print("  %s %02d:00  %d calls, %d tokens" % (r[0], r[1], r[2], r[3] or 0))

# What about before the gate? Show the high-usage period
print()
print("=== Before gate: daily stats ===")
rows4 = db.execute(
    "SELECT date(timestamp_ms/1000, 'unixepoch', '+9 hours') as day, "
    "COUNT(*), SUM(tokens_used), AVG(tokens_used), MAX(tokens_used) "
    "FROM audit WHERE action=? AND timestamp_ms < ? AND tokens_used > 0 "
    "GROUP BY day ORDER BY day",
    ("llm_call", gate_start)
).fetchall()
for r in rows4:
    print("  %s  %d calls  total=%d  avg=%.0f  max=%d" % (r[0], r[1], r[2] or 0, r[3] or 0, r[4] or 0))
