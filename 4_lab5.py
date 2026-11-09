import sys

if sys.platform == "win32":
    import subprocess
    from functools import partial
    import langchain_mcp_adapters.sessions as mcp_sessions

    mcp_sessions.stdio_client = partial(mcp_sessions.stdio_client, errlog=subprocess.DEVNULL)
    print("Applied the Windows adjustment")
else:
    print("Not Windows, so nothing to do here")

# Imports and environment first

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from sidekick_tools import search, send_push_notification, wikipedia_lookup
from sidekick import Sidekick

load_dotenv(override=True)

simple_worker = create_agent(
    model="openai:gpt-5.4-mini",
    tools=[search, send_push_notification, wikipedia_lookup],
    system_prompt="You are Sidekick, a helpful personal assistant. Use your tools to complete the task.",
    checkpointer=InMemorySaver(),
)

async def ask(worker, message):
    config = {"configurable": {"thread_id": "simple-sidekick"}}
    result = await worker.ainvoke({"messages": [{"role": "user", "content": message}]}, config=config)
    return result["messages"][-1].content

async def main():    
    reply = await ask(simple_worker, "Search for who won the Nobel Prize in Physics in 2023 and send a push notification with a short summary.")
    print(reply)

if __name__ == "__main__":
    asyncio.run(main())