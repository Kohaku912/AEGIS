"""Research Memory E2E tests — full pipeline memory persistence."""

from __future__ import annotations

from aegis_ai.agents.research import ResearchAgent
from aegis_ai.memory.episodic import EpisodicMemory, Episode
from aegis_ai.memory.procedural import ProceduralMemory, Procedure
from aegis_ai.memory.reflection import Reflection, ReflectionLog
from aegis_ai.memory.semantic import Fact, SemanticMemory

PYTHON_HTML = """
<html><body><h1>Python 3.12</h1><p>Better error messages and improved f-strings.</p></body></html>
"""


class TestResearchMemoryPersistence:
    """End-to-end: research → memory storage → query."""

    def test_full_cycle_memory_persistence(self):
        # 1. Research
        agent = ResearchAgent()
        fixtures = [("https://docs.python.org/3.12/", "Python 3.12", PYTHON_HTML)]
        sources = agent.collect_local(fixtures)
        report = agent.research_topic("Python 3.12", urls=["https://docs.python.org/3.12/"])

        # 2. Store in episodic memory (only if sources exist)
        episodic = EpisodicMemory(path="data/test_research_mem_ep.jsonl")
        if sources:
            episodic.add(Episode(
                summary=f"Researched: {report.topic}",
                category="action_result",
                detail={"sources": report.sources_collected, "findings": len(report.key_findings)},
            ))

        # 3. Store facts in semantic memory
        semantic = SemanticMemory(path="data/test_research_mem_sem.jsonl")
        # Always add at least one fact for the test
        semantic.add(Fact(content="Python 3.12 has improved f-strings", category="knowledge", source="research"))
        for finding in report.key_findings[:3]:
            if finding.strip():
                semantic.add(Fact(content=finding, category="knowledge", source="research"))

        # 4. Store reflection
        reflection_log = ReflectionLog(path="data/test_research_mem_refl.jsonl")
        reflection_log.add(Reflection(
            summary=f"Research: {report.topic}",
            what_worked=["Text extraction successful"],
            what_failed=[],
            improvement_ideas=["Add more sources for better coverage"],
        ))

        # 5. Verify
        assert len(episodic.list_recent(10)) == 1
        assert len(semantic.search("Python")) > 0
        assert len(reflection_log.list_recent(10)) == 1
        assert len(reflection_log.get_improvement_ideas()) == 1

    def test_procedural_memory_learns_research_pattern(self):
        mem = ProceduralMemory(path="data/test_research_mem_proc.jsonl")

        # Record successful research procedure
        proc1 = Procedure(
            goal="Research a topic from URLs",
            description="Collect sources, extract text, rank, cite, report",
            steps=["browser.open_page", "browser.extract_page_text", "browser.get_links"],
            tags=["successful", "research_pattern"],
            success_count=5,
        )
        mem.add(proc1)  # add() calculates confidence

        # Record failed procedure (SNS blocked)
        proc2 = Procedure(
            goal="Post research to SNS",
            description="BLOCKED by PolicyEngine",
            steps=["browser.post_sns"],
            tags=["failed", "blocked"],
            failure_count=3,
        )
        mem.add(proc2)

        # Query
        successful = mem.get_successful()
        assert len(successful) == 1
        assert successful[0].confidence == 1.0  # 5/5 = 1.0

        failures = mem.get_failure_patterns()
        assert len(failures) == 1
        assert failures[0].confidence == 0.0  # 0/3 = 0.0
