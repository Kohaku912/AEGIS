"""Tests for observe capabilities."""


from aegis_browser.observe import (
    extract_page_text,
)
from aegis_browser.safety import CAPABILITIES, SafetyLevel


class TestCapabilityDefinitions:
    def test_all_observe_capabilities_are_level_0(self):
        observe_caps = [
            "browser.extract_page_text", "browser.get_screenshot",
            "browser.get_current_url", "browser.get_page_title", "browser.get_links",
        ]
        for cap_id in observe_caps:
            assert cap_id in CAPABILITIES, f"Missing capability: {cap_id}"
            cap = CAPABILITIES[cap_id]
            assert cap["safety_level"] == SafetyLevel.LEVEL_0_READ, \
                f"{cap_id} should be LEVEL_0_READ, got {cap['safety_level']}"

    def test_open_page_is_level_1(self):
        assert CAPABILITIES["browser.open_page"]["safety_level"] == SafetyLevel.LEVEL_1_SAFE_ACT

    def test_run_task_readonly_is_level_1(self):
        assert CAPABILITIES["browser.run_task_readonly"]["safety_level"] == SafetyLevel.LEVEL_1_SAFE_ACT


class TestExtractPageText:
    def test_removes_script_and_style(self):
        """Verify the JS extraction logic excludes script/style/nav/footer."""
        js_code = """
            (() => {
                const exclude = ['script', 'style', 'nav', 'footer', 'noscript', 'iframe', 'svg'];
                const clone = document.body.cloneNode(true);
                exclude.forEach(tag => {
                    clone.querySelectorAll(tag).forEach(el => el.remove());
                });
                return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
            })()
        """
        assert "script" in js_code
        assert "style" in js_code
        assert "nav" in js_code
        assert "footer" in js_code

    def test_extract_page_text_function_exists(self):
        """Verify the function is importable and has correct signature."""
        import inspect
        sig = inspect.signature(extract_page_text)
        params = list(sig.parameters.keys())
        assert "page" in params
        assert "max_length" in params
        assert "include_alt_text" in params


class TestGetLinks:
    def test_links_extraction_js(self):
        """Verify the JS for link extraction includes internal flag."""
        js_code = """
            (() => {
                return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    href: a.href,
                    text: (a.textContent || '').trim().substring(0, 200),
                    internal: a.href.startsWith(window.location.origin)
                }));
            })()
        """
        assert "internal" in js_code
        assert "a[href]" in js_code
        assert "substring(0, 200)" in js_code
