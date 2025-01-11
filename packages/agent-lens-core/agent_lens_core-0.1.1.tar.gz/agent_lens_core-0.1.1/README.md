<img src="./static/agent-lens.png" alt="Agent Lens Logo" width="full"/>

<br/>

[![Documentation](https://img.shields.io/badge/Documentation-📕-blue)](https://docs.agent-lens.com)
[![Twitter Follow](https://img.shields.io/twitter/follow/agent_lens?style=social)](https://x.com/agent_lens)

Make websites accessible for AI agents 🤖.

Agent lens is the easiest way to connect your AI agents with the browser.

To learn more about the library, check out the [documentation 📕](https://docs.agent-lens.com).

# Quick start

With pip:

```bash
pip install agent_lens_core
```

(optional) install playwright:

```bash
playwright install
```

Spin up your agent:

```python
from langchain_openai import ChatOpenAI
from agent_lens_core import Agent
import asyncio

async def main():
    agent = Agent(
        task="Find a one-way flight from Bali to Oman on 12 January 2025 on Google Flights. Return me the cheapest option.",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

And don't forget to add your API keys to your `.env` file.

```bash
OPENAI_API_KEY=
```

For other settings, models, and more, check out the [documentation 📕](https://docs.agent-lens.com).

# Demo

Prompt: Find flights on kayak.com from Zurich to Beijing from 25.12.2024 to 02.02.2025.

![flight search 8x 10fps](https://github.com/user-attachments/assets/ea605d4a-90e6-481e-a569-f0e0db7e6390)

<br/><br/>

## More examples

For more examples see the [examples](examples) folder

# Contributing

Contributions are welcome! Feel free to open issues for bugs or feature requests.

## Local Setup

To learn more about the library, check out the [local setup 📕](https://docs.agent-lens.com/development/local-setup).

---

<div align="center">
  Made with ❤️ in Zurich and San Francisco
</div>
