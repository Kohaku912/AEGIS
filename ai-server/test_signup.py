import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
import json

async def test_full_signup():
    from browser_use import Agent
    from browser_use.llm.openai.chat import ChatOpenAI
    from browser_use.browser import BrowserProfile, BrowserSession
    from aegis_browser.browser_use_agent import _patch_browser_use_models

    config_path = '../browser-server/config.json'
    with open(config_path) as f:
        config = json.load(f)

    llm_config = config.get('llm', {})
    llm = ChatOpenAI(
        model=llm_config.get('model', 'deepseek-v4-flash'),
        api_key=llm_config.get('api_key'),
        base_url=llm_config.get('base_url'),
        dont_force_structured_output=True,
    )

    _patch_browser_use_models()

    profile = BrowserProfile(keep_alive=True)
    session = BrowserSession(browser_profile=profile)

    task = """Go to https://accounts.google.com/signup and create a Google account:
- First name: Test
- Last name: User
- Birthday: January 15, 1990
- Gender: Male
- When asked for email, choose to create a new Gmail address
- Username: testuser12345
- Password: TestPass123!
- Complete all steps until account is created or you hit phone/email verification"""

    agent = Agent(task=task, llm=llm, max_actions_per_step=1, browser_session=session)

    try:
        result = await agent.run(max_steps=30)
        print("=== FINAL RESULT ===")
        result_str = str(result)
        if "Final Result" in result_str:
            start = result_str.find("Final Result")
            print(result_str[start:start+2000])
        else:
            print(result_str[:2000])
    except Exception as e:
        print(f"ERROR: {e}")

asyncio.run(test_full_signup())
