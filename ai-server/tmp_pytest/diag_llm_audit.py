import json
from pathlib import Path
hits=[]
for p in list(Path("/app/data").rglob("*.jsonl")) + list(Path("/app/data").rglob("*.log")):
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "llm_tool_call" in txt:
        hits.append(p)
print("files with llm_tool_call:", [str(h) for h in hits])
for p in hits[:2]:
    lines=[l for l in p.read_text(encoding="utf-8",errors="replace").splitlines() if "llm_tool_call" in l]
    print("===", p, len(lines))
    for line in lines[-3:]:
        try: e=json.loads(line)
        except: continue
        d = e.get("detail") or e
        print("  decision:", e.get("decision"), "tool_count:", d.get("tool_count"), "tokens:", d.get("tokens"), "out_tokens:", d.get("output_tokens"))
        print("  RESPONSE_PREVIEW:", json.dumps(str(d.get("response_preview"))[:1500], ensure_ascii=False))
        print("  PROMPT_PREVIEW:", json.dumps(str(d.get("prompt_preview"))[:2500], ensure_ascii=False))
