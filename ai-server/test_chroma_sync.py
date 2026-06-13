import sys, os
sys.path.insert(0, '.')
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.memory.chroma_semantic import ChromaSemanticMemory
from aegis_ai.llm.factory import create_llm_provider
from pathlib import Path

data_dir = str(Path('aegis_ai/web/dashboard_routes.py').resolve().parent.parent.parent.parent / 'data')
llm = create_llm_provider()
mem = AdvancedMemory(data_dir=data_dir + '/memory', llm_provider=llm)
sem = ChromaSemanticMemory(chroma_path=data_dir + '/chroma')
count = sem.sync_from_advanced_memory(mem)
print(f'Synced: {count}')
entries = sem.get_all(limit=5)
print(f'Entries: {len(entries)}')
for e in entries[:3]:
    print(f'  {e["content"][:80]}')
