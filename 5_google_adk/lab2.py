#From Edward Donner's 2026 course: AI Engineer Agentic Track: The Complete Agent & MCP Course 
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from quiet import silence
import asyncio
import board
import requests
import subprocess
from pathlib import Path
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

silence()  # turn down some noisy library logging so the agent's trace is easy to read

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
load_dotenv(override=True)

MODEL = "gemini-3.1-flash-lite"

# agent = LlmAgent(
#     model=MODEL,
#     name="assistant",
#     instruction="You are a concise, friendly assistant. Reply in a single short sentence.",
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


def send_push_notification(message: str) -> str:
    """Send a short push notification to the user's phone to report a result or that a job is done."""
    payload = {
        "token": os.getenv("PUSHOVER_TOKEN"),
        "user": os.getenv("PUSHOVER_USER"),
        "message": message,
        "sound": "climb"
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    return f"Push notification sent (status {response.status_code})."

board_agent = LlmAgent(
    model=MODEL,
    name="board_agent",
    instruction="You help manage a shared todo board.",
    tools=[show_todos, complete_task],    
)



workspace = Path("a2a_demo/task_worker/workspace").resolve()   # the only folder the agent may touch

filesystem = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", str(workspace)],
            cwd=str(workspace),  # start the server in the workspace so relative file names resolve there
        ),
        timeout=60
    ),
    errlog=subprocess.DEVNULL,
)

file_agent = LlmAgent(
    model=MODEL,
    name="file_agent",
    instruction="You can read and write files in your workspace. Use your tools to do what is asked.",
    tools=[filesystem],
)



INSTRUCTIONS = """
You are a careful worker with a shared todo board and a set of file tools.

Take the pending goal and see it through. Begin by laying out a short plan: the handful of concrete steps the work itself breaks down into, added to the board under the goal. Then carry them out with your file tools, marking each step done as you finish it. Once the steps are all done, close the goal. Your files live in the single folder your tools are allowed to use.
"""

worker = LlmAgent(
    model=MODEL,
    name="task_worker",
    instruction=INSTRUCTIONS,
    tools=[show_todos, plan_steps, complete_task, filesystem, send_push_notification],
)

board.reset_board()
goal_id = board.add_goal("Read notes.txt, translate its contents into natural Spanish, and write the Spanish to spanish.txt and send a push notification with a summary.")
board.claim_todo(goal_id)



async def main():    

    # Drive the loop ourselves with run_async instead of run_debug, so we can watch it:
    # print each tool call, and re-draw the board whenever a step is planned or ticked off.
    runner = InMemoryRunner(agent=worker)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="ed")

    async for event in runner.run_async(
        user_id="ed",
        session_id=session.id,
        new_message=types.UserContent("Please work the pending goal on the board."),
    ):
        for call in event.get_function_calls():
            print(f"tool: {call.name}({call.args})")
        if any(r.name in ("plan_steps", "complete_task") for r in event.get_function_responses()):
            board.show_board()
        if event.is_final_response():
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())