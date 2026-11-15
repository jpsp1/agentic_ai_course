# The imports

from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from IPython.display import Image, display
import os
# On Windows, a stdio MCP server started from a Jupyter kernel writes to a stderr stream with no
# real file descriptor and crashes with io.UnsupportedOperation: fileno. We send the server's
# stderr to the null device so it always has somewhere real to write, which lets every cell below
# use MCPServerStdio exactly as the OpenAI Agents SDK documents it. Mac and Linux are unaffected.
import functools
import subprocess
import agents.mcp.server
import asyncio

load_dotenv(override=True)



agents.mcp.server.stdio_client = functools.partial(agents.mcp.server.stdio_client, errlog=subprocess.DEVNULL)

fetch_params = {"command": "uvx", "args": ["mcp-server-fetch"]}

playwright_params = {"command": "npx", "args": [ "@playwright/mcp@latest"]}


sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))  # the only folder the filesystem server may touch
os.makedirs(sandbox_path, exist_ok=True)
files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

INSTRUCTIONS = """
You browse the internet to accomplish your instructions.
Accept cookies and navigate pop-ups as needed.
If one website isn't fruitful, try another.
Be persistent until you have solved your assignment,
trying different options and sites as needed.
When you need to write files, you do that inside the sandbox/ folder only.
"""

#TASK = "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md"

TASK = "Find job offerings in the Lisbon region, then summarize it in markdown to jobs.md"


async def main():    
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.list_tools()
    #print(fetch_tools)
    # print(fetch_tools[0].description)
    # print("\n\n")
    # print(fetch_tools[0].inputSchema)

    
  

    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as server:
        playwright_tools = await server.list_tools()

    #print(playwright_tools)

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as server:
        file_tools = await server.list_tools()

    print(file_tools)


    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as mcp_server_files:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as mcp_server_browser:
            agent = Agent(
                name="investigator",
                instructions=INSTRUCTIONS,
                model="gpt-5.4-mini",
                mcp_servers=[mcp_server_files, mcp_server_browser]
                )
            with trace("investigate"):
                result = await Runner.run(agent, TASK, max_turns=20)
                print(result.final_output)    

if __name__ == "__main__":
    asyncio.run(main())