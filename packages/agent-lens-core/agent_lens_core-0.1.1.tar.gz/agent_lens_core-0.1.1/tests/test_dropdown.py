"""
Simple try of the agent.

@dev You need to add OPENAI_API_KEY to your environment variables.
"""

from agent_lens_core import Agent, AgentHistoryList, Controller
from langchain_openai import ChatOpenAI
import asyncio
import os
import sys

from agent_lens_core.browser.browser import Browser, BrowserConfig
from agent_lens_core.browser.context import BrowserContext, BrowserContextConfig

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


llm = ChatOpenAI(model='gpt-4o')
# browser = Browser(config=BrowserConfig(headless=False))

agent = Agent(
    task=(
        'go to https://codepen.io/geheimschriftstift/pen/mPLvQz and first get all options for the dropdown and then select the 5th option'
    ),
    llm=llm,
    browser_context=BrowserContext(
        browser=Browser(config=BrowserConfig(
            headless=False, disable_security=True)),
    ),
)


async def test_dropdown():
    history: AgentHistoryList = await agent.run(20)
    # await controller.browser.close(force=True)

    result = history.final_result()
    assert result is not None
    assert 'Duck' in result
    # await browser.close()
