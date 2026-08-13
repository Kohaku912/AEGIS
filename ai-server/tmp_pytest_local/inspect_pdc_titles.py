import json
import sqlite3

conn = sqlite3.connect("/app/data/personal_data/core.db")
print("=== titles with question marks ===")
rows = conn.execute(
    """
    SELECT event_type, title, payload_json
    FROM events
    WHERE title LIKE '%?%' OR payload_json LIKE '%????%'
    ORDER BY timestamp_ms DESC
    LIMIT 30
    """
).fetchall()
print("count_sample", len(rows))
for event_type, title, payload_json in rows:
    payload = json.loads(payload_json or "{}")
    bits = {
        key: payload.get(key)
        for key in (
            "app_name",
            "process_name",
            "window_title",
            "active_window_title",
            "control_name",
            "package_name",
            "title",
            "text",
            "value",
        )
        if payload.get(key)
    }
    print("---")
    print("type", event_type)
    print("title", repr(title))
    print("payload_bits", bits)

print("=== recent 10 ===")
for event_type, title, device, ts, payload_json in conn.execute(
    "SELECT event_type, title, source_device, timestamp_ms, payload_json FROM events ORDER BY timestamp_ms DESC LIMIT 10"
):
    payload = json.loads(payload_json or "{}")
    bits = {
        key: payload.get(key)
        for key in (
            "app_name",
            "window_title",
            "active_window_title",
            "control_name",
            "package_name",
            "value",
            "keyboard_count",
            "url",
            "title",
            "text",
        )
        if payload.get(key) not in (None, "", 0)
    }
    print(event_type, "|", repr(title), "|", device, "|", bits)
