"""Intent Router — routes user intents to appropriate agents/systems."""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any

from aegis_ai.interaction.intent import Intent, classify_intent
from aegis_ai.interaction.message import Message, Response

logger = logging.getLogger("aegis_ai.interaction.router")


class InteractionRouter:
    """Routes user messages to appropriate agents/systems.

    Usage:
        router = InteractionRouter(
            research_agent=research,
            support_agent=support,
            tool_broker=broker,
            settings_store=settings,
            approval_store=approvals,
        )
        response = router.route(message)
    """

    def __init__(
        self,
        research_agent: Any = None,
        support_agent: Any = None,
        self_dev_agent: Any = None,
        tool_broker: Any = None,
        settings_store: Any = None,
        approval_store: Any = None,
        audit_log: Any = None,
        llm_provider: Any = None,
    ) -> None:
        self._research = research_agent
        self._support = support_agent
        self._self_dev = self_dev_agent
        self._broker = tool_broker
        self._settings = settings_store
        self._approval = approval_store
        self._audit = audit_log
        self._llm = llm_provider

    def route(self, message: Message) -> Response:
        """Route a user message to the appropriate handler.

        Returns a Response with the result.
        """
        intent = classify_intent(message.text)
        now_ms = int(time.time() * 1000)

        response = Response(
            response_id=f"resp_{uuid.uuid4().hex[:8]}",
            message_id=message.message_id,
            channel=message.channel,
            timestamp_ms=now_ms,
        )

        try:
            if intent == Intent.RESEARCH_REQUEST:
                response = self._handle_research(message, response)
            elif intent == Intent.SUPPORT_FEEDBACK:
                response = self._handle_support_feedback(message, response)
            elif intent == Intent.SETTINGS_REQUEST:
                response = self._handle_settings(message, response)
            elif intent == Intent.APPROVAL_DECISION:
                response = self._handle_approval(message, response)
            elif intent == Intent.SELF_DEV_REQUEST:
                response = self._handle_self_dev(message, response)
            elif intent == Intent.STATUS_CHECK:
                response = self._handle_status(message, response)
            elif intent == Intent.HELP_REQUEST:
                response = self._handle_help(message, response)
            elif intent == Intent.TOOL_REQUEST:
                response = self._handle_tool_request(message, response)
            else:
                response = self._handle_llm_fallback(message, response)

        except Exception as e:
            logger.error("Interaction routing failed: %s", e)
            response.text = f"Sorry, something went wrong: {e}"

        # Audit
        if self._audit:
            self._audit.log_decision(
                "interaction", f"intent.{intent.name}", "HANDLED",
                detail={"channel": message.channel.name, "text": message.text[:100]},
            )

        return response

    def _handle_research(self, message: Message, response: Response) -> Response:
        """Handle research requests."""
        if self._research:
            try:
                report = self._research.research_topic(message.text)
                if hasattr(report, "summary"):
                    response.text = report.summary
                    response.sources = [{"url": s.url, "title": s.title} for s in getattr(report, "sources", [])]
                else:
                    response.text = str(report)
            except Exception as e:
                response.text = f"Research failed: {e}"
        elif self._llm:
            # Fallback: use LLM for general research questions
            text = message.text.strip()
            has_url = bool(re.search(r'https?://[^\s]+', text))
            has_search = any(kw in text.lower() for kw in ["search for", "look up", "browse", "open", "go to"])

            if has_url or has_search:
                return self._handle_browser_request(message, response)
            else:
                # General question - use LLM directly
                try:
                    result = self._llm.generate(
                        prompt=text,
                        system_prompt="You are AEGIS, a helpful AI assistant. Answer concisely.",
                        max_tokens=500,
                    )
                    response.text = result.content if result.success else f"LLM error: {result.error}"
                except Exception as e:
                    response.text = f"Research failed: {e}"
        else:
            response.text = "Research Agent is not available."
        return response

    def _handle_support_feedback(self, message: Message, response: Response) -> Response:
        """Handle support feedback (accept/reject suggestions)."""
        text_lower = message.text.lower()
        accepted = any(w in text_lower for w in ["accept", "yes", "ok", "thanks"])
        rejected = any(w in text_lower for w in ["reject", "no", "dismiss"])

        if accepted:
            response.text = "Thank you for the feedback! I'll remember this."
        elif rejected:
            response.text = "Understood. I'll adjust future suggestions."
        else:
            response.text = "Could you clarify your feedback?"

        return response

    def _handle_settings(self, message: Message, response: Response) -> Response:
        """Handle settings requests."""
        if self._settings:
            settings = self._settings.get()
            response.text = (
                f"Current settings:\n"
                f"- Autonomous loop: {'enabled' if settings.autonomous.autonomous_loop_enabled else 'disabled'}\n"
                f"- Support agent: {'enabled' if settings.autonomous.support_agent_enabled else 'disabled'}\n"
                f"- Self-dev: {'enabled' if settings.autonomous.self_dev_proposal_enabled else 'disabled'}\n"
                f"\nUse the Dashboard to change settings: http://127.0.0.1:8090"
            )
        else:
            response.text = "Settings store not available."
        return response

    def _handle_approval(self, message: Message, response: Response) -> Response:
        """Handle approval decisions."""
        if self._approval:
            pending = self._approval.get_pending()
            if pending:
                response.text = f"You have {len(pending)} pending approval(s).\n"
                response.pending_approvals = [
                    {"approval_id": r.approval_id, "capability_id": r.capability_id, "tool_name": r.tool_name}
                    for r in pending[:5]
                ]
                response.text += "Use the Approval UI to decide: http://127.0.0.1:8080/approvals"
            else:
                response.text = "No pending approvals."
        else:
            response.text = "Approval store not available."
        return response

    def _handle_self_dev(self, message: Message, response: Response) -> Response:
        """Handle self-development requests."""
        if self._self_dev:
            response.text = "Self-dev analysis queued. I'll review recent reflections and propose improvements."
        else:
            response.text = "Self-dev Agent is not available."
        return response

    def _handle_status(self, message: Message, response: Response) -> Response:
        """Handle status checks."""
        response.text = (
            "AEGIS is running. Use the Dashboard for detailed status:\n"
            "http://127.0.0.1:8090\n\n"
            "Quick links:\n"
            "- Servers: http://127.0.0.1:8090/dashboard/servers\n"
            "- Events: http://127.0.0.1:8090/dashboard/events\n"
            "- Approvals: http://127.0.0.1:8080/approvals"
        )
        return response

    def _handle_help(self, message: Message, response: Response) -> Response:
        """Handle help requests."""
        response.text = (
            "I can help with:\n"
            "- Research: 'research Python 3.12 features'\n"
            "- Settings: 'show settings' or 'enable support agent'\n"
            "- Approvals: 'show pending approvals'\n"
            "- Status: 'what's the status?'\n"
            "- Self-dev: 'improve the event bus'\n\n"
            "For dangerous operations, I'll route you to the Approval UI."
        )
        return response

    def _handle_tool_request(self, message: Message, response: Response) -> Response:
        """Handle direct tool requests — routes through PolicyEngine."""
        if self._broker:
            response.text = (
                "Tool requests must go through the Approval UI for safety. "
                "Please use the Dashboard or Approval UI: http://127.0.0.1:8080/approvals"
            )
        else:
            response.text = "Tool Broker not available."
        return response

    def _handle_llm_fallback(self, message: Message, response: Response) -> Response:
        """Handle unknown intents using LLM fallback."""
        if not self._llm:
            response.text = (
                "I'm not sure what you mean. Could you rephrase? "
                "I can help with research, settings, approvals, or general questions."
            )
            return response

        text = message.text.strip()

        # Check if user wants browser operations
        browser_keywords = ["open", "go to", "navigate", "browse", "visit", "search for", "look up"]
        is_browser_request = any(kw in text.lower() for kw in browser_keywords)

        # Check if it looks like a URL
        url_pattern = r'https?://[^\s]+'
        has_url = bool(re.search(url_pattern, text))

        if is_browser_request or has_url:
            return self._handle_browser_request(message, response)

        # General LLM conversation
        try:
            system_prompt = (
                "You are AEGIS, an autonomous AI assistant. You can:\n"
                "- Browse the web and extract information\n"
                "- Take screenshots of the PC\n"
                "- Run research tasks\n"
                "- Control PC, Android, Room devices (with approval)\n"
                "- Manage settings\n\n"
                "Respond concisely and helpfully. If the user asks you to do something "
                "that requires device access, explain that it needs approval."
            )
            result = self._llm.generate(
                prompt=text,
                system_prompt=system_prompt,
                max_tokens=500,
            )
            if result.success:
                response.text = result.content
            else:
                response.text = f"LLM error: {result.error}"
        except Exception as e:
            logger.error("LLM fallback failed: %s", e)
            response.text = f"Sorry, I couldn't process that: {e}"

        return response

    def _handle_browser_request(self, message: Message, response: Response) -> Response:
        """Handle browser automation requests."""
        text = message.text.strip()

        # Extract URL from message
        url_match = re.search(r'https?://[^\s]+', text)
        url = url_match.group(0) if url_match else ""

        # If no URL, try to construct a search URL
        if not url:
            # Extract search query
            search_patterns = [
                r'search\s+(?:for\s+)?(.+)',
                r'look\s+up\s+(.+)',
                r'google\s+(.+)',
                r'find\s+(.+)',
            ]
            for pattern in search_patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    query = m.group(1).strip()
                    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    break

        if not url:
            response.text = "Please provide a URL or search query. Example: 'open https://example.com' or 'search for Python 3.12'"
            return response

        # Execute browser automation
        try:
            import asyncio
            from playwright.async_api import async_playwright

            async def browse():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=30000)
                    title = await page.title()

                    # Extract text content
                    text_content = await page.evaluate("""
                        (() => {
                            const exclude = ['script', 'style', 'nav', 'footer', 'noscript'];
                            const clone = document.body.cloneNode(true);
                            exclude.forEach(tag => {
                                clone.querySelectorAll(tag).forEach(el => el.remove());
                            });
                            return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
                        })()
                    """)

                    await browser.close()
                    return title, text_content[:2000]

            title, content = asyncio.run(browse())

            # Use LLM to summarize if available
            if self._llm:
                summary_result = self._llm.generate(
                    prompt=f"Summarize this webpage content concisely:\n\nTitle: {title}\n\nContent:\n{content}",
                    system_prompt="You are a web content summarizer. Be concise and informative.",
                    max_tokens=300,
                )
                if summary_result.success:
                    response.text = f"**{title}**\n\n{summary_result.content}\n\n_Source: {url}_"
                else:
                    response.text = f"**{title}**\n\n{content[:500]}..."
            else:
                response.text = f"**{title}**\n\n{content[:500]}..."

        except Exception as e:
            logger.error("Browser automation failed: %s", e)
            response.text = f"Failed to browse {url}: {e}"

        return response
