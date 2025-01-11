from agent_lens_core.browser.context import BrowserContextConfig
from agent_lens_core.browser.browser import Browser
from agent_lens_core.agent.service import Agent
import asyncio
import os
import sys

from langchain_openai import ChatOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


llm = ChatOpenAI(model='gpt-4o', temperature=0.0)


async def main():
    browser = Browser()

    async with await browser.new_context(
            config=BrowserContextConfig(trace_path='./tmp/traces/')
    ) as context:
        agent = Agent(
            task='Go to hackernews, then go to apple.com and return all titles of open tabs',
            llm=llm,
            browser_context=context,
        )
        await agent.run()

    await browser.close()


asyncio.run(main())
