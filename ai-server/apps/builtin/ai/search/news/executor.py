import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src'))
from aegis_ai.integrations.duckduckgo_search import DuckDuckGoSearch

data = json.loads(sys.stdin.read())
query = data.get("query", "")
max_results = data.get("max_results", 5)
if not query:
    print(json.dumps({"ok": False, "error": "No query provided"}))
    sys.exit(1)

search = DuckDuckGoSearch()
response = search.search_news(query, max_results=max_results)
if response.success and response.results:
    lines = []
    for r in response.results[:max_results]:
        lines.append(f"- {r.title}: {r.snippet[:100]}")
        lines.append(f"  {r.url}")
    print(json.dumps({"ok": True, "result": f"News results for '{query}':\n" + "\n".join(lines)}))
else:
    print(json.dumps({"ok": True, "result": f"No news results for: {query}"}))
