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
import asyncio
from langchain_core.tools import tool

load_dotenv(override=True)




@tool
def book_meeting(person: str, day: str) -> str:
    """Book a meeting with a person on a given day."""
    return f"Meeting booked with {person} on {day}."

approval_agent = create_agent(
    model="openai:gpt-5.4-mini",
    tools=[book_meeting],
    system_prompt="You are a scheduling assistant. Use the book_meeting tool.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"book_meeting": True})],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "approval-demo"}}

async def main():    
    result = await approval_agent.ainvoke(
        {"messages": [{"role": "user", "content": "Book a meeting with Sam on Friday."}]}, config
    )

    interrupt = result["__interrupt__"][0]
    print("The agent paused and is asking for approval:")
    print(interrupt.value["action_requests"][0]["description"])

    #resumed = await approval_agent.ainvoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
    
    resumed = await approval_agent.ainvoke(Command(resume={"decisions": [{"type": "reject", "message": "Rejected - no meetings on Fridays"}]}), config)


    print(resumed["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
