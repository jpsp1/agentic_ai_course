#From Edward Donner's 2026 course: AI Engineer Agentic Track: The Complete Agent & MCP Course 

# The framework prints a couple of "experimental" notices on import; quiet them.
import asyncio
import warnings
import board
warnings.filterwarnings("ignore", message=r".*experimental.*")


import subprocess
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import Agent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient

load_dotenv(override=True)

MODEL = "gpt-5.4-mini"

client = OpenAIChatClient(model=MODEL)

# agent = Agent(
#     client=client,
#     instructions="You are a concise, friendly assistant. Reply in a single short sentence.",
# )



board.reset_board()
board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt.")
board.list_todos()
board.show_board()

def show_todos() -> list[dict]:
    """List every todo on the board. A goal has parent_id None; a step has parent_id set to its goal's id."""
    return board.list_todos()

def plan_steps(goal_id: int, steps: list[str]) -> dict:
    """Break a goal into an ordered checklist of steps on the board. Pass the goal's id and a short list of step descriptions."""
    return {"goal_id": goal_id, "step_ids": [board.add_step(goal_id, step) for step in steps]}

def complete_task(task_id: int, result: str) -> dict:
    """Mark a todo (a step or the goal) with this id as done and record a short result summary."""
    board.complete_todo(task_id, result)
    return {"task_id": task_id, "status": "done"}

board_agent = Agent(
    client=client,
    instructions="You help manage a shared todo board.",
    tools=[show_todos, complete_task],
)    

workspace = Path("workspace").resolve()   # the only folder the agent may touch


class FilesystemMCP(MCPStdioTool):
    """The filesystem server with its stderr sent to DEVNULL and its working
    directory set to the workspace, so file names resolve there and it runs
    cleanly from a Jupyter kernel on Windows."""

    def get_mcp_client(self):
        from mcp.client.stdio import StdioServerParameters, stdio_client

        params = StdioServerParameters(command=self.command, args=self.args, env=self.env, cwd=str(workspace))
        return stdio_client(server=params, errlog=subprocess.DEVNULL)


filesystem = FilesystemMCP(
    name="filesystem",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", str(workspace)],
)


file_agent = Agent(
    client=client,
    instructions="You can read and write files in your workspace. Use your tools to do what is asked.",
    tools=[filesystem],
)


INSTRUCTIONS = """
You are a careful worker with a shared todo board and a set of file tools.

Take the pending goal and see it through. Begin by laying out a short plan: the handful of concrete steps the work itself breaks down into, added to the board under the goal. Then carry them out with your file tools, marking each step done as you finish it. Once the steps are all done, close the goal. Your files live in the single folder your tools are allowed to use.
"""

worker = Agent(
    client=client,
    instructions=INSTRUCTIONS,
    tools=[show_todos, plan_steps, complete_task, filesystem],
)

board.reset_board()
goal_id = board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt.")
board.claim_todo(goal_id)



async def main():    
    #result = await agent.run("Say hello in Spanish.")
    #print(result.text)
    #result = await board_agent.run("What is on the board right now, and what is its status?")
    #print(result.text)
    # async with filesystem:
    #     result = await file_agent.run("Read notes.txt and summarize it in one short sentence.")
    # print(result.text)
    async with filesystem:
        await worker.run("Please work the pending goal on the board.")
    board.show_board()
if __name__ == "__main__":
    asyncio.run(main())
