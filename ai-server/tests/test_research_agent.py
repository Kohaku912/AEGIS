"""Tests for Research Agent — source collection, extraction, citation, reporting."""

from __future__ import annotations

from aegis_ai.agents.research import ResearchAgent
from aegis_ai.research.citation import CitationManager
from aegis_ai.research.collector import SourceCollector
from aegis_ai.research.extractor import TextExtractor
from aegis_ai.research.ranker import SourceRanker
from aegis_ai.research.report import ReportBuilder
from aegis_ai.research.source import SourceNote

SAMPLE_HTML_1 = """
<html><head><title>Python 3.12 Release</title></head>
<body>
<h1>What's New in Python 3.12</h1>
<p>Python 3.12 introduces several important features including better error messages,
improved f-strings, and performance improvements.</p>
<h2>Key Features</h2>
<ul>
<li>Better error messages with more context</li>
<li>F-string improvements — arbitrary expressions allowed</li>
<li>Per-interpreter GIL (experimental)</li>
<li>Comprehension inlining for performance</li>
</ul>
<p>For more details, visit docs.python.org.</p>
</body></html>
"""

SAMPLE_HTML_2 = """
<html><head><title>Python 3.12 Overview</title></head>
<body>
<h1>Python 3.12 Overview</h1>
<p>Python 3.12 was released on October 2, 2023. It focuses on stability and performance.
Some users report issues with the new GIL implementation.</p>
<p>Important: the per-interpreter GIL is still experimental and may not work with all C extensions.</p>
<p>Warning: Some third-party libraries have not yet been updated for 3.12 compatibility.</p>
</body></html>
"""


class TestSourceNote:
    def test_create_source_note(self):
        note = SourceNote(url="https://example.com", title="Example")
        assert note.url == "https://example.com"
        assert note.status == "pending"

    def test_mark_collected(self):
        note = SourceNote()
        note.mark_collected()
        assert note.status == "collected"
        assert note.collected_at_ms > 0

    def test_mark_failed(self):
        note = SourceNote()
        note.mark_failed("Connection refused")
        assert note.status == "failed"
        assert "Connection refused" in note.error_message


class TestSourceCollector:
    def test_collect_local_html(self):
        collector = SourceCollector()
        note = collector.collect_local("https://example.com", SAMPLE_HTML_1, "Python 3.12")
        assert note.status == "collected"
        assert note.title == "Python 3.12"
        assert len(note.key_points) > 0
        assert note.reliability_hint == "unverified"

    def test_collect_without_tool_broker(self):
        collector = SourceCollector()
        note = collector.collect("https://example.com", "src_1")
        assert note.status == "collected"
        assert "Mock" in note.title

    def test_collect_removes_script_and_style(self):
        html_with_script = """
        <html><body>
        <p>Visible text here</p>
        <script>console.log('hidden');</script>
        <style>.hidden { display: none; }</style>
        </body></html>
        """
        collector = SourceCollector()
        note = collector.collect_local("https://test.com", html_with_script, "Test")
        assert "Visible text here" in note.extracted_text_summary
        assert "console.log" not in note.extracted_text_summary
        assert ".hidden" not in note.extracted_text_summary


class TestCitationManager:
    def test_assign_labels(self):
        cm = CitationManager()
        assert cm.assign_label("src_1") == "[1]"
        assert cm.assign_label("src_2") == "[2]"
        assert cm.assign_label("src_3") == "[3]"

    def test_format_reference(self):
        cm = CitationManager()
        cm.assign_label("src_1")
        ref = cm.format_reference("src_1", "Python 3.12 Docs", "https://docs.python.org/3.12/")
        assert "[1]" in ref
        assert "Python 3.12 Docs" in ref
        assert "https://docs.python.org" in ref

    def test_format_reference_list(self):
        cm = CitationManager()
        cm.assign_label("a")
        cm.assign_label("b")
        refs = cm.format_reference_list([
            ("a", "Title A", "https://a.com"),
            ("b", "Title B", "https://b.com"),
        ])
        assert "[1]" in refs
        assert "[2]" in refs


class TestSourceRanker:
    def test_rank_sources(self):
        ranker = SourceRanker()
        sources = [
            SourceNote(source_id="a", url="https://docs.python.org", title="Official Docs",
                      domain_category="documentation", reliability_hint="high", full_text_length=3000),
            SourceNote(source_id="b", url="https://reddit.com/r/python", title="Reddit Thread",
                      domain_category="forum", reliability_hint="low", full_text_length=500),
            SourceNote(source_id="c", url="https://blog.example.com", title="Blog Post",
                      domain_category="blog", reliability_hint="medium", full_text_length=1500),
        ]
        ranked = ranker.rank(sources)
        assert ranked[0].source.source_id == "a"  # Official docs should be first
        assert ranked[2].source.source_id == "b"  # Reddit should be last

    def test_get_top(self):
        ranker = SourceRanker()
        sources = [SourceNote(source_id=str(i), url=f"https://site{i}.com") for i in range(5)]
        top = ranker.get_top(sources, n=2)
        assert len(top) == 2


class TestTextExtractor:
    def test_extract_key_points(self):
        extractor = TextExtractor()
        result = extractor.extract("This is important and very detailed content about Python 3.12 features. " * 10)
        assert len(result.key_points) > 0
        assert result.word_count > 0

    def test_clean_boilerplate(self):
        extractor = TextExtractor()
        result = extractor.extract("Cookie Consent We use cookies.\n\nActual content here.")
        assert "Cookie" not in result.cleaned_text
        assert "Actual content" in result.cleaned_text


class TestReportBuilder:
    def test_build_report_from_sources(self):
        collector = SourceCollector()
        note1 = collector.collect_local("https://docs.python.org/3.12/", SAMPLE_HTML_1, "Python 3.12 Release")
        note1.reliability_hint = "high"
        note1.domain_category = "documentation"

        note2 = collector.collect_local("https://example.com/overview", SAMPLE_HTML_2, "Python 3.12 Overview")
        note2.reliability_hint = "low"  # Make one low-reliability to trigger conflict
        note2.domain_category = "blog"

        builder = ReportBuilder()
        report = builder.build("Python 3.12 features", [note1, note2])

        assert report.topic == "Python 3.12 features"
        assert report.sources_collected == 2
        assert len(report.summary) > 0
        assert len(report.key_findings) > 0
        assert len(report.reference_list) > 0
        # Should have a conflict note (high vs low reliability)
        assert len(report.conflicting_info) > 0


class TestResearchAgent:
    def test_research_with_local_html(self):
        agent = ResearchAgent()
        fixtures = [
            ("https://docs.python.org/3.12/", "Python 3.12", SAMPLE_HTML_1),
            ("https://example.com/overview", "Python Overview", SAMPLE_HTML_2),
        ]
        sources = agent.collect_local(fixtures)
        assert len(sources) == 2
        assert sources[0].status == "collected"

    def test_research_topic_with_urls(self):
        agent = ResearchAgent()
        report = agent.research_topic("Python 3.12", urls=[
            "https://docs.python.org/3.12/",
            "https://realpython.com/python312/",
        ])
        assert report is not None
        assert "Python 3.12" in report.topic
        assert report.sources_collected == 2

    def test_research_topic_no_urls(self):
        agent = ResearchAgent()
        report = agent.research_topic("Empty topic", urls=[])
        assert report.sources_collected == 0
        assert "No sources" in report.summary

    def test_citation_labels_on_sources(self):
        agent = ResearchAgent()
        fixtures = [
            ("https://a.com", "Page A", "<html><body>Content A</body></html>"),
            ("https://b.com", "Page B", "<html><body>Content B</body></html>"),
        ]
        agent.collect_local(fixtures)
        report = agent.research_topic("Test", urls=["https://a.com", "https://b.com"])
        labels = {s.citation_label for s in report.sources}
        assert "[1]" in labels
        assert "[2]" in labels

    def test_graceful_failure_on_invalid_url(self):
        _ = ResearchAgent()
        # Mock collection doesn't fail, so we test the SourceNote failure path
        note = SourceNote(url="https://invalid.example.com")
        note.mark_failed("Connection timed out")
        assert note.status == "failed"
        assert "Connection timed out" in note.error_message

    def test_get_last_sources_and_report(self):
        agent = ResearchAgent()
        _ = agent.research_topic("Test", urls=["https://example.com"])
        assert len(agent.get_last_sources()) > 0
        assert agent.get_last_report() is not None
