"""Browser-Use Integration — natural language browser automation.

Provides:
- BrowserUseTaskExecutor: Executes browser tasks using browser-use
- BrowserUseSafetyBoundary: Safety checks for browser tasks

Usage:
    from aegis_ai.browser_use import BrowserUseTaskExecutor
    executor = BrowserUseTaskExecutor(llm_client=llm)
    result = executor.execute("Go to example.com and extract text")
"""

from aegis_ai.browser_use.executor import (  # noqa: F401
    BrowserTaskResult,
    BrowserUseSafetyBoundary,
    BrowserUseTaskExecutor,
)
