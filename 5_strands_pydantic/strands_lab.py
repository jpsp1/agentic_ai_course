#From Edward Donner's 2026 course: AI Engineer Agentic Track: The Complete Agent & MCP Course 

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
import asyncio
import board


load_dotenv(override=True)

MODEL = "gpt-5.4-mini"

model = OpenAIModel(client_args={"api_key": os.environ["OPENAI_API_KEY"]}, model_id=MODEL)

# agent = Agent(
#     model=model,
#     system_prompt="You are a concise, friendly assistant. Reply in a single short sentence.",
# )


@tool
def show_todos() -> list[dict]:
    """List every todo on the board. A goal has parent_id None; a step has parent_id set to its goal's id."""
    return board.list_todos()

@tool
def plan_steps(goal_id: int, steps: list[str]) -> dict:
    """Break a goal into an ordered checklist of steps on the board.

    Args:
        goal_id: The id of the goal to break down.
        steps: Short descriptions of the steps to take, in order.
    """
    return {"goal_id": goal_id, "step_ids": [board.add_step(goal_id, step) for step in steps]}

@tool
def complete_task(task_id: int, result: str) -> dict:
    """Mark a todo (a step or the goal) done and record a short result summary.

    Args:
        task_id: The id of the todo to mark done.
        result: A short summary of what was accomplished.
    """
    board.complete_todo(task_id, result)
    return {"task_id": task_id, "status": "done"}


board.reset_board()
board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt.")
board.list_todos()
print("Current board:")
board.show_board()


board_agent = Agent(
    model=model,
    system_prompt="You help manage a shared todo board.",
    tools=[show_todos, complete_task],
)

workspace = Path("workspace").resolve()   # the only folder the agent may touch

filesystem = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", str(workspace)],
            cwd=str(workspace),  # start the server in the workspace so relative file names resolve there
        ),
        errlog=subprocess.DEVNULL,
    ),
    startup_timeout=60
)

# file_agent = Agent(
#     model=model,
#     system_prompt="You can read and write files in your workspace. Use your tools to do what is asked.",
#     tools=[filesystem],
# )


INSTRUCTIONS = """
You are a careful worker with a shared todo board and a set of file tools.

Take the pending goal and see it through. Begin by laying out a short plan: the handful of concrete steps the work itself breaks down into, added to the board under the goal. Then carry them out with your file tools, marking each step done as you finish it. Once the steps are all done, close the goal. Your files live in the single folder your tools are allowed to use.
"""

worker = Agent(
    model=model,
    system_prompt=INSTRUCTIONS,
    tools=[show_todos, plan_steps, complete_task, filesystem],
)

board.reset_board()
goal_id = board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt.")
board.claim_todo(goal_id)



async def main():    
    #result = await agent.invoke_async("Say hello in Spanish.")
    #result = await board_agent.invoke_async("What is on the board right now, and what is its status?")
    #result = await file_agent.invoke_async("Read notes.txt and summarize it in one short sentence.")
    await worker.invoke_async("Please work the pending goal on the board.")
    board.show_board()



if __name__ == "__main__":
    asyncio.run(main())