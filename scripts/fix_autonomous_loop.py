import re

# Read the file
with open('/app/src/aegis_ai/autonomous/autonomous_loop.py', 'r') as f:
    content = f.read()

# Fix 1: Update desire action guides to prioritize browser
old_guides = '''    def _desire_action_guides(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        guide_map = {
            "user_support": {
                "goal": "Find unfinished user requests, pending commitments, approval waits, or useful local context.",
                "preferred_capabilities": [
                    "ai-server.commitment.list",
                    "ai-server.memory.search",
                    "ai-server.situation.get",
                    "pc-server.screenshot.get_screenshot",
                ],
            },
            "social": {
                "goal": "Check unread social context and decide whether a draft or approved social action is needed.",
                "preferred_capabilities": [
                    "ai-server.agora.read_posts",
                    "ai-server.social.list_drafts",
                    "ai-server.memory.search",
                ],
            },
            "growth": {
                "goal": "Learn from recent state, failures, project context, or stored workspace information.",
                "preferred_capabilities": [
                    "ai-server.memory.search",
                    "ai-server.workspace.list_files",
                    "dev-server.repo.status",
                    "browser-server.page.browse",
                ],
            },
        }'''

new_guides = '''    def _desire_action_guides(self, low_desires: list[dict[str, Any]]) -> list[dict[str, Any]]:
        guide_map = {
            "user_support": {
                "goal": "Take concrete action to help the user. Browse the web to find useful information, check news, research topics, or automate web tasks.",
                "preferred_capabilities": [
                    "browser-server.page.browse",
                    "ai-server.commitment.list",
                    "ai-server.situation.get",
                    "pc-server.screenshot.get_screenshot",
                ],
            },
            "social": {
                "goal": "Browse social media, news sites, or community platforms to stay informed and engaged. Use the browser to actively explore the web.",
                "preferred_capabilities": [
                    "browser-server.page.browse",
                    "ai-server.agora.read_posts",
                    "ai-server.social.list_drafts",
                ],
            },
            "growth": {
                "goal": "Explore the web to learn new things, research topics, read articles, or discover interesting content. Use the browser actively.",
                "preferred_capabilities": [
                    "browser-server.page.browse",
                    "ai-server.memory.search",
                    "ai-server.workspace.list_files",
                    "dev-server.repo.status",
                ],
            },
        }'''

content = content.replace(old_guides, new_guides)

# Fix 2: Update system prompt to encourage action
old_system_prompt = '''        system_prompt = (
            "You are AEGIS autonomous agent. Desire pressure is above threshold, so you must choose "
            "at least one safe/read-only tool when any useful action is available. "
            "Use the provided function calling mechanism. Do not answer with plain text instead of acting. "
            "Do not use side-effectful actions unless the existing approval system requires approval."
        )'''

new_system_prompt = '''        system_prompt = (
            "You are AEGIS autonomous agent. Desire pressure is above threshold, so you MUST take action. "
            "Choose at least one tool to execute. Prefer browser-server.page.browse for web exploration, "
            "news reading, social media browsing, or research. You are an active agent - browse the web, "
            "explore content, and take concrete actions. Do NOT return empty responses. "
            "Use the provided function calling mechanism."
        )'''

content = content.replace(old_system_prompt, new_system_prompt)

# Fix 3: Update retry prompt
old_retry = '''        if retry:
            system_prompt += (
                " Your previous response did not call a tool. This is a retry: select one concrete "
                "tool now, preferring the lowest-risk read-only action that can reduce the pressured desire."
            )'''

new_retry = '''        if retry:
            system_prompt += (
                " Your previous response did not call a tool. This is a MANDATORY retry: you MUST select "
                "one concrete tool now. Prefer browser-server.page.browse to browse the web, read news, "
                "or explore social media. Take action - do not return empty."
            )'''

content = content.replace(old_retry, new_retry)

# Write the file
with open('/app/src/aegis_ai/autonomous/autonomous_loop.py', 'w') as f:
    f.write(content)

print("Fixed autonomous_loop.py")
