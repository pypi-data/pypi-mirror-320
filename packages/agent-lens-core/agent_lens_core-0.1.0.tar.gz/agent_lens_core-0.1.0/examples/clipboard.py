from agent_lens_core.browser.context import BrowserContext
from agent_lens_core.browser.browser import Browser, BrowserConfig
from agent_lens_core import Agent, Controller
from langchain_openai import ChatOpenAI
import pyperclip
import asyncio
import os
import sys
from pathlib import Path

from agent_lens_core.agent.views import ActionResult

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


browser = Browser(
    config=BrowserConfig(
        headless=False,
    )
)
controller = Controller()


@controller.registry.action('Copy text to clipboard')
def copy_to_clipboard(text: str):
    pyperclip.copy(text)
    return ActionResult(extracted_content=text)


@controller.registry.action('Paste text from clipboard', requires_browser=True)
async def paste_from_clipboard(browser: BrowserContext):
    text = pyperclip.paste()
    # send text to browser
    page = await browser.get_current_page()
    await page.keyboard.type(text)

    return ActionResult(extracted_content=text)


async def main():
    task = (
        f'Copy the text "Hello, world!" to the clipboard, then go to google.com and paste the text'
    )
    model = ChatOpenAI(model='gpt-4o')
    agent = Agent(
        task=task,
        llm=model,
        controller=controller,
        browser=browser,
    )

    await agent.run()
    await browser.close()

    input('Press Enter to close...')


if __name__ == '__main__':
    asyncio.run(main())
